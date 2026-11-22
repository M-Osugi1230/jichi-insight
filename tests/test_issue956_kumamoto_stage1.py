"""Issue #956: Kumamoto cluster stage 1 — Kumamoto Prefecture registration.

Pins the reviewed package registered for Kumamoto Prefecture in
cluster 15 stage 1: municipality identity, the FY2022-FY2024
ordinary-account settlements cross-checked between the MIC
settlement cards and the fiscal situation collections (with the
cross-check design limit recorded: the prefecture's own
collection page republishes MIC data, so the check runs between
the two MIC publications), the FY2026 general-account initial
budget from Bill No. 46 of the February 2026 regular session
(with the prefectural tax figure resolved to the exact
thousand-yen value by visual transcription of the image-only
bill PDF and cross-checked against the June 2026 supplementary
bill's Table 1), the current basic policy / comprehensive
strategy review, and Governor Kimura Takashi's current term
(2024-04-16 to 2028-04-15) with its evidence packet.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "data" / "reviewed" / "kumamoto-prefecture"
MID = "jp-local-430005"


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
    assert municipality["official_code"] == "430005"
    assert "430005" in "7000020430005"
    assert municipality["name_ja"] == "熊本県"
    assert municipality["municipality_type"] == "prefecture"
    assert municipality["data_status"] == "reviewed"
    assert municipality["fiscal_years"] == [2022, 2023, 2024, 2026]
    assert municipality["last_verified_at"] == "2026-11-23"


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
        2022: (1_028_620_307_000, 978_345_151_000, 224_737_382_000),
        2023: (954_296_621_000, 903_825_031_000, 225_860_631_000),
        2024: (922_220_421_000, 880_334_474_000, 239_929_033_000),
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
        # Unlike Kyoto, the debt-reduction fund carries a balance in
        # all three years, so the fund balance has three components.
        assert {b["key"] for b in fund} == {
            "fiscal_adjustment_fund",
            "debt_redemption_fund",
            "other_specific_purpose_funds",
        }
        debt = by_metric["debt_balance"]["breakdown"]
        assert sum(b["amount_yen"] for b in debt) == by_metric["debt_balance"]["amount_yen"]


def test_settlement_unpublished_categories_are_not_invented() -> None:
    for year in (2022, 2023, 2024):
        by_metric = settlement(year)
        purpose_keys = {b["key"] for b in by_metric["expenditure_by_purpose"]["breakdown"]}
        # Printed as "-" in both sources; never zero-filled.
        assert "fire_service" not in purpose_keys
        assert "prior_year_advance_appropriation" not in purpose_keys
        assert "special_ward_fiscal_adjustment_grant" not in purpose_keys
        # Miscellaneous expenditures carry printed values in Kumamoto.
        assert "miscellaneous_expenditures" in purpose_keys
        nature_keys = {b["key"] for b in by_metric["expenditure_by_nature"]["breakdown"]}
        assert "prior_year_advance_appropriation" not in nature_keys
        assert "unemployment_relief_project" not in nature_keys
    # The automobile acquisition tax grant is "-" in FY2022/FY2024
    # but carries a printed value in FY2023.
    for year in (2022, 2024):
        purpose_keys = {
            b["key"] for b in settlement(year)["expenditure_by_purpose"]["breakdown"]
        }
        assert "automobile_acquisition_tax_grant" not in purpose_keys
    fy2023_purpose = {
        b["key"] for b in settlement(2023)["expenditure_by_purpose"]["breakdown"]
    }
    assert "automobile_acquisition_tax_grant" in fy2023_purpose


def test_settlement_ratios_are_published_values() -> None:
    fy2024 = settlement(2024)
    assert fy2024["current_balance_ratio"]["value"] == 91.5
    assert fy2024["real_debt_service_ratio"]["value"] == 8.9
    assert fy2024["future_burden_ratio"]["value"] == 212.5
    assert fy2024["fiscal_strength_index"]["value"] == 0.42277
    assert fy2024["real_balance_ratio"]["value"] == 4.8
    assert fy2024["population"]["value"] == 1_716_360


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
            f"kumamoto-prefecture-mic-settlement-card-fy{packet['subject_id'].split('-')[4]}",
            (
                "kumamoto-prefecture-fiscal-situation-collection-fy"
                f"{packet['subject_id'].split('-')[4]}"
            ),
        ]
        # The cross-check design limit is recorded in every packet:
        # the prefecture's collection page republishes MIC data, so
        # it is not an independent second system.
        assert any("転載" in q for q in packet["open_questions"])


def test_fy2026_initial_budget_records() -> None:
    records = load_json(PKG / "fiscal_records.json")
    assert len(records) == 3
    by_metric = {r["metric"]: r for r in records}
    assert by_metric["total_revenue"]["amount_yen"] == 935_335_562_000
    assert by_metric["total_expenditure"]["amount_yen"] == 935_335_562_000
    # The prefectural tax figure is the exact thousand-yen value
    # printed in Table 1 of Bill No. 46 (the budget outline only
    # gives the million-yen level).
    assert by_metric["local_tax"]["amount_yen"] == 177_985_266_000
    for record in records:
        assert record["municipality_id"] == MID
        assert record["stage"] == "initial_budget"
        assert record["account_type"] == "general"
        assert record["period_start"] == "2026-04-01"
        assert record["period_end"] == "2027-03-31"
        # The result is stated verbatim as 「可決」, not 「原案可決」.
        assert "「可決」" in record["note"]
        assert "原案可決" not in record["note"]
        assert "2026年3月18日" in record["note"]
    packets = load_json(PKG / "evidence_packets.json")
    assert len(packets) == 3
    assert {p["subject_id"] for p in packets} == {r["id"] for r in records}


def test_plan_review_records() -> None:
    review = load_json(PKG / "plan_review.json")
    assert review["official_code"] == "430005"
    assert review["review_status"] == "reviewed"
    roles = {r["evidence_role"] for r in review["records"]}
    assert roles == {
        "current_plan_identity",
        "policy_structure",
        "implementation_layer",
        "progress_governance",
    }
    joined = " ".join(r["statement"] for r in review["records"])
    assert "くまもと新時代共創基本方針" in joined
    assert "くまもと新時代共創総合戦略" in joined
    assert "OODA" in joined


def test_governor_term_registration() -> None:
    terms = load_json(ROOT / "data" / "entities" / "executives" / "executive_terms.json")
    term = next(t for t in terms if t["municipality_id"] == MID)
    assert term["id"] == "jp-local-430005-executive-2024-04-16"
    assert term["office"] == "governor"
    assert term["person_name"] == "木村 敬"
    assert term["term_start"] == "2024-04-16"
    assert term["term_end"] == "2028-04-15"
    assert term["election_date"] == "2024-03-24"
    assert term["status"] == "current"
    # Promises are registered in the promise stage, not here; the
    # 2024 bulletin has not been located on the commission's current
    # pages, so no manifesto source is registered yet.
    assert term["manifesto_source_ids"] == []
    assert len(term["sources"]) == 5

    packets = load_json(ROOT / "data" / "entities" / "executives" / "evidence_packets.json")
    packet = next(p for p in packets if p["subject_id"] == term["id"])
    election_claim = next(c for c in packet["claims"] if c["field"] == "election_date")
    assert "383,010票" in election_claim["statement"]
    assert "49.63%" in election_claim["statement"]
    term_end_claim = next(c for c in packet["claims"] if c["field"] == "term_end")
    assert "令和10年4月15日" in term_end_claim["statement"]
    assert packet["open_questions"]


def test_finance_source_catalog_shape() -> None:
    catalog = load_json(ROOT / "data" / "catalog" / "kumamoto_prefecture_finance_sources.json")
    assert catalog["scope"] == "cluster15-kumamoto-deep-dive"
    assert len(catalog["records"]) == 14
    assert all(r["municipality_key"] == "kumamoto-prefecture" for r in catalog["records"])
    assert all(r["review_status"] == "reviewed" for r in catalog["records"])
