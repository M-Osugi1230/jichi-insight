import json
from collections import defaultdict
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
PAGE_INDEX_PATH = ROOT / "data/catalog/hokkaido_indicator_page_index.json"
PAGE_SCHEMA_PATH = ROOT / "schemas/hokkaido_indicator_page_index.schema.json"
SOURCE_INDEX_PATH = ROOT / "data/catalog/hokkaido_indicator_source_index.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_hokkaido_indicator_page_index_matches_schema():
    page_index = load(PAGE_INDEX_PATH)
    schema = load(PAGE_SCHEMA_PATH)
    validator = Draft202012Validator(
        schema,
        format_checker=FormatChecker(),
    )
    assert list(validator.iter_errors(page_index)) == []


def test_page_index_contains_exact_indicator_sequence_one_to_108():
    page_index = load(PAGE_INDEX_PATH)
    records = page_index["records"]

    assert len(records) == 108
    assert [record["indicator_number"] for record in records] == list(range(1, 109))
    assert len({record["indicator_number"] for record in records}) == 108
    assert len(
        {(record["source_id"], record["page_number"]) for record in records}
    ) == 108
    assert all(record["position_status"] == "verified" for record in records)


def test_each_document_has_every_page_once_and_matches_source_ranges():
    page_index = load(PAGE_INDEX_PATH)
    source_index = load(SOURCE_INDEX_PATH)
    records_by_source = defaultdict(list)
    for record in page_index["records"]:
        records_by_source[record["source_id"]].append(record)

    assert set(records_by_source) == {
        document["source_id"] for document in source_index["documents"]
    }

    for document in source_index["documents"]:
        records = records_by_source[document["source_id"]]
        assert [record["page_number"] for record in records] == list(
            range(1, document["page_count"] + 1)
        )
        assert [record["indicator_number"] for record in records] == list(
            range(
                document["first_indicator_number"],
                document["last_indicator_number"] + 1,
            )
        )
        assert {record["policy_field_id"] for record in records} == {
            document["policy_field_id"]
        }


def test_number_sequence_is_complete_but_relationship_review_remains_active():
    page_index = load(PAGE_INDEX_PATH)

    assert page_index["sequence_status"] == "complete"
    assert page_index["relationship_status"] == "active"
    assert all(
        record["relationship_status"] == "pending_review"
        for record in page_index["records"]
    )
    assert "indicator_name" not in page_index["records"][0]
    assert "baseline" not in page_index["records"][0]
    assert "target" not in page_index["records"][0]


def test_page_index_sources_and_policy_fields_exist():
    page_index = load(PAGE_INDEX_PATH)
    catalog = load(ROOT / "data/catalog/policy_sources.json")
    hierarchy = load(ROOT / "data/entities/policy/hokkaido_policy_hierarchy.json")
    source_ids = {source["id"] for source in catalog["records"]}
    policy_field_ids = {
        field["id"]
        for direction in hierarchy["directions"]
        for field in direction["fields"]
    }

    assert {record["source_id"] for record in page_index["records"]} <= source_ids
    assert {
        record["policy_field_id"] for record in page_index["records"]
    } <= policy_field_ids
