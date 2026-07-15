from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATHS = [
    "data/catalog/official_sources.json",
    "data/catalog/fukuoka_finance_sources.json",
    "data/catalog/fukuoka_city_finance_sources.json",
    "data/catalog/kitakyushu_finance_sources.json",
    "data/catalog/fukuoka_assembly_sources.json",
    "data/catalog/executive_sources.json",
]


def load_json(path: str) -> Any:
    with (ROOT / path).open(encoding="utf-8") as handle:
        return json.load(handle)


def validation_errors(schema_path: str, instance: Any) -> list[str]:
    validator = Draft202012Validator(
        load_json(schema_path),
        format_checker=FormatChecker(),
    )
    return [error.message for error in validator.iter_errors(instance)]


def source_ids() -> set[str]:
    return {
        source["id"]
        for path in CATALOG_PATHS
        for source in load_json(path)["records"]
    }


def test_executive_source_catalog_matches_contract() -> None:
    catalog = load_json("data/catalog/executive_sources.json")
    assert validation_errors("schemas/source_catalog.schema.json", catalog) == []
    assert len(catalog["records"]) == 4
    assert len({record["id"] for record in catalog["records"]}) == 4


def test_executive_registry_matches_shared_contracts() -> None:
    terms = load_json("data/entities/executives/executive_terms.json")
    packets = load_json("data/entities/executives/evidence_packets.json")

    assert len(terms) == 3
    assert {term["municipality_id"] for term in terms} == {
        "jp-local-400009",
        "jp-local-401307",
        "jp-local-401005",
    }
    for term in terms:
        assert validation_errors("schemas/executive_term.schema.json", term) == []
        assert term["status"] == "current"
        assert term["review_status"] == "reviewed"
        assert term["confidence"] == "high"
    for packet in packets:
        assert validation_errors("schemas/evidence_packet.schema.json", packet) == []


def test_manifesto_readiness_is_not_confused_with_progress() -> None:
    terms = load_json("data/entities/executives/executive_terms.json")
    by_municipality = {term["municipality_id"]: term for term in terms}

    assert by_municipality["jp-local-400009"]["manifesto_source_ids"] == []
    assert by_municipality["jp-local-401307"]["manifesto_source_ids"] == []
    assert by_municipality["jp-local-401005"]["manifesto_source_ids"] == [
        "kitakyushu-mayor-election-2023-bulletin"
    ]


def test_every_executive_has_evidence_and_known_sources() -> None:
    terms = load_json("data/entities/executives/executive_terms.json")
    packets = load_json("data/entities/executives/evidence_packets.json")
    known_sources = source_ids()

    assert {packet["subject_id"] for packet in packets} == {
        term["id"] for term in terms
    }
    for term in terms:
        assert set(term["sources"]) <= known_sources
        assert set(term["manifesto_source_ids"]) <= known_sources
    for packet in packets:
        assert packet["open_questions"]
        for claim in packet["claims"]:
            assert set(claim["source_ids"]) <= known_sources
