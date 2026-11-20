from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data/reviewed/osaka-prefecture"
TERM_ID = "jp-local-270008-executive-2023-04-09"


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def settlement() -> dict[tuple[int, str], dict[str, Any]]:
    records = load_json(BASE / "settlement_records.json")
    return {(r["fiscal_year"], r["metric"]): r for r in records}


def test_osaka_municipality_identity() -> None:
    municipality = load_json(BASE / "municipality.json")
    assert municipality["id"] == "jp-local-270008"
    # The official code 270008 also appears inside Osaka Prefecture's
    # corporate number 4000020270008 on the governor's profile page.
    assert municipality["official_code"] == "270008"
    assert municipality["fiscal_years"] == [2022, 2023, 2024, 2026]


def test_osaka_settlement_headline_values_and_arithmetic() -> None:
    records = settlement()
    assert len(records) == 51

    # Thousand-yen values transcribed from the MIC settlement cards and
    # cross-checked against the MIC fiscal situation collections (all
    # 17 metrics x 3 years matched) and, for FY2024 headlines, Osaka's
    # own IR material at billion-yen precision.
    expected = {
        2022: (3942613114, 3895343951, 1455218797),
        2023: (3358436064, 3325569052, 1478135691),
        2024: (3316968053, 3279987111, 1591643432),
    }
    for fy, (revenue, expenditure, tax) in expected.items():
        assert records[(fy, "total_revenue")]["amount_yen"] == revenue * 1000
        assert records[(fy, "total_expenditure")]["amount_yen"] == expenditure * 1000
        assert records[(fy, "local_tax")]["amount_yen"] == tax * 1000
        formal = records[(fy, "formal_balance")]["amount_yen"]
        carryover = records[(fy, "carryover_resources")]["amount_yen"]
        real = records[(fy, "real_balance")]["amount_yen"]
        assert formal == revenue * 1000 - expenditure * 1000
        assert real == formal - carryover
        purpose = records[(fy, "expenditure_by_purpose")]["breakdown"]
        assert sum(item["amount_yen"] for item in purpose) == expenditure * 1000
        funds = records[(fy, "fund_balance")]["breakdown"]
        assert (
            sum(item["amount_yen"] for item in funds)
            == records[(fy, "fund_balance")]["amount_yen"]
        )
        debt = records[(fy, "debt_balance")]["breakdown"]
        assert (
            sum(item["amount_yen"] for item in debt)
            == records[(fy, "debt_balance")]["amount_yen"]
        )


def test_osaka_fy2023_current_balance_ratio_uses_labelled_value() -> None:
    records = settlement()
    # The FY2023 card workbook shifts rows by one: the value printed on
    # the row labelled 経常収支比率 is 97.4, while 101.3 on the next row
    # is the variant excluding temporary fiscal measures bonds. The
    # fiscal situation collection's summary table confirms 97.4.
    assert records[(2023, "current_balance_ratio")]["value"] == 97.4
    assert records[(2022, "current_balance_ratio")]["value"] == 102.2
    assert records[(2024, "current_balance_ratio")]["value"] == 96.4


def test_osaka_fy2026_enacted_budget() -> None:
    records = {r["metric"]: r for r in load_json(BASE / "fiscal_records.json")}
    # Bill No.1 (submitted 2026-02-24) fixes the general account total
    # at 3,921,606,338 thousand yen and prefectural tax at
    # 1,700,082,000 thousand yen; the bill passed as proposed on
    # 2026-03-24 in the February 2026 regular session.
    assert records["total_revenue"]["amount_yen"] == 3921606338000
    assert records["total_expenditure"]["amount_yen"] == 3921606338000
    assert records["local_tax"]["amount_yen"] == 1700082000000
    for record in records.values():
        assert record["stage"] == "initial_budget"
        assert record["account_type"] == "general"


def test_osaka_plan_review_records_vision_not_period_plan() -> None:
    review = load_json(BASE / "plan_review.json")
    assert review["official_code"] == "270008"
    roles = {record["evidence_role"] for record in review["records"]}
    assert roles == {
        "current_plan_identity",
        "policy_structure",
        "implementation_layer",
        "progress_governance",
    }
    identity = next(
        r for r in review["records"] if r["evidence_role"] == "current_plan_identity"
    )
    assert "副首都ビジョン" in identity["statement"]
    assert "総合計画" in identity["statement"]


def test_osaka_governor_term_and_reelection_history() -> None:
    terms = load_json(ROOT / "data/entities/executives/executive_terms.json")
    matches = [term for term in terms if term["id"] == TERM_ID]
    assert len(matches) == 1
    term = matches[0]

    # The prefecture's official FAQ states the term day by day
    # (2023-04-09 to 2027-04-08) and the election commission's
    # term-expiry list (current as of 2026-11-11, after the
    # re-election) still gives 2027-04-08.
    assert term["person_name"] == "吉村 洋文"
    assert term["election_date"] == "2023-04-09"
    assert term["term_start"] == "2023-04-09"
    assert term["term_end"] == "2027-04-08"
    # The February 2026 re-election (resignation-triggered, won with
    # 3,024,106 votes) does not start a new term, so no second term
    # record exists for Osaka. The promise stage (Issue #772) later
    # connected the 2026 re-election bulletin as the manifesto source
    # of this same term.
    osaka_terms = [t for t in terms if t["municipality_id"] == "jp-local-270008"]
    assert len(osaka_terms) == 1
    assert term["manifesto_source_ids"] == [
        "osaka-pref-governor-election-2026-bulletin"
    ]

    packets = load_json(ROOT / "data/entities/executives/evidence_packets.json")
    packet = next(p for p in packets if p["subject_id"] == TERM_ID)
    history = [c for c in packet["claims"] if c["field"] == "election_history"]
    assert len(history) == 1
    assert "3,024,106" in history[0]["statement"]
    assert "第二期" in history[0]["statement"]


def test_osaka_finance_catalog_shape() -> None:
    catalog = load_json(ROOT / "data/catalog/osaka_prefecture_finance_sources.json")
    assert catalog["scope"] == "cluster4-osaka-deep-dive"
    assert len(catalog["records"]) == 14
    assert {r["municipality_key"] for r in catalog["records"]} == {"osaka-prefecture"}
