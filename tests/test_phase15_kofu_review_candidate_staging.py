from __future__ import annotations

import json
from pathlib import Path

import jsonschema

REPO_ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_PATH = REPO_ROOT / "data" / "candidates" / "kofu-city" / "review_candidate.json"
SCHEMA_PATH = REPO_ROOT / "schemas" / "phase15_review_candidate.schema.json"
QUEUE_PATH = REPO_ROOT / "data" / "catalog" / "phase15_core_capital_review_queue.json"
INVENTORY_PATH = REPO_ROOT / "data" / "indexed" / "kofu-city" / "source_inventory.json"
WEB_ROOT = REPO_ROOT / "web"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def fiscal_record(candidate: dict, record_id: str) -> dict:
    records = candidate["candidate_package"]["fiscal_records"]
    return next(record for record in records if record["id"] == record_id)


def evidence_packet(candidate: dict, packet_id: str) -> dict:
    packets = candidate["candidate_package"]["evidence_packets"]
    return next(packet for packet in packets if packet["id"] == packet_id)


def plan_record(candidate: dict, record_id: str) -> dict:
    records = candidate["candidate_package"]["plan_review"]["records"]
    return next(record for record in records if record["id"] == record_id)


def test_kofu_candidate_validates_and_is_not_published() -> None:
    candidate = load_json(CANDIDATE_PATH)
    schema = load_json(SCHEMA_PATH)

    jsonschema.Draft202012Validator(schema).validate(candidate)

    assert candidate["candidate_id"] == "kofu-phase15-review-candidate"
    assert candidate["official_code"] == "192015"
    assert candidate["name_ja"] == "甲府市"
    assert candidate["status"] == "review_candidate"
    assert candidate["package_state"] == "prepared"
    assert candidate["publication"]["eligible"] is False
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
    assert candidate["source_inventory_path"] == (
        "data/indexed/kofu-city/source_inventory.json"
    )


def test_kofu_sources_match_inventory_and_stay_official_only() -> None:
    candidate = load_json(CANDIDATE_PATH)
    inventory = load_json(INVENTORY_PATH)
    sources = candidate["candidate_package"]["source_catalog"]["sources"]
    inventory_sources = inventory["sources"]

    assert [source["id"] for source in sources] == [
        source["id"] for source in inventory_sources
    ]
    assert [source["official_url"] for source in sources] == [
        source["official_url"] for source in inventory_sources
    ]
    assert all(
        source["official_url"].startswith("https://www.city.kofu.yamanashi.jp/")
        for source in sources
    )
    assert all(source["evidence_location"] for source in sources)
    assert all(source["use_boundary"] for source in sources)
    by_id = {source["id"]: source for source in sources}
    for verified_id in (
        "kofu-seventh-plan",
        "kofu-budget-2026",
        "kofu-settlement-2024",
    ):
        assert by_id[verified_id]["verification_status"] == (
            "primary_source_live_verified_2026-11-16"
        )
    assert by_id["kofu-first-implementation-design"]["verification_status"] == (
        "official_landing_not_live_verified_2026-11-16"
    )


def test_kofu_fiscal_amounts_are_primary_source_verified() -> None:
    candidate = load_json(CANDIDATE_PATH)
    package = candidate["candidate_package"]

    assert len(package["fiscal_records"]) == 3
    for record in package["fiscal_records"]:
        assert record["value"] is None
        assert record["value_status"] == "available"
        assert record["confidence"] == "medium"
        assert record["review_status"] == "needs_review"

    # The FY2026 initial budget was enacted as bill No. 5 at the
    # March 2026 regular council session (vote on 2026-03-25), so it
    # must not be labelled as a draft proposal (予算案). The amount
    # is the sen-yen total on which the account summary table and
    # both the revenue and expenditure tables of the city's official
    # initial-budget materials agree (91,787,060千円); it is kept at
    # sen-yen precision and never expanded into synthetic yen.
    budget = fiscal_record(
        candidate, "jp-local-192015-fiscal-2026-total-expenditure"
    )
    assert budget["fiscal_year"] == 2026
    assert budget["stage"] == "initial_budget"
    assert budget["amount_yen"] == 91787060000
    assert "議案第5号" in budget["note"]
    assert "令和8年3月25日" in budget["note"]

    # The FY2024 settlement totals are published at yen precision in
    # the audit commissioners' settlement-review opinion (甲監発第24号).
    # Their difference must equal the published balance
    # (歳入歳出差引額) of 1,605,557,300 yen.
    revenue = fiscal_record(candidate, "jp-local-192015-fiscal-2024-total-revenue")
    expenditure = fiscal_record(
        candidate, "jp-local-192015-fiscal-2024-total-expenditure"
    )
    for settlement in (revenue, expenditure):
        assert settlement["fiscal_year"] == 2024
        assert settlement["stage"] == "settlement"
    assert revenue["amount_yen"] == 91644865806
    assert expenditure["amount_yen"] == 90039308506
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 1605557300
    assert "議案第95号" in revenue["note"]
    assert "認定" in revenue["note"]
    assert "令和7年10月2日" in revenue["note"]

    assert len(package["evidence_packets"]) == 3
    for packet in package["evidence_packets"]:
        assert packet["review_status"] == "needs_review"
        assert all(
            claim["decision"] == "needs_review" for claim in packet["claims"]
        )
        assert all("未確認" not in claim["statement"] for claim in packet["claims"])
        assert packet["open_questions"]

    budget_packet = evidence_packet(
        candidate, "evidence-kofu-city-2026-total-expenditure"
    )
    assert "議案第5号" in budget_packet["claims"][0]["statement"]
    assert "91,787,060千円" in budget_packet["claims"][0]["statement"]

    revenue_packet = evidence_packet(
        candidate, "evidence-kofu-city-2024-total-revenue"
    )
    assert "91,644,865,806円" in revenue_packet["claims"][0]["statement"]
    assert "議案第95号" in revenue_packet["claims"][0]["statement"]
    assert "令和7年10月2日" in revenue_packet["claims"][0]["statement"]


def test_kofu_plan_framework_is_primary_source_checked() -> None:
    candidate = load_json(CANDIDATE_PATH)
    plan = candidate["candidate_package"]["policy_structure"]["current_plan"]

    assert plan["title"] == "第七次甲府市総合計画"
    assert plan["start_fiscal_year"] == 2026
    assert plan["end_fiscal_year"] == 2035
    assert plan["vision"] == "幸せ実感 希望ある未来を創り続けるまち 甲府"
    assert [goal["name_ja"] for goal in plan["basic_goals"]] == [
        "未来に輝く『ひと』を育む",
        "安全・安心で快適な『まち』を創る",
        "都市機能と自然が調和する甲府の『魅力』を磨く",
    ]
    assert [len(goal["measures"]) for goal in plan["basic_goals"]] == [6, 6, 6]

    period = plan_record(candidate, "kofu-current-plan-period")
    assert period["decision"] == "needs_review"
    assert period["value"] == "2026年度～2035年度"
    assert "議案第109号" in period["statement"]

    structure = plan_record(candidate, "kofu-current-policy-structure")
    assert structure["decision"] == "needs_review"
    assert "18施策" in structure["statement"]

    governance = plan_record(candidate, "kofu-progress-governance-framework")
    assert governance["decision"] == "needs_review"
    assert "ローリング方式" in governance["statement"]

    transition = plan_record(candidate, "kofu-sixth-plan-transition")
    assert transition["evidence_role"] == "plan_transition"
    assert transition["decision"] == "needs_review"

    linkage = plan_record(candidate, "kofu-fy2024-settlement-linkage")
    assert linkage["decision"] == "not_assessable"
    assert linkage["fiscal_year"] == 2024


def test_kofu_promotion_is_reflected_in_canonical_queue() -> None:
    queue = load_json(QUEUE_PATH)
    summary = queue["summary"]
    assert summary["reviewed_complete_count"] == 40
    assert summary["pending_record_review_count"] == 27
    assert summary["next_official_code"] == "272159"

    kofu = next(
        record
        for record in queue["execution_queue"]
        if record["official_code"] == "192015"
    )
    assert kofu["status"] == "reviewed_complete"
    assert kofu["completion_path"] == "data/catalog/kofu_phase15_completion.json"


def test_web_runtime_does_not_import_kofu_candidate_data() -> None:
    forbidden = ("data/candidates", "kofu-city/review_candidate")
    for path in WEB_ROOT.rglob("*"):
        if path.is_file() and path.suffix in {".ts", ".tsx", ".js", ".mjs"}:
            text = path.read_text(encoding="utf-8")
            assert all(token not in text for token in forbidden), path
