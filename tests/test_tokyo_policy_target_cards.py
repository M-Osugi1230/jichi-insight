import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "data/reviewed/tokyo_policy_target_cards.json"
EVIDENCE_PATH = ROOT / "data/evidence/tokyo_policy_target_card_evidence.json"
MANIFEST_PATH = ROOT / "data/catalog/tokyo_policy_target_review_manifest.json"
CATALOG_SCHEMA_PATH = ROOT / "schemas/tokyo_policy_target_cards.schema.json"
EVIDENCE_SCHEMA_PATH = ROOT / "schemas/tokyo_policy_target_card_evidence.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(schema_path: Path, instance):
    validator = Draft202012Validator(
        load(schema_path),
        format_checker=FormatChecker(),
    )
    errors = sorted(validator.iter_errors(instance), key=lambda error: list(error.path))
    assert not errors, [error.message for error in errors]


def test_complete_tokyo_target_card_catalog_and_evidence_are_schema_valid():
    validate(CATALOG_SCHEMA_PATH, load(CATALOG_PATH))
    validate(EVIDENCE_SCHEMA_PATH, load(EVIDENCE_PATH))


def test_complete_tokyo_review_covers_every_page_area_and_target_card():
    catalog = load(CATALOG_PATH)
    manifest = load(MANIFEST_PATH)
    items = catalog["items"]
    areas = catalog["policy_areas"]

    assert catalog["source_document_sha256"] == (
        "b49d23d9dae4107f31d79cee762341e5634ae4b9e33779a498a13ff192077b8c"
    )
    assert len(items) == catalog["target_card_count"] == 304
    assert len(areas) == catalog["policy_area_count"] == 25
    assert [item["display_order"] for item in items] == list(range(1, 305))
    assert [item["id"] for item in items] == [
        f"policy-target-tokyo-card-{number:03d}" for number in range(1, 305)
    ]
    assert {item["source_page"] for item in items} == set(range(1, 61))
    assert {item["policy_area_code"] for item in items} == {
        f"{number:02d}" for number in range(1, 26)
    }
    assert sum(area["target_card_count"] for area in areas) == 304

    assert manifest["reviewed_page_count"] == 60
    assert manifest["reviewed_policy_area_count"] == 25
    assert manifest["reviewed_target_card_count"] == 304
    assert manifest["remaining_page_count"] == 0
    assert manifest["status"] == "complete"


def test_tokyo_target_cards_have_one_to_one_evidence_and_unique_source_locations():
    catalog = load(CATALOG_PATH)
    evidence = load(EVIDENCE_PATH)
    items = catalog["items"]
    packets = evidence["packets"]
    items_by_id = {item["id"]: item for item in items}
    packets_by_subject = {packet["subject_id"]: packet for packet in packets}

    assert evidence["packet_count"] == len(packets) == 304
    assert set(packets_by_subject) == set(items_by_id)
    assert len(packets_by_subject) == 304

    source_locations = {
        (
            item["source_page"],
            tuple(item["source_card_bbox"]),
            item["target_name_original"],
        )
        for item in items
    }
    assert len(source_locations) == 304

    for subject_id, item in items_by_id.items():
        packet = packets_by_subject[subject_id]
        assert packet["source_page"] == item["source_page"]
        assert packet["source_card_bbox"] == item["source_card_bbox"]
        assert packet["claims"]
        assert packet["review_status"] == "reviewed"


def test_tokyo_review_keeps_target_cards_separate_from_chart_points_and_actuals():
    items = load(CATALOG_PATH)["items"]
    detailed = [item for item in items if item["detailed_series_status"] == "reviewed"]
    card_only = [item for item in items if item["detailed_series_status"] == "not_normalized"]

    assert len(detailed) == 8
    assert len(card_only) == 296
    assert {item["policy_area_code"] for item in detailed} == {"01"}
    assert {item["source_page"] for item in detailed} == {1, 2}
    assert all(item["actual_linkage_status"] == "not_linked" for item in items)
    assert all(item["evaluation_status"] == "not_assessed" for item in items)
    assert all(item["review_status"] == "reviewed" for item in items)


def test_tokyo_grouped_panels_and_duplicate_layers_are_preserved_without_duplication():
    items = load(CATALOG_PATH)["items"]
    source_text = "\n".join(item["source_card_text_original"] for item in items)

    assert "2,000" in source_text
    assert "385万戸" in source_text
    assert any(
        "200" in item["source_card_text_original"]
        and "自治体" in item["source_card_text_original"]
        for item in items
    )
    assert all(item["highlighted_target_text_original"] for item in items)
    assert all(item["source_card_text_original"].strip() for item in items)


def test_tokyo_semantic_flags_cover_non_comparable_target_types():
    items = load(CATALOG_PATH)["items"]
    flags = {flag for item in items for flag in item["semantic_flags"]}

    assert {
        "cumulative",
        "maintenance",
        "minimum",
        "maximum",
        "ranking",
        "qualitative",
        "rate",
        "count",
        "money",
        "time",
    } <= flags
