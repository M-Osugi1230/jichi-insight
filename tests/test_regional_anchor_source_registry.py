import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "data/catalog/regional_anchor_source_registry.json"
SCHEMA_PATH = ROOT / "schemas/regional_anchor_source_registry.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_regional_anchor_source_registry_matches_schema():
    validator = Draft202012Validator(
        load(SCHEMA_PATH),
        format_checker=FormatChecker(),
    )
    assert list(validator.iter_errors(load(REGISTRY_PATH))) == []


def test_exact_nine_regional_anchors_are_registered_once():
    registry = load(REGISTRY_PATH)
    expected = ["01", "04", "13", "23", "27", "34", "37", "40", "47"]
    records = registry["records"]

    assert registry["anchor_codes"] == expected
    assert [record["prefecture_code"] for record in records] == expected
    assert len({record["prefecture_code"] for record in records}) == 9


def test_six_new_anchors_have_all_source_categories_without_review_promotion():
    registry = load(REGISTRY_PATH)
    categories = set(registry["source_categories"])
    new_anchor_codes = {"13", "23", "27", "34", "37", "47"}
    by_code = {record["prefecture_code"]: record for record in registry["records"]}

    for code in new_anchor_codes:
        record = by_code[code]
        assert record["anchor_status"] == "source_indexed"
        assert record["numeric_target_status"] == "indexed"
        assert record["evidence_paths"] == []
        assert {source["category"] for source in record["sources"]} == categories
        assert len(record["sources"]) == 6
        assert all(source["status"] == "indexed" for source in record["sources"])
        assert all(source["url"].startswith("https://") for source in record["sources"])
        assert len({source["id"] for source in record["sources"]}) == 6


def test_reviewed_anchor_references_point_to_repository_evidence():
    records = {
        record["prefecture_code"]: record for record in load(REGISTRY_PATH)["records"]
    }
    reviewed_codes = {"01", "04", "40"}

    for code in reviewed_codes:
        record = records[code]
        assert record["numeric_target_status"] == "reviewed"
        assert record["evidence_paths"]
        assert all((ROOT / path).is_file() for path in record["evidence_paths"])


def test_source_roles_preserve_known_structural_boundaries():
    records = {
        record["prefecture_code"]: record for record in load(REGISTRY_PATH)["records"]
    }

    osaka_notes = " ".join(source["note"] for source in records["27"]["sources"])
    assert "単一総合実施計画がない" in osaka_notes
    assert "履歴管理対象" in osaka_notes

    okinawa_sources = {source["category"]: source for source in records["47"]["sources"]}
    assert "令和7～9年度" in okinawa_sources["implementation_plan"]["title"]
    assert "個別事業評価と混同しない" in okinawa_sources["project_evaluation"]["note"]

    assert all(
        "達成率" not in source["note"]
        for record in records.values()
        for source in record["sources"]
    )
