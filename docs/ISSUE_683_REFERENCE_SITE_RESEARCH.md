# Issue #683 — 「知りたいこと」からたどり着くための参考サイト調査

- 調査日: 2026-11-19
- 対象: Jichi Insight（https://jimieru.com/）の発見性・導線の検討
- 対応 Issue: https://github.com/M-Osugi1230/jichi-insight/issues/683
- 提案・タスク別監査: [ISSUE_683_TASK_NAVIGATION_PROPOSAL.md](./ISSUE_683_TASK_NAVIGATION_PROPOSAL.md)
- ステータス: **提案のみ・実装承認前**。この調査による UI・データ・スキーマ変更は行わない。

## 0. 調査範囲・再現可能性

### 実施したこと

1. Jichi Insight 本番の `/`、`/municipalities/`、`/compare/`、`/projects/`、`/promises/`、`/assemblies/`、`/review-progress/` に対して、公開 Web ページとして取得を試みた。
2. **本番 `jimieru.com` の HTML は今回の外部取得環境で取得不可**（ルートは DisabledError、他のページはアクセス不可）。したがって、視覚・インタラクションを実機で確認したとは主張しない。認証・ネットワーク由来かサイト障害かは判定できない。
3. 代替として、接続済み GitHub の **main ブランチのページ実装**（`apps/web/app/`、`apps/web/components/SiteHeader.tsx`、`docs/MEASUREMENT.md`）を取得し、公開ルート、画面文言、コンポーネント配置、リンク構造を静的に追跡した。これを以下 **「実装確認」** と記す。実機の折り返しや読み込み時間、ユーザーの実際の迷いは未測定。
4. 外部参考サイトは各サイトの指定URLを実際に検索・開き、読めたページ構造を調査した。JavaScript主体で本文を読み取れなかったサイトは「公開ページ＋説明ページからの確認」と区別する。

**重要**: ここでいう「導線の問題」は、利用者テストで観測された事実ではなく、実装から再現可能な **利用者タスク上の仮説**。3分理解テスト／支援技術の実機確認で検証してから UI 変更を決定する。

## 1. 参考サイト比較（各 URL を確認）

| # | 参考サイト・実際の対象 URL | 観察できた導線 | Jichi Insight に借りられる点 | そのまま借りられない点・注意 |
|---|---|---|---|---|
| 1 | GOV.UK [サービスと情報](https://www.gov.uk/browse)、[Council Tax](https://www.gov.uk/browse/housing-local-services/council-tax) | 組織名ではなく「Housing and local services」「Council Tax」等の生活者語彙→「支払う／減免を受ける／異議申立て」の行動別リンクへ段階的に絞る。長い説明より先に行動選択。 | 冒頭に「借金を確認」「議会の議決を見る」等の **問い／タスク** を並べ、先の画面を説明するリンクにする。階層が深くても戻れるパンくず。 | GOV.UK は行政手続きを提供する公式窓口。Jichi Insight は資料の検証・閲覧サービスであり、「申請できる」「必ず答えがある」と誤認させない。 |
| 2 | TheyWorkForYou [トップ](https://www.theyworkforyou.com/)、[議員を探す](https://www.theyworkforyou.com/mps/)、[最近の表決](https://www.theyworkforyou.com/divisions/)、[討論](https://www.theyworkforyou.com/debates/) | 郵便番号・人物・トピックの単一入力から始め、討論・表決を別カテゴリに分離。最近の採決は日付→議案→内訳をたどれる。 | 「地域から／議案・話題から」の二入口。議会一覧→会期→議案→公式表決を行き来できる見出し・一覧絞込。 | 英国の個人別表決データと日本の自治体議会の公開粒度は違う。**福岡県・福岡市・北九州市の議員別賛否は未公表**。会派別は両市のみ。個人票の推計・議員ランキング・スコアは不可。 |
| 3 | USAspending.gov [トップ](https://www.usaspending.gov/)、[Spending Explorer](https://www.usaspending.gov/explorer)、[Advanced Search](https://www.usaspending.gov/search) | トップで大づかみ（Explorer）と条件検索（Advanced Search）を選択可能。年度、対象、カテゴリ等のスコープで財政情報を絞る設計。 | **概要→条件を明示して深掘り→個別根拠**の二層導線、検索条件の見える化を借りる。 | 対象は米連邦の spending / awards で、自治体の予算・決算・起債・基金・事業成果とは母集団も概念も違う。サイト本体は JS 主体で、今回本文・操作の全機能を直接検証できなかったため、上記は公開説明と検索結果も併用した限定所見。 |
| 4 | OpenSpending [データセット検索](https://www.openspending.org/)、[Explorer 操作手順](https://docs.openspending.org/en/latest/users/explore/) | キーワード・国・会計期間のフィルタでデータセットに入り、該当パッケージを選んでビューアへ進む。検索前に「どの期間の何のデータか」を明示。 | 検索結果に **資料の年度・段階・出典・Reviewed 状態**を並記し、同名資料を取り違えさせない。 | データセット閲覧ツールの自由度を初学者向けトップに持ち込まない。数値データの網羅性・比較可能性を保証しない。 |
| 5 | Where Does My Money Go? 系: [元のプロジェクトと Daily Bread](https://github.com/openspending/wheredoesmymoneygo.org)、近縁の実動例 [Where My Tax Goes](https://wheremytaxgoes.uk/) | 「税金は何に使われる？」という問いと分野検索から始め、金額表示を総額／1人当たり／100通貨単位等に切替。概算の前提・年度・出典を同じ画面に表示。 | 「お金の行き先を知る」入口、単位・年度・金額段階の補助説明、出典のすぐそばでの欠損注記。 | 個人の税負担がそのまま自治体の個別支出に流れたかのような表示は禁止。人口・分母・税配分が確認できない地域では、1人当たりや疑似税負担を生成しない。元プロジェクトは歴史的デザイン例であり現行稼働状況の証拠ではない。 |
| 6 | Institute for Fiscal Studies [Where and how does the government spend its money?](https://ifs.org.uk/calculators/where-and-how-does-government-spend-its-money) | 最初に「政府はどこで何に支出しているか」という問いと範囲を提示し、地域差・時系列の探索へ誘導。本文に補足説明も持つ。 | 自治体／年度／予算・決算段階を前置きした上で、まず一枚の答えと「詳しい根拠」を分ける。 | 英国の政府支出と市町村の一般会計を混同しない。グラフ先行より **出典・定義差** を優先。 |
| 7 | 東京都財務局 [財政情報](https://www.zaimu.metro.tokyo.lg.jp/ja/zaisei/zaisei)、[都財政の見える化ボード案内](https://www.zaimu.metro.tokyo.lg.jp/ja/zaisei/zaisei/dashboard) | 予算・決算の主要情報を「見える化ボード」に集約し、説明や公開文書とつなぐ。 | 数字の概観と出典資料を近接配置し、初学者から詳細閲覧へ段階的に進める。 | 東京都単独の同一組織データと全国自治体の部分的 Reviewed 収録は異なる。自治体横断の同条件を推測しない。ページは案内を確認。埋込ダッシュボードの個別インタラクションは今回未検証。 |
| 8 | RESAS [トップ](https://resas.go.jp/)、[地域ビジネス環境分析](https://resas.go.jp/industry-regional-environment-analysis/)、[支出分析](https://resas.go.jp/region-cycle-spending/) | 地域を軸に地図・グラフで多面的な情報へ進む。テーマごとの分析画面を分ける。 | 「自治体を選択してから、借金／事業／議会等を選ぶ」地域コンテキストの保持。地域→テーマの切替を分かりやすくする。 | RESAS は産業・経済分析であり、議会の採決や公約評価の出典ではない。JS 主体の各分析画面の操作を今回詳細検証したわけではない。 |
| 9 | e-Stat [地域別統計](https://www.e-stat.go.jp/regional-statistics/ssdsview)、[統計ダッシュボードの説明](https://dashboard.e-stat.go.jp/static/whatIs)、[地域選択データ検索](https://dashboard.e-stat.go.jp/dataSearch?language=ja) | 地域→分野／系列→期間の絞り込み。統計名が不明でもテーマから探し、既製グラフで概況を確認できる。 | 自治体名だけでなく **「市債」「基金」「子育て」等の生活者用語** を探索の入口にし、分野・年度を後から選べる。 | 統計系列の均一性を Jichi Insight の全フィールドに当てはめない。原資料の定義差を残す。 |
| 10 | 報道機関・可視化参考: Reuters Graphics [作品一覧](https://graphics.thomsonreuters.com/)、[Reuters newsroom charts/maps/tables guide](https://reuters-graphics.github.io/newsroom-datawrapper-guide/) | 専門用語を最初に全て見せず、見出し・地図・図表で要点を伝え、必要なら表・補足へ入る。制作ガイドに図表・地図・表の選択肢がある。 | **一画面一つの明確な問い**、数値の直後に定義・出典・単位、図表の表形式代替を組み合わせる。 | 編集記事の物語化、政治的評価や感情的な色付けは取り込まない。Reuters の完成品個別記事を全て操作検証したわけではない。 |
| 11 | 追加候補: [Where My Tax Goes](https://wheremytaxgoes.uk/) の「Find anything」「Show as」「About these numbers」 | 題材の検索→表示単位切替→方法説明が同じ画面で連動する。スクリーンリーダー用テキストと根拠が重要。 | 「市の借金は？」の最初の答えに **当該年度の数値の有無と単位** を示し、数字なしの場合も明確なメッセージで終了できるようにする。 | 個人年収を入力させる機能は不要。必要のない個人情報は収集しない。 |

**補足**: 外部サイトの「優れている」は画面の探索構造に対する設計上の評価であり、実際の利用者のタスク成功率を測定した比較ではない。

## 2. 繰り返し現れた良いパターン

| パターン | 観察された例 | Jichi Insight の適用候補 | 公開データ上の安全条件 |
|---|---|---|---|
| **A. 自然言語のタスクを先頭に置く** | GOV.UK、IFS | 「借金を知る」「公約を確認」「議案と表決を確認」「支出と結果を確認」「2市を並べる」 | 答えが収録されていないときも正直に案内する |
| **B. 地域名・話題名の二入口** | TheyWorkForYou、e-Stat | トップに地域検索と「知りたいこと」の並列導線 | 自治体の収録深度と未収録を混同しない |
| **C. 概観と専門条件の二層** | USAspending、東京都、Where My Tax Goes | まず一画面の答え、次に年度・会計・段階・証拠へ | 同条件でないデータを混在させない |
| **D. 問題に対応した結果一覧の絞込** | OpenSpending、TheyWorkForYou | 議案の件名・会期・政策分野検索、事業名検索 | 無関係なレコードを自動接続しない |
| **E. 根拠・限界は答えのすぐ近く** | OpenSpending、e-Stat、Reuters | 出典ボタン、公開状態、基準日をカード・詳細見出しの近くに配置 | 原文と要約、公開と未公表を明確に分離 |
| **F. キーボードと単純な代替表** | GOV.UK、e-Stat の領域構造 | スキップリンク、見出し、表での値と出典併記 | 地図・視覚グラフだけに頼らない |

## 3. 採用しないパターン

- 政治家・議員・議会・自治体の得点、活動量順位、支出額ランキング、採点色・勝敗表。
- 対象3議会で未公表の **議員個人別の賛否** の推測・復元。福岡県議会の会派別賛否も推測しない。
- `not_assessable` を「未達」に変換、未掲載をゼロとみなす、自治体の優劣を暗黙に示す色づけ。
- 税負担の個人換算や支出目的の表示を、確認できない公費の因果関係として断定すること。
- 解析 SDK、セッション追跡、PV 最大化、人気投票、サイト内人気ランキング。
- データのない自治体・年度・分野について、整っているように見せる架空の結果を生成すること。

## 4. 参考資料と監査対象コード

### Jichi Insight の実装上の監査対象（2026-11-19、main）

- `apps/web/app/page.tsx` — 日本地図が先頭、問いのカードは詳細表示 `<details>` 内
- `apps/web/components/SiteHeader.tsx` — 全国／政策と成果／予算・財政／首長／議会の分類ナビ
- `apps/web/app/municipalities/page.tsx` — 全国から自治体名を探す、67市の Reviewed 詳細
- `apps/web/app/municipalities/[slug]/page.tsx` — 概要、計画、財政、実績接続、出典、確認範囲
- `apps/web/app/compare/page.tsx` — 福岡市・北九州市の同条件4指標のみ
- `apps/web/app/projects/page.tsx`、`apps/web/app/promises/page.tsx`、`apps/web/app/assemblies/page.tsx` — 各領域の入口
- `apps/web/app/review-progress/page.tsx` — 67自治体の状況一覧
- `docs/MEASUREMENT.md` — Q1〜Q4、3分理解テストと Search Console の既存方針

### 根拠の取り扱い

本表の URL は各サイトの入口／調査ページの **具体的な URL** であり、一次サイト本文を確認できたものと JS 制約のため説明ページ等で補完したものを各行で区別した。新しい実装での情報設計は、上記実例をコピーするのでなく、自治体資料の **review status / publication status / fiscal stage / source** を必ず保持する。
