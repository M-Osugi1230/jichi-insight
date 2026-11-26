"""Issue #1014 (Yamagata City part): Yamagata cluster stage 1.

The FY2022-FY2024 ordinary-account settlement detail of Yamagata
City was already registered under the Issue #691 programme (51
records cross-checked between the Ministry of Internal Affairs and
Communications' settlement cards and the fiscal situation
collections published for the city), so stage 1 verifies that
registration in place -- arithmetic, two-system sources and packet
coverage -- and re-verified the FY2024 headline values against the
collection workbook itself. Stage 1 adds what was missing: the
FY2026 initial budget's local tax (the general-account total was
already registered at Phase 15 and matches Bill No. 8 exactly) and
the registration of Mayor Sato Takahiro's current term
(2023-09-28 to 2027-09-27), with the source search for the 2023
election bulletin. The bulletin itself no longer sits at the
city's official URL (404, and the election page no longer links
to it); the search registers the surviving go2senkyo CDN copy,
whose content was verified against the official election page
and result report (no archived capture of the official URL
survives, so unlike Okayama City no digest match was possible;
that limitation is recorded in the search record itself).
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data/reviewed/yamagata-city"
MID = "jp-local-062014"


def load_json(relative_path: str | Path):
    path = ROOT / relative_path if isinstance(relative_path, str) else relative_path
    return json.loads(path.read_text(encoding="utf-8"))


def test_yamagata_city_identity() -> None:
    municipality = load_json(BASE / "municipality.json")

    assert municipality["id"] == MID
    assert municipality["official_code"] == "062014"
    assert municipality["name_ja"] == "山形市"
    assert municipality["municipality_type"] == "core_city"
    assert municipality["data_status"] == "reviewed"


def _settlement_records() -> list[dict]:
    return load_json(BASE / "settlement_records.json")


def _by_year_metric(records: list[dict]) -> dict[tuple[int, str], dict]:
    return {(r["fiscal_year"], r["metric"]): r for r in records}


def _expected_sources(fiscal_year: int) -> list[str]:
    return [
        f"yamagata-city-mic-settlement-card-fy{fiscal_year}",
        f"yamagata-city-fiscal-situation-collection-fy{fiscal_year}",
    ]


def test_yamagata_settlement_headlines() -> None:
    records = _settlement_records()
    assert len(records) == 51
    by = _by_year_metric(records)

    # Thousand-yen values as printed in the collections; stored in yen.
    expected = {
        # fiscal_year: (revenue, expenditure, local_tax, standard
        # fiscal scale, fund balance total, debt balance) in
        # thousand yen
        2022: (120040990, 116397300, 36504766, 53644763, 9717077, 109903007),
        2023: (113804179, 111052627, 37068298, 54488682, 8996037, 108319422),
        2024: (114220746, 111197489, 36313263, 56114324, 8058404, 105276782),
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


def test_yamagata_settlement_arithmetic() -> None:
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
        assert sum(capital_children.values()) == breakdown["capital_expenses"]

        fund = by[(fiscal_year, "fund_balance")]
        assert len(fund["breakdown"]) == 3
        assert (
            sum(item["amount_yen"] or 0 for item in fund["breakdown"])
            == fund["amount_yen"]
        )

        debt = by[(fiscal_year, "debt_balance")]
        assert sum(item["amount_yen"] for item in debt["breakdown"]) == debt["amount_yen"]


def test_yamagata_settlement_breakdowns_handle_unprinted_categories() -> None:
    by = _by_year_metric(_settlement_records())
    for fiscal_year in (2022, 2023, 2024):
        purpose = {
            item["label"]: item["amount_yen"]
            for item in by[(fiscal_year, "expenditure_by_purpose")]["breakdown"]
        }
        # Neither miscellaneous expenditures nor the prior-year
        # advance appropriation carries a printed amount for
        # Yamagata City in any year: kept as null, never zero-filled.
        assert purpose["諸支出金"] is None
        assert purpose["前年度繰上充用金"] is None
        nature_labels = {
            item["label"]
            for item in by[(fiscal_year, "expenditure_by_nature")]["breakdown"]
        }
        # The unemployment-measures category is not printed either:
        # omitted from the breakdown entirely.
        assert "失業対策事業費" not in nature_labels


def test_yamagata_settlement_ratios_are_published_values() -> None:
    by = _by_year_metric(_settlement_records())
    assert by[(2022, "current_balance_ratio")]["value"] == 90.8
    assert by[(2023, "current_balance_ratio")]["value"] == 90.3
    assert by[(2024, "current_balance_ratio")]["value"] == 92.1
    assert by[(2022, "real_debt_service_ratio")]["value"] == 7.6
    assert by[(2023, "real_debt_service_ratio")]["value"] == 7.8
    assert by[(2024, "real_debt_service_ratio")]["value"] == 7.8
    assert by[(2022, "future_burden_ratio")]["value"] == 97.0
    assert by[(2023, "future_burden_ratio")]["value"] == 92.5
    assert by[(2024, "future_burden_ratio")]["value"] == 87.3
    assert by[(2022, "fiscal_strength_index")]["value"] == 0.76
    assert by[(2023, "fiscal_strength_index")]["value"] == 0.74
    assert by[(2024, "fiscal_strength_index")]["value"] == 0.74
    assert by[(2022, "real_balance_ratio")]["value"] == 4.7
    assert by[(2023, "real_balance_ratio")]["value"] == 3.8
    assert by[(2024, "real_balance_ratio")]["value"] == 3.8
    # Resident-register population as of 1 January following the
    # fiscal year, per the collections' summary tables.
    assert by[(2022, "population")]["value"] == 240441
    assert by[(2023, "population")]["value"] == 238293
    assert by[(2024, "population")]["value"] == 236164


def test_yamagata_settlement_packets_cover_every_record() -> None:
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


def test_yamagata_catalog_shape() -> None:
    catalog = load_json("data/catalog/yamagata_city_finance_sources.json")
    assert catalog["scope"] == "phase15-core-capital-review"
    assert len(catalog["records"]) == 10
    assert {record["municipality_key"] for record in catalog["records"]} == {
        "yamagata-city"
    }
    for record in catalog["records"]:
        assert record["url"].startswith("https://")
        assert record["review_status"] == "reviewed"
    validator_text = (ROOT / "scripts/validate_static_export.py").read_text(
        encoding="utf-8"
    )
    assert "yamagata_city_finance_sources.json" in validator_text


def test_yamagata_fy2026_local_tax_added() -> None:
    records = {r["id"]: r for r in load_json(BASE / "fiscal_records.json")}
    packets = load_json(BASE / "evidence_packets.json")
    assert {p["subject_id"] for p in packets} == set(records)

    # The FY2026 initial-budget total was registered at Phase 15 as
    # the expenditure-side record and matches Article 1 of Bill
    # No. 8 exactly (revenue and expenditure are the same printed
    # total), so it is unchanged at stage 1.
    total = records["jp-local-062014-fiscal-2026-total-expenditure"]
    assert total["amount_yen"] == 117_146_000_000

    # The FY2026 local tax was missing and is added. It is verified
    # against Table 1 (revenue) of Bill No. 8 itself, which the
    # council passed as proposed (原案のとおり可決) on 2026-03-24,
    # so the printed bill value is the enacted value; the six
    # sub-items of the city tax sum to the printed total.
    local_tax = records["jp-local-062014-fiscal-2026-local-tax"]
    assert local_tax["stage"] == "initial_budget"
    assert local_tax["metric"] == "local_tax"
    assert local_tax["amount_yen"] == 38_753_158_000
    assert local_tax["sources"] == [
        "yamagata-budget-2026",
        "yamagata-budget-2026-enactment",
    ]
    assert "原案のとおり可決" in local_tax["note"]


def test_yamagata_plan_review_unchanged_from_phase15() -> None:
    # The current plan (Yamagata City Development Plan 2030,
    # FY2025-FY2029) was already registered at Phase 15; the unit
    # of registration for stage 2 is decided there, so stage 1
    # leaves the plan review unchanged.
    plan = load_json(BASE / "plan_review.json")
    records = {record["id"]: record for record in plan["records"]}
    assert set(records) == {
        "yamagata-current-plan-period",
        "yamagata-current-policy-structure",
        "yamagata-previous-plan-and-transition",
        "yamagata-progress-indicator-structure",
        "yamagata-fy2024-settlement-linkage",
    }
    assert records["yamagata-current-plan-period"]["value"] == "2025年度～2029年度"
    assert records["yamagata-current-policy-structure"]["value"] == 19


def test_yamagata_mayor_term_and_votes() -> None:
    terms = load_json("data/entities/executives/executive_terms.json")
    term = next(t for t in terms if t["municipality_id"] == MID)
    assert term["id"] == "jp-local-062014-executive-2023-09-28"
    assert term["person_name"] == "佐藤 孝弘"
    # The start follows the Article 259 proviso chain anchored by
    # the officially stated expiry and by the mayoral profile's
    # stated first inauguration date (2015-09-28, same 4-year
    # cycle).
    assert term["term_start"] == "2023-09-28"
    # The expiry is stated directly in the Yamagata Prefecture
    # official list of municipalities (as of 2026-06-01:
    # 任期満了日 R9.9.27).
    assert term["term_end"] == "2027-09-27"
    assert term["election_date"] == "2023-09-10"
    # The manifesto connection was added at stage 3 (Issue #1037):
    # the term now links the 2023 election bulletin copy verified at
    # stage 1.
    assert term["manifesto_source_ids"] == [
        "yamagata-city-mayor-election-2023-bulletin"
    ]
    assert len([t for t in terms if t["municipality_id"] == MID]) == 1

    packets = load_json("data/entities/executives/evidence_packets.json")
    packet = next(p for p in packets if p["subject_id"] == term["id"])
    claims = {claim["field"]: claim for claim in packet["claims"]}
    # The vote count has no field on the term record; it is kept in
    # the evidence packet (66,670 votes in the 2023 election per
    # the city election commission's official result report; the
    # two candidates' votes sum to the valid-vote total 78,106).
    assert "66,670票" in claims["election_date"]["statement"]
    assert claims["term_end"]["source_ids"] == ["yamagata-pref-municipality-list"]
    assert packet["open_questions"]


def test_yamagata_bulletin_search_registered() -> None:
    searches = load_json("data/entities/executives/manifesto_source_searches.json")
    search = next(s for s in searches if s["id"] == "manifesto-source-search-yamagata-city-2023")
    assert search["executive_term_id"] == "jp-local-062014-executive-2023-09-28"
    assert search["result_status"] == "source_registered"
    assert search["manifesto_source_ids_found"] == [
        "yamagata-city-mayor-election-2023-bulletin"
    ]
    assert search["nonexistence_claim"] is False
    # The registration is honest about its basis: the official URL
    # is 404 and no archived capture survives, so the copy's
    # identity rests on content verification, not a digest match.
    assert "404" in search["review_note"]
    assert "ダイジェスト照合はできなかった" in search["review_note"]

    catalog = load_json("data/catalog/executive_sources.json")
    assert catalog["version"] == "0.68.0"
    bulletin = next(
        r for r in catalog["records"] if r["id"] == "yamagata-city-mayor-election-2023-bulletin"
    )
    assert bulletin["url"].startswith("https://prod-cdn.go2senkyo.com/")
    assert "b7633c048c0f9add22f7c09e7598beff697d2755e5be6c58c9bc2c95fc868e88" in bulletin["notes"]


def test_yamagata_web_wiring() -> None:
    executives = (ROOT / "apps/web/lib/executives.ts").read_text(encoding="utf-8")
    assert '"jp-local-062014": "yamagata-city"' in executives
    catalog = (ROOT / "apps/web/lib/catalog.ts").read_text(encoding="utf-8")
    assert "yamagata_city_finance_sources.json" in catalog
    assert '"yamagata-city"' in catalog
    quality = (ROOT / "apps/web/lib/dataQuality.ts").read_text(encoding="utf-8")
    assert "yamagata-city/fiscal_records.json" in quality
    assert "yamagata-city/settlement_records.json" in quality
    assert '"yamagata-city": "山形市"' in quality
