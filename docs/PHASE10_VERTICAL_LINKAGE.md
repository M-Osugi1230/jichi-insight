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
- `data/catalog/phase10_reference_depth_reviews.json`
- `data/catalog/phase10_anchor_depth_reviews.json`
- `data/catalog/phase10_tohoku_depth_reviews.json`
- `data/catalog/phase10_wave1_source_inventory.json`
- `schemas/phase10_uniformity.schema.json`
- `schemas/phase10_regional_depth_reviews.schema.json`

`phase10_uniformity.json` stores the common eleven-dimension baseline and only the verified prefecture-specific differences. The public 47-prefecture matrix is derived from this manifest, preventing duplicated state and update drift. It is the canonical answer to “are all prefectures equally deep?”

The depth-review registries preserve the official source, reporting period, accepted claim, and unresolved linkage boundary behind every promotion:

- `phase10_reference_depth_reviews.json`: Miyagi and Fukuoka reference implementations
- `phase10_anchor_depth_reviews.json`: Hokkaido, Tokyo, Aichi, Osaka, Hiroshima, Kagawa, and Okinawa
- `phase10_tohoku_depth_reviews.json`: Aomori, Iwate, Akita, Yamagata, and Fukushima

## Uniform dimensions

Every prefecture is tracked against the same eleven dimensions.

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

Nationwide target and Evidence coverage is already uniform:

- Reviewed target statements: 47 / 47
- Reviewed Evidence Packet coverage: 47 / 47
- Publication verification baseline: 47 / 47

Fourteen prefectures have all five delivery-evidence layers indexed or better:

- nine regional anchors;
- the five remaining Tohoku prefectures: Aomori, Iwate, Akita, Yamagata, and Fukushima.

Thirteen prefectures have all five layers Reviewed. Miyagi is the exception because its settlement layer remains `indexed` while its annual actuals are already `linked`.

Current depth:

- annual actuals Reviewed or better: 14 / 47
  - Miyagi is `linked`
  - thirteen prefectures are `reviewed`
- budget Reviewed or better: 14 / 47
- settlement Reviewed or better: 13 / 47
  - Miyagi has the official settlement entrance `indexed`
- priority projects Reviewed or better: 14 / 47
- audit Reviewed or better: 14 / 47

Accountability and delivery linkage remains shallower:

- contract entrances indexed: 2 / 47
- assembly evidence indexed: 2 / 47
- executive-manifesto evidence indexed: 1 / 47
- prefectures passing the complete eleven-dimension gate: 0 / 47

These counts are deliberately conservative. Reviewed source coverage does not promote a dimension to `linked`; target, period, scope, department, project identity, and amount must still be checked.

## Completed review batches

### Miyagi and Fukuoka reference implementations

Miyagi remains the annual-actual linkage reference. Fukuoka remains the finance and settlement review reference. Both retain explicit boundaries for budget, settlement, priority-project, assembly, audit, contract, and manifesto linkage.

### Seven additional regional anchors

Hokkaido, Tokyo, Aichi, Osaka, Hiroshima, Kagawa, and Okinawa have Reviewed annual-progress, budget, settlement, priority-project, and audit sources.

### Tohoku batch

Aomori, Iwate, Akita, Yamagata, and Fukushima have the same five layers Reviewed. Important plan-version boundaries remain explicit:

- Akita: old-plan evaluation and settlement are not attached to the new plan automatically.
- Yamagata: prior and later implementation-plan target versions remain separate.
- other prefectures retain reporting-year, measurement-year, and project-identity boundaries.

The Tohoku evidence is published at `/municipalities/phase10/tohoku`.

## Execution order from here

### Work package A — complete five-layer review nationwide

1. Kanto: Ibaraki, Tochigi, Gunma, Saitama, Chiba, and Kanagawa.
2. Chubu.
3. Kinki.
4. Chugoku.
5. Shikoku.
6. Kyushu and Okinawa.

Each prefecture advances independently. Regional batches are an execution convenience, not a quality shortcut.

### Work package B — link reviewed evidence to targets and projects

1. Link annual actuals to Reviewed target statements.
2. Create stable policy / measure / project crosswalks.
3. Keep budget, revised budget, settlement, project cost, and contract amount separate.
4. Link audit findings only where the subject policy or project is verifiable.
5. Add assembly and executive-manifesto evidence without conflating political promises and administrative plans.

### Work package C — complete delivery and accountability depth

- index and review contract / procurement evidence;
- connect assembly questions, proposals, decisions, and explanations;
- connect audit findings and corrective action;
- connect current-term executive manifesto promises where primary evidence is available;
- verify all public routes and Evidence coverage.

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
- schema validation, regression tests, lint, typecheck, static export, and Production Smoke pass;
- `data/catalog/phase10_completion.json` is `complete` and every gate is `passed`.

Until every condition is met, the phase remains `in_progress`.
