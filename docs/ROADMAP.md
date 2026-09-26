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

Status: `in_progress`

Phase 12完了により、北九州市・福岡市の2市をReviewed referenceとして保持しつつ、残る18市すべてが個票レベルのreview queueへ入りました。Phase 12由来のblocked source inventoryは0です。

Canonical queue（2026-09-27同期）:

- Reviewed reference: 2市（北九州市、福岡市）
- Review queue eligible: 18市
- Reviewed complete: 8市（札幌市、仙台市、さいたま市、千葉市、横浜市、川崎市、相模原市、新潟市）
- Review in progress: 1市（静岡市）
- Pending record review: 9市
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

### Current work — Shizuoka record review

Status: `in_progress`

新潟市のReviewed completionにより、Canonical queueの次対象は静岡市（221007）です。Phase 12で確定した公式Source Inventoryを起点に、現行計画identity、実施・進行管理層、成果指標、財政、version boundaryをEvidence付きでレビューします。

Phase 13では、公式一次資料・version・期間・財政state・評価主体を分離し、未公開Evidenceを推測補完しません。Schema、Evidence coverage、回帰テストを通過するまで市単位のPhase 13完了を宣言しません。

正本:

- `data/catalog/phase13_designated_city_review_queue.json`
- `data/catalog/*_phase13_policy_review_manifest.json`
- `data/catalog/*_phase13_completion.json`
- `data/evidence/*_evidence.json`
- `tests/test_phase13_*.py`

## After Phase 13

1. 静岡市をReviewed completeへ進め、その後の9市を順次Reviewed到達深度まで処理し、全20政令指定都市の市レベル基盤を完成させる
2. 中核市・県庁所在地
3. その他市区町村
4. 選挙・候補者比較
5. API、データダウンロード、研究・報道向け機能
6. 比較可能性が確認された指標だけを用いた比較機能
