import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "data/reviewed/aichi_policy_indicators.json"
EVIDENCE_PATH = ROOT / "data/evidence/aichi_policy_indicator_evidence.json"
MANIFEST_PATH = ROOT / "data/catalog/aichi_policy_indicator_review_manifest.json"


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


def test_aichi_catalog_evidence_and_manifest_are_schema_valid():
    validate("aichi_policy_indicators.schema.json", load(CATALOG_PATH))
    validate("aichi_policy_indicator_evidence.schema.json", load(EVIDENCE_PATH))
    validate(
        "aichi_policy_indicator_review_manifest.schema.json",
        load(MANIFEST_PATH),
    )


def test_aichi_counts_match_canonical_data():
    catalog = load(CATALOG_PATH)
    evidence = load(EVIDENCE_PATH)
    manifest = load(MANIFEST_PATH)
    items = catalog["items"]
    series = [series for item in items for series in item["series"]]

    assert len(items) == 56
    assert len({item["id"] for item in items}) == 56
    assert [item["display_order"] for item in items] == list(range(1, 57))
    assert len(series) == 62
    assert sum(item["linked_current_series_count"] for item in items) == 61
    assert sum(item["target_series_count"] for item in items) == 29
    assert sum(item["repost_of"] is not None for item in items) == 2
    assert evidence["packet_count"] == len(evidence["packets"]) == 56
    assert manifest["reviewed_indicator_row_count"] == 56
    assert manifest["unique_indicator_count"] == 54
    assert manifest["reviewed_indicator_series_count"] == 62
    assert manifest["series_with_current_value"] == 61
    assert manifest["series_with_target_value"] == 29
    assert manifest["evidence_packet_count"] == 56
    assert manifest["status"] == "complete"


def test_aichi_evidence_covers_every_indicator_once():
    catalog_ids = {item["id"] for item in load(CATALOG_PATH)["items"]}
    evidence = load(EVIDENCE_PATH)
    subject_ids = [packet["subject_id"] for packet in evidence["packets"]]

    assert set(subject_ids) == catalog_ids
    assert len(subject_ids) == len(set(subject_ids))
    assert all(packet["review_status"] == "reviewed" for packet in evidence["packets"])
    assert all(packet["claims"] for packet in evidence["packets"])


def test_aichi_preserves_multi_series_and_missing_values():
    items = {item["display_order"]: item for item in load(CATALOG_PATH)["items"]}

    special_support = items[10]
    assert [series["label"] for series in special_support["series"]] == [
        "特別支援学級",
        "通級指導教室",
    ]
    assert special_support["series"][1]["values"][1]["value"] == 662.5

    childcare = items[16]
    assert [series["label"] for series in childcare["series"]] == ["夫", "妻"]

    health = items[23]
    assert [series["label"] for series in health["series"]] == ["男性", "女性"]
    assert all(
        series["values"][-1]["operator"] == "minimum"
        for series in health["series"]
    )

    water = items[53]
    assert len(water["series"]) == 4
    assert {series["label"] for series in water["series"]} == {
        "河川 BOD",
        "海域 COD",
        "海域 全窒素",
        "海域 全りん",
    }

    road = items[40]
    assert {value["status"] for value in road["series"][0]["values"]} == {"missing"}
    assert road["linked_current_series_count"] == 0


def test_aichi_preserves_aggregation_and_definition_boundaries():
    items = {item["display_order"]: item for item in load(CATALOG_PATH)["items"]}

    happiness_target = items[1]["series"][0]["values"][-1]
    assert happiness_target["aggregation_scope"] == "multi_period_average"
    assert happiness_target["operator"] == "minimum"

    foreign_company_target = items[38]["series"][0]["values"][-1]
    assert foreign_company_target["aggregation_scope"] == "cumulative"

    migration_values = items[49]["series"][0]["values"]
    assert [value["aggregation_scope"] for value in migration_values] == [
        "multi_period_average",
        "single_period",
        "cumulative",
    ]

    farmer_note = items[34]["series"][0]["comparability_note_original"]
    assert "販売農家数" in farmer_note
    assert "農業経営体数" in farmer_note
    assert "直接比較しない" in farmer_note


def test_aichi_reposts_and_target_revision_are_explicit():
    items = load(CATALOG_PATH)["items"]
    reposts = [item for item in items if item["repost_of"]]
    assert [(item["display_order"], item["repost_of"]) for item in reposts] == [
        (48, "aichi-indicator-036"),
        (51, "aichi-indicator-003"),
    ]

    revisions = [
        item
        for item in items
        if item["target_revision_status"] == "revised_in_2025_report"
    ]
    assert len(revisions) == 1
    assert revisions[0]["display_order"] == 12
    assert "2025年度" in revisions[0]["series"][0]["comparability_note_original"]
    assert "2026年度" in revisions[0]["series"][0]["comparability_note_original"]


def test_aichi_does_not_infer_policy_achievement_or_management_project_scores():
    catalog = load(CATALOG_PATH)
    manifest = load(MANIFEST_PATH)

    assert all(item["evaluation_status"] == "not_assessed" for item in catalog["items"])
    assert manifest["policy_achievement_assessed_indicator_count"] == 0
    assert manifest["management_projects_evaluated_2025"] == 296
    assert manifest["management_projects_without_evaluation_result_2025"] == 28
