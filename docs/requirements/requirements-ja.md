# Network Troubleshooting Retrieval Assistant 要件定義書

## 1. 背景・目的

通信ネットワークの障害対応では、正式なトラブルシューティング手順が存在するものの、

* マニュアルが長く分散している
* 正しい順序や必須チェックを即座に思い出せない
* 安全確認や検証が抜け落ちやすい

という課題がある。

本システムは **Troubleshooting Guide（Frontline LAN）を唯一の知識源** とし、
自然言語で入力されたネットワーク障害内容に対して、
**ガイド準拠・順序保証・安全重視**のトラブルシューティング手順を提示する
Retrieval Assistant を構築することを目的とする。

---

## 2. スコープ

### 2.1 対象範囲（In Scope）

* LAN ネットワーク障害（主に L1 / L2、一部 L3）
* ユーザ視点のネットワーク接続問題
* Troubleshooting Guide に記載された手順・方法・チェック

### 2.2 対象外（Out of Scope）

* サーバ・アプリケーション障害
* 認証・認可（IAM/AD）問題
* OS・端末内部の不具合
* Guide に記載のない独自ノウハウ

---

## 3. 全体アーキテクチャ概要

* **Retrieval Augmented Generation (RAG)** 構成
* ドキュメントは事前に chunking され、フェイズ別にメタデータ付与
* **Orchestrator（状態機械）** が各 Agent を順序制御

```
[Guardrail]
   ↓
[Identification]
   ↓
[Localization]
   ↓
[Analysis]
   ↓
[Action]
   ↓
[Validation]
   ↓
[Documentation]
   ↓
[Resolved | Loop]
```

---

## 4. ドキュメント処理方針

### 4.1 Chunking

* Recursive Text Splitter を使用
* 見出し単位を優先し、1手順（箇条書きセット）が1chunkに収まる粒度

### 4.2 Chunk メタデータ

各 chunk に以下を付与する：

| メタデータ         | 内容                                                                               |
| ------------- | -------------------------------------------------------------------------------- |
| phase         | identification / localization / analysis / action / verification / documentation |
| layer         | physical / switch / network（該当時）                                                 |
| artifact_type | procedure / checklist / method / concept / warning                               |
| priority      | MUST / SHOULD / OPTIONAL                                                         |

---

## 5. Agent 設計

### 5.1 Guardrail Agent

**目的**：ネットワーク以外の問題を除外

* 入力：自然文障害説明
* 出力：

  * network_related 判定
  * 非ネットワークの場合の理由

---

### 5.2 Identification Agent

**目的**：ユーザ症状の分類（問題の定義）

* 分類：

  * Can't connect
  * Connection drops
  * Network is slow

* 出力：

  * complaint_type
  * 前提条件（動作実績の有無、新規/既存）
  * 不足情報

---

### 5.3 Localization Agent

**目的**：問題箇所の切り分けと確認手段の提示

* スコープ分割：

  * single station
  * collision domain
  * broadcast domain
  * routed network

* 出力：

  * 想定影響範囲
  * 実施すべきテスト手順（順序付き）

※ physical layer を起点とする論理順序を遵守

---

### 5.4 Analysis Agent

**目的**：テスト結果から原因を特定

* 入力：テスト結果・観測情報
* 出力：

  * root cause（暫定/確定）
  * 根拠（evidence）
  * 信頼度

---

### 5.5 Action Agent

**目的**：是正措置の提示（安全最優先）

**必須出力項目**：

* 修復手順（guide 由来）
* 安全確認（safety checks）
* 影響評価（impact assessment）
* ロールバック手順

※ いずれか欠けた場合、次フェイズへ進行不可

---

### 5.6 Validation Agent

**目的**：解決確認と副作用検証

* 出力：

  * ユーザ確認手順
  * 再現テスト
  * 副作用チェック

---

### 5.7 Documentation & Feedback Agent

**目的**：ナレッジ化とフィードバック生成

* 出力：

  * インシデントサマリ
  * 原因・対策・検証結果
  * 再発防止ポイント
  * ユーザ向けフィードバック文

---

## 6. Orchestrator（制御要件）

* 各フェイズは **exit criteria** を満たさない限り遷移不可
* テスト未実施・証拠不足時は前フェイズへ差し戻し
* 解決しない場合は Identification または Localization にループ

---

## 7. 非機能要件

* ガイド外知識を用いない（hallucination 防止）
* 全出力は「ガイド由来」であることを説明可能
* 順序・安全・検証を強制

---

## 8. 成果物

* 動作デモ
* 実行可能なコードベース
* 本要件定義書
* 高レベルアーキテクチャ説明

---

## 9. 評価観点への対応

| 課題要求                     | 本設計での対応               |
| ------------------------ | --------------------- |
| Logical test sequence    | Orchestrator による状態制御  |
| Verify before proceeding | フェイズごとの exit criteria |
| Safety precautions       | Action Agent の必須出力    |
| Guide-based retrieval    | Phase フィルタ付き RAG      |

---

以上
