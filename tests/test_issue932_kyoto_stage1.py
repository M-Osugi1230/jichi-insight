"""Issue #932: Kyoto cluster stage 1 — Kyoto Prefecture registration.

Pins the reviewed package registered for Kyoto Prefecture in
cluster 12 stage 1: municipality identity, the FY2022-FY2024
ordinary-account settlements cross-checked between the MIC
settlement cards and the fiscal situation collections, the
FY2026 general-account initial budget from Bill No. 1 of the
February 2026 regular session (with the prefectural tax figure
resolved to the exact thousand-yen value in the bill's Table 1),
the current comprehensive plan review, and Governor
Nishiwaki Takatoshi's current term (2026-04-16 to 2030-04-15)
with its evidence packet.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "data" / "reviewed" / "kyoto-prefecture"
MID = "jp-local-260002"


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
    assert municipality["official_code"] == "260002"
    assert "260002" in "2000020260002"
    assert municipality["name_ja"] == "京都府"
    assert municipality["municipality_type"] == "prefecture"
    assert municipality["data_status"] == "reviewed"
    assert municipality["fiscal_years"] == [2022, 2023, 2024, 2026]
    assert municipality["last_verified_at"] == "2026-11-22"


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
        2022: (1_172_280_594_000, 1_155_652_494_000, 375_081_078_000),
        2023: (1_042_685_775_000, 1_024_886_167_000, 377_132_017_000),
        2024: (1_047_275_458_000, 1_037_555_668_000, 393_262_256_000),
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
        # The debt-reduction fund is printed as "-" (no balance) in
        # both sources in all three years, so it is not a component.
        assert {b["key"] for b in fund} == {
            "fiscal_adjustment_fund",
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
        assert "miscellaneous_expenditures" not in purpose_keys
        assert "prior_year_advance_appropriation" not in purpose_keys
        assert "special_ward_fiscal_adjustment_grant" not in purpose_keys
        nature_keys = {b["key"] for b in by_metric["expenditure_by_nature"]["breakdown"]}
        assert "prior_year_advance_appropriation" not in nature_keys
        assert "unemployment_relief_project" not in nature_keys
    fy2024_purpose = {
        b["key"] for b in settlement(2024)["expenditure_by_purpose"]["breakdown"]
    }
    assert "automobile_acquisition_tax_grant" not in fy2024_purpose


def test_settlement_ratios_are_published_values() -> None:
    fy2024 = settlement(2024)
    assert fy2024["current_balance_ratio"]["value"] == 93.5
    assert fy2024["real_debt_service_ratio"]["value"] == 17.1
    assert fy2024["future_burden_ratio"]["value"] == 257.2
    assert fy2024["fiscal_strength_index"]["value"] == 0.58058
    assert fy2024["real_balance_ratio"]["value"] == 0.9
    assert fy2024["population"]["value"] == 2_472_013


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
            f"kyoto-prefecture-mic-settlement-card-fy{packet['subject_id'].split('-')[4]}",
            (
                "kyoto-prefecture-fiscal-situation-collection-fy"
                f"{packet['subject_id'].split('-')[4]}"
            ),
        ]


def test_fy2026_initial_budget_records() -> None:
    records = load_json(PKG / "fiscal_records.json")
    assert len(records) == 3
    by_metric = {r["metric"]: r for r in records}
    assert by_metric["total_revenue"]["amount_yen"] == 1_043_260_000_000
    assert by_metric["total_expenditure"]["amount_yen"] == 1_043_260_000_000
    # The prefectural tax figure is the exact thousand-yen value
    # printed in Table 1 of Bill No. 1 (the budget outline only
    # gives the million-yen level).
    assert by_metric["local_tax"]["amount_yen"] == 314_000_000_000
    for record in records:
        assert record["municipality_id"] == MID
        assert record["stage"] == "initial_budget"
        assert record["account_type"] == "general"
        assert record["period_start"] == "2026-04-01"
        assert record["period_end"] == "2027-03-31"
        assert "原案可決" in record["note"]
        assert "2026年3月12日" in record["note"]
    packets = load_json(PKG / "evidence_packets.json")
    assert len(packets) == 3
    assert {p["subject_id"] for p in packets} == {r["id"] for r in records}


def test_plan_review_records() -> None:
    review = load_json(PKG / "plan_review.json")
    assert review["official_code"] == "260002"
    assert review["review_status"] == "reviewed"
    roles = {r["evidence_role"] for r in review["records"]}
    assert roles == {
        "current_plan_identity",
        "policy_structure",
        "implementation_layer",
        "progress_governance",
    }
    joined = " ".join(r["statement"] for r in review["records"])
    assert "京都府総合計画" in joined
    assert "20" in joined  # twenty field-by-field basic policies


def test_governor_term_registration() -> None:
    terms = load_json(ROOT / "data" / "entities" / "executives" / "executive_terms.json")
    term = next(t for t in terms if t["municipality_id"] == MID)
    assert term["id"] == "jp-local-260002-executive-2026-04-16"
    assert term["office"] == "governor"
    assert term["person_name"] == "西脇 隆俊"
    assert term["term_start"] == "2026-04-16"
    assert term["term_end"] == "2030-04-15"
    assert term["election_date"] == "2026-04-05"
    assert term["status"] == "current"
    # Promises are registered in the promise stage, not here.
    # Stage 3 (Issue #938) then transcribed the bulletin manuscript
    # and registered it as the term's manifesto source.
    assert term["manifesto_source_ids"] == [
        "kyoto-pref-governor-election-2026-bulletin"
    ]
    assert len(term["sources"]) == 5

    packets = load_json(ROOT / "data" / "entities" / "executives" / "evidence_packets.json")
    packet = next(p for p in packets if p["subject_id"] == term["id"])
    election_claim = next(c for c in packet["claims"] if c["field"] == "election_date")
    assert "412,583票" in election_claim["statement"]
    proclamation = next(
        c for c in packet["claims"] if c["field"] == "election_proclamation_date"
    )
    assert "2026年3月19日" in proclamation["statement"]
    assert packet["open_questions"]


def test_finance_source_catalog_shape() -> None:
    catalog = load_json(ROOT / "data" / "catalog" / "kyoto_prefecture_finance_sources.json")
    assert catalog["scope"] == "cluster12-kyoto-deep-dive"
    assert len(catalog["records"]) == 12
    assert all(r["municipality_key"] == "kyoto-prefecture" for r in catalog["records"])
    assert all(r["review_status"] == "reviewed" for r in catalog["records"])
