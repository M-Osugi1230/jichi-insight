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
- Phase 10の5層公式資料入口: 47 / 47
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

資料入口を確認した`indexed`と、内容・期間・対象範囲・出典を確認した`reviewed`、同じ政策系列へ一対一で接続した`linked`は別の状態です。

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

### 2026-08-01時点の保守的な基準値

- Reviewed政策目標: 47 / 47
- Reviewed Evidence: 47 / 47
- 年度実績・予算・決算・重点事業・監査の5層すべて入口確認以上: 47 / 47
- 5層すべてReviewed: 46 / 47
  - 宮城県の決算は入口確認
- 年度実績 Reviewed以上: 47 / 47
  - うちLinked: 1 / 47（宮城県）
- 予算 Reviewed以上: 47 / 47
- 決算 Reviewed以上: 46 / 47
- 重点事業 Reviewed以上: 47 / 47
- 監査 Reviewed以上: 47 / 47
- 契約 indexed以上: 2 / 47
- 議会 indexed以上: 2 / 47
- 首長公約 indexed以上: 1 / 47
- 11項目すべて同一粒度完了: 0 / 47

5層の公式資料レビューは全国まで到達しました。ただし、これは資料の内容・期間・役割・未接続範囲を確認した状態です。政策目標と年度実績、予算額、決算額、重点事業、監査意見を一対一で接続したことを意味しません。

新計画初年度、旧計画評価、年度途中モニタリング、過年度決算、評価制度入口しか確認できない場合は、その制約を各地域台帳と公開ページに明記しています。

正本:

- [`data/catalog/phase10_uniformity.json`](data/catalog/phase10_uniformity.json)
- [`data/catalog/phase10_completion.json`](data/catalog/phase10_completion.json)
- [`data/catalog/phase10_regional_depth_index.json`](data/catalog/phase10_regional_depth_index.json)
- [`data/catalog/phase10_reference_depth_reviews.json`](data/catalog/phase10_reference_depth_reviews.json)
- [`data/catalog/phase10_anchor_depth_reviews.json`](data/catalog/phase10_anchor_depth_reviews.json)
- [`data/catalog/phase10_tohoku_depth_reviews.json`](data/catalog/phase10_tohoku_depth_reviews.json)
- [`data/catalog/phase10_kanto_depth_reviews.json`](data/catalog/phase10_kanto_depth_reviews.json)
- [`data/catalog/phase10_chubu_depth_reviews.json`](data/catalog/phase10_chubu_depth_reviews.json)
- [`data/catalog/phase10_kinki_depth_reviews.json`](data/catalog/phase10_kinki_depth_reviews.json)
- [`data/catalog/phase10_chugoku_depth_reviews.json`](data/catalog/phase10_chugoku_depth_reviews.json)
- [`data/catalog/phase10_shikoku_depth_reviews.json`](data/catalog/phase10_shikoku_depth_reviews.json)
- [`data/catalog/phase10_kyushu_depth_reviews.json`](data/catalog/phase10_kyushu_depth_reviews.json)
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

1. 全47都道府県の年度実績をReviewed政策目標へ一対一照合
2. 政策・施策・事業の共通IDを作成
3. 予算、補正予算、決算、事業費、契約額を別レコードで接続
4. 契約・調達、議会説明、監査指摘、是正措置を同じ政策系列へ接続
5. 現任期の首長公約を行政計画と分離して接続
6. 全公開値・関係のEvidence coverageと公開状態を検証
7. 47都道府県すべてが11項目の共通ゲートへ到達した場合のみPhase 10を完了

## License

コード、方法論、データの権利関係は分離して扱います。ライセンス確定前の内容は、権利者の明示的な許可なく再利用できません。詳細は [DATA_POLICY.md](DATA_POLICY.md) を参照してください。

## Phase 10 completion (2026-08-01)

Phase 10 is complete at nationwide document scope for all 47 prefectures. The five delivery-evidence layers are linked by prefecture, official role, and reporting period. Contracts, assembly, and executive-manifesto coverage is Reviewed through an official source entrance or an explicit official-host search outcome. Missing results do not assert nonexistence. Record-level one-to-one deepening and policy-achievement assessment remain outside this completion claim.
