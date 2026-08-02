# Phase 11 — Nationwide record-level linkage

Status: `in_progress`

Phase 10 completed the declared nationwide document-scope gate for all 47 prefectures. Phase 11 deepens that foundation from official-document relationships to reviewed one-to-one records.

## Objective

Connect the same policy or accountability record across the layers that official evidence permits.

```text
Policy target or measure
→ Annual actual
→ Budget
→ Settlement
→ Priority project
→ Contract / payee
→ Audit finding
→ Assembly evidence
→ Executive promise
```

Phase 11 does not require every layer to exist for every record. It requires the maximum verified depth to be explicit and forbids filling missing relationships by inference.

## Promotion gate

A relationship can be `linked` only when reviewers confirm the relevant combination of:

- current plan and target version
- indicator name, definition, unit, population, and component structure
- target year, reporting year, measurement year, and fiscal year
- policy, measure, project name, department, office, and implementation period
- budget, supplementary budget, settlement, project cost, and contract amount roles
- candidate, election, term, and original manifesto wording
- official URL, PDF page, extraction position, and review boundary

Automated extraction may identify candidates but cannot promote them to `linked` without reviewed evidence.

## Wave 1 exhaustive inventory

All existing record-level results in the four reference prefectures are controlled by one exhaustive migration inventory.

| Prefecture | Source records | Linked | Partial | Not linked |
|---|---:|---:|---:|---:|
| Hokkaido | 108 | 90 | 18 | 0 |
| Miyagi | 627 | 238 | 26 | 363 |
| Tokyo | 8 | 6 | 2 | 0 |
| Fukuoka | 118 | 86 | 12 | 20 |
| **Total** | **861** | **420** | **58** | **383** |

The inventory references all 11 canonical record files. Regression tests load every record dynamically and fail when:

- a catalog part file is omitted or reordered;
- a record ID appears twice within a prefecture source;
- a linkage state falls outside `linked`, `partial`, or `not_linked`;
- source-record counts differ from the canonical catalog summary;
- aggregate totals differ from 861 / 420 / 58 / 383;
- one of the initial common-schema references no longer resolves to the full inventory;
- a source is promoted from `not_assessed` without an explicit methodology change.

Canonical inventory files:

- `data/catalog/phase11_wave1_migration.json`
- `schemas/phase11_wave1_migration.schema.json`
- `tests/test_phase11_wave1_migration.py`

## Reusable normalized record shape

`schemas/phase11_record_linkage.schema.json` defines the reusable Phase 11 record shape. It preserves:

- original record and hierarchy identifiers;
- the reviewed linkage status and unresolved reason;
- source-specific identity context such as department, office, normalized project name, match basis, and candidate matches;
- current, intermediate target, final target, actual, budget, settlement, project-cost, and contract-amount roles as separate measurements;
- raw value text, periods, numeric or textual components;
- Evidence locations for the whole record and individual money measurements;
- the original review boundary;
- `not_assessed` and comparison-exclusion states.

## Hokkaido normalization complete

All 108 Hokkaido records transform deterministically into the reusable record shape.

- Linked: 90
- Partial: 18
- Not linked: 0
- Policy-achievement assessments: 0

The 18 partial records retain all original reason groups:

- target version changed: 3
- unit scale changed or requires explicit conversion: 3
- indicator definition or numbering changed: 10
- component structure changed: 2

Canonical files:

- `data/catalog/phase11_hokkaido_normalization.json`
- `schemas/phase11_hokkaido_normalization.schema.json`
- `scripts/normalize_phase11_hokkaido.py`
- `tests/test_phase11_hokkaido_normalization.py`

## Miyagi normalization complete

All 627 Miyagi budget-project records transform deterministically into the reusable record shape.

- Linked: 238
- Partial: 26
- Not linked: 363
- Policy-achievement assessments: 0

For every record, the transformation preserves policy and measure references, original and normalized project names, department, office, implementation period, match basis, budget amount and page, settlement amount and page, project number, candidate matches, and review boundary.

The three result states remain distinct:

- `linked`: the same measure, normalized project name, department, and office identify one settlement record;
- `partial`: one or more settlement candidates are retained, but no candidate is promoted;
- `not_linked`: no FY2024 settlement candidate is available, and the missing relationship remains explicit.

FY2026 budget and FY2024 settlement values are always separate measurements. A difference between them is not converted into an execution rate or policy outcome.

Canonical files:

- `data/catalog/phase11_miyagi_normalization.json`
- `schemas/phase11_miyagi_normalization.schema.json`
- `scripts/normalize_phase11_miyagi.py`
- `tests/test_phase11_miyagi_normalization.py`

## Normalization progress

| Prefecture | Records normalized | Status |
|---|---:|---|
| Hokkaido | 108 / 108 | Complete |
| Miyagi | 627 / 627 | Complete |
| Tokyo | 0 / 8 | Next |
| Fukuoka | 0 / 118 | Pending |
| **Wave 1** | **735 / 861** | In progress |

State totals normalized so far:

- Linked: 328 / 420
- Partial: 44 / 58
- Not linked: 363 / 383

## Initial common-schema reference records

Four records demonstrate the shared cross-layer representation while the full source inventory remains canonical.

1. Hokkaido: food self-sufficiency target to annual actual
2. Miyagi: policy measure to priority project, budget, and settlement
3. Tokyo: children-policy target to annual actual
4. Fukuoka: policy target to annual actual

Canonical files:

- `data/catalog/phase11_reference_records.json`
- `schemas/phase11_reference_records.schema.json`
- `data/catalog/phase11_execution_queue.json`
- `schemas/phase11_execution_queue.schema.json`
- `tests/test_phase11_reference_records.py`

## Next normalization order

Wave 1 proceeds without skipping source states.

1. ~~Normalize all 90 Hokkaido linked annual-actual records.~~ Complete.
2. ~~Preserve all 18 Hokkaido partial records with their exact unresolved reason.~~ Complete.
3. ~~Normalize all 238 Miyagi linked project-money records.~~ Complete.
4. ~~Preserve 26 Miyagi partial and 363 not-linked records without promotion.~~ Complete.
5. Normalize the six Tokyo linked target groups and preserve the two source conflicts.
6. Normalize 86 Fukuoka linked targets, 12 revised-target partial records, and 20 not-linked records.
7. Derive reusable normalizers only after every source-specific field has an explicit mapping or retained boundary.

## Waves

### Wave 1 — Reference implementations

Unify the existing Hokkaido, Miyagi, Tokyo, and Fukuoka records under the shared contract and derive reusable promotion rules. The exhaustive inventory is complete. Hokkaido and Miyagi are normalized; Tokyo and Fukuoka remain.

### Wave 2 — Remaining regional anchors

Add Aichi, Osaka, Hiroshima, Kagawa, and Okinawa. Each anchor must have at least one reviewed record-level chain or an explicit maximum official-source depth.

### Wave 3 — Nationwide minimum record depth

Apply the same quality gate to the remaining 38 prefectures. Equal record counts are not required because official publication depth differs. The gate, evidence standard, and missing-state treatment must remain uniform.

## Completion boundary

Phase 11 is complete when:

1. all 47 prefectures have at least one record-level linkage or a reviewed maximum-depth record;
2. every record validates against the shared schema and resolves to existing evidence;
3. plan versions, periods, money types, and responsibility roles are not mixed;
4. public pages and publication checks pass;
5. no policy-achievement, causality, or cross-prefecture comparability claim is inferred from linkage alone.

## Non-goals

- scoring policy ideology
- recommending candidates
- treating record count as municipal performance
- calculating achievement from mismatched target versions
- converting budget-to-settlement differences into policy outcomes
- ranking indicators before comparability is verified
