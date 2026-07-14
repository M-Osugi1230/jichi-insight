# ADR 0001: Static-first monorepo

- Status: Accepted
- Date: 2026-07-15

## Context

初期対象は3自治体で、更新頻度よりも追跡可能性、低コスト、安全性が重要です。一方、将来は全国検索、履歴、API、レビューUIが必要になります。

## Decision

Next.jsのWebとPythonのデータ処理を単一リポジトリで管理し、初期公開はReviewedデータから静的生成します。スキーマを両者の契約とし、将来PostgreSQLへ移行できるIDと時系列モデルを採用します。

## Consequences

- 初期運用が単純で、公開面への攻撃面が小さい
- PRでデータ差分をレビューできる
- リアルタイム更新には向かない
- データ増加時にDB移行が必要
