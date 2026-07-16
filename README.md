# Jichi Insight

**約束・予算・実行・成果を、ひとつにつなぐ。**

Jichi Insight（自治体インサイト）は、自治体が公開する財政、事業、契約、政策評価、マニフェスト、議会資料を構造化し、自治体・首長・議会が「何を約束し、いくら使い、何を実行し、何を実現したか」を、一次資料に基づいて理解できるようにする自治体IR・行政アカウンタビリティ基盤です。

## Product status

`47-prefecture registry / 9 official entries verified / Fukuoka policy targets 1–118 reviewed / pre-alpha`

福岡県・福岡市・北九州市で構築したデータモデルと品質ゲートを、全国47都道府県へ展開しています。全国登録とReviewedデータ公開は別の状態として管理し、候補URLや未確認資料を公開済みのように扱いません。プロジェクトの存在理由と判断基準は [North Star](docs/NORTH_STAR.md) に固定し、着想から現在までの重要な判断は [Project Memory](docs/PROJECT_MEMORY.md) に残しています。

## The problem

自治体情報は相当量が公開されています。しかし、予算書、決算書、事務事業評価、契約情報、議事録、監査報告、選挙公報が別々の場所と形式に分散し、住民が「一つの政策」を追うには大きな負担があります。

Jichi Insightは、公開情報を増やすだけでなく、次の流れへ接続します。

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
- **自治体、首長、議会に同じ評価軸を当てず、役割ごとに評価する**
- **総合点より先に、根拠と領域別指標を提示する**
- **訂正、反論、変更履歴を残す**
- **根拠が不足する場合は、無理に評価しない**

## Current nationwide coverage

- 全国登録：47/47都道府県
- 公式ホームページ確認済み：9都道府県
- 総合計画入口の索引化：3都道府県
- Reviewed政策データ：1都道府県
- 公開済み都道府県ページ：1件
- 公式URL候補・手動確認前：38都道府県
- 第1波の地域拠点：北海道、宮城県、東京都、愛知県、大阪府、広島県、香川県、福岡県、沖縄県

全国展開は `registered → official_entry_verified → source_cataloged → reviewed_data → actuals_linked → published` の品質段階で進めます。詳細は [Nationwide expansion](docs/NATIONWIDE_EXPANSION.md) を参照してください。

## Current reviewed source and data coverage

公式資料カタログは [`data/catalog`](data/catalog) にあります。

- Reviewedパイロット：福岡県、福岡市、北九州市
- 公式資料入口・年度別資料：48件
- Reviewed財政値：22件
- 福岡県：13件
- 福岡市：4件
- 北九州市：5件
- 財政Evidence Packet coverage：22/22件
- 同条件比較：福岡市・北九州市の一般会計4指標
- Reviewed政策基本方向：4件
- Reviewed政策取組事項：30件
- Reviewed政策数値目標：118件（取組1〜26、指標1〜118）
- 条件型目標と上限・下限目標：原文の条件・比較演算を保持して表示
- 再掲行：15行を既存指標への参照として扱い、重複登録していない
- 年度実績へ接続済みの政策数値目標：0件
- 政策評価済み取組事項：0件
- Reviewed議会海外活動：福岡県議会3件
- 海外活動報告書確認：1/3件
- 訪問単位の費用確認：0/3件
- 公開済み総合評価：0件
- 次工程：全国公式入口の確認、9地域拠点の総合計画索引、福岡県取組27以降、年度実績、重点事業、契約、KPI、公約、議案・採決への接続

実データは [`data/reviewed`](data/reviewed) と [`data/entities`](data/entities) にあり、公開する財政値、議会海外活動、政策体系・数値目標にEvidence Packetを持たせています。

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

- [North Star — 目的・課題意識・不変原則](docs/NORTH_STAR.md)
- [Project Memory — 着想と重要判断](docs/PROJECT_MEMORY.md)
- [Project charter](docs/PROJECT_CHARTER.md)
- [Product requirements](docs/PRODUCT_REQUIREMENTS.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Data model](docs/DATA_MODEL.md)
- [Methodology](docs/METHODOLOGY.md)
- [Editorial policy](docs/EDITORIAL_POLICY.md)
- [Assembly accountability](docs/ASSEMBLY_ACCOUNTABILITY.md)
- [Nationwide expansion](docs/NATIONWIDE_EXPANSION.md)
- [Data quality and publication readiness](docs/DATA_QUALITY.md)
- [Corrections and right of reply](docs/CORRECTIONS.md)
- [Development plan](docs/DEVELOPMENT_PLAN.md)
- [Roadmap](docs/ROADMAP.md)
- [Release checklist](docs/RELEASE_CHECKLIST.md)
- [Risk register](docs/RISK_REGISTER.md)
- [Data policy](DATA_POLICY.md)
- [Governance](GOVERNANCE.md)
- [Contributing](CONTRIBUTING.md)

## Initial nationwide delivery target

全国登録しただけでは、全国版の完成とはみなしません。次の順序で品質を上げます。

1. 47都道府県の公式入口を手動確認
2. 47都道府県の総合計画・実施計画・数値目標を索引化
3. 9地域拠点でEvidence Packet付きReviewed政策データを公開
4. 年度実績、重点事業、予算・決算、契約を接続
5. 首長公約と議会資料を役割別に接続
6. 比較可能性を検証した指標だけを横断比較
7. 政令指定都市、中核市、県庁所在地、その他市区町村へ展開

最初の全国版でも、比較条件が揃う前の全国ランキングや人物の総合点は公開しません。

## License

コード・方法論・データの権利関係は性質が異なるため、公開ライセンスは分離して確定します。ライセンス決定前の内容は、権利者の明示的な許可なく再利用できません。詳細は [DATA_POLICY.md](DATA_POLICY.md) を参照してください。
