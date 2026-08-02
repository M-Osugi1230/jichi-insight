# Jichi Insight

**約束・予算・実行・成果を、ひとつにつなぐ。**

Jichi Insight（自治体インサイト）は、自治体が公開する政策計画、財政、事業、契約、政策評価、監査、議会、首長公約を構造化し、「何を目指し、いくら使い、何を実行し、何が変わり、どう説明したか」を一次資料から確認できるようにする自治体IR・行政アカウンタビリティ基盤です。

## Product status

`Phase 10 complete / Phase 11 Wave 2 complete / Wave 3 active / 47 prefectures published / pre-alpha`

- 全国登録・公式入口・現行政策計画: 47 / 47
- Evidence-backed Reviewed数値目標: 47 / 47
- Phase 10文書スコープ同一粒度: 47 / 47
- Phase 11 Wave 1: 4都道府県・861個票を全件正規化
- Phase 11 Wave 2: 5地域拠点・711件・725系列を全件正規化
- Wave 2 current値あり / 欠損・未接続: 340 / 385系列
- Wave 3: 残る38県を都道府県コード順に処理中
- 次の対象: 青森県（02）、岩手県（03）
- 独自の政策達成評価: 0件
- 比較可能性未確認の全国ランキング: 0件

Phase 10は全国の文書スコープを完成させました。Phase 11では個票接続またはReviewed最大到達深度へ進めています。公式資料が不足する場合も推測で埋めず、何が未接続かを明示します。

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

### Wave 3 active

残る38県を都道府県コード順に処理します。各県はReviewed個票接続またはReviewed最大到達深度へ必ず到達させます。最初は青森県（02）、次に岩手県（03）です。

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
