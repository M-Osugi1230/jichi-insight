"""Issue #1012: Fukushima cluster stage 1 — Fukushima Prefecture registration.

Pins the reviewed package registered for Fukushima Prefecture in
cluster 16 stage 1: municipality identity, the FY2022-FY2024
ordinary-account settlements cross-checked between the MIC
settlement cards and the fiscal situation collections published
by the prefecture itself (with the cross-check design limit
recorded: both systems rest on the same national settlement
statistics, so the check detects transcription errors but is not
an independent verification of the statistics themselves), the
FY2026 general-account initial budget from Bill No. 1 of the
February 2026 regular session (passed 2026-03-19, result stated
verbatim as 「原案可決」), the current comprehensive plan review,
and Governor Uchibori Masao's current term (2026-11-12 to
2030-11-11) with its evidence packet. The governor's vote count
(585,641) is the prefectural total in the final ballot-count
file published on the election commission's official results
site; no press figure is used. Fukushima Prefecture had no
earlier reviewed registration in this repository, so the package
is a new registration and nothing was replaced.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "data" / "reviewed" / "fukushima-prefecture"
MID = "jp-local-070009"
BULLETIN = "fukushima-pref-governor-election-2026-bulletin"


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
    assert municipality["official_code"] == "070009"
    assert "070009" in "7000020070009"
    assert municipality["name_ja"] == "福島県"
    assert municipality["municipality_type"] == "prefecture"
    assert municipality["data_status"] == "reviewed"
    assert municipality["fiscal_years"] == [2022, 2023, 2024, 2026]
    assert municipality["last_verified_at"] == "2026-11-26"


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
        2022: (1_344_287_454_000, 1_306_838_789_000, 298_171_646_000),
        2023: (1_257_263_227_000, 1_224_298_248_000, 301_967_791_000),
        2024: (1_191_872_923_000, 1_152_505_464_000, 301_357_477_000),
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


def test_settlement_unpublished_categories_are_not_invented() -> None:
    for year in (2022, 2023, 2024):
        by_metric = settlement(year)
        purpose_keys = {b["key"] for b in by_metric["expenditure_by_purpose"]["breakdown"]}
        # Printed as "-" in both sources; never zero-filled.
        assert "fire_service" not in purpose_keys
        assert "miscellaneous_expenditures" not in purpose_keys
        assert "prior_year_advance_appropriation" not in purpose_keys
        assert "separate_taxation_allocation_grant" not in purpose_keys
        assert "light_oil_tax_grant" not in purpose_keys
        assert "special_ward_fiscal_adjustment_grant" not in purpose_keys
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
    assert fy2024["current_balance_ratio"]["value"] == 95.8
    assert fy2024["real_debt_service_ratio"]["value"] == 6.0
    assert fy2024["future_burden_ratio"]["value"] == 115.3
    assert fy2024["fiscal_strength_index"]["value"] == 0.51927
    assert fy2024["real_balance_ratio"]["value"] == 1.5
    assert fy2024["population"]["value"] == 1_771_314


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
            f"fukushima-prefecture-mic-settlement-card-fy{packet['subject_id'].split('-')[4]}",
            (
                "fukushima-prefecture-fiscal-situation-collection-fy"
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
    assert by_metric["total_revenue"]["amount_yen"] == 1_260_607_000_000
    assert by_metric["total_expenditure"]["amount_yen"] == 1_260_607_000_000
    assert by_metric["local_tax"]["amount_yen"] == 241_794_000_000
    for record in records:
        assert record["municipality_id"] == MID
        assert record["stage"] == "initial_budget"
        assert record["account_type"] == "general"
        assert record["period_start"] == "2026-04-01"
        assert record["period_end"] == "2027-03-31"
    # The result is stated verbatim as 「原案可決」 on 2026-03-19.
    revenue_note = by_metric["total_revenue"]["note"]
    assert "「原案可決」" in revenue_note
    assert "2026年3月19日" in revenue_note
    # The tax figure is cross-checked against the supplementary
    # budget (No. 2) itemised statement's pre-revision amount.
    assert "補正前の額" in by_metric["local_tax"]["note"]
    packets = load_json(PKG / "evidence_packets.json")
    assert len(packets) == 3
    assert {p["subject_id"] for p in packets} == {r["id"] for r in records}


def test_plan_review_records() -> None:
    review = load_json(PKG / "plan_review.json")
    assert review["official_code"] == "070009"
    assert review["review_status"] == "reviewed"
    roles = {r["evidence_role"] for r in review["records"]}
    assert roles == {
        "current_plan_identity",
        "policy_structure",
        "implementation_layer",
        "progress_governance",
    }
    joined = " ".join(r["statement"] for r in review["records"])
    assert "福島県総合計画" in joined
    assert "18政策" in joined
    assert "ふくしま創生総合戦略" in joined
    assert "第2期福島県復興計画" in joined


def test_governor_term_registration() -> None:
    terms = load_json(ROOT / "data" / "entities" / "executives" / "executive_terms.json")
    term = next(t for t in terms if t["municipality_id"] == MID)
    assert term["id"] == "jp-local-070009-executive-2026-11-12"
    assert term["office"] == "governor"
    assert term["person_name"] == "内堀 雅雄"
    assert term["term_start"] == "2026-11-12"
    assert term["term_end"] == "2030-11-11"
    assert term["election_date"] == "2026-10-25"
    assert term["status"] == "current"
    # The 2026 bulletin survives on the election commission's
    # current official pages and is registered as the manifesto
    # source; promise extraction itself is deferred to stage 3.
    assert term["manifesto_source_ids"] == [BULLETIN]
    assert len(term["sources"]) == 5

    packets = load_json(ROOT / "data" / "entities" / "executives" / "evidence_packets.json")
    packet = next(p for p in packets if p["subject_id"] == term["id"])
    election_claim = next(c for c in packet["claims"] if c["field"] == "election_date")
    # The vote count is the prefectural total in the election
    # commission's official final ballot-count file.
    assert "585,641票" in election_claim["statement"]
    assert "44.05%" in election_claim["statement"]
    term_end_claims = [c for c in packet["claims"] if c["field"] == "term_end"]
    assert len(term_end_claims) == 1
    assert "2030年11月11日" in term_end_claims[0]["statement"]
    assert packet["open_questions"]


def test_manifesto_source_search_registration() -> None:
    searches = load_json(
        ROOT / "data" / "entities" / "executives" / "manifesto_source_searches.json"
    )
    search = next(
        s for s in searches if s["executive_term_id"] == "jp-local-070009-executive-2026-11-12"
    )
    assert search["result_status"] == "source_registered"
    assert search["manifesto_source_ids_found"] == [BULLETIN]
    assert search["nonexistence_claim"] is False


def test_finance_source_catalog_shape() -> None:
    catalog = load_json(ROOT / "data" / "catalog" / "fukushima_prefecture_finance_sources.json")
    assert catalog["scope"] == "cluster16-fukushima-deep-dive"
    assert len(catalog["records"]) == 15
    assert all(r["municipality_key"] == "fukushima-prefecture" for r in catalog["records"])
    assert all(r["review_status"] == "reviewed" for r in catalog["records"])
