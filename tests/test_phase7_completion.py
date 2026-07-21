import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
COMPLETION_PATH = ROOT / "data/catalog/phase7_completion.json"
COMPLETION_SCHEMA_PATH = ROOT / "schemas/phase7_completion.schema.json"
COVERAGE_PATH = ROOT / "data/catalog/prefecture_coverage.json"
INVENTORY_PATH = ROOT / "data/catalog/nationwide_source_inventory.json"
PUBLISHED_PATH = ROOT / "data/catalog/published_prefecture_pages.json"
PUBLISHED_SCHEMA_PATH = ROOT / "schemas/published_prefecture_pages.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_phase7_completion_manifest_matches_schema():
    manifest = load(COMPLETION_PATH)
    validator = Draft202012Validator(
        load(COMPLETION_SCHEMA_PATH),
        format_checker=FormatChecker(),
    )
    assert list(validator.iter_errors(manifest)) == []


def test_published_prefecture_page_registry_matches_schema():
    registry = load(PUBLISHED_PATH)
    validator = Draft202012Validator(
        load(PUBLISHED_SCHEMA_PATH),
        format_checker=FormatChecker(),
    )
    assert list(validator.iter_errors(registry)) == []


def test_phase7_counts_are_derived_from_canonical_registries():
    manifest = load(COMPLETION_PATH)
    coverage = load(COVERAGE_PATH)
    inventory = load(INVENTORY_PATH)
    published = load(PUBLISHED_PATH)

    expected = {
        "registered_prefectures": len(coverage["records"]),
        "verified_official_entries": len(coverage["verified_official_codes"]),
        "indexed_policy_plan_entries": len(coverage["plan_entry_indexed_codes"]),
        "current_policy_plan_entries": len(coverage["current_plan_confirmed_codes"]),
        "source_inventory_records": len(inventory["records"]),
        "published_prefecture_pages": len(published["records"]),
    }
    assert manifest["counts"] == expected
    assert expected == {
        "registered_prefectures": 47,
        "verified_official_entries": 47,
        "indexed_policy_plan_entries": 47,
        "current_policy_plan_entries": 47,
        "source_inventory_records": 47,
        "published_prefecture_pages": 6,
    }


def test_published_pages_are_unique_and_reference_registered_prefectures():
    coverage_codes = {
        record["prefecture_code"] for record in load(COVERAGE_PATH)["records"]
    }
    records = load(PUBLISHED_PATH)["records"]
    codes = [record["prefecture_code"] for record in records]
    routes = [record["route"] for record in records]

    assert codes == ["01", "04", "13", "23", "27", "40"]
    assert len(codes) == len(set(codes))
    assert len(routes) == len(set(routes))
    assert set(codes) <= coverage_codes
    assert all(record["publication_status"] == "published" for record in records)


def test_every_prefecture_tracks_all_phase7_source_categories():
    inventory = load(INVENTORY_PATH)
    required_categories = {
        "policy_plan",
        "implementation_plan",
        "kpi_source",
        "annual_evaluation",
        "budget",
        "project_evaluation",
    }

    assert set(inventory["categories"]) == required_categories
    assert len(inventory["records"]) == 47
    assert all(
        set(record["sources"]) == required_categories
        for record in inventory["records"]
    )


def test_phase7_gate_evidence_paths_exist_and_gate_ids_are_unique():
    manifest = load(COMPLETION_PATH)
    gate_ids = [gate["id"] for gate in manifest["gates"]]

    assert len(gate_ids) == len(set(gate_ids)) == 8
    for gate in manifest["gates"]:
        for relative_path in gate["evidence_paths"]:
            assert (ROOT / relative_path).exists(), relative_path


def test_phase7_status_cannot_overstate_production_verification():
    manifest = load(COMPLETION_PATH)
    gates = {gate["id"]: gate["status"] for gate in manifest["gates"]}

    if manifest["status"] == "complete":
        assert manifest["completed_at"] is not None
        assert set(gates.values()) == {"passed"}
    else:
        assert manifest["status"] == "verification_pending"
        assert manifest["completed_at"] is None
        assert gates["production_smoke"] == "pending"
        assert all(
            status == "passed"
            for gate_id, status in gates.items()
            if gate_id != "production_smoke"
        )
