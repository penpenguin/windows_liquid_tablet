# AGENTS.md — iPadをWindows液タブ化する自作プロジェクト向けCodex指示書

このリポジトリの目的は、iPadをWindowsの液晶ペンタブレット相当として使うための自作システムを段階的に実装することです。最初の実用目標は、EasyCanvas 2025風の「追加ディスプレイ表示 + Apple Pencil入力 + 筆圧 + 傾き + 低遅延操作」です。最終目標は、Windows側で仮想ディスプレイとして認識され、Apple Pencil入力がWindows Ink/TabletPC系のペン入力として描画アプリへ届く状態です。

この文書はCodex向けの常時適用指示です。ユーザーから個別タスクが与えられたら、この文書を最上位方針として扱ってください。

---

## 1. 最重要ゴール

実装対象は以下の4要素です。

1. Windowsホストアプリ
   - iPadとの接続管理
   - 画面キャプチャ
   - 低遅延映像エンコード/送信
   - iPadから受け取ったApple PencilイベントのWindows入力注入
   - ログ、診断、設定UI

2. iPadアプリ
   - Windows映像の低遅延表示
   - Apple Pencilの座標、筆圧、傾き、可能ならホバーの取得
   - 指タッチとPencil入力の分離
   - 入力イベント送信
   - キャリブレーションUI、ショートカットUI

3. Windows仮想ディスプレイドライバ
   - WindowsにiPad用の追加モニターを認識させる
   - まずはIddCx / Indirect Display Driver方式を第一候補とする
   - MVPでは未実装でもよいが、設計は最初から分離しておく

4. オプションの仮想HIDペンドライバ
   - 初期実装では必須ではない
   - `InjectSyntheticPointerInput` によるWindows Ink/TabletPC入力で実用性を先に検証する
   - 互換性不足が明確になった段階でUMDF/KMDF HID minidriverを検討する

---

## 2. 実装方針の優先順位

優先順位は次の通りです。

1. まず動くものを作る
2. その動作をテストで固定する
3. 低遅延化する
4. 座標精度、筆圧、傾きの品質を上げる
5. 仮想ディスプレイ化する
6. 必要になったら仮想HIDペン化する

いきなりWindowsドライバ全体を実装しないでください。最初はユーザーモードのWindowsホスト + iPadアプリ + Synthetic Pointer入力で縦に貫通させます。

---

## 3. 禁止事項

次の実装は禁止です。

- Windowsの未公開API、カーネルフック、入力フック、アンチチート回避、署名回避、セキュリティ機構の無効化を前提にすること
- AppleのPrivate APIを使うこと
- 既存商用アプリの通信プロトコルやバイナリを解析・模倣すること
- ドライバ署名を迂回する手順を成果物に含めること
- テストが通っていないのに「完了」と報告すること
- 大規模な書き換えを一括で行い、失敗時に原因分離できない状態にすること
- 映像転送、入力注入、ドライバを密結合にすること

テスト署名、WDK、開発者モードなど、Microsoftが公式に提供する開発・検証フローは利用してよいです。ただし一般配布可能な署名済みドライバとして扱わないでください。

---

## 4. 技術スタックの標準案

既存リポジトリに明確な選定がある場合はそれを尊重します。新規リポジトリでは以下を標準とします。

### Windows

- 言語: C++20を第一候補。Rust既存基盤がある場合はRustでもよい
- ビルド: CMake + Visual Studio 2022
- GUI: 最初はWin32/consoleでよい。後でWinUI 3またはQtを検討
- 画面キャプチャ: Desktop Duplication API または Windows.Graphics.Capture
- 入力注入: `CreateSyntheticPointerDevice` + `InjectSyntheticPointerInput`
- 映像エンコード: 初期は差し替え可能なインターフェース。最終候補はMedia Foundation / GPU encoder / H.264
- ドライバ: IddCx / WDF / WDK

### iPad

- 言語: Swift
- UI: UIKitまたはSwiftUI + UIViewRepresentable
- Pencil入力: UIKit raw touch (`UITouch`) を第一候補
- 映像表示: 初期は差し替え可能なRenderer。最終候補はVideoToolbox / AVSampleBufferDisplayLayer / Metal
- 通信: Network.framework。MVPはTCPまたはWebSocket、低遅延版はUDP/QUIC/WebRTCを検討

### 共通

- プロトコル定義は`protocol/`に集約する
- 座標変換、筆圧カーブ、傾き補正は純粋関数化してユニットテスト可能にする
- 低レベルAPI呼び出しは薄いadapterに閉じ込める

---

## 5. 推奨ディレクトリ構成

既存構成がない場合、次の構成を作ってください。

```text
/
  AGENTS.md
  README.md
  docs/
    architecture.md
    protocol.md
    milestones.md
    testing.md
    manual-test-checklist.md
    driver-notes.md
  protocol/
    pen_packet.h
    pen_packet.md
    schema_tests/
  windows/
    host/
      CMakeLists.txt
      src/
        main.cpp
        app/
        capture/
        codec/
        input/
        net/
        mapping/
        diagnostics/
      tests/
    idd_driver/
      README.md
      src/
      inf/
    hid_driver_optional/
      README.md
      src/
      inf/
  ipad/
    iPadTablet/
      iPadTablet.xcodeproj or Package.swift
      Sources/
        App/
        Pencil/
        Video/
        Network/
        Mapping/
        Diagnostics/
      Tests/
  tools/
    latency_probe/
    packet_dump/
  scripts/
    build_windows.ps1
    test_windows.ps1
    format.ps1
```

ドライバ部分が未実装の段階でも、`README.md`とstubインターフェースを用意しておくこと。

---

## 6. ループエンジニアリング規約

Codexは、各タスクを次のループで進めてください。

### 6.1 入口ループ

1. リポジトリ構成を確認する
2. 既存のREADME、AGENTS.md、docs、ビルドスクリプトを読む
3. 現在のマイルストーンを特定する
4. 変更範囲を最小化する
5. 受入条件を明文化してから実装する

### 6.2 実装ループ

各変更は以下を1サイクルとします。

```text
Plan → Small Patch → Build/Test → Inspect Failure → Fix → Re-run → Document
```

1サイクルのパッチは、可能なら1つの責務に限定します。例: `PenPacket`定義だけ、座標変換だけ、Synthetic Pointer adapterだけ。

### 6.3 テストループ

コード変更後は必ず該当テストを実行します。テスト環境がない場合は、その理由、実行不能だったコマンド、代替検証を明記します。

最低限、次のいずれかを実行してください。

```powershell
pwsh ./scripts/test_windows.ps1
cmake --build build --config Debug
ctest --test-dir build --output-on-failure
```

iPad側は実行可能環境がある場合のみ次を試します。

```bash
xcodebuild test -scheme iPadTablet -destination 'platform=iOS Simulator,name=iPad Pro (13-inch)'
```

ただしApple Pencil実機入力はSimulatorで完全検証できないため、実機手順を`docs/manual-test-checklist.md`へ残してください。

### 6.4 失敗時ループ

ビルドまたはテストが失敗した場合、次の順序で処理します。

1. 最初のエラーを特定する
2. 関連ログだけを抜粋する
3. 原因仮説を1つ立てる
4. 最小修正を行う
5. 同じテストを再実行する
6. 連続して同じ方向で3回失敗したら、別案または切り分けテストを作る

失敗ログを隠さないでください。未解決なら未解決として報告してください。

### 6.5 完了報告ループ

タスク完了時は以下を簡潔に報告します。

```text
変更内容:
検証結果:
未検証/制限:
次の推奨ステップ:
```

「たぶん動く」「未確認だが完了」などの表現は禁止です。未確認なら「未確認」と明示してください。

---

## 7. マイルストーン

### M0: リポジトリ初期化

目的: プロジェクトの骨格、設計文書、ビルド入口を作る。

成果物:

- README
- docs/architecture.md
- docs/protocol.md
- docs/milestones.md
- Windows host skeleton
- iPad app skeleton
- テスト用ディレクトリ

受入条件:

- Windows側の空ビルドが通る
- プロトコル仕様が文書化されている
- 以降のM1〜M8がREADMEから辿れる

---

### M1: Windows Synthetic Pen入力の単体検証

目的: Windows側でApple Pencil相当のペンイベントを注入できることを確認する。

実装:

- `windows/host/src/input/synthetic_pen.*`
- `CreateSyntheticPointerDevice(PT_PEN, 1, POINTER_FEEDBACK_NONE)`を使う
- `InjectSyntheticPointerInput`でDOWN/MOVE/UPを送る
- `pressure`, `tiltX`, `tiltY`を渡す
- 座標はWindows仮想スクリーン左上基準にする

テスト:

- `SyntheticPen`をモック可能にする
- adapter以外の状態遷移をユニットテストする
- 手動テスト用に「固定矩形を筆圧付きで描く」debug commandを作る

受入条件:

- KritaまたはWindows Ink対応テストアプリで線が描ける
- 筆圧値0〜1024のマッピングがテストされている
- DOWN後にUPが必ず送られる
- 例外時・切断時に強制UPするfail-safeがある

---

### M2: iPad Apple Pencil入力の取得

目的: iPad側でPencilの座標、筆圧、傾き情報を取得できることを確認する。

実装:

- `PencilCaptureView`
- `touch.type == .pencil`のみをPencil入力として扱う
- `preciseLocation(in:)`, `force`, `maximumPossibleForce`, `altitudeAngle`, `azimuthAngle(in:)`を取得する
- coalesced touchesを処理する
- 指タッチはPencil入力として送らない

テスト:

- 座標正規化のユニットテスト
- pressure正規化のユニットテスト
- tilt変換のユニットテスト
- 実機手動テスト項目を追加

受入条件:

- Pencil DOWN/MOVE/UPをログに出せる
- pressureが0.0〜1.0で取れる
- tiltX/tiltYの符号補正が設定可能
- 指タッチは無視または別イベントに分離されている

---

### M3: 入力プロトコルとWindows受信

目的: iPadからWindowsへPencilイベントを送り、Windows側でペン注入する。

プロトコル:

- 初期はlittle-endian binary packet
- magic, version, type, sequence, timestampを必ず持つ
- 座標は0.0〜1.0の正規化値
- pressureは0.0〜1.0
- tiltX/tiltYは-90〜90度
- DOWN/UPの欠落に備え、Windows側でtimeout強制UPを実装する

推奨パケット:

```c
#pragma pack(push, 1)
struct PenPacketV1 {
    uint32_t magic;       // 'IPEN' little endian
    uint16_t version;     // 1
    uint16_t type;        // 0=down, 1=move, 2=up, 3=hover, 4=cancel
    uint32_t seq;
    float x;              // 0..1
    float y;              // 0..1
    float pressure;       // 0..1
    int16_t tiltX;        // -90..90
    int16_t tiltY;        // -90..90
    uint16_t buttons;     // bit flags
    uint64_t tDeviceNs;
};
#pragma pack(pop)
```

受入条件:

- iPadからWindowsへDOWN/MOVE/UPが届く
- Windows側で線が描ける
- packet parserにfuzz/invalid packetテストがある
- seq欠落をログできる
- 切断時に強制UPする

---

### M4: 既存ディスプレイの映像転送

目的: まだ仮想ディスプレイを作らず、既存Windows画面をiPadへ表示する。

実装:

- Windows側capture interface
- debug用には低品質/低FPSでもよい
- 最終目標はH.264/HEVC系の低遅延ストリーム
- 映像と入力は別チャンネルにする
- 古いフレームは捨てる

受入条件:

- iPadにWindows画面が表示される
- 入力イベントと映像表示が同時に動く
- 送信FPS、受信FPS、encode latency、decode latencyのログを出せる

---

### M5: 座標マッピングとキャリブレーション

目的: iPad表示上のPencil位置とWindows入力座標を一致させる。

実装:

- `NormalizedPoint -> VirtualScreenPoint`変換
- Windowsディスプレイ配置を取得するadapter
- 回転補正
- アスペクト比補正
- DPI/スケール補正
- キャリブレーションUI

受入条件:

- 画面四隅、中央、斜線で位置ズレを確認できる
- Windows拡張ディスプレイ配置が変わっても再計算できる
- 右利き/左利き、iPad縦横回転を設定できる設計になっている

---

### M6: Indirect Display Driver / IddCxによる仮想ディスプレイ

目的: WindowsにiPad用の追加ディスプレイを認識させる。

実装方針:

- IddCxベースのIndirect Display Driverを第一候補にする
- 最初はWindows Driver Samplesの考え方に沿った最小driverにする
- driver内でネットワーク処理をしない
- driverは仮想モニターを作ることに集中する
- host.exeがその仮想モニターをキャプチャして送信する

受入条件:

- Windowsのディスプレイ設定に仮想モニターが表示される
- 解像度候補を最低3つ提示できる
- 60Hzを報告できる
- host.exeがその画面をキャプチャできる
- テスト署名/開発インストール手順をdocsに明記する

---

### M7: 低遅延化

目的: 描画用途として許容できる遅延に近づける。

実装:

- 入力は映像より優先する
- 送信キューを浅くする
- 古い映像フレームは破棄する
- B-frameなし設定を検討する
- encode/decode/network/renderの各区間を計測する
- jitter bufferを最小化する

受入条件:

- end-to-end latency測定手段がある
- ログにp50/p95の遅延を出せる
- 低遅延モードと高画質モードを分ける設計がある

---

### M8: 実用機能

目的: EasyCanvas風の使い勝手へ近づける。

実装候補:

- 筆圧カーブ
- 傾き補正
- パームリジェクション設定
- サイドボタン/ショートカットパネル
- undo/redoジェスチャー
- 接続先自動検出
- QRコード/ペアリングコード
- 再接続
- 診断画面
- ログエクスポート

受入条件:

- Clip Studio Paint / Krita / Photoshopの手動検証チェックリストがある
- 筆圧カーブ設定が保存される
- 接続断から復帰できる

---

### M9: 仮想HIDペンドライバ optional

目的: Synthetic Pointerで不足する互換性を補う。

実装方針:

- UMDF HID minidriverを第一候補にする
- vhidmini2型の構成を参考にする
- HID digitizer usageを使う
- X/Y, Tip Switch, In Range, Pressure, X Tilt, Y Tiltを報告する
- 最初からWinTab互換を目標にしない

受入条件:

- Device Manager上でHIDペン相当として見える
- Windows Ink対応アプリで筆圧が取れる
- インストール/アンインストール手順が明記されている
- ドライバ署名の制約をREADMEに明記する

---

## 8. 品質基準

### 8.1 入力品質

- DOWN/MOVE/UPの順序を保証する
- UP欠落時のfail-safeを必ず持つ
- pressureは0.0〜1.0からWindows側0〜1024へ変換する
- tiltX/tiltYは-90〜90へclampする
- 座標はWindows仮想スクリーン座標に変換する
- 指タッチはPencilイベントと混ぜない

### 8.2 映像品質

- フレームキューを深くしない
- 古いフレームは捨てる
- 入力遅延を映像品質より優先するモードを持つ
- 解像度、FPS、bitrateを設定可能にする設計にする

### 8.3 ログ品質

ログには以下を含める。

- 接続状態
- packet seq
- packet drop
- input latency
- capture latency
- encode latency
- network latency推定
- decode/render latency
- current display mapping
- forced pen-up発生回数

個人情報や不要な画面内容をログに保存しないこと。

---

## 9. テスト方針

### Unit Tests

必須:

- PenPacket encode/decode
- invalid packet rejection
- normalized coordinate mapping
- pressure mapping
- tilt clamp
- pen state machine
- timeout forced-up
- display rectangle mapping

### Integration Tests

可能な範囲で実装:

- loopback transport
- fake iPad packet generator
- synthetic pen debug drawer
- fake capture frame generator
- latency logger

### Manual Tests

`docs/manual-test-checklist.md`に次を含める。

- Windows 11 + Krita
- Windows 11 + Clip Studio Paint
- Windows 11 + Photoshop
- USB/IP接続または同一LAN接続
- iPad横向き
- iPad縦向き
- 筆圧弱/中/強
- ペンを右に倒す/左に倒す/手前に倒す/奥に倒す
- パーム接触しながら描く
- 接続断/復帰
- Windowsディスプレイ配置変更後の再接続

---

## 10. パフォーマンス目標

MVPでは数値未達でもよいが、測定可能にすることを必須とする。

目標値:

- 入力packet送信周期: coalesced touchを可能な限り反映
- 入力注入遅延: できるだけ数ms台
- 映像: 60fpsを初期目標、120fpsは後続
- end-to-end描画遅延: まず100ms未満、次に50ms未満を目指す
- 切断時forced-up: 100ms〜300ms以内で発火する設定を持つ

測定不能な最適化をしないでください。先に計測点を入れてください。

---

## 11. 既存描画アプリとの互換性

最初の対象はWindows Ink/TabletPC系入力です。

優先検証順:

1. Krita
2. Clip Studio Paint
3. Photoshop
4. Blender / ZBrush等は後続

WinTab専用互換は後回しです。Synthetic Pointerで不足が出た場合、HID minidriverまたは別互換レイヤーを検討してください。

---

## 12. Codexへの作業指示フォーマット

ユーザーから大きなタスクが与えられた場合、Codexは内部で次の形式に分解して進めてください。

```text
Task:
Target milestone:
Files to inspect:
Proposed minimal patch:
Build/test command:
Acceptance criteria:
Rollback plan:
```

実装後の報告は次の形式にしてください。

```text
Done:
Changed files:
Validation:
Known limitations:
Next:
```

---

## 13. 典型的な最初のタスク

新規リポジトリで最初にCodexへ依頼するタスクはこれです。

```text
M0/M1を実装してください。
まずリポジトリ構成を作り、Windows hostのCMake skeleton、PenPacket定義、座標/筆圧変換のユニットテスト、SyntheticPen adapterのinterfaceを追加してください。
実OS入力注入はadapterに閉じ込め、CIや非Windows環境ではmockでテストできるようにしてください。
ビルドとテストのスクリプトも追加し、READMEに次のマイルストーンを書いてください。
```

次のタスクはこれです。

```text
M1の実入力注入debug commandを実装してください。
Windows 10 1809以降のdesktop appでCreateSyntheticPointerDevice(PT_PEN, 1, POINTER_FEEDBACK_NONE)を作り、指定座標にDOWN/MOVE/UPを注入できるCLIを追加してください。
pressure 0.0〜1.0を0〜1024へ変換し、tiltX/tiltYを-90〜90でclampしてください。
失敗時はGetLastErrorをログしてください。
```

---

## 14. 実装時の重要メモ

- `PT_PEN`のSynthetic Pointerは1 pointerとして扱う
- `POINTER_PEN_INFO.pressure`は0〜1024
- `tiltX`と`tiltY`は-90〜90
- `ptPixelLocation`は仮想スクリーン左上基準
- iPad側座標は必ず0.0〜1.0へ正規化して送る
- Windows側でディスプレイ矩形にマッピングする
- iPadの向きとWindows側ディスプレイ回転は別物として扱う
- Apple Pencil USB-Cは筆圧非対応なので、筆圧検証時は対応Pencilを使うことをREADMEに明記する
- 実機検証が必要な項目をSimulatorテストで代替したと主張しないこと

---

## 15. ドキュメント更新規約

コード変更で以下が変わった場合、必ずdocsも更新してください。

- プロトコル形式
- ビルド手順
- Windows API選定
- iPad API選定
- 手動テスト手順
- 既知の制限
- マイルストーンの状態

`docs/milestones.md`には、各マイルストーンを次の状態で管理してください。

```text
Not started / In progress / Partially verified / Verified / Blocked
```

---

## 16. 最終プロダクト定義

このプロジェクトが「使える」と言える条件は以下です。

- WindowsにiPad用画面を表示できる
- iPad上でその画面を見ながらApple Pencilで描ける
- Windows側描画アプリで筆圧が取れる
- 座標ズレが実用範囲に収まる
- 切断時にペン押下状態が残らない
- 接続・切断・再接続が安定している
- 手動テストチェックリストが整備されている
- 未対応機能がREADMEに正直に書かれている

