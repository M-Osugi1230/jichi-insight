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


def test_kofu_candidate_validates_and_stays_unreviewed() -> None:
    candidate = load_json(CANDIDATE_PATH)
    schema = load_json(SCHEMA_PATH)

    jsonschema.Draft202012Validator(schema).validate(candidate)

    assert candidate["candidate_id"] == "kofu-phase15-review-candidate"
    assert candidate["official_code"] == "192015"
    assert candidate["name_ja"] == "甲府市"
    assert candidate["status"] == "review_candidate"
    assert candidate["package_state"] == "prepared"
    assert candidate["publication"]["eligible"] is False
    assert candidate["human_review"]["status"] == "pending"
    assert candidate["human_review"]["required"] is True
    assert candidate["human_review"]["reviewed_at"] is None
    assert candidate["human_review"]["reviewer_note"] is None
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
    assert by_id["kofu-seventh-plan"]["verification_status"] == (
        "primary_source_live_verified_2026-11-16"
    )
    for unverified_id in (
        "kofu-first-implementation-design",
        "kofu-budget-2026",
        "kofu-settlement-2024",
    ):
        assert by_id[unverified_id]["verification_status"] == (
            "official_landing_not_live_verified_2026-11-16"
        )


def test_kofu_fiscal_amounts_remain_unconfirmed_not_assessable() -> None:
    candidate = load_json(CANDIDATE_PATH)
    package = candidate["candidate_package"]

    assert len(package["fiscal_records"]) == 3
    for record in package["fiscal_records"]:
        assert record["amount_yen"] is None
        assert record["value"] is None
        assert record["value_status"] == "not_found"
        assert record["confidence"] == "not_assessable"
        assert record["review_status"] == "needs_review"

    budget = fiscal_record(
        candidate, "jp-local-192015-fiscal-2026-total-expenditure"
    )
    assert budget["fiscal_year"] == 2026
    assert budget["stage"] == "initial_budget"
    assert "二次情報" in budget["note"]

    revenue = fiscal_record(candidate, "jp-local-192015-fiscal-2024-total-revenue")
    expenditure = fiscal_record(
        candidate, "jp-local-192015-fiscal-2024-total-expenditure"
    )
    for settlement in (revenue, expenditure):
        assert settlement["fiscal_year"] == 2024
        assert settlement["stage"] == "settlement"
    assert "議案第95号" in revenue["note"]
    assert "認定" in revenue["note"]

    assert len(package["evidence_packets"]) == 3
    for packet in package["evidence_packets"]:
        assert packet["review_status"] == "needs_review"
        assert all(
            claim["decision"] == "needs_review" for claim in packet["claims"]
        )
        assert all("未確認" in claim["statement"] for claim in packet["claims"])
        assert packet["open_questions"]


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


def test_kofu_is_still_pending_in_canonical_queue() -> None:
    queue = load_json(QUEUE_PATH)
    summary = queue["summary"]
    assert summary["reviewed_complete_count"] == 25
    assert summary["pending_record_review_count"] == 42
    assert summary["next_official_code"] == "192015"

    kofu = next(
        record
        for record in queue["execution_queue"]
        if record["official_code"] == "192015"
    )
    assert kofu["status"] == "pending_record_review"
    assert kofu["completion_path"] is None


def test_web_runtime_does_not_import_kofu_candidate_data() -> None:
    forbidden = ("data/candidates", "kofu-city/review_candidate")
    for path in WEB_ROOT.rglob("*"):
        if path.is_file() and path.suffix in {".ts", ".tsx", ".js", ".mjs"}:
            text = path.read_text(encoding="utf-8")
            assert all(token not in text for token in forbidden), path
