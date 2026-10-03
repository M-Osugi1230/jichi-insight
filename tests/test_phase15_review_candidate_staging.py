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
    assert candidate["official_code"] == "032018"
    assert candidate["name_ja"] == "盛岡市"
    assert candidate["status"] == "review_candidate"
    assert candidate["human_review"]["required"] is True
    assert candidate["human_review"]["status"] == "pending"
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
    if candidate["package_state"] != "prepared":
        return

    package = candidate["candidate_package"]
    source_catalog = package["source_catalog"]
    plan_review = package["plan_review"]

    assert source_catalog["official_code"] == "032018"
    assert source_catalog["name_ja"] == "盛岡市"
    assert len(source_catalog["sources"]) >= 4
    assert all(
        source["official_url"].startswith("https://")
        for source in source_catalog["sources"]
    )
    assert all(source["evidence_location"] for source in source_catalog["sources"])
    assert all(source["use_boundary"] for source in source_catalog["sources"])

    assert plan_review["official_code"] == "032018"
    assert plan_review["name_ja"] == "盛岡市"
    assert plan_review["review_status"] == "review_in_progress"
    assert len(plan_review["records"]) >= 3
    assert all(
        record["decision"] in {"needs_review", "not_assessable"}
        for record in plan_review["records"]
    )

    assert candidate["human_review"]["status"] == "pending"
    assert candidate["publication"]["eligible"] is False
