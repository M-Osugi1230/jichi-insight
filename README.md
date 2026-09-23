# Jichi Insight

**約束・予算・実行・成果を、ひとつにつなぐ。**

Jichi Insight（自治体インサイト）は、自治体が公開する政策計画、財政、事業、契約、政策評価、監査、議会、首長公約を構造化し、「何を目指し、いくら使い、何を実行し、何が変わり、どう説明したか」を一次資料から確認できるようにする自治体IR・行政アカウンタビリティ基盤です。

## Product status

`Phase 12 complete / Phase 13 active / 47 prefectures complete / 20 designated cities inventoried / pre-alpha`

- 全国47都道府県: Phase 11まで完了
- Phase 11個票基盤: 47都道府県・15,327レコード
- 政令指定都市 Source Inventory: 20 / 20
- Phase 13 Reviewed reference: 2市（北九州市、福岡市）
- Phase 13 Reviewed complete: 3市（札幌市、仙台市、さいたま市）
- Phase 13 Review in progress: 1市（千葉市）
- Phase 13 Pending record review: 14市
- 千葉市現行計画: 189 / 189事業identity、406 work itemsをstructured化済み
- 千葉市旧計画: 360 / 360事業identity、再掲68 / 68を一次identityへ解決済み
- 千葉市Versioned Linkage: 構造的一致60関係＋公式PDF手動確認6関係、計66関係をReviewed continuedとして昇格
- 独自の政策達成評価: 0件
- 比較可能性未確認の全国・都市ランキング: 0件

Phase 10で全国47都道府県の共通文書スコープ、Phase 11で個票レベルのReviewed接続またはReviewed最大到達深度、Phase 12で20政令指定都市の公式Source Inventoryを完成させました。現在はPhase 13として、政令指定都市を個票レベルへ深掘りしています。公式資料が不足する場合も推測で埋めず、何が未接続かを明示します。

進捗の正本は `data/catalog/phase13_designated_city_review_queue.json` と各Phase completion manifestです。READMEは人向けの要約であり、状態が競合する場合はmachine-readable catalogを優先します。

## Evidence chain

```text
Promise        計画・選挙で何を約束したか
   ↓
Money          いくら確保し、いくら使ったか
   ↓
Action         どの事業・契約を実行したか
   ↓
Result         目標に対して何が変わったか
   ↓
Accountability 誰が判断し、どう説明したか
```

## Non-negotiable principles

- 事実、比較、解釈、評価を分ける
- 一次資料を優先する
- 未公開・未確認・不明を推測で補完しない
- 政策思想、政党、人物の好悪を採点しない
- 出典、更新日、抽出方法、レビュー状態を表示する
- 自治体、首長、議会、監査を役割別に扱う
- 訂正、反論、変更履歴を残す
- 根拠が不足する場合は評価しない
- `not_indexed`を「存在しない」に読み替えない
- 比較可能性が未確認の指標をランキングへ含めない

## Quality states

```text
registered
→ official_entry_verified
→ plan_entry_indexed
→ current_plan_confirmed
→ source_cataloged
→ reviewed_data
→ actuals_linked or reviewed_maximum_depth
→ published
```

`indexed`、`reviewed`、`linked`、`reviewed_maximum_depth`、`published`は別の状態です。計画基準値を年度実績へ流用せず、全国参考値を自治体実績へ読み替えません。

## Phase 10 — Nationwide uniform depth

2026年8月1日、47都道府県すべてが政策・KPI、Evidence、年度実績、予算、決算、重点事業、契約、議会、監査、首長公約、公開検証の11項目共通ゲートへ到達しました。

Phase 10の完了は**全国の文書スコープ**です。個別目標、予算科目、事業、契約、議会発言、監査指摘をすべて一対一接続したという意味ではありません。

正本:

- [`data/catalog/phase10_completion.json`](data/catalog/phase10_completion.json)
- [Phase 10 nationwide uniform depth](docs/PHASE10_VERTICAL_LINKAGE.md)

## Phase 11 — Nationwide record-level linkage

### Wave 1 complete

北海道、宮城県、東京都、福岡県の861個票を共通Schemaへ正規化しました。

- Linked: 420
- Partial: 58
- Not linked: 383

### Wave 2 complete

愛知県、大阪府、広島県、香川県、沖縄県の5拠点を完了しました。

| 都道府県 | レコード | 境界 |
|---|---:|---|
| 愛知県 | 56 | 62系列、current値1系列欠損、目標改定と再掲を保持 |
| 大阪府 | 83 | 77 Linked、6 Partial、旧系列と事業因果は未接続 |
| 広島県 | 62 | 59 Linked、3測定待ちPartial、複合原文を保持 |
| 香川県 | 135 | 141表示箇所、再掲6、R7→R8改定87を保持 |
| 沖縄県 | 375 | 計画基準値→R9目標の最大深度、全件Partial |

沖縄県の現在の正本は計画カタログでありReviewed年度実績ではありません。375件すべてで`annual_actual`を未接続のまま保持し、全国値も参考情報として分離しています。

Wave 2統合ゲート:

- 5拠点・711件
- 725指標系列
- current値あり340系列
- current値欠損・未接続385系列
- 進捗目標または明示的target 602系列
- 政策達成評価0件
- 比較対象への昇格0件

正本:

- [`data/catalog/phase11_wave1_completion.json`](data/catalog/phase11_wave1_completion.json)
- [`data/catalog/phase11_wave2_completion.json`](data/catalog/phase11_wave2_completion.json)
- [`data/catalog/phase11_execution_queue.json`](data/catalog/phase11_execution_queue.json)
- [`schemas/phase11_record_linkage.schema.json`](schemas/phase11_record_linkage.schema.json)
- [Phase 11 methodology](docs/PHASE11_RECORD_LINKAGE.md)

### Wave 3 complete

残る38県・13,755レコードを都道府県コード順に処理し、全件を共通SchemaとEvidence・欠損状態・非評価境界へ通しました。

- 完了県: 38 / 38
- Reviewed最大到達深度: 13,755レコード
- Linkedへ推測昇格したレコード: 0
- Partial: 13,755
- 政策達成・因果関係・全国比較の独自判定: 0

Phase 11全体では47都道府県・15,327レコードです。

## Phase 12 — Designated-city source inventory

2026年8月12日、20政令指定都市すべての公式Source Inventoryを完了しました。

- Reviewed reference: 2市（北九州市、福岡市）
- Source inventory complete: 18 / 18
- Source inventory partial: 0
- Pending source inventory: 0

正本:

- [`data/catalog/phase12_designated_city_execution_queue.json`](data/catalog/phase12_designated_city_execution_queue.json)
- [Phase 12 designated cities](docs/PHASE12_DESIGNATED_CITIES.md)

## Phase 13 — Designated-city record review

Status: `in_progress`

現在のCanonical queue:

- Reviewed reference: 2市（北九州市、福岡市）
- Reviewed complete: 3市（札幌市、仙台市、さいたま市）
- Review in progress: 1市（千葉市）
- Pending record review: 14市
- Blocked source inventory: 0市

千葉市では現行2026〜2028年度実施計画の189事業identityと406 work items、旧2023〜2025年度360事業identityの全件レビューを完了しました。旧計画の再掲68件も一次identityへ解決済みです。Versioned Linkageでは、正規化事業名・施策コード・担当組織が同時に整合する60関係を自動初回Reviewed continuedへ昇格し、自動基準から外れた完全同名6関係も旧・現の公式PDFで事業目的・取組項目・施策移動・所管変更を個別確認して手動Reviewedへ追加しました。現在は計66関係をReviewedとし、残りは名称類似から推測せずEvidenceレビューを継続しています。

正本:

- [`data/catalog/phase13_designated_city_review_queue.json`](data/catalog/phase13_designated_city_review_queue.json)
- [Roadmap](docs/ROADMAP.md)

## Repository map

```text
apps/web/       公開サイト
pipelines/      収集・抽出・正規化・検証
data/           カタログ、Reviewedデータ、Evidence
schemas/        公開データのJSON Schema
scripts/        リポジトリ・データ・公開品質検証
tests/          回帰テスト
docs/           方針、設計、ロードマップ、方法論
.github/        CI、Issue、PR、依存関係更新
```

## Local setup

### Web

```bash
corepack enable
pnpm install
pnpm dev
```

### Repository validation

```bash
python -m pip install -e ".[dev]"
python scripts/validate_repository.py
pytest
```

### Full check

```bash
pnpm check
```

## Documentation

- [North Star](docs/NORTH_STAR.md)
- [Project Memory](docs/PROJECT_MEMORY.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Data model](docs/DATA_MODEL.md)
- [Methodology](docs/METHODOLOGY.md)
- [Editorial policy](docs/EDITORIAL_POLICY.md)
- [Data quality](docs/DATA_QUALITY.md)
- [Corrections and right of reply](docs/CORRECTIONS.md)
- [Roadmap](docs/ROADMAP.md)
- [Phase 10 nationwide uniform depth](docs/PHASE10_VERTICAL_LINKAGE.md)
- [Phase 11 record linkage](docs/PHASE11_RECORD_LINKAGE.md)
- [Release checklist](docs/RELEASE_CHECKLIST.md)

## License

コード、方法論、データの権利関係は分離して扱います。ライセンス確定前の内容は、権利者の明示的な許可なく再利用できません。詳細は [DATA_POLICY.md](DATA_POLICY.md) を参照してください。
