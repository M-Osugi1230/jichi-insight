# Jichi Insight

**約束・予算・実行・成果を、ひとつにつなぐ。**

Jichi Insight（自治体インサイト）は、自治体が公開する財政、事業、契約、政策評価、マニフェスト、議会資料を構造化し、自治体・首長・議会が「何を約束し、いくら使い、何を実行し、何を実現したか」を、一次資料に基づいて理解できるようにする自治体IR・行政アカウンタビリティ基盤です。

## Product status

`47/47 official entries verified / 47/47 policy-plan entries indexed and current-confirmed / Hokkaido indicators 1–108 reviewed / Fukuoka policy targets 1–118 reviewed / Miyagi KPI groups 1–128 and series 1–149 reviewed / Miyagi 95 annual-result series linked / pre-alpha`

全国登録、公式入口、政策計画入口、現行性確認、Reviewedデータ、年度実績接続、公開を別々の品質状態として管理します。候補URL、未確認資料、旧計画を公開済みのように扱いません。

## The problem

自治体情報は相当量が公開されています。しかし、予算書、決算書、事務事業評価、契約情報、議事録、監査報告、選挙公報が別々の場所と形式に分散し、住民が「一つの政策」を追うには大きな負担があります。

Jichi Insightは、公開情報を次の流れへ接続します。

```text
Promise        選挙・計画で何を約束したか
   ↓
Money          いくら確保し、何に使ったか
   ↓
Action         どの事業・契約を実行したか
   ↓
Result         目標に対して何が変わったか
   ↓
Accountability 誰が判断し、どう説明したか
```

## Non-negotiable principles

- **事実、比較、解釈、評価を分ける**
- **一次資料を優先する**
- **未公開・未確認・不明を推測で補完しない**
- **政策思想、政党、人物の好悪を採点しない**
- **出典、更新日、抽出方法、レビュー状態を表示する**
- **自治体、首長、議会を役割別に扱う**
- **訂正、反論、変更履歴を残す**
- **根拠が不足する場合は、無理に評価しない**

## Current nationwide coverage

- 全国登録：47/47都道府県
- 公式ホームページ確認：47/47都道府県
- 政策計画入口索引：47/47都道府県
- 現行政策計画入口確認：47/47都道府県
- Reviewed政策データ：2都道府県（北海道・福岡県）
- 年度実績接続中：宮城県
- 全国レビューキュー：47/47都道府県
- 公開済み都道府県ページ：3件（北海道・宮城県・福岡県）

全国展開は、

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

の品質段階で進めます。

単一の「総合計画」を持たない県についても、長期ビジョン、総合戦略、年度版政策集、施策方針など、公式の名称と役割を保持します。全国ランキングは比較可能性の確認前に公開しません。

機械可読な正本：

- [`data/catalog/prefecture_coverage.json`](data/catalog/prefecture_coverage.json)
- [`data/catalog/nationwide_policy_review_queue.json`](data/catalog/nationwide_policy_review_queue.json)
- [Nationwide expansion](docs/NATIONWIDE_EXPANSION.md)

## Reviewed data status

### Hokkaido

- Reviewed指標：108/108件
- KPI Evidence Packet：108件
- 複数分野参照、条件目標、上下限、範囲、累計、欠損、異なる最終目標年を原文の意味のまま保持
- 年度実績・政策評価：未接続

### Miyagi

- 政策体系：4基本方向、8政策、18取組
- 目標値グループ：128/128件
- 個別指標系列：149/149件
- KPI Evidence Packet：128件
- 年度実績を直接接続した目標グループ：82件
- 年度実績を直接接続した系列：95件
- 定義・範囲の要確認系列：15件
- 年度実績行：440件
- 年度実績Evidence Packet：110件
- 未直接接続系列：54件
- 次工程：取組16〜18と残る系列の年度実績接続

報告年度と測定年度、評価書の旧目標と現行計画の目標を分離し、公式達成率を独自に再計算しません。政策評価は全件`not_assessed`です。

### Fukuoka and other reviewed data

- Reviewed財政値：22件（福岡県13、福岡市4、北九州市5）
- 財政Evidence Packet coverage：22/22件
- Reviewed政策取組事項：30件（福岡県）
- Reviewed政策数値目標：118件（福岡県）
- Reviewed議会海外活動：福岡県議会3件
- 公開済み総合評価：0件

## Repository map

```text
apps/web/       公開サイト
pipelines/      収集・抽出・正規化・検証
data/           カタログ、例示データ、レビュー済みデータ
schemas/        公開データのJSON Schema
scripts/        リポジトリ・データ品質検証
tests/          自動テスト
docs/           方針、設計、ロードマップ、評価方法
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
- [Wave 1 policy review queue](docs/WAVE1_POLICY_REVIEW_QUEUE.md)
- [Data quality and publication readiness](docs/DATA_QUALITY.md)
- [Corrections and right of reply](docs/CORRECTIONS.md)
- [Development plan](docs/DEVELOPMENT_PLAN.md)
- [Roadmap](docs/ROADMAP.md)
- [Release checklist](docs/RELEASE_CHECKLIST.md)
- [Risk register](docs/RISK_REGISTER.md)

## Next delivery gates

1. 宮城県の取組16〜18と残る年度実績接続
2. Wave 1の6都府県で実施計画・KPI・年度評価・予算の資料インベントリを作成
3. Wave 2の38県を地域単位で同じ工程へ展開
4. 重点事業、予算、契約、監査、議会、公約を政策目標へ縦接続
5. 比較可能性を検証した指標だけを横断比較へ昇格

## License

コード・方法論・データの権利関係は性質が異なるため、公開ライセンスは分離して確定します。ライセンス決定前の内容は、権利者の明示的な許可なく再利用できません。詳細は [DATA_POLICY.md](DATA_POLICY.md) を参照してください。
