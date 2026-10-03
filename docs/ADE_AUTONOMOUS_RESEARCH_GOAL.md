# ADE Autonomous Research Goal — Phase 15

Status: `active-design`

## North Star

Jichi Insight exists to create an information environment in which residents can evaluate municipalities, mayors/governors, and assemblies for themselves from traceable primary-source evidence.

ADE must accelerate this purpose without lowering the repository's evidence, review, attribution, or publication standards.

## Campaign objective

Use ADE to advance Phase 15 from the current canonical queue state to completion while preserving Jichi Insight's non-inference rules.

The immediate operating objective is:

> For each remaining Phase 15 municipality, prepare a complete, evidence-backed review candidate from official primary sources, validate it against repository schemas and regressions, and carry it through PR/CI. Final promotion to `reviewed_complete` must not bypass the repository's existing human-review meaning of `Reviewed`.

Current canonical starting point:

- target municipalities: 67
- reviewed complete: 4
- review in progress: 1 — Morioka
- pending record review: 62
- blocked source inventory: 0

The machine-readable queue remains authoritative:
`data/catalog/phase15_core_capital_review_queue.json`.

## Evidence chain

ADE work must preserve the project's evidence chain:

```text
Promise
  -> Money
  -> Action
  -> Result
  -> Accountability
```

The goal is not to maximize raw record count. The goal is to increase the number of municipalities for which residents can inspect a trustworthy, source-linked accountability package and clearly see what is still unknown.

## Autonomous loop

For one municipality at a time, in canonical queue order:

1. Read the current Source Inventory and Phase 15 contract.
2. Identify the declared v1 review package and missing evidence.
3. Use official primary sources only for promoted facts.
4. Preserve source URL, evidence locator, version, period, fiscal state, and availability state.
5. Build or update the municipality review package.
6. Keep unpublished, unresolved, historical-only, aggregate-only, draft, and non-comparable evidence explicit.
7. Run schema validation, repository validation, regression tests, Python lint, web lint/typecheck/build, static-export validation, and publication audit.
8. Independently inspect the proposed changes for non-inference violations and provenance gaps.
9. Open a bounded PR whose changed files are restricted to the accepted ADE task paths.
10. Require target `Quality` workflow success before trusted merge.
11. After merge, require the repository's existing deployment/production verification path to remain green.
12. Continue to the next queue municipality only after the current task has durable completion evidence or an explicit blocker/HUMAN_WAIT.

## Human-review boundary

The current repository defines `Reviewed` as primary-source evidence checked by a person.

Therefore ADE must not silently redefine that term.

ADE may autonomously produce, validate, and independently review a complete `review_candidate`. Promotion to `reviewed_complete` is allowed only when the existing human-review requirement has been satisfied or a future dedicated ADR explicitly changes the quality-state definition.

A missing human approval is a legitimate `HUMAN_WAIT`, not a reason to fabricate completion.

## Non-negotiable prohibitions

ADE must never:

- infer an unpublished fact;
- convert `not_indexed` into non-existence;
- reuse historical/prior-plan actuals as current-plan actuals without official linkage;
- collapse proposal, enacted, supplementary, execution, settlement, project cost, contract amount, or subsidy amount;
- merge target, measurement, reporting, fiscal, publication, or evaluation years;
- promote draft/public-comment/advisory material as adopted policy;
- convert source-reported assessments into Jichi Insight's own achievement score;
- infer causality from co-occurrence or timing;
- allocate aggregate values to individual identities without official evidence;
- create cross-city scores or rankings before comparability review;
- score political ideology, party, or personal preference;
- reduce evidence quality merely to increase municipality coverage.

## Campaign success criteria

The Phase 15 campaign is complete only when the repository's own Phase 15 completion definition is satisfied, including:

- all 67 municipalities are legitimately `reviewed_complete`;
- no municipality remains `review_in_progress` or `pending_record_review`;
- every municipality has a valid completion contract and referenced review-package files;
- fiscal records and evidence packets validate;
- deferred evidence remains explicit;
- independent policy-achievement judgments remain zero;
- causal-attribution judgments remain zero;
- unverified cross-city rankings remain zero;
- repository/data validation, regression tests, web checks, deployment checks, and Production Smoke pass on the merged head.

## First ADE pilot

The first bounded pilot is Morioka (official code 032018), the current queue head.

Pilot success requires:

- a complete Morioka Phase 15 review candidate;
- no weakening of evidence or non-inference rules;
- deterministic tests for the new package;
- green target Quality workflow;
- trusted ADE PR binding and merge gate;
- explicit human-review status before any `reviewed_complete` promotion;
- durable evidence that ADE can resume with the next municipality after completion or HUMAN_WAIT.

Only after this pilot proves the loop should ADE broaden to multiple municipalities per campaign.


## Candidate staging contract

ADE-generated Phase 15 evidence must enter a non-public staging boundary before human review. The initial pilot uses `data/candidates/morioka-city/review_candidate.json`, validated by `schemas/phase15_review_candidate.schema.json`. Candidate state must remain `review_candidate`, `human_review.status=pending`, and `publication.eligible=false`. The Phase 15 queue remains `review_in_progress` until a person checks the cited primary sources and a separate promotion change creates the normal Reviewed package.
