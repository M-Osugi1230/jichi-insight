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

All 861 normalized records validate against one shared Schema. Source records, status totals, IDs, Evidence references, unresolved states, non-assessment, and comparison exclusion are checked together.

Canonical controls:

- `data/catalog/phase11_wave1_migration.json`
- `data/catalog/phase11_wave1_completion.json`
- `schemas/phase11_record_linkage.schema.json`
- `tests/test_phase11_wave1_completion.py`

## Wave 2 active — Remaining regional anchors

Targets:

- Aichi
- Osaka
- Hiroshima
- Kagawa
- Okinawa

### Aichi normalization complete

All 56 reviewed indicator rows and all 62 series are normalized.

- Current-value series available: 61
- Current-value series missing: 1
- Implementation-plan progress-target series: 29
- Repost rows: 2
- Rows with a 2025 target revision: 1
- Policy-achievement assessments: 0

Rows become Partial when a current series is missing or the 2025 report revised the target. Repost rows retain original and repost Evidence pages.

Files:

- `data/catalog/phase11_aichi_normalization.json`
- `schemas/phase11_aichi_normalization.schema.json`
- `scripts/normalize_phase11_aichi.py`
- `tests/test_phase11_aichi_normalization.py`

### Osaka normalization complete

All 83 reviewed `Beyond EXPO 2025` indicator rows and all 91 series are normalized.

- Linked rows: 77
- Partial rows: 6
- Current-value series available: 85
- Current-value series missing: 6
- Explicit target series: 1
- Policy-achievement assessments: 0

The 2040s economic target and five first-survey-pending indicators remain Partial. The legacy `将来ビジョン・大阪` lineage and FY2026 business list remain separate.

Files:

- `data/catalog/phase11_osaka_normalization.json`
- `schemas/phase11_osaka_normalization.schema.json`
- `scripts/normalize_phase11_osaka.py`
- `tests/test_phase11_osaka_normalization.py`

### Hiroshima normalization complete

All 62 reviewed indicators from the revised Hiroshima Vision are normalized.

- Linked: 59
- Partial pending measurement: 3
- Policy areas: 17
- Qualitative target records: 1
- Policy-achievement assessments: 0

Compound cells, national comparators, average periods, approximate values, decrease semantics, and qualitative conditions remain reviewed raw text. Indicators 006–008 remain Partial because no current measurement is reported.

Files:

- `data/catalog/phase11_hiroshima_normalization.json`
- `schemas/phase11_hiroshima_normalization.schema.json`
- `scripts/normalize_phase11_hiroshima.py`
- `tests/test_phase11_hiroshima_normalization.py`

### Kagawa normalization complete

All 135 reviewed unique indicators in the extended Kagawa plan are normalized.

- Linked records: 135
- Partial / Not linked: 0 / 0
- Indicator series: 135
- Display occurrences retained as Evidence: 141
- Reposted indicators: 6
- R7-to-R8 target revisions: 87
- Unchanged target versions: 48
- Policy-achievement assessments: 0

Each indicator keeps three separate measurements: current value, original R7 target, and extended-plan R8 target. Corrected values, compound sub-series, cumulative periods, conditional text, and reference-year targets remain raw. Reposts remain one unique indicator with multiple Evidence locations.

Files:

- `data/catalog/phase11_kagawa_normalization.json`
- `schemas/phase11_kagawa_normalization.schema.json`
- `scripts/normalize_phase11_kagawa.py`
- `tests/test_phase11_kagawa_normalization.py`

### Wave 2 progress

- Anchors complete: 4 / 5
- Records normalized: 336
- Indicator series normalized: 350
- Current-value series available: 340
- Current-value series missing: 10
- Progress or explicit target series: 227
- Next anchor: Okinawa

Okinawa has 375 reviewed current-plan indicators: 36 major and 339 outcome indicators. The current catalog provides plan baselines and R9 targets but not reviewed annual actuals. The valid maximum depth is therefore to normalize all 375 records as Partial, preserving national comparators, rationale/source text, island and SDGs flags, qualitative targets, and the source anomaly while keeping annual actual unavailable.

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
