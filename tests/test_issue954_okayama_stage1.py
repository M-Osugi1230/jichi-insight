"""Issue #954: Okayama cluster stage 1 — Okayama Prefecture registration.

Pins the reviewed package registered for Okayama Prefecture in
cluster 14 stage 1: municipality identity, the FY2022-FY2024
ordinary-account settlements cross-checked between the MIC
settlement cards and the prefecture's fiscal situation
collections (the most verifiable prefecture-side publication
for ordinary-account values, because the prefecture's own
settlement booklet is published by account and carries no
ordinary-account indicators), the FY2026 general-account
initial budget fixed to the exact thousand-yen values in the
prefectural gazette, the current comprehensive plan review,
and Governor Ibaragi Ryuta's current term (2024-11-12 to
2028-11-11) with its evidence packet.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "data" / "reviewed" / "okayama-prefecture"
MID = "jp-local-330001"


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
    assert municipality["official_code"] == "330001"
    assert "330001" in "4000020330001"
    assert municipality["name_ja"] == "岡山県"
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
        2022: (802_008_865_000, 788_998_145_000, 275_034_434_000),
        2023: (730_821_476_000, 721_336_380_000, 268_508_917_000),
        2024: (742_640_366_000, 733_805_981_000, 291_056_131_000),
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
        # Unlike Kyoto, the debt-reduction fund has a balance in all
        # three years, so the fund balance has three components.
        assert {b["key"] for b in fund} == {
            "fiscal_adjustment_fund",
            "debt_reduction_fund",
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
        # The special local consumption tax grant is printed as "-"
        # in FY2022/FY2023 and has no row at all in FY2024.
        assert "special_local_consumption_tax_grant" not in purpose_keys
        nature_keys = {b["key"] for b in by_metric["expenditure_by_nature"]["breakdown"]}
        assert "prior_year_advance_appropriation" not in nature_keys
        assert "unemployment_relief_project" not in nature_keys
    # The automobile acquisition tax grant has printed values in
    # FY2022/FY2023 but is "-" in FY2024.
    assert "automobile_acquisition_tax_grant" in {
        b["key"] for b in settlement(2022)["expenditure_by_purpose"]["breakdown"]
    }
    assert "automobile_acquisition_tax_grant" not in {
        b["key"] for b in settlement(2024)["expenditure_by_purpose"]["breakdown"]
    }


def test_settlement_disaster_recovery_printed_difference_is_kept() -> None:
    # The purpose and nature tables print slightly different
    # disaster recovery amounts in both sources; each table's
    # printed value is registered as printed, never harmonised.
    expected = {
        2022: (1_564_255_000, 1_564_250_000),
        2023: (1_586_336_000, 1_586_334_000),
        2024: (2_657_641_000, 2_657_640_000),
    }
    for year, (purpose_value, nature_value) in expected.items():
        by_metric = settlement(year)
        purpose = {
            b["key"]: b["amount_yen"]
            for b in by_metric["expenditure_by_purpose"]["breakdown"]
        }
        nature = {
            b["key"]: b["amount_yen"]
            for b in by_metric["expenditure_by_nature"]["breakdown"]
        }
        assert purpose["disaster_recovery"] == purpose_value
        assert nature["disaster_recovery_works"] == nature_value


def test_settlement_ratios_are_published_values() -> None:
    fy2024 = settlement(2024)
    assert fy2024["current_balance_ratio"]["value"] == 94.1
    assert fy2024["real_debt_service_ratio"]["value"] == 10.9
    assert fy2024["future_burden_ratio"]["value"] == 157.5
    assert fy2024["fiscal_strength_index"]["value"] == 0.52853
    assert fy2024["real_balance_ratio"]["value"] == 0.4
    assert fy2024["population"]["value"] == 1_835_478


def test_settlement_evidence_packets_cover_every_record() -> None:
    records = load_json(PKG / "settlement_records.json")
    packets = load_json(PKG / "settlement_evidence_packets.json")
    assert len(packets) == 51
    assert {p["subject_id"] for p in packets} == {r["id"] for r in records}
    for packet in packets:
        assert packet["review_status"] == "reviewed"
        claim = packet["claims"][0]
        assert claim["decision"] == "accepted"
        year = packet["subject_id"].split("-")[4]
        assert claim["source_ids"] == [
            f"okayama-prefecture-mic-settlement-card-fy{year}",
            f"okayama-prefecture-fiscal-situation-collection-fy{year}",
        ]
        # The choice of the second source system and its rationale
        # are recorded in every packet.
        assert any("財政状況資料集" in q for q in packet["open_questions"])


def test_fy2026_initial_budget_records() -> None:
    records = load_json(PKG / "fiscal_records.json")
    assert len(records) == 3
    by_metric = {r["metric"]: r for r in records}
    assert by_metric["total_revenue"]["amount_yen"] == 819_698_359_000
    assert by_metric["total_expenditure"]["amount_yen"] == 819_698_359_000
    # The prefectural tax figure is the exact thousand-yen value
    # printed in Table 1 of the budget as promulgated in the
    # prefectural gazette (Notice No. 129, Extra of 2026-03-19).
    assert by_metric["local_tax"]["amount_yen"] == 280_362_922_000
    for record in records:
        assert record["municipality_id"] == MID
        assert record["stage"] == "initial_budget"
        assert record["account_type"] == "general"
        assert record["period_start"] == "2026-04-01"
        assert record["period_end"] == "2027-03-31"
        assert "原案可決" in record["note"]
        assert "2026年3月19日" in record["note"]
        assert "県告示第129号" in record["note"]
    packets = load_json(PKG / "evidence_packets.json")
    assert len(packets) == 3
    assert {p["subject_id"] for p in packets} == {r["id"] for r in records}


def test_plan_review_records() -> None:
    review = load_json(PKG / "plan_review.json")
    assert review["official_code"] == "330001"
    assert review["review_status"] == "reviewed"
    roles = {r["evidence_role"] for r in review["records"]}
    assert roles == {
        "current_plan_identity",
        "policy_structure",
        "implementation_layer",
        "progress_governance",
    }
    joined = " ".join(r["statement"] for r in review["records"])
    assert "第4次晴れの国おかやま生き活きプラン" in joined
    assert "22" in joined  # twenty-two strategy programmes
    assert "99" in joined  # ninety-nine Iki-iki indicators


def test_governor_term_registration() -> None:
    terms = load_json(ROOT / "data" / "entities" / "executives" / "executive_terms.json")
    term = next(t for t in terms if t["municipality_id"] == MID)
    assert term["id"] == "jp-local-330001-executive-2024-11-12"
    assert term["office"] == "governor"
    assert term["person_name"] == "伊原木 隆太"
    assert term["term_start"] == "2024-11-12"
    assert term["term_end"] == "2028-11-11"
    assert term["election_date"] == "2024-10-27"
    assert term["status"] == "current"
    # The 2024 election bulletin was issued, but its presence on
    # the election commission's current site is unconfirmed, so
    # the manifesto sources stay empty until stage 3 re-checks.
    assert term["manifesto_source_ids"] == []
    assert len(term["sources"]) == 5

    packets = load_json(ROOT / "data" / "entities" / "executives" / "evidence_packets.json")
    packet = next(p for p in packets if p["subject_id"] == term["id"])
    election_claim = next(c for c in packet["claims"] if c["field"] == "election_date")
    # The commission's own count is 634,587 votes; the 634,586
    # figure in Wikipedia's governor list is wrong.
    assert "634,587票" in election_claim["statement"]
    proclamation = next(
        c for c in packet["claims"] if c["field"] == "election_proclamation_date"
    )
    assert "2024年10月10日" in proclamation["statement"]
    assert packet["open_questions"]


def test_finance_source_catalog_shape() -> None:
    catalog = load_json(ROOT / "data" / "catalog" / "okayama_prefecture_finance_sources.json")
    assert catalog["scope"] == "cluster14-okayama-deep-dive"
    assert len(catalog["records"]) == 11
    assert all(r["municipality_key"] == "okayama-prefecture" for r in catalog["records"])
    assert all(r["review_status"] == "reviewed" for r in catalog["records"])
