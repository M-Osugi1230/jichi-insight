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
- multi-series indicator histories with series identity and per-value periods;
- series IDs, labels, units, raw values, source statuses, scopes, operators, and directions;
- source-versus-catalog conflicts with nullable missing sides;
- original and repost Evidence locations;
- record-level and measurement-level Evidence;
- `linked`, `partial`, and `not_linked` without automatic promotion;
- `not_assessed` and comparison exclusion.

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
- Progress-target series configured by the implementation plan: 29
- Target values displayed in the annual report: 62 series
- Repost rows: 2
- Rows with a 2025 target revision: 1
- Policy-achievement assessments: 0

Rows become Partial when a current series is missing or the 2025 report revised the target. Repost rows retain the original Evidence page and the repost page.

Files:

- `data/catalog/phase11_aichi_normalization.json`
- `schemas/phase11_aichi_normalization.schema.json`
- `scripts/normalize_phase11_aichi.py`
- `tests/test_phase11_aichi_normalization.py`

### Osaka normalization complete

All 83 reviewed `Beyond EXPO 2025` indicator rows and all 91 series are normalized.

- Strategy target: 1
- Objective KPIs: 27
- Subjective and Well-Being indicators: 55
- Linked rows: 77
- Partial rows: 6
- Series with current observations: 85
- Series without current observations: 6
- Explicit target series: 1
- Policy-achievement assessments: 0

The 2040s economic target and five first-survey-pending indicators remain Partial. The legacy `将来ビジョン・大阪` series remains a separate lineage, and the FY2026 business list remains not linked.

Files:

- `data/catalog/phase11_osaka_normalization.json`
- `schemas/phase11_osaka_normalization.schema.json`
- `scripts/normalize_phase11_osaka.py`
- `tests/test_phase11_osaka_normalization.py`

### Hiroshima normalization complete

All 62 reviewed indicators from the revised Hiroshima Vision are normalized across the three canonical source files.

- Linked indicators with current observations: 59
- Partial indicators pending measurement: 3
- Not linked: 0
- Policy areas: 17
- Qualitative target records: 1
- Policy-achievement assessments: 0

Indicator cells may contain several sub-values, national comparators, average periods, approximate values, decrease semantics, or qualitative conditions. The normalization therefore retains each official baseline, current, target, target period, source, change state, Evidence ID, and PDF page as reviewed raw text instead of inferring a component structure.

Indicators 006, 007, and 008 remain Partial because the revised vision records a future first survey rather than a current observation. Their original text remains visible and their numeric value remains missing. Indicator 042 retains its qualitative nuclear-disarmament target without numeric conversion.

Files:

- `data/catalog/phase11_hiroshima_normalization.json`
- `schemas/phase11_hiroshima_normalization.schema.json`
- `scripts/normalize_phase11_hiroshima.py`
- `tests/test_phase11_hiroshima_normalization.py`

### Wave 2 progress

- Anchors complete: 3 / 5
- Records normalized: 201
- Indicator series normalized: 215
- Current-value series available: 205
- Current-value series missing: 10
- Progress or explicit target series: 92
- Next anchor: Kagawa

Kagawa will preserve all 135 unique indicators, 141 display occurrences, six reposts, 87 R7-to-R8 target revisions, corrected values, cumulative periods, and reference targets without duplicate promotion.

Each remaining anchor must reach one of two valid states:

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
