# Jichi Insight

**約束・予算・実行・成果を、ひとつにつなぐ。**

Jichi Insight（自治体インサイト）は、自治体が公開する政策計画、財政、事業、契約、政策評価、監査、議会、首長公約を構造化し、「何を目指し、いくら使い、何を実行し、何が変わり、どう説明したか」を一次資料から確認できるようにする自治体IR・行政アカウンタビリティ基盤です。

## Product status

`Phase 10 complete / 47 prefectures published / pre-alpha`

- 全国登録: 47 / 47
- 公式ホームページ確認: 47 / 47
- 現行政策計画確認: 47 / 47
- Evidence-backed Reviewed数値目標: 47 / 47
- 全国公開ページ: 47 / 47
- Phase 10同一粒度完了: 47 / 47
- 独自の政策達成評価: 0件
- 比較可能性未確認の全国ランキング: 0件

Phase 9で全47都道府県の政策目標とEvidence-backed Reviewed基盤を整備し、Phase 10で年度実績、予算、決算、重点事業、監査を文書スコープで接続しました。契約・議会・首長公約は、都道府県公式一次資料または「不存在を断定しない公式検索結果」までReviewedとしています。

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

資料入口を確認した`indexed`、内容・期間・対象範囲・出典を確認した`reviewed`、定義と期間を照合して同じ系列へ接続した`linked`は別の状態です。

## Phase 10 — Nationwide uniform depth

2026年8月1日、47都道府県すべてが次の11項目の共通ゲートへ到達しました。

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

### 完了状態

- Reviewed政策目標: 47 / 47
- Reviewed Evidence: 47 / 47
- 年度実績 文書スコープLinked: 47 / 47
- 予算 文書スコープLinked: 47 / 47
- 決算 文書スコープLinked: 47 / 47
- 重点事業 文書スコープLinked: 47 / 47
- 監査 文書スコープLinked: 47 / 47
- 契約・議会・首長公約 Reviewed coverage: 47 / 47（141役割）
  - 安定した公式一次資料入口: 3件
  - 現任期確認待ち: 1件
  - 安定一次資料未特定の公式検索結果: 137件
- 公開検証 Reviewed: 47 / 47
- 11項目すべて同一粒度完了: 47 / 47

### 完了範囲

Phase 10の完了は**全国の文書スコープ**を対象とします。個別の目標、予算科目、事業、契約、議会発言、監査指摘をすべて一対一接続したという意味ではありません。

安定した一次資料が見つからない場合は、不存在とは断定せず、確認した公式ホスト、検索条件、検索日、再確認条件をEvidenceとして保持します。政策の達成・未達は判定せず、比較可能性が確認されるまで全国ランキングにも使用しません。

### 正本

- [`data/catalog/phase10_uniformity.json`](data/catalog/phase10_uniformity.json)
- [`data/catalog/phase10_execution_queue.json`](data/catalog/phase10_execution_queue.json)
- [`data/catalog/phase10_completion.json`](data/catalog/phase10_completion.json)
- [`data/catalog/phase10_nationwide_core_linkage.json`](data/catalog/phase10_nationwide_core_linkage.json)
- [`data/catalog/phase10_nationwide_accountability_linkage.json`](data/catalog/phase10_nationwide_accountability_linkage.json)
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

## Post-Phase 10 deepening

1. 北海道・宮城県・東京都・福岡県で確立した個票接続工程を他県へ展開
2. 政策・施策・事業・予算科目・契約・議会発言・監査指摘の安定IDを拡張
3. 現任期の首長公約を候補者・任期・原文単位で確認
4. 公式サイト移転や新年度資料を再探索し、検索結果から一次資料へ昇格
5. 比較可能性が確認された指標だけを将来の比較機能へ接続

この深掘りはPhase 10の完了状態を覆すものではなく、文書スコープから個票スコープへ精度を高める継続工程です。

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

## License

コード、方法論、データの権利関係は分離して扱います。ライセンス確定前の内容は、権利者の明示的な許可なく再利用できません。詳細は [DATA_POLICY.md](DATA_POLICY.md) を参照してください。
