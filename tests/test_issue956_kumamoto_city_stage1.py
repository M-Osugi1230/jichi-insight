"""Issue #956 (Kumamoto City part): Kumamoto cluster stage 1.

Covers the FY2022-FY2024 ordinary-account settlements of Kumamoto
City, cross-checked field by field between the Ministry of Internal
Affairs and Communications' fiscal situation collections and the
collections the city itself publishes on its official site (the two
Excel systems agree cell by cell), and corroborated against the
city's published settlement cards. The population is registered as
of 1 January from the collections' summary tables, while the cards
print the 31 March figure. Also covers the stage-1 mayoral term
registration (current term only: the mayor was re-elected on
2026-11-15, but the new term had not begun at registration) and the
addition of the FY2026 initial budget's local tax (the total was
already registered at Phase 13 and matches the enacted budget).
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data/reviewed/kumamoto-city"
MID = "jp-local-431001"


def load_json(relative_path: str | Path):
    path = ROOT / relative_path if isinstance(relative_path, str) else relative_path
    return json.loads(path.read_text(encoding="utf-8"))


def test_kumamoto_city_identity() -> None:
    municipality = load_json(BASE / "municipality.json")

    assert municipality["id"] == MID
    assert municipality["official_code"] == "431001"
    assert municipality["name_ja"] == "熊本市"
    assert municipality["municipality_type"] == "designated_city"
    assert municipality["data_status"] == "reviewed"


def _settlement_records() -> list[dict]:
    return load_json(BASE / "settlement_records.json")


def _by_year_metric(records: list[dict]) -> dict[tuple[int, str], dict]:
    return {(r["fiscal_year"], r["metric"]): r for r in records}


def _expected_sources(fiscal_year: int) -> list[str]:
    return [
        f"kumamoto-city-mic-fiscal-situation-collection-fy{fiscal_year}",
        f"kumamoto-city-fiscal-situation-collection-fy{fiscal_year}",
    ]


def test_kumamoto_settlement_headlines() -> None:
    records = _settlement_records()
    assert len(records) == 51
    by = _by_year_metric(records)

    # Thousand-yen values as printed in the collections; stored in yen.
    expected = {
        # fiscal_year: (revenue, expenditure, local_tax, standard
        # fiscal scale, fund balance total, debt balance) in
        # thousand yen
        2022: (412805953, 403175196, 125493743, 203631086, 29090759, 500366831),
        2023: (416919228, 405529703, 128068501, 207948832, 35510535, 496140908),
        2024: (431338303, 421832522, 127753091, 214885728, 34782492, 493247935),
    }
    for fiscal_year, (
        revenue,
        expenditure,
        local_tax,
        standard_scale,
        fund_total,
        debt_total,
    ) in expected.items():
        assert by[(fiscal_year, "total_revenue")]["amount_yen"] == revenue * 1000
        assert by[(fiscal_year, "total_expenditure")]["amount_yen"] == expenditure * 1000
        assert by[(fiscal_year, "local_tax")]["amount_yen"] == local_tax * 1000
        assert (
            by[(fiscal_year, "standard_fiscal_scale")]["amount_yen"]
            == standard_scale * 1000
        )
        assert by[(fiscal_year, "fund_balance")]["amount_yen"] == fund_total * 1000
        assert by[(fiscal_year, "debt_balance")]["amount_yen"] == debt_total * 1000
    for record in records:
        assert record["municipality_id"] == MID
        assert record["account_type"] == "ordinary"
        assert record["stage"] == "settlement"
        assert record["review_status"] == "reviewed"
        assert record["sources"] == _expected_sources(record["fiscal_year"])


def test_kumamoto_settlement_arithmetic() -> None:
    by = _by_year_metric(_settlement_records())
    for fiscal_year in (2022, 2023, 2024):
        revenue = by[(fiscal_year, "total_revenue")]["amount_yen"]
        expenditure = by[(fiscal_year, "total_expenditure")]["amount_yen"]
        formal = by[(fiscal_year, "formal_balance")]["amount_yen"]
        carryover = by[(fiscal_year, "carryover_resources")]["amount_yen"]
        real = by[(fiscal_year, "real_balance")]["amount_yen"]
        assert revenue - expenditure == formal
        assert formal - carryover == real

        purpose = by[(fiscal_year, "expenditure_by_purpose")]
        assert (
            sum(item["amount_yen"] or 0 for item in purpose["breakdown"])
            == expenditure
        )
        nature = by[(fiscal_year, "expenditure_by_nature")]
        top_level = [
            item for item in nature["breakdown"] if item["parent_key"] is None
        ]
        assert sum(item["amount_yen"] for item in top_level) == expenditure
        breakdown = {item["key"]: item["amount_yen"] for item in nature["breakdown"]}
        children = {
            item["key"]: item["amount_yen"]
            for item in nature["breakdown"]
            if item["parent_key"] == "mandatory_expenses"
        }
        assert sum(children.values()) == breakdown["mandatory_expenses"]
        capital_children = {
            item["key"]: item["amount_yen"]
            for item in nature["breakdown"]
            if item["parent_key"] == "capital_expenses"
        }
        # Construction and disaster recovery works sum to the capital
        # total; the "うち単独" sub-item hangs under construction.
        assert sum(capital_children.values()) == breakdown["capital_expenses"]

        fund = by[(fiscal_year, "fund_balance")]
        assert len(fund["breakdown"]) == 3
        assert (
            sum(item["amount_yen"] or 0 for item in fund["breakdown"])
            == fund["amount_yen"]
        )

        debt = by[(fiscal_year, "debt_balance")]
        assert sum(item["amount_yen"] for item in debt["breakdown"]) == debt["amount_yen"]


def test_kumamoto_settlement_breakdowns_handle_unprinted_categories() -> None:
    by = _by_year_metric(_settlement_records())
    for fiscal_year in (2022, 2023, 2024):
        purpose = {
            item["label"]: item["amount_yen"]
            for item in by[(fiscal_year, "expenditure_by_purpose")]["breakdown"]
        }
        # The prior-year advance appropriation has no printed amount
        # in either system in any year: kept as null, never zero-filled.
        # Miscellaneous expenditures are printed for Kumamoto City
        # (unlike Hiroshima City) and are registered with values.
        assert purpose["前年度繰上充用金"] is None
        assert purpose["諸支出金"] is not None
        nature_labels = {
            item["label"]
            for item in by[(fiscal_year, "expenditure_by_nature")]["breakdown"]
        }
        # The unemployment-measures category is "-" in both systems:
        # omitted from the breakdown entirely.
        assert "失業対策事業費" not in nature_labels
    # The FY2024 standalone-construction figure follows the fiscal
    # situation collection (22,085,294 thousand yen); the settlement
    # card prints a differently defined figure (24,079,896 thousand
    # yen, including prefectural-project contributions), and the
    # difference is recorded in the record note.
    nature_2024 = {
        item["key"]: item["amount_yen"]
        for item in by[(2024, "expenditure_by_nature")]["breakdown"]
    }
    assert nature_2024["independent_construction"] == 22_085_294_000
    assert "24,079,896千円" in by[(2024, "expenditure_by_nature")]["note"]


def test_kumamoto_settlement_ratios_are_published_values() -> None:
    by = _by_year_metric(_settlement_records())
    assert by[(2022, "current_balance_ratio")]["value"] == 93.0
    assert by[(2023, "current_balance_ratio")]["value"] == 93.0
    assert by[(2024, "current_balance_ratio")]["value"] == 95.4
    assert by[(2022, "real_debt_service_ratio")]["value"] == 5.4
    assert by[(2023, "real_debt_service_ratio")]["value"] == 5.5
    assert by[(2024, "real_debt_service_ratio")]["value"] == 5.9
    assert by[(2022, "future_burden_ratio")]["value"] == 102.2
    assert by[(2023, "future_burden_ratio")]["value"] == 92.9
    assert by[(2024, "future_burden_ratio")]["value"] == 93.1
    # Both systems print the fiscal strength index to two decimals
    # (0.70 / 0.69 / 0.68); it is registered as printed, not recomputed.
    assert by[(2022, "fiscal_strength_index")]["value"] == 0.7
    assert by[(2023, "fiscal_strength_index")]["value"] == 0.69
    assert by[(2024, "fiscal_strength_index")]["value"] == 0.68
    assert by[(2022, "real_balance_ratio")]["value"] == 3.7
    assert by[(2023, "real_balance_ratio")]["value"] == 3.4
    assert by[(2024, "real_balance_ratio")]["value"] == 3.2
    # Resident-register population as of 1 January following the
    # fiscal year, per the collections' summary tables (the cards
    # print the 31 March figure instead: 729,937 / 729,326 / 729,138
    # — a different reference date, recorded in the record notes).
    assert by[(2022, "population")]["value"] == 731476
    assert by[(2023, "population")]["value"] == 731722
    assert by[(2024, "population")]["value"] == 731331


def test_kumamoto_settlement_packets_cover_every_record() -> None:
    records = _settlement_records()
    packets = load_json(BASE / "settlement_evidence_packets.json")
    assert {packet["subject_id"] for packet in packets} == {
        record["id"] for record in records
    }
    by_id = {record["id"]: record for record in records}
    for packet in packets:
        assert packet["review_status"] == "reviewed"
        assert len(packet["claims"]) == 1
        claim = packet["claims"][0]
        assert claim["decision"] == "accepted"
        assert claim["source_ids"] == by_id[packet["subject_id"]]["sources"]


def test_kumamoto_catalog_shape() -> None:
    catalog = load_json("data/catalog/kumamoto_city_finance_sources.json")
    assert catalog["scope"] == "phase15-core-capital-review"
    assert len(catalog["records"]) == 11
    assert {record["municipality_key"] for record in catalog["records"]} == {
        "kumamoto-city"
    }
    for record in catalog["records"]:
        assert record["url"].startswith("https://")
        assert record["review_status"] == "reviewed"
    validator_text = (ROOT / "scripts/validate_static_export.py").read_text(
        encoding="utf-8"
    )
    assert "kumamoto_city_finance_sources.json" in validator_text


def test_kumamoto_fy2026_local_tax_added() -> None:
    records = {r["id"]: r for r in load_json(BASE / "fiscal_records.json")}
    packets = load_json(BASE / "evidence_packets.json")
    assert {p["subject_id"] for p in packets} == set(records)

    # The FY2026 initial-budget total was registered at Phase 13 and
    # matches Article 1 of the enacted budget bill exactly, so it is
    # unchanged at stage 1.
    total = records["jp-local-431001-fiscal-2026-total-revenue"]
    assert total["amount_yen"] == 437_840_000_000

    # The FY2026 local tax was missing and is added. It is verified
    # against Table 1 of Bill No. 3 itself (the FY2026 general
    # account budget book), which the council passed (可決) on
    # 2026-03-23, so the printed bill value is the enacted value.
    local_tax = records["jp-local-431001-fiscal-2026-local-tax"]
    assert local_tax["stage"] == "initial_budget"
    assert local_tax["metric"] == "local_tax"
    assert local_tax["amount_yen"] == 140_331_000_000
    assert local_tax["sources"] == [
        "kumamoto-city-budget-fy2026",
        "kumamoto-city-council-results-fy2026",
    ]
    assert "可決" in local_tax["note"]


def test_kumamoto_plan_review_unchanged_from_phase13() -> None:
    # The current plan (8th Comprehensive Plan, FY2024-FY2031) was
    # already registered at Phase 13 with its FY2026 action plan and
    # FY2024 administrative evaluation; stage 1 leaves it unchanged.
    plan = load_json(BASE / "plan_review.json")
    records = {record["id"]: record for record in plan["records"]}
    assert set(records) == {
        "kumamoto-current-plan",
        "kumamoto-fy2026-action-plan",
        "kumamoto-fy2024-evaluation",
    }
    assert records["kumamoto-current-plan"]["title"] == "熊本市第8次総合計画"
    assert "2024年度から2031年度" in records["kumamoto-current-plan"]["statement"]
    assert records["kumamoto-fy2026-action-plan"]["value"] == 4
    assert records["kumamoto-fy2024-evaluation"]["value"] == "published"


def test_kumamoto_mayor_term_and_votes() -> None:
    terms = load_json("data/entities/executives/executive_terms.json")
    term = next(t for t in terms if t["municipality_id"] == MID)
    assert term["id"] == "jp-local-431001-executive-2022-12-03"
    assert term["person_name"] == "大西 一史"
    # The start follows the Article 259 proviso chain anchored by
    # the officially stated expiry (the 2022 election was a
    # term-expiry election held before the previous term expired).
    assert term["term_start"] == "2022-12-03"
    # The expiry is stated directly in the Kumamoto Prefectural
    # Election Commission's official list of mayoral term expiries
    # (as of 2026-11-01).
    assert term["term_end"] == "2026-12-02"
    assert term["election_date"] == "2022-11-13"
    # No manifesto connection at stage 1 (the 2022 election bulletin
    # is handled at the promise stage).
    assert term["manifesto_source_ids"] == []
    # Only the current term is registered: the term won in the
    # 2026-11-15 election (2026-12-03 to 2030-12-02) had not begun
    # at registration and must not appear as a term yet.
    assert len([t for t in terms if t["municipality_id"] == MID]) == 1

    packets = load_json("data/entities/executives/evidence_packets.json")
    packet = next(p for p in packets if p["subject_id"] == term["id"])
    claims = {claim["field"]: claim for claim in packet["claims"]}
    # The vote count has no field on the term record; it is kept in
    # the evidence packet (143,943 votes in the 2022 election per
    # the MIC's official election record; 133,988 votes in the
    # 2026 re-election per the city election commission).
    assert "143,943票" in claims["election_date"]["statement"]
    assert "133,988票" in claims["election_2026_result"]["statement"]
    assert claims["term_end"]["source_ids"] == [
        "kumamoto-pref-mayor-term-expiry-list"
    ]
    assert packet["open_questions"]
    assert "2026-12-03" in packet["open_questions"][0]


def test_kumamoto_web_wiring() -> None:
    executives = (ROOT / "apps/web/lib/executives.ts").read_text(encoding="utf-8")
    assert '"jp-local-431001": "kumamoto-city"' in executives
    catalog = (ROOT / "apps/web/lib/catalog.ts").read_text(encoding="utf-8")
    assert "kumamoto_city_finance_sources.json" in catalog
    assert '"kumamoto-city"' in catalog
    quality = (ROOT / "apps/web/lib/dataQuality.ts").read_text(encoding="utf-8")
    assert "kumamoto-city/fiscal_records.json" in quality
    assert "kumamoto-city/settlement_records.json" in quality
    assert '"kumamoto-city": "熊本市"' in quality
