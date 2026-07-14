# Governance

## Roles

初期段階では、リポジトリ所有者がProduct Owner兼Maintainerを務めます。評価方法、公開基準、政治的中立性に関する変更は、通常のUI変更より高いレビュー基準を適用します。

## Decision classes

| Class | Example | Required process |
|---|---|---|
| Product | 画面、導線、検索 | PRと通常レビュー |
| Data | 新規資料、値の修正 | 出典確認とデータレビュー |
| Methodology | 評価式、閾値 | ADR、影響分析、変更履歴 |
| Editorial | 表現、中立性 | 編集方針確認 |
| Security/Privacy | 個人情報、脆弱性 | 非公開検討を優先 |

## Protected principles

次は通常の機能PRで変更しません。

- 事実と評価の分離
- 一次資料優先
- 推測補完の禁止
- 政治思想を採点しない
- 根拠と変更履歴の公開
- 訂正・反論手続
- 評価可能性が不足する場合に点数を出さない

変更する場合は、専用ADR、公開説明、移行計画が必要です。

## Release authority

正式公開、評価方法の変更、重大訂正はMaintainer承認を必要とします。
