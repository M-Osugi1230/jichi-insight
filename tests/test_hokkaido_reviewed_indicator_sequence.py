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
]
EVIDENCE_PATHS = [
    POLICY_DIR / "hokkaido_indicator_food_evidence_packets.json",
    POLICY_DIR / "hokkaido_indicator_tourism_evidence_packets.json",
    POLICY_DIR / "hokkaido_indicator_zero_carbon_evidence_packets.json",
    POLICY_DIR / "hokkaido_indicator_digital_evidence_packets.json",
    POLICY_DIR / "hokkaido_indicator_manufacturing_growth_evidence_packets.json",
]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_reviewed_hokkaido_indicators_form_one_sequence_through_39():
    indicators = [
        item
        for path in CATALOG_PATHS
        for item in load(path)["items"]
    ]
    numbers = sorted(item["indicator_number"] for item in indicators)
    ids = [item["id"] for item in indicators]

    assert numbers == list(range(1, 40))
    assert len(ids) == len(set(ids)) == 39
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

    assert len(packets) == 39
    assert len(subject_ids) == len(set(subject_ids))
    assert set(subject_ids) == indicator_ids


def test_manifest_counts_match_reviewed_files():
    manifest = load(ROOT / "data/catalog/hokkaido_policy_review_manifest.json")
    indicator_count = sum(len(load(path)["items"]) for path in CATALOG_PATHS)
    evidence_count = sum(len(load(path)) for path in EVIDENCE_PATHS)

    assert manifest["reviewed_indicator_count"] == indicator_count == 39
    assert manifest["indicator_evidence_packet_count"] == evidence_count == 39
    assert manifest["remaining_indicator_count"] == 108 - indicator_count == 69
