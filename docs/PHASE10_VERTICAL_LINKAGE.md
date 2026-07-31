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
- `data/catalog/phase10_wave1_source_inventory.json`
- `schemas/phase10_uniformity.schema.json`

`phase10_uniformity.json` stores the common eleven-dimension baseline and only the verified prefecture-specific differences. The public 47-prefecture matrix is derived from this manifest, preventing duplicated state and update drift. It is the canonical answer to “are all prefectures equally deep?”

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

Source state and linkage state remain different. A budget page can be `indexed` while no budget line is yet linked to a target.

## Baseline on 2026-08-01

Nationwide target and Evidence coverage is already uniform:

- Reviewed target statements: 47 / 47
- Reviewed Evidence Packet coverage: 47 / 47
- Publication verification baseline: 47 / 47

Downstream depth is not yet uniform:

- annual actuals linked: 1 prefecture
- annual actuals indexed but not linked: 1 prefecture
- budget indexed or better: 2 prefectures
- settlement Reviewed or better: 1 prefecture
- priority-project entrances indexed: 2 prefectures
- contract entrances indexed: 2 prefectures
- assembly evidence indexed: 1 prefecture
- audit evidence indexed: 0 prefectures
- executive-manifesto evidence indexed: 1 prefecture
- prefectures passing the complete uniform gate: 0 / 47

These counts are deliberately conservative. Partial pilot records do not promote an entire prefecture to `linked`.

## Execution order

### Work package A — finish the reference implementations

1. Miyagi: connect the existing annual-actual spine to budget, settlement, priority projects, and contracts.
2. Fukuoka: connect Reviewed finance and settlement records to policy targets, then attach annual evaluation and project records.
3. Extend both references to assembly, audit, and executive-manifesto evidence.

### Work package B — complete the remaining seven regional anchors

Hokkaido, Tokyo, Aichi, Osaka, Hiroshima, Kagawa, and Okinawa receive the same source inventory and linkage gates. No anchor is promoted by analogy to Miyagi or Fukuoka.

### Work package C — expand through seven regional batches

- Tohoku
- Kanto
- Chubu
- Kinki
- Chugoku
- Shikoku
- Kyushu and Okinawa

Each prefecture advances independently. Regional batches are an execution convenience, not a quality shortcut.

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
