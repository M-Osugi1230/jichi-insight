import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def validate(schema_path: str, value):
    validator = Draft202012Validator(
        load(schema_path),
        format_checker=FormatChecker(),
    )
    return list(validator.iter_errors(value))


def test_policy_collection_profile_fixture_is_valid():
    fixture = load("data/examples/policy_collection_profile.example.json")
    assert validate("schemas/policy_collection_profile.schema.json", fixture) == []
    assert fixture["id"] == "policy-profile-example-city"
    assert "架空" in fixture["caveats"][0]


def test_real_policy_collection_profiles_match_contract():
    profiles = load("data/entities/policy/policy_collection_profiles.json")
    assert len(profiles) == 3
    assert {profile["municipality_key"] for profile in profiles} == {
        "fukuoka-prefecture",
        "fukuoka-city",
        "kitakyushu-city",
    }
    for profile in profiles:
        assert validate("schemas/policy_collection_profile.schema.json", profile) == []
        assert profile["review_status"] == "reviewed"
        assert profile["capabilities"]
        assert profile["caveats"]


def test_confirmed_counts_and_depth_are_not_flattened():
    profiles = {
        profile["municipality_key"]: profile
        for profile in load("data/entities/policy/policy_collection_profiles.json")
    }
    prefecture = profiles["fukuoka-prefecture"]
    prefecture_counts = {
        capability["dimension"]: capability["count"]
        for capability in prefecture["capabilities"]
    }
    assert prefecture_counts["strategic_directions"] == 4
    assert prefecture_counts["initiative_progress"] == 30
    assert prefecture_counts["annual_reports"] == 3
    assert prefecture["extraction_readiness"] == "high"

    city = profiles["fukuoka-city"]
    city_counts = {
        capability["dimension"]: capability["count"]
        for capability in city["capabilities"]
    }
    assert city_counts["priority_project_sheets"] == 12
    assert city["extraction_readiness"] == "high"

    kitakyushu = profiles["kitakyushu-city"]
    assert kitakyushu["extraction_readiness"] == "medium"
    assert all(
        capability["availability"] == "entry_point_only"
        for capability in kitakyushu["capabilities"]
    )


def test_profile_sources_and_evidence_are_complete():
    profiles = load("data/entities/policy/policy_collection_profiles.json")
    packets = load(
        "data/entities/policy/policy_collection_profile_evidence_packets.json"
    )
    policy_sources = load("data/catalog/policy_sources.json")["records"]
    source_ids = {source["id"] for source in policy_sources}

    assert {packet["subject_id"] for packet in packets} == {
        profile["id"] for profile in profiles
    }
    for profile in profiles:
        for capability in profile["capabilities"]:
            assert set(capability["source_ids"]) <= source_ids

    for packet in packets:
        assert validate("schemas/evidence_packet.schema.json", packet) == []
        assert packet["open_questions"]
        for claim in packet["claims"]:
            assert set(claim["source_ids"]) <= source_ids
