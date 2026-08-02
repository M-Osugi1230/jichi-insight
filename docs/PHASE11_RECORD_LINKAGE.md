# Phase 11 — Nationwide record-level linkage

Status: `in_progress`

Phase 10 completed the nationwide document-scope gate for all 47 prefectures. Phase 11 deepens that foundation to reviewed one-to-one records or an explicit reviewed maximum official-source depth.

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

A missing relationship is never filled by inference. Plan versions, reporting periods, units, money roles, organizations, and Evidence locations must remain separate.

## Wave 1 complete — Reference implementations

| Prefecture | Records | Linked | Partial | Not linked |
|---|---:|---:|---:|---:|
| Hokkaido | 108 | 90 | 18 | 0 |
| Miyagi | 627 | 238 | 26 | 363 |
| Tokyo | 8 | 6 | 2 | 0 |
| Fukuoka | 118 | 86 | 12 | 20 |
| **Total** | **861** | **420** | **58** | **383** |

All 861 records validate against one shared Schema. IDs, source records, Evidence, status totals, unresolved states, non-assessment, and comparison exclusion are integrated gates.

Canonical controls:

- `data/catalog/phase11_wave1_completion.json`
- `schemas/phase11_record_linkage.schema.json`
- `tests/test_phase11_wave1_completion.py`

## Wave 2 complete — Remaining regional anchors

Wave 2 completed Aichi, Osaka, Hiroshima, Kagawa, and Okinawa.

| Prefecture | Records | Normalized depth |
|---|---:|---|
| Aichi | 56 | 62 series; 61 current-value series and one missing series |
| Osaka | 83 | 91 series; 77 Linked and six Partial rows |
| Hiroshima | 62 | 59 Linked and three pending-measurement Partial rows |
| Kagawa | 135 | 135 Linked records and 141 retained display occurrences |
| Okinawa | 375 | Plan-baseline-to-R9-target maximum depth; all Partial |
| **Total** | **711** | **725 indicator series** |

### Aichi

Every baseline, current, and target value retains series identity, label, unit, period, raw value, source status, operator, aggregation scope, direction, and comparability note. A missing current series and a revised target remain Partial conditions. Reposts retain original and repost Evidence pages.

### Osaka

The current `Beyond EXPO 2025` catalog is normalized without attaching the legacy Osaka future-vision lineage or FY2026 business-list causality. The 2040s economic target and five first-survey-pending indicators remain Partial.

### Hiroshima

Compound cells, national comparators, average periods, approximate values, decrease semantics, and qualitative conditions remain reviewed raw text. Three future-survey indicators remain Partial. A qualitative nuclear-disarmament target is not converted to a number.

### Kagawa

All 135 unique indicators retain current values, original R7 targets, extended-plan R8 targets, corrected values, cumulative periods, compound cells, conditions, and reference targets. Six reposted indicators remain one record each with multiple Evidence locations.

### Okinawa

All 375 current-plan indicators are normalized at the maximum reviewed official-source depth.

- Major indicators: 36
- Outcome indicators: 339
- Island indicators: 32
- SDGs-priority indicators: 43
- Qualitative targets: 9
- National reference values provided: 174
- Official source anomalies retained: 1

The current source provides plan baselines and R9 targets, not reviewed annual actuals. Every Okinawa record therefore remains Partial, `annual_actual` remains explicitly unavailable, and national values remain reference context rather than Okinawa results.

Canonical Wave 2 controls:

- `data/catalog/phase11_wave2_completion.json`
- `schemas/phase11_wave2_completion.schema.json`
- `tests/test_phase11_wave2_completion.py`
- `data/catalog/phase11_aichi_normalization.json`
- `data/catalog/phase11_osaka_normalization.json`
- `data/catalog/phase11_hiroshima_normalization.json`
- `data/catalog/phase11_kagawa_normalization.json`
- `data/catalog/phase11_okinawa_normalization.json`

Wave 2 integration totals:

- Anchors complete: 5 / 5
- Records: 711
- Indicator series: 725
- Current-value series available: 340
- Current-value series missing or unavailable: 385
- Progress or explicit target series: 602
- Reviewed maximum-depth records: 375
- Policy-achievement assessments: 0
- Comparison-eligible records: 0

## Wave 3 active — Nationwide minimum record depth

Wave 3 applies the same quality gate to the remaining 38 prefectures in prefecture-code order, beginning with Aomori (`02`) and Iwate (`03`). Equal record counts are not required. Every prefecture must receive either:

1. a Schema-valid reviewed record-level linkage; or
2. a reviewed maximum official-source depth that states why deeper linkage is not yet supportable.

Missing, unpublished, partial, and not-assessable states remain explicit.

## Phase 11 completion boundary

Phase 11 is complete when:

1. all 47 prefectures have a record-level linkage or reviewed maximum-depth record;
2. every record validates against the shared Schema and resolves to Evidence;
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
