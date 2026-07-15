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


def test_source_request_fixture_is_unsent_and_valid():
    fixture = load("data/examples/source_request.example.json")
    assert validate("schemas/source_request.schema.json", fixture) == []
    assert fixture["status"] == "draft"
    assert fixture["sent_at"] is None
    assert fixture["response_received_at"] is None
    assert fixture["response_summary"] is None


def test_real_source_request_drafts_are_unsent_and_complete():
    requests = load("data/entities/executives/source_requests.json")
    assert len(requests) == 2
    for request in requests:
        assert validate("schemas/source_request.schema.json", request) == []
        assert request["status"] == "draft"
        assert request["sent_at"] is None
        assert request["response_received_at"] is None
        assert request["response_summary"] is None
        assert request["contact_channels"]
        assert request["requested_items"]


def test_source_request_references_and_evidence_are_complete():
    requests = load("data/entities/executives/source_requests.json")
    packets = load("data/entities/executives/source_request_evidence_packets.json")
    searches = load("data/entities/executives/manifesto_source_searches.json")
    terms = load("data/entities/executives/executive_terms.json")
    executive_sources = load("data/catalog/executive_sources.json")["records"]
    official_sources = load("data/catalog/official_sources.json")["records"]

    term_ids = {term["id"] for term in terms}
    search_ids = {search["id"] for search in searches}
    source_ids = {source["id"] for source in [*official_sources, *executive_sources]}

    assert {request["executive_term_id"] for request in requests} <= term_ids
    assert {request["manifesto_source_search_id"] for request in requests} <= search_ids
    assert {packet["subject_id"] for packet in packets} == {
        request["id"] for request in requests
    }

    for request in requests:
        assert set(request["source_ids"]) <= source_ids
        for channel in request["contact_channels"]:
            assert channel["public_source_id"] in source_ids

    for packet in packets:
        assert validate("schemas/evidence_packet.schema.json", packet) == []
        assert packet["open_questions"]
        for claim in packet["claims"]:
            assert set(claim["source_ids"]) <= source_ids
