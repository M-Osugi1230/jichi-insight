import json
from pathlib import Path
from urllib.parse import urlparse

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


def test_policy_source_catalog_matches_contract_and_pilot_scope():
    catalog = load("data/catalog/policy_sources.json")
    assert validate("schemas/policy_source_catalog.schema.json", catalog) == []
    assert len(catalog["records"]) == 10
    assert {record["municipality_key"] for record in catalog["records"]} == {
        "fukuoka-prefecture",
        "fukuoka-city",
        "kitakyushu-city",
    }
    assert len({record["id"] for record in catalog["records"]}) == len(
        catalog["records"]
    )


def test_policy_source_catalog_covers_the_accountability_chain():
    records = load("data/catalog/policy_sources.json")["records"]
    roles = {record["source_role"] for record in records}
    assert {
        "strategic_plan",
        "implementation_plan",
        "annual_progress_report",
        "annual_priority_program",
        "project_review",
        "progress_management",
    } <= roles
    assert all(record["collection_status"] == "ready_for_extraction" for record in records)
    assert all(record["review_status"] == "reviewed" for record in records)


def test_policy_sources_use_official_municipal_domains():
    records = load("data/catalog/policy_sources.json")["records"]
    allowed_hosts = {
        "www.pref.fukuoka.lg.jp",
        "www.city.fukuoka.lg.jp",
        "www.city.kitakyushu.lg.jp",
    }
    assert {urlparse(record["url"]).hostname for record in records} <= allowed_hosts


def test_policy_source_fixture_is_fictional_and_valid():
    fixture = load("data/examples/policy_source_catalog.example.json")
    assert validate("schemas/policy_source_catalog.schema.json", fixture) == []
    assert fixture["records"][0]["organization"] == "架空市"
