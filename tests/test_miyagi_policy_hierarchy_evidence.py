import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
HIERARCHY = POLICY / "miyagi_policy_hierarchy.json"
EVIDENCE = POLICY / "miyagi_policy_hierarchy_evidence_packets.json"
INVENTORY = ROOT / "data/catalog/miyagi_policy_source_inventory.json"
SCHEMA = ROOT / "schemas/evidence_packet.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_evidence_packets_match_schema_and_hierarchy_subjects():
    hierarchy = load(HIERARCHY)
    packets = load(EVIDENCE)
    validator = Draft202012Validator(load(SCHEMA))
    direction_ids = {direction["id"] for direction in hierarchy["directions"]}
    subject_ids = {packet["subject_id"] for packet in packets}

    assert len(packets) == 5
    assert all(list(validator.iter_errors(packet)) == [] for packet in packets)
    assert direction_ids <= subject_ids
    assert "policy-collection-miyagi-reconstruction-support" in subject_ids
    assert all(packet["review_status"] == "reviewed" for packet in packets)
    assert all(packet["open_questions"] == [] for packet in packets)


def test_all_evidence_sources_exist_in_source_inventory():
    packets = load(EVIDENCE)
    inventory_sources = {
        source["id"] for source in load(INVENTORY)["sources"]
    }

    for packet in packets:
        for claim in packet["claims"]:
            assert set(claim["source_ids"]) <= inventory_sources
            assert claim["decision"] == "accepted"
            assert claim["location_note"]


def test_direction_packets_preserve_policy_and_measure_ranges():
    packets = {
        packet["subject_id"]: packet
        for packet in load(EVIDENCE)
    }
    expected_ranges = {
        "policy-direction-miyagi-industry-growth": "政策1・2と施策1〜5",
        "policy-direction-miyagi-children-parenting": "政策3・4と施策6〜9",
        "policy-direction-miyagi-inclusive-community": "政策5・6と施策10〜14",
        "policy-direction-miyagi-resilient-environment": "政策7・8と施策15〜18",
    }

    for subject_id, expected in expected_ranges.items():
        claim = next(
            claim
            for claim in packets[subject_id]["claims"]
            if claim["field"] == "policies_and_measures"
        )
        assert expected in claim["statement"]
        assert "公式掲載順" in claim["review_note"]


def test_typography_difference_and_parallel_domains_are_explicit():
    packets = {
        packet["subject_id"]: packet
        for packet in load(EVIDENCE)
    }
    resilient = packets["policy-direction-miyagi-resilient-environment"]
    title_claim = next(
        claim for claim in resilient["claims"] if claim["field"] == "title_original"
    )
    reconstruction = packets["policy-collection-miyagi-reconstruction-support"]
    collection_claim = next(
        claim
        for claim in reconstruction["claims"]
        if claim["field"] == "collection_title"
    )

    assert "『強靱』表記" in title_claim["review_note"]
    assert "別枠" in collection_claim["statement"]
    assert "政策番号1〜8へ含めず" in collection_claim["review_note"]
