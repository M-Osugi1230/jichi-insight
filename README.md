# Jichi Insight

**約束・予算・実行・成果を、ひとつにつなぐ。**

Jichi Insight（自治体インサイト）は、自治体が公開する財政、事業、契約、政策評価、マニフェスト、議会資料を構造化し、自治体・首長・議会が「何を約束し、いくら使い、何を実行し、何を実現したか」を、一次資料に基づいて理解できるようにする自治体IR・行政アカウンタビリティ基盤です。

## Product status

`47-prefecture registry / Wave 1 current plans 9 of 9 confirmed / Hokkaido indicators 1–91 reviewed with Evidence Packets / Fukuoka policy targets 1–118 reviewed / pre-alpha`

福岡県・福岡市・北九州市で構築したデータモデルと品質ゲートを、全国47都道府県へ展開しています。全国登録、計画入口、現行性確認、Reviewedデータ公開を別の状態として管理し、候補URL、未確認資料、旧計画を公開済みのように扱いません。プロジェクトの存在理由と判断基準は [North Star](docs/NORTH_STAR.md) に固定し、着想から現在までの重要な判断は [Project Memory](docs/PROJECT_MEMORY.md) に残しています。

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
- 第1波の政策資料カタログ：9/9都道府県
- Reviewed政策データ：1都道府県
- 部分Reviewed化作業中：北海道（政策体系、108指標位置、複数分野参照5件、指標1〜91のKPI本文・Evidenceを完了）
- 作業待ち：宮城県、愛知県、香川県、広島県、沖縄県、東京都、大阪府
- 公開済み都道府県ページ：1件
- 第1波の地域拠点：北海道、宮城県、東京都、愛知県、大阪府、広島県、香川県、福岡県、沖縄県

全国展開は `registered → official_entry_verified → source_cataloged → current_plan_confirmed → reviewed_data → actuals_linked → published` の品質段階で進めます。北海道は政策体系・資料位置・複数分野関係と指標1〜91のみReviewed済みであり、残る17指標・年度実績・公開ページが未完了のため、都道府県全体の`reviewed_data`にはまだ昇格していません。詳細は [Nationwide expansion](docs/NATIONWIDE_EXPANSION.md) と [Wave 1 policy review queue](docs/WAVE1_POLICY_REVIEW_QUEUE.md) を参照してください。

## Current reviewed source and data coverage

公式資料カタログは [`data/catalog`](data/catalog) にあります。

- Reviewedパイロット：福岡県、福岡市、北九州市
- 政策資料カタログ：36件
- Reviewed政策資料：10件
- 第1波の索引済み戦略資料：8件
- 北海道指標PDF：18件・合計108ページ
- 北海道指標位置：1〜108、欠落0件・重複0件
- 北海道複数分野参照：5件（指標16、17、24、45、50）
- 北海道Reviewed指標：91/108件（指標1〜91）
- 北海道KPI Evidence Packet：91件
- 北海道の目標設定済み：86件
- 北海道の一部目標設定：2件（指標31・32）
- 北海道の目標未設定：3件（指標3・6・10。「―」を0へ変換せずnullで保持）
- 北海道の条件目標：指標42、46、52、69、74、75、80の条件部分を`conditional`または原文付き複合条件として保持
- 北海道の複数系列：指標13・14・16・24・37・50・54・56・58・59
- 北海道の下限目標：指標13〜16の9系列と指標84の中間・最終目標を`at_least`で保持
- 北海道の現状値なし：指標14外国人系列、指標15、指標32をnullで保持
- 北海道の非単調目標：指標20、指標39を原文のまま保持
- 北海道の累計値：指標40の累計到達値、指標41の5年・10年累計、指標83の1965年以降累計を区別
- 北海道の負値：指標43の-41.4→-39.7→-38.0を欠損へ変換せず保持
- 北海道の外部ベンチマーク目標：指標46の「全国値」を固定数値へ変換しない
- 北海道の明示的ゼロ値：指標49の0人目標、指標53の0教科実績、指標61の0圏域目標、指標80の社会増減均衡0人を欠損補完と区別
- 北海道の男女別系列：指標50を男性・女性に分離し、2政策分野参照を保持
- 北海道の相対条件目標：指標52の「現状より増加」と指標80の「社会増」を具体値へ変換しない
- 北海道の学校段階・男女系列：指標54を4系列、指標56・58を2系列、指標59を3系列で保持
- 北海道の100％目標：指標55・56・58・59・90の明示的目標を数値として保持
- 医療・福祉の参考内訳：指標62の圏域別看護職員数、指標63の求人倍率をKPI系列へ混入しない
- 実績年度と公表年：指標64・65、84〜87、89、91は公表年ではなく実績年・基準日を保持
- 就業率の参考内訳：指標66・67の男女別、指標68の年齢階層別をKPI系列へ混入しない
- 法定雇用率連動目標：指標69の「法定雇用率以上」を固定数値へ変換しない
- 労働時間の参考推移：指標70は北海道の目標表3値だけを保持し、全国比較の過去推移を系列へ混入しない
- 中小企業・商業の参考データ：指標71の全国・第3位推移、指標72の振興局別組織数、指標73の空き店舗要因をKPI系列へ混入しない
- 犯罪指標の複合条件：指標74・75は固定閾値だけでなく過去5年平均条件も同時に保持し、最終目標を固定数値へ変換しない
- 安全・安心の参考データ：指標76の年齢別内訳、指標77の算出要素、指標78の全国推移、指標79の区域・医療機関別病床をKPI系列へ混入しない
- 年齢範囲の異なる就業率：指標68と指標78を別指標として保持し、単純統合しない
- 地域づくりの参考データ：指標80の日本人・外国人・振興局別内訳、指標81の自治体別隊員数、指標82の窓口別相談数をKPI系列へ混入しない
- 北方領土返還要求署名：指標83を年度別署名数ではなく1965年以降の累計到達値として保持
- グローバル化の参考データ：指標84の教育局管内別英語力、指標85の市区町村・在留資格・国籍別外国人居住者数をKPI系列へ混入しない
- 北海道の強靱化の基準日：指標86〜89は3月末、指標90・91は4月1日時点として保持
- 北海道の強靱化の参考内訳：指標89の建設管理部地域別、指標90の病院数内訳、指標91の振興局別カバー率をKPI系列へ混入しない
- 北海道の強靱化の欠損：指標88の過去推移におけるデータなし年、指標90の比較不能な2020年度以前を0や推計値で補完しない
- 参考グラフの数値：過去推移、認知件数、刑法犯総数を目標系列へ混入しない
- 公式資料入口・年度別資料：48件
- Reviewed財政値：22件
- 福岡県：13件
- 福岡市：4件
- 北九州市：5件
- 財政Evidence Packet coverage：22/22件
- 同条件比較：福岡市・北九州市の一般会計4指標
- Reviewed政策基本方向：7件（福岡県4件、北海道3件）
- 北海道Reviewed政策分野：18件
- 北海道政策体系Evidence Packet：3件
- 北海道指標対象：一意108件、政策分野への重複込み掲載行113件
- Reviewed政策取組事項：30件（福岡県）
- Reviewed政策数値目標：118件（福岡県取組1〜26、指標1〜118）
- 条件型目標と上限・下限目標：原文の条件・比較演算を保持して表示
- 再掲・複数分野掲載：福岡県15行、北海道5件を既存指標への参照として扱い、重複登録していない
- 年度実績へ接続済みの政策数値目標：0件
- 政策評価済み取組事項：0件
- Reviewed議会海外活動：福岡県議会3件
- 海外活動報告書確認：1/3件
- 訪問単位の費用確認：0/3件
- 公開済み総合評価：0件
- 次工程：北海道指標92〜98（社会経済の基盤整備）をEvidence Packet付きでReviewed化し、その後に指標99〜102（自然・環境）へ進む

PDFページ数108、一意指標数108、重複込み掲載行113は別の意味を持つ数値として管理します。ページ数の一致だけを根拠に指標レコードを自動生成せず、113掲載行との差分5件は追加の政策分野参照として保存します。

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
