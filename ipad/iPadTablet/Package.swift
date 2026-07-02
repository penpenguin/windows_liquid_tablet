// swift-tools-version: 5.9

import PackageDescription

let package = Package(
    name: "iPadTablet",
    platforms: [
        .iOS(.v16)
    ],
    products: [
        .library(name: "iPadTablet", targets: ["iPadTablet"])
    ],
    targets: [
        .target(name: "iPadTablet", path: "Sources"),
        .testTarget(
            name: "MappingTests",
            dependencies: ["iPadTablet"],
            path: "Tests/MappingTests"
        )
    ]
)
