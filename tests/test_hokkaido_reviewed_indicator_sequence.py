import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY_DIR = ROOT / "data/entities/policy"

CATALOG_PATHS = [
    POLICY_DIR / "hokkaido_indicator_catalog_food.json",
    POLICY_DIR / "hokkaido_indicator_catalog_tourism.json",
    POLICY_DIR / "hokkaido_indicator_catalog_zero_carbon.json",
    POLICY_DIR / "hokkaido_indicator_catalog_digital.json",
    POLICY_DIR / "hokkaido_indicator_catalog_manufacturing_growth.json",
    POLICY_DIR / "hokkaido_indicator_catalog_industry_cross_sector.json",
    POLICY_DIR / "hokkaido_indicator_catalog_children_parenting.json",
    POLICY_DIR / "hokkaido_indicator_catalog_education_learning.json",
    POLICY_DIR / "hokkaido_indicator_catalog_medical_welfare.json",
    POLICY_DIR / "hokkaido_indicator_catalog_employment_work.json",
    POLICY_DIR / "hokkaido_indicator_catalog_sme_commerce.json",
    POLICY_DIR / "hokkaido_indicator_catalog_safety_security.json",
]
EVIDENCE_PATHS = [
    POLICY_DIR / "hokkaido_indicator_food_evidence_packets.json",
    POLICY_DIR / "hokkaido_indicator_tourism_evidence_packets.json",
    POLICY_DIR / "hokkaido_indicator_zero_carbon_evidence_packets.json",
    POLICY_DIR / "hokkaido_indicator_digital_evidence_packets.json",
    POLICY_DIR / "hokkaido_indicator_manufacturing_growth_evidence_packets.json",
    POLICY_DIR / "hokkaido_indicator_industry_cross_sector_evidence_packets.json",
    POLICY_DIR / "hokkaido_indicator_children_parenting_evidence_packets.json",
    POLICY_DIR / "hokkaido_indicator_education_learning_evidence_packets.json",
    POLICY_DIR / "hokkaido_indicator_medical_welfare_evidence_packets.json",
    POLICY_DIR / "hokkaido_indicator_employment_work_evidence_packets.json",
    POLICY_DIR / "hokkaido_indicator_sme_commerce_evidence_packets.json",
    POLICY_DIR / "hokkaido_indicator_safety_security_evidence_packets.json",
]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_reviewed_hokkaido_indicators_form_one_sequence_through_79():
    indicators = [
        item
        for path in CATALOG_PATHS
        for item in load(path)["items"]
    ]
    numbers = sorted(item["indicator_number"] for item in indicators)
    ids = [item["id"] for item in indicators]

    assert numbers == list(range(1, 80))
    assert len(ids) == len(set(ids)) == 79
    assert all(item["review_status"] == "reviewed" for item in indicators)
    assert all(item["actual_linkage_status"] == "not_linked" for item in indicators)
    assert all(item["evaluation_status"] == "not_assessed" for item in indicators)


def test_every_reviewed_indicator_has_exactly_one_evidence_packet():
    indicator_ids = {
        item["id"]
        for path in CATALOG_PATHS
        for item in load(path)["items"]
    }
    packets = [
        packet
        for path in EVIDENCE_PATHS
        for packet in load(path)
    ]
    subject_ids = [packet["subject_id"] for packet in packets]

    assert len(packets) == 79
    assert len(subject_ids) == len(set(subject_ids))
    assert set(subject_ids) == indicator_ids


def test_manifest_counts_match_reviewed_files():
    manifest = load(ROOT / "data/catalog/hokkaido_policy_review_manifest.json")
    indicator_count = sum(len(load(path)["items"]) for path in CATALOG_PATHS)
    evidence_count = sum(len(load(path)) for path in EVIDENCE_PATHS)

    assert manifest["reviewed_indicator_count"] == indicator_count == 79
    assert manifest["indicator_evidence_packet_count"] == evidence_count == 79
    assert manifest["remaining_indicator_count"] == 108 - indicator_count == 29


def test_conditional_targets_remain_non_numeric_and_original():
    indicators = [
        item
        for path in CATALOG_PATHS
        for item in load(path)["items"]
    ]
    conditional_values = [
        value
        for indicator in indicators
        for series in indicator["series"]
        for value in series["values"]
        if value["status"] == "conditional"
    ]

    assert len(conditional_values) == 10
    assert all(value["value"] is None for value in conditional_values)
    texts = [value["value_text_original"] for value in conditional_values]
    assert texts.count("各年において前年よりも上昇") == 2
    assert texts.count("全国値") == 2
    assert texts.count("現状より増加") == 2
    assert texts.count("法定雇用率以上") == 2
    assert texts.count("中間目標値以下かつ過去５年平均値以下") == 1
    assert texts.count("中間目標値以上かつ過去５年平均値以上") == 1
