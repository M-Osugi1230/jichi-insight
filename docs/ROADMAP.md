# Roadmap

Jichi Insightは日付ではなく、品質ゲートの通過で進行を管理します。`indexed`、`reviewed`、`linked`、`published`を混同せず、一次資料とEvidenceが不足する状態を推測で埋めません。

## Phase 0〜6 — Foundation and initial publication

Status: `complete_for_initial_publication`

プロジェクト憲章、PRD、編集・データ方針、モノレポ、Web、JSON Schema、CI、公式資料マップ、訂正・反論、利用規約、プライバシー、免責、運用手順、公開前監査、Production Smokeを整備しました。正式なPublic betaには外部法務・アクセシビリティ・運用の実地ゲートが残ります。

## Phase 7 — Nationwide prefecture registry

Status: `complete`

47都道府県の共通コード、公式入口、現行政策計画、全国資料カバレッジ、状態分離、静的出力、Production Smokeを完了しました。

## Phase 8 — Regional anchor expansion

Status: `complete`

北海道、宮城県、東京都、愛知県、大阪府、広島県、香川県、福岡県、沖縄県の9地域拠点で、政策計画、主要数値目標、Evidence Packet、公開ページ、静的出力、本番確認を完了しました。

## Phase 9 — Nationwide Reviewed targets

Status: `complete`

全47都道府県をEvidence-backed Reviewed目標基盤へ引き上げました。独自の政策達成評価と比較可能性未確認の全国ランキングは0件です。

## Phase 10 — Nationwide uniform depth

Status: `complete`（2026-08-01）

47都道府県を、政策・KPI、Evidence、年度実績、予算、決算、重点事業、契約、議会、監査、首長公約、公開検証の共通文書スコープへ引き上げました。

正本:

- `data/catalog/phase10_completion.json`
- `docs/PHASE10_VERTICAL_LINKAGE.md`

## Phase 11 — Nationwide record-level linkage

Status: `complete`（2026-08-05）

47都道府県すべてを、共通Schemaを通るReviewed個票接続または公式資料上の最大到達深度へ引き上げました。全15,327レコードについて、一次資料、Evidence位置、版、期間、単位、母集団、欠損・未接続境界を保持しています。

- Wave 1: 4都道府県、861レコード
- Wave 2: 5都道府県、711レコード
- Wave 3: 38都道府県、13,755レコード
- 合計: 47都道府県、15,327レコード
- 独自の政策達成評価: 0
- 比較対象への自動昇格: 0

Phase 11完了は、すべての個票が目標・実績・予算・決算・事業・契約・監査・議会・公約まで完全接続されたことを意味しません。公式資料が不足する個票はPartialまたはNot linkedとして残し、推測で補完していません。

### Wave 1 — Reference implementations

Status: `complete`

北海道、宮城県、東京都、福岡県の861個票を全件正規化しました。

- Linked: 420
- Partial: 58
- Not linked: 383
- 独自の政策達成評価: 0

正本:

- `data/catalog/phase11_wave1_completion.json`
- `tests/test_phase11_wave1_completion.py`

### Wave 2 — Remaining regional anchors

Status: `complete`

愛知県、大阪府、広島県、香川県、沖縄県の5拠点、711レコード、725指標系列を完了しました。

- current値あり: 340系列
- current値欠損・未接続: 385系列
- 進捗目標または明示的target: 602系列
- 最大到達深度レコード: 375
- 独自の政策達成評価: 0
- 比較対象への昇格: 0

沖縄県の正本は計画基準値とR9目標であり、Reviewed年度実績ではありません。計画基準値をannual actualへ流用せず、全国値も参考情報のまま保持します。

正本:

- `data/catalog/phase11_wave2_completion.json`
- `schemas/phase11_wave2_completion.schema.json`
- `tests/test_phase11_wave2_completion.py`

### Wave 3 — Nationwide minimum record depth

Status: `complete`

残る38県、13,755レコードを都道府県コード順に処理しました。全件が共通Schemaと同じEvidence・欠損状態・非評価境界を通過する設計です。

- 完了県: 38 / 38
- Reviewed最大到達深度: 13,755レコード
- Linkedへ推測昇格したレコード: 0
- Partial: 13,755
- 政策達成・因果関係・全国比較の独自判定: 0

正本:

- `data/catalog/phase11_execution_queue.json`
- `data/catalog/phase11_completion.json`
- `schemas/phase11_completion.schema.json`
- `tests/test_phase11_completion.py`

## Phase 12 — Designated-city source inventory

Status: `complete`（2026-08-12）

政令指定都市20市を対象に、都道府県フェーズで確立したEvidence・期間・財政状態・非評価境界を市レベルへ展開しました。北九州市・福岡市の2市をReviewed referenceとして保持し、残る18市すべてを`source_inventory_complete`まで引き上げました。

- 政令指定都市: 20 / 20
- Reviewed reference: 2市（北九州市、福岡市）
- Source inventory complete: 18 / 18
- Source inventory partial: 0
- Pending source inventory: 0

Phase 12の`source_inventory_complete`は、すべての期待資料がすでに存在することを意味しません。現時点の公式公開体系を確認し、現行総合計画、自治体が公式に設けている実施層・進行管理、予算、決算、過年度資料との版境界を棚卸ししたうえで、未公開または別立てされていない層を明示的なavailability/evidence boundaryとして残せていることを意味します。存在しない年度実績を推測で作成したり、旧計画の実績を現行計画へ流用したりしません。

静岡市、堺市、神戸市、岡山市、広島市についても、未公開・未解決の証拠層を削除せずPhase 13の個票レベルblockerとして保持したまま、source inventory自体は現行公式公開体系の最大到達深度まで確認済みとしてcompleteへ昇格しました。

正本:

- `data/catalog/phase12_designated_city_execution_queue.json`
- `data/indexed/*-city/source_inventory.json`
- `schemas/phase12_*_source_inventory.schema.json`
- `tests/test_phase12_designated_city_execution_queue.py`
- `tests/test_phase12_*_source_inventory.py`

## Phase 13 — Designated-city record review

Status: `complete`（2026-09-29）

Phase 12完了により、北九州市・福岡市の2市をReviewed referenceとして保持しつつ、残る18市すべてが個票レベルのreview queueへ入りました。Phase 12由来のblocked source inventoryは0です。

Canonical queue（2026-09-28同期）:

- Reviewed reference: 2市（北九州市、福岡市）
- Review queue eligible: 18市
- Reviewed complete: 18市（札幌市、仙台市、さいたま市、千葉市、横浜市、川崎市、相模原市、新潟市、静岡市、浜松市、名古屋市、京都市、大阪市、堺市、神戸市、岡山市、広島市、熊本市）
- Review in progress: 0市
- Pending record review: 0市
- Blocked source inventory: 0市

状態の正本は `data/catalog/phase13_designated_city_review_queue.json` です。文書上の集計とmachine-readable queueが競合する場合はqueueを優先します。

### Milestone M2 — First reviewed-complete designated city

Status: `complete`（2026-08-12）

仙台市をPhase 13最初の`reviewed_complete`都市として確定しました。完了深度は`declared_review_package_v1`であり、以下のパッケージをSchema・Evidence coverage・回帰テストで固定します。

- 現行基本計画・実施計画・市民意識調査方法・自己評価集計のコア: 6レコード
- チャレンジプロジェクト: 108 / 108事業の事業名、所管、担当、証拠頁、仙台市自己評価
- 2025年市民意識調査: 現状・施策評価34項目
- 2025年市民意識調査: 今後特に力を入れるべき施策26項目
- 財政トップライン: 3レコード（2026年度一般会計当初予算歳入総額、2024年度一般会計決算歳入総額・歳出総額）

仙台市の`reviewed_complete`は全公開データの網羅を意味しません。回答区分別分布、属性別クロス集計、住みやすさ・愛着・外国人住民・自由記述、108事業の個別KPI/成果、款項目別財政・補正・執行・事業費・契約・補助金接続は`deferred_depth`として明示的に未レビューのまま残します。これらを現行レビューから推測補完しません。

また、108事業の自治体自己評価、市民意識調査の評価、市民が今後重視してほしい施策、財政値は相互に非等価です。統合スコア、Jichi Insight独自の政策達成度、因果効果、他都市比較可能性、ランキングへ自動変換しません。

正本:

- `data/catalog/sendai_phase13_completion.json`
- `schemas/sendai_phase13_completion.schema.json`
- `data/catalog/sendai_phase13_progress_linkage.json`
- `tests/test_phase13_sendai_completion.py`


### Milestone M3 — Sapporo reviewed complete

Status: `complete`（2026-08-18）

札幌市は`declared_review_package_v1`としてReviewed completeです。

- Action Plan project identities: 599件（主要406、その他193）
- Outcome indicators: 26件
- Principal project target universe: 403件
- 中央公表で個別名称と現況を確認できたcurrent status: 8件
- 個別ラベル未公表のまま保持: 395件
- Fiscal top-line records: 3件

38/356/9の集計値を名称未公表の395事業へ配分せず、未解決状態を保持しています。

正本:

- `data/catalog/sapporo_phase13_completion.json`
- `schemas/sapporo_phase13_completion.schema.json`

### Milestone M4 — Saitama reviewed complete

Status: `complete`（2026-08-19）

さいたま市は`declared_review_package_v1`としてReviewed completeです。

- Current project identities: 258件
- Current target identities: 531件
- Current outcome indicators: 97件
- Historical unique projects: 299件
- Priority strategy KPIs: 40件
- Fiscal top-line records: 3件

現行531目標のうち値レビュー未完了の509件、成果指標の完全な測定出典、旧299事業と現行258事業の版間接続はdeferred depthとして明示しています。

正本:

- `data/catalog/saitama_phase13_completion.json`
- `schemas/saitama_phase13_completion.schema.json`

### Milestone M5 — Chiba reviewed complete

Status: `complete`（2026-09-24）

千葉市は`declared_review_package_v1`としてReviewed completeです。

- Current project identities: 189 / 189
- Current work items: 406
- Current quantitative policy indicators: 40
- Overall goal indicators: 1
- Qualitative constituent factors (primary): 6
- Historical project identities: 360 / 360
- Historical repost occurrences resolved: 68 / 68
- Versioned Linkage reviewed: 66（構造的一致60、公式PDF手動確認6）
- Versioned Linkage deferred: 旧294事業・現行123事業
- Fiscal top-line records: 3

未接続の旧事業を終了、現行事業を新規と自動判定せず、改称・統合・分割も名称類似だけでは確定しません。現行計画の将来年度進捗、個別事業費・契約・補助金接続も`deferred_depth`として明示します。

正本:

- `data/catalog/chiba_phase13_completion.json`
- `schemas/chiba_phase13_completion.schema.json`
- `data/catalog/chiba_phase13_policy_review_manifest.json`
- `data/catalog/chiba_current_project_work_item_review_manifest.json`
- `data/catalog/chiba_historical_project_identity_review_manifest.json`
- `data/catalog/chiba_versioned_project_linkage_review.json`
- `tests/test_phase13_chiba_completion.py`

### Milestone M6 — Yokohama reviewed complete

Status: `complete`（2026-09-25）

横浜市は`declared_review_package_v1`としてReviewed completeです。

- Current plan adoption: 2026-06-05
- Current policy groups: 14
- Current measure groups: 33
- Cross-cutting project themes: 3
- Policy monitoring indicator identities: 15
- Official proposal snapshot values: 15
- Final-booklet value confirmation deferred: 15
- Historical 2022–2025 source-reported aggregate: 指標改善・向上 約90%、外部環境影響を除いた目標達成率 約79%
- Fiscal top-line records: 3

政策群と施策群、政策指標と施策指標、原案snapshotと最終冊子、旧2022〜2025計画と現行2026〜2029計画、当初予算と決算をそれぞれ別version / evidence roleとして保持します。原案詳細値を最終確定値へ自動昇格せず、旧計画の90%・79%を現行計画実績やJichi Insight独自の達成率へ変換しません。

正本:

- `data/catalog/yokohama_phase13_completion.json`
- `schemas/yokohama_phase13_completion.schema.json`
- `data/catalog/yokohama_phase13_policy_review_manifest.json`
- `data/catalog/yokohama_current_policy_structure.json`
- `data/catalog/yokohama_policy_monitoring_indicator_proposal_snapshot.json`
- `data/catalog/yokohama_prior_plan_final_review_summary.json`
- `tests/test_phase13_yokohama_completion.py`

### Milestone M7 — Kawasaki reviewed complete

Status: `complete`（2026-09-25）

川崎市は`declared_review_package_v1`としてReviewed completeです。

- Current basic policies: 5
- Current policies: 18
- Current measures: 48
- Current administrative projects: 350（公式aggregate structure）
- Priority theme: 1（少子高齢化・人口減少対策）
- Priority initiative lanes: 5
- Historical FY2024 evaluation: 74施策・572事務事業
- Historical source-reported breakdown: 17件上回る、462件ほぼ達成、93件下回る、上回る又はほぼ達成83.8%
- FY2026 general-account initial budget: 937,753,480,000円
- FY2024 general-account settlement estimate: 歳入871,327,000,000円 / 歳出862,154,000,000円
- Fiscal top-line records: 3

350事務事業の個票identity、48施策の成果指標、現行2026〜2029計画の年度進捗、旧第3期572事業と現行第4期350事業のversioned linkage、個別事業と予算・契約・補助金の接続は`deferred_depth`として明示します。旧計画の17/462/93および83.8%は川崎市によるsource-reported evaluationであり、現行計画実績やJichi Insight独自の政策達成率へ変換しません。

正本:

- `data/catalog/kawasaki_phase13_completion.json`
- `schemas/kawasaki_phase13_completion.schema.json`
- `data/catalog/kawasaki_phase13_policy_review_manifest.json`
- `data/catalog/kawasaki_current_policy_structure.json`
- `data/catalog/kawasaki_prior_plan_2024_evaluation_summary.json`
- `data/reviewed/kawasaki-city/plan_review.json`
- `data/reviewed/kawasaki-city/fiscal_records.json`
- `tests/test_phase13_kawasaki_completion.py`

### Milestone M8 — Sagamihara reviewed complete

Status: `complete`（2026-09-27）

相模原市は`declared_review_package_v1`としてReviewed completeです。

- Current basic-plan period: 2020〜2027年度
- Current vision groups: 6（aggregate）
- Current measures: 47（aggregate）
- Latest rolling implementation program: 2026〜2028年度
- Current priority themes: 3（少子化対策、雇用促進対策、中山間地域対策）
- Midterm progress coverage: 2020〜2024年度、全47施策＋重点テーマ
- Evaluation lanes: 市の1次評価、総合計画審議会の2次評価、市民アンケート
- FY2026 general-account initial budget: 405,500,000,000円
- FY2024 general-account settlement: 歳入359,794,590,156円 / 歳出349,624,530,765円
- Fiscal top-line records: 3

47施策の個別identity・評価結果・成果指標、最新推進プログラムの個別事業、設問別・属性別市民アンケート、現基本計画2020〜2027と2028年度を含むローリング推進プログラム／次期総合計画のversion transition、個別財政接続は`deferred_depth`として明示します。行政1次評価、審議会2次評価、市民アンケートを統合スコアへ変換しません。

正本:

- `data/catalog/sagamihara_phase13_completion.json`
- `schemas/sagamihara_phase13_completion.schema.json`
- `data/catalog/sagamihara_phase13_policy_review_manifest.json`
- `data/catalog/sagamihara_current_policy_structure.json`
- `data/catalog/sagamihara_current_progress_review_summary.json`
- `data/reviewed/sagamihara-city/plan_review.json`
- `data/reviewed/sagamihara-city/fiscal_records.json`
- `tests/test_phase13_sagamihara_completion.py`

### Milestone M9 — Niigata reviewed complete

Status: `complete`（2026-09-27）

新潟市は`declared_review_package_v1`としてReviewed completeです。

- Current plan period: 2023〜2030年度
- Current fields: 8
- Current policies: 16
- Current measures: 45（aggregate）
- Priority strategies: 10
- Sustainable-governance pillars: 3
- Overall indicators: 4
- FY2025 overall-indicator results reviewed: 4
- Policy-indicator universe: 87
- Accountability lanes: 行政進捗評価・外部有識者・市民アンケート
- FY2026 general-account initial budget: 442,500,000,000円
- FY2024 general-account settlement: 歳入463,544,553,000円 / 歳出452,133,373,000円
- Fiscal top-line records: 3

4総合指標のA/B/Cは新潟市によるsource-reported evaluationとして保持し、Jichi Insight独自評価へ変換しません。2026年度中間見直し素案はdraft versionのまま隔離します。45施策、87政策指標、取組指標、主な事業の個票完全構造化、正式な中間見直し、2027〜2030年度後期実施計画、個別財政接続は`deferred_depth`として明示します。

正本:

- `data/catalog/niigata_phase13_completion.json`
- `schemas/niigata_phase13_completion.schema.json`
- `data/catalog/niigata_phase13_policy_review_manifest.json`
- `data/catalog/niigata_current_policy_structure.json`
- `data/catalog/niigata_current_progress_review_summary.json`
- `data/reviewed/niigata-city/plan_review.json`
- `data/reviewed/niigata-city/fiscal_records.json`
- `tests/test_phase13_niigata_completion.py`

### Milestone M10 — Shizuoka reviewed complete

Status: `complete`（2026-09-27）

静岡市は`declared_review_package_v1`としてReviewed completeです。

- Current plan period: 2026〜2035年度
- Plan layers: 3
- Current policy fields: 9
- Current policies: 45（aggregate）
- Current implementation plan: 2026〜2030年度、毎年度改定
- Implementation semantics: 施策ごとに成果指標、取組名・内容・事業費・担当課
- Current fifth-plan annual progress: 0（not_yet_available）
- Historical progress route preserved: 第4次総2024年度評価
- FY2026 general-account initial budget: 403,500,000,000円
- FY2024 general-account settlement: 歳入387,089,852,000円 / 歳出376,221,432,000円
- Fiscal top-line records: 3

第5次総の年度実績がまだ公表されていないため、存在しないResultを推測で作らず、旧第4次総2024評価をcurrent actualへ流用しません。45政策・成果指標・実施計画取組の個票完全構造化、第5次総の将来年度実績、第4次総→第5次総のversioned linkage、個別財政接続は`deferred_depth`として明示します。

正本:

- `data/catalog/shizuoka_phase13_completion.json`
- `schemas/shizuoka_phase13_completion.schema.json`
- `data/catalog/shizuoka_phase13_policy_review_manifest.json`
- `data/catalog/shizuoka_current_policy_structure.json`
- `data/catalog/shizuoka_current_progress_availability.json`
- `data/reviewed/shizuoka-city/plan_review.json`
- `data/reviewed/shizuoka-city/fiscal_records.json`
- `tests/test_phase13_shizuoka_completion.py`

### Milestone M11 — Hamamatsu reviewed complete

Status: `complete`（2026-09-28）

浜松市は`declared_review_package_v1`としてReviewed completeです。

- Current basic-plan period: 2025〜2034年度
- Current fields: 7
- Current basic policies: 25
- Current policies: 125（aggregate）
- Outcome-indicator universe: 38
- Life-satisfaction indicators: 50（総合8・分野7・個別35）
- FY2025 reviewed life-satisfaction results: 15（総合8・分野7）
- FY2026 implementation plan: Action / PDCA・OODA・EBPM
- FY2026 general-account initial budget: 440,100,000,000円
- FY2024 general-account settlement: 歳入416,537,079,000円 / 歳出403,849,303,000円
- Fiscal top-line records: 3

2025年度にレビューした15件は市民の主観的実感を測る指標であり、政策効果や因果関係を直接示すものではありません。成果指標38件、125政策、個別実感35指標、実施計画事業の完全個票化、2026年度通年Result、個別財政接続は`deferred_depth`として明示します。

正本:

- `data/catalog/hamamatsu_phase13_completion.json`
- `schemas/hamamatsu_phase13_completion.schema.json`
- `data/catalog/hamamatsu_phase13_policy_review_manifest.json`
- `data/catalog/hamamatsu_current_policy_structure.json`
- `data/catalog/hamamatsu_current_implementation_review_summary.json`
- `data/reviewed/hamamatsu-city/plan_review.json`
- `data/reviewed/hamamatsu-city/fiscal_records.json`
- `tests/test_phase13_hamamatsu_completion.py`

### Milestone M12 — Nagoya reviewed complete

Status: `complete`（2026-09-28）

名古屋市は`declared_review_package_v1`としてReviewed completeです。

- Current plan period: 2024〜2028年度
- City visions: 5
- Current measures: 42（aggregate）
- Outcome indicators: 135（aggregate）
- Listed projects: 506（aggregate）
- FY2024 indicator classification: A54 / B18 / C23 / D40
- FY2024 source-reported A+B+C: 95 / 135
- FY2024 project classification: ☆☆☆☆384 / ☆☆☆96 / ☆☆20 / ☆6 / 全面的見直し0
- FY2024 source-reported upper two project classes: 480 / 506
- Citizen survey: 4,000人対象、有効回収率44.2%
- FY2026 general-account initial budget (amended enacted version): 1,696,086,000,000円
- FY2024 general-account settlement: 歳入1,505,378,206,754円 / 歳出1,486,264,707,319円
- Fiscal top-line records: 3

95/135および480/506は名古屋市によるsource-reported aggregateです。未確認個票へ機械配分せず、Jichi Insight独自の政策達成度へ変換しません。42施策・135指標・506事業の完全個票化、市民アンケート詳細、概算事業費と一般会計財政の個別接続は`deferred_depth`として明示します。

正本:

- `data/catalog/nagoya_phase13_completion.json`
- `schemas/nagoya_phase13_completion.schema.json`
- `data/catalog/nagoya_phase13_policy_review_manifest.json`
- `data/catalog/nagoya_current_policy_structure.json`
- `data/catalog/nagoya_current_progress_review_summary.json`
- `data/reviewed/nagoya-city/plan_review.json`
- `data/reviewed/nagoya-city/fiscal_records.json`
- `tests/test_phase13_nagoya_completion.py`

### Milestone M13 — Kyoto reviewed complete

Status: `complete`（2026-09-28）

京都市は`declared_review_package_v1`としてReviewed completeです。

- Current basic concept: 2026〜2050年
- Current strategy: 2024〜2027年度（令和8年3月改定）
- Current strategy policies: 6
- Strategy components: 3（政策、しごとの仕方改革、持続可能な行財政運営の確立）
- Strategic perspectives: 3（ひらく、きわめる、つなぐ）
- Current FY2024 strategy progress route: published
- Historical basic-plan policy fields preserved: 27（京プラン2025）
- Accountability lanes: 行政実施報告・市会報告・監査
- FY2026 general-account initial budget: 1,007,967,000,000円
- FY2024 general-account settlement: 歳入980,100,000,000円 / 歳出971,800,000,000円（公式資料の億円表示に基づくrounded source value）
- Fiscal top-line records: 3

同じ2024年度報告内でも、現行新京都戦略と旧京プラン2025の27政策分野を別versionとして保持します。6政策配下の施策・KPI・実績、リーディング・プロジェクト・政策集の全件個票、京都基本構想と新京都戦略の細粒度linkage、個別財政接続は`deferred_depth`として明示します。行政実施報告・市会報告・監査を統合スコアへ変換しません。

正本:

- `data/catalog/kyoto_phase13_completion.json`
- `schemas/kyoto_phase13_completion.schema.json`
- `data/catalog/kyoto_phase13_policy_review_manifest.json`
- `data/catalog/kyoto_current_strategy_structure.json`
- `data/catalog/kyoto_current_progress_review_summary.json`
- `data/reviewed/kyoto-city/plan_review.json`
- `data/reviewed/kyoto-city/fiscal_records.json`
- `tests/test_phase13_kyoto_completion.py`

### Milestone M14 — Osaka reviewed complete

Status: `complete`（2026-09-29）

大阪市は`declared_review_package_v1`としてReviewed completeです。

- Basic concept urban visions: 3
- FY2026 annual city-policy domains: 4
- FY2026 initiative headings: 15
- Ward operating-policy lanes: 24
- Listed bureau/office lanes: 28（うち府市共同設置2局）
- Latest completed operating-policy self-evaluation: FY2025
- FY2026 general-account initial budget: 2,188,221,000,000円
- FY2024 general-account settlement: 歳入2,090,062,147,558円 / 歳出2,065,562,115,148円
- Fiscal top-line records: 3

大阪市は単一の多年度実施計画ではなく、基本構想、年度市政運営方針、区・局の年度運営方針・自己評価という分散型構造を持つため、その構造をそのまま保持します。FY2025自己評価をFY2026 actualへ流用せず、24区・各局のsource-reported evaluationを全市統合スコアへ変換しません。個別区・局の指標・実績・自己評価、FY2026方針との細粒度linkage、FY2026通年Result、個別財政接続は`deferred_depth`として明示します。

正本:

- `data/catalog/osaka_phase13_completion.json`
- `schemas/osaka_phase13_completion.schema.json`
- `data/catalog/osaka_phase13_policy_review_manifest.json`
- `data/catalog/osaka_current_policy_structure.json`
- `data/catalog/osaka_current_progress_review_summary.json`
- `data/reviewed/osaka-city/plan_review.json`
- `data/reviewed/osaka-city/fiscal_records.json`
- `tests/test_phase13_osaka_completion.py`

### Milestone M15 — Sakai reviewed complete

Status: `complete`（2026-09-29）

堺市は`declared_review_package_v1`としてReviewed completeです。

- Current top-level plan: 堺市基本計画2030（2026〜2030年度）
- KGI: 3
- Priority strategies: 5
- Measures: 27
- Current completed annual results: 0（not_yet_available）
- FY2026 general-account initial budget: 521,700,000,000円
- FY2024 general-account settlement: 歳入477,935,503,067円 / 歳出470,108,227,969円

旧基本計画2025の進捗を現行2030計画のactualへ流用しません。個別KPI・事業・versioned linkage・個別財政接続は`deferred_depth`として保持します。

### Milestone M16 — Kobe reviewed complete

Status: `complete`（2026-09-29）

神戸市は`declared_review_package_v1`としてReviewed completeです。

- Sixth Basic Plan: 2026〜2035年度
- Kobe 2030 Vision: 2026〜2030年度
- Current directions: 3
- Progress governance: annual external-expert review
- Current completed annual results: 0（not_yet_available）
- FY2026 general-account initial budget: 977,781,231,000円
- FY2024 general-account settlement: 歳入945,588,848,718円 / 歳出930,659,433,328円

初年度Resultを予算や旧計画から推測せず、KGI/KPI linkage、個別事業、年度Result、個別財政接続は`deferred_depth`として保持します。

### Milestone M17 — Okayama reviewed complete

Status: `complete`（2026-09-29）

岡山市は`declared_review_package_v1`としてReviewed completeです。

- Seventh Comprehensive Plan long-term: 2026〜2035年度
- First midterm plan: 2026〜2030年度
- Perspectives: 4
- Basic directions: 8
- Policies: 30
- Measures: 99
- Current completed annual results: 0（not_yet_available）
- FY2026 general-account initial budget: 4,298億6,338万円余
- FY2024 general-account settlement: 歳入4,065億円余 / 歳出3,877億円余

公式資料の「余」を偽の円単位精度へ昇格せず、個別成果指標・取組・区別計画・最初の年度評価・個別財政接続は`deferred_depth`として保持します。

### Milestone M18 — Hiroshima reviewed complete

Status: `complete`（2026-09-29）

広島市は`declared_review_package_v1`としてReviewed completeです。

- Planning layers: 3（基本構想・基本計画・実施計画）
- Sixth Basic Plan: 2020〜2030年度
- Current implementation plan: 2025〜2030年度
- Progress governance: KPI + external-input PDCA
- Separately identified current annual-result package: 0（v1 source set）
- FY2026 general-account initial budget: 794,011,359,000円
- FY2024 general-account settlement: 歳入720,118,240,000円 / 歳出716,676,720,000円（万円単位公表）

PDCA governanceをannual Resultそのものへ読み替えず、KPI・事務事業・改訂履歴・個別財政接続は`deferred_depth`として保持します。

### Milestone M19 — Kumamoto reviewed complete

Status: `complete`（2026-09-29）

熊本市は`declared_review_package_v1`としてReviewed completeです。

- Eighth Comprehensive Plan: 2024〜2031年度
- Planning layers: 3
- Visions: 8
- FY2026 Action Plan priority items: 4
- Current-plan FY2024 administrative evaluation: published
- Accountability roles: municipal administrative evaluation / Comprehensive Plan Council deliberation
- FY2026 general-account initial budget: 437,840,000,000円（原案どおり可決）
- FY2024 general-account settlement: 歳入428,730,240,000円 / 歳出419,712,090,000円

行政評価と審議会審議を別Evidence roleとして保持し、source-reported進捗をJichi Insight独自の政策達成度へ変換しません。個別施策・指標・評価シート、FY2026事業、複数年度Result系列、個別財政接続は`deferred_depth`として保持します。

### Phase 13 completion gate

Status: `complete`（2026-09-29）

- Designated cities: 20 / 20
- Reviewed reference: 2
- Execution queue reviewed complete: 18 / 18
- Review in progress: 0
- Pending record review: 0
- Blocked source inventory: 0
- Independent policy-achievement assessments: 0
- Causal-attribution promotions: 0
- Unverified cross-city rankings: 0

正本:

- `data/catalog/phase13_completion.json`
- `schemas/phase13_completion.schema.json`
- `data/catalog/phase13_designated_city_review_queue.json`
- `schemas/phase13_designated_city_review_queue.schema.json`
- `tests/test_phase13_completion.py`
- `tests/test_phase13_designated_city_review_queue.py`

## Phase 14 — Core cities and prefectural capitals source inventory

Status: `in_progress`（2026-09-29）

Phase 13のdesignated-city contractを再利用し、中核市・県庁所在地へSource Inventoryを拡張します。政令指定都市20市はPhase 13で完了済みのため重複対象にしません。

### Target universe

- Current core cities: 62
- Total prefectural capitals: 47
- Prefectural capitals already covered as designated cities: 15
- Remaining prefectural capitals: 32
- Core-city / remaining-capital overlap: 27
- Prefectural-capital-only: 5（新宿区、津市、山口市、徳島市、佐賀市）
- Unique Phase 14 targets: 67

対象identityは5桁標準地域コードと6桁全国地方公共団体コードを併記し、中核市status・県庁所在地statusを名称から推測しません。中核市移行候補は正式移行までは対象に自動昇格しません。

### Wave plan

- Wave 1 北海道・東北: 10
- Wave 2 関東: 12
- Wave 3 北陸・甲信: 6
- Wave 4 東海: 6
- Wave 5 近畿: 14
- Wave 6 中国: 7
- Wave 7 四国: 4
- Wave 8 九州・沖縄: 8

### Milestone P14-M1 — Hokkaido / Tohoku source inventory

Status: `complete`（2026-09-29）

10市を`source_inventory_complete`へ昇格しました。

- 函館市
- 旭川市
- 青森市
- 八戸市
- 盛岡市
- 秋田市
- 山形市
- 福島市
- 郡山市
- いわき市

各自治体で、現行計画、実施・進行管理またはそのavailability境界、FY2026予算、直近決算を公式入口で確認しています。

特に以下の境界を保持します。

- 函館市: 現行基本構想は2026年度終期、実施計画は2029年度まで、次期基本構想は策定過程
- 八戸市: 第7次総合計画は2026年度終期、FY2026年度戦略・市民委員会と次期計画策定を分離
- 福島市: 第6次総合計画を2026年度まで1年延長、次期計画とversion分離
- いわき市: 固定期間総合計画ではなく、理念・更新型経営指針・年度骨太方針の非標準modelを保持

Phase 14は`indexed_not_reviewed`のSource Inventoryです。個別政策・KPI・事業・評価値・予算額・決算額のReviewed昇格はPhase 15で行います。

### Milestone P14-M2 — Kanto source inventory

Status: `complete`（2026-09-30）

関東12自治体を`source_inventory_complete`へ昇格しました。

- 水戸市
- 宇都宮市
- 前橋市
- 高崎市
- 川越市
- 川口市
- 越谷市
- 船橋市
- 柏市
- 新宿区
- 八王子市
- 横須賀市

現行計画、実施・進行管理またはその制度根拠、FY2026予算、直近決算を公式入口で確認しました。

特に以下の境界を保持します。

- 高崎市: 公式HTMLで確認できる第6次総合計画の開始年度は保持し、終期はSource Inventoryで推測補完しない
- 川越市・川口市・越谷市・柏市: 2025～2026前後に現行計画が切り替わるため、FY2024決算をcurrent-plan actualへ流用しない
- 新宿区: special wardとして基本構想・総合計画frameworkと第三次実行計画を保持し、東京都本体やcity型modelへ変換しない
- 横須賀市: 2層型のYOKOSUKAビジョン＋実施計画を保持し、FY2026予算proposalとenacted stateを分離する

### Milestone P14-M3 — Hokuriku / Koshin source inventory

Status: `complete`（2026-09-30）

北陸・甲信6市を`source_inventory_complete`へ昇格しました。

- 富山市
- 金沢市
- 福井市
- 甲府市
- 長野市
- 松本市

現行計画、実施・進行管理、FY2026予算、直近決算の公式入口を確認しました。

特に以下の境界を保持します。

- 富山市: 第2次総合計画後期基本計画がFY2026最終年度、第3次総合計画は策定中
- 金沢市: 2024～2033未来共創計画をKPI前進期評価に基づき2026年6月改訂。原版・改訂版をversion分離
- 福井市: 第八次総合計画・実施計画がFY2026最終年度。毎年度成果報告/KPIはsource-reported evaluationとして保持
- 甲府市: 第七次総合計画がFY2026開始、2035年度まで。第1次実施計画はローリング
- 長野市: 第五次後期基本計画がFY2026最終年度、FY2027開始予定の第六次計画はdraft/transition lane
- 松本市: 第12次基本計画がFY2026開始、FY2024決算は旧第11次計画期間として分離

### Milestone P14-M4 — Tokai source inventory

Status: `complete`（2026-09-30）

東海6自治体を`source_inventory_complete`へ昇格しました。

- 岐阜市
- 豊橋市
- 岡崎市
- 一宮市
- 豊田市
- 津市

現行計画、実施・進行管理、FY2026予算、直近決算の公式入口を確認しました。

特に以下の境界を保持します。

- 岐阜市: 2022年度開始の未来のまちづくり構想について、固定終期を公式HTMLで確認できないため推測補完しない
- 豊橋市: 第6次総合計画後期基本計画はFY2026～2030、実施計画は3年ローリング、FY2024決算は前期期間
- 岡崎市: 第7次総合計画後期計画FY2026～2030。未来投資計画の進捗管理とFY2024前期期間Evidenceを分離
- 一宮市: 第7次計画最終期。FY2026～2027実施計画は終期に合わせた2年版で、第8次計画はtransition lane
- 豊田市: 第9次総合計画FY2025～2034。毎年度ローリング結果と翌年度施策別事業集を時点分離
- 津市: 期間を定めない基本構想＋FY2018～2027第2次基本計画。県庁所在地only分類を保持

### Milestone P14-M5 — Kinki source inventory

Status: `complete`（2026-09-30）

近畿14自治体を`source_inventory_complete`へ昇格しました。

- 大津市
- 豊中市
- 吹田市
- 高槻市
- 枚方市
- 八尾市
- 寝屋川市
- 東大阪市
- 姫路市
- 尼崎市
- 明石市
- 西宮市
- 奈良市
- 和歌山市

現行計画、実施・進行管理、FY2026予算、直近決算の公式入口を確認しました。

特に以下の境界を保持します。

- 吹田市: 第4次総合計画はFY2019～2028だが、最新5年ローリング実施計画はFY2026～2030。期間差をそのまま保持
- 枚方市: 第5次総合計画基本構想はFY2016開始で固定終期を設定せず、第3期実行計画のみFY2024～2027
- 八尾市・尼崎市・明石市: FY2024実績・決算をcurrent後期計画・戦略のactualへ流用しない
- 東大阪市: 第2次実施計画Ver.1.0/2.0/3.0と年度PDCAをversioned Evidenceとして分離
- 姫路市: 施策評価3年周期と事業PDCA年次周期を統合しない
- 奈良市: 第5次総合計画FY2022～2031の前期推進方針がFY2026最終年度で、後期推進方針はtransition lane
- 和歌山市: 第5次長期総合計画FY2017～2026の最終年度と次期計画transitionを分離

### Milestone P14-M6 — Chugoku source inventory

Status: `complete`（2026-09-30）

中国7自治体を`source_inventory_complete`へ昇格しました。

- 鳥取市
- 松江市
- 倉敷市
- 呉市
- 福山市
- 下関市
- 山口市

特に以下の境界を保持します。

- 鳥取市: 第12次総合計画がFY2026開始。基本構想10年、基本計画/実施計画5年、FY2026予算はproposal/enacted等を分離
- 松江市: MATSUE DREAMS 2030はFY2022～2029、実施計画は毎年度PDCA更新、KPI進捗はsource-reported
- 倉敷市: 第七次総合計画FY2021～2030、年度実施計画・行政評価・市民アンケートを別Evidence roleで保持
- 呉市: FY2026に後期基本計画へ移行。年度構成事業集/KPI進捗と前期期間FY2024決算をversion分離
- 福山市: 第3期福山みらい創造ビジョンがFY2026開始。第2期効果検証を第3期actualへ流用しない
- 下関市: 第3次総合計画FY2025～2034、FY2026～2030実施計画は2026年9月までに第2次改定。改定履歴を保持
- 山口市: 県庁所在地only。後期基本計画FY2023～2027、第9次実行計画FY2026～2028、FY2028次期計画transitionを分離

### Milestone P14-M7 — Shikoku source inventory

Status: `complete`（2026-09-30）

四国4自治体を`source_inventory_complete`へ昇格しました。

- 徳島市
- 高松市
- 松山市
- 高知市

特に以下の境界を保持します。

- 徳島市: 県庁所在地only。総合計画2025、前期/後期基本計画、毎年度アクションプラン、外部評価委員会を別layerで保持
- 高松市: 第7次総合計画FY2024～2031。第1期まちづくりプランFY2024～2026と第2期FY2026～2028がFY2026で重複
- 松山市: 第7次総合計画FY2025～2034、実施計画FY2025～2027。FY2024決算・監査は旧第6次計画期間
- 高知市: 後期基本計画の名目終期はFY2030だが、公式方針ではFY2026末で現行計画を廃止しFY2027～2034新計画へ移行予定。nominal/effective periodを分離

### Current work — Kyushu / Okinawa source inventory

Status: `in_progress`

Wave 8は久留米市（402036）から開始します。

Canonical status:

- Source inventory complete: 59 / 67
- Source inventory in progress: 1
- Pending source inventory: 7
- Next official code: 402036

正本:

- `data/catalog/phase14_core_capital_target_registry.json`
- `data/catalog/phase14_core_capital_execution_queue.json`
- `schemas/phase14_core_capital_target_registry.schema.json`
- `schemas/phase14_core_capital_execution_queue.schema.json`
- `schemas/phase14_municipality_source_inventory.schema.json`
- `tests/test_phase14_core_capital_registry.py`
- `tests/test_phase14_wave1_source_inventory.py`
- `tests/test_phase14_wave2_source_inventory.py`
- `tests/test_phase14_wave3_source_inventory.py`
- `tests/test_phase14_wave4_source_inventory.py`
- `tests/test_phase14_wave5_source_inventory.py`
- `tests/test_phase14_wave6_source_inventory.py`
- `tests/test_phase14_wave7_source_inventory.py`

## After Phase 14

1. Phase 15 — 中核市・県庁所在地のrecord-level Reviewed化
2. その他市区町村
3. 選挙・候補者比較
4. API、データダウンロード、研究・報道向け機能
5. 比較可能性が確認された指標だけを用いた比較機能
