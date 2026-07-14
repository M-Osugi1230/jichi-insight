# Governance

## Roles

初期段階では、リポジトリ所有者がProduct Owner兼Maintainerを務めます。評価方法、公開基準、政治的中立性に関する変更は、通常のUI変更より高いレビュー基準を適用します。

## Decision hierarchy

プロダクト判断は次の順で整合性を確認します。

1. `docs/NORTH_STAR.md`
2. `docs/PROJECT_MEMORY.md`
3. `docs/PROJECT_CHARTER.md`
4. `docs/METHODOLOGY.md`
5. ADR
6. Product requirements / roadmap / individual issues

下位文書や短期的なIssueがNorth Starと矛盾する場合は、North Starを優先します。

## Decision classes

| Class | Example | Required process |
|---|---|---|
| Product | 画面、導線、検索 | PRと通常レビュー |
| Data | 新規資料、値の修正 | 出典確認とデータレビュー |
| Methodology | 評価式、閾値 | ADR、影響分析、変更履歴 |
| Editorial | 表現、中立性 | 編集方針確認 |
| Security/Privacy | 個人情報、脆弱性 | 非公開検討を優先 |
| North Star | 目的、対象、非交渉原則 | 専用PR、ADR、公開説明 |

## Protected principles

次は通常の機能PRで変更しません。

- 事実、比較、解釈、評価の分離
- 一次資料優先
- 推測補完の禁止
- 政治思想を採点しない
- 自治体、首長、議会の役割別評価
- 根拠と変更履歴の公開
- 訂正・反論手続
- 評価可能性が不足する場合に点数を出さない

変更する場合は、専用ADR、影響分析、公開説明、移行計画が必要です。

## Pre-merge North Star check

すべての重要PRで次を確認します。

- 利用者が自分で判断するための根拠を増やしているか
- 単なる話題性、批判性、ランキング性を優先していないか
- 公開されていないことと、未確認を区別しているか
- 首長と議会の責任を混同していないか
- データ量の拡大が品質を下げていないか
- 一次資料まで戻れるか

## Release authority

正式公開、評価方法の変更、North Starの変更、重大訂正はMaintainer承認を必要とします。
