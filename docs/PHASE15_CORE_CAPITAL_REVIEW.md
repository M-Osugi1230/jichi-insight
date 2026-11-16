# Phase 15 — Core cities and prefectural capitals record review

Status: `in_progress`（2026-10-01）

Phase 14で`source_inventory_complete`となった67自治体を、公式一次資料とrecord-level Evidence locatorを保持した`reviewed_complete`へ段階的に昇格します。

## Scope

- Target municipalities: 67
- Source phase: Phase 14
- Execution order: Phase 14 registry sequence
- Promotion target: `reviewed_complete`
- Blocked source inventories at start: 0

Phase 15は「公式Sourceを発見した」だけではReviewedにしません。自治体ごとに宣言したv1 review packageを作り、Schema、Evidence location、version/fiscal state、非推測境界、回帰テストを通過した場合だけ`reviewed_complete`へ昇格します。

## Required review layers

1. current plan identity and version
2. policy / measure structure at declared v1 depth
3. implementation or annual operating layer
4. available progress / KPI / evaluation evidence
5. plan transition and historical/current boundaries
6. FY2026 budget state
7. recent settlement state
8. audit / assembly / accountability role when used by the package
9. record-level official source URL and stable evidence locator
10. explicit deferred depth for evidence that is unpublished, unresolved, draft, historical-only, aggregate-only, or outside the declared v1 package

## Non-inference gates

- proposal / enacted / supplementary / execution / settlementを統合しない
- target / measurement / reporting / fiscal / publication / evaluation yearを同一視しない
- 旧計画の実績を現行計画actualへ流用しない
- draft・public comment・答申を採択済み計画へ先取り昇格しない
- source-reported evaluationをJichi Insight独自の政策達成評価へ変換しない
- aggregate値を個別identityへ配賦しない
- comparison methodology未確認の指標を都市間比較・score・rankingへ昇格しない
- causal attributionを資料の併存や時系列一致だけで認定しない

## Completion contract

各自治体は共通Schema `schemas/phase15_municipality_completion.schema.json` を使います。

必須package:

- official source catalog
- plan review
- policy structure
- progress / transition review
- fiscal records
- fiscal Evidence packets
- quality gate
- deferred depth
- completion boundary

共通Queue:

- `data/catalog/phase15_core_capital_review_queue.json`
- `schemas/phase15_core_capital_review_queue.schema.json`
- `tests/test_phase15_core_capital_review_queue.py`

## First completion — Hakodate

函館市をPhase 15最初の`reviewed_complete`としました。

Declared v1 package:

- current basic concept: 2017–2026
- priority projects: 2
- basic goals: 5
- current-plan measures: 20
- implementation layer: 第3期函館市活性化総合戦略 2025–2029
- implementation-strategy basic goals: 4
- evaluation governance: internal evaluation + external evaluation by the municipal regional-revitalization council
- successor plan: 2027–2036 draft kept in `draft_public_comment_open`
- FY2026 general-account initial-budget proposal: one reviewed top-line record
- FY2024 general-account settlement: exact revenue and expenditure top-line records

Deferred depth includes current third-strategy KPI/project item review, current-period annual KPI actuals, fine-grained current-plan-to-strategy linkage, successor-plan adoption, fiscal project detail, causality and cross-city comparability.

## Second completion — Asahikawa

旭川市を2市目の`reviewed_complete`へ昇格しました。

Declared v1 package:

- current comprehensive plan: 2016–2027
- current basic-plan version: 2023-12 revised edition
- basic goals: 5
- basic policies: 13
- current-plan measures: 34
- priority themes: 3
- third promotion plan: 2024–2027, 2026-06 revision
- annual project-group revision + PDCA / administrative evaluation governance
- current evaluation-indicator appendix availability reviewed without bulk-promoting source-reported achievement rates
- FY2026 general-account initial budget: 181,800,000,000 yen
- FY2024 general-account settlement: exact revenue and expenditure values from audit evidence

Deferred depth includes all current promotion-plan indicator identities/values, all expansion-measure/project identities and annual version diffs, all 34 measure indicator detail, successor-plan adoption, fiscal project detail, causality and cross-city comparability.

## Third completion — Aomori

青森市を3市目の`reviewed_complete`へ昇格しました。

Declared v1 package:

- current comprehensive plan: 青森市総合計画前期基本計画 2024–2028
- policy pillars: 3
- current-plan policies: 17
- policy realization directions: 5
- evaluation governance: annual indicator setting/tracking + major policy outcome reporting
- FY2026 general-account initial budget: 133,510,000,000 yen (enacted)
- FY2024 general-account settlement: exact revenue (142,517,400,928 yen) and expenditure (138,679,303,495 yen) values from audit evidence

Deferred depth includes row-level promotion for all measure indicators/targets/actuals/grades, major project detail from performance report, fine-grained policy-indicator-project linkage, fiscal project linkage, causality and cross-city comparability.

## Fourth completion — Hachinohe

八戸市を4市目の`reviewed_complete`へ昇格しました。

Declared v1 package:

- current comprehensive plan: 第7次八戸市総合計画 FY2022–FY2026
- action guidelines: 3
- current policies: 6
- current measures: 55
- annual strategy layer: 未来共創推進戦略2026 (9 strategies, 780 listed projects, 691 unique projects)
- evaluation governance: municipal committee review covering 616 projects, management indicators, survey data, and self-evaluations
- successor plan transition: はちのへビジョン8.0 draft (public comment completed)
- FY2026 general-account initial budget: 104,200,000,000 yen (enacted)
- FY2024 general-account settlement: exact revenue (108,585,206 thousand yen) and expenditure (105,245,944 thousand yen) values from audit evidence

Deferred depth includes row-level indicator values for all 55 measures, 691 project detail records, strategy-to-measure fine-grained linkage, successor plan adoption version, fiscal project detail, causality and cross-city comparability.

## Fifth completion — Morioka

盛岡市を5市目の`reviewed_complete`へ昇格しました（2026-11-15、公開責任者・大杉邑大のレビュー承認に基づく）。

Declared v1 package:

- current comprehensive plan: 盛岡市総合計画基本構想 2025–2034
- vision: 輝きが増し 活力に満ち 夢をかなえるまち盛岡
- basic goals: 4
- current-plan measures: 25
- management principles: 5
- implementation layer: 実施計画（令和7年度から16年度）、現行版 2026–2028、3年ローリング方式
- FY2026 general-account initial budget: 126,510,000,000 yen (enacted; 議案第3号 可決)
- FY2024 general-account settlement: exact revenue (135,207,433,943 yen) and expenditure (132,975,741,966 yen) values from the settlement summary table

Deferred depth includes all implementation-plan item/KPI identities and actuals, current-plan annual evaluation evidence, the FY2024 settlement-to-item linkage (kept not_assessable), direct confirmation of bill No. 3 on the official council vote-result page (provisional locator: council newsletter results table, corroborated by the bill text and press reporting), fiscal project detail, causality and cross-city comparability.

## Sixth completion — Akita

秋田市を6市目の`reviewed_complete`へ昇格しました（2026-11-15、公開責任者・大杉邑大のレビュー承認に基づく）。

Declared v1 package:

- current comprehensive plan: 第15次秋田市総合計画（秋田市『プラスの循環』プラン） 2026–2030
- structure: 基本構想＋推進計画（第3期秋田市まち・ひと・しごと創生総合戦略と統合）
- future city images: 5
- policy headings: 12
- plus-cycle strategies: 5
- previous plan: 第14次秋田市総合計画（県都『あきた』創生プラン） 2021–2025 — a separate plan, not directly comparable
- FY2026 general-account initial budget: 144,180,000,000 yen (enacted; 議案第2号 可決（賛成多数）, confirmed directly on the official council vote-result page)
- FY2024 general-account settlement: revenue (154,582,839 thousand yen) and expenditure (152,675,103 thousand yen) values at thousand-yen source precision

Deferred depth includes the exhaustive enumeration of all measures and KPIs, full-text confirmation of the basic-concept complete edition PDF, the old/new plan measure and KPI mapping, current-plan annual evaluation evidence, the FY2024 settlement-to-item linkage (kept not_assessable), fiscal project detail, causality and cross-city comparability.

## Seventh completion — Yamagata

山形市を7市目の`reviewed_complete`へ昇格しました（2026-11-15、公開責任者・大杉邑大のレビュー承認に基づく）。

Declared v1 package:

- current comprehensive plan: 山形市発展計画2030 2025–2029 (adopted March 2025; doubles as the local comprehensive strategy)
- structure: plan book in five chapters; chapter 4 sets out 19 policy fields
- policy fields: 19
- outcome indicators: 45 (baseline and target values set per policy field)
- previous plan: 山形市発展計画2025 2020–2024 — a separate plan, not directly comparable
- FY2026 general-account initial budget: 117,146,000,000 yen (enacted; 議第8号 原案のとおり可決 on 2026-03-24, confirmed on the official council vote-result list)
- FY2024 general-account settlement: exact revenue (114,253,058,301 yen) and expenditure (111,230,120,306 yen) values from the settlement book

Deferred depth includes the exhaustive enumeration of all policy fields and outcome indicators and their KPI detail, full-text confirmation of the plan book PDF, the old/new plan policy and indicator mapping, current-plan annual evaluation evidence, the FY2024 settlement certification date and result, the FY2024 settlement-to-item linkage (kept not_assessable), the presence or absence of FY2026 supplementary budgets, settlement breakdown by policy, fiscal project detail, causality and cross-city comparability.

## Eighth completion — Fukushima

福島市を8市目の`reviewed_complete`へ昇格しました（2026-11-15、公開責任者・大杉邑大のレビュー承認に基づく）。

Declared v1 package:

- current comprehensive plan: 第6次福島市総合計画 2021–2026 (period originally 2021–2025, extended by one year in March 2026)
- structure: two layers — まちづくり基本ビジョン (basic vision) and 実行プラン (execution plan)
- plan period extension: decided and voted in the March 2026 council session so the next (7th) plan can be prepared with fuller verification; FY2024 settlement and FY2026 budget both fall inside the current plan period, FY2026 being its final year
- FY2026 general-account initial budget: 124,500,000,000 yen (enacted; 議案第5号 原案可決 on 2026-03-27, confirmed on the official council deliberation results; thousand-yen precision confirmed in the budget overview annex table)
- FY2024 general-account settlement: exact revenue (136,983,126,064 yen) and expenditure (130,714,101,758 yen) values from the settlement book

Deferred depth includes the exhaustive enumeration of all basic policies, priority measures, individual measures and indicator values, full-text confirmation of the basic vision and execution plan PDFs, ingestion of the FY2024 execution-plan evaluation content, the vote breakdown and minutes for bill No. 5, the FY2024 settlement-to-item linkage (kept not_assessable), settlement breakdown by policy, the mapping to the forthcoming 7th comprehensive plan, fiscal project detail, causality and cross-city comparability.

## Ninth completion — Koriyama

郡山市を9市目の`reviewed_complete`へ昇格しました（2026-11-15、公開責任者・大杉邑大のレビュー承認に基づく）。

Declared v1 package:

- current comprehensive plan: 郡山市第7次総合計画 2026–2033 (started April 2026)
- structure: two layers — 公共計画 (public plan, main volume) and 行政計画 (administrative plan, first implementation plan); the population vision and comprehensive strategy are integrated into the plan
- plan transition: the previous framework 郡山市まちづくり基本指針（あすまちこおりやま） was the top plan through FY2025; the FY2024 settlement belongs to its seventh implementation plan (2024–2027, first year) and falls outside the current plan period, so the FY2024 settlement is not linked to current-plan items
- FY2026 general-account initial budget: 144,720,000,000 yen (enacted; 議案第39号 原案可決 with a majority on 2026-03-19, confirmed on the official council vote results; thousand-yen precision in the enacted bill text)
- FY2024 general-account settlement: exact revenue (160,788,173,369 yen) and expenditure (154,354,939,781 yen) values from the settlement book

Deferred depth includes the exhaustive enumeration of all basic goals, policy packages, individual measures and KPIs, full-text confirmation of the main-volume (public plan) PDF, the old/new framework policy and indicator mapping, current-plan annual evaluation evidence, the per-member vote breakdown for bill No. 39, the final cross-check against the enacted budget book, the current budget amount including supplementary budgets, the FY2024 settlement-to-item linkage (kept not_assessable), settlement breakdown by policy, fiscal project detail, causality and cross-city comparability.

## Tenth completion — Utsunomiya

宇都宮市を10市目の`reviewed_complete`へ昇格しました（2026-11-15、公開責任者・大杉邑大のレビュー承認に基づく）。

Declared v1 package:

- current comprehensive plan: 第6次宇都宮市総合計画 — basic concept (target year 2050), basic plan 2018–2027 (first phase 2018–2022, latter phase 2023–2027), implementation plan (roughly three years, revised annually)
- latter basic plan structure: six future-city policy pillars （子育て・教育／健康・福祉／安全・安心／魅力創造・交流／産業・環境／交通） plus the administrative management base; target city image is the "Super Smart City" formulation
- FY2026 general-account initial budget: 246,550,000,000 yen (enacted; 議案第18号 原案可決 on 2026-03-24, confirmed directly on the official council meeting-result page)
- FY2024 general-account settlement: revenue (242,716,210 thousand yen) and expenditure (236,437,643 thousand yen) values at thousand-yen source precision from the official settlement figures document; certification 議案第102号 原案認定 on 2025-09-30 confirmed on the official council meeting-result page

Deferred depth includes the exhaustive enumeration of strategic projects, measures and KPIs under each pillar, full-text confirmation of the latter basic plan book, the yen-precision settlement totals (not printed in the checked official summary documents; the audit opinion PDF could not be text-extracted for figure matching), administrative evaluation results, the FY2024 settlement-to-item linkage (kept not_assessable), fiscal project detail, causality and cross-city comparability.

## Eleventh completion — Maebashi

前橋市を11市目の`reviewed_complete`へ昇格しました（2026-11-15、公開責任者・大杉邑大のレビュー承認に基づく）。

Declared v1 package:

- current comprehensive plan: 第七次前橋市総合計画 (formulated March 2018), period 2018–2027, two layers only — basic concept plus promotion plan (revised every 3–4 years); current promotion plan is the third-term plan 2025–2027 (2025 revised edition) with six chapters mirroring the six pillars of the basic concept
- FY2026 general-account initial budget: 161,841,682,000 yen (enacted; 議案第15号 可決（多数）; vote date 2026-03-26 taken from the vote-disclosure section of the official result PDF, which does not print the date on the result table itself). The candidate's 161,841,680,000 yen was a transcription error from the mayor's 万円-precision explanation and is corrected in the candidate in this branch
- FY2024 general-account settlement at exact yen precision from the Audit Commission's settlement review opinion: revenue 159,237,541,694 yen / expenditure 154,807,075,147 yen (balance 4,430,466,547 yen matches); certification 議案第94号 可決（全員） per the official result table (no vote date printed, so none is recorded)

Deferred depth includes the exhaustive enumeration of priority measures, projects and KPIs under the six chapters, full-text confirmation of the plan book, individual administrative-evaluation results, the FY2024 settlement-to-item linkage (kept not_assessable), fiscal project detail, causality and cross-city comparability.

## Twelfth completion — Takasaki

高崎市を12市目の`reviewed_complete`へ昇格しました（2026-11-15、公開責任者・大杉邑大のレビュー承認に基づく）。

Declared v1 package:

- current comprehensive plan: 高崎市第6次総合計画, period 2018–2027, organised in three sections — 第1節 都市づくりの基本戦略 (14 strategies), 第2節 地域の特性を生かした振興策による都市づくり (7 regions), 第3節 主要施策 (4 fields: 総務教育・保健福祉・市民経済・建設水道) — and deliberately not mapped onto a generic three-layer model
- FY2026 general-account initial budget: 175,220,000,000 yen (enacted; 議案第28号 原案可決（賛成多数） in the 令和8年第2回定例会 vote-result PDF; the PDF does not print individual vote dates, so no vote date is recorded)
- FY2024 general-account settlement at published thousand-yen precision from the comprehensive audit report: revenue 183,362,219 thousand yen / expenditure 177,037,888 thousand yen (sub-thousand rounded; yen-precision totals are not published online — the settlement book is inspection-only). The candidate's man-yen-rounded values (183,362,220,000 / 177,037,890,000 yen) differ from the verified values and are corrected in the candidate in this branch. Certification 議案第78号・認定 in the 令和7年第4回定例会 vote-result PDF (again no individual vote date printed)

Deferred depth includes the names of the 14 strategies and the measures under each field, full-text confirmation of the plan book, the yen-precision settlement totals, designated-project progress-management results, the FY2024 settlement-to-item linkage (kept not_assessable), fiscal project detail, causality and cross-city comparability.

## Thirteenth completion — Kawagoe

川越市を13市目の`reviewed_complete`へ昇格しました（2026-11-15、公開責任者・大杉邑大のレビュー承認に基づく）。

Declared v1 package:

- current comprehensive plan: 第五次川越市総合計画 — basic concept 2026–2035, first basic plan 2026–2030, second basic plan 2031–2035, implementation plan 2026–2028 (rolling); eight fields and 38 measures in the first basic plan (4/5/5/5/4/5/5/5 per field, field names enumerated from the official plan page; individual measure names are not enumerated); future city image 「ずっと安心、もっと幸せ、魅力あふれるまち 川越」
- FY2026 general-account initial budget: 143,850,000,000 yen (enacted; 議案第29号 原案可決 on 2026-03-25, confirmed in the council newsletter 市議会だより 令和8年5月1日号）
- FY2024 general-account settlement at exact yen precision: revenue 136,944,893,371 yen / expenditure 130,469,349,651 yen (balance 6,475,543,720 yen matches); certification 議案第66号 certified 2025-09-29 （市議会だより 令和7年11月1日号）. FY2024 belongs to the fourth plan's second basic plan (2021–2025, year 4), so its linkage to the current plan stays not_assessable

Deferred depth includes the names and KPIs of the 38 measures, full-text confirmation of the plan book, evaluation evidence for the new plan (none exists yet), fiscal project detail, causality and cross-city comparability.

## Fourteenth completion — Kawaguchi

川口市を14市目の`reviewed_complete`へ昇格しました（2026-11-15、公開責任者・大杉邑大のレビュー承認に基づく）。

Declared v1 package:

- current comprehensive plan: 第6次川口市総合計画 — three layers (basic concept 2026–2035, first basic plan 2026–2030, second basic plan 2031–2035, implementation plan on a three-year rolling basis, FY2026 edition 2026–2028), three basic principles, and the eight official めざす姿 formulations taken verbatim from the city plan page (secondary paraphrase lists are not used); future city image 「産業と文化と自然が調和した 輝きあふれるまち 川口」
- FY2026 general-account initial budget: 256,970,000,000 yen (enacted; 議案第18号 原案可決 on **2026-03-23** as printed on the official vote-result table — a secondary research note giving 2026-03-24 was wrong and is not used)
- FY2024 general-account settlement at exact yen precision: revenue 259,800,531,831 yen / expenditure 247,943,564,747 yen (balance 11,856,967,084 yen matches); certification 議案第183号 certified 2025-11-28 (recorded in the candidate via PR #497); the bill's vote-table number in the December session table remains unconfirmed and is carried as the explicit open residual. FY2024 belongs to the fifth plan's second basic plan (2021–2025), so its linkage to the current plan stays not_assessable

Deferred depth includes the measures and KPIs under the eight goals, full-text confirmation of the plan book, the certification vote-table number, citizen-survey results, fiscal project detail, causality and cross-city comparability.

## Fifteenth completion — Iwaki

いわき市を15市目の`reviewed_complete`へ昇格しました（2026-11-15、公開責任者・大杉邑大のレビュー承認に基づく）。

Declared v1 package:

- current policy framework: いわき市まちづくりの基本方針 — **no fixed-period comprehensive plan exists**: Iwaki abolished the fixed-term plan model when the old plan ended in FY2020 and now runs on a framework with no fixed end date — a universal philosophy （まちづくりの理念， vision 『誰もが「住んで良かった、住み続けたい」と思える魅力にあふれた「いわき」』) plus the management guideline （経営指針）, which positions priority projects for roughly the next five years and is verified and updated every year, plus the annual いわき版骨太の方針 issued mid-year. The FY2026 guideline (updated April 2026) organises its positioned projects under five pillars （次世代を育てる／命・暮らしを守る／まちの魅力を高める／豊かさを創る／構造改革・DX推進事業）. No plan period is recorded, because none exists
- FY2026 general-account initial budget: 159,490,126,000 yen (enacted; 議案第35号 原案可決 on 2026-03-12 per the council vote-result list; amount from Article 1 of the budget book)
- FY2024 general-account settlement at exact yen precision: revenue 162,539,391,275 yen / expenditure 155,415,603,914 yen (balance 7,123,787,361 yen matches); certification 議案第18号 certified 2025-12-19 after continued review from the October session. FY2024 was executed under the current basic-policy framework (no cross-plan attribution problem), but its item-level linkage to the guideline's positioned projects was not performed, so the linkage stays not_assessable

Deferred depth includes the individual projects and KPIs under the five pillars, the audit commission's settlement review opinion (not inspected), itemised cross-checks against the budget/settlement detail books, supplementary-budget history, fiscal project detail, causality and cross-city comparability (the no-fixed-end framework must not be measured with the same yardstick as fixed-period plans).

## Sixteenth completion — Mito

水戸市を16市目の`reviewed_complete`へ昇格しました（2026-11-15、所有者・大杉邑大がチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

Declared v1 package:

- current plan: 水戸市第7次総合計画－みと魁・Nextプラン－ — basic concept 2024–2033 (vision 『こども育む くらし楽しむ みらいに躍動する 魁のまち・水戸』), basic plan in two halves (first 2024–2028, second 2029–2033; 総論＋各論）, three-year implementation plans prepared annually on a rolling basis (current edition 2026–2028). Three basic principles; the basic plan's 各論 is organised under four pillars （まち全体で「こどもたちを育むみと」／多くの人が集い、産業が集積する「活力あるみと」／命と健康、暮らしを守る「安全・安心なみと」／市民と行政で「共に創るみと」) with 11 mid-level items and 43 sub-items, plus two priority projects in the 総論 (Mission1 みとっこ未来プロジェクト／Mission2 若い世代の移住・定住加速プロジェクト）
- FY2026 general-account initial budget: 130,814,000,000 yen (enacted; 議案第26号 原案可決 on 2026-03-18, the final day of the 1st regular session of Reiwa 8; amount from the official budget overview's 千円-denominated scale table, consistent with the mayor's press-conference summary)
- FY2024 general-account settlement at exact yen precision: revenue 128,541,227,654 yen / expenditure 126,380,047,662 yen (balance 2,161,179,992 yen matches); certification 認定第1号 (covering the general and special accounts together) certified 2025-09-22. FY2024 is the first fiscal year of the seventh plan's period (no cross-plan attribution problem), but its item-level linkage to individual plan projects was not performed, so the linkage stays not_assessable

Deferred depth includes the measures and KPIs under the four pillars (including the 43 sub-items), full-text confirmation of the plan book, the audit commission's settlement review opinion (not inspected), annual evaluation evidence under the implementation plans, fiscal project detail, causality and cross-city comparability.

## Seventeenth completion — Koshigaya

越谷市を17市目の`reviewed_complete`へ昇格しました（2026-11-16、所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

Declared v1 package:

- current plan: 第5次越谷市総合振興計画 — basic concept 2021–2030 (vision 『水と緑と太陽に恵まれた みんなが活躍する安全・安心・共生都市』), basic plan in two halves (first 2021–2025, second 2026–2030), three-year implementation plans prepared on a rolling basis (latter-plan first edition 2026–2028). Basic principles from the municipal autonomy basic ordinance （人間尊重／市民主権； principles 参加・協働・情報共有）; the current latter basic plan has four chapters, whose chapter 3 （分野別計画） is organised under six goals （大綱） with 24 top-level measures （大項目）, four promotion viewpoints （危機管理、地域脱炭素、デジタル化、インクルージョン（包摂性）), and the まち・ひと・しごと創生越谷市総合戦略 positioned in chapter 4
- FY2026 general-account initial budget: 132,700,000,000 yen (enacted; 第25号議案 原案可決 on 2026-03-18, the final day of the March 2026 regular session; amount from Article 1 of the official budget book （総則）, stated in thousands of yen, consistent with the mayor's FY2026 policy speech figure of 1,327億円）
- FY2024 general-account settlement at exact yen precision: revenue 140,215,912,093 yen / expenditure 131,705,070,771 yen (balance 8,510,841,322 yen matches); certification 第101号議案 certified （認定可決） 2025-09-25. FY2024 belongs to the first basic plan period of the same fifth plan, so its totals must not be reused as results of the current latter basic plan; its item-level linkage to individual plan projects was not performed, so the linkage stays not_assessable

Deferred depth includes the individual projects and achievement indicators under the six goals and 24 measures, full-text confirmation of the plan book, the audit commission's settlement review opinion (not inspected), cross-checks against the settlement detail book, supplementary-budget history, fiscal project detail, causality and cross-city comparability.

## Eighteenth completion — Funabashi

船橋市を18市目の`reviewed_complete`へ昇格しました（2026-11-16、所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

Declared v1 package:

- current plan: 第3次船橋市総合計画 — basic concept and basic plan 2022–2031 as a single ten-year plan with no first/second-half split (vision 『人も まちも 輝く 笑顔あふれる 船橋』), three-year implementation plans prepared on a rolling basis (current edition 2026–2028). The basic concept sets five cross-field aimed city images （めざすまちの姿） and two basic stances （多様な主体との協働／持続可能な行財政運営）; the basic plan is organised under 24 basic measures （基本施策） with 71 measures （施策）, related to the aimed city images through a matrix rather than a hierarchy
- FY2026 general-account initial budget: 270,640,000,000 yen (enacted; 議案第1号 passed on 2026-03-25 at the 1st regular council session of 2026; amount from Article 1 of the official budget book, stated in thousands of yen, consistent with the official budget overview and the supplementary-budget reference material)
- FY2024 general-account settlement at the published thousand-yen precision: revenue 249,314,444千円 / expenditure 243,229,426千円 (balance 6,085,018千円 matches the published formal balance); certification 認定第1号 certified on 2025-10-03. Yen-level totals are not published in the official online sources, so they are not synthesised and the thousand-yen precision is kept explicit. FY2024 belongs to the same third plan period, but its totals were not linked to individual basic measures or projects, so the linkage stays not_assessable

Deferred depth includes the individual projects and achievement indicators under the 24 basic measures and 71 measures, full-text confirmation of the plan book, the audit commission's settlement review opinion (not inspected), confirmation of yen-level settlement totals, cross-checks against the settlement detail book, supplementary-budget history, fiscal project detail, causality and cross-city comparability.

## Nineteenth completion — Kashiwa

柏市を19市目の`reviewed_complete`へ昇格しました（2026-11-16、所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

Declared v1 package:

- current plan: 柏市第六次総合計画 — basic concept 2025–2034 (vision 『柏に関わる一人ひとりが想いを実現できるまち～多様な価値や人々がつながり、新たな価値の創造に挑戦～』), basic plan in two halves (first 2025–2029, second 2030–2034), three-year implementation plans revised every year (current edition 2026–2028). The basic concept sets three basic goals （基本的な目標） that cut across fields; the first-half basic plan combines three cross-field priority themes （重点テーマ, seven items) with a policy framework （施策体系） of 22 fields （分野） and 66 measures （施策）
- FY2026 general-account initial budget: 191,224,000,000 yen (enacted; 議案第34号 原案可決 on 2026-03-24 at the 1st regular council session of 2026; amount from the official budget overview's revenue/expenditure tables, stated in thousands of yen)
- FY2024 general-account settlement at exact yen precision: revenue 175,594,266,737 yen / expenditure 168,389,488,303 yen (balance 7,204,778,434 yen matches the published 歳入歳出差引残高）; certification 議案第16号 certified （原案認定） 2025-10-02. FY2024 predates the sixth plan period and belongs to the former fifth plan, so its totals must not be reused as results of the current plan; its item-level linkage to individual plan projects was not performed, so the linkage stays not_assessable

Deferred depth includes the individual projects and achievement indicators under the 22 fields and 66 measures and the priority themes, full-text confirmation of the plan book, the audit commission's settlement review opinion (not inspected), cross-checks against the settlement detail book, supplementary-budget history, fiscal project detail, causality and cross-city comparability.

## Twentieth completion — Shinjuku

新宿区を20番目の`reviewed_complete`へ昇格しました（2026-11-16、所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

Declared v1 package:

- current plan: 新宿区総合計画 — basic concept adopted in FY2007 and held through FY2027, the final year of the comprehensive plan (vision 『『新宿力』で創造する、やすらぎとにぎわいのまち』); comprehensive plan 2018–2027 integrating the basic plan and the urban master plan, with the basic plan setting five basic policies （基本政策） and 33 individual measures （個別施策）; third action plan 2024–2027 with 65 projects, revised by rolling review. Shinjuku is a special ward: this framework is recorded as it is and is not converted into a single city-style comprehensive plan model
- FY2026 general-account initial budget: 187,835,560,000 yen (enacted; 第1号議案 passed; amount from Article 1 of the official budget book, stated in thousands of yen. The vote date 2026-03-24 is identified from the regular session schedule — the final day's plenary session was for votes on bills — and final confirmation against the plenary session minutes remains outstanding)
- FY2024 general-account settlement at exact yen precision: revenue 190,137,549,271 yen / expenditure 184,195,725,502 yen (balance 5,941,823,769 yen matches the published 歳入歳出差引額）; certification 認定第1号 certified on 2025-10-20. FY2024 falls inside the current comprehensive plan period, but its totals are section-level aggregates and are not linked to individual measures or action-plan projects, so the linkage stays not_assessable

Deferred depth includes the individual projects and achievement indicators under the 33 individual measures and the 65 action-plan projects, full-text confirmation of the plan book, the audit commission's settlement review opinion (not inspected), cross-checks against the settlement detail book, final confirmation of the FY2026 budget vote date against the plenary session minutes, supplementary-budget history, fiscal project detail, causality and cross-city comparability.

## Twenty-first completion — Hachioji

八王子市を21番目の`reviewed_complete`へ昇格しました（2026-11-16、所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

Declared v1 package:

- current plan: 八王子未来デザイン2040 — basic concept adopted unanimously by the city council in December 2012 (based on the draft submitted by a 184-member citizens' conference) and inherited by the current plan, with the basic concept's principle 『人とひと、人と自然が響き合い、みんなで幸せを紡ぐまち八王子』; basic plan FY2023–FY2030 looking ahead to 2040 (the '2040' in the plan name is the outlook year, not the plan period), organising 37 measures （施策） under the concept's six city images （都市像）; implementation and progress governance through the management plan (first period FY2023–FY2026) and annual action plans, with three-tier administrative evaluation （施策評価・事務事業評価・細事業評価） feeding each year's budget compilation
- FY2026 general-account initial budget: 245,100,000,000 yen (enacted; 第5号議案 passed on 2026-03-26 at the 1st regular council session of 2026; amount from the official budget overview's scale table in thousands of yen, cross-checked against the revenue/expenditure tables)
- FY2024 general-account settlement at exact yen precision: revenue 241,406,662,517 yen / expenditure 236,288,910,299 yen (balance 5,117,752,218 yen matches the published 歳入歳出差引額 in the audit commission's settlement review opinion); certification 第133号議案 certified on 2025-10-08. FY2024 falls inside the current basic plan period, but its totals are section-level aggregates and are not linked to individual measures or priority projects, so the linkage stays not_assessable

Deferred depth includes the individual sub-measures, KPIs and priority projects under the 37 measures and the management plan, full-text confirmation of the plan book, the substantive content of the audit commission's settlement review opinion, individual administrative-evaluation results, cross-checks against the settlement detail book, final confirmation of the vote proceedings against the plenary session minutes, supplementary-budget history, fiscal project detail, causality and cross-city comparability.

## Twenty-second completion — Yokosuka

横須賀市を22番目の`reviewed_complete`へ昇格しました（2026-11-16、所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

Declared v1 package:

- current plan: YOKOSUKAビジョン2030 — the city's top plan (横須賀市基本構想・基本計画), replacing the former three-layer structure (basic concept / basic plan / implementation plan) with a two-layer structure that integrates the basic concept and the basic plan; plan period FY2022–FY2029; city-wide future image 『変化を力に進むまち』, developed by backcasting from the desired future state and adopted as 議案第57号 on 2022-03-24; ten field-level future images （分野別未来像）, with the per-field policy directions beneath them not enumerated in v1; implementation and progress governance through the Yokosuka Rebirth Plan （横須賀再興プラン, current version 2026-2029, also serving as the machi-hito-shigoto comprehensive strategy) and administrative evaluation (implementation-plan progress management plus the general review of administrative work, advised by the Policy Promotion and Administrative Evaluation Committee)
- FY2026 general-account initial budget: 180,120,000,000 yen (enacted; 議案第18号 passed as proposed on 2026-03-25 at the March 2026 regular council session; amount from Article 1 of the bill as published in the official budget book, 180,120,000千円, cross-checked against the first table's revenue/expenditure totals)
- FY2024 general-account settlement at exact yen precision: revenue 177,898,477,901 yen / expenditure 171,999,984,597 yen (balance 5,898,493,304 yen matches the published 収支差引額 in the audit committee's settlement review opinion); certification 議案第100号 certified on 2025-10-07. FY2024 falls inside the current vision period and inside the previous implementation plan period (FY2022–FY2025), but its totals are section-level aggregates and are not linked to individual fields or projects, so the linkage stays not_assessable

Deferred depth includes the full enumeration of the per-field policy directions under the ten field-level future images, the Rebirth Plan's individual projects, numerical targets and KPIs, individual administrative-evaluation results, full-text confirmation of the plan books, the substantive content of the audit committee's settlement review opinion, cross-checks against the settlement detail book, final confirmation of the vote proceedings against the plenary session minutes, supplementary-budget history, fiscal project detail, causality and cross-city comparability.

## Twenty-third completion — Toyama

富山市を23番目の`reviewed_complete`へ昇格しました（2026-11-16、所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

Declared v1 package:

- current plan: 第2次富山市総合計画 — the city's top plan with a three-layer structure (basic concept / basic plan / implementation plan); basic concept period FY2017–FY2026 with the city vision 『人・まち・自然が調和する活力都市とやま』 and the basic philosophy of compact town development; the basic plan runs in a first half (FY2017–FY2021) and a latter half (FY2022–FY2026), and the current basic plan is the latter basic plan (adopted March 2022), which sets four town-development goals with 14 policies and 51 measures beneath them (the 51 measures are not enumerated in v1) plus the Next Stage priority projects (seven priority themes from three viewpoints); implementation and progress governance through annual implementation plans (the FY2026 implementation plan is the final-year plan of the current plan, covering 177 comprehensive-plan projects) and outcome-oriented town development (outcome indicators per measure, effect measurement through citizen surveys, and the PDCA administrative management cycle). The third Toyama City comprehensive plan is being drafted (FY2024–FY2026) and is recorded only as a plan transition, with its content not recorded and not connected to the current plan's structure
- FY2026 general-account initial budget: 199,776,107,000 yen (enacted; 議案第1号 passed as proposed on 2026-03-24 at the March 2026 regular council session; amount from the official budget overview's account table at thousand-yen precision, 199,776,107千円, cross-checked against the post-vote budget scale table; the amount carried forward to the March supplementary budget, shown as an external figure in the overview, is not included)
- FY2024 general-account settlement at thousand-yen precision as published: revenue 189,996,111千円 / expenditure 185,876,806千円 (balance 形式収支 4,119,305千円 matches the published figure in the official settlement document); certification 認定第1号 certified on 2025-11-28 after continued review from the September 2025 session into the December 2025 session. The published precision is thousand yen, so no yen-precision totals are synthesized. FY2024 falls inside the latter basic plan period (FY2022–FY2026), but its totals are section-level aggregates and are not linked to individual goals, policies, measures or projects, so the linkage stays not_assessable

Deferred depth includes the full enumeration of the latter basic plan's 51 measures, the implementation plan's comprehensive-plan projects and their outcome indicators and results, full-text confirmation of the plan books, the content of the third comprehensive plan now being drafted, inspection of the audit committee's settlement review opinion (including whether yen-precision totals are published there), cross-checks against the settlement detail book and the budget book's bill text and first table, final confirmation of the vote proceedings against the plenary session minutes, supplementary-budget history, fiscal project detail, causality and cross-city comparability.

## Twenty-fourth completion — Kanazawa

金沢市を24番目の`reviewed_complete`へ昇格しました（2026-11-16、所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

Declared v1 package:

- current plan: 未来共創計画 — the action plan for the Kanazawa city vision 『未来を拓く世界の共創文化都市・金沢』 (adopted by council vote in December 2023) and the city's top administrative plan; a single ten-year plan FY2024–FY2033 rather than a basic-concept / basic-plan / implementation-plan layer structure, with three stages inside the period (advancement period 2 years, enrichment period 4 years, development period 4 years); five basic policies from the city vision with 21 policy directions beneath them (four under each of basic policies 1–4 and five under basic policy 5; the measures and major projects under the policy directions and all 85 KPIs are not enumerated in v1); progress governance through KPI-based PDCA (citizen-awareness indicators from the annual citizen survey and policy indicators), stage evaluations and plan revisions, with the plan versions (original February 2024, February 2025 revision, June 2026 revision) kept separate and revision-added measures never retroactively connected to the original framework
- FY2026 general-account initial budget: 207,800,000,000 yen (enacted; enactment confirmed by the official city gazette No. 3209 (2026-03-11), notice No. 56, publishing the budget outline as passed by the February 2026 regular monthly council session under Article 219(2) of the Local Autonomy Act; a skeleton budget (骨格予算) compiled ahead of the mayoral election, centred on mandatory expenses and continuing projects; the general-account budget bill number and the vote date are not identified in the primary sources consulted and are not recorded)
- FY2024 general-account settlement at yen precision as published: revenue 218,624,336,395 yen / expenditure 210,147,360,368 yen (balance 歳入歳出差引残額 8,476,976,027 yen matches the published figure in the official settlement summary table); certification 認定第1号 certified at the December 2025 regular monthly council session (the exact certification date is not printed in the council's official deliberation results and is not recorded). FY2024 is the first year of the plan period (advancement stage), but its totals are section-level aggregates and are not linked to individual basic policies, policy directions or KPIs, so the linkage stays not_assessable

Deferred depth includes the full enumeration of the measures and major projects under the 21 policy directions, all 85 KPIs and their results, the revision differences (including the 13 measures / 36 major projects added by the June 2026 revision), cross-checks against the settlement detail book and the budget book's bill text and first table, identification of the budget bill number and vote date and of the settlement certification date, inspection of the audit committee's settlement review opinion, supplementary-budget history, fiscal project detail, causality and cross-city comparability.

## Twenty-fifth completion — Fukui

福井市を25番目の`reviewed_complete`へ昇格しました（2026-11-16、所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

Declared v1 package:

- current plan: 第八次福井市総合計画 — the city's governing plan under the city vision 『みんなが輝く 全国に誇れる ふくい』 inherited from the seventh plan; a five-year plan FY2022–FY2026 (FY2026 is its final year) structured as vision / priority policies / policies / measures, with a separate implementation plan setting the major projects and numerical targets; four fields (社会基盤・市民福祉・産業・教育) holding 14 policies beneath them (the 53 measures and 64 KPIs under the policies are not enumerated in v1); progress governance through the annual comprehensive-plan reports (成果報告書 and KPI achievement status), with KPI achievement kept as the municipality's self-evaluation. The plan framework was confirmed from official comprehensive-plan reports (the FY2024 KPI achievement annex) and the official FY2026 budget overview because retrieval of the plan book pages failed; it is not recorded as confirmed from the plan book itself. The ninth comprehensive plan, now being drafted in the council (審議会), is kept only as a plan-transition record in a separate version and is never retroactively connected to the eighth plan's framework
- FY2026 general-account initial budget: 137,700,000,000 yen (enacted; bill No. 1 『令和8年度福井市一般会計予算』, submitted 2026-02-16 and passed as proposed (原案可決) on 2026-03-19 at the March 2026 regular council session, confirmed in the council's official deliberation results)
- FY2024 general-account settlement at yen precision as published: revenue 133,427,298,121 yen / expenditure 130,218,901,390 yen (balance 差引・形式収支 3,208,396,731 yen matches the published figure in the official settlement summary table 総表・その2; real balance 実質収支 2,248,179,731 yen); certification 第66号議案 certified on 2025-12-01 (submitted 2025-09-25). FY2024 is the third year of the plan period, but its totals are section-level aggregates and are not linked to individual policies, measures or KPIs, so the linkage stays not_assessable

Deferred depth includes the full enumeration of the 53 measures and 64 KPIs and their results, the implementation plan's major projects, confirmation of the plan framework against the plan book itself when it becomes retrievable, cross-checks against the settlement detail book and the budget book's bill text (第1号議案第1条) and first table, inspection of the audit committee's settlement review opinion, the ninth plan's framework, supplementary-budget history, fiscal project detail, causality and cross-city comparability.

## Twenty-sixth completion — Kofu

甲府市を26番目の`reviewed_complete`へ昇格しました（2026-11-16、所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

Declared v1 package:

- current plan: 第七次甲府市総合計画 — the city's top-level plan under Article 22 of the Kofu City Autonomy Basic Ordinance; a two-layer plan of a basic concept (FY2026–FY2035, ten years) and an implementation plan revised annually under a three-year rolling method; the city vision is 『幸せ実感 希望ある未来を創り続けるまち 甲府』 and the basic concept was enacted as bill No. 109 on 2025-12-17; three basic goals holding six measures each, 18 measures in total (the sub-measures beneath the measures and the implementation plan's projects are not enumerated in v1), with cross-cutting perspectives (population-decline countermeasures, a sustainable society, administrative reform) and the promotion principles (collaboration, well-being, civic pride); progress governance through evaluation and improvement of the implementation plan's measures and projects — FY2026 is the plan's first year and no annual results under the implementation plan have been published yet. The sixth comprehensive plan (FY2016–FY2025) is kept only as a plan-transition record in a separate version and is never retroactively connected to the seventh plan's framework
- FY2026 general-account initial budget: 91,787,060 thousand yen (enacted; bill No. 5 『令和8年度甲府市一般会計予算』, passed on 2026-03-25 at the March 2026 regular council session, confirmed in the council's official deliberation results). The amount is published at sen-yen (thousand-yen) precision, so it is kept at that precision and yen-precision amounts are not synthesized
- FY2024 general-account settlement at yen precision as published: revenue 91,644,865,806 yen / expenditure 90,039,308,506 yen (balance 歳入歳出差引額 1,605,557,300 yen matches the published figure in the audit commissioners' settlement-review opinion 甲監発第24号; real balance 実質収支 1,191,233,328 yen); certification 議案第95号 certified on 2025-10-02. FY2024 is a settlement of the sixth plan's period and its period does not overlap the seventh plan, and its totals are section-level aggregates that are not linked to individual goals, measures or projects, so the linkage stays not_assessable

Deferred depth includes the full enumeration of the sub-measures and the first implementation plan's measure-and-project framework, cross-checks against the budget explanatory materials and the settlement detail book (事項別明細書) at section level, the sixth plan's framework itself, annual results and evaluation evidence under the implementation plan, supplementary-budget history, fiscal project detail, causality and cross-city comparability.

## Twenty-seventh completion — Nagano

長野市を27番目の`reviewed_complete`へ昇格しました（2026-11-16、所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

Declared v1 package:

- current plan: 第五次長野市総合計画 — a three-layer comprehensive plan of a basic concept, basic plans and implementation plans; the basic concept was enacted by the city council in March 2017 and runs FY2017–FY2026 (ten years), the city vision is 『幸せ実感都市『ながの』〜“オールながの”で未来を創造しよう〜』; the basic plans run five years each (first period FY2017–FY2021, latter period FY2022–FY2026, the latter integrating the city's machi-hito-shigoto creation strategy) and the implementation plans are one-year plans revised annually; the basic concept's framework places seven fields holding 22 policies, and the latter basic plan unfolds 55 measures under the policies plus three cross-field themes (the strategy) (the 55 measures are not enumerated in v1); progress governance through a PDCA cycle led by the comprehensive plan promotion headquarters (chaired by the mayor), with evaluation and verification results published every year as the plan progress status (survey and statistical indicators and individual sheets). FY2026 is the plan's final year. The next comprehensive plan (starting FY2027, now being prepared in the city's comprehensive council) is kept only as a plan-transition record in a separate version and is never retroactively connected to the fifth plan's framework
- FY2026 general-account initial budget: 195,220,000 thousand yen (enacted; bill No. 1 『令和8年度長野市一般会計予算』, passed as proposed (原案可決) on 2026-03-23 at the March 2026 regular council session, with the amendment to bill No. 1 rejected, confirmed in the council's official deliberation status). The amount is published at sen-yen (thousand-yen) precision, so it is kept at that precision and yen-precision amounts are not synthesized
- FY2024 general-account settlement at yen precision as published: revenue 170,949,499,030 yen / expenditure 166,702,305,036 yen (balance 歳入歳出差引額 4,247,193,994 yen matches the published figure in the audit commissioners' settlement-review opinion 7監査第40号; real balance 実質収支 2,636,253,994 yen); certification 認定第2号 certified on 2025-09-30. FY2024 falls inside the fifth plan's period (the third year of the latter basic plan), but its totals are section-level aggregates that are not linked to individual policies, measures or indicators, and no reconciliation against the published progress status has been performed, so the linkage stays not_assessable

Deferred depth includes the full enumeration of the 55 measures and their indicators and results, the implementation plan's individual projects, cross-checks against the budget explanatory materials and the settlement detail book (事項別明細書) at section level, reconciliation of the settlement totals against the published progress status, the next plan's framework itself, supplementary-budget history, fiscal project detail, causality and cross-city comparability.

## Twenty-eighth completion — Matsumoto

松本市を28番目の`reviewed_complete`へ昇格しました（2026-11-16、所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

Declared v1 package:

- current plan: 松本市基本構想2030・第12次基本計画 — a three-layer comprehensive plan of a basic concept, basic plans and implementation plans; Basic Concept 2030 runs FY2021–FY2030 under the basic philosophy of evolving and deepening the city's identity symbolized by the "three gaku" (peaks, music, learning), with the catchphrase 『豊かさと幸せに 挑み続ける 三ガク都』 and five action goals that citizens and the administration work on together; the twelfth basic plan is the concept's latter plan for FY2026–FY2030 and incorporates the third Matsumoto regional-revitalization comprehensive strategy; it sets four purposes, three policy directions, two priority strategies (zero carbon; DX/digitalization) and four emphasized viewpoints, with 47 basic measures across seven fields (all 47 measures are enumerated); outcome indicators (KPI) are set for each basic measure for target and progress management, and administrative-operation measures are defined separately in the administrative action guidelines. The eleventh basic plan (FY2021–FY2025) is kept only as a separate version, and the twelfth plan's framework is never retroactively connected to the eleventh plan period
- FY2026 general-account initial budget: 114,980,000 thousand yen (enacted; bill No. 43 『令和8年度松本市一般会計予算』, submitted to the February 2026 regular session and voted on at the plenary of 2026-03-16 per the agenda of minutes No. 5, which lists the committee-chair reports and votes for bills No. 1 to No. 71; enactment is corroborated by the official June 2026 supplementary-budget overview, which carries the initial amount of 114,980,000 thousand yen as the already-enacted base amount. The minutes-body wording 原案可決 was not directly confirmed and is not asserted). The amount is published at sen-yen (thousand-yen) precision, so it is kept at that precision and yen-precision amounts are not synthesized
- FY2024 general-account settlement at yen precision as published: revenue 116,331,387,915 yen / expenditure 113,406,566,809 yen (balance 歳入歳出差引額 2,924,821,106 yen matches the published figure in the audit commission's settlement-review opinion 松監事第24号; real balance 実質収支 2,503,250,288 yen); certification 議案第18号 certified on 2025-11-04 at the third extraordinary session of 2025, after continued review by the settlement special committee during the recess. FY2024 is a settlement of the eleventh basic plan period (FY2021–FY2025) under Basic Concept 2030 — a different plan version from the twelfth basic plan — and its totals are section-level aggregates that are not linked to the twelfth plan's measures or indicators, so the linkage stays not_assessable

Deferred depth includes the outcome-indicator (KPI) actuals of the 47 measures, the implementation plan's individual projects, cross-checks against the budget explanatory materials and the settlement detail book (事項別明細書) at section level, the eleventh basic plan's framework itself, supplementary-budget history, fiscal project detail, causality and cross-city comparability.

## Twenty-ninth completion — Gifu

岐阜市を29番目の`reviewed_complete`へ昇格しました（2026-11-16、所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

Declared v1 package:

- current framework: 岐阜市未来のまちづくり構想 — a vision-type framework, not a fixed-period layered comprehensive plan; adopted in February 2022 and starting FY2022, it sets a future vision for around 2040, 『人がつながる 創造が生まれる しなやかさのあるまち』, with no fixed end year (the 2040 horizon is a target horizon, never recorded as a fixed end) and reviews every five years; four basic approaches (オール岐阜のまちづくり／シビックプライドの醸成／DXと脱炭素化／持続可能で選ばれるまち) and five policy fields (教育・子育て／健康・福祉・医療／市民協働・防災・環境／産業・労働・交流／都市基盤整備・交通・中心市街地活性化), each field carrying three citizen-survey-based indicators (all five fields and their indicators are enumerated), plus an administrative-management viewpoint; the subordinate 岐阜市未来創生総合戦略 (FY2024–FY2027) reflects the concept's vision, integrates the regional-revitalization comprehensive strategy and the SDGs Future City plan, and runs on three pillars (ひとの創生・しごとの創生・まちの創生); progress is managed annually against three numerical targets for the vision and the field indicators, with the 岐阜市未来のまちづくり懇談会 advising on progress evaluation. The concept revision now in preparation is kept only as a transition chronology record
- FY2026 general-account initial budget: 200,680,000 thousand yen (enacted; bill No. 1 『令和8年度岐阜市一般会計予算』, submitted to the first (March) 2026 regular session and passed as proposed on 2026-03-27 per the council's official voting-results list; the official FY2026 budget explanatory book's section-level revenue and expenditure totals agree at the same amount). The amount is published at sen-yen (thousand-yen) precision, so it is kept at that precision and yen-precision amounts are not synthesized
- FY2024 general-account settlement at yen precision as published: revenue 198,779,091,770 yen / expenditure 192,092,917,389 yen (balance 歳入歳出差引額 6,686,174,381 yen matches the published figure in the official settlement-by-account table; the revenue total also matches the section-level revenue table of the general-account settlement document); certification 第107号議案 certified on 2025-09-25. FY2024 is a settlement of the concept's third year and the Future Creation Comprehensive Strategy's first year, but its totals are account- and section-level aggregates and the concept's indicators are mainly citizen-survey-based subjective indicators, so the totals are not linked to the concept's fields or indicators or to the strategy's KPIs and the linkage stays not_assessable

Deferred depth includes the field-level plans' measures and projects under the five policy fields, the Future Creation Comprehensive Strategy's KPI actuals, the final cross-check against the settlement detail book (事項別明細書) at section level, the FY2024 real balance (実質収支, not published in the settlement-by-account table), the predecessor framework (ぎふし未来地図) and the revised concept's framework, supplementary-budget history, fiscal project detail, causality and cross-city comparability.

## Thirtieth completion — Toyohashi

豊橋市を30番目の`reviewed_complete`へ昇格しました（2026-11-16、所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

Declared v1 package:

- current plan: 第6次豊橋市総合計画 — a fixed-period three-layer comprehensive plan (basic concept / basic plan / implementation plan); the basic concept runs FY2021–FY2030 with the basic philosophy 『私たちがつくる 未来をつくる』 and the target city image 『未来を担う 人を育むまち・豊橋』; the basic plan moved from its first period (FY2021–FY2025) to the latter basic plan (FY2026–FY2030), which is the current plan; the latter basic plan's field plans hold eight fields and 38 policies (all 38 policies are enumerated), and the cross-field city-building strategy (まちづくり戦略) is positioned as the priority layer with four individual strategies and 13 basic policies; progress is managed by reviewing the implementation plan every year on a three-year rolling basis and mapping each project to the city-building strategy, with cross-field administrative operations carried in the implementation plan's 『基本計画推進のために』 chapter. The first-to-latter basic plan transition is kept only as a version chronology record
- FY2026 general-account initial budget: 165,610,000 thousand yen (enacted; bill No. 4 『令和8年度豊橋市一般会計予算』, submitted to the March 2026 regular session, referred to the budget special committee and passed as proposed on 2026-03-24 per the council's official voting-results list; the official June 2026 supplementary-budget material carries the same current-budget total). The amount is published at sen-yen (thousand-yen) precision, so it is kept at that precision and yen-precision amounts are not synthesized
- FY2024 general-account settlement at yen precision as published: revenue 153,279,132,232 yen / expenditure 151,163,708,560 yen (the balance of 2,115,423,672 yen is consistent with the published balance of 2,115,424 thousand yen (rounded) in the official settlement summary; the appendix's account-level table and section summary table agree). The settlement certification bill, bill No. 95 『令和6年度豊橋市一般会計歳入歳出決算認定について』, was voted NOT certified (不認定) at the September 2025 regular session, as confirmed by the mayor's official notification dated 2025-09-29; the rejection is recorded exactly as published and is never recorded as a certification. The exact vote date remains unidentified — the 2025-09-29 date is the notification date and is not asserted as the vote date. The December 2025 regular session received report No. 37 『決算不認定に係る措置について』 on the measures taken in response to the non-certification. FY2024 is a settlement of the first basic plan period (FY2021–FY2025), a different plan version from the latter basic plan, so the totals are not linked to the latter plan's policies or strategies and the linkage stays not_assessable

Deferred depth includes the field plans' measures and projects under the 38 policies, the project linkage for each of the city-building strategy's 13 basic policies, cross-checks against the budget book and the settlement book (事項別明細書) at section level, the FY2024 real-balance statement values, the exact vote date of bill No. 95, the first basic plan's framework itself, supplementary-budget history, fiscal project detail, causality and cross-city comparability.

## Thirty-first completion — Okazaki

岡崎市を31番目の`reviewed_complete`へ昇格しました（2026-11-16、所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

Declared v1 package:

- current plan: 第7次岡崎市総合計画 — the Comprehensive Policy Guidelines (ten-year policy guidelines looking thirty years ahead; target year FY2050; future city image 『一歩先の暮らしで三河を拓く 中枢・中核都市おかざき』; four basic guidelines), the Future Investment Plan and individual plans; the Future Investment Plan moved from its first period (FY2021–FY2025) to the latter period (FY2026–FY2030, revised in March 2026), which is the current plan; the latter plan's main initiatives hold ten fields and 54 initiatives (all 54 are enumerated), and the cross-field Future Investment Packages (未来のまち／未来のひと／未来のしごと／未来のパートナーシップ) group the promotion projects; progress is managed by grouping the ten fields into four groups (まち・環境／ひと・社会／しごと・経済／行政運営・パートナーシップ) for target setting and progress management, with reference indicators (FY2030 target values and current values) set for each group, and the packages' project lists are revised as circumstances change. The first-to-latter period transition is kept only as a version chronology record
- FY2026 general-account initial budget: 154,850,000 thousand yen (enacted; bill No. 56 『令和8年度岡崎市一般会計予算』, submitted to the March 2026 regular session, referred to the Budget and Settlement Committee and voted on 2026-03-23, the session's final day, per the official session agendas (議事日程第1号・議案付託表・議事日程第4号); the March 2026 session's voting-results list itself was not retrieved, so the exact 'passed as proposed' (原案可決) wording is not asserted — enactment is corroborated by the published enacted-budget overview and by the FY2026 supplementary budgets (No. 1 at the same session and Nos. 2–3 at the June 2026 session) that presuppose the initial budget). The amount is published at sen-yen (thousand-yen) precision, so it is kept at that precision and yen-precision amounts are not synthesized
- FY2024 general-account settlement at yen precision as published: revenue 157,798,763,028 yen / expenditure 148,542,565,874 yen (the balance of 9,256,197,154 yen matches the published balance in the official settlement overview, whose summary table and account-level table agree, and the real balance (純剰余金) of 6,459,331,285 yen after deducting carryover funding of 2,796,865,869 yen also checks out). The settlement certification bill, certification bill No. 1 『令和6年度岡崎市一般・特別会計の決算の認定について』, was certified on 2025-09-30 at the September 2025 regular session per the council's official voting-results list (it was not rejected). FY2024 is a settlement of the Future Investment Plan's first period (FY2021–FY2025), a different plan version from the latter plan, so the totals are not linked to the latter plan's initiatives or packages and the linkage stays not_assessable

Deferred depth includes the Future Investment Packages' project lists under the 54 main initiatives, the group-level reference indicators' individual values, cross-checks against the budget book and the settlement book (事項別明細書) at section level, direct confirmation of the 'passed as proposed' wording from the March 2026 session's voting-results list, the audit commissioners' settlement review opinion, the first period's framework itself, supplementary-budget history, fiscal project detail, causality and cross-city comparability.

## Thirty-second completion — Ichinomiya

一宮市を32番目の`reviewed_complete`へ昇格しました（2026-11-16、所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

Declared v1 package:

- current plan: 第7次一宮市総合計画 — a three-layer structure of basic concept (FY2018–FY2027; future city image 『木曽の清流に映え、心ふれあう躍動都市 一宮』; five plans and two managements), basic plan (first period FY2018–FY2022 / latter period FY2023–FY2027, the latter being the current plan) and implementation plans (three-year rolling, with the final edition covering FY2026–FY2027 to match the plan's end); the latter basic plan's structure holds seven groups (プラン1 健やかにいきる／プラン2 快適にくらす／プラン3 安全・安心を高める／プラン4 活力を生みだす／プラン5 未来の人財を育てる／マネジメント1 人を呼び込む／マネジメント2 持続可能で未来につなげる) and 35 policies (all 35 are enumerated); progress is managed through administrative evaluation PDCA, combining outcome indicators (grades A–D) and citizen perception indicators (grades a–d) into 16-grade policy evaluations plus project evaluations (necessity, effectiveness, efficiency) — the municipality's self-evaluation framework. The transition to the Eighth Comprehensive Plan (under preparation) is kept only as a version chronology record
- FY2026 general-account initial budget: 146,740,000 thousand yen (enacted; mayoral bill No. 3 『令和8年度愛知県一宮市一般会計予算』, submitted to the March 2026 regular session, referred to four committees and passed on 2026-03-23 per the city's official split-vote list (賛否の分かれた議案等) and the session agenda; the city's published result wording is 'passed' (可決), so the exact 'passed as proposed' (原案可決) wording is not asserted). The amount is published at sen-yen (thousand-yen) precision, so it is kept at that precision and yen-precision amounts are not synthesized
- FY2024 general-account settlement at yen precision as published: revenue 150,057,354,584 yen / expenditure 143,608,246,738 yen (the balance of 6,449,107,846 yen matches the published balance in the official settlement book, whose summary table and general-account statement agree; the real balance is 6,207,237 thousand yen per the settlement book's real-balance statement (実質収支に関する調書), kept at that statement's sen-yen precision with rounding, never expanded into synthetic yen). The settlement certification bill, certification bill No. 4 『令和6年度愛知県一宮市一般会計歳入歳出決算の認定について』, was certified on 2025-12-01 at the December 2025 regular session per the council's official bill-and-result list (it was not rejected). FY2024 is a settlement inside the latter basic plan period (FY2023–FY2027), the same plan version, but no official total-level mapping from settlement totals to the plan's policies or indicators exists, so the totals are not linked to the plan's policies and the linkage stays not_assessable

Deferred depth includes the implementation-plan projects under the 35 policies, the per-policy outcome and citizen-perception indicator values, cross-checks against the budget book and the settlement book (事項別明細書) at section level, direct confirmation of the vote from the March 2026 session's final-day minutes, the audit commissioners' settlement review opinion, the Eighth Plan's framework itself, supplementary-budget history, fiscal project detail, causality and cross-city comparability.

## Thirty-third completion — Toyota

豊田市を33番目の`reviewed_complete`へ昇格しました（2026-11-16、所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

Declared v1 package:

- current plan: 第9次豊田市総合計画 — a two-layer structure of the Mirai Concept (ミライ構想; a long-term direction looking ahead to 2050, future image 『つながる つくる 暮らし楽しむまち・とよた』, basic approaches to town-building, and a hub-linked future city structure) and the Mirai Realization Strategy 2030 (ミライ実現戦略2030; FY2025–FY2029), which sets two action principles (ともにこどものミライに夢と希望をつくる／ともにミライにつながるまちをつくる), five action goals and twelve target states holding 30 policies (all 30 are enumerated; the policies are as adopted and are revised as annual progress and socioeconomic conditions change); progress is managed through annual rolling (policy rolling and project rolling feeding budget compilation), with results published alongside the initial budget compilation and the year's main initiatives published as annual policy project collections (施策別事業集) — the municipality's own progress-management framework. The transition from the Eighth Comprehensive Plan is kept only as a version chronology record
- FY2026 general-account initial budget: 211,800,000 thousand yen (enacted; bill No. 45 『令和8年度豊田市一般会計予算』, submitted by Mayor 太田稔彦 on 2026-02-20, referred to the Budget and Settlement Committee and passed as proposed (原案可決) on 2026-03-18 per the council's official voting-result table for the March 2026 regular session; in that table the result and date cells for bill No. 45 use the ditto mark (〃), resolving to the table's explicit first entry (bill No. 5: passed as proposed, 2026-03-18), and that reading is recorded explicitly). The amount is published at sen-yen (thousand-yen) precision, so it is kept at that precision and yen-precision amounts are not synthesized
- FY2024 general-account settlement at yen precision as published: revenue 246,602,084,906 yen / expenditure 229,543,452,176 yen (the balance of 17,058,632,730 yen matches the published balance in the official settlement book published by the city as open data, and both totals are consistent with the audit committee's sen-yen figures; the real balance is 8,192,990 thousand yen per the audit committee's settlement review opinion (豊監発第393号, 2025-08-21), kept at that opinion's sen-yen precision, never expanded into synthetic yen; the real-balance statement (実質収支に関する調書) itself has not been directly confirmed). The settlement certification bill, approval bill No. 4 (令和7年承認第4号) 『令和6年度豊田市一般会計決算』, was certified on 2025-09-24 at the September 2025 regular session per the council's official voting-result table (it was not rejected). FY2024 is a settlement of the Eighth Comprehensive Plan period, a different plan version from the current Ninth Plan, and no official total-level mapping from settlement totals to the strategy's goals or policies exists, so the totals are not linked to the plan's policies and the linkage stays not_assessable

Deferred depth includes the individual projects in the annual policy project collections under the 30 policies, the per-target-state indicator values, cross-checks against the budget book and the settlement book (事項別明細書) at section level, direct confirmation of the vote from the March 2026 session's minutes (including the reading of the ditto-mark cells), direct confirmation of the real-balance statement itself, the Eighth Plan's framework itself, supplementary-budget history, fiscal project detail, causality and cross-city comparability.

## Thirty-fourth completion — Tsu

津市を34番目の`reviewed_complete`へ昇格しました（2026-11-16、所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

Declared v1 package:

- current plan: 津市総合計画 — a two-layer structure of the Basic Concept (基本構想; the basic philosophy of town-building, showing the desired city image and the future image 『笑顔があふれ幸せに暮らせる県都 津市 ～夢や希望、明るい未来が広がるまちへ～』 with six town-building outlines, for which no fixed plan period is set — that absence of a fixed period is kept as published and is not collapsed into a fixed-period model) and the Second Basic Plan (第2次基本計画; FY2018–FY2027), which sets six goals corresponding to the Basic Concept's outlines plus the cross-cutting block 『将来像の実現に向けて』, holding 19 basic policies and 53 policies (all 53 are enumerated); progress is managed through project evaluation and policy evaluation (事務事業評価・施策評価), with results published annually as the 『津市総合計画第2次基本計画事務事業評価・施策評価報告書』 — the municipality's own progress-management framework. The transition from the preceding plans (基本構想・前期基本計画／後期基本計画) and the formulation of the next Tsu City Comprehensive Plan are kept only as version chronology records
- FY2026 general-account initial budget: 124,187,000 thousand yen (enacted; bill No. 39 『令和8年度津市一般会計予算』, submitted by Mayor 前葉泰幸 on 2026-02-27, referred by jurisdiction to the standing committees and passed as proposed (原案可決) on 2026-03-26 per the council's official voting-result table for the first regular session of 2026, with the plenary minutes of 2026-03-26 also directly recording that it was passed as proposed by majority vote). The amount is published at sen-yen (thousand-yen) precision, so it is kept at that precision and yen-precision amounts are not synthesized
- FY2024 general-account settlement at yen precision as published: revenue 123,307,646,176 yen / expenditure 122,840,878,576 yen (the balance of 466,767,600 yen matches the balance recorded in the settlement appendix's real-balance statement (実質収支に関する調書); the real balance is 175,738,909 yen per that same statement, kept at yen precision exactly as published because the statement itself is published in yen). The settlement certification bill, certification bill No. 1 (認定第1号) 『令和6年度津市一般会計歳入歳出決算』, was certified on 2025-09-25 at the third regular session of 2025 per the council's official voting-result table (it was not rejected). FY2024 is a settlement inside the Second Basic Plan period, so the plan version is the same as the current plan, but no official total-level mapping from settlement totals to the plan's goals, basic policies or policies exists, so the totals are not linked to the plan's policies and the linkage stays not_assessable

Deferred depth includes the individual projects under the 53 policies in the project evaluation, the per-policy indicator values, cross-checks against the budget book and the settlement book (事項別明細書) at section level, the contents of the audit commissioners' settlement review opinion, the preceding plans' frameworks themselves and the next plan's framework, supplementary-budget history, fiscal project detail, causality and cross-city comparability.

## Thirty-fifth completion — Otsu

大津市を35番目の`reviewed_complete`へ昇格しました（2026-11-16、所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

Declared v1 package:

- current plan: 大津市総合計画 — a two-layer structure of the Basic Concept (基本構想; FY2017–FY2028, showing the future city image 『ひと、自然、歴史の縁で織りなす 住み続けたいまち“大津再生” ～コンパクトで持続可能なまちへの変革～』 and three basic principles (まちづくりの基本理念)) and the Action Plans that divide the Basic Concept's twelve years into three four-year terms, the current one being the Third Action Plan (第3期実行計画; FY2025–FY2028), which sets three basic directions holding 13 basic policies and 32 measures (all 32 are enumerated); progress is managed through administrative evaluation (行政評価: comprehensive-plan progress management and project evaluation), with results published annually as administrative evaluation reports — the municipality's own progress-management framework. The succession from the First Action Plan (FY2017–FY2020) and the Second Action Plan (FY2021–FY2024) to the Third Action Plan is kept only as version chronology records, and the status of the next comprehensive plan after the Basic Concept period (ending FY2028) is left unconfirmed
- FY2026 general-account initial budget: 142,684,000 thousand yen (enacted; bill No. 3 『令和8年度大津市一般会計予算』, submitted by Mayor 佐藤健司 on 2026-02-19, referred to the Budget and Settlement Standing Committee and passed on 2026-03-25 per the council's official bill-result list (『議案の一覧・結果（令和7年度）』). The list's published result wording is only "可決（多数）" and does not state "原案可決", so that wording is not asserted and stays unconfirmed (direct confirmation in the plenary minutes has not been made). The amount is published at sen-yen (thousand-yen) precision, so it is kept at that precision and yen-precision amounts are not synthesized
- FY2024 general-account settlement at yen precision as published: revenue 146,909,564,029 yen / expenditure 143,932,903,895 yen (the balance of 2,976,660,134 yen matches the balance printed in the official settlement book; the real balance is 2,791,920 thousand yen per the audit commissioners' settlement review opinion summary, kept at sen-yen precision because that opinion is published in thousand yen — the yen value in the real-balance statement itself stays unconfirmed). The settlement certification bill, bill No. 110 (議案第110号) 『令和6年度大津市一般会計の決算の認定について』, was certified on 2025-10-28 per the council's official bill-result list (it was not rejected). FY2024 is the final-year settlement of the Second Action Plan (FY2021–FY2024), so the plan version differs from the current Third Action Plan, and no official total-level mapping from settlement totals to the plan's basic directions, basic policies or measures exists, so the totals are not linked to the plan's measures and the linkage stays not_assessable

Deferred depth includes the individual projects under the 32 measures in the project evaluation, the per-measure outcome indicator values, cross-checks against the budget book and the settlement book (事項別明細書) at section level, direct confirmation of the yen value in the real-balance statement itself, direct confirmation of the "原案可決" wording for bill No. 3 in the plenary minutes, the First and Second Action Plans' frameworks themselves, the next comprehensive plan, supplementary-budget history, fiscal project detail, causality and cross-city comparability.

## Thirty-sixth completion — Toyonaka

豊中市を36番目の`reviewed_complete`へ昇格しました（2026-11-16、所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

Declared v1 package:

- current plan: 第4次豊中市総合計画 — the city's top-level plan under the Toyonaka City Basic Autonomy Ordinance, in a three-layer structure of basic concept （基本構想）, basic plan （基本計画） and implementation plan （実施計画）. The basic concept runs FY2018–FY2027 and shows the future city image 『みらい創造都市 とよなか ～明日がもっと楽しみなまち～』 with the policy outline （施策大綱） for its realization. The basic plan is split into a first period (FY2018–FY2022) and the current latter basic plan (FY2023–FY2027), which sets five chapters holding 16 measures (all 16 are enumerated) plus the leading project （南部地域活性化プロジェクト）, kept outside the measure count; the implementation plan is provided through the digital budget book from FY2024 onward; progress is managed through policy evaluation （政策評価： the 16 measures and the leading project are evaluated every year on two axes — progress and content — with results published in the digital budget book and the policy evaluation result summaries) — the municipality's own progress-management framework. The succession from the first basic plan (FY2018–FY2022, 17 measures) to the latter basic plan is kept only as version chronology records, and the status of the next comprehensive plan after the basic concept period (ending FY2027) is left unconfirmed
- FY2026 general-account initial budget: 206,946,719 thousand yen (enacted; bill 市議案第8号 『令和8年度豊中市一般会計予算』, submitted by Mayor 長内繁樹 on 2026-02-24 and passed as proposed （原案可決） on 2026-03-23 per the council's official voting-results list (『議決結果（令和8年（2026年）3月定例会）』), whose published wording states 原案可決）. The amount is published at sen-yen (thousand-yen) precision, so it is kept at that precision and yen-precision amounts are not synthesized
- FY2024 general-account settlement at yen precision as published: revenue 197,263,021,788 yen / expenditure 191,790,466,590 yen (the balance of 5,472,555,198 yen matches the balance printed in the official settlement book; the real balance is 4,930,077 thousand yen per the real-balance statement itself, kept at sen-yen precision because that statement is published in thousand yen with rounding adjustments). The settlement certification bill, bill 市議案第74号 『令和6年度大阪府豊中市各経済歳入歳出決算認定について』 (covering the general account and the other accounts), was submitted to the September 2025 regular session, went through continued review, and was voted NOT certified （不認定） on 2025-11-28 at the December 2025 regular session per the council's official voting-results list — that outcome is recorded exactly as published and is never rewritten as a certification. FY2024 is a settlement inside the latter basic plan period (its second year), so the plan version is the same as the current plan, but no official total-level mapping from settlement totals to the plan's 16 measures or the leading project exists, so the totals are not linked to the plan's measures and the linkage stays not_assessable

Deferred depth includes the individual projects under the 16 measures, the per-measure outcome indicator values, the leading project's project breakdown, cross-checks against the budget explanation book and the settlement book （事項別明細書） at section level, the content of the mayor's measures in response to the non-certification (Local Autonomy Act Article 233(7)) and of any report to the council, the first basic plan's framework itself, the next comprehensive plan, supplementary-budget history, fiscal project detail, causality and cross-city comparability.

## Thirty-seventh completion — Suita

吹田市を37番目の`reviewed_complete`へ昇格しました（2026-11-16、所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

Declared v1 package:

- current plan: 第4次吹田市総合計画 — in a three-layer structure of basic concept （基本構想）, basic plan （基本計画） and implementation plan （実施計画）. The basic concept and the basic plan both run FY2019–FY2028; the basic concept shows the future image in its closing passage 『だれもが安心してすこやかで快適に暮らし続けられるまち』 (no fixed-form vision title exists). The basic plan was revised at a mid-term review in March 2024 into the current revised basic plan (FY2024–FY2028, with the second-phase Machi-Hito-Shigoto creation strategy bound in), which sets eight outlines （大綱） holding 19 policies and 52 measures (all 52 are enumerated); cross-field perspectives （取組の視点） printed on the framework chart are kept outside the measure count; the implementation plan is a five-year rolling plan and the current one (FY2026–FY2030) extends beyond the comprehensive plan's final year (FY2028), a period gap kept as structure; progress is managed through a PDCA cycle (administrative evaluation （行政評価） using policy indicators and a citizen-awareness survey held basically every four years, with each fiscal year's progress published on the official progress page) — the municipality's own progress-management framework. The succession from the original basic plan to the revised basic plan is kept only as version chronology records, and the status of the next (fifth) comprehensive plan after the fourth plan period (ending FY2028) is left unconfirmed
- FY2026 general-account initial budget: 181,996,567 thousand yen (enacted; bill 議案第19号 『令和8年度吹田市一般会計予算』, submitted by Mayor 後藤圭二 on 2026-02-18 and passed as proposed （原案可決） at the February 2026 regular session per the council's official voting-results and vote-split list (『令和8年(2026年)2月定例会議決結果・賛否一覧表』, 23 to 9), whose published wording states 原案可決）. The voting date (2026-03-24) was identified from the council's official session schedule — the final day's plenary was the only one holding debate and voting — and has not been finally confirmed in the plenary minutes. The amount is published at sen-yen (thousand-yen) precision, so it is kept at that precision and yen-precision amounts are not synthesized
- FY2024 general-account settlement at yen precision as published: revenue 179,335,489,298 yen / expenditure 178,490,836,452 yen (the balance of 844,652,846 yen is consistent with the formal balance of 844,653 thousand yen published in the official report; the real balance is 259,882 thousand yen per that report, kept at sen-yen precision because the report is published in thousand yen; the report also records a 1,900,000 thousand yen transfer from the fiscal adjustment fund to keep the real balance in surplus). The settlement certification bill, bill 認定第1号 『令和6年度吹田市一般会計歳入歳出決算認定について』, was submitted to the September 2025 regular session, referred to the settlement standing committee, went through continued review, and was certified at the November 2025 regular session per the council's official voting-results and vote-split list (24 to 9); the voting date (2025-12-22) was likewise identified from the council's official session schedule and has not been finally confirmed in the plenary minutes. FY2024 is the first year of the revised basic plan, so the plan version is the same as the current plan, but no official total-level mapping from settlement totals to the plan's 19 policies or 52 measures exists, so the totals are not linked to the plan's policies or measures and the linkage stays not_assessable

Deferred depth includes the individual projects under the 52 measures, the per-measure policy indicator values, the citizen-awareness indicator values, final confirmation of both voting dates in the plenary minutes, cross-checks against the budget book and the settlement book （事項別明細書） at section level, the content of the audit commissioners' settlement review opinion, the original basic plan's framework itself, the next comprehensive plan, supplementary-budget history, fiscal project detail, causality and cross-city comparability.

## Thirty-eighth completion — Takatsuki

高槻市を38番目の`reviewed_complete`へ昇格しました（2026-11-16、所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

Declared v1 package:

- current plan: 第6次高槻市総合計画 — in a two-layer structure of basic concept （基本構想） and basic plan （基本計画）. The basic concept starts in FY2021 with target year FY2030, presenting eight future city images （将来の都市像） and the town-building motto 『輝く未来を創造する 関西の中央都市 高槻』; the basic plan sets eight fields corresponding to those images, holding 29 measures and 139 measure directions (all 29 measures and all 139 directions are enumerated). Fiscal and administrative management during the plan period follows a separately prepared implementation plan (three-year rolling, renewed every year; the current edition covers FY2026–FY2028), and progress is managed around that implementation plan, with each major project undergoing a retrospective evaluation （実績の振り返り（評価）) before the following years' plan is set — the municipality's own progress-management framework. The succession from the Fifth Takatsuki City Comprehensive Plan (Takatsuki City Comprehensive Strategy Plan, FY2010–FY2020) is kept only as version chronology records, and the status of the next comprehensive plan after the Sixth Plan period (ending FY2030) is left unconfirmed
- FY2026 general-account initial budget: 151,189,961 thousand yen (enacted; bill 議案第32号 『令和8年度高槻市一般会計予算』, submitted by Mayor 濱田剛史 on 2026-02-25 and passed as proposed （原案可決） at the March 2026 regular session per the council's official voting-results document (『令和8年第1回定例会（3月定例会）の議決結果』 （付議事件と議決てんまつ）), with both the published wording and the voting date (2026-03-23) confirmed directly in that document rather than inferred from the session schedule). The amount is published at sen-yen (thousand-yen) precision, so it is kept at that precision and yen-precision amounts are not synthesized
- FY2024 general-account settlement at yen precision as published: revenue 147,928,131,915 yen / expenditure 142,805,684,915 yen (their difference of 5,122,447,000 yen matches the balance printed in the official settlement book; the real balance is 3,523,157 thousand yen per the real-balance statement, kept at sen-yen precision because that statement is published in thousand yen; the fund transfer under Local Autonomy Act Article 233-2 is zero). The settlement certification bill, bill 認定第1号 『令和6年度高槻市一般会計歳入歳出決算認定について』, was submitted to the September 2025 regular session, placed under continued review on 2025-09-08, and certified at the December 2025 regular session on 2025-12-03 per the council's official voting-results documents. FY2024 is a settlement inside the Sixth Plan period, so the plan version is the same as the current plan, but no official total-level mapping from settlement totals to the plan's eight fields or 29 measures exists, so the totals are not linked to the plan's fields or measures and the linkage stays not_assessable

Deferred depth includes the individual major projects under the 29 measures and 139 measure directions, the per-measure indicator values, cross-checks against the budget book and the settlement book （事項別明細書） at section level, the content of the audit commissioners' settlement review opinion, the Fifth Plan's framework itself, the next comprehensive plan, supplementary-budget history, fiscal project detail, causality and cross-city comparability.

## Thirty-ninth completion — Hirakata

枚方市を39番目の`reviewed_complete`へ昇格しました（2026-11-16、所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

Declared v1 package:

- current plan: 第5次枚方市総合計画 — in a three-layer structure of basic concept （基本構想）, basic plan （基本計画） and action plan （実行計画）. The basic concept starts in FY2016 and sets no fixed plan period, presenting the future image 『持続的に発展し、一人ひとりが輝くまち 枚方』 and five basic goals; the basic plan covers FY2016-FY2027 (twelve years); the action plan runs in four-year periods (the current Third Action Plan covers FY2024-FY2027). The basic plan and the Third Action Plan hold 28 policy goals and four plan-promotion units (32 policy-goal units in total) under the five basic goals, with 79 policies in total (all 32 policy-goal units and all 79 policies are enumerated). Progress is managed around the action plan: each year the municipality verifies and evaluates the action plan using the results of concrete initiatives, indicators and citizen satisfaction captured through subjective indicators (internal evaluation plus external evaluation by policy evaluators), and the Third Action Plan is revised at budget-compilation time, while the basic plan is verified and evaluated on a four-year PDCA cycle — the municipality's own progress-management framework. The transition to the next comprehensive plan (starting FY2028, now being formulated, which keeps the Fifth Plan's basic concept as its base and revises the basic plan) is kept only as a version chronology record, and the current plan's content is never connected forward into the next plan period
- FY2026 general-account initial budget: 176,300,000 thousand yen (enacted; bill 議案第84号 『令和8年度大阪府枚方市一般会計予算』, referred to the budget special committee at the March 2026 regular session on its first day (2026-02-24) and passed as proposed （原案可決） on the fifth day (2026-03-27) per the council's official voting-results list (『付議事件議決結果一覧』), with both the published wording and the voting date confirmed directly in that document rather than inferred from the session schedule). The amount is published at sen-yen (thousand-yen) precision, so it is kept at that precision and yen-precision amounts are not synthesized
- FY2024 general-account settlement at yen precision as published: revenue 167,040,111,596 yen / expenditure 164,593,615,013 yen (their difference of 2,446,496,583 yen matches the balance printed in the official settlement book; the real balance is 1,938,746,472 yen per the settlement summary document （決算概要説明書）, kept at yen precision because that document publishes it in yen; the real-balance statement page in the settlement book itself could not be read because its fonts are not embedded, so direct confirmation of that statement itself remains unconfirmed). The settlement certification bill, bill 認定第1号 『令和6年度大阪府枚方市一般会計歳入歳出決算の認定について』, was referred to the settlement special committee on the first day of the September 2025 regular session (2025-09-05) and certified on the seventh day (2025-10-17) per the council's official voting-results list. FY2024 is a settlement inside the basic plan period and is the first year of the Third Action Plan, so the plan version is the same as the current plan, but no official total-level mapping from settlement totals to the plan's 28 policy goals or 79 policies exists, so the totals are not linked to the plan's policy goals or policies and the linkage stays not_assessable

Deferred depth includes the individual projects under the 32 policy-goal units and 79 policies, the per-policy indicator values (subjective and objective indicators), cross-checks against the budget book and the settlement book （事項別明細書） at section level, the content of the audit commissioners' settlement review opinion, direct confirmation of the real-balance statement itself in the settlement book, the next comprehensive plan's framework itself, supplementary-budget history, fiscal project detail, causality and cross-city comparability.

## Fortieth completion — Yao

八尾市を40番目の`reviewed_complete`へ昇格しました（2026-11-16、所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

Declared v1 package:

- current plan: 第6次八尾市総合計画『八尾新時代しあわせ成長プラン』 — in a three-layer structure of basic concept （基本構想）, basic plan （基本計画） and implementation plan （実施計画） established under the Yao City Comprehensive Plan Establishment Ordinance, with the basic concept and the basic plan enacted by council vote. The basic concept covers FY2021-FY2028 (eight years), presenting the future city image 『つながり、かがやき、しあわせつづく、成長都市 八尾』, six town-development goals with their policy directions, and the town-development promotion measures; the basic plan splits the eight years into an earlier period (FY2021-FY2024) and a latter period (FY2025-FY2028) of four years each, the current version being the latter basic plan; the implementation plan is reviewed every fiscal year. The latter basic plan's measure structure is a matrix: its 33 measures relate to the six goals in 83 goal-measure links in total (all 33 measures and all 83 links are enumerated); the earlier basic plan's measure 16 『上水道の安定供給』 was removed from the latter plan's structure and the number left vacant when the waterworks was integrated into the Osaka Wide-Area Waterworks Enterprise Group in April 2025. Progress is managed through administrative evaluation under Article 13 of the Citizen Participation and Collaboration Town-Development Basic Ordinance (measure evaluation via implementation plan documents and implementation plan result documents; project evaluation from the viewpoints of appropriateness, effectiveness and efficiency) — the municipality's own progress-management framework. The transition from the earlier basic plan to the latter basic plan within the Sixth Plan is kept only as a version chronology record, and results from the earlier period are never connected forward into the latter period
- FY2026 general-account initial budget: 132,613,637 thousand yen (enacted; bill 議案第18号 『令和8年度八尾市一般会計予算の件』, passed as proposed （原案可決） on 2026-03-27 at the February 2026 regular session per the council's official voting results (『2026年2月市議会定例会 議決結果』), with both the published wording and the voting date confirmed directly in that document rather than inferred from the session schedule). The amount is published at sen-yen (thousand-yen) precision, so it is kept at that precision and yen-precision amounts are not synthesized
- FY2024 general-account settlement at yen precision as published: revenue 126,116,660,528 yen / expenditure 123,882,040,366 yen (their difference of 2,234,620,162 yen matches the balance printed in the real-balance statement of the official settlement book; the real balance is 1,797,799,491 yen, kept at yen precision as directly confirmed in that statement itself). The settlement certification bill, bill 認定第1号, was certified on 2025-10-22 at the September 2025 regular session per the council's official voting results; discussion-count tallies in public-relations materials are not voting results and were not used to confirm the general-account certification. FY2024 is a settlement of the earlier basic plan period (FY2021-FY2024), so its plan version differs from the current latter basic plan, and no official total-level mapping from settlement totals to the plan's measures exists, so the totals are not linked to the plan's measures and the linkage stays not_assessable

Deferred depth includes the individual projects under the 33 measures, the per-measure indicator values, cross-checks against the budget book and the settlement book （事項別明細書） at section level, the content of the audit commissioners' settlement review opinion, the earlier basic plan's full measure structure, supplementary-budget history, fiscal project detail, causality and cross-city comparability.

## Forty-first completion — Neyagawa

寝屋川市を41番目の`reviewed_complete`へ昇格しました（2026-11-16、所有者・大杉邑大が2026-11-15にチャットで『レビューはあなたがやってください。それで大丈夫です』と明示してレビューをClaudeへ委任し、Claudeが一次資料で検証したことに基づく。所有者本人が一次資料を直接レビューしたものではない）。

Declared v1 package:

- current plan: 第六次寝屋川市総合計画 — integrated with the Second Neyagawa City まち・ひと・しごと創生総合戦略， structured as a basic strategy （基本戦略 = 基本構想 plus 戦略プラン） and an implementation plan （実施計画）. The basic strategy covers FY2021-FY2027 (seven years), presenting the future image 『新たな価値を創り、選ばれるまち 寝屋川 ～イノベーションの創出～』; the implementation plan splits into an earlier period (FY2021-FY2023, three years) and a latter period (FY2024-FY2027, four years), the current version being the latter implementation plan (FY2026 edition). The strategic plan's 19 measures are grouped into the three key factors' nine appeal measures （訴求力のある施策）, four life-supporting measures （生活を支える施策） and six quality-of-life measures （くらしの質を高める施策）, all enumerated; the latter implementation plan lists 74 developments （施策の展開） under the measures, each with projects （取組）, leading projects and progress-management indicators. Progress is managed by integrating the plan's progress management with administrative evaluation based on the PDCI cycle (Plan・Do・Check・Innovation) — the municipality's own progress-management framework. The transition from the earlier implementation plan to the latter implementation plan within the Sixth Plan is kept only as a version chronology record, and results from the earlier period are never connected forward into the latter period; the status of the next (Seventh) comprehensive plan is unconfirmed
- FY2026 general-account initial budget: 109,730,000 thousand yen as published (1,097億3,000万円; enacted; bill 議案第28号 『令和8年度寝屋川市一般会計予算』, submitted on 2026-02-24 and passed as proposed （原案可決） on 2026-03-25 at the March 2026 regular session per the council's official list of submitted items (『令和8年3月市議会定例会 付議事件一覧表』), with the bill number, the published wording and the voting date confirmed directly in that document rather than inferred from the session schedule). The city's published amount is at man-yen (ten-thousand-yen) precision, so it is kept at that precision and finer amounts are not synthesized; the exact sen-yen-precision total in the initial budget book remains unconfirmed
- FY2024 general-account settlement at sen-yen (thousand-yen) precision as published: revenue 106,597,604 thousand yen / expenditure 105,333,971 thousand yen (their difference of 1,263,633 thousand yen matches the balance printed in the real-balance statement （実質収支に関する調書） of the official settlement book and the figures in the September 2025 reference materials; the real balance is 1,248,678 thousand yen, kept at sen-yen precision as confirmed in that statement itself). The settlement certification bill, bill 認定第1号, was submitted to the September 2025 regular session, referred to the Budget and Settlement Standing Committee and kept under continued review during recess, and was certified on 2025-12-03 at the December 2025 regular session per the council's official lists of submitted items. FY2024 is the first year of the latter implementation plan (FY2024-FY2027), so its plan version is the same as the current one, but no official total-level mapping from settlement totals to the plan's measures or developments exists, so the totals are not linked to the plan's measures and the linkage stays not_assessable

Deferred depth includes the 74 developments and individual projects under the 19 measures, the per-measure indicator values (measure indicators and progress-management indicators), the exact sen-yen-precision FY2026 initial budget total, cross-checks against the budget book and the settlement book （事項別明細書） at section level, the content of the audit commissioners' settlement review opinion, the status of the next (Seventh) comprehensive plan, supplementary-budget history, fiscal project detail, causality and cross-city comparability.

## Current queue

- Reviewed complete: 41 / 67 — 函館市、旭川市、青森市、八戸市、盛岡市、秋田市、山形市、福島市、郡山市、いわき市、水戸市、宇都宮市、前橋市、高崎市、川越市、川口市、越谷市、船橋市、柏市、新宿区、八王子市、横須賀市、富山市、金沢市、福井市、甲府市、長野市、松本市、岐阜市、豊橋市、岡崎市、一宮市、豊田市、津市、大津市、豊中市、吹田市、高槻市、枚方市、八尾市、寝屋川市
- Review in progress: 0
- Pending record review: 26
- Blocked source inventory: 0
- Next official code: 272272

## Definition of Phase 15 completion

Phase 15 is complete only when:

- all 67 queue records are `reviewed_complete`
- no municipality remains `review_in_progress` or `pending_record_review`
- every completed municipality has a valid Phase 15 completion contract
- all referenced review-package files exist
- all reviewed fiscal records and Evidence packets validate
- all deferred evidence remains explicit
- independent policy-achievement, causal-attribution and unverified cross-city ranking counts remain zero
- final repository/data validation, regression tests, web checks and Production Smoke pass on the merged head
