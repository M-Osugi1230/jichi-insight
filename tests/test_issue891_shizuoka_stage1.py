"""Issue #891: Shizuoka cluster stage 1 — Shizuoka Prefecture base data.

Covers the entity identity, the FY2026 general-account initial budget, the
FY2022-FY2024 ordinary-account settlements (cross-checked between the MIC
settlement cards and the fiscal situation collections hosted on the MIC
site, with arithmetic checks), the Shizuoka Prefecture Comprehensive Plan
(Well-being Plan) review and the governor term.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data/reviewed/shizuoka-prefecture"
MID = "jp-local-220001"


def load_json(relative_path: str | Path):
    path = ROOT / relative_path if isinstance(relative_path, str) else relative_path
    return json.loads(path.read_text(encoding="utf-8"))


def test_shizuoka_prefecture_identity() -> None:
    municipality = load_json(BASE / "municipality.json")

    # The official local-government code is 220001: the prefecture's
    # corporate number 7000020220001 (stated on the official
    # prefecture site) ends in the code, and the MIC settlement cards
    # carry the Shizuoka sheet under code 22.
    assert municipality["id"] == MID
    assert municipality["official_code"] == "220001"
    assert municipality["official_code"] in "7000020220001"
    assert municipality["name_ja"] == "静岡県"
    assert municipality["data_status"] == "reviewed"
    assert municipality["fiscal_years"] == [2022, 2023, 2024, 2026]


def _settlement_records() -> list[dict]:
    return load_json(BASE / "settlement_records.json")


def _by_year_metric(records: list[dict]) -> dict[tuple[int, str], dict]:
    return {(r["fiscal_year"], r["metric"]): r for r in records}


def test_shizuoka_settlement_headlines() -> None:
    records = _settlement_records()
    assert len(records) == 51
    by = _by_year_metric(records)

    # Thousand-yen values as printed on the MIC cards; stored in yen.
    expected = {
        # fiscal_year: (revenue, expenditure, local_tax) in thousand yen
        2022: (1384631998, 1359231789, 582858775),
        2023: (1269197338, 1250356192, 585904682),
        2024: (1311457126, 1295659466, 623147771),
    }
    for fiscal_year, (revenue, expenditure, local_tax) in expected.items():
        assert by[(fiscal_year, "total_revenue")]["amount_yen"] == revenue * 1000
        assert by[(fiscal_year, "total_expenditure")]["amount_yen"] == expenditure * 1000
        assert by[(fiscal_year, "local_tax")]["amount_yen"] == local_tax * 1000
        for record in (
            by[(fiscal_year, "total_revenue")],
            by[(fiscal_year, "total_expenditure")],
            by[(fiscal_year, "local_tax")],
        ):
            assert record["account_type"] == "ordinary"
            assert record["stage"] == "settlement"
            assert record["review_status"] == "reviewed"
            assert record["sources"] == [
                f"shizuoka-prefecture-mic-settlement-card-fy{fiscal_year}",
                f"shizuoka-prefecture-fiscal-situation-collection-fy{fiscal_year}",
            ]


def test_shizuoka_settlement_arithmetic() -> None:
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
        assert sum(item["amount_yen"] for item in purpose["breakdown"]) == expenditure
        nature = by[(fiscal_year, "expenditure_by_nature")]
        top_level = [
            item for item in nature["breakdown"] if item["parent_key"] is None
        ]
        assert sum(item["amount_yen"] for item in top_level) == expenditure

        fund = by[(fiscal_year, "fund_balance")]
        assert len(fund["breakdown"]) == 3
        # All three fund categories carry published balances in all
        # three years, so they sum to the fund balance directly.
        assert all(item["amount_yen"] is not None for item in fund["breakdown"])
        assert (
            sum(item["amount_yen"] for item in fund["breakdown"])
            == fund["amount_yen"]
        )

        debt = by[(fiscal_year, "debt_balance")]
        assert sum(item["amount_yen"] for item in debt["breakdown"]) == debt["amount_yen"]


def test_shizuoka_settlement_breakdowns_omit_dash_categories() -> None:
    by = _by_year_metric(_settlement_records())
    for fiscal_year in (2022, 2023, 2024):
        purpose_labels = {
            item["label"]
            for item in by[(fiscal_year, "expenditure_by_purpose")]["breakdown"]
        }
        # Categories printed as "-" on the card (no such expenditure for
        # a prefecture) are omitted, never zero-filled.
        assert "消防費" not in purpose_labels
        assert "諸支出金" not in purpose_labels
        assert "前年度繰上充用金" not in purpose_labels
        assert "特別区財政調整交付金" not in purpose_labels
        nature_labels = {
            item["label"]
            for item in by[(fiscal_year, "expenditure_by_nature")]["breakdown"]
        }
        assert "前年度繰上充用金" not in nature_labels
        assert "失業対策事業費" not in nature_labels
    # The automobile acquisition tax grant is printed as 4 thousand yen
    # in FY2024 (a real published value, not a dash), so it stays in the
    # breakdown with that amount.
    labels_2024 = {
        item["label"]: item["amount_yen"]
        for item in by[(2024, "expenditure_by_purpose")]["breakdown"]
    }
    assert labels_2024["自動車取得税交付金"] == 4000


def test_shizuoka_settlement_ratios_are_published_values() -> None:
    by = _by_year_metric(_settlement_records())
    # The labelled (main) current-balance ratio is registered, not the
    # parenthesised variant that excludes the special revenue-shortfall
    # bonds and temporary fiscal measures bonds.
    assert by[(2022, "current_balance_ratio")]["value"] == 95.4
    assert by[(2023, "current_balance_ratio")]["value"] == 95.6
    assert by[(2024, "current_balance_ratio")]["value"] == 94.4
    assert by[(2024, "real_debt_service_ratio")]["value"] == 14.3
    assert by[(2024, "future_burden_ratio")]["value"] == 234.1
    assert by[(2024, "fiscal_strength_index")]["value"] == 0.68341
    assert by[(2024, "population")]["value"] == 3575704


def test_shizuoka_settlement_packets_cover_every_record() -> None:
    records = _settlement_records()
    packets = load_json(BASE / "settlement_evidence_packets.json")
    assert {packet["subject_id"] for packet in packets} == {
        record["id"] for record in records
    }
    for packet in packets:
        assert packet["review_status"] == "reviewed"
        assert len(packet["claims"]) == 1
        claim = packet["claims"][0]
        assert claim["decision"] == "accepted"
        assert len(claim["source_ids"]) == 2


def test_shizuoka_budget_2026_records() -> None:
    records = load_json(BASE / "fiscal_records.json")
    assert len(records) == 3
    by_metric = {record["metric"]: record for record in records}

    # Enacted FY2026 general-account initial budget (Bill No. 1 of the
    # February 2026 regular session, passed unanimously on 2026-03-16
    # as 「可決・全員一致」). The prefecture's published summaries give
    # only million-yen figures, so the thousand-yen values are taken
    # from Bill No. 96 (the FY2026 supplementary budget), whose Table 1
    # states the pre-supplement amounts — the enacted initial budget
    # itself — in thousand yen.
    assert by_metric["total_revenue"]["amount_yen"] == 1414100000000
    assert by_metric["total_expenditure"]["amount_yen"] == 1414100000000
    assert by_metric["local_tax"]["amount_yen"] == 542000000000
    for record in records:
        assert record["fiscal_year"] == 2026
        assert record["account_type"] == "general"
        assert record["stage"] == "initial_budget"
        assert record["review_status"] == "reviewed"

    packets = load_json(BASE / "evidence_packets.json")
    assert {packet["subject_id"] for packet in packets} == {
        record["id"] for record in records
    }


def test_shizuoka_plan_review() -> None:
    review = load_json(BASE / "plan_review.json")
    assert review["id"] == "phase15-shizuoka-plan-review"
    assert review["official_code"] == "220001"
    assert review["review_status"] == "reviewed"
    roles = {record["evidence_role"] for record in review["records"]}
    assert roles == {
        "current_plan_identity",
        "policy_structure",
        "implementation_layer",
        "progress_governance",
    }
    identity = next(
        record
        for record in review["records"]
        if record["evidence_role"] == "current_plan_identity"
    )
    assert "しずおか ウェルビーイングプラン" in identity["statement"]
    structure = next(
        record
        for record in review["records"]
        if record["evidence_role"] == "policy_structure"
    )
    assert "政策の柱" in structure["statement"]
    assert "197の取組" in structure["statement"]


def test_shizuoka_governor_term() -> None:
    terms = load_json("data/entities/executives/executive_terms.json")
    term = next(t for t in terms if t["municipality_id"] == MID)
    assert term["person_name"] == "鈴木 康友"
    assert term["office"] == "governor"
    # The 2024 election was a vacancy election held after Governor
    # Kawakatsu resigned, so under the main text of Article 259 of the
    # Public Offices Election Act the term runs from the election day
    # itself for four years. The expiry is also stated verbatim on the
    # prefectural election commission's official term page
    # (令和10年5月25日), and the two agree. The governor won with
    # 728,500 votes (recorded in the evidence packet, directly checked
    # against the Minamiizu Town election commission's official
    # ballot-count result, which states the prefecture-wide total).
    # Earlier terms are not registered.
    assert term["term_start"] == "2024-05-26"
    assert term["term_end"] == "2028-05-25"
    assert term["election_date"] == "2024-05-26"
    assert [t for t in terms if t["municipality_id"] == MID] == [term]
    # Stage 1 registered no manifesto source: the bulletin's candidate
    # panels are image-based, so the promise registration decision
    # belonged to the cluster's promise stage. Stage 3 (Issue #900)
    # then transcribed the panel and registered the bulletin.
    assert term["manifesto_source_ids"] == [
        "shizuoka-pref-governor-election-2024-bulletin"
    ]
    assert term["sources"] == [
        "shizuoka-pref-governor",
        "shizuoka-pref-term-list",
        "minamiizu-town-governor-election-2024-result",
    ]

    packets = load_json("data/entities/executives/evidence_packets.json")
    packet = next(p for p in packets if p["subject_id"] == term["id"])
    election_claims = [
        claim for claim in packet["claims"] if claim["field"] == "election_date"
    ]
    assert len(election_claims) == 1
    assert "728,500票" in election_claims[0]["statement"]


def test_shizuoka_catalog_shape() -> None:
    catalog = load_json("data/catalog/shizuoka_prefecture_finance_sources.json")
    assert catalog["scope"] == "cluster10-shizuoka-deep-dive"
    assert len(catalog["records"]) == 12
    assert {record["municipality_key"] for record in catalog["records"]} == {
        "shizuoka-prefecture"
    }
    for record in catalog["records"]:
        assert record["url"].startswith("https://")
        assert record["review_status"] == "reviewed"
