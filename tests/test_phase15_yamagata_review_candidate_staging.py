from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "data/candidates/yamagata-city/review_candidate.json"
CANDIDATE_SCHEMA = ROOT / "schemas/phase15_review_candidate.schema.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"
WEB_ROOT = ROOT / "apps/web"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(schema_path: Path, instance):
    validator = Draft202012Validator(
        load(schema_path), format_checker=FormatChecker()
    )
    return list(validator.iter_errors(instance))


def test_yamagata_candidate_staging_contract_validates():
    candidate = load(CANDIDATE)

    assert validate(CANDIDATE_SCHEMA, candidate) == []
    assert candidate["candidate_id"] == "yamagata-phase15-review-candidate"
    assert candidate["phase"] == 15
    assert candidate["official_code"] == "062014"
    assert candidate["name_ja"] == "山形市"
    assert (
        candidate["source_inventory_path"]
        == "data/indexed/yamagata-city/source_inventory.json"
    )
    assert (ROOT / candidate["source_inventory_path"]).is_file()
    assert candidate["status"] == "review_candidate"
    assert candidate["package_state"] == "prepared"
    assert candidate["human_review"]["required"] is True
    assert candidate["human_review"]["status"] == "pending"
    assert candidate["human_review"]["reviewed_at"] is None
    assert candidate["human_review"]["reviewer_note"] is None
    assert candidate["publication"]["eligible"] is False


def test_yamagata_candidate_does_not_promote_queue_state():
    queue = load(QUEUE)
    yamagata_row = next(
        item for item in queue["execution_queue"]
        if item["official_code"] == "062014"
    )

    assert yamagata_row["status"] == "pending_record_review"
    assert not yamagata_row.get("completion_path")


def test_candidate_staging_is_not_referenced_by_public_web_source():
    forbidden = "data/candidates"
    hits: list[str] = []

    for path in WEB_ROOT.rglob("*"):
        if not path.is_file() or path.suffix not in {".ts", ".tsx", ".js", ".mjs"}:
            continue
        if forbidden in path.read_text(encoding="utf-8"):
            hits.append(str(path.relative_to(ROOT)))

    assert hits == []


def test_prepared_yamagata_candidate_retains_human_boundary_and_evidence_shape():
    candidate = load(CANDIDATE)
    assert candidate["package_state"] == "prepared"

    package = candidate["candidate_package"]
    source_catalog = package["source_catalog"]
    plan_review = package["plan_review"]
    policy_structure = package["policy_structure"]
    progress_review = package["progress_review"]
    fiscal_records = package["fiscal_records"]
    evidence_packets = package["evidence_packets"]

    # Source Catalog assertions
    assert source_catalog["id"] == "yamagata-phase15-sources"
    assert source_catalog["phase"] == 15
    assert source_catalog["official_code"] == "062014"
    assert source_catalog["name_ja"] == "山形市"
    assert len(source_catalog["sources"]) == 5
    source_ids = {s["id"] for s in source_catalog["sources"]}
    assert source_ids == {
        "yamagata-development-plan-2030",
        "yamagata-progress-indicators",
        "yamagata-budget-2026",
        "yamagata-budget-book-2026",
        "yamagata-settlement-2024",
    }
    assert all(
        source["official_url"].startswith("https://www.city.yamagata-yamagata.lg.jp/")
        for source in source_catalog["sources"]
    )
    assert all(source["format"] == "html" for source in source_catalog["sources"])
    assert all(bool(source["evidence_location"]) for source in source_catalog["sources"])
    assert all(bool(source["use_boundary"]) for source in source_catalog["sources"])

    # Plan Review assertions
    assert plan_review["id"] == "phase15-yamagata-plan-review"
    assert plan_review["official_code"] == "062014"
    assert plan_review["name_ja"] == "山形市"
    assert plan_review["review_status"] == "review_in_progress"
    assert len(plan_review["records"]) == 4
    record_ids = {r["id"] for r in plan_review["records"]}
    assert record_ids == {
        "yamagata-current-plan-period",
        "yamagata-current-policy-structure",
        "yamagata-progress-indicator-structure",
        "yamagata-fy2024-settlement-linkage",
    }
    assert all(
        record["decision"] in {"needs_review", "not_assessable"}
        for record in plan_review["records"]
    )
    assert all(
        bool(record["evidence_location"])
        for record in plan_review["records"]
        if "evidence_location" in record
    )
    assert all(
        record["source_url"].startswith("https://www.city.yamagata-yamagata.lg.jp/")
        for record in plan_review["records"]
    )

    # Policy Structure assertions
    assert policy_structure["id"] == "yamagata-current-policy-structure"
    assert policy_structure["phase"] == 15
    assert policy_structure["official_code"] == "062014"
    assert policy_structure["name_ja"] == "山形市"
    current_plan = policy_structure["current_plan"]
    assert current_plan["title"] == "山形市発展計画2030"
    assert current_plan["start_fiscal_year"] == 2025
    assert current_plan["end_fiscal_year"] == 2029
    assert current_plan["vision"] == "健康医療先進都市・発展創生都市"
    assert len(current_plan["basic_goals"]) == 4
    goal_names = [goal["name_ja"] for goal in current_plan["basic_goals"]]
    assert goal_names == [
        "健康医療・福祉の充実",
        "教育・文化の振興",
        "産業・経済の活性化",
        "安全・安心と快適な都市基盤",
    ]
    total_measures = sum(
        len(goal["measures"]) for goal in current_plan["basic_goals"]
    )
    assert total_measures == 19
    assert len(current_plan["management_principles"]) == 4
    assert current_plan["management_principles"] == [
        "市民協働・地域力向上",
        "持続可能な財政運営",
        "デジタル化・DXの推進",
        "広域連携の推進",
    ]

    # Progress Review assertions
    assert progress_review["id"] == "yamagata-current-progress-review-summary"
    assert progress_review["phase"] == 15
    assert progress_review["official_code"] == "062014"
    assert progress_review["name_ja"] == "山形市"
    assert progress_review["review_status"] == "review_candidate_staging"
    framework = progress_review["implementation_plan_framework"]
    assert (
        framework["title"]
        == "山形市発展計画2030 成果指標・進行管理枠組み"
    )
    assert framework["period"] == "2025年度～2029年度（毎年度評価・ローリング）"
    assert framework["evaluation_structure"]

    # Fiscal Records & Evidence Packets assertions
    assert len(fiscal_records) == 3
    assert all(
        rec["municipality_id"] == "jp-local-062014" and rec["review_status"] == "needs_review"
        for rec in fiscal_records
    )
    assert all(rec["account_type"] == "general" for rec in fiscal_records)
    assert all(rec["value_status"] == "available" for rec in fiscal_records)
    assert all(rec["confidence"] == "medium" for rec in fiscal_records)
    assert {rec["fiscal_year"] for rec in fiscal_records} == {2024, 2026}
    assert {rec["stage"] for rec in fiscal_records} == {
        "initial_budget",
        "settlement",
    }
    assert {rec["metric"] for rec in fiscal_records} == {
        "total_expenditure",
        "total_revenue",
    }

    assert len(evidence_packets) == 3
    fiscal_ids = {rec["id"] for rec in fiscal_records}
    assert {pkt["subject_id"] for pkt in evidence_packets} == fiscal_ids
    assert all(pkt["subject_type"] == "fiscal_record" for pkt in evidence_packets)
    assert all(pkt["review_status"] == "needs_review" for pkt in evidence_packets)
    assert all(pkt["claims"] for pkt in evidence_packets)
    assert all(
        claim["decision"] == "needs_review" and bool(claim["location_note"])
        for pkt in evidence_packets
        for claim in pkt["claims"]
    )

    # Quality Boundaries & Deferred Depth assertions
    assert len(candidate["quality_boundaries"]) >= 4
    quality_text = " ".join(candidate["quality_boundaries"]).lower()
    assert "score" in quality_text
    assert "causal" in quality_text
    assert "ranking" in quality_text
    assert any(
        "human" in boundary.lower() or "person checks" in boundary.lower()
        for boundary in candidate["quality_boundaries"]
    )
    assert len(candidate["deferred_depth"]) == 3
    deferred_ids = {depth["id"] for depth in candidate["deferred_depth"]}
    assert deferred_ids == {
        "current-plan-granular-kpi-and-project-linkage",
        "budget-amendment-and-settlement-project-linkage",
        "policy-outcome-causal-and-cross-city-comparability",
    }
    assert all(
        depth["status"] == "deferred_not_required_for_candidate_staging"
        for depth in candidate["deferred_depth"]
    )

    # Human Review & Publication boundaries
    assert candidate["human_review"]["required"] is True
    assert candidate["human_review"]["status"] == "pending"
    assert candidate["human_review"]["reviewed_at"] is None
    assert candidate["human_review"]["reviewer_note"] is None
    assert candidate["publication"]["eligible"] is False
