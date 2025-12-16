## 1. テストシナリオ サマリ表（Identify〜Verify）

| ID | テストインプット（ユーザ入力そのまま） | Identify（facts/keywords取得確認） | Locate（評価の主対象） | Analyze | Action | Verify |
|----|--------------------------------------|----------------------------------|------------------------|---------|--------|--------|
| P1 | 新設席でリンクしない。wiremap FAIL | 事実/語抽出できるか | wiremap→lengthの論理分岐 | 終端不良特定 | 再成端 | AutoTest PASS |
| P2 | Cat6A認証でFAIL、時々リンクダウン | 認証FAIL/断続抽出 | 設定確認→認証→TDR | 性能不足特定 | 交換/再成端 | 再認証 PASS |
| P3 | 特定時間だけ遅くなる | 時間依存症状抽出 | 通常/再現時分岐 | 環境要因 | 経路変更 | 再発なし |
| F1 | 光リンクが上がらない | 光/リンク抽出 | 極性→清掃→OLTS | 汚染/極性 | 清掃/再接続 | 損失OK |
| N1 | サーバに繋がらない（単一端末） | 接続不可/単一抽出 | Link→IP→GW分岐 | 設定起因 | 設定修正 | 接続OK |
| N2 | しばらくすると切れる | 断続症状抽出 | 再現待ち→取得 | 再送/Timeout | MTU/経路 | 再発なし |
| N3 | このPCだけ遅い | 単一端末抽出 | 比較→物理/設定 | Duplex不一致 | 設定修正 | 性能回復 |
| S1 | スイッチ配下で遅延 | スイッチ語抽出 | ミラー観測分岐 | 輻輳 | 設定修正 | 遅延解消 |

## 2. 各テストシナリオ詳細（Identify〜Verify）

---

### P1 新設席でリンクしない。wiremap FAIL
**Input**
新設席でリンクしない。wiremap FAIL

**Identify（評価対象）**
- facts:
  - 新設席である
  - リンクしない
  - wiremap が FAIL
- extracted_keywords:
  - wiremap
  - link
  - FAIL
- media_hint: physical

**Locate**
1. AutoTest 実行
   - FAIL → wiremap 詳細確認
2. wiremap 結果判定
   - open/short/miswire
3. length 測定
   - 異常距離で終端/途中切り分け

**Analyze**
- RJ45圧着またはパンチダウン不良

**Action**
- 終端再圧着 / 再パンチ

**Verify**
- AutoTest 再実行 → PASS

---

### P2 Cat6A認証でFAIL、時々リンクダウン
**Input**
Cat6A認証でFAIL、時々リンクダウン

**Identify**
- facts:
  - Cat6A認証で FAIL
  - 時々リンクダウン
- extracted_keywords:
  - Cat6A
  - 認証
  - FAIL
  - リンクダウン
- media_hint: physical

**Locate**
1. テスタ設定確認（Cat6A / Channel）
2. AutoTest
3. 認証テスト（IL/NEXT）
   - marginal → TDR/TDX

**Analyze**
- 長さ超過 / 接点劣化

**Action**
- ケーブル短縮 / 再成端 / 交換

**Verify**
- 再認証テスト PASS

---

### P3 特定時間だけ遅くなる
**Input**
特定時間だけ遅くなる

**Identify**
- facts:
  - 特定時間だけ遅くなる
- extracted_keywords:
  - 遅い
  - 時間
- media_hint: unknown

**Locate**
1. 通常時 AutoTest（想定 PASS）
2. 問題時間帯に再テスト
3. ノイズ/インパルス測定

**Analyze**
- 環境要因によるノイズ混入

**Action**
- 配線経路変更 / シールド / Fiber化

**Verify**
- 同時間帯で再発なし

---

### F1 光リンクが上がらない
**Input**
光リンクが上がらない

**Identify**
- facts:
  - 光リンクが上がらない
- extracted_keywords:
  - 光
  - link
- media_hint: physical

**Locate**
1. TX/RX 極性確認
2. VFL 確認
3. 端面清掃
4. OLTS 測定

**Analyze**
- 端面汚染または極性不一致

**Action**
- 清掃 / 極性修正 / 再接続

**Verify**
- OLTS 損失が基準内

---

### N1 サーバに繋がらない（単一端末）
**Input**
サーバに繋がらない（単一端末）

**Identify**
- facts:
  - サーバに繋がらない
  - 単一端末
- extracted_keywords:
  - サーバ
  - 端末
- media_hint: network

**Locate**
1. Link 状態確認
2. IP 設定確認
3. Ping GW
   - 成功/失敗で分岐

**Analyze**
- IP / DNS 設定不備

**Action**
- 設定修正

**Verify**
- Ping / アプリ接続成功

---

### N2 しばらくすると切れる
**Input**
しばらくすると切れる

**Identify**
- facts:
  - 一定時間後に切断
- extracted_keywords:
  - 切れる
- media_hint: unknown

**Locate**
1. Ping 連続実行
2. 再現時にキャプチャ取得

**Analyze**
- 再送増加 / タイムアウト

**Action**
- MTU / 経路調整

**Verify**
- 長時間再発なし

---

### N3 このPCだけ遅い
**Input**
このPCだけ遅い

**Identify**
- facts:
  - このPCだけ遅い
- extracted_keywords:
  - PC
  - 遅い
- media_hint: unknown

**Locate**
1. 他PCと Ping/Throughput 比較
2. ケーブル入替
3. Duplex/Speed 確認

**Analyze**
- Duplex 不一致

**Action**
- Auto-negotiation 修正

**Verify**
- 再送消失・性能回復

---

### S1 スイッチ配下で遅延
**Input**
スイッチ配下で遅延

**Identify**
- facts:
  - スイッチ配下で遅延
- extracted_keywords:
  - スイッチ
  - 遅延
- media_hint: switch

**Locate**
1. 設定バックアップ
2. ミラーポート設定
3. トラフィック観測
   - oversubscription 考慮

**Analyze**
- 輻輳 / 再送増加

**Action**
- ポート / VLAN / QoS 修正

**Verify**
- 遅延再発なし
