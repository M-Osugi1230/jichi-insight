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

## Current queue

- Reviewed complete: 4 / 67 — 函館市、旭川市、青森市、八戸市
- Review in progress: 1 — 盛岡市
- Pending record review: 62
- Blocked source inventory: 0
- Next official code: 032018

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
