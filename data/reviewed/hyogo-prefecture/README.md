# Hyogo Prefecture reviewed package

Scope: Hyogo cluster stage 1 (Issue #854) — entity identity, the
current plan review, the FY2026 general-account initial budget, the
FY2022-FY2024 ordinary-account settlements and the governor's current
term.

- Municipality: 兵庫県 (`jp-local-280003`, official code 280003), as
  carried by the MIC settlement cards and the fiscal situation
  collections. The prefecture's official pages print the corporate
  number 8000020280003, whose last six digits match the code.
- FY2026 initial budget: general account 2,318,223,000 thousand yen
  and prefectural tax revenue 909,400,000 thousand yen, from Bill
  No. 1 of the 374th regular session (第1号議案「令和8年度兵庫県
  一般会計予算」), passed as proposed on 2026-03-23 (原案可決), as
  published in the Hyogo Prefecture official gazette (兵庫県公報,
  2026-03-23 extra issue). The prefectural tax office's page states
  the tax revenue as 9,104億円, which differs from the gazette's
  enacted figure of 9,094億円 by 10億円; the gazette figure is
  registered as authoritative and the difference is recorded in the
  record's note.
- Settlements: FY2022-FY2024 ordinary-account records were
  cross-checked between two primary sources — the MIC settlement
  cards (都道府県決算カード, Hyogo sheet) and the fiscal situation
  collections (財政状況資料集) as hosted on the MIC site. All values
  agreed on every indicator except two FY2022 ratios: the real debt
  service ratio (card 15.2 vs collection 15.5) and the future burden
  ratio (card 326.4 vs collection 330.8). The card values are
  registered as authoritative and the disagreement is recorded in
  the records' notes and evidence packets; nothing was guessed or
  recomputed. Arithmetic checks (revenue − expenditure = formal
  balance; formal balance − carryover resources = real balance;
  purpose/nature breakdown sums = total expenditure; the fund
  categories sum to the fund balance) all pass. Ratios are
  registered as published, never recomputed; the labelled
  current-balance ratio is used rather than the parenthesised
  variant. Categories shown as "－" in the sources are omitted from
  the breakdowns (no value is guessed or zero-filled): 消防費・
  諸支出金・前年度繰上充用金・特別区財政調整交付金・
  特別地方消費税交付金 in every year, and 自動車取得税交付金 in
  FY2024 (it has values in FY2022-FY2023). The debt reduction fund
  (減債基金) is "－" in both sources for all three years, so its
  breakdown amount is null; the fund balance is the sum of the
  fiscal adjustment fund and the other specific-purpose funds.
- Plan: the prefecture has no fixed-term statutory comprehensive
  plan. The top layer is the long-term vision ひょうごビジョン2050
  (adopted March 2022, theme 「躍動する兵庫」), and its most
  comprehensive implementation programme is the third-term Hyogo
  Regional Creation Strategy (第三期「兵庫県地域創生戦略」,
  2025-2029, adopted March 2025) — the strategy under Article 6 of
  the Hyogo Prefecture Regional Creation Ordinance and the
  prefectural comprehensive strategy under Article 9 of the Act on
  Overcoming Population Decline and Vitalizing Local Economy. The
  strategy is structured as three pillars, eight directions and
  measures, with about 200 indicators targeted at FY2029;
  implementation runs through annual action plans, and progress is
  governed by the annual implementation status report published
  under the ordinance (the FY2025 report for the third term is
  published). The third term's evaluation format was confirmed in
  stage 2 (see below).
- Governor: 斎藤 元彦, current term 2024-11-17 to 2028-11-16. He
  first took office on 2021-08-01 (53rd governor). On 2024-09-19
  the prefectural assembly passed a unanimous no-confidence motion;
  he did not dissolve the assembly and therefore lost office on
  2024-09-30 under Article 178 of the Local Autonomy Act. The
  deputy governor acted in the interim (that acting period is not
  registered as a term). He was re-elected in the vacancy election
  of 2024-11-17 (54th governor) with 1,113,911 votes, as stated in
  the Kobe City election commission's official result record (the
  same Hyogo-wide figure appears in the Nishinomiya and Himeji
  result publications). Because this was a vacancy election, the
  term runs four years from the election day itself under the main
  text of Article 259 of the Public Offices Election Act. The
  previous term (2021) is not registered, following the treatment of
  predecessor terms in earlier clusters. The cross-check of the
  2028-11-16 expiry against the prefectural election commission's
  own term-expiry list is still outstanding and is recorded as an
  open question in the evidence packet.

Stage 2 (Issue #858) registers 10 of the third-term strategy's
policy items as reviewed projects for FY2025, the only fiscal year
whose implementation status report is published. The registration
unit is the numbered policy item (取組方針): the prefecture's own
evaluation framework labels the eight directions as the strategy's
measures (施策) and the numbered items as policy items, but
following the Chiba precedent of registering the plan's
measure-level units, the items — each with its own title, purpose
text and main initiatives — are registered. Selection cycles
through the eight directions in official publication order and
takes the items in order within each direction; it is not by
budget size (see
`data/catalog/hyogo_priority_project_selection.json`).

- The population is the strategy's 66 listed items (64 unique; two
  entries are cross-references to an item whose home is another
  direction). The second-term strategy's items are not mapped
  across versions.
- Amounts are not registered: the annual action plans list main
  projects per item with a budget per project, but no per-item
  total is published, and summing only the listed main projects
  would not give the item's total; the FY2025 implementation report
  lists main projects without amounts. `budget_records` therefore
  carries a null amount with the reason recorded (nothing is
  zero-filled).
- The prefecture publishes no per-item rating, so
  `official_evaluation` is null for every project. The third term
  keeps the second term's A–D achievement grades (A: 100% or more,
  B: 90–100%, C: 70–90%, D: below 70% of the annual target), but
  they are assigned per indicator, and the 187 indicators are set
  per direction, not per item. The direction-level aggregates are
  recorded in the evidence packets instead.
- KPIs are empty for the same reason: indicators belong to
  directions, and attaching a direction's indicators to one of its
  items would misattribute them.

Not yet published for Hyogo Prefecture:

- Governor's promises (the 2024 election bulletin is preserved on
  the Kobe City site, but its candidate columns are image-only, so
  the promise registration decision — by visual transcription —
  belongs to the cluster's promise stage)
- Assembly records
- FY2026 execution and settlement figures
