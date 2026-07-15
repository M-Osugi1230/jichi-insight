import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATHS = [
    f"data/entities/policy/fukuoka_prefecture_initiative_{number:02d}_targets.json"
    for number in range(21, 27)
]
EVIDENCE_PATHS = [
    "data/entities/policy/"
    f"fukuoka_prefecture_initiative_{number:02d}_target_evidence_packet.json"
    for number in range(21, 27)
]


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def validate(schema_path: str, value):
    validator = Draft202012Validator(
        load(schema_path),
        format_checker=FormatChecker(),
    )
    return list(validator.iter_errors(value))


def component(items, index=0, component_index=0):
    return items[index]["components"][component_index]


def test_initiatives_21_to_26_are_valid_and_continuous():
    catalogs = [load(path) for path in CATALOG_PATHS]
    target_counts = [len(catalog["items"]) for catalog in catalogs]
    numbers = [
        item["target_number"]
        for catalog in catalogs
        for item in catalog["items"]
    ]
    source_pages = [catalog["source_page"] for catalog in catalogs]
    printed_pages = [catalog["printed_page"] for catalog in catalogs]

    assert target_counts == [2, 1, 3, 2, 6, 5]
    assert numbers == list(range(100, 119))
    assert source_pages == [8, 8, 9, 9, 9, 10]
    assert printed_pages == [323, 323, 324, 324, 324, 325]

    for catalog in catalogs:
        assert validate("schemas/policy_target_catalog.schema.json", catalog) == []
        assert all(
            item["actual_linkage_status"] == "not_linked"
            for item in catalog["items"]
        )
        assert all(
            item["evaluation_status"] == "not_assessed"
            for item in catalog["items"]
        )


def test_environment_and_infrastructure_targets_preserve_semantics():
    environment, waste, resilience, vitality, regions, infrastructure = [
        load(path)["items"] for path in CATALOG_PATHS
    ]

    water_quality = environment[1]["components"]
    water_baselines = [item["baseline_value"] for item in water_quality]
    water_targets = [item["target_text"] for item in water_quality]
    assert water_baselines == [96.0, 61.1, 83.3]
    assert water_targets == [
        "BOD 3mg/L以下",
        "COD 8mg/L以下",
        "全窒素 1.0mg/L以下",
    ]
    assert all(item["target_value"] is None for item in water_quality)
    assert all(
        item["target_scope"] == "relative_condition"
        for item in water_quality
    )

    assert component(waste)["baseline_value"] == 5482
    assert component(waste)["target_value"] == 5510
    assert component(waste)["preferred_direction"] == "decrease"

    resilience_targets = [
        component(resilience, index)["target_value"] for index in range(3)
    ]
    assert resilience_targets == [61, 100, 105500]
    assert component(resilience, 2)["preferred_direction"] == "decrease"

    vitality_targets = [
        component(vitality, index)["target_value"] for index in range(2)
    ]
    assert vitality_targets == [30, 140]
    assert all(
        component(vitality, index)["target_scope"] == "cumulative"
        for index in range(2)
    )

    region_targets = [
        component(regions, index)["target_value"] for index in range(6)
    ]
    assert region_targets == [100, 100, 75.2, 100, 10, 53.1]
    assert all(
        item["indicator_name_original"]
        not in {"飲酒運転による交通事故発生件数", "交通事故死者数"}
        for item in regions
    )

    infrastructure_targets = [
        component(infrastructure, index)["target_value"]
        for index in range(5)
    ]
    assert infrastructure_targets == [69.7, 98.0, 18.2, 18.8, 100]
    for index in (2, 3):
        assert component(infrastructure, index)["target_operator"] == "at_most"
        assert component(infrastructure, index)["preferred_direction"] == "decrease"
    assert all(
        item["indicator_name_original"]
        not in {
            "温室効果ガスの総排出量の削減率",
            "再生可能エネルギー発電設備導入容量",
        }
        for item in infrastructure
    )


def test_initiatives_21_to_26_have_evidence_and_valid_references():
    catalogs = [load(path) for path in CATALOG_PATHS]
    packets = [load(path) for path in EVIDENCE_PATHS]
    sources = load("data/catalog/policy_sources.json")["records"]
    initiatives = load(
        "data/entities/policy/fukuoka_prefecture_policy_initiatives.json"
    )["items"]
    source_ids = {source["id"] for source in sources}
    initiative_ids = {item["id"] for item in initiatives}
    catalog_initiative_ids = {
        catalog["policy_initiative_id"] for catalog in catalogs
    }
    packet_subject_ids = {packet["subject_id"] for packet in packets}
    catalog_ids = {catalog["id"] for catalog in catalogs}

    assert catalog_initiative_ids <= initiative_ids
    assert packet_subject_ids == catalog_ids
    for catalog in catalogs:
        assert set(catalog["source_ids"]) <= source_ids
    for packet in packets:
        assert validate("schemas/evidence_packet.schema.json", packet) == []
        assert packet["open_questions"]
        for claim in packet["claims"]:
            assert set(claim["source_ids"]) <= source_ids

    notes = " ".join(
        claim["review_note"] or ""
        for packet in packets
        for claim in packet["claims"]
    )
    assert "指標23・24の再掲" in notes
    assert "指標94・97の再掲" in notes
