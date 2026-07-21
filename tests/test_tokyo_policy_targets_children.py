import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "data/entities/policy/tokyo_policy_target_catalog_children.json"
EVIDENCE_PATH = ROOT / "data/entities/policy/tokyo_policy_target_children_evidence_packets.json"
MANIFEST_PATH = ROOT / "data/catalog/tokyo_policy_target_review_manifest.json"
INDEX_PATH = ROOT / "data/catalog/tokyo_policy_target_source_index.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(schema_name: str, instance):
    schema = load(ROOT / "schemas" / schema_name)
    errors = sorted(
        Draft202012Validator(
            schema,
            format_checker=FormatChecker(),
        ).iter_errors(instance),
        key=lambda error: list(error.path),
    )
    assert not errors, [error.message for error in errors]


def test_tokyo_children_catalog_and_manifest_are_schema_valid():
    catalog = load(CATALOG_PATH)
    manifest = load(MANIFEST_PATH)
    index = load(INDEX_PATH)
    validate("tokyo_policy_target_catalog.schema.json", catalog)
    validate("tokyo_policy_target_review_manifest.schema.json", manifest)
    validate("tokyo_policy_target_source_index.schema.json", index)


def test_tokyo_children_review_has_contiguous_groups_and_series():
    catalog = load(CATALOG_PATH)
    items = catalog["items"]
    assert [item["target_group_number"] for item in items] == list(range(1, 9))
    assert sum(len(item["series"]) for item in items) == 9
    assert all(item["review_status"] == "reviewed" for item in items)
    assert all(item["actual_linkage_status"] == "not_linked" for item in items)
    assert all(item["evaluation_status"] == "not_assessed" for item in items)


def test_tokyo_children_evidence_covers_every_reviewed_group():
    catalog = load(CATALOG_PATH)
    evidence = load(EVIDENCE_PATH)
    expected_subjects = {item["id"] for item in catalog["items"]}
    actual_subjects = {packet["subject_id"] for packet in evidence}
    assert actual_subjects == expected_subjects
    assert len(evidence) == 8
    assert all(packet["review_status"] == "reviewed" for packet in evidence)
    assert all(packet["claims"] for packet in evidence)
    assert all(
        claim["source_ids"] == ["tokyo-policy-targets-2026"]
        for packet in evidence
        for claim in packet["claims"]
    )


def test_tokyo_children_preserves_semantic_boundaries():
    items = {item["target_group_number"]: item for item in load(CATALOG_PATH)["items"]}

    action_target = items[2]
    assert action_target["population_scope_original"] == "17歳"
    assert action_target["series"][0]["values"][-1]["operator"] == "minimum"

    qualitative = items[4]["series"][0]
    assert qualitative["unit_original"] == "実施状態"
    assert {value["status"] for value in qualitative["values"]} == {"qualitative"}

    child_support = items[6]
    assert len(child_support["series"]) == 2
    assert {series["label"] for series in child_support["series"]} == {
        "養育費の取り決めをしている場合の受領率",
        "養育費の取り決めの有無に関わらない受領率",
    }

    municipality_targets = [items[7], items[8]]
    assert all(
        item["population_scope_original"] == "東京都内62区市町村"
        for item in municipality_targets
    )
    assert all(
        item["series"][0]["values"][-1]["operator"] == "maintain"
        for item in municipality_targets
    )


def test_tokyo_source_index_and_manifest_counts_match_catalog():
    catalog = load(CATALOG_PATH)
    manifest = load(MANIFEST_PATH)
    index = load(INDEX_PATH)
    reviewed_groups = len(catalog["items"])
    reviewed_series = sum(len(item["series"]) for item in catalog["items"])

    assert index["page_count"] == 60
    assert index["indexed_page_count"] == 60
    assert [page["page_number"] for page in index["pages"]] == list(range(1, 61))
    reviewed_pages = [
        page["page_number"]
        for page in index["pages"]
        if page["review_status"] == "reviewed"
    ]
    assert reviewed_pages == [1, 2]
    assert manifest["reviewed_target_group_count"] == reviewed_groups == 8
    assert manifest["reviewed_indicator_series_count"] == reviewed_series == 9
    assert manifest["evidence_packet_count"] == 8
    assert manifest["reviewed_page_count"] + manifest["remaining_page_count"] == 60
    assert manifest["actual_linked_indicator_series_count"] == 0
    assert manifest["evaluation_assessed_target_group_count"] == 0
