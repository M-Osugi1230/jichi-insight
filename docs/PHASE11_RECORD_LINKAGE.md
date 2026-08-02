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

The inventory references all 11 canonical record files. Regression tests load every record dynamically and fail when a source file, record ID, status, count, or non-assessment boundary changes unexpectedly.

Canonical inventory files:

- `data/catalog/phase11_wave1_migration.json`
- `schemas/phase11_wave1_migration.schema.json`
- `tests/test_phase11_wave1_migration.py`

## Reusable normalized record shape

`schemas/phase11_record_linkage.schema.json` preserves source-specific identity, measurement roles, components, Evidence locations, unresolved candidate matches, and official-source conflicts without forcing them into one value.

The schema now supports:

- record and hierarchy identifiers;
- project identity and candidate settlement matches;
- target series IDs, catalog roles, labels, units, values, and periods;
- source-versus-catalog conflicts with nullable missing sides;
- record-level and measurement-level Evidence;
- `linked`, `partial`, and `not_linked` without automatic promotion;
- `not_assessed` and comparison exclusion.

## Hokkaido normalization complete

All 108 Hokkaido records transform deterministically into the reusable record shape.

- Linked: 90
- Partial: 18
- Not linked: 0

The 18 partial records retain target-version, unit-scale, definition/numbering, and component-structure reasons.

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

FY2026 budget and FY2024 settlement remain separate measurements. Candidate matches are retained without promotion, and records absent from the settlement source remain explicitly not linked.

Canonical files:

- `data/catalog/phase11_miyagi_normalization.json`
- `schemas/phase11_miyagi_normalization.schema.json`
- `scripts/normalize_phase11_miyagi.py`
- `tests/test_phase11_miyagi_normalization.py`

## Tokyo normalization complete

All eight Tokyo children-policy target groups transform deterministically into the reusable record shape.

- Linked target groups: 6
- Linked series: 7
- Partial target groups: 2
- Not linked: 0

Each linked series retains its stable series ID, catalog role, label, unit, raw value, value status, and measurement period.

The two partial records retain both official-source sides:

- life-plan education remains partial because the policy review reports FY2023 while the January 2026 target list records FY2024;
- disabled-child and medical-care-child acceptance remains partial because the policy review reports 44 municipalities / 2023 while the target list records 47 municipalities / 2024.

A missing catalog value in one conflict is stored as `null`, not guessed. Neither official document overwrites the other.

Canonical files:

- `data/catalog/phase11_tokyo_normalization.json`
- `schemas/phase11_tokyo_normalization.schema.json`
- `scripts/normalize_phase11_tokyo.py`
- `tests/test_phase11_tokyo_normalization.py`

## Normalization progress

| Prefecture | Records normalized | Status |
|---|---:|---|
| Hokkaido | 108 / 108 | Complete |
| Miyagi | 627 / 627 | Complete |
| Tokyo | 8 / 8 | Complete |
| Fukuoka | 0 / 118 | Next |
| **Wave 1** | **743 / 861** | In progress |

State totals normalized so far:

- Linked: 334 / 420
- Partial: 46 / 58
- Not linked: 363 / 383

## Next normalization order

Wave 1 proceeds without skipping source states.

1. ~~Normalize all Hokkaido records.~~ Complete.
2. ~~Normalize all Miyagi records.~~ Complete.
3. ~~Normalize all Tokyo records and preserve both conflicts.~~ Complete.
4. Normalize 86 Fukuoka linked targets, 12 revised-target partial records, and 20 not-linked records.
5. Run one integrated Wave 1 gate over all 861 normalized records.

## Waves

### Wave 1 — Reference implementations

The exhaustive inventory is complete. Hokkaido, Miyagi, and Tokyo are normalized; Fukuoka remains.

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
