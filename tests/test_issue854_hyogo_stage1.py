"""Issue #854: Hyogo cluster stage 1 — Hyogo Prefecture base data.

Covers the entity identity, the FY2026 general-account initial budget, the
FY2022-FY2024 ordinary-account settlements (cross-checked between the MIC
settlement cards and the fiscal situation collections hosted on the MIC
site, with arithmetic checks), the Hyogo Vision 2050 / third-term Regional
Creation Strategy plan review and the governor term.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data/reviewed/hyogo-prefecture"
MID = "jp-local-280003"


def load_json(relative_path: str | Path):
    path = ROOT / relative_path if isinstance(relative_path, str) else relative_path
    return json.loads(path.read_text(encoding="utf-8"))


def test_hyogo_prefecture_identity() -> None:
    municipality = load_json(BASE / "municipality.json")

    # The official local-government code is 280003: the prefecture's
    # official pages print the corporate number 8000020280003 (a check
    # digit followed by 000020 and the code), and the MIC settlement
    # cards carry the Hyogo sheet under that code.
    assert municipality["id"] == MID
    assert municipality["official_code"] == "280003"
    assert municipality["official_code"] in "8000020280003"
    assert municipality["name_ja"] == "兵庫県"
    assert municipality["data_status"] == "reviewed"
    assert municipality["fiscal_years"] == [2022, 2023, 2024, 2026]


def _settlement_records() -> list[dict]:
    return load_json(BASE / "settlement_records.json")


def _by_year_metric(records: list[dict]) -> dict[tuple[int, str], dict]:
    return {(r["fiscal_year"], r["metric"]): r for r in records}


def test_hyogo_settlement_headlines() -> None:
    records = _settlement_records()
    assert len(records) == 51
    by = _by_year_metric(records)

    # Thousand-yen values as printed on the MIC cards; stored in yen.
    expected = {
        # fiscal_year: (revenue, expenditure, local_tax) in thousand yen
        2022: (2683182088, 2648172795, 805042506),
        2023: (2444905048, 2417645312, 818640340),
        2024: (2426324829, 2407333062, 857076784),
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
                f"hyogo-prefecture-mic-settlement-card-fy{fiscal_year}",
                f"hyogo-prefecture-fiscal-situation-collection-fy{fiscal_year}",
            ]


def test_hyogo_settlement_arithmetic() -> None:
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
        # The debt reduction fund is "-" in both sources for all three
        # years, so its breakdown amount is null and the fund balance is
        # the sum of the other two categories.
        debt_reduction = next(
            item for item in fund["breakdown"] if item["key"] == "debt_reduction_fund"
        )
        assert debt_reduction["amount_yen"] is None
        assert (
            sum(item["amount_yen"] or 0 for item in fund["breakdown"])
            == fund["amount_yen"]
        )

        debt = by[(fiscal_year, "debt_balance")]
        assert sum(item["amount_yen"] for item in debt["breakdown"]) == debt["amount_yen"]


def test_hyogo_settlement_breakdowns_omit_dash_categories() -> None:
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
        assert "特別地方消費税交付金" not in purpose_labels
        nature_labels = {
            item["label"]
            for item in by[(fiscal_year, "expenditure_by_nature")]["breakdown"]
        }
        assert "前年度繰上充用金" not in nature_labels
        assert "失業対策事業費" not in nature_labels
    # The automobile acquisition tax grant has real values in
    # FY2022-FY2023 but is printed as "-" in FY2024, so it appears only
    # in the first two years' breakdowns.
    for fiscal_year in (2022, 2023):
        labels = {
            item["label"]
            for item in by[(fiscal_year, "expenditure_by_purpose")]["breakdown"]
        }
        assert "自動車取得税交付金" in labels
    labels_2024 = {
        item["label"]
        for item in by[(2024, "expenditure_by_purpose")]["breakdown"]
    }
    assert "自動車取得税交付金" not in labels_2024


def test_hyogo_settlement_ratios_are_published_values() -> None:
    by = _by_year_metric(_settlement_records())
    # The labelled (main) current-balance ratio is registered, not the
    # parenthesised variant that excludes the special revenue-shortfall
    # bonds and temporary fiscal measures bonds.
    assert by[(2022, "current_balance_ratio")]["value"] == 98.7
    assert by[(2023, "current_balance_ratio")]["value"] == 97.3
    assert by[(2024, "current_balance_ratio")]["value"] == 99.4
    assert by[(2024, "real_debt_service_ratio")]["value"] == 17.1
    assert by[(2024, "future_burden_ratio")]["value"] == 311.3
    assert by[(2024, "fiscal_strength_index")]["value"] == 0.62169
    assert by[(2024, "population")]["value"] == 5393607


def test_hyogo_fy2022_ratio_disagreement_is_documented() -> None:
    by = _by_year_metric(_settlement_records())
    # For FY2022 the two primary sources disagree on two ratios: the
    # settlement card prints 15.2 / 326.4 while the fiscal situation
    # collection prints 15.5 / 330.8. The card values are registered as
    # authoritative and the disagreement is recorded, never guessed away.
    debt_service = by[(2022, "real_debt_service_ratio")]
    assert debt_service["value"] == 15.2
    assert "15.5" in debt_service["note"]
    future_burden = by[(2022, "future_burden_ratio")]
    assert future_burden["value"] == 326.4
    assert "330.8" in future_burden["note"]

    packets = load_json(BASE / "settlement_evidence_packets.json")
    by_subject = {packet["subject_id"]: packet for packet in packets}
    for record in (debt_service, future_burden):
        packet = by_subject[record["id"]]
        assert any("一致しない" in q for q in packet["open_questions"])


def test_hyogo_settlement_packets_cover_every_record() -> None:
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


def test_hyogo_budget_2026_records() -> None:
    records = load_json(BASE / "fiscal_records.json")
    assert len(records) == 3
    by_metric = {record["metric"]: record for record in records}

    # Enacted FY2026 general-account initial budget (Bill No. 1 of the
    # 374th regular session, passed as proposed on 2026-03-23), as
    # published in the Hyogo Prefecture official gazette.
    assert by_metric["total_revenue"]["amount_yen"] == 2318223000000
    assert by_metric["total_expenditure"]["amount_yen"] == 2318223000000
    assert by_metric["local_tax"]["amount_yen"] == 909400000000
    # The prefectural tax office's page states the tax revenue as
    # 9,104億円; the gazette's enacted figure (9,094億円) is
    # authoritative and the difference is recorded in the note.
    assert "9,104億円" in by_metric["local_tax"]["note"]
    for record in records:
        assert record["fiscal_year"] == 2026
        assert record["account_type"] == "general"
        assert record["stage"] == "initial_budget"
        assert record["review_status"] == "reviewed"

    packets = load_json(BASE / "evidence_packets.json")
    assert {packet["subject_id"] for packet in packets} == {
        record["id"] for record in records
    }


def test_hyogo_plan_review() -> None:
    review = load_json(BASE / "plan_review.json")
    assert review["id"] == "phase15-hyogo-plan-review"
    assert review["official_code"] == "280003"
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
    assert "ひょうごビジョン2050" in identity["statement"]
    assert "地域創生戦略" in identity["statement"]
    structure = next(
        record
        for record in review["records"]
        if record["evidence_role"] == "policy_structure"
    )
    assert "8つの方向性" in structure["statement"]


def test_hyogo_governor_term() -> None:
    terms = load_json("data/entities/executives/executive_terms.json")
    term = next(t for t in terms if t["municipality_id"] == MID)
    assert term["person_name"] == "斎藤 元彦"
    assert term["office"] == "governor"
    # The governor lost office on 2024-09-30 after a unanimous
    # no-confidence motion (he did not dissolve the assembly), and was
    # re-elected in the vacancy election of 2024-11-17, so the term
    # runs four years from the election day itself under the main text
    # of Article 259 of the Public Offices Election Act. The previous
    # term (2021) is not registered.
    assert term["term_start"] == "2024-11-17"
    assert term["term_end"] == "2028-11-16"
    assert term["election_date"] == "2024-11-17"
    assert [t for t in terms if t["municipality_id"] == MID] == [term]
    # Stage 1 registered no manifesto source (the bulletin is
    # preserved on the Kobe City site and its candidate panels are
    # image-only); stage 3 (Issue #862) transcribed the panel and
    # connected the bulletin as the term's manifesto source.
    assert term["manifesto_source_ids"] == [
        "hyogo-pref-governor-election-2024-bulletin"
    ]
    assert term["sources"] == [
        "hyogo-pref-governor",
        "kobe-city-governor-election-2024-result",
    ]


def test_hyogo_catalog_shape() -> None:
    catalog = load_json("data/catalog/hyogo_prefecture_finance_sources.json")
    assert catalog["scope"] == "cluster8-hyogo-deep-dive"
    assert len(catalog["records"]) == 12
    assert {record["municipality_key"] for record in catalog["records"]} == {
        "hyogo-prefecture"
    }
    for record in catalog["records"]:
        assert record["url"].startswith("https://")
        assert record["review_status"] == "reviewed"
