# ADR 0002: Evidence-first publishing

- Status: Accepted
- Date: 2026-07-15

## Context

自治体・首長・議会を扱うため、誤った数値や評価は一般的なコンテンツ誤りより大きな影響を持ちます。

## Decision

すべての主要な事実・評価をEvidenceへ接続します。自動抽出データは`extracted`として保存し、評価や主要表示には原則`reviewed`以上だけを使用します。出典を確認できない情報は推測で埋めません。

## Consequences

- 公開速度は遅くなる
- 調査結果を再現しやすい
- 訂正対応が容易になる
- データ件数と品質深度を分けて管理する必要がある
