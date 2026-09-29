# Jichi Insight

**約束・予算・実行・成果を、ひとつにつなぐ。**

Jichi Insight（自治体インサイト）は、自治体が公開する政策計画、財政、事業、契約、政策評価、監査、議会、首長公約を構造化し、「何を目指し、いくら使い、何を実行し、何が変わり、どう説明したか」を一次資料から確認できるようにする自治体IR・行政アカウンタビリティ基盤です。

## Product status

`Phase 14 active / Phase 13 complete / 47 prefectures complete / 20 designated cities reviewed / pre-alpha`

- 全国47都道府県: Phase 11まで完了
- Phase 11個票基盤: 47都道府県・15,327レコード
- 政令指定都市 Source Inventory: 20 / 20
- Phase 13 Reviewed reference: 2市（北九州市、福岡市）
- Phase 13 Reviewed complete: 18市（札幌市、仙台市、さいたま市、千葉市、横浜市、川崎市、相模原市、新潟市、静岡市、浜松市、名古屋市、京都市、大阪市、堺市、神戸市、岡山市、広島市、熊本市）
- Phase 13 Review in progress: 0市
- Phase 13 Pending record review: 0市
- Phase 14 target universe: 67自治体（中核市62＋県庁所在地only 5）
- Phase 14 Source Inventory complete: 10 / 67（Wave 1 北海道・東北 complete）
- Phase 14 Source Inventory in progress: 1（Wave 2 水戸市）
- 千葉市現行計画: 189 / 189事業identity、406 work itemsをstructured化済み
- 千葉市旧計画: 360 / 360事業identity、再掲68 / 68を一次identityへ解決済み
- 千葉市Versioned Linkage: 構造的一致60関係＋公式PDF手動確認6関係、計66関係をReviewed continuedとして昇格
- 独自の政策達成評価: 0件
- 比較可能性未確認の全国・都市ランキング: 0件

Phase 10で全国47都道府県の共通文書スコープ、Phase 11で個票レベルのReviewed接続またはReviewed最大到達深度、Phase 12で20政令指定都市の公式Source Inventory、Phase 13で全20政令指定都市のv1 record-review foundationを完成させました。北九州市・福岡市をReviewed referenceとして保持し、残る18市は自治体別completion contractまで到達しています。公式資料が不足・未公表・未解決の場合も推測で埋めず、何が未接続かを明示します。

進捗の正本は `data/catalog/phase14_core_capital_execution_queue.json`、`data/catalog/phase14_core_capital_target_registry.json`、各Phase completion manifestです。READMEは人向けの要約であり、状態が競合する場合はmachine-readable catalogを優先します。

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

Status: `complete`（2026-09-29）

全20政令指定都市のv1 record-review foundationを完了しました。

- Reviewed reference: 2市（北九州市、福岡市）
- Reviewed complete: 18 / 18市
- Review in progress: 0市
- Pending record review: 0市
- Blocked source inventory: 0市
- 独自の政策達成評価: 0件
- 因果効果の独自判定: 0件
- 比較可能性未確認の都市ランキング: 0件

18市それぞれについて、現行計画identity、自治体が公式に設けている実施・進行管理層、利用可能な年度実績、一般会計財政トップライン、version / availability / evidence boundaryを宣言した`declared_review_package_v1`までレビューし、Schema・Evidence coverage・回帰テストで固定しました。未公表の年度実績、旧計画の結果、source-reported evaluation、丸められた財政値を推測で補完・再解釈していません。

Phase 13の完了は、全政策・KPI・事業・契約・補助金・予算科目・決算科目を完全接続したことを意味しません。都市ごとの`deferred_depth`に追加レビュー対象を明示し、比較可能性が別途確認されるまでは都市間ランキングへ昇格しません。

正本:

- [`data/catalog/phase13_completion.json`](data/catalog/phase13_completion.json)
- [`data/catalog/phase13_designated_city_review_queue.json`](data/catalog/phase13_designated_city_review_queue.json)
- [`schemas/phase13_completion.schema.json`](schemas/phase13_completion.schema.json)
- [Roadmap](docs/ROADMAP.md)


## Phase 14 — Core cities and prefectural capitals source inventory

Status: `in_progress`（2026-09-29）

Phase 13で完了した20政令指定都市を除き、中核市と県庁所在地の公式Source Inventoryを拡張します。

- Current core cities: 62
- Prefectural capitals remaining after Phase 13: 32
- Core-city / capital overlap: 27
- Prefectural-capital-only: 5（新宿区、津市、山口市、徳島市、佐賀市）
- Unique Phase 14 targets: 67
- Wave 1 北海道・東北: 10 / 10 source_inventory_complete
- Wave 2 関東: 12 / 12 source_inventory_complete
- Wave 3 北陸・甲信: 6 / 6 source_inventory_complete
- Wave 4 東海: 6 / 6 source_inventory_complete
- Wave 5 近畿: 大津市から source inventory開始
- Reviewed promotion: 0（Phase 15で実施）

Wave 1北海道・東北10市、Wave 2関東12自治体、Wave 3北陸・甲信6市、Wave 4東海6自治体まで完了しました。Wave 4では岐阜市、豊橋市、岡崎市、一宮市、豊田市、津市をSource Inventory化し、岐阜市の固定終期未確認、一宮市の第8次計画transition、津市の期間を定めない基本構想＋固定期間基本計画、各市の自治体自己評価・ローリング結果を独自評価へ変換しない境界を保持しています。

正本:

- [`data/catalog/phase14_core_capital_target_registry.json`](data/catalog/phase14_core_capital_target_registry.json)
- [`data/catalog/phase14_core_capital_execution_queue.json`](data/catalog/phase14_core_capital_execution_queue.json)
- [`schemas/phase14_municipality_source_inventory.schema.json`](schemas/phase14_municipality_source_inventory.schema.json)
- [`tests/test_phase14_core_capital_registry.py`](tests/test_phase14_core_capital_registry.py)
- [`tests/test_phase14_wave1_source_inventory.py`](tests/test_phase14_wave1_source_inventory.py)
- [`tests/test_phase14_wave2_source_inventory.py`](tests/test_phase14_wave2_source_inventory.py)
- [`tests/test_phase14_wave3_source_inventory.py`](tests/test_phase14_wave3_source_inventory.py)
- [`tests/test_phase14_wave4_source_inventory.py`](tests/test_phase14_wave4_source_inventory.py)

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
