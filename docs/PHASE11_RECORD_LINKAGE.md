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

## Initial reference records

The first shared contract preserves four existing implementations without rewriting their source registries.

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

## Waves

### Wave 1 — Reference implementations

Unify the existing Hokkaido, Miyagi, Tokyo, and Fukuoka records under the shared contract and derive reusable promotion rules.

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
