# Phase 11 — Nationwide record-level linkage

Status: `in_progress`

Phase 10 completed the declared nationwide document-scope gate for all 47 prefectures. Phase 11 deepens that foundation from official-document relationships to reviewed one-to-one records.

## Objective

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

- current plan and target version;
- indicator name, definition, unit, population, and component structure;
- target year, reporting year, measurement year, and fiscal year;
- policy, measure, project name, department, office, and implementation period;
- budget, supplementary budget, settlement, project cost, and contract amount roles;
- candidate, election, term, and original manifesto wording;
- official URL, PDF page, extraction position, and review boundary.

Automated extraction may identify candidates but cannot promote them to `linked` without reviewed evidence.

## Wave 1 complete — Reference implementations

All existing record-level results in the four reference prefectures are inventoried and normalized.

| Prefecture | Records | Linked | Partial | Not linked |
|---|---:|---:|---:|---:|
| Hokkaido | 108 | 90 | 18 | 0 |
| Miyagi | 627 | 238 | 26 | 363 |
| Tokyo | 8 | 6 | 2 | 0 |
| Fukuoka | 118 | 86 | 12 | 20 |
| **Total** | **861** | **420** | **58** | **383** |

Wave 1 completion means:

- all 11 canonical linkage files are included;
- every source record appears exactly once;
- all 861 normalized records validate against one shared Schema;
- global normalized IDs and source-record keys are unique;
- all 420 Linked, 58 Partial, and 383 Not linked judgments remain unchanged;
- every record remains `not_assessed` and excluded from cross-prefecture comparison;
- no missing row, revised target, candidate match, or source conflict is promoted by inference.

Canonical completion controls:

- `data/catalog/phase11_wave1_migration.json`
- `data/catalog/phase11_wave1_completion.json`
- `schemas/phase11_record_linkage.schema.json`
- `schemas/phase11_wave1_completion.schema.json`
- `tests/test_phase11_wave1_completion.py`

## Reusable normalized record shape

`schemas/phase11_record_linkage.schema.json` preserves:

- record and hierarchy identifiers;
- project identity, departments, offices, match bases, and candidate settlements;
- canonical target context and annual-report target context as separate layers;
- series IDs, labels, units, raw values, scopes, operators, and periods;
- source-versus-catalog conflicts with nullable missing sides;
- record-level and measurement-level Evidence;
- `linked`, `partial`, and `not_linked` without automatic promotion;
- `not_assessed` and comparison exclusion.

## Hokkaido normalization

All 108 records are normalized.

- Linked: 90
- Partial: 18
- Not linked: 0

The 18 partial records retain target-version, unit-scale, definition/numbering, and component-structure reasons.

Files:

- `data/catalog/phase11_hokkaido_normalization.json`
- `scripts/normalize_phase11_hokkaido.py`
- `tests/test_phase11_hokkaido_normalization.py`

## Miyagi normalization

All 627 budget-project records are normalized.

- Linked: 238
- Partial: 26
- Not linked: 363

FY2026 budget and FY2024 settlement remain separate measurements. Candidate matches are retained without promotion, and records absent from the settlement source remain explicitly not linked.

Files:

- `data/catalog/phase11_miyagi_normalization.json`
- `scripts/normalize_phase11_miyagi.py`
- `tests/test_phase11_miyagi_normalization.py`

## Tokyo normalization

All eight children-policy target groups are normalized.

- Linked target groups: 6
- Linked series: 7
- Partial target groups: 2

The two partial records retain both official-source sides. Neither official document overwrites the other, and missing catalog values remain `null`.

Files:

- `data/catalog/phase11_tokyo_normalization.json`
- `scripts/normalize_phase11_tokyo.py`
- `tests/test_phase11_tokyo_normalization.py`

## Fukuoka normalization

All 118 target-actual records are normalized and resolved against all 26 canonical policy-target catalogs.

- Linked: 86
- Partial: 12
- Not linked: 20

Each record preserves the canonical plan baseline and target separately from the annual report's initial value, reported target, and annual actual.

- Linked records use the same target definition and retain the reported actual.
- Partial records retain the revised annual-report target and raw actual as `available_raw_only`; the revised target does not overwrite the canonical plan target.
- Not-linked records retain their canonical targets while the missing annual-report row remains explicit with no invented page or value.
- Ten reviewed aliases retain the official source indicator name and review note.

Files:

- `data/catalog/phase11_fukuoka_normalization.json`
- `scripts/normalize_phase11_fukuoka.py`
- `tests/test_phase11_fukuoka_normalization.py`

## Wave 2 active — Remaining regional anchors

Targets:

- Aichi
- Osaka
- Hiroshima
- Kagawa
- Okinawa

The next action is Aichi. Its current indicator catalog will be inventoried against the latest official progress source before any annual actual is promoted.

Each anchor must reach one of two valid states:

1. at least one Schema-valid record-level Evidence Chain; or
2. a reviewed maximum official-source depth explaining why deeper linkage is not yet supportable.

## Wave 3 — Nationwide minimum record depth

After the remaining anchors, apply the same gate to the other 38 prefectures. Equal record counts are not required because official publication depth differs. Evidence standards and missing-state treatment remain uniform.

## Phase 11 completion boundary

Phase 11 is complete when:

1. all 47 prefectures have at least one record-level linkage or a reviewed maximum-depth record;
2. every record validates against the shared Schema and resolves to existing Evidence;
3. plan versions, periods, money types, and responsibility roles are not mixed;
4. public pages and publication checks pass;
5. no policy-achievement, causality, or cross-prefecture comparability claim is inferred from linkage alone.

## Non-goals

- scoring policy ideology;
- recommending candidates;
- treating record count as municipal performance;
- calculating achievement from mismatched target versions;
- converting budget-to-settlement differences into policy outcomes;
- ranking indicators before comparability is verified.
