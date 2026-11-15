# Jichi Insight — UI benchmark and iteration plan (2026-11-15)

## Purpose / evidence boundary

Improve first-time use of Jichi Insight without weakening the project's verified-data boundary.
This is a **source-code and documented-reference review**, not a usability study or screenshot-based audit.
Direct external rendering of the production GitHub Pages URL was unavailable during this review.
No performance score, conversion rate or accessibility compliance status is claimed here.

## External reference comparison

| Reference | User-facing pattern we can confirm | Adopt | Do not copy without adapting |
|---|---|---|---|
| [Google Data Commons Place Explorer](https://datacommons.org/place/) | A place-name search leads to statistics about a selected place | Municipality-name-first discovery and coherent locality profiles | Population rankings or comparisons lacking Jichi's comparable reviewed data |
| [Our World in Data](https://ourworldindata.org/) | Chart explorers expose place, metric, chart/map/table and source choices | Readable trends, chart ↔ table ↔ official-source navigation | Unjustified correlations or hiding missing/undefined values in charts |
| [GOV.UK Design System](https://design-system.service.gov.uk/) | Consistent, accessible navigation, forms, components and task-oriented copy | Plain Japanese, accessible labels, focus behavior, progressive disclosure | A government-branded visual identity |
| [e-Stat](https://www.e-stat.go.jp/) | Keyword, theme and region search plus data tables/maps | Region/category filters and explicit coverage | Exposing every advanced setting on the first screen |
| [データでわかる東京](https://tdb.metro.tokyo.lg.jp/) | Thematic public-policy dashboards | Policy topics with citizen-readable explanations | Summarizing a policy as successful without evidence |
| [デジタル庁 ダッシュボード実践ガイド](https://www.digital.go.jp/resources/dashboard-guidebook) | Guidance for chart selection, layout, legibility and non-misleading communication | Chart standards, grid, annotations, date/source treatment | Decorative graphs where no comparable series exists |

Additional standards:
- [GOV.UK Government Design Principles](https://www.gov.uk/guidance/government-design-principles): start with user needs; make complex things simple; iterate.
- [WCAG 2.2](https://www.w3.org/TR/WCAG22/): keyboard access, contrast, perceivable focus and pointer targets.

## Current Jichi Insight findings (from `main` at review time)

1. The homepage hero leads with a large conceptual statement and review counts, but the search UI lives several sections down the municipality index.
2. The prefecture search component (`CoverageExplorer.tsx`) already supports name/region/plan-title filtering and meaningful evidence states; this should be reused conceptually, not replaced by guessed municipality data.
3. The homepage and municipality index prioritize technical statuses (Reviewed, Evidence, Phase numbers) before first-time tasks.
4. Prefecture index status rails include labels originally set near 0.5 rem: readability merits attention.
5. At the time of the audit, some static page/metadata text displayed 15,124 records while the canonical reviewed count in project status is 15,327. User-facing numbers must be derived from source-of-truth state.
6. Detailed Phase 15 city pages are faithful to evidence but start with a technical narrative rather than a citizen-focused summary.
7. Current comparison scope is explicitly limited to matched Fukuoka City / Kitakyushu City financial values; expansion cannot precede comparability review.

## Target information architecture

1. **Search** — find a prefecture or a reviewed city quickly. Explicitly state what is not indexed/reviewed.
2. **Locality overview** — simple facts, date, source, review boundary.
3. **Money** — what is reported as initial budget, settlement, revenue and spending, never mixed.
4. **Promises and actions** — policy objectives and what is linked to project execution.
5. **Results** — historical actuals only where definitions and measurement periods permit.
6. **Accountability** — leaders, assemblies, audits and evidence where available.
7. **Evidence and missing data** — always reachable; do not bury limits behind a score.

Keep neutral official-source verification and Jichi editorial interpretation separate in every step.

## Iteration backlog

### Iteration 1 (this PR): discoverability and readability

- [x] Homepage search for all reviewed prefectures and reviewed-complete Phase 15 cities.
- [x] Search result name/region differentiation and explicit coverage note.
- [x] Keyboard-supported search, links, empty state and accessible form text.
- [x] Smaller mobile hero height/padding.
- [x] Human-readable text-size improvements to prefecture card evidence labels.
- [x] Remove stale record count literals from index and data-quality text.
- [ ] Visual review on 375/390/768/1280px device widths.
- [ ] VoiceOver and keyboard audit.
- [ ] Lighthouse accessibility and performance baseline.

### Iteration 2: citizen-facing municipality profile

- [ ] A consistent executive summary panel across reviewed locality pages.
- [ ] Section jump navigation: overview / fiscal / plans / results / accountability / sources.
- [ ] The year, account type, review date and evidence status remain visible at the value level.
- [ ] A clear unavailable/unknown state rather than displaying zero or guessing.

### Iteration 3: comparison and visualization

- [ ] Introduce timeline charts only for actuals that are verified and definitionally aligned.
- [ ] Provide linked table, units, source page and data download alongside each chart.
- [ ] Add a map as an optional discovery view; always keep keyboard-accessible text search.
- [ ] Any municipality-to-municipality comparison passes documented equivalence gates.
- [ ] Never turn counts, linkage status or missing information into an attainment ranking.

## Acceptance targets (targets, NOT measured results)

- In a moderated first-time test, a user can find a supported municipality and open one official supporting source within 3 minutes.
- At viewport widths 375px, 390px and 768px, core search and navigation work without unwanted horizontal page scrolling.
- All primary search controls can be used with a keyboard and a Japanese IME; focus remains visible.
- UI component and graphical contrasts meet WCAG 2.2 applicable AA criteria.
- Link destinations for municipality results and source documents are checked against the generated static export.
- No unreviewed source candidates are falsely presented as Reviewed.
- First-screen language explains the user's task, not the project's internal phases.

## Change policy

Ship each iteration in a reviewable PR. Keep verification states and canonical datasets intact.
Do not automatically merge a PR when accessibility, usability, build, or reviewed-data boundaries remain unverified.
