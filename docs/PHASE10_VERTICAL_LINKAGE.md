# Phase 10 — Nationwide uniform depth

Phase 10 brings all 47 prefectures to the same minimum information depth. Phase 9 completed Evidence-backed Reviewed target statements nationwide. Phase 10 connects those targets to delivery and accountability evidence without pretending that a source entrance is already a verified linkage.

```text
Reviewed target statement
→ annual actual
→ budget
→ settlement
→ priority project
→ contract / procurement
→ assembly explanation
→ audit finding
→ executive manifesto
→ publication verification
```

Phase 10 does not create an independent policy score. An increase in a value, the existence of a budget, or the execution of a project is not by itself evidence that a policy succeeded.

## Canonical machine-readable state

- `data/catalog/phase10_uniformity.json`
- `data/catalog/phase10_execution_queue.json`
- `data/catalog/phase10_completion.json`
- `data/catalog/phase10_regional_depth_index.json`
- `data/catalog/phase10_reference_depth_reviews.json`
- `data/catalog/phase10_anchor_depth_reviews.json`
- `data/catalog/phase10_tohoku_depth_reviews.json`
- `data/catalog/phase10_kanto_depth_reviews.json`
- `data/catalog/phase10_chubu_depth_reviews.json`
- `data/catalog/phase10_kinki_depth_reviews.json`
- `data/catalog/phase10_chugoku_depth_reviews.json`
- `data/catalog/phase10_shikoku_depth_reviews.json`
- `data/catalog/phase10_kyushu_depth_reviews.json`
- `schemas/phase10_uniformity.schema.json`
- `schemas/phase10_regional_depth_index.schema.json`
- `schemas/phase10_regional_depth_reviews.schema.json`

`phase10_uniformity.json` stores the eleven-dimension baseline and reference-specific overrides. The completed regional index overlays the 38 non-anchor prefectures from the seven regional registries. Together with the nine reference and anchor prefectures, the public matrix covers all 47 without duplicating the same state in multiple files.

Every source review preserves:

- official source title and URL;
- official owner;
- reporting or measurement period;
- the claim supported by the source;
- the boundary that remains unresolved;
- the next linkage action.

## Uniform dimensions

| Dimension | Phase 10 completion requirement |
| --- | --- |
| Policy targets and KPI | `reviewed` or better |
| Evidence Packet | `reviewed` or better |
| Annual actuals | `linked` |
| Budget | `linked` |
| Settlement | `linked` |
| Priority projects | `linked` |
| Contracts and procurement | `linked` |
| Assembly explanation | `linked` |
| Audit | `linked` |
| Executive manifesto | `linked` |
| Publication verification | `reviewed` or better |

A prefecture is not complete because one policy is deeply linked. It is complete only when the agreed publication scope for every dimension passes the same gate and unsupported relationships remain explicitly unresolved.

## Status vocabulary

- `not_indexed`: no official entrance has been fixed in the catalog.
- `indexed`: an official source entrance has been confirmed.
- `reviewed`: contents, period, scope, and evidence location have been checked.
- `linked`: the downstream record has been definition-checked against the same target, policy, project, or term.

Source state and linkage state remain different. A budget page can be `reviewed` while no budget line is yet linked to a target.

## Current verified depth on 2026-08-01

Nationwide baseline:

- Reviewed target statements: 47 / 47
- Reviewed Evidence Packet coverage: 47 / 47
- Publication verification baseline: 47 / 47
- five delivery-evidence layers indexed or better: 47 / 47
- all five delivery-evidence layers Reviewed: 46 / 47
- prefectures passing the complete eleven-dimension gate: 0 / 47

Five-layer source-review depth:

- annual actuals Reviewed or better: 47 / 47
  - Miyagi is `linked`
- budget Reviewed or better: 47 / 47
- settlement Reviewed or better: 46 / 47
  - Miyagi remains `indexed`
- priority projects Reviewed or better: 47 / 47
- audit Reviewed or better: 47 / 47

Accountability and target-level linkage remain substantially shallower:

- contract entrances indexed: 2 / 47
- assembly evidence indexed: 2 / 47
- executive-manifesto evidence indexed: 1 / 47
- complete eleven-dimension records: 0 / 47

The five-layer nationwide review is a source-coverage milestone, not Phase 10 completion. New-plan first years, older-plan evaluations, in-year monitoring, latest-available prior settlements, and evaluation-framework-only sources remain explicitly bounded in the registries.

## Completed source-review batches

### Reference implementations

- Miyagi: annual actual linkage reference; settlement remains Indexed.
- Fukuoka: finance and settlement review reference.

### Seven regional anchors

Hokkaido, Tokyo, Aichi, Osaka, Hiroshima, Kagawa, and Okinawa have Reviewed annual-actual, budget, settlement, priority-project, and audit sources.

### Seven regional registries

- Tohoku: Aomori, Iwate, Akita, Yamagata, Fukushima
- Kanto: Ibaraki, Tochigi, Gunma, Saitama, Chiba, Kanagawa
- Chubu: Niigata, Toyama, Ishikawa, Fukui, Yamanashi, Nagano, Gifu, Shizuoka
- Kinki: Mie, Shiga, Kyoto, Hyogo, Nara, Wakayama
- Chugoku: Tottori, Shimane, Okayama, Yamaguchi
- Shikoku: Tokushima, Ehime, Kochi
- Kyushu: Saga, Nagasaki, Kumamoto, Oita, Miyazaki, Kagoshima

Regional pages publish the official source, period, supported claim, unresolved boundary, and next action. Regional grouping is an execution and navigation convenience; it is not a quality shortcut.

## Execution order from here

### Work package A — target and actual crosswalks

1. Link each Reviewed annual-actual series to its Phase 9 target statement.
2. Confirm definition, unit, population, geography, measurement year, reporting year, and plan version.
3. Preserve `review_needed` where one-to-one identity cannot be verified.

### Work package B — money and project spine

1. Create stable policy / measure / project identifiers.
2. Link current budget, revised budget, expenditure, settlement, project cost, and contract amount as separate records.
3. Link priority projects only after department, period, scope, and identifier are checked.
4. Preserve historical plan and project versions instead of overwriting them.

### Work package C — accountability depth

1. Index and review contract and procurement evidence.
2. Connect assembly questions, proposals, decisions, and executive explanations.
3. Connect audit findings, recommendations, and corrective action.
4. Connect current-term executive manifesto promises where primary evidence is available.
5. Keep political promises and administrative plans in separate source roles.

### Work package D — publication verification

1. Require Evidence for every public value and relationship.
2. Verify all regional pages and nationwide matrix counts against machine-readable catalogs.
3. Confirm unsupported relationships remain visible rather than guessed.
4. Run schema validation, regression tests, lint, typecheck, static export, publication audit, and Production Smoke.

## Data rules

1. Reporting year and measurement year remain separate.
2. Current and previous plan versions remain separate.
3. Budget, revised budget, expenditure, settlement, project cost, and contract amount are not interchangeable.
4. A project name match is not sufficient; department, period, scope, and identifier must also be checked.
5. Assembly questions and audit findings are evidence of explanation and oversight, not automatic proof of success or failure.
6. Manifesto promises are linked only where the responsible government, term, wording, and policy scope can be verified.
7. Every promoted public record requires Evidence.
8. Unsupported links stay review-needed rather than being guessed.
9. No nationwide ranking is allowed before comparability is verified.
10. `not_indexed` means “not yet indexed,” not “does not exist.”

## Exit gates

Phase 10 is complete only when:

- all 47 prefectures are present in the uniform depth matrix;
- all 47 meet the completion threshold for all eleven dimensions;
- all public values and relationships have Evidence coverage of 100%;
- old plans, current plans, reporting years, and measurement years remain separated;
- budget, settlement, project, and contract values are not conflated;
- assembly, audit, and manifesto links are role- and term-correct;
- unsupported relationships remain explicit;
- the public Phase 10 matrix matches the machine-readable catalog;
- schema validation, regression tests, lint, typecheck, static export, publication audit, and Production Smoke pass;
- `data/catalog/phase10_completion.json` is `complete` and every gate is `passed`.

Until every condition is met, the phase remains `in_progress`.
