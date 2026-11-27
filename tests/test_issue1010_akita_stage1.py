import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "reviewed" / "akita-prefecture"
PLAN_URL = (
    "https://www.pref.akita.lg.jp/uploads/public/archive_0000094577_00/"
    "%E3%80%90%E8%BB%BD%E9%87%8F%E7%89%88%E3%80%91"
    "%E7%A7%8B%E7%94%B0%E7%9C%8C%E7%B7%8F%E5%90%88%E8%A8%88%E7%94%BB"
    "%EF%BC%88%E5%86%8A%E5%AD%90%E3%83%BB%E8%A6%8B%E9%96%8B%E3%81%8D%EF%BC%89.pdf"
)
FISCAL_STATUS_ID = "akita-prefecture-fiscal-status-2026-06"
ASSEMBLY_VOTES_ID = "akita-prefecture-assembly-2026-feb-session-votes"
BUDGET_OUTLINE_ID = "akita-prefecture-budget-outline-fy2026"
BULLETIN_ID = "akita-pref-governor-election-2025-bulletin"


def load_json(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def load_base(name: str):
    return json.loads((BASE / name).read_text(encoding="utf-8"))


def test_municipality_identity_is_reviewed() -> None:
    municipality = load_base("municipality.json")
    assert municipality["id"] == "jp-local-050008"
    assert municipality["official_code"] == "050008"
    assert municipality["name_ja"] == "秋田県"
    assert municipality["official_url"] == "https://www.pref.akita.lg.jp/"
    assert municipality["data_status"] == "reviewed"
    assert municipality["fiscal_years"] == [2022, 2023, 2024, 2026]
    assert municipality["sources"][0] == "akita-pref-home"


def test_plan_review_registers_the_comprehensive_plan_without_projects() -> None:
    review = load_base("plan_review.json")
    assert review["id"] == "phase15-akita-plan-review"
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
    assert "秋田県総合計画" in identity["statement"]
    assert "令和8年（2026年）3月" in identity["statement"]
    structure = next(
        r for r in review["records"] if r["evidence_role"] == "policy_structure"
    )
    assert "8つの政策" in structure["statement"]
    assert "施策" in structure["statement"]
    governance = next(
        r for r in review["records"]
        if r["evidence_role"] == "progress_governance"
    )
    # The new plan's annual evaluation format is not yet published;
    # fixing the registration unit is deferred to stage 2.
    assert "政策評価制度" in governance["statement"]
    assert "施策評価" in governance["statement"]
    assert "段階2" in governance["statement"]
    for record in review["records"]:
        assert record["source_url"] == PLAN_URL


def test_fiscal_records_register_the_enacted_initial_budget() -> None:
    records = load_base("fiscal_records.json")
    assert len(records) == 3
    by_metric = {record["metric"]: record for record in records}
    assert by_metric["total_revenue"]["amount_yen"] == 604_145_000_000
    assert by_metric["total_expenditure"]["amount_yen"] == 604_145_000_000
    for metric in ("total_revenue", "total_expenditure"):
        record = by_metric[metric]
        assert record["fiscal_year"] == 2026
        assert record["stage"] == "initial_budget"
        assert record["account_type"] == "general"
        assert set(record["sources"]) == {FISCAL_STATUS_ID, ASSEMBLY_VOTES_ID}
        # Bill No. 45 was decided 「原案可決」 on 2026-03-19.
        assert "原案可決" in record["note"]
        assert "2026年3月19日" in record["note"]


def test_fiscal_local_tax_is_carried_as_not_published() -> None:
    records = load_base("fiscal_records.json")
    local_tax = next(r for r in records if r["metric"] == "local_tax")
    # The prefectural tax is confirmed only to the million-yen figure
    # (99,270 million yen) in the web-published documents; the
    # thousand-yen figure is not published on the web, so no rounded
    # value is registered as an exact figure.
    assert local_tax["amount_yen"] is None
    assert local_tax["value"] is None
    assert local_tax["value_status"] == "not_published"
    assert "99,270百万円" in local_tax["note"]
    assert set(local_tax["sources"]) == {FISCAL_STATUS_ID, BUDGET_OUTLINE_ID}


def test_settlement_records_cover_three_years_with_fifty_one_records() -> None:
    records = load_base("settlement_records.json")
    assert len(records) == 51
    assert {record["fiscal_year"] for record in records} == {2022, 2023, 2024}
    for record in records:
        assert record["review_status"] == "reviewed"
        assert record["confidence"] == "high"
        year = record["fiscal_year"]
        assert record["sources"] == [
            f"akita-prefecture-mic-settlement-card-fy{year}",
            f"akita-prefecture-fiscal-situation-collection-fy{year}",
        ]


def test_settlement_values_match_the_cross_checked_sources() -> None:
    records = load_base("settlement_records.json")
    by_key = {(r["fiscal_year"], r["metric"]): r for r in records}
    fy2024 = {metric: r for (year, metric), r in by_key.items() if year == 2024}
    assert fy2024["total_revenue"]["amount_yen"] == 633_863_121_000
    assert fy2024["total_expenditure"]["amount_yen"] == 616_844_972_000
    assert fy2024["local_tax"]["amount_yen"] == 130_438_146_000
    assert fy2024["real_balance_ratio"]["value"] == 3.1
    # The labelled current balance ratio is registered, not the
    # parenthesised variant (89.7).
    assert fy2024["current_balance_ratio"]["value"] == 89.5
    assert fy2024["real_debt_service_ratio"]["value"] == 14.3
    assert fy2024["future_burden_ratio"]["value"] == 232.9
    assert fy2024["fiscal_strength_index"]["value"] == 0.32741
    assert fy2024["population"]["value"] == 907_593
    fund = fy2024["fund_balance"]
    assert fund["amount_yen"] == 74_436_862_000
    assert sum(item["amount_yen"] for item in fund["breakdown"]) == 74_436_862_000
    fund_by_key = {item["key"]: item["amount_yen"] for item in fund["breakdown"]}
    assert fund_by_key["debt_reduction_fund"] == 27_452_504_000
    debt = fy2024["debt_balance"]
    assert debt["amount_yen"] == 1_206_673_154_000
    assert sum(item["amount_yen"] for item in debt["breakdown"]) == 1_206_673_154_000
    debt_by_key = {item["key"]: item["amount_yen"] for item in debt["breakdown"]}
    # The temporary fiscal measures bonds figure is derived by
    # subtraction and marked as such in the breakdown note.
    assert debt_by_key["temporary_fiscal_measures_bonds"] == 350_193_637_000
    purpose = fy2024["expenditure_by_purpose"]
    assert len(purpose["breakdown"]) == 19
    assert (
        sum(item["amount_yen"] for item in purpose["breakdown"])
        == purpose["amount_yen"]
    )
    nature = fy2024["expenditure_by_nature"]
    assert len(nature["breakdown"]) == 17
    top_level = [
        item for item in nature["breakdown"] if item["parent_key"] is None
    ]
    assert sum(item["amount_yen"] for item in top_level) == nature["amount_yen"]


def test_settlement_arithmetic_holds_for_all_years() -> None:
    records = load_base("settlement_records.json")
    by_key = {(r["fiscal_year"], r["metric"]): r for r in records}
    for year in (2022, 2023, 2024):
        y = {metric: r for (yy, metric), r in by_key.items() if yy == year}
        assert (
            y["total_revenue"]["amount_yen"] - y["total_expenditure"]["amount_yen"]
            == y["formal_balance"]["amount_yen"]
        )
        assert (
            y["formal_balance"]["amount_yen"]
            - y["carryover_resources"]["amount_yen"]
            == y["real_balance"]["amount_yen"]
        )
        assert (
            sum(
                item["amount_yen"]
                for item in y["expenditure_by_purpose"]["breakdown"]
            )
            == y["total_expenditure"]["amount_yen"]
        )
        assert (
            sum(
                item["amount_yen"]
                for item in y["expenditure_by_nature"]["breakdown"]
                if item["parent_key"] is None
            )
            == y["total_expenditure"]["amount_yen"]
        )


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
            f"akita-prefecture-mic-settlement-card-fy{year}",
            f"akita-prefecture-fiscal-situation-collection-fy{year}",
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
    assert total["claims"][0]["source_ids"] == [
        FISCAL_STATUS_ID,
        ASSEMBLY_VOTES_ID,
    ]
    local_tax = next(
        packet for packet in packets
        if packet["subject_id"].endswith("local-tax")
    )
    # The thousand-yen fixing route for the prefectural tax is
    # recorded as an open question.
    assert any("千円" in question for question in local_tax["open_questions"])


def test_governor_term_is_registered_with_the_bulletin_source() -> None:
    terms = load_json("data/entities/executives/executive_terms.json")
    term = next(t for t in terms if t["municipality_id"] == "jp-local-050008")
    assert term["id"] == "jp-local-050008-executive-2025-04-20"
    assert term["person_name"] == "鈴木 健太"
    assert term["term_start"] == "2025-04-20"
    assert term["term_end"] == "2029-04-19"
    assert term["election_date"] == "2025-04-06"
    # The 2025 election bulletin survives as a copy on the Yurihonjo
    # City official site, verified byte-identical to its Wayback
    # Machine capture, so it is registered as the manifesto source.
    assert term["manifesto_source_ids"] == [BULLETIN_ID]
    assert set(term["sources"]) == {
        "akita-pref-governor-inauguration-2025",
        "akita-pref-term-list",
        "akita-pref-governor-election-2025-results",
        "akita-pref-governor-election-2025-results-page",
        "akita-pref-governor-election-2025-gazette",
        # Stage 3 (Issue #1038) added the bulletin itself, the
        # source of the registered promises, to the term sources.
        BULLETIN_ID,
    }


def test_governor_evidence_packet_records_votes_and_open_questions() -> None:
    packets = load_json("data/entities/executives/evidence_packets.json")
    packet = next(
        p for p in packets if p["id"] == "evidence-akita-pref-current-governor-term"
    )
    assert {claim["field"] for claim in packet["claims"]} == {
        "person_name",
        "election_date",
        "term_start",
        "term_end",
        "election_proclamation_date",
    }
    election = next(
        claim for claim in packet["claims"] if claim["field"] == "election_date"
    )
    assert "273,270" in election["statement"]
    assert len(packet["open_questions"]) == 1
    assert "開始日" in packet["open_questions"][0]


def test_manifesto_search_registers_the_verified_bulletin_copy() -> None:
    searches = load_json("data/entities/executives/manifesto_source_searches.json")
    search = next(
        s for s in searches if s["id"] == "manifesto-source-search-akita-pref-2025"
    )
    assert search["executive_term_id"] == "jp-local-050008-executive-2025-04-20"
    assert search["result_status"] == "source_registered"
    assert search["manifesto_source_ids_found"] == [BULLETIN_ID]
    assert search["nonexistence_claim"] is False
    # The copy's byte identity with the 2025-05-15 Wayback capture is
    # the recorded basis for treating the copy as the original.
    assert "680355120c3afb5c17ece4fb9dd63ef086fdd8063953c6630f367a9d2f7d34f8" in (
        search["review_note"]
    )


def test_source_catalog_registers_only_verified_prefecture_sources() -> None:
    catalog = load_json("data/catalog/akita_prefecture_finance_sources.json")
    assert catalog["version"] == "0.1.0"
    assert catalog["scope"] == "cluster18-akita-deep-dive"
    assert len(catalog["records"]) == 12
    assert {
        record["municipality_key"] for record in catalog["records"]
    } == {"akita-prefecture"}
    card = next(
        r for r in catalog["records"]
        if r["id"] == "akita-prefecture-mic-settlement-card-fy2024"
    )
    assert card["url"] == "https://www.soumu.go.jp/main_content/001064044.xlsx"
    collection = next(
        r for r in catalog["records"]
        if r["id"] == "akita-prefecture-fiscal-situation-collection-fy2024"
    )
    assert collection["url"] == (
        "https://www.soumu.go.jp/main_content/001063380.xlsx"
    )


def test_executive_catalog_includes_the_akita_sources() -> None:
    catalog = load_json("data/catalog/executive_sources.json")
    assert catalog["version"] == "0.69.0"
    assert len(catalog["records"]) == 223
    akita = [
        r for r in catalog["records"] if r["municipality_key"] == "akita-prefecture"
    ]
    assert len(akita) == 6
    bulletin = next(r for r in akita if r["id"] == BULLETIN_ID)
    assert bulletin["url"] == (
        "https://www.city.yurihonjo.lg.jp/_res/projects/default_project/"
        "_page_/001/011/232/tijikouhou.pdf"
    )


def test_web_wiring_includes_akita_prefecture() -> None:
    catalog_ts = (ROOT / "apps/web/lib/catalog.ts").read_text(encoding="utf-8")
    quality_ts = (ROOT / "apps/web/lib/dataQuality.ts").read_text(encoding="utf-8")
    executives_ts = (ROOT / "apps/web/lib/executives.ts").read_text(encoding="utf-8")
    assert '"akita-prefecture"' in catalog_ts
    assert "akita_prefecture_finance_sources.json" in catalog_ts
    assert "data/reviewed/akita-prefecture/settlement_records.json" in quality_ts
    assert '"jp-local-050008": "akita-prefecture"' in executives_ts
