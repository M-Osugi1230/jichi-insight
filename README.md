# Jichi Insight

**約束・予算・実行・成果を、ひとつにつなぐ。**

Jichi Insight（自治体インサイト）は、自治体が公開する財政、事業、契約、政策評価、マニフェスト、議会資料を構造化し、自治体・首長・議会が「何を約束し、いくら使い、何を実行し、何を実現したか」を、一次資料に基づいて理解できるようにする自治体IR・行政アカウンタビリティ基盤です。

## Product status

`47-prefecture registry / Wave 1 current plans 9 of 9 confirmed / Hokkaido indicators 1–108 reviewed with Evidence Packets / Miyagi 4 directions, 8 policies and 18 measures reviewed / Fukuoka policy targets 1–118 reviewed / pre-alpha`

福岡県・福岡市・北九州市で構築したデータモデルと品質ゲートを、全国47都道府県へ展開しています。全国登録、計画入口、現行性確認、政策体系、KPI本文、年度実績、政策評価、公開を別の状態として管理し、候補URL、未確認資料、旧計画を公開済みのように扱いません。プロジェクトの存在理由と判断基準は [North Star](docs/NORTH_STAR.md) に固定し、着想から現在までの重要な判断は [Project Memory](docs/PROJECT_MEMORY.md) に残しています。

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
- 第1波の公式ホームページ確認：9/9都道府県
- 第1波の総合計画入口索引：9/9都道府県
- 全国の総合計画入口索引：9/47都道府県
- 第1波の現行計画確認：9/9都道府県
- Reviewed政策データ：2都道府県（福岡県・北海道）
- 政策体系Reviewed・KPI索引中：宮城県
- 作業待ち：愛知県、香川県、広島県、沖縄県、東京都、大阪府
- 公開済み都道府県ページ：3件（福岡県・北海道・宮城県）
- 第1波の地域拠点：北海道、宮城県、東京都、愛知県、大阪府、広島県、香川県、福岡県、沖縄県

全国展開は `registered → official_entry_verified → source_cataloged → current_plan_confirmed → policy_hierarchy_reviewed → reviewed_data → actuals_linked → published` の品質段階で進めます。北海道は18政策分野、108指標、複数分野参照5件、Evidence Packet 108件のReviewed工程を完了しました。ただし年度実績・達成率・政策評価は未接続です。宮城県は公式資料10件・資料関係6件を固定し、4基本方向・8政策・18施策・復興支援4分野をReviewed化しました。次は中期実施計画の目標指標一覧を18施策へ接続します。詳細は [Nationwide expansion](docs/NATIONWIDE_EXPANSION.md) と [Wave 1 policy review queue](docs/WAVE1_POLICY_REVIEW_QUEUE.md) を参照してください。

## Current reviewed source and data coverage

公式資料カタログは [`data/catalog`](data/catalog) にあります。

### Hokkaido

- 北海道指標PDF：18件・合計108ページ
- 北海道指標位置：1〜108、欠落0件・重複0件
- 北海道複数分野参照：5件（指標16、17、24、45、50）
- 北海道Reviewed指標：108/108件
- 北海道KPI Evidence Packet：108件
- 目標設定済み：103件
- 一部目標設定：2件（指標31・32）
- 目標未設定：3件（指標3・6・10。「―」を0へ変換せずnullで保持）
- 条件目標値：19件。前年比較、全国値、相対条件、法定雇用率、複合条件、社会増、範囲、過去最高値を数値化せず保持
- 複数系列：指標13・14・16・24・37・50・54・56・58・59・95・101
- 下限目標：指標13〜16の9系列と指標84の中間・最終目標を`at_least`で保持
- 現状値なし：指標14外国人系列、指標15、指標32をnullで保持
- 累計値：指標40の累計到達値、指標41の5年・10年累計、指標83の1965年以降累計を区別
- 範囲目標：指標101の東部・北部・中部を3系列に分け、`37.5～50`と`25～50`を単一数値へ変換しない
- 過去最高値目標：指標107・108の「過去最高値」を条件目標として保持し、参考値60人・8個へ置換しない
- 異なる最終目標年：指標97・106の2031年、指標107・108の2034年を2033年へ補正しない
- 実績年度と公表年：公表時期が遅れる指標でも、公表年ではなく実績年度・基準日を保持
- 参考内訳：男女、年齢、地域、管内、病院、空港、産業、国籍、在留資格、夏季・冬季、オリンピック・パラリンピック別の参考値をKPI系列へ混入しない
- 欠損：データなし年や比較不能期間を0や推計値で補完しない
- 年度実績へ接続済み：0件
- 政策評価済み：0件

### Miyagi

- 最上位計画：「新・宮城の将来ビジョン」2021〜2030年度
- 現行実施計画：中期2025〜2027年度、2026年2月改定
- 公式資料インベントリ：10件
- 資料間関係：6件
- 最上位計画PDF：84ページ
- 現行実施計画PDF：61ページ
- 最新確定成果・評価PDF：210ページ
- Reviewed基本方向：4件
- Reviewed政策：8件
- Reviewed施策：18件
- 復興完了に向けた別枠取組分野：4件
- 政策体系Evidence Packet：5件
- 最上位ビジョンと実施計画を分離
- 政策、施策、構成事業を別階層で管理
- 復興支援4分野を政策9として登録しない
- 目標値、年度実績、県の自己評価、行政評価委員会意見を分離
- 活動年度と評価年度・公表日を分離
- 評価原案、審議過程、確定評価を別状態で管理
- KPI本文へ接続済み：0件
- 年度実績へ接続済み：0件
- 政策評価済み：0件

### Other reviewed data

- Reviewedパイロット：福岡県、福岡市、北九州市
- 政策資料カタログ：36件
- Reviewed政策資料：10件
- 公式資料入口・年度別資料：48件
- Reviewed財政値：22件（福岡県13、福岡市4、北九州市5）
- 財政Evidence Packet coverage：22/22件
- 同条件比較：福岡市・北九州市の一般会計4指標
- Reviewed政策基本方向：11件（福岡県4、北海道3、宮城県4）
- Reviewed政策取組事項：30件（福岡県）
- Reviewed政策数値目標：118件（福岡県取組1〜26、指標1〜118）
- 再掲・複数分野掲載：福岡県15行、北海道5件を既存指標への参照として扱い、重複登録していない
- Reviewed議会海外活動：福岡県議会3件
- 公開済み総合評価：0件
- 次工程：北海道の年度実績・進捗資料との接続、宮城県の目標指標索引

PDFページ数、一意指標数、重複込み掲載行、政策数、施策数、構成事業数は別の意味を持つ数値として管理します。ページ数や目次件数だけを根拠に本文レコードを自動生成しません。

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
- [Wave 1 policy review queue](docs/WAVE1_POLICY_REVIEW_QUEUE.md)
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
3. 47都道府県で現行計画・後継計画・改定状況を確認
4. 9地域拠点でEvidence Packet付きReviewed政策データを公開
5. 年度実績、重点事業、予算・決算、契約を接続
6. 首長公約と議会資料を役割別に接続
7. 比較可能性を検証した指標だけを横断比較
8. 政令指定都市、中核市、県庁所在地、その他市区町村へ展開

最初の全国版でも、比較条件が揃う前の全国ランキングや人物の総合点は公開しません。

## License

コード・方法論・データの権利関係は性質が異なるため、公開ライセンスは分離して確定します。ライセンス決定前の内容は、権利者の明示的な許可なく再利用できません。詳細は [DATA_POLICY.md](DATA_POLICY.md) を参照してください。
