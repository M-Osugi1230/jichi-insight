"""Safety tests for Fukui Phase 15 non-public review candidate."""

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "data/candidates/fukui-city/review_candidate.json"
INVENTORY = ROOT / "data/indexed/fukui-city/source_inventory.json"
SCHEMA = ROOT / "schemas/phase15_review_candidate.schema.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"
WEB_ROOT = ROOT / "apps/web"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_fukui_candidate_validates_and_is_not_published():
    candidate = read(CANDIDATE)
    schema = read(SCHEMA)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = list(validator.iter_errors(candidate))
    assert errors == []
    assert candidate["candidate_id"] == "fukui-phase15-review-candidate"
    assert candidate["phase"] == 15
    assert candidate["official_code"] == "182010"
    assert candidate["name_ja"] == "福井市"
    assert (
        candidate["source_inventory_path"]
        == "data/indexed/fukui-city/source_inventory.json"
    )
    assert (ROOT / candidate["source_inventory_path"]).is_file()
    assert candidate["status"] == "review_candidate"
    assert candidate["package_state"] == "prepared"
    assert candidate["human_review"]["required"] is True
    assert candidate["human_review"]["status"] == "approved"
    assert candidate["human_review"]["reviewed_at"] == "2026-11-16"
    assert candidate["human_review"]["reviewer_note"]
    # The owner did not review the primary sources personally: on
    # 2026-11-15 the owner explicitly delegated the review to Muse in
    # chat, and the note must record that delegation rather than
    # claiming an owner review.
    assert "委任" in candidate["human_review"]["reviewer_note"]
    assert "レビューはあなたがやってください" in candidate["human_review"]["reviewer_note"]
    assert candidate["publication"]["eligible"] is False


def test_fukui_sources_match_existing_official_inventory():
    candidate = read(CANDIDATE)
    inventory = read(INVENTORY)
    sources = candidate["candidate_package"]["source_catalog"]["sources"]
    expected = inventory["sources"]
    assert len(sources) == len(expected) == 5
    assert {source["id"] for source in sources} == {
        source["id"] for source in expected
    }
    actual_urls = {(source["id"], source["official_url"]) for source in sources}
    assert actual_urls == {
        (source["id"], source["official_url"]) for source in expected
    }
    assert all(
        source["official_url"].startswith("https://www.city.fukui.lg.jp/")
        for source in sources
    )
    assert all(
        source["verification_status"] == "primary_source_live_verified_2026-11-16"
        for source in sources
    )
    assert all(bool(source["evidence_location"]) for source in sources)
    assert all(bool(source["use_boundary"]) for source in sources)


def test_fukui_prepared_candidate_records_only_verified_fiscal_values():
    candidate = read(CANDIDATE)
    package = candidate["candidate_package"]

    fiscal_records = package["fiscal_records"]
    assert len(fiscal_records) == 3
    by_id = {rec["id"]: rec for rec in fiscal_records}
    assert set(by_id) == {
        "jp-local-182010-fiscal-2026-total-expenditure",
        "jp-local-182010-fiscal-2024-total-revenue",
        "jp-local-182010-fiscal-2024-total-expenditure",
    }
    assert all(rec["municipality_id"] == "jp-local-182010" for rec in fiscal_records)
    assert all(rec["account_type"] == "general" for rec in fiscal_records)
    assert all(rec["value_status"] == "available" for rec in fiscal_records)
    assert all(rec["review_status"] == "needs_review" for rec in fiscal_records)
    assert all(rec["confidence"] == "medium" for rec in fiscal_records)

    # The FY2026 initial budget was enacted as bill No. 1
    # (第1号議案) at the March 2026 regular council session,
    # passed as proposed (原案可決) on 2026-03-19, so it must
    # not be labelled as a draft proposal (予算案). The amount
    # is the exact sen-yen total in the official budget
    # overview (137,700,000千円, down 2,430,000千円 / 1.7%
    # from FY2025's 140,130,000千円).
    budget = by_id["jp-local-182010-fiscal-2026-total-expenditure"]
    assert budget["fiscal_year"] == 2026
    assert budget["stage"] == "initial_budget"
    assert budget["metric"] == "total_expenditure"
    assert budget["metric_label"] == "一般会計当初予算総額"
    assert budget["amount_yen"] == 137700000000
    assert "第1号議案" in budget["note"]
    assert "令和8年3月19日" in budget["note"]
    assert "原案可決" in budget["note"]

    # The FY2024 settlement totals are published at yen
    # precision in the city's official settlement summary
    # table (総表・その2, 単位 円), so the yen figures below
    # are the exact published totals. Their difference must
    # equal the published balance (差引・形式収支) of
    # 3,208,396,731 yen.
    revenue = by_id["jp-local-182010-fiscal-2024-total-revenue"]
    assert revenue["fiscal_year"] == 2024
    assert revenue["stage"] == "settlement"
    assert revenue["metric"] == "total_revenue"
    assert revenue["amount_yen"] == 133427298121
    expenditure = by_id["jp-local-182010-fiscal-2024-total-expenditure"]
    assert expenditure["fiscal_year"] == 2024
    assert expenditure["stage"] == "settlement"
    assert expenditure["metric"] == "total_expenditure"
    assert expenditure["amount_yen"] == 130218901390
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 3208396731

    packets = package["evidence_packets"]
    assert {pkt["subject_id"] for pkt in packets} == set(by_id)
    assert all(pkt["subject_type"] == "fiscal_record" for pkt in packets)
    assert all(pkt["review_status"] == "needs_review" for pkt in packets)
    assert all(pkt["claims"] for pkt in packets)
    assert all(
        claim["decision"] == "needs_review" and bool(claim["location_note"])
        for pkt in packets
        for claim in pkt["claims"]
    )

    # The FY2026 budget claim must record the enactment
    # route (bill No. 1, passed as proposed on 2026-03-19).
    budget_packet = next(
        pkt
        for pkt in packets
        if pkt["subject_id"] == "jp-local-182010-fiscal-2026-total-expenditure"
    )
    assert "第1号議案" in budget_packet["claims"][0]["statement"]
    assert "原案可決" in budget_packet["claims"][0]["statement"]
    assert "成立" in budget_packet["claims"][0]["statement"]

    # The FY2024 settlement was certified as bill No. 66
    # (第66号議案, covering the general and special accounts)
    # on 2025-12-01, per the council's official deliberation
    # results for the December 2025 regular session.
    revenue_packet = next(
        pkt
        for pkt in packets
        if pkt["subject_id"] == "jp-local-182010-fiscal-2024-total-revenue"
    )
    assert "第66号議案" in revenue_packet["claims"][0]["statement"]
    assert "令和7年12月1日" in revenue_packet["claims"][0]["statement"]
    assert "認定" in revenue_packet["claims"][0]["statement"]
    assert "第66号議案" in revenue["note"]
    assert "第66号議案" in expenditure["note"]

    plan_review = package["plan_review"]
    assert plan_review["review_status"] == "pending_record_review"
    decisions = {rec["id"]: rec["decision"] for rec in plan_review["records"]}
    # FY2024 is the third year of the plan period, but
    # settlement totals are section-level aggregates with no
    # official mapping to individual policies or KPIs, so
    # the linkage stays explicitly not assessable.
    assert decisions["fukui-fy2024-settlement-linkage"] == "not_assessable"
    assert all(
        decision in {"needs_review", "not_assessable"}
        for decision in decisions.values()
    )
    period = next(
        rec for rec in plan_review["records"] if rec["id"] == "fukui-current-plan-period"
    )
    assert period["value"] == "2022年度～2026年度"

    # The next (ninth) plan is recorded only as a version
    # chronology record, never merged back into the eighth
    # plan's framework.
    transition = next(
        rec
        for rec in plan_review["records"]
        if rec["id"] == "fukui-ninth-plan-transition"
    )
    assert transition["evidence_role"] == "plan_transition"
    assert "第九次福井市総合計画" in transition["statement"]

    # The current plan is the Eighth Fukui City
    # Comprehensive Plan (FY2022 to FY2026), a five-year
    # plan under the inherited city vision. Its policy
    # structure is four fields holding 14 policies, exactly
    # as published in the city's official FY2024 KPI report;
    # the 53 measures and 64 KPIs under the policies are
    # not enumerated here.
    current_plan = package["policy_structure"]["current_plan"]
    assert current_plan["title"] == "第八次福井市総合計画"
    assert current_plan["start_fiscal_year"] == 2022
    assert current_plan["end_fiscal_year"] == 2026
    assert current_plan["vision"] == "みんなが輝く 全国に誇れる ふくい"
    goals = current_plan["basic_goals"]
    assert [goal["name_ja"] for goal in goals] == [
        "社会基盤分野（快適に暮らすまち）",
        "市民福祉分野（住みよいまち）",
        "産業分野（活き活きと働くまち）",
        "教育分野（学び成長するまち）",
    ]
    assert [goal["measures"] for goal in goals] == [
        [
            "公共交通に関する政策",
            "中心市街地に関する政策",
            "生活インフラに関する政策",
        ],
        [
            "地域活性化に関する政策",
            "共生、協働に関する政策",
            "福祉に関する政策",
            "環境に関する政策",
            "防災、安全安心に関する政策",
        ],
        [
            "農林水産業に関する政策",
            "商工業に関する政策",
            "観光に関する政策",
        ],
        [
            "文化、歴史、自然に関する政策",
            "学校教育に関する政策",
            "生涯学習、生涯スポーツに関する政策",
        ],
    ]


def test_fukui_promotion_is_reflected_in_canonical_queue():
    queue = read(QUEUE)
    item = next(
        row for row in queue["execution_queue"] if row["official_code"] == "182010"
    )
    assert item["status"] == "reviewed_complete"
    assert item["completion_path"] == "data/catalog/fukui_phase15_completion.json"
    assert queue["summary"]["reviewed_complete_count"] == 43
    assert queue["summary"]["pending_record_review_count"] == 24
    assert queue["summary"]["next_official_code"] == "282022"


def test_public_web_does_not_import_candidate_staging():
    violations = []
    for path in WEB_ROOT.rglob("*"):
        if (
            path.is_file()
            and path.suffix in {".ts", ".tsx", ".js", ".mjs"}
            and "data/candidates" in path.read_text(encoding="utf-8")
        ):
            violations.append(str(path.relative_to(ROOT)))
    assert violations == []
