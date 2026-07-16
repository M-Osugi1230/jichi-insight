import json
from pathlib import Path
from urllib.parse import urlparse

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

WAVE_ONE_SOURCE_KEYS = {
    "hokkaido-prefecture": "01",
    "miyagi-prefecture": "04",
    "tokyo-metropolis": "13",
    "aichi-prefecture": "23",
    "osaka-prefecture": "27",
    "hiroshima-prefecture": "34",
    "kagawa-prefecture": "37",
    "okinawa-prefecture": "47",
}
PILOT_KEYS = {
    "fukuoka-prefecture",
    "fukuoka-city",
    "kitakyushu-city",
}


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def validate(schema_path: str, value):
    validator = Draft202012Validator(
        load(schema_path),
        format_checker=FormatChecker(),
    )
    return list(validator.iter_errors(value))


def test_policy_source_catalog_matches_contract_and_expanded_scope():
    catalog = load("data/catalog/policy_sources.json")
    assert validate("schemas/policy_source_catalog.schema.json", catalog) == []
    assert catalog["version"] == "0.3.0"
    assert catalog["updated_at"] == "2026-07-16"
    assert len(catalog["records"]) == 36
    assert {record["municipality_key"] for record in catalog["records"]} == (
        PILOT_KEYS | set(WAVE_ONE_SOURCE_KEYS)
    )
    assert len({record["id"] for record in catalog["records"]}) == len(
        catalog["records"]
    )
    assert len({record["url"] for record in catalog["records"]}) == len(
        catalog["records"]
    )


def test_reviewed_pilot_sources_keep_their_existing_quality_boundary():
    records = load("data/catalog/policy_sources.json")["records"]
    pilot_records = [
        record for record in records if record["municipality_key"] in PILOT_KEYS
    ]

    assert len(pilot_records) == 10
    assert all(
        record["collection_status"] == "ready_for_extraction"
        for record in pilot_records
    )
    assert all(record["review_status"] == "reviewed" for record in pilot_records)
    assert all(record["confidence"] == "high" for record in pilot_records)


def test_wave_one_strategic_sources_are_indexed_and_verified_but_not_reviewed():
    records = load("data/catalog/policy_sources.json")["records"]
    wave_one_records = [
        record
        for record in records
        if record["municipality_key"] in WAVE_ONE_SOURCE_KEYS
        and record["source_role"] == "strategic_plan"
    ]

    assert len(wave_one_records) == 8
    assert {record["municipality_key"] for record in wave_one_records} == set(
        WAVE_ONE_SOURCE_KEYS
    )
    assert all(record["collection_status"] == "indexed" for record in wave_one_records)
    assert all(record["review_status"] == "verified" for record in wave_one_records)
    assert all(record["confidence"] == "high" for record in wave_one_records)
    assert all("kpis" in record["extraction_targets"] for record in wave_one_records)


def test_hokkaido_kpi_sources_are_eighteen_verified_pdf_documents():
    records = load("data/catalog/policy_sources.json")["records"]
    kpi_sources = [
        record
        for record in records
        if record["municipality_key"] == "hokkaido-prefecture"
        and record["source_role"] == "kpi_source"
    ]

    assert len(kpi_sources) == 18
    assert all(record["format"] == "pdf" for record in kpi_sources)
    assert all(record["collection_status"] == "indexed" for record in kpi_sources)
    assert all(record["review_status"] == "verified" for record in kpi_sources)
    assert all(record["extraction_targets"] == ["kpis"] for record in kpi_sources)
    assert [record["title"].split(" ")[2] for record in kpi_sources] == [
        f"{number:02d}" for number in range(1, 19)
    ]


def test_wave_one_source_titles_and_urls_match_the_nationwide_registry():
    records = load("data/catalog/policy_sources.json")["records"]
    coverage = load("data/catalog/prefecture_coverage.json")
    sources_by_key = {
        record["municipality_key"]: record
        for record in records
        if record["municipality_key"] in WAVE_ONE_SOURCE_KEYS
        and record["source_role"] == "strategic_plan"
    }
    plan_sources_by_code = {
        source["prefecture_code"]: source for source in coverage["plan_sources"]
    }

    for municipality_key, prefecture_code in WAVE_ONE_SOURCE_KEYS.items():
        source = sources_by_key[municipality_key]
        nationwide_source = plan_sources_by_code[prefecture_code]
        assert source["title"] == nationwide_source["title"]
        assert source["url"] == nationwide_source["url"]


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
        "kpi_source",
    } <= roles


def test_policy_sources_use_official_municipal_domains():
    records = load("data/catalog/policy_sources.json")["records"]
    allowed_hosts = {
        "www.pref.hokkaido.lg.jp",
        "www.pref.miyagi.jp",
        "www.seisakukikaku.metro.tokyo.lg.jp",
        "www.pref.aichi.jp",
        "www.pref.osaka.lg.jp",
        "www.pref.hiroshima.lg.jp",
        "www.pref.kagawa.lg.jp",
        "www.pref.fukuoka.lg.jp",
        "www.pref.okinawa.jp",
        "www.city.fukuoka.lg.jp",
        "www.city.kitakyushu.lg.jp",
    }
    assert {urlparse(record["url"]).hostname for record in records} <= allowed_hosts


def test_superseded_tokyo_and_osaka_sources_do_not_return():
    records = load("data/catalog/policy_sources.json")["records"]
    titles = {record["title"] for record in records}
    urls = {record["url"] for record in records}

    assert "「未来の東京」戦略" not in titles
    assert "将来ビジョン・大阪" not in titles
    assert not any("/basic-plan/choki-plan" in url for url in urls)
    assert not any("/shouraivision/" in url for url in urls)


def test_policy_source_fixture_is_fictional_and_valid():
    fixture = load("data/examples/policy_source_catalog.example.json")
    assert validate("schemas/policy_source_catalog.schema.json", fixture) == []
    assert fixture["records"][0]["organization"] == "架空市"
