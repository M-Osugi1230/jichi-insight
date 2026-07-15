import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def validate(schema_path, value):
    validator = Draft202012Validator(
        load(schema_path),
        format_checker=FormatChecker(),
    )
    return list(validator.iter_errors(value))


def test_manifesto_source_search_fixture_is_registered_and_linked():
    fixture = load("data/examples/manifesto_source_search.example.json")
    executive_term = load("data/examples/executive_term.example.json")
    source = load("data/examples/source.example.json")

    assert validate("schemas/manifesto_source_search.schema.json", fixture) == []
    assert fixture["executive_term_id"] == executive_term["id"]
    assert set(fixture["checked_source_ids"]) == {source["id"]}
    assert fixture["manifesto_source_ids_found"] == []
    assert fixture["nonexistence_claim"] is False


def test_manifesto_source_searches_match_contract_and_safety_boundary():
    searches = load("data/entities/executives/manifesto_source_searches.json")

    assert len(searches) == 3
    assert {search["executive_term_id"] for search in searches} == {
        "jp-local-400009-executive-2025-04-14",
        "jp-local-401307-executive-2022-12-07",
        "jp-local-401005-executive-2023-02-20",
    }

    for search in searches:
        assert validate("schemas/manifesto_source_search.schema.json", search) == []
        assert search["nonexistence_claim"] is False
        assert search["checked_source_ids"]
        assert search["next_actions"]

    missing = [
        search
        for search in searches
        if search["result_status"] == "no_stable_primary_source_found"
    ]
    assert len(missing) == 2
    assert all(search["manifesto_source_ids_found"] == [] for search in missing)

    registered = next(
        search for search in searches if search["result_status"] == "source_registered"
    )
    assert registered["manifesto_source_ids_found"] == [
        "kitakyushu-mayor-election-2023-bulletin"
    ]


def test_manifesto_source_search_references_and_evidence_are_complete():
    searches = load("data/entities/executives/manifesto_source_searches.json")
    packets = load(
        "data/entities/executives/manifesto_source_search_evidence_packets.json"
    )
    terms = load("data/entities/executives/executive_terms.json")
    executive_sources = load("data/catalog/executive_sources.json")["records"]
    official_sources = load("data/catalog/official_sources.json")["records"]

    term_ids = {term["id"] for term in terms}
    source_ids = {
        source["id"] for source in [*official_sources, *executive_sources]
    }

    assert {search["executive_term_id"] for search in searches} <= term_ids
    assert {packet["subject_id"] for packet in packets} == {
        search["id"] for search in searches
    }

    for search in searches:
        assert set(search["checked_source_ids"]) <= source_ids
        assert set(search["manifesto_source_ids_found"]) <= source_ids

    for packet in packets:
        assert validate("schemas/evidence_packet.schema.json", packet) == []
        assert packet["open_questions"]
        for claim in packet["claims"]:
            assert set(claim["source_ids"]) <= source_ids
