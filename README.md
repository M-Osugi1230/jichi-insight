# Jichi Insight

**約束・予算・実行・成果を、ひとつにつなぐ。**

Jichi Insight（自治体インサイト）は、自治体が公開する政策計画、財政、事業、契約、政策評価、監査、議会、首長公約を構造化し、「何を目指し、いくら使い、何を実行し、何が変わり、どう説明したか」を一次資料から確認できるようにする自治体IR・行政アカウンタビリティ基盤です。

## Product status

`Phase 9 complete / Phase 10 in progress / 47 prefectures published / pre-alpha`

- 全国登録: 47 / 47
- 公式ホームページ確認: 47 / 47
- 現行政策計画確認: 47 / 47
- Evidence-backed Reviewed数値目標: 47 / 47
- 全国公開ページ: 47 / 47
- Phase 10同一粒度完了: 0 / 47
- 独自の政策達成評価: 0件
- 比較可能性未確認の全国ランキング: 0件

Phase 9で、全47都道府県の政策目標とEvidence-backed Reviewed基盤が揃いました。Phase 10では、年度実績、予算、決算、重点事業、契約、議会、監査、首長公約を同じ品質ゲートで接続します。

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
→ actuals_linked
→ published
```

資料入口を確認した`indexed`と、値・期間・対象範囲を確認した`reviewed`、同じ政策系列へ接続した`linked`は別の状態です。

## Phase 10 — Nationwide uniform depth

47都道府県すべてを、次の11項目で同じ最低粒度へ引き上げます。

1. 政策・KPI
2. Evidence Packet
3. 年度実績
4. 予算
5. 決算
6. 重点事業
7. 契約
8. 議会
9. 監査
10. 首長公約
11. 公開検証

現在の保守的な基準値:

- Reviewed政策目標: 47 / 47
- Reviewed Evidence: 47 / 47
- 年度実績 linked: 1 / 47
- 予算 indexed以上: 2 / 47
- 決算 reviewed以上: 1 / 47
- 重点事業 indexed以上: 2 / 47
- 契約 indexed以上: 2 / 47
- 議会 indexed以上: 1 / 47
- 監査 indexed以上: 0 / 47
- 首長公約 indexed以上: 1 / 47

正本:

- [`data/catalog/phase10_uniformity.json`](data/catalog/phase10_uniformity.json)
- [`data/catalog/phase10_execution_queue.json`](data/catalog/phase10_execution_queue.json)
- [`data/catalog/phase10_completion.json`](data/catalog/phase10_completion.json)
- [Phase 10 nationwide uniform depth](docs/PHASE10_VERTICAL_LINKAGE.md)

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
- [Project charter](docs/PROJECT_CHARTER.md)
- [Product requirements](docs/PRODUCT_REQUIREMENTS.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Data model](docs/DATA_MODEL.md)
- [Methodology](docs/METHODOLOGY.md)
- [Editorial policy](docs/EDITORIAL_POLICY.md)
- [Assembly accountability](docs/ASSEMBLY_ACCOUNTABILITY.md)
- [Nationwide expansion](docs/NATIONWIDE_EXPANSION.md)
- [Data quality](docs/DATA_QUALITY.md)
- [Corrections and right of reply](docs/CORRECTIONS.md)
- [Roadmap](docs/ROADMAP.md)
- [Phase 9 execution](docs/PHASE9_EXECUTION.md)
- [Phase 10 nationwide uniform depth](docs/PHASE10_VERTICAL_LINKAGE.md)
- [Release checklist](docs/RELEASE_CHECKLIST.md)
- [Risk register](docs/RISK_REGISTER.md)

## Current execution order

1. 宮城県の年度実績を予算・決算・重点事業・契約へ接続
2. 福岡県のReviewed財政・決算を政策目標へ接続
3. 残る7地域拠点を同じ深度へ引き上げ
4. 残る38県を7地域バッチで処理
5. 議会、監査、首長公約を政策系列へ接続
6. 全47都道府県の公開検証

## License

コード、方法論、データの権利関係は分離して扱います。ライセンス確定前の内容は、権利者の明示的な許可なく再利用できません。詳細は [DATA_POLICY.md](DATA_POLICY.md) を参照してください。
