"""Safety tests for Toyama Phase 15 non-public review candidate."""

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "data/candidates/toyama-city/review_candidate.json"
INVENTORY = ROOT / "data/indexed/toyama-city/source_inventory.json"
SCHEMA = ROOT / "schemas/phase15_review_candidate.schema.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"
WEB_ROOT = ROOT / "apps/web"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_toyama_candidate_validates_and_is_not_published():
    candidate = read(CANDIDATE)
    schema = read(SCHEMA)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = list(validator.iter_errors(candidate))
    assert errors == []
    assert candidate["candidate_id"] == "toyama-phase15-review-candidate"
    assert candidate["phase"] == 15
    assert candidate["official_code"] == "162019"
    assert candidate["name_ja"] == "富山市"
    assert (
        candidate["source_inventory_path"]
        == "data/indexed/toyama-city/source_inventory.json"
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


def test_toyama_sources_match_existing_official_inventory():
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
        source["official_url"].startswith("https://www.city.toyama.lg.jp/")
        for source in sources
    )
    assert all(
        source["verification_status"] == "primary_source_live_verified_2026-11-16"
        for source in sources
    )
    assert all(bool(source["evidence_location"]) for source in sources)
    assert all(bool(source["use_boundary"]) for source in sources)


def test_toyama_prepared_candidate_records_only_verified_fiscal_values():
    candidate = read(CANDIDATE)
    package = candidate["candidate_package"]

    fiscal_records = package["fiscal_records"]
    assert len(fiscal_records) == 3
    by_id = {rec["id"]: rec for rec in fiscal_records}
    assert set(by_id) == {
        "jp-local-162019-fiscal-2026-total-expenditure",
        "jp-local-162019-fiscal-2024-total-revenue",
        "jp-local-162019-fiscal-2024-total-expenditure",
    }
    assert all(rec["municipality_id"] == "jp-local-162019" for rec in fiscal_records)
    assert all(rec["account_type"] == "general" for rec in fiscal_records)
    assert all(rec["value_status"] == "available" for rec in fiscal_records)
    assert all(rec["review_status"] == "needs_review" for rec in fiscal_records)
    assert all(rec["confidence"] == "medium" for rec in fiscal_records)

    # The FY2026 initial budget was enacted (原案可決) as bill
    # No. 1 (議案第1号) at the March 2026 regular council
    # session (plenary vote on 2026-03-24), so it must not be
    # labelled as a draft proposal (予算案). The amount is the
    # exact sen-yen total in the official budget overview
    # (199,776,107千円); the external supplementary amount
    # moved forward to the March supplementary budget is not
    # part of the initial budget total.
    budget = by_id["jp-local-162019-fiscal-2026-total-expenditure"]
    assert budget["fiscal_year"] == 2026
    assert budget["stage"] == "initial_budget"
    assert budget["metric"] == "total_expenditure"
    assert budget["metric_label"] == "一般会計当初予算総額"
    assert budget["amount_yen"] == 199776107000

    # The FY2024 settlement totals are published only at
    # sen-yen precision in the city's official settlement
    # document (単位 千円), so the yen figures below are the
    # sen-yen values converted as-is, not synthesized yen
    # totals. Their difference must equal the published
    # balance (形式収支) of 4,119,305 thousand yen.
    revenue = by_id["jp-local-162019-fiscal-2024-total-revenue"]
    assert revenue["fiscal_year"] == 2024
    assert revenue["stage"] == "settlement"
    assert revenue["metric"] == "total_revenue"
    assert revenue["amount_yen"] == 189996111000
    expenditure = by_id["jp-local-162019-fiscal-2024-total-expenditure"]
    assert expenditure["fiscal_year"] == 2024
    assert expenditure["stage"] == "settlement"
    assert expenditure["metric"] == "total_expenditure"
    assert expenditure["amount_yen"] == 185876806000
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 4119305000
    assert "千円単位" in revenue["note"]
    assert "合成していない" in revenue["note"]

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

    # The FY2026 budget claim must record the enactment: bill
    # No. 1, passed as proposed on 2026-03-24.
    budget_packet = next(
        pkt
        for pkt in packets
        if pkt["subject_id"] == "jp-local-162019-fiscal-2026-total-expenditure"
    )
    assert "議案第1号" in budget_packet["claims"][0]["statement"]
    assert "可決" in budget_packet["claims"][0]["statement"]
    assert "議案第1号" in budget["note"]
    assert "令和8年3月24日" in budget["note"]

    # The FY2024 settlement was certified as certification
    # bill No. 1 (認定第1号) on 2025-11-28, after continued
    # review from the September 2025 session into the
    # December 2025 session, per the council newsletter.
    revenue_packet = next(
        pkt
        for pkt in packets
        if pkt["subject_id"] == "jp-local-162019-fiscal-2024-total-revenue"
    )
    assert "認定第1号" in revenue_packet["claims"][0]["statement"]
    assert "令和7年11月28日" in revenue_packet["claims"][0]["statement"]
    assert "認定" in revenue_packet["claims"][0]["statement"]
    assert "認定第1号" in revenue["note"]
    assert "認定第1号" in expenditure["note"]

    plan_review = package["plan_review"]
    assert plan_review["review_status"] == "pending_record_review"
    decisions = {rec["id"]: rec["decision"] for rec in plan_review["records"]}
    # FY2024 falls inside the latter basic plan period, but
    # settlement totals are section-level aggregates with no
    # official mapping to individual projects, so the linkage
    # stays explicitly not assessable.
    assert decisions["toyama-fy2024-settlement-linkage"] == "not_assessable"
    assert all(
        decision in {"needs_review", "not_assessable"}
        for decision in decisions.values()
    )
    period = next(
        rec for rec in plan_review["records"] if rec["id"] == "toyama-current-plan-period"
    )
    assert period["value"] == "2022年度～2026年度"

    # The third comprehensive plan is still being drafted and
    # must be recorded only as a transition record, never as
    # the current plan.
    transition = next(
        rec
        for rec in plan_review["records"]
        if rec["id"] == "toyama-next-plan-transition"
    )
    assert transition["evidence_role"] == "plan_transition"
    assert "策定" in transition["statement"]

    # The current plan is the 2nd Toyama City Comprehensive
    # Plan (basic concept FY2017 to FY2026, latter basic plan
    # FY2022 to FY2026). Its basic goals are the four town
    # development goals of the latter basic plan, and the
    # measures under each goal are its policies (14 in total),
    # exactly as published in official city documents; the 51
    # individual measures (施策) are not enumerated here.
    current_plan = package["policy_structure"]["current_plan"]
    assert current_plan["title"] == "第2次富山市総合計画"
    assert current_plan["start_fiscal_year"] == 2017
    assert current_plan["end_fiscal_year"] == 2026
    assert current_plan["vision"] == "人・まち・自然が調和する活力都市とやま"
    goals = current_plan["basic_goals"]
    assert [goal["name_ja"] for goal in goals] == [
        "すべての人が輝き安心して暮らせるまち【人材・暮らし】",
        "安心・安全で持続性のある魅力的なまち【都市・環境】",
        "人が集い活気にあふれ希望に満ちたまち【活力・交流】",
        "共生社会を実現し誇りを大切にする協働のまち【協働・連携】",
    ]
    assert [goal["measures"] for goal in goals] == [
        [
            "すべての世代が学び活躍できるひとづくり",
            "いつまでも元気で暮らせる健康づくり",
            "誰もが自立し安心して暮らせるまちづくり",
        ],
        [
            "人にやさしい安心・安全なまちづくり",
            "コンパクトなまちづくり",
            "潤いと安らぎのあるまちづくり",
            "自然にやさしいまちづくり",
        ],
        [
            "新たな価値を創出する産業づくり",
            "観光・交流のまちづくり",
            "いきいきと働けるまちづくり",
            "歴史・文化・芸術のまちづくり",
        ],
        [
            "市民協働による共生社会づくり",
            "市民の誇りづくり",
            "しなやかな行政体づくり",
        ],
    ]


def test_toyama_promotion_is_reflected_in_canonical_queue():
    queue = read(QUEUE)
    item = next(
        row for row in queue["execution_queue"] if row["official_code"] == "162019"
    )
    assert item["status"] == "reviewed_complete"
    assert item["completion_path"] == "data/catalog/toyama_phase15_completion.json"
    assert queue["summary"]["reviewed_complete_count"] == 68
    assert queue["summary"]["pending_record_review_count"] == 0
    assert queue["summary"]["next_official_code"] is None


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
