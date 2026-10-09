from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "data/candidates/morioka-city/review_candidate.json"
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


def test_morioka_candidate_staging_contract_validates():
    candidate = load(CANDIDATE)

    assert validate(CANDIDATE_SCHEMA, candidate) == []
    assert candidate["candidate_id"] == "morioka-phase15-review-candidate"
    assert candidate["phase"] == 15
    assert candidate["official_code"] == "032018"
    assert candidate["name_ja"] == "盛岡市"
    assert candidate["status"] == "review_candidate"
    assert (
        candidate["source_inventory_path"]
        == "data/indexed/morioka-city/source_inventory.json"
    )
    assert candidate["package_state"] == "prepared"
    assert candidate["human_review"]["required"] is True
    assert candidate["human_review"]["status"] == "pending"
    assert candidate["human_review"]["reviewed_at"] is None
    assert candidate["human_review"]["reviewer_note"] is None
    assert candidate["publication"]["eligible"] is False


def test_morioka_candidate_does_not_promote_queue_state():
    queue = load(QUEUE)
    row = next(
        item for item in queue["execution_queue"]
        if item["official_code"] == "032018"
    )

    assert row["status"] == "review_in_progress"
    assert not row.get("completion_path")


def test_candidate_staging_is_not_referenced_by_public_web_source():
    forbidden = "data/candidates"
    hits: list[str] = []

    for path in WEB_ROOT.rglob("*"):
        if not path.is_file() or path.suffix not in {".ts", ".tsx", ".js", ".mjs"}:
            continue
        if forbidden in path.read_text(encoding="utf-8"):
            hits.append(str(path.relative_to(ROOT)))

    assert hits == []


def test_prepared_candidate_retains_human_boundary_and_evidence_shape():
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
    assert source_catalog["id"] == "morioka-phase15-sources"
    assert source_catalog["phase"] == 15
    assert source_catalog["official_code"] == "032018"
    assert source_catalog["name_ja"] == "盛岡市"
    assert len(source_catalog["sources"]) == 5
    source_ids = {s["id"] for s in source_catalog["sources"]}
    assert source_ids == {
        "morioka-current-plan",
        "morioka-implementation-2026-2028",
        "morioka-budget-2026",
        "morioka-budget-book-2026",
        "morioka-settlement-2024",
    }
    assert all(
        source["official_url"].startswith("https://")
        for source in source_catalog["sources"]
    )
    assert all(source["format"] == "html" for source in source_catalog["sources"])
    assert all(source["evidence_location"] for source in source_catalog["sources"])
    assert all(source["use_boundary"] for source in source_catalog["sources"])

    # Plan Review assertions
    assert plan_review["id"] == "phase15-morioka-plan-review"
    assert plan_review["official_code"] == "032018"
    assert plan_review["name_ja"] == "盛岡市"
    assert plan_review["review_status"] == "review_in_progress"
    assert len(plan_review["records"]) == 4
    record_ids = {r["id"] for r in plan_review["records"]}
    assert record_ids == {
        "morioka-current-plan-period",
        "morioka-current-policy-structure",
        "morioka-implementation-rolling-structure",
        "morioka-fy2024-settlement-linkage",
    }
    assert all(
        record["decision"] in {"needs_review", "not_assessable"}
        for record in plan_review["records"]
    )

    # Policy Structure assertions
    assert policy_structure["id"] == "morioka-current-policy-structure"
    assert policy_structure["phase"] == 15
    assert policy_structure["official_code"] == "032018"
    assert policy_structure["name_ja"] == "盛岡市"
    current_plan = policy_structure["current_plan"]
    assert current_plan["title"] == "盛岡市総合計画基本構想"
    assert current_plan["start_fiscal_year"] == 2025
    assert current_plan["end_fiscal_year"] == 2034
    assert current_plan["vision"] == "輝きが増し 活力に満ち 夢をかなえるまち盛岡"
    assert len(current_plan["basic_goals"]) == 4
    goal_names = [goal["name_ja"] for goal in current_plan["basic_goals"]]
    assert goal_names == [
        "豊かな地域資源が活力を生み出すまちづくり",
        "人を育み未来を選べるまちづくり",
        "人がいきいきとつながり支え合うまちづくり",
        "安全・安心で快適に暮らせるまちづくり",
    ]
    total_measures = sum(
        len(goal["measures"]) for goal in current_plan["basic_goals"]
    )
    assert total_measures == 25
    assert len(current_plan["management_principles"]) == 5

    # Progress Review assertions
    assert progress_review["id"] == "morioka-current-progress-review-summary"
    assert progress_review["phase"] == 15
    assert progress_review["official_code"] == "032018"
    assert progress_review["name_ja"] == "盛岡市"
    assert progress_review["review_status"] == "review_candidate_staging"
    framework = progress_review["implementation_plan_framework"]
    assert framework["title"] == "盛岡市総合計画実施計画（令和7年度から16年度）"
    assert framework["period"] == "2026年度～2028年度（毎年度ローリング）"
    assert framework["evaluation_structure"]

    # Fiscal Records & Evidence Packets assertions
    assert len(fiscal_records) == 3
    assert all(record["municipality_id"] == "jp-local-032018" for record in fiscal_records)
    assert all(record["account_type"] == "general" for record in fiscal_records)
    assert all(record["value_status"] == "available" for record in fiscal_records)
    assert all(record["review_status"] == "needs_review" for record in fiscal_records)
    assert all(record["confidence"] == "medium" for record in fiscal_records)
    assert {record["fiscal_year"] for record in fiscal_records} == {2024, 2026}
    assert {record["stage"] for record in fiscal_records} == {
        "initial_budget",
        "settlement",
    }
    assert {record["metric"] for record in fiscal_records} == {
        "total_expenditure",
        "total_revenue",
    }

    assert len(evidence_packets) == 3
    fiscal_ids = {record["id"] for record in fiscal_records}
    assert {packet["subject_id"] for packet in evidence_packets} == fiscal_ids
    assert all(packet["subject_type"] == "fiscal_record" for packet in evidence_packets)
    assert all(packet["review_status"] == "needs_review" for packet in evidence_packets)
    assert all(packet["claims"] for packet in evidence_packets)
    assert all(
        claim["decision"] == "needs_review"
        for packet in evidence_packets
        for claim in packet["claims"]
    )

    # Quality Boundaries & Deferred Depth assertions
    assert len(candidate["quality_boundaries"]) >= 4
    assert any(
        "human-review" in boundary.lower() or "person checks" in boundary.lower()
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
