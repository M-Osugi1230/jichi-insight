import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "reviewed" / "yamagata-prefecture"
FIGURES_ID = "yamagata-prefecture-budget-figures-fy2026"
ASSEMBLY_ID = "yamagata-prefecture-assembly-2026-feb-session-results"
PLAN_URLS = {
    "https://www.pref.yamagata.jp/documents/16782/dai4zikeikaku_cyoukikousou_gaiyou.pdf",
    "https://www.pref.yamagata.jp/documents/45885/dai4jikokisasshi.pdf",
    "https://www.pref.yamagata.jp/documents/53500/04_2-1_shinchokujoukyoutohyouka.pdf",
}


def load_json(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def load_base(name: str):
    return json.loads((BASE / name).read_text(encoding="utf-8"))


def test_municipality_identity_is_reviewed() -> None:
    municipality = load_base("municipality.json")
    assert municipality["id"] == "jp-local-060003"
    assert municipality["official_code"] == "060003"
    # The prefecture's corporate number ends in the municipality code.
    assert "060003" in "5000020060003"
    assert municipality["name_ja"] == "山形県"
    assert municipality["official_url"] == "https://www.pref.yamagata.jp/"
    assert municipality["data_status"] == "reviewed"
    assert municipality["fiscal_years"] == [2022, 2023, 2024, 2026]
    assert municipality["sources"][0] == "yamagata-pref-home"


def test_plan_review_registers_the_comprehensive_plan_without_projects() -> None:
    review = load_base("plan_review.json")
    assert review["review_status"] == "reviewed"
    assert len(review["records"]) == 4
    assert {record["evidence_role"] for record in review["records"]} == {
        "current_plan_identity",
        "policy_structure",
        "implementation_layer",
        "progress_governance",
    }
    identity = next(
        r for r in review["records"]
        if r["evidence_role"] == "current_plan_identity"
    )
    assert "第4次山形県総合発展計画" in identity["statement"]
    assert "令和2年3月" in identity["statement"]
    structure = next(
        r for r in review["records"] if r["evidence_role"] == "policy_structure"
    )
    assert "政策の柱" in structure["statement"]
    assert "28" in structure["statement"]
    governance = next(
        r for r in review["records"]
        if r["evidence_role"] == "progress_governance"
    )
    # The official evaluation unit is the policy; fixing the registration
    # unit is stage 2 work.
    assert "毎年度" in governance["statement"]
    assert "政策" in governance["statement"]
    assert "段階2" in governance["statement"]
    for record in review["records"]:
        assert record["source_url"] in PLAN_URLS
        assert record["decision"] == "accepted"


def test_fiscal_records_register_the_enacted_initial_budget() -> None:
    records = load_base("fiscal_records.json")
    assert len(records) == 3
    assert {record["amount_yen"] for record in records} == {
        700_284_000_000,
        115_300_000_000,
    }
    for record in records:
        assert record["fiscal_year"] == 2026
        assert record["stage"] == "initial_budget"
        assert record["account_type"] == "general"
        assert set(record["sources"]) == {FIGURES_ID, ASSEMBLY_ID}
        # The thousand-yen figures were fixed through Table 1 ("amount
        # before correction") of Supplementary Budget No. 1; the decision
        # wording is 「可決」, not 「原案可決」.
        assert "補正予算（第1号）" in record["note"]
        assert "第1表" in record["note"]
        assert "2026年3月16日" in record["note"]
        assert "「可決」" in record["note"]


def test_settlement_records_cover_three_years_with_fifty_one_records() -> None:
    records = load_base("settlement_records.json")
    assert len(records) == 51
    assert {record["fiscal_year"] for record in records} == {2022, 2023, 2024}
    for record in records:
        assert record["review_status"] == "reviewed"
        assert record["confidence"] == "high"
        year = record["fiscal_year"]
        assert record["sources"] == [
            f"yamagata-prefecture-mic-settlement-card-fy{year}",
            f"yamagata-prefecture-fiscal-situation-collection-fy{year}",
        ]


def test_settlement_values_match_the_cross_checked_sources() -> None:
    records = load_base("settlement_records.json")
    by_key = {(r["fiscal_year"], r["metric"]): r for r in records}
    fy2024 = {metric: r for (year, metric), r in by_key.items() if year == 2024}
    assert fy2024["total_revenue"]["amount_yen"] == 674_209_779_000
    assert fy2024["total_expenditure"]["amount_yen"] == 661_550_290_000
    assert fy2024["local_tax"]["amount_yen"] == 147_231_538_000
    assert fy2024["real_balance_ratio"]["value"] == 1.6
    # The labelled current balance ratio is registered, not the
    # parenthesised variant (96.0).
    assert fy2024["current_balance_ratio"]["value"] == 95.8
    assert fy2024["real_debt_service_ratio"]["value"] == 13.4
    assert fy2024["future_burden_ratio"]["value"] == 212.2
    assert fy2024["fiscal_strength_index"]["value"] == 0.37417
    assert fy2024["population"]["value"] == 1_012_355
    fund = fy2024["fund_balance"]
    assert fund["amount_yen"] == 58_753_508_000
    assert sum(item["amount_yen"] for item in fund["breakdown"]) == 58_753_508_000
    fund_by_key = {item["key"]: item["amount_yen"] for item in fund["breakdown"]}
    assert fund_by_key["debt_reduction_fund"] == 18_301_890_000
    debt = fy2024["debt_balance"]
    assert debt["amount_yen"] == 1_128_936_417_000
    assert sum(item["amount_yen"] for item in debt["breakdown"]) == 1_128_936_417_000
    debt_by_key = {item["key"]: item["amount_yen"] for item in debt["breakdown"]}
    # The balance excluding temporary fiscal measures bonds is the printed
    # collection value; the bonds figure itself is derived by subtraction.
    assert debt_by_key["bonds_excluding_temporary_fiscal"] == 790_299_798_000
    assert debt_by_key["temporary_fiscal_measures_bonds"] == 338_636_619_000
    purpose = fy2024["expenditure_by_purpose"]
    assert len(purpose["breakdown"]) == 19
    assert (
        sum(item["amount_yen"] for item in purpose["breakdown"])
        == purpose["amount_yen"]
    )
    nature = fy2024["expenditure_by_nature"]
    assert len(nature["breakdown"]) == 18
    top_level = [
        item for item in nature["breakdown"] if item["parent_key"] is None
    ]
    assert sum(item["amount_yen"] for item in top_level) == nature["amount_yen"]


def test_settlement_evidence_packets_match_the_records() -> None:
    records = load_base("settlement_records.json")
    packets = load_base("settlement_evidence_packets.json")
    assert len(packets) == 51
    assert {packet["subject_id"] for packet in packets} == {
        record["id"] for record in records
    }
    for packet in packets:
        year = packet["subject_id"].split("-")[4]
        assert packet["claims"][0]["source_ids"] == [
            f"yamagata-prefecture-mic-settlement-card-fy{year}",
            f"yamagata-prefecture-fiscal-situation-collection-fy{year}",
        ]


def test_fiscal_evidence_packets_fix_the_budget_route() -> None:
    records = load_base("fiscal_records.json")
    packets = load_base("evidence_packets.json")
    assert len(packets) == 3
    assert {packet["subject_id"] for packet in packets} == {
        record["id"] for record in records
    }
    total = next(
        packet for packet in packets
        if packet["subject_id"].endswith("total-revenue")
    )
    assert total["claims"][0]["source_ids"] == [FIGURES_ID, ASSEMBLY_ID]
    # The route through Table 1 of Supplementary Budget No. 1 is recorded
    # as an open question for re-verification.
    assert any("第1表" in question for question in total["open_questions"])


def test_governor_term_is_registered_with_an_empty_manifesto_list() -> None:
    terms = load_json("data/entities/executives/executive_terms.json")
    term = next(t for t in terms if t["municipality_id"] == "jp-local-060003")
    assert term["id"] == "jp-local-060003-executive-2025-02-14"
    assert term["person_name"] == "吉村 美栄子"
    assert term["term_start"] == "2025-02-14"
    assert term["term_end"] == "2029-02-13"
    assert term["election_date"] == "2025-01-26"
    # The bulletin is located (reproduced in the official election record)
    # but transcription and linking are stage 3 work, so no manifesto
    # source is registered at this stage.
    assert term["manifesto_source_ids"] == []
    assert set(term["sources"]) == {
        "yamagata-pref-governor",
        "yamagata-pref-governor-term-list",
        "yamagata-pref-governor-election-2025-results",
    }


def test_governor_evidence_packet_records_votes_and_open_questions() -> None:
    packets = load_json("data/entities/executives/evidence_packets.json")
    packet = next(
        p for p in packets if p["id"] == "evidence-yamagata-pref-current-governor-term"
    )
    assert {claim["field"] for claim in packet["claims"]} == {
        "person_name",
        "election_date",
        "term_start",
        "term_end",
    }
    election = next(
        claim for claim in packet["claims"] if claim["field"] == "election_date"
    )
    assert "318,364" in election["statement"]
    assert len(packet["open_questions"]) == 2
    assert "開始日" in packet["open_questions"][0]
    assert "選挙公報" in packet["open_questions"][1]


def test_source_catalog_registers_only_verified_prefecture_sources() -> None:
    catalog = load_json("data/catalog/yamagata_prefecture_finance_sources.json")
    assert catalog["version"] == "0.1.0"
    assert catalog["scope"] == "cluster17-yamagata-deep-dive"
    assert len(catalog["records"]) == 10
    assert {
        record["municipality_key"] for record in catalog["records"]
    } == {"yamagata-prefecture"}
    card = next(
        r for r in catalog["records"]
        if r["id"] == "yamagata-prefecture-mic-settlement-card-fy2024"
    )
    assert card["url"] == "https://www.soumu.go.jp/main_content/001064044.xlsx"
    figures = next(r for r in catalog["records"] if r["id"] == FIGURES_ID)
    assert figures["url"] == (
        "https://www.pref.yamagata.jp/documents/53068/0501gian2.pdf"
    )


def test_web_wiring_includes_yamagata_prefecture() -> None:
    catalog_ts = (ROOT / "apps/web/lib/catalog.ts").read_text(encoding="utf-8")
    quality_ts = (ROOT / "apps/web/lib/dataQuality.ts").read_text(encoding="utf-8")
    executives_ts = (ROOT / "apps/web/lib/executives.ts").read_text(encoding="utf-8")
    assert '"yamagata-prefecture"' in catalog_ts
    assert "yamagata_prefecture_finance_sources.json" in catalog_ts
    assert "data/reviewed/yamagata-prefecture/settlement_records.json" in quality_ts
    assert '"jp-local-060003": "yamagata-prefecture"' in executives_ts
