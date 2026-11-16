# Roadmap

Jichi Insightは日付ではなく、品質ゲートの通過で進行を管理します。`indexed`、`reviewed`、`linked`、`published`を混同せず、一次資料とEvidenceが不足する状態を推測で埋めません。

## Phase 0〜6 — Foundation and initial publication

Status: `complete_for_initial_publication`

プロジェクト憲章、PRD、編集・データ方針、モノレポ、Web、JSON Schema、CI、公式資料マップ、訂正・反論、利用規約、プライバシー、免責、運用手順、公開前監査、Production Smokeを整備しました。正式なPublic betaを経て、2026-11-15に正式公開へ移行しました（外部法務確認等の未実施事項は RELEASE_CHECKLIST に明記したうえで、公開責任者が移行を判断しました）。

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

Status: `complete`（2026-09-30）

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

### Milestone P14-M8 — Kyushu / Okinawa source inventory

Status: `complete`（2026-09-30）

九州・沖縄8自治体を`source_inventory_complete`へ昇格しました。

- 久留米市
- 佐賀市
- 長崎市
- 佐世保市
- 大分市
- 宮崎市
- 鹿児島市
- 那覇市

特に以下の境界を保持します。

- 久留米市: 久留米未来デザイン計画2035がFY2026開始。FY2024決算は旧計画期間
- 佐賀市: 県庁所在地only。基本構想FY2025～2040と4年の未来共創プランを別periodとして保持
- 長崎市: 後期基本計画FY2026～2030、実施計画FY2026～2028。current施策評価は未公表状態を明示
- 佐世保市: 後期基本計画FY2024～2027。政策推進枠を含む予算編成過程と政策成果を分離
- 大分市: おおいたビジョン2034がFY2025開始。FY2025末114指標の自治体進捗をsource-reportedとして保持
- 宮崎市: 第六次総合計画FY2025～2034。FY2026評価はFY2025実績を対象、FY2024決算・監査は旧計画期間
- 鹿児島市: 前期基本計画・第2期実施計画がFY2026最終年度。FY2027～2031後期基本計画は素案transition lane
- 那覇市: 第5次総合計画FY2018～2027、実施計画FY2026～2028、第6次計画策定開始。overlapping horizonを保持

### Phase 14 completion

Status: `complete`（2026-09-30）

Canonical status:

- Source inventory complete: 67 / 67
- Source inventory in progress: 0
- Pending source inventory: 0
- Reviewed promotion: 0
- Phase 13 designated-city overlap: 0
- Next official code: null
- Waves complete: 8 / 8

Phase 14完了はrecord-level Reviewed完了を意味しません。67自治体すべてについて現行計画、実施・進行管理、FY2026予算、直近決算の公式Source Inventoryを確立し、非標準plan model、version transition、未公表、旧計画Evidence、budget state等の境界を保持した状態です。個別政策・KPI・事業・評価・財政値のReviewed化はPhase 15で行います。

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
- `tests/test_phase14_wave8_source_inventory.py`
- `data/catalog/phase14_completion.json`
- `schemas/phase14_completion.schema.json`
- `tests/test_phase14_completion.py`

## Phase 15 — Core cities and prefectural capitals record review

Status: `in_progress`（2026-10-01）

Phase 14で`source_inventory_complete`となった67自治体を、record-level Evidence付きの`reviewed_complete`へ昇格します。

Canonical status:

- Reviewed complete: 48 / 67（函館市、旭川市、青森市、八戸市、盛岡市、秋田市、山形市、福島市、郡山市、いわき市、水戸市、宇都宮市、前橋市、高崎市、川越市、川口市、越谷市、船橋市、柏市、新宿区、八王子市、横須賀市、富山市、金沢市、福井市、甲府市、長野市、松本市、岐阜市、豊橋市、岡崎市、一宮市、豊田市、津市、大津市、豊中市、吹田市、高槻市、枚方市、八尾市、寝屋川市、東大阪市、姫路市、尼崎市、明石市、西宮市、奈良市、和歌山市）
- Review in progress: 0
- Pending record review: 19
- Blocked source inventory: 0
- Next official code: 312010

### Milestone P15-M1 — First reviewed-complete core city

Status: `complete`（2026-10-01）

函館市をPhase 15最初の`reviewed_complete`自治体として確定しました。

v1 declared package:

- 現行基本構想 2017～2026
- 2重点プロジェクト
- 5基本目標
- 20施策
- 第3期函館市活性化総合戦略 2025～2029
- 内部評価＋函館市まち・ひと・しごと創生推進会議による外部評価の制度
- 次期基本構想2027～2036は2026-10-01時点でパブリックコメント中の素案としてtransition laneに保持
- FY2026一般会計当初予算案トップライン
- FY2024一般会計決算の歳入・歳出exact values

第3期戦略の個別KPI/current actual、現行20施策との細粒度linkage、次期構想の採択後内容、補正・執行・契約・補助金等はdeferred depthです。

### Milestone P15-M2 — Asahikawa reviewed package

Status: `complete`（2026-10-01）

旭川市をPhase 15の2市目の`reviewed_complete`自治体として確定しました。

v1 declared package:

- 第8次旭川市総合計画 2016～2027
- 基本計画 令和5年12月改定版
- 5基本目標
- 13基本政策
- 34施策
- 3重点テーマ
- 第3期推進計画 2024～2027・2026年6月改訂版
- 毎年度事業群見直し、PDCA、行政評価、4年ごとの施策評価
- 現行推進計画の評価指標appendix availabilityをreview
- FY2026一般会計当初予算 181,800,000,000円
- FY2024一般会計収入済額 182,479,594,406円
- FY2024一般会計支出済額 180,794,635,444円

評価指標全件の個別identity/value、展開施策・事業群の全件年度差分、34施策の全成果指標、次期計画確定内容、補正・執行・契約・補助金等はdeferred depthです。

### Milestone P15-M3 — Aomori reviewed package

Status: `complete`（2026-10-01）

青森市をPhase 15の3市目の`reviewed_complete`自治体として確定しました。

v1 declared package:

- 青森市総合計画前期基本計画 2024～2028
- 3政策柱
- 17政策
- 政策を実現するための5方向性
- 全施策に「目標とする指標」を設定する進行管理設計
- FY2024主要施策成果報告の年度目標値・実績値・自治体A/B/C/D評価availability
- FY2026一般会計当初予算 133,510,000,000円（原案可決）
- FY2024一般会計歳入 142,517,400,928円
- FY2024一般会計歳出 138,679,303,495円

個別指標値の全件promotion、主要事業全件、政策・指標・事業の細粒度linkage、補正・執行・契約・補助金はdeferred depthです。青森市のA/B/C/D評価をJichi Insight独自の政策達成度、因果効果、他都市比較score、rankingへ変換しません。

### Milestone P15-M4 — Hachinohe reviewed package

Status: `complete`（2026-10-01）

八戸市をPhase 15の4市目の`reviewed_complete`自治体として確定しました。

v1 declared package:

- 第7次八戸市総合計画 FY2022～FY2026
- 3行動指針
- 6政策
- 55施策
- 未来共創推進戦略2026: 9戦略
- FY2026事業一覧: 再掲込み780件 / 再掲除外691実事業
- latest completed progress review: FY2025市民委員会意見書（全616事業を基礎に6政策55施策を審議）
- FY2027開始予定「はちのへビジョン8.0」はdraft transitionとして保持
- FY2026一般会計当初予算 104,200,000,000円（原案可決）
- FY2024一般会計歳入 108,585,206千円
- FY2024一般会計歳出 105,245,944千円

FY2024決算は公式資料が千円単位のため、円換算後も1,000円未満のprecisionを主張しません。55施策の全指標、691実事業、9戦略配下の全プロジェクト、次期計画採択後version、補正・執行・契約・補助金はdeferred depthです。

### Milestone P15-M5 — Morioka reviewed package

Status: `complete`（2026-11-15）

盛岡市をPhase 15の5市目の`reviewed_complete`自治体として確定しました（公開責任者・大杉邑大のレビュー承認に基づく）。

v1 declared package:

- 盛岡市総合計画基本構想 2025～2034
- 将来像「輝きが増し 活力に満ち 夢をかなえるまち盛岡」
- 4基本目標
- 25施策
- 5自治体経営理念
- 実施計画（令和7年度から16年度）現行版 2026～2028・3年ローリング方式
- FY2026一般会計当初予算 126,510,000,000円（議案第3号 可決・成立予算）
- FY2024一般会計収入済額 135,207,433,943円
- FY2024一般会計支出済額 132,975,741,966円

実施計画の個別事業・指標の全件identityと実績、現行計画の年次評価証拠、FY2024決算と個別事業の接続（not_assessableとして保持）、補正・執行・契約・補助金はdeferred depthです。議案第3号の議決確認は市議会だよりの議決結果表を暫定locatorとし、公式議決結果ページでの直接確認は未達のまま残存事項として明記します。

### Milestone P15-M6 — Akita reviewed package

Status: `complete`（2026-11-15）

秋田市をPhase 15の6市目の`reviewed_complete`自治体として確定しました（公開責任者・大杉邑大のレビュー承認に基づく）。

v1 declared package:

- 第15次秋田市総合計画（秋田市『プラスの循環』プラン） 2026～2030
- 基本構想＋推進計画（第3期秋田市まち・ひと・しごと創生総合戦略と統合）の2部構成
- 将来都市像 5
- 政策見出し 12
- プラスの循環戦略 5
- 前計画：第14次秋田市総合計画（県都『あきた』創生プラン） 2021～2025（別計画であり直接比較しない）
- FY2026一般会計当初予算 144,180,000,000円（議案第2号 可決（賛成多数）・成立予算、議決は市議会公式の議決結果ページで直接確認）
- FY2024一般会計歳入 154,582,839千円
- FY2024一般会計歳出 152,675,103千円

第15次計画の全施策・全KPIの網羅的集計、基本構想全体版PDFの全文確認、第14次・第15次計画の施策新旧対応、現行計画の年次評価証拠、FY2024決算と個別事業の接続（not_assessableとして保持）、補正・執行・契約・補助金はdeferred depthです。

### Milestone P15-M7 — Yamagata reviewed package

Status: `complete`（2026-11-15）

山形市をPhase 15の7市目の`reviewed_complete`自治体として確定しました（公開責任者・大杉邑大のレビュー承認に基づく）。

v1 declared package:

- 山形市発展計画2030 2025～2029（令和7年3月策定、「地方版総合戦略」を兼ねる）
- 計画本編は第1章～第5章で構成され、第4章に19の政策分野を掲げる
- 政策分野 19
- 成果指標 45（政策分野ごとに基準値・目標値を設定）
- 前計画：山形市発展計画2025 2020～2024（別計画であり直接比較しない）
- FY2026一般会計当初予算 117,146,000,000円（議第8号 原案のとおり可決・成立予算、議決は市議会公式の議決議案一覧で確認）
- FY2024一般会計歳入 114,253,058,301円
- FY2024一般会計歳出 111,230,120,306円

19政策分野・45成果指標の個別名称の全件列挙とKPI詳細、計画本編PDFの全文確認、発展計画2025と発展計画2030の新旧対応、現行計画の年次評価証拠、FY2024決算の認定日・認定結果、FY2024決算と個別事業の接続（not_assessableとして保持）、FY2026補正予算の有無、決算の施策別内訳、補正・執行・契約・補助金はdeferred depthです。

### Milestone P15-M8 — Fukushima reviewed package

Status: `complete`（2026-11-15）

福島市をPhase 15の8市目の`reviewed_complete`自治体として確定しました（公開責任者・大杉邑大のレビュー承認に基づく）。

v1 declared package:

- 第6次福島市総合計画 2021～2026（当初2021～2025、令和8年3月に1年延長）
- 構成は「まちづくり基本ビジョン」と「実行プラン」の2階層
- 計画期間の延長は令和8年3月市議会定例会議で議決され、FY2024決算・FY2026当初予算はいずれも現行計画の期間内（FY2026は最終年度）
- FY2026一般会計当初予算 124,500,000,000円（議案第5号 原案可決・成立予算、議決は市議会公式の審議結果で確認、千円単位の精度は予算概要資料編の表で確定）
- FY2024一般会計歳入 136,983,126,064円
- FY2024一般会計歳出 130,714,101,758円

基本方針・重点施策・個別施策の個別名称の全件列挙と指標値、まちづくり基本ビジョン・実行プランの全文確認、FY2024実行プラン評価の内容取り込み、議案第5号の賛否内訳・議事録、FY2024決算と個別事業の接続（not_assessableとして保持）、決算の施策別内訳、第7次福島市総合計画との新旧対応、補正・執行・契約・補助金はdeferred depthです。

### Milestone P15-M9 — Koriyama reviewed package

Status: `complete`（2026-11-15）

郡山市をPhase 15の9市目の`reviewed_complete`自治体として確定しました（公開責任者・大杉邑大のレビュー承認に基づく）。

v1 declared package:

- 郡山市第7次総合計画 2026～2033（2026年4月開始）
- 構成は公共計画（本編）と行政計画（第1次実施計画）の2層で、人口ビジョン・総合戦略を一体的に策定
- FY2024決算は旧枠組み「郡山市まちづくり基本指針（あすまちこおりやま）」の第七次実施計画（2024～2027）の初年度に帰属し、現行計画の期間外のため現行計画の事業へ接続しない
- FY2026一般会計当初予算 144,720,000,000円（議案第39号 原案可決・賛成多数・成立予算、議決は市議会公式の議決結果で確認）
- FY2024一般会計歳入 160,788,173,369円
- FY2024一般会計歳出 154,354,939,781円

基本目標・政策パッケージ・個別施策の個別名称の全件列挙とKPI、公共計画本編PDFの全文確認、新旧計画の施策・KPI対応、現行計画の年次評価証拠、議案第39号の議員別賛否、成立後の当初予算書本体との最終数値突合、補正予算を含む予算現額、FY2024決算と個別事業の接続（not_assessableとして保持）、決算の施策別内訳、補正・執行・契約・補助金はdeferred depthです。

### Milestone P15-M10 — Utsunomiya reviewed package

Status: `complete`（2026-11-15）

宇都宮市をPhase 15の10市目の`reviewed_complete`自治体として確定しました（公開責任者・大杉邑大のレビュー承認に基づく）。

v1 declared package:

- 第6次宇都宮市総合計画（基本構想は目標年次2050年、基本計画2018年度～2027年度の前期・後期各5年、実施計画は3年間程度・毎年改定）
- 後期基本計画の政策の柱は6つの未来都市（子育て・教育、健康・福祉、安全・安心、魅力創造・交流、産業・環境、交通）と行政経営基盤
- FY2026一般会計当初予算 246,550,000,000円（議案第18号 原案可決・成立予算、議決は市議会公式の会議結果ページで直接確認）
- FY2024一般会計歳入 242,716,210千円
- FY2024一般会計歳出 236,437,643千円
- FY2024決算の認定は議案第102号（2025年9月30日・原案認定）

後期基本計画の戦略事業・施策・KPIの全件列挙、計画書本編の全文確認、FY2024決算の円単位総額、行政評価の個別結果、FY2024決算と個別事業の接続（not_assessableとして保持）、補正・執行・契約・補助金はdeferred depthです。

### Milestone P15-M11 — Maebashi reviewed package

Status: `complete`（2026-11-15）

前橋市をPhase 15の11市目の`reviewed_complete`自治体として確定しました（公開責任者・大杉邑大のレビュー承認に基づく）。

v1 declared package:

- 第七次前橋市総合計画（2018年3月策定、2018年度～2027年度、基本構想＋推進計画の2層構成、推進計画は3～4年ごと見直し、現行は第3期推進計画2025年度～2027年度）
- 推進計画は基本構想の6つの柱に対応する6章構成
- FY2026一般会計当初予算 161,841,682,000円（議案第15号・可決（多数）・成立予算。候補の161,841,680,000円は市長説明の万円精度記載からの転記誤りであり、本ブランチで候補ごと訂正）
- FY2024一般会計歳入 159,237,541,694円（監査委員の決算審査意見書の円単位額）
- FY2024一般会計歳出 154,807,075,147円
- FY2024決算の認定は議案第94号（可決（全員）。結果表に議決日の印字がないため日付は記録しない）

推進計画の重点施策・個別事業・KPIの全件列挙、計画書本編の全文確認、行政評価の個別結果、FY2024決算と個別事業の接続（not_assessableとして保持）、補正・執行・契約・補助金はdeferred depthです。

### Milestone P15-M12 — Takasaki reviewed package

Status: `complete`（2026-11-15）

高崎市をPhase 15の12市目の`reviewed_complete`自治体として確定しました（公開責任者・大杉邑大のレビュー承認に基づく）。

v1 declared package:

- 高崎市第6次総合計画（2018年度～2027年度、3節構成：第1節 都市づくりの基本戦略14戦略、第2節 地域の特性を生かした振興策7地域、第3節 主要施策4分野。一般的な3層モデルには当てはめない）
- FY2026一般会計当初予算 175,220,000,000円（議案第28号・原案可決（賛成多数）・成立予算。議決結果PDFに個別の議決日の印字がないため日付は記録しない）
- FY2024一般会計歳入 183,362,219千円（包括外部監査報告書の千円単位額。候補の万円丸め値183,362,220,000円は検証値と異なるため、本ブランチで候補ごと訂正）
- FY2024一般会計歳出 177,037,888千円（同上。候補の177,037,890,000円もあわせて訂正）
- FY2024決算の認定は議案第78号（令和7年第4回定例会）

14戦略・施策の全件列挙、計画書本編の全文確認、FY2024決算の円単位総額、指定事業の進行管理結果、FY2024決算と個別事業の接続（not_assessableとして保持）、補正・執行・契約・補助金はdeferred depthです。

### Milestone P15-M13 — Kawagoe reviewed package

Status: `complete`（2026-11-15）

川越市をPhase 15の13市目の`reviewed_complete`自治体として確定しました（公開責任者・大杉邑大のレビュー承認に基づく）。

v1 declared package:

- 第五次川越市総合計画（基本構想2026年度～2035年度、前期基本計画2026年度～2030年度、後期基本計画2031年度～2035年度、実施計画2026年度～2028年度ローリング、8分野・38施策、将来都市像『ずっと安心、もっと幸せ、魅力あふれるまち 川越』）
- FY2026一般会計当初予算 143,850,000,000円（議案第29号・原案可決・成立予算）
- FY2024一般会計歳入 136,944,893,371円
- FY2024一般会計歳出 130,469,349,651円
- FY2024決算の認定は議案第66号（2025年9月29日認定）。FY2024は第四次計画の後期基本計画（2021年度～2025年度）に帰属

38施策の個別名称・KPIの全件列挙、計画書本編の全文確認、FY2024決算と現行計画事業の接続（not_assessableとして保持）、補正・執行・契約・補助金はdeferred depthです。

### Milestone P15-M14 — Kawaguchi reviewed package

Status: `complete`（2026-11-15）

川口市をPhase 15の14市目の`reviewed_complete`自治体として確定しました（公開責任者・大杉邑大のレビュー承認に基づく）。

v1 declared package:

- 第6次川口市総合計画（基本構想2026年度～2035年度、前期基本計画2026年度～2030年度、後期基本計画2031年度～2035年度、実施計画3か年ローリングの3層構成、基本理念3つ、8つのめざす姿は公式ページの正式名称、将来都市像『産業と文化と自然が調和した 輝きあふれるまち 川口』）
- FY2026一般会計当初予算 256,970,000,000円（議案第18号・原案可決・成立予算。議決日は公式の議決結果表の印字どおり2026年3月23日）
- FY2024一般会計歳入 259,800,531,831円
- FY2024一般会計歳出 247,943,564,747円
- FY2024決算の認定は議案第183号（2025年11月28日認定）。12月定例会の議決結果表における議決番号は未確認の残件。FY2024は第5次計画の後期基本計画（2021年度～2025年度）に帰属

8つのめざす姿配下の施策・KPIの全件列挙、計画書本編の全文確認、認定の議決番号確認、FY2024決算と現行計画事業の接続（not_assessableとして保持）、補正・執行・契約・補助金はdeferred depthです。

### Milestone P15-M15 — Iwaki reviewed package

Status: `complete`（2026-11-15）

いわき市をPhase 15の15市目の`reviewed_complete`自治体として確定しました（公開責任者・大杉邑大のレビュー承認に基づく）。

v1 declared package:

- いわき市まちづくりの基本方針（固定期間の総合計画は存在しない。旧総合計画は令和2年度で終了し、固定終期を持たない方針体系：普遍的な『まちづくりの理念』（めざすべきまちの姿『誰もが「住んで良かった、住み続けたい」と思える魅力にあふれた「いわき」』）＋毎年度検証・更新する『まちづくりの経営指針』＋年度途中策定の『いわき版骨太の方針』。令和8年度経営指針は5つの柱：次世代を育てる／命・暮らしを守る／まちの魅力を高める／豊かさを創る／構造改革・DX推進事業。計画期間は存在しないため記録しない）
- FY2026一般会計当初予算 159,490,126,000円（議案第35号・原案可決・2026年3月12日・成立予算）
- FY2024一般会計歳入 162,539,391,275円
- FY2024一般会計歳出 155,415,603,914円
- FY2024決算の認定は議案第18号（令和7年10月定例会からの継続審査を経て2025年12月19日認定）。FY2024は現行の基本方針の枠組みのもとで執行された決算

経営指針の位置付け事業の個別詳細・実績、監査委員の決算審査意見の内容確認、事項別明細との突合、FY2024決算と経営指針事業の接続（not_assessableとして保持）、補正・執行・契約・補助金はdeferred depthです。

### Milestone P15-M16 — Mito reviewed package

Status: `complete`（2026-11-15）

水戸市をPhase 15の16市目の`reviewed_complete`自治体として確定しました（所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

v1 declared package:

- 水戸市第7次総合計画－みと魁・Nextプラン－（基本構想2024年度～2033年度、基本計画は前期2024年度～2028年度・後期2029年度～2033年度の各5年間で総論と各論で構成、3か年実施計画を毎年度ローリングで策定する3層構成。基本理念は3つ、基本計画・各論は四つの柱（まち全体で「こどもたちを育むみと」／多くの人が集い、産業が集積する「活力あるみと」／命と健康、暮らしを守る「安全・安心なみと」／市民と行政で「共に創るみと」）・11の中項目・43の小項目の施策の大綱で構成され、重点プロジェクトはMission1『みとっこ未来プロジェクト』とMission2『若い世代の移住・定住加速プロジェクト』。将来都市像は『こども育む くらし楽しむ みらいに躍動する 魁のまち・水戸』）
- FY2026一般会計当初予算 130,814,000,000円（議案第26号・原案可決・2026年3月18日・成立予算）
- FY2024一般会計歳入 128,541,227,654円
- FY2024一般会計歳出 126,380,047,662円
- FY2024決算の認定は認定第1号（一般会計及び特別会計を一括、2025年9月22日認定）。FY2024は第7次総合計画の計画期間の初年度の決算

43の小項目・施策・KPIの全件列挙、計画書本編の全文確認、監査委員の決算審査意見の内容確認、FY2024決算と第7次総合計画事業の接続（not_assessableとして保持）、補正・執行・契約・補助金はdeferred depthです。

### Milestone P15-M17 — Koshigaya reviewed package

Status: `complete`（2026-11-16）

越谷市をPhase 15の17市目の`reviewed_complete`自治体として確定しました（所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

v1 declared package:

- 第5次越谷市総合振興計画（基本構想2021年度～2030年度、基本計画は前期2021年度～2025年度・後期2026年度～2030年度の各5年間、実施計画は3年計画をローリング方式で策定する3層構成。基本理念は越谷市自治基本条例の『人間尊重』と『市民主権』で、参加・協働・情報共有の3つを原則とする。現行の後期基本計画は4章構成で、第3章分野別計画は大綱6件と大項目（施策）全24件で構成され、推進ビジョン（危機管理、地域脱炭素、デジタル化、インクルージョン（包摂性））の4つの視点を掲げ、第4章にまち・ひと・しごと創生越谷市総合戦略を位置付ける。将来像は『水と緑と太陽に恵まれた みんなが活躍する安全・安心・共生都市』）
- FY2026一般会計当初予算 132,700,000,000円（第25号議案・原案可決・2026年3月18日・成立予算）
- FY2024一般会計歳入 140,215,912,093円
- FY2024一般会計歳出 131,705,070,771円
- FY2024決算の認定は第101号議案（2025年9月25日に認定可決）。FY2024は第5次計画の前期基本計画期間の決算

後期基本計画の個別事業・達成指標の全件列挙、計画書本編の全文確認、監査委員の決算審査意見の内容確認、FY2024決算と基本計画事業の接続（not_assessableとして保持）、補正・執行・契約・補助金はdeferred depthです。

### Milestone P15-M18 — Funabashi reviewed package

Status: `complete`（2026-11-16）

船橋市をPhase 15の18市目の`reviewed_complete`自治体として確定しました（所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

v1 declared package:

- 第3次船橋市総合計画（基本構想・基本計画は2022年度～2031年度の10年間で基本計画に前期・後期の分割なし、実施計画は3年間を毎年度見直すローリング方式で現行版は2026年度～2028年度の3層構成。基本構想は5つの『めざすまちの姿』と2つの『基本姿勢』（多様な主体との協働／持続可能な行財政運営）を掲げ、基本計画は基本施策24件と施策71件で構成され、基本施策とめざすまちの姿の関係はマトリックス型で示される。将来都市像は『人も まちも 輝く 笑顔あふれる 船橋』）
- FY2026一般会計当初予算 270,640,000,000円（議案第1号・可決・2026年3月25日・成立予算）
- FY2024一般会計歳入 249,314,444千円（千円単位の公表精度）
- FY2024一般会計歳出 243,229,426千円（千円単位の公表精度）
- FY2024決算の認定は認定第1号（2025年10月3日に認定）。FY2024は第3次計画の計画期間に属する決算。決算額は千円単位の公表精度のまま保持し、円単位の総額は公式資料で確認できていないため合成しない

基本施策・施策の個別事業・達成指標の全件列挙、計画書本編の全文確認、監査委員の決算審査意見の内容確認、決算の円単位総額の確認、FY2024決算と基本計画事業の接続（not_assessableとして保持）、補正・執行・契約・補助金はdeferred depthです。

### Milestone P15-M19 — Kashiwa reviewed package

Status: `complete`（2026-11-16）

柏市をPhase 15の19市目の`reviewed_complete`自治体として確定しました（所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

v1 declared package:

- 柏市第六次総合計画（基本構想は2025年度～2034年度の10年間、基本計画は前期2025年度～2029年度・後期2030年度～2034年度の各5年間、実行計画は3年間を計画期間とし毎年度見直しを行う構造。基本構想は3つの『基本的な目標』（もっと、創造的なまちへ／もっと、居心地のよいまちへ／もっと、地域の個性が輝くまちへ）を掲げ、前期基本計画は分野横断的な3つの『重点テーマ』（全7項目）と施策体系（22分野・66施策）で構成される。将来の姿は『柏に関わる一人ひとりが想いを実現できるまち～多様な価値や人々がつながり、新たな価値の創造に挑戦～』）
- FY2026一般会計当初予算 191,224,000,000円（議案第34号・原案可決・2026年3月24日・成立予算）
- FY2024一般会計歳入 175,594,266,737円
- FY2024一般会計歳出 168,389,488,303円
- FY2024決算の認定は議案第16号（2025年10月2日に原案認定）。FY2024は旧・第五次総合計画の期間の決算

前期基本計画の個別事業・達成指標の全件列挙、計画書本編の全文確認、監査委員の決算審査意見の内容確認、FY2024決算と計画事業の接続（not_assessableとして保持）、補正・執行・契約・補助金はdeferred depthです。

### Milestone P15-M20 — Shinjuku reviewed package

Status: `complete`（2026-11-16）

新宿区をPhase 15の20番目の`reviewed_complete`自治体として確定しました（所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

v1 declared package:

- 新宿区総合計画（基本構想は平成19年度策定で、現在の基本構想は総合計画の最終年度である令和9年度まで。総合計画は平成30年度～令和9年度の10年間で基本計画と都市マスタープランを総合化した計画であり、基本計画は5つの基本政策のもとに33の個別施策を掲げる。実行計画は現行の第三次実行計画が令和6年度～令和9年度の4か年で計画事業65事業を体系化し、ローリングで見直しを行う。めざすまちの姿は『『新宿力』で創造する、やすらぎとにぎわいのまち』。新宿区は特別区であり、この体系を市型の単一総合計画モデルへ変換せずそのまま保持する）
- FY2026一般会計当初予算 187,835,560,000円（第1号議案・可決・成立予算。議決日は定例会日程から2026年3月24日と特定し、本会議録による最終確認は未実施の残件として保持する）
- FY2024一般会計歳入 190,137,549,271円
- FY2024一般会計歳出 184,195,725,502円
- FY2024決算の認定は認定第1号（2025年10月20日に認定）。FY2024は現行総合計画の期間内の決算であるが、決算総額は款別の集計値であり個別施策・計画事業との接続は行っていない

第三次実行計画の計画事業・指標の全件列挙、計画書本編の全文確認、監査委員の決算審査意見の内容確認、FY2024決算と計画事業の接続（not_assessableとして保持）、補正・執行・契約・補助金はdeferred depthです。

### Milestone P15-M21 — Hachioji reviewed package

Status: `complete`（2026-11-16）

八王子市をPhase 15の21番目の`reviewed_complete`自治体として確定しました（所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

v1 declared package:

- 八王子未来デザイン2040（基本構想は市民184名の市民会議の素案を踏まえて策定され平成24年（2012年）12月に市議会で全会一致で可決されたものを継承し、基本計画は2040年を展望して令和5年度～令和12年度（2023年度～2030年度）の8か年で、基本構想の6つの都市像のもとに37の施策を体系化する。基本理念は『人とひと、人と自然が響き合い、みんなで幸せを紡ぐまち八王子』。計画名の『2040』は将来像の展望年であり計画期間ではない。実施・進行管理は経営計画（前期 2023年度～2026年度）と年次アクションプラン、行政評価（施策評価・事務事業評価・細事業評価の3層）が担う）
- FY2026一般会計当初予算 245,100,000,000円（第5号議案・2026年3月26日可決・成立予算）
- FY2024一般会計歳入 241,406,662,517円
- FY2024一般会計歳出 236,288,910,299円
- FY2024決算の認定は第133号議案（2025年10月8日に認定）。FY2024は現行基本計画の期間内の決算であるが、決算総額は款別の集計値であり個別施策・重点事業との接続は行っていない

基本計画の細施策・KPI、経営計画の重点事業・アクションプランの詳細、行政評価の個別評価結果、計画書本編の全文確認、決算審査意見書の意見内容の精査、FY2024決算と計画事業の接続（not_assessableとして保持）、補正・執行・契約・補助金はdeferred depthです。

### Milestone P15-M22 — Yokosuka reviewed package

Status: `complete`（2026-11-16）

横須賀市をPhase 15の22番目の`reviewed_complete`自治体として確定しました（所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

v1 declared package:

- YOKOSUKAビジョン2030（横須賀市基本構想・基本計画として、従来の基本構想・基本計画・実施計画の3層構成を変更し基本構想と基本計画を一体化した2層構成の最上位計画。計画期間は令和4年度～令和11年度（2022年度～2029年度）で、市全体の未来像『変化を力に進むまち』のもとに10の分野別未来像を定める。基本構想の改訂及び基本計画の策定は議案第57号として令和4年3月24日に議決された。分野ごとの政策の方針の全件は列挙しない。実施・進行管理は横須賀再興プラン（現行は2026-2029、横須賀市まち・ひと・しごと創生総合戦略を兼ねる）と行政評価（実施計画の進行管理と事務事業等の総点検）が担う）
- FY2026一般会計当初予算 180,120,000,000円（議案第18号・2026年3月25日原案可決・成立予算）
- FY2024一般会計歳入 177,898,477,901円
- FY2024一般会計歳出 171,999,984,597円
- FY2024決算の認定は議案第100号（2025年10月7日に認定）。FY2024は現行ビジョンの期間内かつ前実施計画（2022年度～2025年度）の期間内の決算であるが、決算総額は款別の集計値であり個別の分野・事業との接続は行っていない

ビジョンの分野ごとの政策の方針の全件、再興プランの個別事業・数値目標・KPI、行政評価の個別評価結果、計画書本編の全文確認、決算審査意見書の意見内容の精査、FY2024決算と計画事業の接続（not_assessableとして保持）、補正・執行・契約・補助金はdeferred depthです。

### Milestone P15-M23 — Toyama reviewed package

Status: `complete`（2026-11-16）

富山市をPhase 15の23番目の`reviewed_complete`自治体として確定しました（所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

v1 declared package:

- 第2次富山市総合計画（基本構想・基本計画・実施計画の3層構成の最上位計画。基本構想の期間は2017年度～2026年度で、目指す都市像『人・まち・自然が調和する活力都市とやま』と基本理念（コンパクトなまちづくり）を掲げる。基本計画は前期（2017年度～2021年度）と後期（2022年度～2026年度）の各5年間で、現行の基本計画は後期基本計画であり、4つのまちづくりの目標の下に14政策・51施策を位置付ける。51施策の全件は列挙しない。実施・進行管理は年度別実施計画（現行計画の最終年度分は令和8年度実施計画）と成果重視のまちづくり（成果指標・市民意識調査・PDCA）が担う。第3次富山市総合計画は策定中であり、plan_transitionとして分離記録し内容は記録しない）
- FY2026一般会計当初予算 199,776,107,000円（議案第1号・2026年3月24日原案可決・成立予算。3月補正予算への前倒し分は含まない）
- FY2024一般会計歳入 189,996,111千円
- FY2024一般会計歳出 185,876,806千円
- FY2024決算の公表精度は千円単位であり、円単位の総額は合成していない。FY2024決算の認定は認定第1号（2025年11月28日に認定、閉会中継続審査を経て12月定例会初日に認定）。FY2024は後期基本計画の期間内の決算であるが、決算総額は款別の集計値であり個別の目標・政策・施策・事業との接続は行っていない

後期基本計画の51施策の全件、実施計画の総合計画事業・成果指標と実績、計画書本編の全文確認、第3次計画の内容、決算審査意見書における円単位総額・意見内容の確認、FY2024決算と計画事業の接続（not_assessableとして保持）、補正・執行・契約・補助金はdeferred depthです。

### Milestone P15-M24 — Kanazawa reviewed package

Status: `complete`（2026-11-16）

金沢市をPhase 15の24番目の`reviewed_complete`自治体として確定しました（所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

v1 declared package:

- 未来共創計画（金沢市都市像『未来を拓く世界の共創文化都市・金沢』（令和5年12月議決）の実現に向けた行動計画であり、市政運営の最上位計画。基本構想・基本計画・実施計画の層構造ではなく単一の10年計画（2024年度～2033年度）で、期間内に前進期（2年間）・充実期（4年間）・発展期（4年間）の3段階を設定する。都市像の5つの基本方針の下に計21の施策方針を位置付け、各施策方針にKPI（市民意識指標・施策指標）を設定する。進行管理はKPIを活用したPDCAサイクルと共創文化都市推進本部が担う。施策方針の下の施策・主要事業の全件とKPI全85項目は列挙しない。計画の版（原版・令和7年2月改訂・令和8年6月改訂）はversionを分けて保持し、改訂で追加された施策・事業を原版の体系へ遡及接続しない）
- FY2026一般会計当初予算 207,800,000,000円（成立。金沢市公報第3209号・金沢市告示第56号で確認した、市長選挙を控えた骨格予算。一般会計予算の議案番号・議決日は特定していない）
- FY2024一般会計歳入 218,624,336,395円
- FY2024一般会計歳出 210,147,360,368円
- FY2024決算の認定は認定第1号（令和7年12月定例月議会で認定、認定日は特定していない）。FY2024は未来共創計画の計画期間初年度（前進期）の決算であるが、決算総額は款別の集計値であり個別の基本方針・施策方針・KPIとの接続は行っていない

施策方針の下の施策・主要事業の全件、KPI全85項目と実績、改訂差分の詳細、決算事項別明細書の款別合計との突合、一般会計予算の議案番号・議決日と決算の認定日の特定、決算審査意見書における意見内容の確認、FY2024決算と計画事業の接続（not_assessableとして保持）、補正・執行・契約・補助金はdeferred depthです。

### Milestone P15-M25 — Fukui reviewed package

Status: `complete`（2026-11-16）

福井市をPhase 15の25番目の`reviewed_complete`自治体として確定しました（所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

v1 declared package:

- 第八次福井市総合計画（第七次計画から継承した将来都市像『みんなが輝く 全国に誇れる ふくい』の実現に向けた市政運営の指針。計画期間は2022年度～2026年度の5年間で令和8年度が最終年度。『将来都市像』『重点方針』『政策』『施策』の階層で構成し、主要な事業や数値目標を定める実施計画を別途策定する。4分野（社会基盤・市民福祉・産業・教育）のもとに14政策を位置付け、政策の下に53施策と実施計画で設定する64のKPIがある。進行管理は毎年度の総合計画レポート（成果報告書とKPI達成状況）で行い、KPI達成状況は自治体の自己評価として保持する。53施策・64KPIの全件は列挙しない。なお計画体系の確認は、計画本編ページの取得が失敗したため、公式の総合計画レポート類と公式の予算概要で行った経緯を保持し、計画本編そのもので確認したとは記録しない。第九次福井市総合計画は審議会で策定中であり、移行記録としてversionを分けて保持し、次期計画の政策・施策を第八次計画の体系へ遡及接続しない）
- FY2026一般会計当初予算 137,700,000,000円（成立。第1号議案『令和8年度福井市一般会計予算』として令和8年2月16日上程・令和8年3月19日原案可決）
- FY2024一般会計歳入 133,427,298,121円
- FY2024一般会計歳出 130,218,901,390円
- FY2024決算の認定は第66号議案（令和7年9月25日上程、2025年12月1日に認定）。FY2024は第八次計画の計画期間（2022年度～2026年度）の3年目の決算であるが、決算総額は款別の集計値であり個別の政策・施策・KPIとの接続は行っていない

53施策・64KPIの全件と実績、実施計画の主要事業の全件、計画本編そのものによる計画体系の確認、決算事項別明細書の款別合計との突合、予算書の第1号議案第1条の条文・第1表との最終突合、決算審査意見書における意見内容の確認、第九次計画の枠組み、FY2024決算と計画事業の接続（not_assessableとして保持）、補正・執行・契約・補助金はdeferred depthです。

### Milestone P15-M26 — Kofu reviewed package

Status: `complete`（2026-11-16）

甲府市をPhase 15の26番目の`reviewed_complete`自治体として確定しました（所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

v1 declared package:

- 第七次甲府市総合計画（甲府市自治基本条例第22条の規定に基づき策定する本市の最上位計画で、『基本構想』と『実施計画』の2層構成。基本構想の期間は2026年度～2035年度の10年間で、都市像は『幸せ実感 希望ある未来を創り続けるまち 甲府』であり、基本構想は議案第109号として令和7年12月17日に議決された。基本目標は3つ（未来に輝く『ひと』を育む／安全・安心で快適な『まち』を創る／都市機能と自然が調和する甲府の『魅力』を磨く）で、各基本目標に6施策、計18施策を位置付け、横断的視点（人口減少対策・持続可能な社会の構築・時代に即した行政改革）と推進理念（コラボレーション・ウェルビーイング・シビックプライド）を保持する。小施策の全件は列挙しない。実施計画は3年ごとのローリング方式により毎年度見直し、施策・事務事業を適正に評価し改善しながら推進する。令和8年度は計画の初年度であり、実施計画に基づく年度実績・評価の公表はまだない。第六次甲府市総合計画（2016年度～2025年度）とはversionを分けて保持し、第七次計画の基本目標・施策を第六次計画の体系へ遡及接続しない）
- FY2026一般会計当初予算 91,787,060千円（成立。議案第5号『令和8年度甲府市一般会計予算』として令和8年3月25日に可決。公表精度が千円単位のため千円精度のまま記録し、円単位を合成していない）
- FY2024一般会計歳入 91,644,865,806円
- FY2024一般会計歳出 90,039,308,506円
- FY2024決算の認定は議案第95号（2025年10月2日に認定）。FY2024は第六次計画の計画期間（2016年度～2025年度）の決算であり第七次計画とは対象期間が重ならないが、決算総額は款別の集計値であり個別の基本目標・施策との接続は行っていない

小施策の全件、第1次実施計画の施策・事業体系と個別事業の全件、予算書・予算に関する説明書および決算書の事項別明細書の款別合計との突合、第六次計画の枠組み、実施計画に基づく年度実績・評価のエビデンス、FY2024決算と計画事業の接続（not_assessableとして保持）、補正・執行・契約・補助金はdeferred depthです。

### Milestone P15-M27 — Nagano reviewed package

Status: `complete`（2026-11-16）

長野市をPhase 15の27番目の`reviewed_complete`自治体として確定しました（所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

v1 declared package:

- 第五次長野市総合計画（基本構想・基本計画・実施計画の3層構成の総合計画。基本構想は平成29年3月市議会で議決され、期間は2017年度～2026年度の10年間で、まちの将来像は『幸せ実感都市『ながの』〜“オールながの”で未来を創造しよう〜』である。基本計画は前期（2017年度～2021年度）・後期（2022年度～2026年度）の5年間ずつで、後期基本計画には長野市まち・ひと・しごと創生総合戦略を統合する。実施計画は1年間の計画で毎年見直しを行う。基本構想の体系は7分野・22政策であり、後期基本計画では政策の下に55施策を展開し、分野横断テーマ（総合戦略）3テーマを掲げる。55施策の全件は列挙しない。進行管理はPDCAサイクルで行い、総合計画推進本部（本部長は市長）が推進状況の確認・推進手法の検討・予算の重点配分を担い、評価・検証結果は毎年度『長野市総合計画進捗状況』として公表される。第五次計画は令和8年度が最終年度であり、次期長野市総合計画（令和9年度開始）は長野市総合審議会で策定中であり、移行記録としてversionを分けて保持し、次期計画の枠組みを第五次計画の体系へ遡及接続しない）
- FY2026一般会計当初予算 195,220,000千円（成立。議案第1号『令和8年度長野市一般会計予算』として令和8年3月23日に原案可決。公表精度が千円単位のため千円精度のまま記録し、円単位を合成していない）
- FY2024一般会計歳入 170,949,499,030円
- FY2024一般会計歳出 166,702,305,036円
- FY2024決算の認定は認定第2号（2025年9月30日に認定）。FY2024は第五次計画の計画期間内（後期基本計画の3年目）の決算であるが、決算総額は款別の集計値であり個別の政策・施策・指標との接続は行っていない

55施策の全件とその指標・実績、実施計画の個別事業の全件、予算に関する説明書および決算書の事項別明細書の款別合計との突合、総合計画進捗状況と決算総額との突合、次期計画の枠組み、FY2024決算と計画事業の接続（not_assessableとして保持）、補正・執行・契約・補助金はdeferred depthです。

### Milestone P15-M28 — Matsumoto reviewed package

Status: `complete`（2026-11-16）

松本市をPhase 15の28番目の`reviewed_complete`自治体として確定しました（所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

v1 declared package:

- 松本市基本構想2030・第12次基本計画（総合計画は基本構想・基本計画・実施計画の3層構成。松本市基本構想2030は2021年度～2030年度で、基本理念は三ガク都（岳・楽・学）に象徴される松本らしさを「シンカ」（進化・深化）させること、キャッチフレーズは『豊かさと幸せに 挑み続ける 三ガク都』であり、市民と行政が共に取り組む5つの行動目標（みとめる／まなぶ／いかす／つなぐ／いどむ）を定める。第12次基本計画は基本構想2030の後期計画で2026年度～2030年度、第3期松本版地方創生総合戦略を包含する。4つの目的のもと3つの政策の方向性・2つの重点戦略（ゼロカーボン／DX・デジタル化）・4つの重視する視点を掲げ、基本施策は7分野47施策で構成し、47施策の全件を列挙する。基本施策には成果指標（KPI）を設定し目標管理、進行管理を適切に行い、行政運営に関する施策は別途『行政行動指針』で定める。第11次基本計画（2021年度～2025年度）から第12次基本計画への移行はversionを分けて保持し、第12次基本計画の施策体系を第11次基本計画の期間の実績へ遡及接続しない）
- FY2026一般会計当初予算 114,980,000千円（成立。議案第43号『令和8年度松本市一般会計予算』として令和8年2月定例会に提出され、令和8年3月16日の本会議で議決。成立は令和8年度6月補正予算の概要が当初予算額を既定額として扱うことで裏付け。会議録本文における「原案可決」の文言自体は直接確認できていないため断定しない。公表精度が千円単位のため千円精度のまま記録し、円単位を合成していない）
- FY2024一般会計歳入 116,331,387,915円
- FY2024一般会計歳出 113,406,566,809円
- FY2024決算の認定は議案第18号（2025年11月4日に認定。決算特別委員会の閉会中継続審査を経て令和7年第3回臨時会で認定）。FY2024は第11次基本計画（2021年度～2025年度）の決算であり第12次基本計画とは計画versionが異なるため、決算総額と基本施策・成果指標との接続は行っていない

47施策の成果指標（KPI）の実績値、実施計画の個別事業の全件、予算に関する説明書および決算書の事項別明細書の款別合計との突合、第11次基本計画の枠組み、FY2024決算と計画事業の接続（not_assessableとして保持）、補正・執行・契約・補助金はdeferred depthです。

### Milestone P15-M29 — Gifu reviewed package

Status: `complete`（2026-11-16）

岐阜市をPhase 15の29番目の`reviewed_complete`自治体として確定しました（所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

v1 declared package:

- 岐阜市未来のまちづくり構想（固定期間型の総合計画ではなく構想型の枠組み。令和4（2022）年2月策定・2022年度開始で、2040年頃を見据えた将来像『人がつながる 創造が生まれる しなやかさのあるまち』とまちづくりの方向性で構成し、固定終期は定めず5年ごとに見直す。2040年頃は見据える対象年として扱い固定終期として記録しない。4つの基本的な考え方（オール岐阜のまちづくり／シビックプライドの醸成／DXと脱炭素化／持続可能で選ばれるまち）と5分野の方向性（教育・子育て／健康・福祉・医療／市民協働・防災・環境／産業・労働・交流／都市基盤整備・交通・中心市街地活性化、各分野に市民意識調査ベースの指標3件を全件列挙）に行政経営の視点が加わる。下位の岐阜市未来創生総合戦略（2024年度〜2027年度）は構想の将来像を反映し地方版総合戦略とSDGs未来都市計画を統合したもので、3本柱（ひとの創生・しごとの創生・まちの創生）で構成する。進行管理は将来像に関する3つの数値目標と分野ごとの指標で毎年度成果を確認し、未来のまちづくり懇談会が進捗評価に意見を述べる。構想の改定に向けた取組は移行記録としてのみ保持し、改定後の枠組みは記録しない）
- FY2026一般会計当初予算 200,680,000千円（成立。第1号議案『令和8年度岐阜市一般会計予算』として令和8年第1回（3月）定例会に提出され、令和8年3月27日に原案のとおり可決。公式の予算説明書の事項別明細書の歳入・歳出合計とも同額で一致。公表精度が千円単位のため千円精度のまま記録し、円単位を合成していない）
- FY2024一般会計歳入総額 198,779,091,770円
- FY2024一般会計歳出総額 192,092,917,389円
- FY2024決算の認定は第107号議案（2025年9月25日に認定）。FY2024は構想の3年目・未来創生総合戦略の初年度の決算であるが、決算総額は会計別・款別の集計値であり構想の指標は市民意識調査ベースの主観指標を中心とするため、決算総額と構想の分野・指標および総合戦略のKPIとの接続は行っていない

分野別計画の施策・事業の全件、未来創生総合戦略のKPI実績値の全件、決算書の事項別明細書の款別合計との最終突合、決算の実質収支、前身の『ぎふし未来地図』と改定後の構想の枠組み、FY2024決算と構想・戦略の接続（not_assessableとして保持）、補正・執行・契約・補助金はdeferred depthです。

### Milestone P15-M30 — Toyohashi reviewed package

Status: `complete`（2026-11-16）

豊橋市をPhase 15の30番目の`reviewed_complete`自治体として確定しました（所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

v1 declared package:

- 第6次豊橋市総合計画（基本構想・基本計画・実施計画の3層構成の固定期間型総合計画。基本構想は2021年度〜2030年度の10年間で、基本理念は『私たちがつくる 未来をつくる』、目指すまちの姿は『未来を担う 人を育むまち・豊橋』。基本計画は前期基本計画（2021年度〜2025年度）から後期基本計画（2026年度〜2030年度）へ移行し、現行は後期基本計画。後期基本計画の分野別計画は8分野・38政策で構成し全件を列挙する。分野横断の重点化事項として『まちづくり戦略』（4つの個別戦略・13の施策の基本方針）を位置付ける。進行管理は実施計画（現行は令和8〜10年度）を3年間のローリング方式で毎年度見直し、各事業にまちづくり戦略の該当を対応付けることで行い、分野横断の行政運営の取組は実施計画の『基本計画推進のために』に掲げる。前期基本計画から後期基本計画への移行は移行記録としてのみ保持し、後期基本計画の政策を前期基本計画の体系へ遡及接続しない）
- FY2026一般会計当初予算 165,610,000千円（成立。議案第4号『令和8年度豊橋市一般会計予算』として令和8年3月定例会に提出され、予算特別委員会への付託を経て、令和8年3月24日に原案可決。公式『令和8年6月市議会定例会資料（補正予算関係）』の一般会計・現計予算額とも同額で一致。公表精度が千円単位のため千円精度のまま記録し、円単位を合成していない）
- FY2024一般会計歳入総額 153,279,132,232円
- FY2024一般会計歳出総額 151,163,708,560円
- FY2024決算の認定議案である議案第95号は令和7年9月定例会で不認定となった（市長公式通知・令和7年9月29日付で確認。不認定の事実をそのまま記録し、認定されたとは記録しない。議決年月日そのものは未特定のまま保持し、市長通知の日付は通知日であって議決日と断定しない。令和7年12月定例会では報37『決算不認定に係る措置について』が報告された）。FY2024は前期基本計画期間の決算であり後期基本計画とは計画versionが異なるため、決算総額と後期基本計画の政策・まちづくり戦略との接続は行っていない

38政策に基づく分野別計画の施策・事業の全件、まちづくり戦略の基本方針ごとの事業対応の全件、予算書・決算書の事項別明細書の款別合計との最終突合、決算の実質収支に関する調書の値、議案第95号の議決年月日、前期基本計画の枠組み、FY2024決算と後期基本計画の接続（not_assessableとして保持）、補正・執行・契約・補助金はdeferred depthです。

### Milestone P15-M31 — Okazaki reviewed package

Status: `complete`（2026-11-16）

岡崎市をPhase 15の31番目の`reviewed_complete`自治体として確定しました（所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

v1 declared package:

- 第7次岡崎市総合計画（総合政策指針・未来投資計画・個別計画で構成する。総合政策指針は30年先を見据えた10年間の政策指針で、目標年度は令和32年度（2050年）、将来都市像は『一歩先の暮らしで三河を拓く 中枢・中核都市おかざき』、基本指針は公民連携による成長戦略の推進／コンパクトな都市構造の構築／まちへの誇りが育まれる社会づくり／周辺都市との連携の推進の4つ。未来投資計画は前期（2021年度〜2025年度）から後期（2026年度〜2030年度、令和8年3月改定）へ移行し、現行は後期計画。後期計画の『分野別の主な取組』は10分野・全54件で構成し全件を列挙する。分野横断の『未来投資パッケージ』（未来のまち／未来のひと／未来のしごと／未来のパートナーシップの4パッケージ）を掲げる。進行管理は10分野を『まち・環境』『ひと・社会』『しごと・経済』『行政運営・パートナーシップ』の4グループに分けて目標設定・進捗管理を行い、グループごとに参考指標（2030年の目標値と現況値）を設定する方式であり、パッケージの推進事業内訳は随時変更される。未来投資計画の前期から後期への移行は移行記録としてのみ保持し、後期計画の取組を前期期間の実績へ遡及接続しない）
- FY2026一般会計当初予算 154,850,000千円（成立。第56号議案『令和8年度岡崎市一般会計予算』として令和8年3月定例会に提出され、予算決算委員会への付託を経て、令和8年3月23日（定例会最終日）の本会議で採決。ただし令和8年3月定例会の議決結果一覧表そのものは未取得であり、『原案可決』の文言は未確認のまま保持する。成立自体は成立予算の概要の公表と補正予算（第1号〜第3号）の存在で裏付けられる。公表精度が千円単位のため千円精度のまま記録し、円単位を合成していない）
- FY2024一般会計歳入総額 157,798,763,028円
- FY2024一般会計歳出総額 148,542,565,874円
- FY2024決算の認定議案である認定第1号は令和7年9月定例会で令和7年9月30日に認定された（市議会公式『議決結果一覧表』で確認）。FY2024は未来投資計画前期期間の決算であり後期計画とは計画versionが異なるため、決算総額と後期計画の主な取組・未来投資パッケージとの接続は行っていない

54件の主な取組に基づく未来投資パッケージの推進事業の全件、グループ別参考指標の個別値、予算書・決算書の事項別明細書の款別合計との最終突合、令和8年3月定例会の議決結果一覧表による『原案可決』の文言の直接確認、監査委員の決算審査意見書の内容確認、前期計画の枠組み、FY2024決算と後期計画の接続（not_assessableとして保持）、補正・執行・契約・補助金はdeferred depthです。

### Milestone P15-M32 — Ichinomiya reviewed package

Status: `complete`（2026-11-16）

一宮市をPhase 15の32番目の`reviewed_complete`自治体として確定しました（所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

v1 declared package:

- 第7次一宮市総合計画（基本構想・基本計画・実施計画の3層で構成する。基本構想は2018年度〜2027年度の10年間で、都市将来像は『木曽の清流に映え、心ふれあう躍動都市 一宮』、「5つのプラン」と「2つのマネジメント」を掲げる。基本計画は前期（2018年度〜2022年度）から後期（2023年度〜2027年度）へ移行し、現行は後期基本計画。後期基本計画の施策体系は7グループ・全35施策で構成し全件を列挙する。実施計画は3か年度ローリングで、最終版は計画終期に合わせた2026年度〜2027年度の2か年度版。進行管理は行政評価によるPDCA（成果指標と市民の体感指標を組み合わせた16段階の施策評価と事業評価）という自治体の自己評価の枠組みである。第8次総合計画への移行は移行記録としてのみ保持し、次期計画の内容を現行計画期間の実績へ遡及接続しない）
- FY2026一般会計当初予算 146,740,000千円（成立。市長提出議案第3号『令和8年度愛知県一宮市一般会計予算』として令和8年3月定例会に提出され、4委員会への付託を経て、令和8年3月23日の本会議で可決。市の公表する議決結果の文言は「可決」であり、『原案可決』の文言は未確認のまま保持する。公表精度が千円単位のため千円精度のまま記録し、円単位を合成していない）
- FY2024一般会計歳入総額 150,057,354,584円
- FY2024一般会計歳出総額 143,608,246,738円
- FY2024決算の認定議案である認定第4号は令和7年12月定例会で令和7年12月1日に認定された（市議会公式『議案・議決結果一覧（令和7年12月定例会）』で確認）。実質収支額は決算書の実質収支に関する調書により6,207,237千円（千円単位・端数整理）。FY2024は後期基本計画期間の決算であり計画versionは同一だが、決算総額と施策・指標との総額レベルの対応付けは公式資料にないため、決算総額と後期基本計画の施策・指標との接続は行っていない

35施策に基づく実施計画事業の全件、施策別の成果指標・市民の体感指標の個別値、予算書・決算書の事項別明細書の款別合計との最終突合、令和8年3月定例会の最終日の会議録による採決の直接確認、監査委員の決算審査意見書の内容確認、第8次計画の枠組み、FY2024決算と後期基本計画の接続（not_assessableとして保持）、補正・執行・契約・補助金はdeferred depthです。

### Milestone P15-M33 — Toyota reviewed package

Status: `complete`（2026-11-16）

豊田市をPhase 15の33番目の`reviewed_complete`自治体として確定しました（所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

v1 declared package:

- 第9次豊田市総合計画（ミライ構想とミライ実現戦略2030の2層で構成する。ミライ構想は長期（2050年）を展望して設定する普遍的なまちづくりの方向性で、将来像は『つながる つくる 暮らし楽しむまち・とよた』、まちづくりの基本的な考え方（3つの発想の転換と3つの行動の変容）と将来都市構造（拠点連携型都市）を示す。ミライ実現戦略2030は2025年度〜2029年度の5年間で特に注力する取組の方向性で、2つの取組方針（ともにこどものミライに夢と希望をつくる／ともにミライにつながるまちをつくる）のもと、5つの取組目標・12の目指す姿・全30施策で構成し全件を列挙する。進行管理は毎年度ローリング（目指す姿を起点とした施策評価と事業の見直し・新規立案を予算編成へ反映）という自治体の進行管理の枠組みであり、ローリング結果は当初予算の編成と合わせて公表し、当該年度の主な取組は施策別事業集として毎年度公表する。第8次豊田市総合計画からの移行は移行記録としてのみ保持し、第9次計画の内容を前計画期間の実績へ遡及接続しない）
- FY2026一般会計当初予算 211,800,000千円（成立。議案第45号『令和8年度豊田市一般会計予算』として令和8年2月20日に豊田市長太田稔彦から提出され、予算決算委員会への付託を経て、令和8年3月18日の本会議で原案可決。議決結果は市議会公式『議決結果一覧（令和8年3月定例会）』で確認し、同表の議案第45号の欄は議決結果・議決年月日とも「〃」表記であり、同表冒頭の明示行（議案第5号）の原案可決・令和8年3月18日と同値である旨を明記する。公表精度が千円単位のため千円精度のまま記録し、円単位を合成していない）
- FY2024一般会計歳入総額 246,602,084,906円
- FY2024一般会計歳出総額 229,543,452,176円
- FY2024決算の認定議案である令和7年承認第4号（豊田市は「承認第X号」表記）は令和7年9月定例会で令和7年9月24日に認定された（市議会公式『議決結果一覧（令和7年9月定例会）』で確認）。実質収支額は監査委員の決算等審査意見書の決算収支状況により8,192,990千円（千円単位）。実質収支に関する調書そのものの直接確認は未実施のまま保持する。FY2024は第8次総合計画の計画期間の決算であり計画versionが異なるため、決算総額とミライ実現戦略2030の取組目標・施策との接続は行っていない

30施策に基づく施策別事業集の事業の全件、目指す姿ごとの指標の個別値、予算書・決算書の事項別明細書の款別合計との最終突合、令和8年3月定例会の会議録による採決の直接確認、実質収支に関する調書そのものの直接確認、第8次計画の枠組み、FY2024決算と第9次計画の接続（not_assessableとして保持）、補正・執行・契約・補助金はdeferred depthです。

### Milestone P15-M34 — Tsu reviewed package

Status: `complete`（2026-11-16）

津市をPhase 15の34番目の`reviewed_complete`自治体として確定しました（所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

v1 declared package:

- 津市総合計画（基本構想と第2次基本計画の2層で構成する。基本構想はまちづくりの基本的な理念として、めざすべき都市像（望ましいまちの姿『市民がそれぞれの幸せを実感し、心豊かで笑顔あふれる人生を送ることができるまち』、将来像は『笑顔があふれ幸せに暮らせる県都 津市 ～夢や希望、明るい未来が広がるまちへ～』）や市民の暮らし・生き方、土地利用の考え方を示し、計画期間は特に定めていない。固定期間がない点はそのまま保持し、一律の固定期間modelへ潰さない。第2次基本計画は基本構想に掲げる都市像や市民の暮らしなどの実現に向けた施策や取組の方向性を示し、計画期間は2018年度〜2027年度の10年間で、基本構想のまちづくりの大綱に対応する6つの目標と目標を横断する『将来像の実現に向けて』のもと、基本政策19件・全53施策で構成し全件を列挙する。進行管理は事務事業評価・施策評価（実施結果を『津市総合計画第2次基本計画事務事業評価・施策評価報告書』として年度ごとに公表）という自治体の進行管理の枠組みである。先行計画（基本構想・前期基本計画／後期基本計画）からの移行と、策定中の次期津市総合計画は移行記録としてのみ保持し、現行計画の内容を先行計画期間の実績へ遡及接続しない）
- FY2026一般会計当初予算 124,187,000千円（成立。議案第39号『令和8年度津市一般会計予算』として令和8年2月27日に津市長前葉泰幸から提出され、所管別に各常任委員会への付託を経て、令和8年3月26日の本会議で原案可決。議決結果は市議会公式『議決結果一覧表（令和8年第1回津市議会定例会）』で確認し、本会議録でも賛成議員多数により原案のとおり可決することに決定した旨を直接確認した。公表精度が千円単位のため千円精度のまま記録し、円単位を合成していない）
- FY2024一般会計歳入総額 123,307,646,176円
- FY2024一般会計歳出総額 122,840,878,576円
- FY2024決算の認定議案である認定第1号『令和6年度津市一般会計歳入歳出決算』は令和7年第3回定例会で令和7年9月25日に認定された（市議会公式『議決結果一覧表（令和7年第3回津市議会定例会）』で確認）。実質収支額は決算附属書『実質収支に関する調書』により175,738,909円（円単位。同調書は円単位で公表されているため円単位のまま記録する）。FY2024は第2次基本計画の計画期間内の決算であり計画versionは同一だが、決算総額と第2次基本計画の目標・基本政策・施策との総額レベルの対応付けは公式資料にないため接続は行っていない

53施策に基づく事務事業評価の対象事業の全件、施策ごとの指標の個別値、予算書・決算書の事項別明細書の款別合計との最終突合、監査委員の決算審査意見書の内容確認、先行計画および次期計画の枠組み、FY2024決算と第2次基本計画の接続（not_assessableとして保持）、補正・執行・契約・補助金はdeferred depthです。

### Milestone P15-M35 — Otsu reviewed package

Status: `complete`（2026-11-16）

大津市をPhase 15の35番目の`reviewed_complete`自治体として確定しました（所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

v1 declared package:

- 大津市総合計画（基本構想と実行計画の2層で構成する。基本構想は市の最上位計画として将来都市像（『ひと、自然、歴史の縁で織りなす 住み続けたいまち“大津再生” ～コンパクトで持続可能なまちへの変革～』）と、その実現のための方針や政策等を定めた長期的な構想で、計画期間は2017年度〜2028年度の12年間、まちづくりの基本理念は『持続可能な都市経営』『共助社会の確立』『自然、歴史、文化の保全、再生、活用』の3件。実行計画は基本構想の計画期間を4年ごとに3期に分割し、各期間で取り組む具体的な施策等を示すもので、現行は第3期実行計画（2025年度〜2028年度）で、3つの基本方針のもと基本政策13件・全32施策で構成し全件を列挙する。進行管理は行政評価（総合計画進捗管理・事務事業評価。結果は行政評価報告書として年度ごとに公表）という自治体の進行管理の枠組みである。実行計画は第1期（2017年度〜2020年度）・第2期（2021年度〜2024年度）を経て第3期へ移行したもので、移行は移行記録としてのみ保持し、現行計画の内容を先行する実行計画期間の実績へ遡及接続しない。基本構想の計画期間（2028年度）後の次期総合計画の策定状況は未確認のまま保持する）
- FY2026一般会計当初予算 142,684,000千円（成立。議案第3号『令和8年度大津市一般会計予算』として令和8年2月19日に大津市長佐藤健司から提出され、予算決算常任委員会への付託を経て、令和8年3月25日に可決。議決結果は市議会公式『議案の一覧・結果（令和7年度）』で確認した。同ページの公表文言は『可決（多数）』のみで『原案可決』とは表記していないため、その文言は断定せず未確認のまま保持する。公表精度が千円単位のため千円精度のまま記録し、円単位を合成していない）
- FY2024一般会計歳入総額 146,909,564,029円
- FY2024一般会計歳出総額 143,932,903,895円
- FY2024決算の認定議案である議案第110号『令和6年度大津市一般会計の決算の認定について』は令和7年8月通常会議で令和7年10月28日に認定された（市議会公式『議案の一覧・結果（令和7年度）』で確認）。実質収支額は監査委員の決算審査意見書の千円単位の集計により2,791,920千円（千円精度。同審査意見書は千円単位で公表されているため千円精度のまま記録し、実質収支に関する調書そのものの円単位の値は未確認のまま保持する）。FY2024は第2期実行計画の最終年度の決算であり現行の第3期実行計画とは計画versionが異なる上、決算総額と第3期実行計画の基本方針・基本政策・施策との総額レベルの対応付けは公式資料にないため接続は行っていない

32施策に基づく事務事業評価の対象事業の全件、施策ごとの成果指標の個別値、予算書・決算書の事項別明細書の款別合計との最終突合、実質収支に関する調書そのものの円単位の値の直接確認、本会議録本文による『原案可決』の文言の直接確認、第1期・第2期実行計画の枠組み、次期総合計画、FY2024決算と第3期実行計画の接続（not_assessableとして保持）、補正・執行・契約・補助金はdeferred depthです。

### Milestone P15-M36 — Toyonaka reviewed package

Status: `complete`（2026-11-16）

豊中市をPhase 15の36番目の`reviewed_complete`自治体として確定しました（所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

v1 declared package:

- 第4次豊中市総合計画（豊中市自治基本条例に基づき策定された市の最上位計画で、基本構想・基本計画・実施計画の3層で構成する。基本構想はまちの将来像『みらい創造都市 とよなか ～明日がもっと楽しみなまち～』とその実現のための施策大綱を示し、計画期間は2018年度〜2027年度の10年間。基本計画は前期基本計画（2018年度〜2022年度・17施策とリーディングプロジェクト）と後期基本計画（2023年度〜2027年度）に分かれ、現行は後期基本計画で、基本構想の施策大綱に沿った5つの章のもと全16施策で構成し全件を列挙する。リーディングプロジェクト（南部地域活性化プロジェクト）は施策体系とは別枠として保持する。実施計画は基本計画で示した施策を実現するための事業を明らかにするもので、令和6年度以降はデジタル予算書で提供される。進行管理は政策評価（後期基本計画の16施策とリーディングプロジェクトを進捗度・取組み内容の2軸で毎年度評価し、結果はデジタル予算書と政策評価結果概要で公表）という自治体の進行管理の枠組みである。前期基本計画から後期基本計画への移行は移行記録としてのみ保持し、現行計画の内容を前期基本計画期間の実績へ遡及接続しない。基本構想の計画期間（2027年度）後の次期総合計画の策定状況は未確認のまま保持する）
- FY2026一般会計当初予算 206,946,719千円（成立。市議案第8号『令和8年度豊中市一般会計予算』として令和8年2月24日に豊中市長長内繁樹から提出され、令和8年3月定例会で令和8年3月23日に原案可決。議決結果は豊中市議会公式『議決結果（令和8年（2026年）3月定例会）』で確認した。公表精度が千円単位のため千円精度のまま記録し、円単位を合成していない）
- FY2024一般会計歳入総額 197,263,021,788円
- FY2024一般会計歳出総額 191,790,466,590円
- FY2024決算の認定議案である市議案第74号『令和6年度大阪府豊中市各経済歳入歳出決算認定について』は令和7年9月定例会（令和7年9月8日提出）に決算認定4件の1件として提出され、継続審査を経て、令和7年12月定例会で令和7年11月28日に不認定となった（豊中市議会公式『議決結果（令和7年（2025年）12月定例会）』で確認。不認定の事実をそのまま記録し、認定の事実は記録しない）。実質収支額は『令和6年度豊中市各経済実質収支に関する調書』（一般会計）により4,930,077千円（千円精度。同調書は千円単位で端数調整して公表されているため千円精度のまま記録する）。不認定に係る市長の措置（地方自治法第233条第7項に基づく措置と議会への通知）の内容は未確認のまま保持する。FY2024は後期基本計画の期間内の決算であり計画versionは同一であるが、決算総額と後期基本計画の16施策・リーディングプロジェクトとの総額レベルの対応付けは公式資料にないため接続は行っていない

16施策に基づく事務事業の全件、施策ごとの成果指標の個別値、リーディングプロジェクトの事業内訳、予算説明書・決算書の事項別明細書の款別合計との最終突合、不認定に係る市長の措置の内容確認、前期基本計画の枠組み、次期総合計画、FY2024決算と後期基本計画の接続（not_assessableとして保持）、補正・執行・契約・補助金はdeferred depthです。

### Milestone P15-M37 — Suita reviewed package

Status: `complete`（2026-11-16）

吹田市をPhase 15の37番目の`reviewed_complete`自治体として確定しました（所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

v1 declared package:

- 第4次吹田市総合計画（基本構想・基本計画・実施計画の3層で構成する。基本構想は本市がめざす将来像とそれを実現するための基本方向を施策の大綱として示すもので、将来像の定型タイトルは存在せず基本構想の結語『だれもが安心してすこやかで快適に暮らし続けられるまち』として保持する。基本構想・基本計画の計画期間はいずれも2019年度〜2028年度の10年間。基本計画は令和6年3月に中間見直しとして基本計画改訂版（2024年度〜2028年度、あわせて第2期まち・ひと・しごと創生総合戦略を一体的に策定）が策定され、現行は改訂版で、8大綱のもと全19政策・全52施策で構成し全件を列挙する。体系図に併記される取組の視点は施策体系とは別枠として保持する。実施計画は5年間としローリング方式により毎年度見直しを行い、現行の実施計画（2026年度〜2030年度）は総合計画の終期（2028年度）を越える期間を示すが、この期間差は構造として保持する。進行管理はPDCAサイクル（行政評価）という自治体の進行管理の枠組みである。当初基本計画から基本計画改訂版への移行は移行記録としてのみ保持し、現行計画の内容を改訂前の基本計画期間の実績へ遡及接続しない。第4次総合計画の計画期間（2028年度）後の次期（第5次）総合計画の策定状況は未確認のまま保持する）
- FY2026一般会計当初予算 181,996,567千円（成立。議案第19号『令和8年度吹田市一般会計予算』として令和8年2月18日に吹田市長後藤圭二から提出され、令和8年2月定例会で原案可決。議決結果は吹田市議会公式『令和8年(2026年)2月定例会議決結果・賛否一覧表』で確認した（賛否23対9）。議決日（令和8年3月24日）は定例会日程から特定したもので、会議録による最終確認は未実施。公表精度が千円単位のため千円精度のまま記録し、円単位を合成していない）
- FY2024一般会計歳入総額 179,335,489,298円
- FY2024一般会計歳出総額 178,490,836,452円
- FY2024決算の認定議案である認定第1号『令和6年度吹田市一般会計歳入歳出決算認定について』は令和7年9月定例会（令和7年9月16日提出）に提出され、決算常任委員会に付託され継続審査を経て、令和7年11月定例会で認定された（吹田市議会公式の議決結果・賛否一覧表で確認。賛否24対9。認定の議決日（令和7年12月22日）は定例会日程から特定したもので、会議録による最終確認は未実施）。実質収支額は公式報告書により259,882千円（千円精度。形式収支844,653千円から繰越明許費繰越財源584,771千円を控除した額で、同報告書が千円単位で公表しているため千円精度のまま記録する。なお同報告書によれば、実質収支の黒字化を図るため財政調整基金から1,900,000千円を繰り入れている）。FY2024は基本計画改訂版の初年度の決算であり計画versionは同一であるが、決算総額と基本計画改訂版の19政策・52施策との総額レベルの対応付けは公式資料にないため接続は行っていない

52施策に基づく事務事業の全件、施策ごとの施策指標の個別値・市民意識指標の個別値、会議録による両議決日の最終確認、予算書・決算書の事項別明細書の款別合計との最終突合、監査委員の決算審査意見書の内容確認、当初基本計画の枠組み、次期総合計画、FY2024決算と基本計画改訂版の接続（not_assessableとして保持）、補正・執行・契約・補助金はdeferred depthです。

### Milestone P15-M38 — Takatsuki reviewed package

Status: `complete`（2026-11-16）

高槻市をPhase 15の38番目の`reviewed_complete`自治体として確定しました（所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

v1 declared package:

- 第6次高槻市総合計画（基本構想・基本計画の2層で構成する。基本構想はまちづくりの目標となる将来の都市像（8つ）を示し、始期は令和3（2021）年度、目標年次は令和12（2030）年度で、まちづくりの合言葉は『輝く未来を創造する 関西の中央都市 高槻』。基本計画は8つの将来の都市像に対応する8分野のもと全29施策・全139施策の方向で構成し全件を列挙する。計画期間中の行財政運営に当たっては、別途策定する実施計画（計画期間3年間・毎年度策定、現行は令和8年度～令和10年度版）により、基本計画で示された方向性に沿った取組の推進を図る。進行管理は実施計画を軸とし、各主要事業について実績の振り返り（評価）を行った上で次年度以降の計画を行う自治体の進行管理の枠組みである。第5次高槻市総合計画（高槻市総合戦略プラン、2010年度策定～2020年度）から第6次高槻市総合計画への移行は移行記録としてのみ保持し、現行計画の内容を前計画期間の実績へ遡及接続しない。第6次総合計画の計画期間（2030年度）後の次期総合計画の策定状況は未確認のまま保持する）
- FY2026一般会計当初予算 151,189,961千円（成立。議案第32号『令和8年度高槻市一般会計予算』として令和8年2月25日に高槻市長濱田剛史から提出され、令和8年第1回定例会（3月定例会）で原案可決。議決結果は高槻市議会公式『令和8年第1回定例会（3月定例会）の議決結果』（付議事件と議決てんまつ）で文言・議決日とも直接確認した。公表精度が千円単位のため千円精度のまま記録し、円単位を合成していない）
- FY2024一般会計歳入総額 147,928,131,915円
- FY2024一般会計歳出総額 142,805,684,915円
- FY2024決算の認定議案である認定第1号『令和6年度高槻市一般会計歳入歳出決算認定について』は令和7年第4回定例会（9月定例会）に提出され令和7年9月8日に継続審査とされた後、令和7年第5回定例会（12月定例会）で認定された（高槻市議会公式の各定例会の議決結果で確認）。実質収支額は決算附属書類の実質収支に関する調書により3,523,157千円（千円精度。差引額5,122,447千円から繰越明許費繰越額1,599,290千円を控除した額で、同調書が千円単位で公表しているため千円精度のまま記録する。なお同調書によれば、実質収支額のうち地方自治法第233条の2の規定による基金繰入額は0千円である）。FY2024は第6次高槻市総合計画の計画期間内の決算であり計画versionは同一であるが、決算総額と8分野・29施策との総額レベルの対応付けは公式資料にないため接続は行っていない

29施策・139施策の方向に基づく主要事業の全件、施策ごとの指標の個別値、予算書・決算書の事項別明細書の款別合計との最終突合、監査委員の決算審査意見書の内容確認、第5次計画の枠組み、次期総合計画、FY2024決算と第6次総合計画の接続（not_assessableとして保持）、補正・執行・契約・補助金はdeferred depthです。

### Milestone P15-M39 — Hirakata reviewed package

Status: `complete`（2026-11-16）

枚方市をPhase 15の39番目の`reviewed_complete`自治体として確定しました（所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

v1 declared package:

- 第5次枚方市総合計画（基本構想・基本計画・実行計画の3層で構成する。基本構想は平成28（2016）年度を計画始期として計画期間を設定せず、めざすまちの姿『持続的に発展し、一人ひとりが輝くまち 枚方』と5つの基本目標を定める。基本計画は平成28（2016）年度から令和9（2027）年度までの12年間において重点的に進める施策を示す。実行計画は4年間を1期とし、現行は第3期（2024年度～2027年度）。基本計画・第3期実行計画の施策体系は、5つの基本目標のもと、28の施策目標と4つの計画推進（施策目標等全32件）のもとに全79施策を位置づけ、全件を列挙する。進行管理は実行計画を軸とし、具体的な取り組みの実績や指標、主観的指標で把握する市民満足度を活用して毎年度検証・評価（内部評価と施策評価員による外部評価）を行い、第3期実行計画は予算編成の時期に合わせて改訂し、基本計画は4年ごとにPDCAサイクルによる検証・評価を行う自治体の進行管理の枠組みである。第5次総合計画から次期総合計画（令和10（2028）年度始期・策定中、基本構想は第5次を基本とし基本計画を改定する方針）への移行は移行記録としてのみ保持し、現行計画の内容を次期計画期間の実績へ前倒し接続しない）
- FY2026一般会計当初予算 176,300,000千円（成立。議案第84号『令和8年度大阪府枚方市一般会計予算』として令和8年3月定例月議会の第1日（令和8年2月24日）に予算特別委員会へ設置・付託され、第5日（令和8年3月27日）に原案可決。議決結果は枚方市議会公式『付議事件議決結果一覧』で文言・議決日とも直接確認した。公表精度が千円単位のため千円精度のまま記録し、円単位を合成していない）
- FY2024一般会計歳入総額 167,040,111,596円
- FY2024一般会計歳出総額 164,593,615,013円
- FY2024決算の認定議案である認定第1号『令和6年度大阪府枚方市一般会計歳入歳出決算の認定について』は令和7年9月定例月議会の第1日（令和7年9月5日）に決算特別委員会へ設置・付託され、第7日（令和7年10月17日）に認定された（枚方市議会公式『付議事件議決結果一覧』で確認）。実質収支額は公式『令和6年度決算概要説明書』の会計別収支表により1,938,746,472円（円精度。差引額2,446,496,583円から翌年度へ繰越すべき財源507,750,111円を控除した額で、同表が円単位で公表しているため円単位のまま記録する。決算書本体の実質収支に関する調書のページはフォント未埋め込みのため判読できず、調書そのものの直接確認は未実施）。FY2024は基本計画の計画期間内であり第3期実行計画の初年度の決算で計画versionは同一であるが、決算総額と28の施策目標・79施策との総額レベルの対応付けは公式資料にないため接続は行っていない

32の施策目標等・79施策に基づく具体的な取組の全件、施策ごとの指標の個別値（主観的指標・客観的指標）、予算・決算の事項別明細書の款別合計との最終突合、監査委員の決算審査意見書の内容確認、実質収支に関する調書そのものの直接確認、次期総合計画の枠組み、FY2024決算と第5次総合計画の接続（not_assessableとして保持）、補正・執行・契約・補助金はdeferred depthです。

### Milestone P15-M40 — Yao reviewed package

Status: `complete`（2026-11-16）

八尾市をPhase 15の40番目の`reviewed_complete`自治体として確定しました（所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

v1 declared package:

- 第6次八尾市総合計画『八尾新時代しあわせ成長プラン』（八尾市総合計画策定条例に基づき基本構想・基本計画・実施計画の3層で構成し、基本構想と基本計画は市議会の議決を経て策定する。基本構想は2021年度から2028年度までの8年間について、将来都市像『つながり、かがやき、しあわせつづく、成長都市 八尾』と6つのまちづくりの目標・取り組み方向（政策）・まちづくりの推進方策を示す。基本計画は前期（2021年度～2024年度）・後期（2025年度～2028年度）の各4年間であり、現行は後期基本計画である。実施計画は毎年度見直しを行う。後期基本計画の施策体系はマトリクス型であり、6つのまちづくりの目標のもと33施策を位置づけ、各施策と関連する目標の対応は全83対応であり、全件を列挙する。前期基本計画の施策16『上水道の安定供給』は、水道事業が2025年4月に大阪広域水道企業団へ統合されたため後期基本計画の施策体系から削除され欠番である。進行管理は市民参画と協働のまちづくり基本条例第13条に基づく行政評価（施策評価＝実施計画書・実施計画実績書、事務事業評価＝妥当性・有効性・効率性の観点）による自治体の進行管理の枠組みである。第6次総合計画の基本計画の前期から後期への移行は版の履歴としてのみ保持し、前期基本計画期間の実績を後期基本計画の期間へ前倒し接続しない）
- FY2026一般会計当初予算 132,613,637千円（成立。議案第18号『令和8年度八尾市一般会計予算の件』として2026年2月市議会定例会に提出され、2026年3月27日に原案可決。議決結果は八尾市議会公式『2026年2月市議会定例会 議決結果』で文言・議決日とも直接確認した。公表精度が千円単位のため千円精度のまま記録し、円単位を合成していない）
- FY2024一般会計歳入総額 126,116,660,528円
- FY2024一般会計歳出総額 123,882,040,366円
- FY2024決算の認定議案である認定第1号は令和7年9月市議会定例会に提出され、2025年10月22日に認定された（八尾市議会公式『令和7年9月市議会定例会 議決結果』で確認。議会だより等の広報資料に掲載される討論件数の集計は議決結果そのものではなく、一般会計決算の認定の確認には用いていない）。実質収支額は公式決算書の実質収支に関する調書により1,797,799,491円（円精度。差引額2,234,620,162円から翌年度へ繰り越すべき財源436,820,671円を控除した額で、調書そのもので円単位で直接確認した）。FY2024は前期基本計画（2021年度～2024年度）期間の決算であり現行の後期基本計画とは計画の版が異なり、決算総額と施策体系との総額レベルの対応付けは公式資料にないため接続は行っていない

33施策に基づく具体的な取組の全件、施策ごとの指標の個別値、予算・決算の事項別明細書の款別合計との最終突合、監査委員の決算審査意見書の内容確認、前期基本計画の施策体系の全件、FY2024決算と第6次総合計画の接続（not_assessableとして保持）、補正・執行・契約・補助金はdeferred depthです。

### Milestone P15-M41 — Neyagawa reviewed package

Status: `complete`（2026-11-16）

寝屋川市をPhase 15の41番目の`reviewed_complete`自治体として確定しました（所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

v1 declared package:

- 第六次寝屋川市総合計画（第2期寝屋川市まち・ひと・しごと創生総合戦略と統合して策定され、基本戦略（市の目指す将来像や基本姿勢を定める基本構想と、将来像の実現のために推進する施策の展開などを総合的かつ体系的に示す戦略プラン）と、基本戦略に基づいて実施する具体的な取組（事務事業）を示す実施計画で構成する。基本戦略は2021年度から2027年度までの7年間について、将来像『新たな価値を創り、選ばれるまち 寝屋川 ～イノベーションの創出～』を示す。実施計画は前期（2021年度～2023年度・3年間）・後期（2024年度～2027年度・4年間）であり、現行は後期実施計画（令和8年度版）である。戦略プランは19施策で構成し、施策1～9は『3つの最重要ファクター』に位置付けられる訴求力のある施策、施策10～13は生活を支える施策、施策14～19はくらしの質を高める施策であり、全件を列挙する。後期実施計画では施策ごとに施策の展開（全74件）・取組（事務事業）・リーディング事業（総合戦略事業）・進捗管理指標を置く。進行管理は、計画の進捗管理とPDCIサイクル（Plan・Do・Check・Innovation）の考え方に基づく行政評価を一体的に行う自治体の進行管理の枠組みである。実施計画の前期から後期への移行は版の履歴としてのみ保持し、前期実施計画期間の実績を後期実施計画の期間へ前倒し接続しない。次期（第七次）総合計画の策定状況は未確認である）
- FY2026一般会計当初予算 1,097億3,000万円＝109,730,000千円（成立。議案第28号『令和8年度寝屋川市一般会計予算』として令和8年3月市議会定例会に提出（2026年2月24日）され、予算決算常任委員会の審査を経て2026年3月25日に原案可決。議決結果は寝屋川市議会公式『令和8年3月市議会定例会 付議事件一覧表』で議案番号・文言・議決日とも直接確認した。市の公表は万円単位のため、その精度（万円単位）のまま記録し、千円未満の端数を合成していない。千円単位の精密額の当初予算書での確認は未実施である）
- FY2024一般会計歳入総額 106,597,604千円（千円精度）
- FY2024一般会計歳出総額 105,333,971千円（千円精度）
- FY2024決算の認定議案である認定第1号は令和7年9月定例会に提出（2025年9月2日）され、予算決算常任委員会への付託と閉会中の継続審査を経て、令和7年12月定例会で2025年12月3日に認定された（寝屋川市議会公式『令和7年9月市議会定例会 付議事件一覧表』『令和7年12月市議会定例会 付議事件一覧表』で確認）。実質収支額は公式決算書の実質収支に関する調書により1,248,678千円（千円精度。差引額1,263,633千円から翌年度へ繰り越すべき財源14,955千円を控除した額で、調書そのもので確認した。歳入・歳出総額は令和7年9月参考資料『令和6年度 寝屋川市会計別決算状況』の一般会計行とも完全一致する）。FY2024は後期実施計画（2024年度～2027年度）の初年度の決算であり計画の版は現行と同一であるが、決算総額と19施策・施策の展開との総額レベルの対応付けは公式資料にないため接続は行っていない

19施策に基づく施策の展開・取組の全件、施策指標・進捗管理指標の個別値、予算・決算の事項別明細書の款別合計との最終突合、監査委員の決算審査意見書の内容確認、FY2026当初予算の千円単位の精密額の確認、第七次総合計画の策定状況、FY2024決算と第六次総合計画の接続（not_assessableとして保持）、補正・執行・契約・補助金はdeferred depthです。

### Milestone P15-M42 — Higashiosaka reviewed package

Status: `complete`（2026-11-16）

東大阪市をPhase 15の42番目の`reviewed_complete`自治体として確定しました（所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

v1 declared package:

- 東大阪市第3次総合計画（2021年度～2030年度、令和12年を目標年次、将来都市像『つくる・つながる・ひびきあう ― 感動創造都市 東大阪 ―』。そのもとに具体的な事業計画となる実施計画を策定し、第1次実施計画（2021年度～2023年度）と第2次実施計画（2024年度～2027年度）からなり、各実施計画は年度ごとに版（Ver.）が策定され、現行は第2次実施計画Ver.3.0である。施策体系は7分野（人権・共生・協働／子ども・子育て／教育／スポーツ・文化・産業／健康・福祉／都市・環境／防災・治安）で構成し、3つの重点施策（若者・子育て世代に選ばれるまちづくり／高齢者が活躍するまちづくり／人が集まり、活気あふれるまちづくり）を置く。各分野の個別施策の全件列挙は概要版の体系図の縦書きレイアウトのため転記の正確性を担保できず行わない。進行管理は、各年度終了後にPDCAサイクルにより実施計画対象事業の評価を行い、事業評価報告書と評価指標達成状況を公表する自治体の進行管理の枠組みである。実施計画の第1次から第2次への移行と各Ver.の履歴は版の履歴としてのみ保持し、第1次実施計画期間の実績を第2次実施計画の期間へ前倒し接続しない。次期（第4次）総合計画の策定状況は未確認である）
- FY2026一般会計当初予算 241,023,138千円（成立。議案第36号『令和8年度東大阪市一般会計予算』として令和8年2月第1回定例会で2026年3月26日に修正可決（起立多数）。議決結果は市議会公式サイトの議案一覧表で議案番号・文言・議決日とも直接確認した。金額は令和8年度一般会計補正予算（第1回）予算書の『補正前の額』（議決後の成立額）であり、市の財政状況の公表の一般会計予算額241,023百万円とも整合する。公表精度は千円単位のため、その精度（千円単位）のまま記録し、円単位を合成していない。修正可決における修正の具体的内容・修正箇所は未確認である）
- FY2024一般会計歳入総額 233,897,034千円（千円精度）
- FY2024一般会計歳出総額 229,860,314千円（千円精度）
- FY2024決算の認定議案である認定第1号は令和7年9月第3回定例会で2025年9月12日に継続審査（異議なし）とされ、令和7年12月第4回定例会で2025年12月1日に認定された（起立多数。市議会公式サイトの議案一覧表で確認）。実質収支額は監査委員の決算審査意見書（東大阪監第846号）により3,767,144千円（千円精度。歳入・歳出の差引額4,036,720千円が同資料の形式収支と検算一致する）。FY2024は第2次実施計画（2024年度～2027年度）の初年度の決算であり計画の版は現行と同一であるが、決算総額と7分野・3つの重点施策との総額レベルの対応付けは公式資料にないため接続は行っていない

7分野の分野別施策の全件、評価指標の個別値、予算修正の具体的内容、予算・決算の事項別明細書の款別合計との最終突合、監査委員の決算審査意見書の内容（個別の指摘事項等）の精査、次期（第4次）総合計画の策定状況、FY2024決算と第3次総合計画の接続（not_assessableとして保持）、補正・執行・契約・補助金はdeferred depthです。

### Milestone P15-M43 — Himeji reviewed package

Status: `complete`（2026-11-16）

姫路市をPhase 15の43番目の`reviewed_complete`自治体として確定しました（所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

v1 declared package:

- 姫路市総合計画「ふるさと・ひめじプラン2030」（基本構想（2021年度～2030年度の10年間、目指す都市像『ともに生き ともに輝く にぎわい交流拠点都市 姫路』）と実施計画（計画期間3年間・毎年度掲載事業を更新するローリング方式、現行は令和8年度～令和10年度）の2層で構成し、基本構想の10年間と実施計画の3年ローリングを別period semanticsとして保持する。分野体系は9分野（市民活動／健康福祉／教育／環境／産業／観光・スポーツ／都市基盤／防災・安全安心／行財政運営）で構成し、各分野に分野目標と政策を置く。各分野の政策の全件列挙は基本構想冊子の体系一覧が2カラム構成でありテキスト抽出では政策の分野別の帰属が混在して誤りなく転記できないため行わない。進行管理は、3年ごとに実施する政策評価（市民意識調査項目とKPIによる評価）を軸としたPDCAサイクルと、毎年度の事業形成過程における単年度のPDCAサイクルを組み合わせる自治体の進行管理の枠組みである。前総合計画「ふるさと・ひめじプラン2020」（2009年度～2020年度）からの移行は版の履歴としてのみ保持し、前計画期間の実績を現行計画の期間へ前倒し接続しない。次期総合計画の策定状況は未確認である）
- FY2026一般会計当初予算 261,800,000千円（成立。議案第1号『令和8年度姫路市一般会計予算』として令和8年第1回定例会で可決された。市公式『議案及び審議結果』の結果欄の文言は「可決」であり、その文言のまま記録する。議決日2026年3月25日は、会期（2026年2月17日～3月25日。議会報ひめじNo.252）と最終日の表決から特定したものであり、会議録による最終確認は未実施である。金額は市公式『令和8年度 予算の概要』ページと一般会計予算総括表（歳出）で確認した。公表精度は千円単位のため、その精度（千円単位）のまま記録し、円単位を合成していない）
- FY2024一般会計歳入総額 254,438,371千円（千円精度）
- FY2024一般会計歳出総額 245,476,363千円（千円精度）
- FY2024決算の認定議案である議案第90号『令和6年度姫路市一般会計決算認定について』は令和7年第3回定例会で認定された（市公式の議案及び審議結果で確認。認定の議決日2025年10月3日は議員別賛否一覧PDFの発行日付と会期最終日の表決から特定したものであり、会議録による最終確認は未実施である）。実質収支額は市公式『令和6年度決算の概要』により5,797,686千円（千円精度。歳入・歳出の差引額8,962,008千円が同資料の形式収支と検算一致し、翌年度への繰越財源3,164,322千円を差し引いた額）。FY2024は基本構想（2021年度～2030年度）期間内の決算であり計画の版は現行と同一であるが、決算総額と9分野・政策との総額レベルの対応付けは公式資料にないため接続は行っていない

9分野の分野別政策の全件、政策評価の指標（市民意識調査項目・KPI）の個別値、両議決日の会議録による最終確認、予算・決算の事項別明細書の款別合計との最終突合、監査委員の決算審査意見書の内容（個別の指摘事項等）の精査、次期総合計画の策定状況、FY2024決算と「ふるさと・ひめじプラン2030」の接続（not_assessableとして保持）、補正・執行・契約・補助金はdeferred depthです。

### Milestone P15-M44 — Amagasaki reviewed package

Status: `complete`（2026-11-16）

尼崎市をPhase 15の44番目の`reviewed_complete`自治体として確定しました（所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

v1 declared package:

- 第6次尼崎市総合計画（まちづくり構想（2023年度～2032年度の10年間、ありたいまち『ひと咲き まち咲き あまがさき』）とまちづくり基本計画（構想の10年間を前期・後期の5年ごとに分割し、現行は前期2023年度～2027年度）の2層で構成し、構想の期間と基本計画の期間を別period semanticsとして保持する。施策体系は13施策（地域コミュニティ・学び／人権尊重・多文化共生／学校教育／子ども・子育て支援／地域福祉／障害者支援／高齢者支援／健康支援／生活安全／消防・防災／地域経済・雇用就労／環境保全・創造／都市機能・住環境）で構成し、各施策に施策の展開方向（全41件）を置く。各施策の展開方向の全件列挙は計画本編各論が2カラム構成でありテキスト抽出では展開方向の文言の帰属が混在して誤りなく転記できないため行わない。進行管理は、施策評価を起点とした単年度PDCAサイクルと、基本計画期間（5年間）ごとの点検を行う計画期間PDCAを組み合わせる自治体の進行管理の枠組みである。前総合計画（第5次尼崎市総合計画、2013年度～2022年度）からの移行は版の履歴としてのみ保持し、前計画期間の実績を現行計画の期間へ前倒し接続しない。後期まちづくり基本計画（2028年度～2032年度）は策定中であり、現行計画として扱わない）
- FY2026一般会計当初予算 247,210,000千円（成立。議案第1号『令和8年度尼崎市一般会計予算』として第4回定例会で原案可決された。市議会公式『議案等採決結果』の結果欄の文言は「原案可決」であり、その文言のまま記録する。議決日2026年3月19日は、同定例会の第5日（最終日）の議事日程から特定したものであり、会議録による最終確認は未実施である。金額は市公式『令和8年度当初予算の概要（数値編）』の会計別予算規模で確認し、一般会計歳入予算額・一般会計歳出款別予算額の各合計とも一致した。公表精度は千円単位のため、その精度（千円単位）のまま記録し、円単位を合成していない）
- FY2024一般会計歳入総額 240,079,769千円（千円精度）
- FY2024一般会計歳出総額 236,639,777千円（千円精度）
- FY2024決算の認定議案である認定第1号『令和6年度尼崎市歳入歳出決算について』は第2回定例会で認定された（市議会公式の採決結果一覧表で確認。認定の議決日2025年10月7日は同定例会の第6日（最終日）の議事日程から特定したものであり、会議録による最終確認は未実施である）。実質収支額は市公式『令和6年度決算の概要（数値編）』により2,808,992千円（千円精度。歳入・歳出の差引額3,439,992千円が同資料の形式収支と検算一致し、翌年度に繰り越すべき財源631,000千円を差し引いた額）。FY2024は前期まちづくり基本計画（2023年度～2027年度）期間内の決算であり計画の版は現行と同一であるが、決算総額と13施策・展開方向との総額レベルの対応付けは公式資料にないため接続は行っていない

13施策の展開方向（全41件）の全件、施策評価の指標（目標指標・まちづくりの総合指標）の個別値、両議決日の会議録による最終確認、予算・決算の事項別明細書の款別合計との最終突合、監査委員の決算審査意見書の内容（個別の指摘事項等）の精査、FY2024決算と第6次尼崎市総合計画の接続（not_assessableとして保持）、補正・執行・契約・補助金はdeferred depthです。

### Milestone P15-M45 — Akashi reviewed package

Status: `complete`（2026-11-16）

明石市をPhase 15の45番目の`reviewed_complete`自治体として確定しました（所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

v1 declared package:

- あかしSDGs推進計画（明石市第6次長期総合計画）（自治基本条例に基づく市の最上位計画として2022年3月に市議会の議決を経て策定。基本構想を定める推進計画（2022年度～2030年度。2030年のあるべき姿『SDGs未来安心都市・明石 ～いつまでも すべての人に やさしいまちを みんなで～』と、まちづくりの方向性である経済・社会・環境の三側面を定める）、前期戦略計画（2022年度～2025年度）・後期戦略計画（2026年度～2030年度、現行）からなる戦略計画（まち・ひと・しごと創生総合戦略）、各分野の個別計画、年度ごとの実行計画で構成し、推進計画の期間と戦略計画の期間を別period semanticsとして保持する。戦略計画の各分野の主な施策と数値目標（KPI）の全件列挙は行わず、measuresは空のまま追加depthとして保持する。進行管理は、実行計画の策定を通じたPDCAサイクル（毎年度、戦略計画の主な施策の取組状況と数値目標の状況を検証し次年度の実行計画へ反映）と、あかしSDGs推進審議会による審議による自治体の進行管理の枠組みである。前総合計画（第5次長期総合計画、目標年次2020年度・2021年度まで延長運用）からの移行は版の履歴としてのみ保持し、前計画期間の実績を現行計画の期間へ前倒し接続しない）
- FY2026一般会計当初予算 151,508,494千円（成立。議案第29号『令和8年度明石市一般会計予算』は修正議決により成立したものであり、原案可決ではない。市公式『令和8年度当初予算案』ページが「予算議案に対する修正議決後の内容（3月25日）」と明記し、成立額は修正後の予算書第1条で確認した（歳入・歳出の各合計とも一致）。議決日は2026年3月25日。市議会公式の審議結果文書そのものの結果欄の文言と、修正の具体的内容は未確認のまま保持する。公表精度は千円単位のため、その精度（千円単位）のまま記録し、円単位を合成していない）
- FY2024一般会計歳入総額 131,291,999,787円（円単位）
- FY2024一般会計歳出総額 130,356,924,686円（円単位）
- FY2024決算の認定議案である議案第58号（議案第58号～第69号『令和6年度明石市一般会計歳入歳出決算ほか11件』）は、令和7年第2回定例会9月議会で原案どおり認定することに決定した（市議会公式『第2回定例会9月議会審議結果』で直接確認。決定日は2025年10月16日。不認定ではない）。実質収支額は市公式『令和6年度決算資料』により886,767,101円（円単位。歳入・歳出の差引額935,075,101円が同資料の形式収支と検算一致し、翌年度へ繰り越すべき財源48,308,000円を差し引いた額）。FY2024は前期戦略計画（2022年度～2025年度）期間内の決算であり戦略計画の版が現行（後期）と異なるため、決算総額と三側面の方向性・戦略計画の施策との総額レベルの対応付けは公式資料になく接続は行っていない

戦略計画（前期・後期）の各分野の主な施策と数値目標（KPI）の全件、予算議案の審議結果文書の結果欄の文言と予算修正の具体的内容、両議決の会議録による最終確認、予算・決算の事項別明細書の款別合計との最終突合、監査委員の決算審査意見書の内容（個別の指摘事項等）の精査、FY2024決算とあかしSDGs推進計画の接続（not_assessableとして保持）、補正・執行・契約・補助金はdeferred depthです。

### Milestone P15-M46 — Nishinomiya reviewed package

Status: `complete`（2026-11-16）

西宮市をPhase 15の46番目の`reviewed_complete`自治体として確定しました（所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

v1 declared package:

- 第5次西宮市総合計画（市の最上位計画として平成31年3月に策定。基本構想（2019年度～2028年度の10年。都市目標『未来を拓く文教住宅都市・西宮 ～憩い、学び、つながりのある美しいまち～』）、基本計画（前期2019年度～2023年度・後期2024年度～2028年度、現行は後期。本編にアクションプラン（西宮版総合戦略の取組を統合）を収録）、実施計画（各3年・ローリング方式で毎年度見直し、現行は令和8～10年度）で構成し、基本構想の期間と基本計画の前期・後期、実施計画の期間を別period semanticsとして保持する。後期基本計画の施策体系（6部・35施策分野と6つの分野横断の視点）は本編で全件確認し列挙したが、各施策分野の取組内容・部門別計画の全件列挙は行わず、measuresは空のまま追加depthとして保持する。進行管理は、実施計画（基本計画の各施策を具体化する主要な事務・事業について年次的な調整を加え、財源や市長のマニフェストなどとの整合を図る）のローリング方式による毎年度見直しと、収支見通し及び事業計画の公表による自治体の進行管理の枠組みである。前総合計画（第4次西宮市総合計画、基本目標『ふれあい 感動 文教住宅都市・西宮』）からの移行は版の履歴としてのみ保持し、前計画期間の実績を現行計画の期間へ前倒し接続しない）
- FY2026一般会計当初予算 221,422,490千円（成立。議案第493号『令和8年度西宮市一般会計予算』は第16回（令和8年3月）定例会で賛成多数により可決された。市議会公式『議案等審議結果一覧表』は結果文言欄を持たず脚注が採決結果を『賛成多数で可決されたこと』と定義しているため、議決結果はその定義の範囲でのみ記録し、原案のまま可決されたものとして記録していない。同表に議案第493号に対する修正案の行はない。議決日は2026年3月18日（会議録検索システム『議決結果』で確認）。金額は市公式『令和8年度当初予算の概要』の各会計予算規模で確認し、歳入款別合計・歳出目的別合計とも一致した。公表精度は千円単位のため、その精度（千円単位）のまま記録し、円単位を合成していない）
- FY2024一般会計歳入総額 205,479,435千円（千円精度）
- FY2024一般会計歳出総額 204,547,927千円（千円精度）
- FY2024決算の認定議案である認定第15号『令和6年度西宮市一般会計及び特別会計歳入歳出決算認定の件』は、第14回（令和7年9月）定例会で賛成多数により認定された（市議会公式『議案等審議結果一覧表』と会議録検索システム『議決結果』で直接確認。認定日は2025年10月2日）。実質収支額は監査委員決算審査意見書（西監発第53号）第6『一般会計』の表『決算収支の状況』により647,529千円（千円精度。歳入・歳出の差引額931,508千円が同表の形式収支と検算一致し、翌年度へ繰り越すべき財源283,979千円を差し引いた額。総論の一般会計・特別会計合計の実質収支1,861,075千円は使用していない）。FY2024は後期基本計画（2024年度～2028年度）の初年度の決算であり計画の版は現行と同一であるが、決算総額と6部・35施策分野との総額レベルの対応付けは公式資料になく接続は行っていない

後期基本計画の35施策分野ごとの取組内容・部門別計画・指標の全件、予算書・決算書の事項別明細書の款別合計との最終突合、監査委員の決算審査意見書の内容（個別の指摘事項等）の精査、FY2024決算と第5次西宮市総合計画の接続（not_assessableとして保持）、補正・執行・契約・補助金はdeferred depthです。

### Milestone P15-M47 — Nara reviewed package

Status: `complete`（2026-11-16）

奈良市をPhase 15の47番目の`reviewed_complete`自治体として確定しました（所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

v1 declared package:

- 奈良市第5次総合計画（未来ビジョン（2022年度～2031年度の10年。2031年のまちの姿『「わたし」からはじめる「わたしたち」のまち 奈良』、4つのまちの方向性、基本姿勢、重点分野4件（未来を育てる／活気を生み出す／生活をつなぐ／安全を守る））と推進方針（前期2022年度～2026年度・後期2027年度～2031年度、現行は前期推進方針）で構成し、未来ビジョンの期間と推進方針の前期・後期を別period semanticsとして保持する。前期推進方針の施策体系（5章・29施策）は計画本編の施策体系図で全件確認し列挙したが、各施策の下の施策の方向性・指標の全件列挙は行わず、measuresは空のまま追加depthとして保持する。進行管理は、計画の実施状況を毎年度とりまとめて公表し市議会へ報告する自治体の進行管理の枠組み（令和6年度分は報告第52号として2025年9月5日に報告）である。第4次総合計画からの移行（目標年度の1年延長と第5次総合計画の開始延期）は版の履歴としてのみ保持し、前計画期間の実績を現行計画の期間へ前倒し接続しない。策定中の後期推進方針の内容は現行の前期推進方針へ先取りしない）
- FY2026一般会計当初予算 193,425,597千円（成立。議案第16号『令和8年度奈良市一般会計予算』は令和8年3月定例会で2026年3月26日に修正可決された。修正は予算決算委員会に提出された宮池委員提出の修正案によるもので、総額を原案195,000,000千円から1,574,403千円減額した（病院事業会計貸付金1,000,000千円の全額削除、観光費402,500千円、衛生費168,000千円、教育費3,903千円等）。成立額は修正後の額であり、財政課『令和8年度当初予算の概要』の予算規模で確認し、令和8年度一般会計補正予算（第1号）の補正前の額とも一致する。原案の額は成立額として記録していない。公表精度は千円単位のため、その精度（千円単位）のまま記録し、円単位を合成していない）
- FY2024一般会計歳入総額 161,996,348,913円（円単位）
- FY2024一般会計歳出総額 157,827,488,682円（円単位）
- FY2024決算の認定である報告第41号『令和6年度奈良市一般会計歳入歳出決算の認定について』は、令和7年9月定例会で2025年9月29日に認定された（市議会公式『議決結果一覧表（令和7年9月定例会）』で直接確認）。実質収支額は『令和6年度決算総括表』により3,348,707,231円（円単位。歳入・歳出の差引額4,168,860,231円が同表の形式収支と検算一致し、繰り越すべき財源820,153,000円を差し引いた額）。FY2024は前期推進方針（2022年度～2026年度）の期間内の決算であり計画の版は現行と同一であるが、決算総額と5章・29施策との総額レベルの対応付けは公式資料になく接続は行っていない

29施策ごとの施策の方向性・指標の全件、予算書・決算書の事項別明細書の款別合計との最終突合、監査委員の決算審査意見書の内容（個別の指摘事項等）の精査、FY2024決算と奈良市第5次総合計画の接続（not_assessableとして保持）、補正・執行・契約・補助金はdeferred depthです。

### Milestone P15-M48 — Wakayama reviewed package

Status: `complete`（2026-11-16）

和歌山市をPhase 15の48番目の`reviewed_complete`自治体として確定しました（所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

v1 declared package:

- 第5次和歌山市長期総合計画（基本構想・基本計画（2017年度～2026年度の10年。将来都市像『きらり 輝く元気和歌山市』、2026年度の目標人口347,000人）と実施計画（3年・現行2024年度～2026年度、毎年度点検見直し）の3層で構成し、基本構想・基本計画の10年と実施計画の3年を別period semanticsとして保持する。基本計画の各論の政策体系（4つの分野別目標・26政策）は計画本編の目次で全件確認し列挙したが、各政策の下の施策・事業・指標の全件列挙は行わず、measuresは空のまま追加depthとして保持する。あわせて市内を10ブロックに分けた地域別計画を置く。進行管理は、実施計画を毎年度点検・見直しする自治体の進行管理の枠組みである。FY2026は計画の最終年度であり、period_statusはPhase 14インベントリどおりtransition_or_unresolvedを保持する。次期計画（第6次）の策定状況は公式資料で確認できていないため、移行は版の履歴としてのみ保持し、次期計画の内容を現行計画へ先取りしない）
- FY2026一般会計当初予算 165,768,945千円（成立。議案第31号『令和8年度和歌山市一般会計予算』は令和8年2月定例市議会で2026年3月13日に可決された。市議会公式『令和8年2月定例市議会 審議結果』の結果欄の文言は『可決』であり、その文言のまま記録する。当初予算額は市の公式『令和8年度 予算内示資料』（p.5当初予算の概要・p.6予算総括表（単位 千円））の2か所で直接確認し、和歌山市公報（告示第247号別冊）掲載の令和8年度一般会計補正予算（第1号）第1条からの算術的特定（補正後総額168,632,712千円－補正額2,863,767千円＝165,768,945千円）とも一致する。公表精度は千円単位のため、その精度（千円単位）のまま記録し、円単位を合成していない）
- FY2024一般会計歳入総額 171,406,400,509円（円単位）
- FY2024一般会計歳出総額 167,796,054,596円（円単位）
- FY2024決算の認定である認第6号『令和6年度和歌山市一般会計歳入歳出決算』は、令和7年12月定例会で2025年12月1日に認定された（市議会公式『12月定例会採決状況』および『令和7年12月定例市議会 審議結果』で直接確認）。実質収支額は実質収支に関する調書（総括表）により3,361,400千円（千円単位。差引3,610,346千円から翌年度へ繰り越すべき財源248,946千円を差し引いた額であり、調書の千円精度のまま記録し円単位を合成していない。歳入・歳出の円単位の差引残額3,610,345,913円は『令和6年度決算』歳入歳出決算総括表の記載と検算一致）。FY2024は第5次計画の期間内、実施計画（2024年度～2026年度）の初年度の決算であり計画の版は現行と同一であるが、決算総額と4つの分野別目標・26政策との総額レベルの対応付けは公式資料になく接続は行っていない

26政策の下の施策・事業・指標の全件、予算書・決算書の事項別明細書の款別合計との最終突合、監査委員の決算審査意見書の内容（個別の指摘事項等）の精査、FY2024決算と第5次和歌山市長期総合計画の接続（not_assessableとして保持）、補正・執行・契約・補助金はdeferred depthです。

## After Phase 15

1. その他市区町村
2. 選挙・候補者比較
3. API、データダウンロード、研究・報道向け機能
4. 比較可能性が確認された指標だけを用いた比較機能
