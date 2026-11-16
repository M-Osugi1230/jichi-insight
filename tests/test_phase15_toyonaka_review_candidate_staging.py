"""Safety tests for Toyonaka Phase 15 non-public review candidate."""

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "data/candidates/toyonaka-city/review_candidate.json"
INVENTORY = ROOT / "data/indexed/toyonaka-city/source_inventory.json"
SCHEMA = ROOT / "schemas/phase15_review_candidate.schema.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"
WEB_ROOT = ROOT / "apps/web"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_toyonaka_candidate_validates_and_is_not_published():
    candidate = read(CANDIDATE)
    schema = read(SCHEMA)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = list(validator.iter_errors(candidate))
    assert errors == []
    assert candidate["candidate_id"] == "toyonaka-phase15-review-candidate"
    assert candidate["phase"] == 15
    assert candidate["official_code"] == "272035"
    assert candidate["name_ja"] == "豊中市"
    assert (
        candidate["source_inventory_path"]
        == "data/indexed/toyonaka-city/source_inventory.json"
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


def test_toyonaka_sources_match_existing_official_inventory():
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
        source["official_url"].startswith("https://www.city.toyonaka.osaka.jp/")
        for source in sources
    )
    assert all(
        source["verification_status"] == "primary_source_live_verified_2026-11-16"
        for source in sources
    )
    assert all(bool(source["evidence_location"]) for source in sources)
    assert all(bool(source["use_boundary"]) for source in sources)


def test_toyonaka_prepared_candidate_records_only_verified_fiscal_values():
    candidate = read(CANDIDATE)
    package = candidate["candidate_package"]

    fiscal_records = package["fiscal_records"]
    assert len(fiscal_records) == 3
    by_id = {rec["id"]: rec for rec in fiscal_records}
    assert set(by_id) == {
        "jp-local-272035-fiscal-2026-total-expenditure",
        "jp-local-272035-fiscal-2024-total-revenue",
        "jp-local-272035-fiscal-2024-total-expenditure",
    }
    assert all(rec["municipality_id"] == "jp-local-272035" for rec in fiscal_records)
    assert all(rec["account_type"] == "general" for rec in fiscal_records)
    assert all(rec["value_status"] == "available" for rec in fiscal_records)
    assert all(rec["review_status"] == "needs_review" for rec in fiscal_records)
    assert all(rec["confidence"] == "medium" for rec in fiscal_records)

    # The FY2026 initial budget was submitted to the
    # March 2026 regular session as bill No. 8
    # (市議案第8号) on 2026-02-24 and was passed as
    # 原案可決 on 2026-03-23 according to the
    # council's official voting-results page, so the
    # budget must not be labelled as a draft proposal
    # (予算案). The amount is the exact sen-yen total
    # published in the official budget book
    # (市議案第8号, Article 1: 206,946,719 thousand
    # yen), recorded at thousand-yen precision
    # without synthesising a yen figure.
    budget = by_id["jp-local-272035-fiscal-2026-total-expenditure"]
    assert budget["fiscal_year"] == 2026
    assert budget["stage"] == "initial_budget"
    assert budget["metric"] == "total_expenditure"
    assert budget["metric_label"] == "一般会計当初予算総額"
    assert budget["amount_yen"] == 206946719000
    assert "市議案第8号" in budget["note"]
    assert "令和8年3月23日" in budget["note"]
    assert "成立" in budget["note"]
    assert "原案可決" in budget["note"]

    # The FY2024 settlement totals are published at
    # yen precision in the official settlement book
    # (general-account revenue/expenditure
    # settlement), so the yen figures below are the
    # exact published totals. Their difference must
    # equal the balance of 5,472,555,198 yen printed
    # in the settlement book, and the expenditure
    # total plus the carryover and the unused amount
    # must equal the published budget total.
    revenue = by_id["jp-local-272035-fiscal-2024-total-revenue"]
    assert revenue["fiscal_year"] == 2024
    assert revenue["stage"] == "settlement"
    assert revenue["metric"] == "total_revenue"
    assert revenue["amount_yen"] == 197263021788
    expenditure = by_id["jp-local-272035-fiscal-2024-total-expenditure"]
    assert expenditure["fiscal_year"] == 2024
    assert expenditure["stage"] == "settlement"
    assert expenditure["metric"] == "total_expenditure"
    assert expenditure["amount_yen"] == 191790466590
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 5472555198
    assert expenditure["amount_yen"] + 4049909000 + 11524209410 == 207364585000

    # The actual balance (実質収支) is confirmed in
    # the official statement of actual balance
    # (実質収支に関する調書) itself, but that
    # statement is published at thousand-yen
    # precision with per-item rounding (4,930,077
    # thousand yen, after deducting 542,478 thousand
    # yen of resources to be carried forward from
    # the 5,472,555 thousand yen formal balance), so
    # the candidate records it at thousand-yen
    # precision exactly as published and does not
    # synthesise a yen figure.
    assert "4,930,077千円" in revenue["note"]
    assert "542,478千円" in revenue["note"]

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

    # The FY2026 budget claim must record the
    # enactment route (市議案第8号, passed as
    # 原案可決 on 2026-03-23) exactly as the
    # council's official voting results publish it.
    budget_packet = next(
        pkt
        for pkt in packets
        if pkt["subject_id"] == "jp-local-272035-fiscal-2026-total-expenditure"
    )
    assert "市議案第8号" in budget_packet["claims"][0]["statement"]
    assert "成立" in budget_packet["claims"][0]["statement"]
    assert "令和8年3月23日" in budget_packet["claims"][0]["statement"]
    assert "原案可決" in budget_packet["claims"][0]["statement"]

    # The FY2024 settlement certification bill is
    # 市議案第74号. It was submitted to the
    # September 2025 regular session, carried over
    # for continued review, and the council's
    # official voting results for the December 2025
    # session directly record the result as NOT
    # certified (不認定) on 2025-11-28. The
    # candidate must record the rejection as a fact
    # and must never state that the settlement was
    # certified (認定された) in any claim statement
    # or fiscal note.
    revenue_packet = next(
        pkt
        for pkt in packets
        if pkt["subject_id"] == "jp-local-272035-fiscal-2024-total-revenue"
    )
    assert "市議案第74号" in revenue_packet["claims"][0]["statement"]
    assert "不認定" in revenue_packet["claims"][0]["statement"]
    assert "令和7年11月28日" in revenue_packet["claims"][0]["statement"]
    assert "認定された" not in revenue_packet["claims"][0]["statement"]
    expenditure_packet = next(
        pkt
        for pkt in packets
        if pkt["subject_id"] == "jp-local-272035-fiscal-2024-total-expenditure"
    )
    assert "市議案第74号" in expenditure_packet["claims"][0]["statement"]
    assert "不認定" in expenditure_packet["claims"][0]["statement"]
    assert "認定された" not in expenditure_packet["claims"][0]["statement"]
    assert "市議案第74号" in revenue["note"]
    assert "市議案第74号" in expenditure["note"]
    assert "令和7年11月28日" in revenue["note"]
    assert "不認定" in revenue["note"]
    assert "不認定" in expenditure["note"]
    assert "認定された" not in revenue["note"]
    assert "認定された" not in expenditure["note"]
    assert "認定された" not in revenue_packet["claims"][0]["review_note"]
    assert "認定された" not in expenditure_packet["claims"][0]["review_note"]

    plan_review = package["plan_review"]
    assert plan_review["review_status"] == "pending_record_review"
    decisions = {rec["id"]: rec["decision"] for rec in plan_review["records"]}
    # FY2024 falls inside the latter basic plan
    # period (FY2023-FY2027), so the plan version is
    # the same, but no official total-level mapping
    # from settlement totals to the plan's 16
    # measures or the leading project exists. The
    # linkage therefore stays not assessable.
    assert decisions["toyonaka-fy2024-settlement-linkage"] == "not_assessable"
    assert all(
        decision in {"needs_review", "not_assessable"}
        for decision in decisions.values()
    )
    period = next(
        rec
        for rec in plan_review["records"]
        if rec["id"] == "toyonaka-current-plan-period"
    )
    assert period["value"] == "2018年度～2027年度"

    # The succession of basic plans is recorded only
    # as version chronology, never by retroactively
    # mapping another plan's framework onto prior
    # results.
    transition = next(
        rec
        for rec in plan_review["records"]
        if rec["id"] == "toyonaka-plan-transition"
    )
    assert transition["evidence_role"] == "plan_transition"
    assert "前期基本計画" in transition["statement"]
    assert "後期基本計画" in transition["statement"]

    # The current operative plan layer is the latter
    # basic plan of the 4th Toyonaka City
    # Comprehensive Plan (FY2023-FY2027), under the
    # Basic Concept (FY2018-FY2027) whose vision is
    # みらい創造都市 とよなか
    # ～明日がもっと楽しみなまち～. Its structure is
    # five chapters and 16 measures, exactly as
    # published on the official plan page.
    current_plan = package["policy_structure"]["current_plan"]
    assert current_plan["title"] == "第4次豊中市総合計画 後期基本計画"
    assert (
        current_plan["vision"]
        == "みらい創造都市 とよなか ～明日がもっと楽しみなまち～"
    )
    assert current_plan["start_fiscal_year"] == 2023
    assert current_plan["end_fiscal_year"] == 2027
    fields = current_plan["policy_fields"]
    assert [field["name_ja"] for field in fields] == [
        "第1章 子ども・若者が夢や希望をもてるまちづくり",
        "第2章 安全に安心して暮らせるまちづくり",
        "第3章 活力ある快適なまちづくり",
        "第4章 いきいきと心豊かに暮らせるまちづくり",
        "第5章 施策推進に向けた取組み",
    ]
    assert [field["measures"] for field in fields] == [
        [
            "妊娠・出産・子育て支援の充実",
            "教育環境の充実",
            "子ども・若者への総合的な支援の充実",
        ],
        [
            "住み慣れた地域で暮らし続けられるまちづくりの推進",
            "保健・医療環境の充実",
            "消防・救急救命体制の充実",
            "災害に強く、犯罪を防ぎ、安全に暮らせる地域づくり",
        ],
        [
            "環境意識の向上と快適なまちの環境の保全・創造",
            "脱炭素・循環型社会の構築",
            "安全で安心なまちの基盤づくり",
            "だれもが住みやすい住環境の実現",
            "産業振興の充実",
        ],
        ["共に生きる平和なまちづくり", "学びと文化のあふれるまちづくり"],
        ["情報共有・参画・協働に基づくまちづくり", "持続可能な市政運営の推進"],
    ]
    assert sum(len(field["measures"]) for field in fields) == 16


def test_toyonaka_promotion_is_reflected_in_canonical_queue():
    queue = read(QUEUE)
    item = next(
        row for row in queue["execution_queue"] if row["official_code"] == "272035"
    )
    assert item["status"] == "reviewed_complete"
    assert item["completion_path"] == "data/catalog/toyonaka_phase15_completion.json"
    assert queue["summary"]["reviewed_complete_count"] == 55
    assert queue["summary"]["pending_record_review_count"] == 12
    assert queue["summary"]["next_official_code"] == "362018"


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
