from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"
COMPLETION_SCHEMA = ROOT / "schemas/phase15_municipality_completion.schema.json"
SOURCE_CATALOG_SCHEMA = ROOT / "schemas/phase15_source_catalog.schema.json"
PLAN_REVIEW_SCHEMA = ROOT / "schemas/phase15_plan_review.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(schema_path: Path, instance):
    validator = Draft202012Validator(
        load(schema_path), format_checker=FormatChecker()
    )
    return list(validator.iter_errors(instance))


def test_phase15_all_reviewed_complete_packages_validate_common_contracts():
    queue = load(QUEUE)
    completed = [
        row for row in queue["execution_queue"]
        if row["status"] == "reviewed_complete"
    ]

    assert completed
    for row in completed:
        completion_path = ROOT / row["completion_path"]
        assert completion_path.is_file(), row

        completion = load(completion_path)
        assert validate(COMPLETION_SCHEMA, completion) == []
        assert completion["official_code"] == row["official_code"]
        assert completion["name_ja"] == row["name_ja"]
        assert completion["status"] == "reviewed_complete"

        source_catalog = load(ROOT / completion["review_package"]["source_catalog_path"])
        plan_review = load(ROOT / completion["review_package"]["plan_review_path"])

        assert validate(SOURCE_CATALOG_SCHEMA, source_catalog) == []
        assert validate(PLAN_REVIEW_SCHEMA, plan_review) == []

        assert source_catalog["official_code"] == row["official_code"]
        assert source_catalog["name_ja"] == row["name_ja"]
        assert plan_review["official_code"] == row["official_code"]
        assert plan_review["name_ja"] == row["name_ja"]

        assert all(completion["quality_gate"].values())
        assert completion["deferred_depth"]


def test_phase15_common_review_schemas_are_operational_for_existing_references():
    queue = load(QUEUE)
    completed_names = [
        row["name_ja"]
        for row in queue["execution_queue"]
        if row["status"] == "reviewed_complete"
    ]

    assert completed_names[:3] == ["函館市", "旭川市", "青森市"]
