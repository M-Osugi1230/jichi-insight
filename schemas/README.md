# Data contracts

Jichi Insightは、画面や収集処理が独自の解釈でデータを補わないように、JSON Schemaを公開データの契約として使用します。

## Registry

`schemas/registry.json` が、検証対象となるスキーマと代表fixtureの一覧です。

新しいエンティティを追加する場合は、次を同じPRに含めます。

1. JSON Schema
2. 明確に架空と分かるfixture
3. Registry entry
4. Repository validation
5. Reference integrity test
6. Data model documentation

## Core entities

| Entity | Responsibility |
|---|---|
| Source | 一次資料の書誌情報・該当箇所・確認状態 |
| Municipality | 自治体の安定IDと基本属性 |
| Fiscal record | 年度・会計・予算段階・指標ごとの財政値 |
| Project | 個別事業の目的、予算、KPI |
| Contract | 事業と契約先・契約方式・金額の接続 |
| KPI | 基準値、目標値、実績、評価可能性 |
| Executive term | 首長の役職・任期・選挙・公約資料 |
| Promise | 公約原文、期限、目標、関連事業、進捗 |
| Assembly | 議会の任期、定数、会派、委員会 |
| Proposal | 議案、提出主体、結果、関連事業 |
| Vote | 採決方法、結果、議員別賛否の公開状況 |
| Inspection trip | 視察目的、参加者、費用、報告、政策反映 |
| Evidence packet | 一つの公開判断を支える根拠と未解決事項 |

## Status semantics

### Review status

- `verified`: 一次資料と人手による二重確認が完了
- `reviewed`: 一次資料と照合済み
- `extracted`: 候補値を抽出済み、未レビュー
- `inferred`: 資料間の推定を含む
- `missing`: 必要情報を確認できない

### Availability / value status

- `available`
- `published`
- `not_published`
- `not_found`
- `not_applicable`
- `unknown`

利用可能なenumはエンティティごとに限定します。`null`、0、空文字で意味の違いを隠しません。

## Amount rules

- 金額は原則として円単位の整数で保持
- 表示時に億円・万円へ変換
- 当初予算、補正後予算、執行額、決算額を区別
- 金額がない場合は、値と状態を分ける
- マイナスを許可する指標が必要になった場合は、専用指標として定義を見直す

## Reference integrity

Repository validationは、fixture間で次を確認します。

- 自治体 → 財政、事業、首長任期、議会
- 事業 → 契約、KPI、公約
- 議会 → 議案、視察
- 議案 → 採決
- すべての重要エンティティ → Source
- Evidence packet → 対象エンティティとSource

## Change control

既存フィールド、enum、ID規則の破壊的変更にはADRと移行手順が必要です。新しい値を追加する場合も、既存画面と比較ロジックへの影響を確認します。
