"""Safety tests for Funabashi Phase 15 non-public review candidate."""

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "data/candidates/funabashi-city/review_candidate.json"
INVENTORY = ROOT / "data/indexed/funabashi-city/source_inventory.json"
SCHEMA = ROOT / "schemas/phase15_review_candidate.schema.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"
WEB_ROOT = ROOT / "apps/web"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_funabashi_candidate_validates_and_is_not_published():
    candidate = read(CANDIDATE)
    schema = read(SCHEMA)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = list(validator.iter_errors(candidate))
    assert errors == []
    assert candidate["candidate_id"] == "funabashi-phase15-review-candidate"
    assert candidate["phase"] == 15
    assert candidate["official_code"] == "122041"
    assert candidate["name_ja"] == "船橋市"
    assert (
        candidate["source_inventory_path"]
        == "data/indexed/funabashi-city/source_inventory.json"
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


def test_funabashi_sources_match_existing_official_inventory():
    candidate = read(CANDIDATE)
    inventory = read(INVENTORY)
    sources = candidate["candidate_package"]["source_catalog"]["sources"]
    expected = inventory["sources"]
    assert len(sources) == len(expected) == 4
    assert {source["id"] for source in sources} == {
        source["id"] for source in expected
    }
    actual_urls = {(source["id"], source["official_url"]) for source in sources}
    assert actual_urls == {
        (source["id"], source["official_url"]) for source in expected
    }
    assert all(
        source["official_url"].startswith("https://www.city.funabashi.lg.jp/")
        for source in sources
    )
    assert all(
        source["verification_status"] == "primary_source_live_verified_2026-11-16"
        for source in sources
    )
    assert all(bool(source["evidence_location"]) for source in sources)
    assert all(bool(source["use_boundary"]) for source in sources)


def test_funabashi_prepared_candidate_records_only_verified_fiscal_values():
    candidate = read(CANDIDATE)
    package = candidate["candidate_package"]

    fiscal_records = package["fiscal_records"]
    assert len(fiscal_records) == 3
    by_id = {rec["id"]: rec for rec in fiscal_records}
    assert set(by_id) == {
        "jp-local-122041-fiscal-2026-total-expenditure",
        "jp-local-122041-fiscal-2024-total-revenue",
        "jp-local-122041-fiscal-2024-total-expenditure",
    }
    assert all(
        rec["municipality_id"] == "jp-local-122041" for rec in fiscal_records
    )
    assert all(rec["account_type"] == "general" for rec in fiscal_records)
    assert all(rec["value_status"] == "available" for rec in fiscal_records)
    assert all(rec["review_status"] == "needs_review" for rec in fiscal_records)
    assert all(rec["confidence"] == "medium" for rec in fiscal_records)

    # The FY2026 initial budget was enacted (可決) as bill No. 1 at the
    # 1st regular council session of 2026 (vote on 2026-03-25), so it
    # must not be labelled as a draft proposal (予算案). The amount is
    # the exact sen-yen figure stated in Article 1 of the official
    # budget book (270,640,000千円).
    budget = by_id["jp-local-122041-fiscal-2026-total-expenditure"]
    assert budget["fiscal_year"] == 2026
    assert budget["stage"] == "initial_budget"
    assert budget["metric"] == "total_expenditure"
    assert budget["metric_label"] == "一般会計当初予算総額"
    assert budget["amount_yen"] == 270640000000

    # The FY2024 settlement totals are published only at sen-yen
    # precision in the official settlement overview; they are recorded
    # at that published precision without synthesising yen-level
    # figures. Their difference must equal the published balance
    # (形式収支) of 6,085,018千円.
    revenue = by_id["jp-local-122041-fiscal-2024-total-revenue"]
    assert revenue["fiscal_year"] == 2024
    assert revenue["stage"] == "settlement"
    assert revenue["metric"] == "total_revenue"
    assert revenue["amount_yen"] == 249314444000
    expenditure = by_id["jp-local-122041-fiscal-2024-total-expenditure"]
    assert expenditure["fiscal_year"] == 2024
    assert expenditure["stage"] == "settlement"
    assert expenditure["metric"] == "total_expenditure"
    assert expenditure["amount_yen"] == 243229426000
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 6085018000
    assert "千円" in revenue["note"]
    assert "千円" in expenditure["note"]

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

    # The FY2026 budget claim must record the enactment: bill No. 1,
    # passed on 2026-03-25.
    budget_packet = next(
        pkt
        for pkt in packets
        if pkt["subject_id"] == "jp-local-122041-fiscal-2026-total-expenditure"
    )
    assert "議案第1号" in budget_packet["claims"][0]["statement"]
    assert "可決" in budget_packet["claims"][0]["statement"]
    assert "議案第1号" in budget["note"]
    assert "令和8年3月25日" in budget["note"]

    # The FY2024 settlement was certified (認定) as certification
    # bill No. 1 (認定第1号) on 2025-10-03 at the 3rd regular council
    # session of 2025, confirmed from the council's official agenda
    # record and the board of education minutes.
    revenue_packet = next(
        pkt
        for pkt in packets
        if pkt["subject_id"] == "jp-local-122041-fiscal-2024-total-revenue"
    )
    assert "認定第1号" in revenue_packet["claims"][0]["statement"]
    assert "令和7年10月3日" in revenue_packet["claims"][0]["statement"]
    assert "認定" in revenue_packet["claims"][0]["statement"]
    assert "認定第1号" in revenue["note"]
    assert "認定第1号" in expenditure["note"]

    plan_review = package["plan_review"]
    assert plan_review["review_status"] == "pending_record_review"
    decisions = {rec["id"]: rec["decision"] for rec in plan_review["records"]}
    # FY2024 falls inside the current plan period, but the settlement
    # totals alone do not establish a linkage to individual plan
    # projects, so the linkage stays explicitly not assessable.
    assert decisions["funabashi-fy2024-settlement-linkage"] == "not_assessable"
    assert all(
        decision in {"needs_review", "not_assessable"}
        for decision in decisions.values()
    )
    period = next(
        rec
        for rec in plan_review["records"]
        if rec["id"] == "funabashi-current-plan-period"
    )
    assert period["value"] == "2022年度～2031年度"

    # The current plan is the 3rd comprehensive plan (2022-2031), a
    # single ten-year basic plan (no first/second-half split), with
    # the future-city vision recorded verbatim from the official plan.
    current_plan = package["policy_structure"]["current_plan"]
    assert current_plan["title"] == "第3次船橋市総合計画"
    assert current_plan["start_fiscal_year"] == 2022
    assert current_plan["end_fiscal_year"] == 2031
    assert current_plan["vision"] == "人も まちも 輝く 笑顔あふれる 船橋"
    # The basic plan is composed of 24 basic measures (基本施策) with
    # 71 measures (施策) in total, exactly as published in the plan
    # book's structure chart; individual projects are not enumerated.
    # The five "aimed city images" (めざすまちの姿) relate to the
    # basic measures through a matrix, not a hierarchy, so they are
    # recorded in management_principles instead of as goal parents.
    goals = current_plan["basic_goals"]
    assert [goal["name_ja"] for goal in goals] == [
        "健康増進",
        "地域医療",
        "高齢者福祉",
        "地域福祉・生活困窮者支援",
        "障害福祉",
        "国民健康保険・介護保険",
        "子ども・子育て支援",
        "学校教育",
        "生涯学習",
        "文化・スポーツ",
        "防災・減災",
        "消防",
        "市民活動",
        "多文化共生・男女共同参画・平和",
        "住まい",
        "生活安全・生活衛生",
        "商工業",
        "農水産業",
        "計画的な都市づくり",
        "道路・交通",
        "汚水処理",
        "自然との共生",
        "環境負荷の低減",
        "広報広聴・魅力発信",
    ]
    assert sum(len(goal["measures"]) for goal in goals) == 71


def test_funabashi_promotion_is_reflected_in_queue_state():
    queue = read(QUEUE)
    item = next(
        row for row in queue["execution_queue"] if row["official_code"] == "122041"
    )
    assert item["status"] == "reviewed_complete"
    assert item["completion_path"] == "data/catalog/funabashi_phase15_completion.json"
    assert (ROOT / item["completion_path"]).is_file()
    assert queue["summary"]["reviewed_complete_count"] == 28
    assert queue["summary"]["pending_record_review_count"] == 39
    assert queue["summary"]["next_official_code"] == "212016"


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
