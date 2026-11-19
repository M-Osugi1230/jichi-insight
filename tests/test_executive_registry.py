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
    assert len(catalog["records"]) == 34
    assert len({record["id"] for record in catalog["records"]}) == 34


def test_executive_registry_matches_shared_contracts() -> None:
    terms = load_json("data/entities/executives/executive_terms.json")
    packets = load_json("data/entities/executives/evidence_packets.json")

    assert len(terms) == 7
    assert {term["municipality_id"] for term in terms} == {
        "jp-local-400009",
        "jp-local-401307",
        "jp-local-401005",
        "jp-local-230006",
        "jp-local-231002",
        "jp-local-232114",
        "jp-local-010006",
    }
    for term in terms:
        assert validation_errors("schemas/executive_term.schema.json", term) == []
        assert term["status"] == "current"
        assert term["review_status"] == "reviewed"
        assert term["confidence"] == "high"
    for packet in packets:
        assert validation_errors("schemas/evidence_packet.schema.json", packet) == []


def test_executive_term_ends_match_official_term_expiry_records() -> None:
    terms = load_json("data/entities/executives/executive_terms.json")
    packets = load_json("data/entities/executives/evidence_packets.json")
    known_sources = source_ids()

    # Term ends are registered only where an official source states the
    # expiry date itself; they are never derived by adding four years.
    # Hokkaido is the documented exception in construction, not in rigour:
    # no official page states the current expiry day, so the end is fixed
    # by the statutory chain — the previous term's expiry (2023-04-22) is
    # officially published, the 2023 election was a term-expiry election
    # (election commission gazette), and Article 259's proviso plus the
    # four-year term of the Local Autonomy Act fix 2023-04-23 to
    # 2027-04-22. The evidence packet records the full chain.
    expected_term_ends = {
        "jp-local-400009": "2029-04-10",
        "jp-local-401307": "2026-12-06",
        "jp-local-401005": "2027-02-19",
        "jp-local-230006": "2027-02-14",
        "jp-local-231002": "2028-11-23",
        "jp-local-232114": "2028-02-18",
        "jp-local-010006": "2027-04-22",
    }
    for term in terms:
        assert term["term_end"] == expected_term_ends[term["municipality_id"]]

    packets_by_subject = {packet["subject_id"]: packet for packet in packets}
    for term in terms:
        packet = packets_by_subject[term["id"]]
        term_end_claims = [
            claim for claim in packet["claims"] if claim["field"] == "term_end"
        ]
        assert len(term_end_claims) == 1
        assert term_end_claims[0]["decision"] == "accepted"
        assert set(term_end_claims[0]["source_ids"]) <= known_sources
        assert set(term_end_claims[0]["source_ids"]) <= set(term["sources"])


def test_executive_term_starts_follow_statutory_counting() -> None:
    from datetime import date, timedelta

    terms = load_json("data/entities/executives/executive_terms.json")
    packets = load_json("data/entities/executives/evidence_packets.json")
    known_sources = source_ids()

    # Term starts follow the counting rule of Article 259 of the Public
    # Offices Election Act; each four-year term ends the day before the
    # fourth anniversary of its start. The Fukuoka governor's second
    # term starts on 2025-04-11 (the day after the first term expired);
    # the earlier value 2025-04-14 was the 2021 election-proclamation
    # date plus four years and was corrected under Issue #676. The
    # record ID keeps the original date as an opaque identifier.
    expected_term_starts = {
        "jp-local-400009": "2025-04-11",
        "jp-local-401307": "2022-12-07",
        "jp-local-401005": "2023-02-20",
        "jp-local-230006": "2023-02-15",
        "jp-local-231002": "2024-11-24",
        "jp-local-232114": "2024-02-19",
        "jp-local-010006": "2023-04-23",
    }
    for term in terms:
        assert term["term_start"] == expected_term_starts[term["municipality_id"]]
        start = date.fromisoformat(term["term_start"])
        expected_end = start.replace(year=start.year + 4) - timedelta(days=1)
        assert term["term_end"] == expected_end.isoformat()

    packets_by_subject = {packet["subject_id"]: packet for packet in packets}
    governor = next(
        term for term in terms if term["municipality_id"] == "jp-local-400009"
    )
    packet = packets_by_subject[governor["id"]]
    start_claims = [
        claim for claim in packet["claims"] if claim["field"] == "term_start"
    ]
    assert len(start_claims) == 1
    assert start_claims[0]["decision"] == "accepted"
    assert set(start_claims[0]["source_ids"]) <= known_sources
    assert set(start_claims[0]["source_ids"]) <= set(governor["sources"])


def test_manifesto_readiness_is_not_confused_with_progress() -> None:
    terms = load_json("data/entities/executives/executive_terms.json")
    by_municipality = {term["municipality_id"]: term for term in terms}

    assert by_municipality["jp-local-400009"]["manifesto_source_ids"] == [
        "fukuoka-pref-governor-election-2025-bulletin",
    ]
    assert by_municipality["jp-local-401307"]["manifesto_source_ids"] == [
        "fukuoka-city-mayor-election-2022-bulletin",
        "fukuoka-city-mayor-manifesto-2022-go2senkyo-archive",
    ]
    assert by_municipality["jp-local-401005"]["manifesto_source_ids"] == [
        "kitakyushu-mayor-election-2023-bulletin",
        "kitakyushu-mayor-candidate-2023-manifesto-v13-archive",
    ]
    assert by_municipality["jp-local-231002"]["manifesto_source_ids"] == [
        "nagoya-city-mayor-election-2024-bulletin",
    ]
    # Toyota City registers no manifesto source: the 2024 bulletin is
    # not extant as an official web publication and no verifiable
    # candidate publication was found (see the source search record).
    assert by_municipality["jp-local-232114"]["manifesto_source_ids"] == []


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
