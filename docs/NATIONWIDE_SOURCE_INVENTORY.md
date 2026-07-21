# Nationwide source inventory

## Purpose

全国47都道府県の政策計画入口を確認した後、各自治体で何の資料が揃い、どこからが未索引かを同じ形式で追跡します。

正本は [`data/catalog/nationwide_source_inventory.json`](../data/catalog/nationwide_source_inventory.json) です。

## Categories

1. `policy_plan`
   - 総合計画、長期ビジョン、総合戦略、政策集、施策方針等
2. `implementation_plan`
   - 実施計画、アクションプラン、中期実施計画
3. `kpi_source`
   - 数値目標、成果指標、KPI一覧
4. `annual_evaluation`
   - 年度別進捗、政策評価、成果評価
5. `budget`
   - 当初予算、補正予算、決算、主要施策成果
6. `project_evaluation`
   - 重点事業、事務事業評価、行政事業レビュー

## Statuses

- `not_indexed`: 公式資料入口をまだ固定していない
- `indexed`: 公式資料入口を固定した
- `reviewed`: 本文・数値・期間・単位を人が一次資料と照合した
- `linked`: 目標・実績・関連資料を正式に接続した

`not_indexed`は資料が存在しないことを意味しません。Jichi Insight側で公式入口をまだ固定していない状態です。

## Current matrix

2026年7月21日時点：

| Category | Indexed or higher | Reviewed or higher | Linked |
|---|---:|---:|---:|
| 政策計画 | 47/47 | 3/47 | 0/47 |
| 実施計画 | 2/47 | 2/47 | 0/47 |
| KPI・数値目標 | 3/47 | 3/47 | 0/47 |
| 年度評価 | 2/47 | 1/47 | 1/47 |
| 予算・決算 | 1/47 | 1/47 | 0/47 |
| 事業評価 | 0/47 | 0/47 | 0/47 |

### Reviewed or linked examples

- 北海道：政策計画・KPIをReviewed
- 宮城県：政策計画・実施計画・KPIをReviewedし、年度評価をKPIへ接続中
- 福岡県：政策計画・実施計画・KPI・予算をReviewed、年度評価入口をIndexed

## Quality boundaries

- 計画入口を確認しただけでKPI・年度評価・予算まで揃った扱いにしない
- `not_indexed`を0件・未公開・不存在と断定しない
- IndexedをReviewedへ自動昇格しない
- ReviewedをLinkedへ自動昇格しない
- 年度評価の値を現行計画の目標へ定義確認なしで接続しない
- 予算と決算、単年度と累計、人数と率を混同しない
- 比較可能性を確認していない指標を全国ランキングへ含めない

## Next execution order

1. 宮城県の残る年度実績接続
2. Wave 1の東京都、愛知県、大阪府、広島県、香川県、沖縄県
3. Wave 2を地域単位で実施計画・KPI・年度評価まで索引化
4. 予算・重点事業・事業評価を接続
5. 契約、監査、議会、公約へ縦接続
