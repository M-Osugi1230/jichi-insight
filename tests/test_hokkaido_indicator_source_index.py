import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "data/catalog/hokkaido_indicator_source_index.json"
SCHEMA_PATH = ROOT / "schemas/hokkaido_indicator_source_index.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_hokkaido_indicator_source_index_matches_schema():
    index = load(INDEX_PATH)
    schema = load(SCHEMA_PATH)
    validator = Draft202012Validator(
        schema,
        format_checker=FormatChecker(),
    )
    assert list(validator.iter_errors(index)) == []


def test_index_covers_all_eighteen_policy_fields_in_official_order():
    index = load(INDEX_PATH)
    hierarchy = load(ROOT / "data/entities/policy/hokkaido_policy_hierarchy.json")
    official_fields = [
        field
        for direction in hierarchy["directions"]
        for field in direction["fields"]
    ]

    assert index["source_document_count"] == 18
    assert len(index["documents"]) == 18
    assert [document["display_order"] for document in index["documents"]] == list(
        range(1, 19)
    )
    assert [document["policy_field_id"] for document in index["documents"]] == [
        field["id"] for field in official_fields
    ]
    assert len({document["source_id"] for document in index["documents"]}) == 18


def test_pdf_page_counts_and_indicator_ranges_preserve_all_boundaries():
    index = load(INDEX_PATH)

    assert sum(document["page_count"] for document in index["documents"]) == 108
    assert sum(document["indicator_count"] for document in index["documents"]) == 108
    assert index["total_pdf_pages"] == 108
    assert index["expected_unique_indicator_count"] == 108
    assert index["duplicate_inclusive_indicator_count"] == 113
    assert "混同しない" in index["counting_boundary"]
    assert index["document_index_status"] == "completed"
    assert index["indicator_position_status"] == "completed"
    assert index["relationship_status"] == "completed"


def test_indicator_ranges_form_one_complete_non_overlapping_sequence():
    index = load(INDEX_PATH)
    numbers = [
        number
        for document in index["documents"]
        for number in range(
            document["first_indicator_number"],
            document["last_indicator_number"] + 1,
        )
    ]

    assert numbers == list(range(1, 109))
    assert all(
        document["indicator_count"]
        == document["last_indicator_number"]
        - document["first_indicator_number"]
        + 1
        for document in index["documents"]
    )
    assert all(
        document["page_count"] == document["indicator_count"]
        for document in index["documents"]
    )
    assert all(
        document["indicator_position_status"] == "indexed"
        for document in index["documents"]
    )


def test_indexed_documents_match_central_policy_source_records():
    index = load(INDEX_PATH)
    catalog = load(ROOT / "data/catalog/policy_sources.json")
    sources_by_id = {source["id"]: source for source in catalog["records"]}

    for document in index["documents"]:
        source = sources_by_id[document["source_id"]]
        assert source["municipality_key"] == "hokkaido-prefecture"
        assert source["source_role"] == "kpi_source"
        assert source["format"] == "pdf"
        assert source["collection_status"] == "indexed"
        assert source["review_status"] == "verified"
        assert source["extraction_targets"] == ["kpis"]
        assert f"{document['page_count']}ページ" in source["notes"]


def test_indicator_relationships_are_completed_in_a_separate_reference_index():
    index = load(INDEX_PATH)
    relationships = load(
        ROOT / "data/catalog/hokkaido_indicator_relationship_index.json"
    )

    assert index["indicator_position_status"] == "completed"
    assert index["relationship_status"] == "completed"
    assert relationships["relationship_status"] == "completed"
    assert relationships["expected_extra_relationship_count"] == 5
    assert "relationships" not in index
    assert "repeated_indicators" not in index
