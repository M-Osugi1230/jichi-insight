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

## Current queue

- Reviewed complete: 24 / 67 — 函館市、旭川市、青森市、八戸市、盛岡市、秋田市、山形市、福島市、郡山市、いわき市、水戸市、宇都宮市、前橋市、高崎市、川越市、川口市、越谷市、船橋市、柏市、新宿区、八王子市、横須賀市、富山市、金沢市
- Review in progress: 0
- Pending record review: 43
- Blocked source inventory: 0
- Next official code: 182010

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
