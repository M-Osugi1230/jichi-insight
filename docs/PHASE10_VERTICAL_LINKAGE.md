# Phase 10 — Vertical linkage from targets to delivery

Phase 10 connects the nationwide Reviewed target statements completed in Phase 9 to the evidence required to understand delivery:

```text
Target statement
→ Annual actual
→ Budget and expenditure
→ Priority project
→ Contract and procurement
→ Evaluation, audit, assembly explanation
```

The phase does not create an independent policy score. A target is not marked achieved merely because a value increased, a budget exists, or a project was executed.

## Starting point

Phase 9 completed Evidence-backed Reviewed numeric-target coverage for all 47 prefectures.

The nationwide source inventory remains much shallower outside policy plans and KPI sources:

- annual evaluation: 1 linked, 1 indexed, 45 not indexed
- budget: 1 reviewed, 46 not indexed
- project evaluation: 47 not indexed
- contracts: tracked for Phase 10, with no prefecture promoted before an official source is cataloged

The machine-readable baseline is:

- `data/catalog/phase10_execution_queue.json`
- `data/catalog/phase10_completion.json`

## Scope

### Wave 1 — nine regional anchors

Hokkaido, Miyagi, Tokyo, Aichi, Osaka, Hiroshima, Kagawa, Fukuoka, and Okinawa are the first vertical-linkage wave because their target structures are already deeply Reviewed and published.

The initial verified baseline is conservative:

- Miyagi: annual actuals linked; budget, projects, and contracts not yet linked
- Fukuoka: annual-evaluation entrance indexed and budget data Reviewed; target-to-actual linkage still pending
- the other seven anchors: source inventory required before promotion

### Wave 2 — remaining 38 prefectures

The seven Phase 9 regional batches are retained. Each prefecture advances independently through:

```text
source_inventory
→ annual_actuals_linkage
→ budget_linkage
→ project_spine
→ publication_verification
```

## Data rules

1. **Source state and linkage state are separate.** Indexed means an official source entrance exists. Linked means a target and a downstream record were definition-checked.
2. **Reporting year and measurement year remain separate.**
3. **Target versions remain separate.** Actuals from a previous plan are not silently attached to a current target.
4. **Budget, expenditure, project, and contract amounts are not interchangeable.**
5. **No inferred achievement rate.** Official rates may be stored as official statements, but Jichi Insight does not recalculate them without a defined method.
6. **No nationwide ranking before comparability verification.**
7. **Every promoted public record requires Evidence.**

## Exit gates

Phase 10 is complete only when:

- all 47 prefectures have explicit source states for annual evaluation, budget, project evaluation, and contracts
- the nine regional anchors have annual actuals linked to Reviewed targets where definitions permit
- the nine anchors have a Reviewed money-and-project spine for selected priority policies
- contract and accountability evidence is linked without conflating procurement with outcomes
- all public values have Evidence coverage of 100%
- unsupported links remain review-needed rather than being guessed
- static export, regression tests, and Production Smoke pass
- `data/catalog/phase10_completion.json` is `complete` with every gate `passed`

## Immediate execution order

1. Keep Miyagi as the active reference implementation and add budget/project/contract entrances.
2. Use Fukuoka as the money-spine reference and connect existing Reviewed finance data to policy targets.
3. Inventory annual evaluation, budget, project evaluation, and contract sources for the remaining seven anchors.
4. Publish linkage-state visibility before publishing any policy-achievement judgment.
5. Expand the same model through the seven regional Wave 2 batches.
