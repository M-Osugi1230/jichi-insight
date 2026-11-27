"""Issue #1070: Iwate cluster stage 1 — Iwate Prefecture registration.

Pins the reviewed package registered for Iwate Prefecture in
cluster 19 stage 1: municipality identity, the FY2022-FY2024
ordinary-account settlements cross-checked between the MIC
settlement cards and the fiscal situation collections published
for Iwate on the MIC site (with the cross-check design limit
recorded: both systems rest on the same national settlement
statistics, so the check detects transcription errors but is
not an independent verification of the statistics themselves),
the FY2026 general-account initial budget from Bill No. 1 of
the February 2026 regular session (passed 2026-03-23, result
stated verbatim as 「意見を付し原案可決」 in the assembly's
bill list), the current prefectural plan review, and Governor
Tasso Takuya's current term (2023-09-11 to 2027-09-10) with its
evidence packet. The governor's vote count (336,502) is the
prefectural total in the election commission's ballot-count
form; no press figure is used. The 2023 election bulletin no
longer appears on the commission's current official pages, so
the search record registers the surviving copy on an
election-information CDN with the digest-collation limit
recorded. Iwate Prefecture had no earlier reviewed
registration in this repository, so the package is a new
registration and nothing was replaced.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "data" / "reviewed" / "iwate-prefecture"
MID = "jp-local-030007"
BULLETIN = "iwate-pref-governor-election-2023-bulletin"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def settlement(fiscal_year: int) -> dict[str, dict]:
    records = load_json(PKG / "settlement_records.json")
    return {
        r["metric"]: r
        for r in records
        if r["municipality_id"] == MID and r["fiscal_year"] == fiscal_year
    }


def test_municipality_identity() -> None:
    municipality = load_json(PKG / "municipality.json")
    assert municipality["id"] == MID
    assert municipality["official_code"] == "030007"
    assert municipality["name_ja"] == "岩手県"
    assert municipality["municipality_type"] == "prefecture"
    assert municipality["data_status"] == "reviewed"
    assert municipality["fiscal_years"] == [2022, 2023, 2024, 2026]
    assert municipality["last_verified_at"] == "2026-11-27"


def test_settlement_record_count_and_coverage() -> None:
    records = load_json(PKG / "settlement_records.json")
    assert len(records) == 51
    assert {r["fiscal_year"] for r in records} == {2022, 2023, 2024}
    assert all(r["municipality_id"] == MID for r in records)
    assert all(r["account_type"] == "ordinary" for r in records)
    assert all(r["review_status"] == "reviewed" for r in records)
    ids = [r["id"] for r in records]
    assert len(set(ids)) == 51


def test_settlement_headline_values() -> None:
    expected = {
        2022: (879_040_072_000, 824_677_066_000, 168_825_953_000),
        2023: (809_515_999_000, 756_669_461_000, 168_353_665_000),
        2024: (804_926_643_000, 757_986_980_000, 171_488_007_000),
    }
    for year, (revenue, expenditure, tax) in expected.items():
        by_metric = settlement(year)
        assert by_metric["total_revenue"]["amount_yen"] == revenue
        assert by_metric["total_expenditure"]["amount_yen"] == expenditure
        assert by_metric["local_tax"]["amount_yen"] == tax


def test_settlement_arithmetic_identity() -> None:
    for year in (2022, 2023, 2024):
        by_metric = settlement(year)
        revenue = by_metric["total_revenue"]["amount_yen"]
        expenditure = by_metric["total_expenditure"]["amount_yen"]
        assert revenue - expenditure == by_metric["formal_balance"]["amount_yen"]
        formal = by_metric["formal_balance"]["amount_yen"]
        carryover = by_metric["carryover_resources"]["amount_yen"]
        assert formal - carryover == by_metric["real_balance"]["amount_yen"]
        purpose = by_metric["expenditure_by_purpose"]["breakdown"]
        assert sum(b["amount_yen"] for b in purpose) == expenditure
        nature = by_metric["expenditure_by_nature"]["breakdown"]
        # Parent category rows coexist with their children; only the
        # top-level rows sum to the total.
        top_level = [b for b in nature if b["parent_key"] is None]
        assert sum(b["amount_yen"] for b in top_level) == expenditure
        fund = by_metric["fund_balance"]["breakdown"]
        assert sum(b["amount_yen"] for b in fund) == by_metric["fund_balance"]["amount_yen"]
        assert {b["key"] for b in fund} == {
            "fiscal_adjustment_fund",
            "debt_redemption_fund",
            "other_specific_purpose_funds",
        }
        debt = by_metric["debt_balance"]["breakdown"]
        assert sum(b["amount_yen"] for b in debt) == by_metric["debt_balance"]["amount_yen"]
        # The excluding-temporary-fiscal-bonds row is the printed
        # value in each collection's summary table.
        excl = next(
            b["amount_yen"] for b in debt if b["key"] == "bonds_excluding_temporary_fiscal"
        )
        assert excl == {
            2022: 825_655_909_000,
            2023: 822_117_329_000,
            2024: 821_673_749_000,
        }[year]


def test_settlement_unpublished_categories_are_not_invented() -> None:
    for year in (2022, 2023, 2024):
        by_metric = settlement(year)
        purpose_keys = {b["key"] for b in by_metric["expenditure_by_purpose"]["breakdown"]}
        # Printed as "-" in both sources; never zero-filled.
        assert "fire_service" not in purpose_keys
        assert "prior_year_advance_appropriation" not in purpose_keys
        assert "separate_taxation_allocation_grant" not in purpose_keys
        assert "special_local_consumption_tax_grant" not in purpose_keys
        assert "light_oil_tax_grant" not in purpose_keys
        assert "special_ward_fiscal_adjustment_grant" not in purpose_keys
        nature_keys = {b["key"] for b in by_metric["expenditure_by_nature"]["breakdown"]}
        assert "prior_year_advance_appropriation" not in nature_keys
        assert "unemployment_relief_project" not in nature_keys
    # The special local consumption tax grant is printed as "-" in
    # FY2022/FY2023, and the FY2024 card has no such row at all;
    # the FY2024 record's note states this explicitly.
    fy2024_purpose_note = settlement(2024)["expenditure_by_purpose"]["note"]
    assert "区分自体が存在しない" in fy2024_purpose_note
    # FY2023 carries small printed values for miscellaneous
    # expenditures and the automobile acquisition tax grant.
    fy2023 = {
        b["key"]: b["amount_yen"]
        for b in settlement(2023)["expenditure_by_purpose"]["breakdown"]
    }
    assert fy2023["miscellaneous_expenditures"] == 5_167_000
    assert fy2023["automobile_acquisition_tax_grant"] == 40_956_000


def test_settlement_ratios_are_published_values() -> None:
    fy2024 = settlement(2024)
    assert fy2024["current_balance_ratio"]["value"] == 93.2
    assert fy2024["real_debt_service_ratio"]["value"] == 12.3
    assert fy2024["future_burden_ratio"]["value"] == 196.8
    assert fy2024["fiscal_strength_index"]["value"] == 0.36343
    assert fy2024["real_balance_ratio"]["value"] == 3.1
    assert fy2024["population"]["value"] == 1_153_900
    # The labelled current-balance ratio is used, not the
    # parenthesised variant printed on the following row.
    assert settlement(2023)["current_balance_ratio"]["value"] == 92.6


def test_settlement_evidence_packets_cover_every_record() -> None:
    records = load_json(PKG / "settlement_records.json")
    packets = load_json(PKG / "settlement_evidence_packets.json")
    assert len(packets) == 51
    assert {p["subject_id"] for p in packets} == {r["id"] for r in records}
    for packet in packets:
        assert packet["review_status"] == "reviewed"
        claim = packet["claims"][0]
        assert claim["decision"] == "accepted"
        assert claim["source_ids"] == [
            f"iwate-prefecture-mic-settlement-card-fy{packet['subject_id'].split('-')[4]}",
            (
                "iwate-prefecture-fiscal-situation-collection-fy"
                f"{packet['subject_id'].split('-')[4]}"
            ),
        ]
        # The cross-check design limit is recorded in every packet:
        # both systems rest on the same settlement statistics.
        assert any("同一の決算統計" in q for q in packet["open_questions"])


def test_fy2026_initial_budget_records() -> None:
    records = load_json(PKG / "fiscal_records.json")
    assert len(records) == 3
    by_metric = {r["metric"]: r for r in records}
    assert by_metric["total_revenue"]["amount_yen"] == 774_233_557_000
    assert by_metric["total_expenditure"]["amount_yen"] == 774_233_557_000
    assert by_metric["local_tax"]["amount_yen"] == 135_788_000_000
    for record in records:
        assert record["municipality_id"] == MID
        assert record["stage"] == "initial_budget"
        assert record["account_type"] == "general"
        assert record["period_start"] == "2026-04-01"
        assert record["period_end"] == "2027-03-31"
    # The result is stated verbatim as 「意見を付し原案可決」 on
    # 2026-03-23 in the assembly's bill list; it is never shortened
    # to 「原案可決」.
    revenue_note = by_metric["total_revenue"]["note"]
    assert "「意見を付し原案可決」" in revenue_note
    assert "2026年3月23日" in revenue_note
    # The tax figure is confirmed at the printed thousand-yen
    # value in the budget explanation document and left unchanged
    # by supplementary budget (No. 2).
    assert "補正の対象外" in by_metric["local_tax"]["note"]
    packets = load_json(PKG / "evidence_packets.json")
    assert len(packets) == 3
    assert {p["subject_id"] for p in packets} == {r["id"] for r in records}


def test_plan_review_records() -> None:
    review = load_json(PKG / "plan_review.json")
    assert review["official_code"] == "030007"
    assert review["review_status"] == "reviewed"
    roles = {r["evidence_role"] for r in review["records"]}
    assert roles == {
        "current_plan_identity",
        "policy_structure",
        "implementation_layer",
        "progress_governance",
    }
    joined = " ".join(r["statement"] for r in review["records"])
    assert "いわて県民計画（2019～2028）" in joined
    assert "10の政策分野" in joined
    assert "いわて幸福関連指標" in joined
    assert "復興推進プラン" in joined
    assert "政策推進プラン" in joined


def test_governor_term_registration() -> None:
    terms = load_json(ROOT / "data" / "entities" / "executives" / "executive_terms.json")
    term = next(t for t in terms if t["municipality_id"] == MID)
    assert term["id"] == "jp-local-030007-executive-2023-09-11"
    assert term["office"] == "governor"
    assert term["person_name"] == "達増 拓也"
    assert term["term_start"] == "2023-09-11"
    assert term["term_end"] == "2027-09-10"
    assert term["election_date"] == "2023-09-03"
    assert term["status"] == "current"
    # The 2023 bulletin survives only as a copy on an
    # election-information CDN; it is registered as the manifesto
    # source with the collation limit recorded, and promise
    # extraction itself is deferred to stage 3.
    assert term["manifesto_source_ids"] == [BULLETIN]
    assert len(term["sources"]) == 5

    packets = load_json(ROOT / "data" / "entities" / "executives" / "evidence_packets.json")
    packet = next(p for p in packets if p["subject_id"] == term["id"])
    election_claim = next(c for c in packet["claims"] if c["field"] == "election_date")
    # The vote count is the prefectural total in the election
    # commission's official ballot-count form.
    assert "336,502票" in election_claim["statement"]
    term_end_claims = [c for c in packet["claims"] if c["field"] == "term_end"]
    assert len(term_end_claims) == 1
    assert "2027年9月10日" in term_end_claims[0]["statement"]
    assert packet["open_questions"]


def test_manifesto_source_search_registration() -> None:
    searches = load_json(
        ROOT / "data" / "entities" / "executives" / "manifesto_source_searches.json"
    )
    search = next(
        s for s in searches if s["executive_term_id"] == "jp-local-030007-executive-2023-09-11"
    )
    assert search["result_status"] == "source_registered"
    assert search["manifesto_source_ids_found"] == [BULLETIN]
    assert search["nonexistence_claim"] is False
    # The record is honest about the official pages: the bulletin
    # could not be found on the commission's current pages and
    # the registered copy could not be digest-collated.
    assert "確認できなかった" in search["review_note"]
    assert "ダイジェスト" in search["review_note"]


def test_finance_source_catalog_shape() -> None:
    catalog = load_json(ROOT / "data" / "catalog" / "iwate_prefecture_finance_sources.json")
    assert catalog["scope"] == "cluster19-iwate-deep-dive"
    assert len(catalog["records"]) == 15
    assert all(r["municipality_key"] == "iwate-prefecture" for r in catalog["records"])
    assert all(r["review_status"] == "reviewed" for r in catalog["records"])
