import XCTest
@testable import iPadTablet

final class HostDiscoveryTests: XCTestCase {
    func testParsesHostMdnsTxtRecordContract() throws {
        let payload = try XCTUnwrap(HostDiscoveryPayload(txtRecord: [
            "version": "1",
            "hostId": "studio-pc",
            "name": "Studio PC",
            "address": "192.168.1.23",
            "inputPort": "54831",
            "videoPort": "54832",
            "pairingCode": "123456",
        ]))

        XCTAssertEqual(payload.hostId, "studio-pc")
        XCTAssertEqual(payload.displayName, "Studio PC")
        XCTAssertEqual(payload.inputEndpoint, PairingEndpoint(address: "192.168.1.23", port: 54831))
        XCTAssertEqual(payload.videoEndpoint, PairingEndpoint(address: "192.168.1.23", port: 54832))
        XCTAssertEqual(payload.pairingCode, PairingCode("123456"))
    }

    func testRejectsUnsupportedDiscoveryPayloadVersion() {
        XCTAssertNil(HostDiscoveryPayload(txtRecord: [
            "version": "2",
            "hostId": "studio-pc",
            "name": "Studio PC",
            "address": "192.168.1.23",
            "inputPort": "54831",
            "videoPort": "54832",
            "pairingCode": "123456",
        ]))
    }

    func testRejectsDiscoveryPayloadWithSharedInputAndVideoPort() {
        XCTAssertNil(HostDiscoveryPayload(txtRecord: [
            "version": "1",
            "hostId": "studio-pc",
            "name": "Studio PC",
            "address": "192.168.1.23",
            "inputPort": "54831",
            "videoPort": "54831",
            "pairingCode": "123456",
        ]))
    }

    func testDiscoveryListUpsertsAndExpiresCandidates() throws {
        let payload = try XCTUnwrap(HostDiscoveryPayload(txtRecord: [
            "version": "1",
            "hostId": "studio-pc",
            "name": "Studio PC",
            "address": "192.168.1.23",
            "inputPort": "54831",
            "videoPort": "54832",
            "pairingCode": "123456",
        ]))
        var list = DiscoveredHostList()

        list.upsert(payload, seenAtNanos: 1_000)
        list.upsert(payload.with(displayName: "Studio PC Updated"), seenAtNanos: 2_000)

        XCTAssertEqual(list.candidates.count, 1)
        XCTAssertEqual(list.candidates[0].payload.displayName, "Studio PC Updated")
        XCTAssertEqual(list.bestCandidate?.payload.hostId, "studio-pc")

        list.removeExpired(nowNanos: 10_000, ttlNanos: 1_000)
        XCTAssertTrue(list.candidates.isEmpty)
    }
}
