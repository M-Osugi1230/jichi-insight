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
    assert len(catalog["records"]) == 76
    assert len({record["id"] for record in catalog["records"]}) == 76


def test_executive_registry_matches_shared_contracts() -> None:
    terms = load_json("data/entities/executives/executive_terms.json")
    packets = load_json("data/entities/executives/evidence_packets.json")

    assert len(terms) == 16
    assert {term["municipality_id"] for term in terms} == {
        "jp-local-400009",
        "jp-local-401307",
        "jp-local-401005",
        "jp-local-230006",
        "jp-local-231002",
        "jp-local-232114",
        "jp-local-010006",
        "jp-local-012041",
        "jp-local-011002",
        "jp-local-270008",
        "jp-local-271004",
        "jp-local-271403",
        "jp-local-140007",
        "jp-local-141003",
        "jp-local-141305",
        "jp-local-110001",
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
    # Asahikawa City follows the same construction: the previous
    # term's expiry (2025-09-25) is stated in the city election
    # commission's official press-release document, the 2025 election
    # was a term-expiry election held before that date, and Article
    # 259's proviso plus the four-year term fix 2025-09-26 to
    # 2029-09-25. The evidence packet records the full chain and the
    # outstanding cross-check against the Hokkaido election
    # commission's term-expiry list.
    # 2027-04-22. The evidence packet records the full chain. Sapporo
    # City's end (2027-05-01) is stated directly in the Hokkaido Election
    # Commission's official term-expiry list; its start (2023-05-02)
    # follows the same Article 259 proviso chain, anchored by the
    # mayoral profile's stated May 2 term start and the stated expiry.
    # Osaka City is a different construction again: the mayor resigned
    # and was re-elected in the February 2026 snap election, so the
    # current term is the residue of the 2023 cycle. Both endpoints are
    # stated directly by official sources (the city's list of past
    # mayors gives the 2026-02-09 start; the city election commission
    # publishes the 2027-04-08 expiry), and the term is not reset by
    # the snap election.
    # Sakai City's end (2027-06-08) is stated directly in the city
    # election commission's official election-schedule page; its start
    # (2023-06-09) follows the same Article 259 proviso chain, anchored
    # by the previous term's expiry (2023-06-08) stated in the election
    # commission's own minutes, and the two values agree.
    # Kanagawa Prefecture's end (2027-04-22) is stated directly in the
    # prefectural election commission's official term-expiry list; its
    # start (2023-04-23) follows the same Article 259 proviso chain
    # (the 2023 election was a term-expiry election held before the
    # previous term expired), and the two values agree.
    # Yokohama City is a vacancy-election construction: the previous
    # mayor resigned on 2026-09-07, so under the main text of Article
    # 259 the term runs four years from the election day itself
    # (2026-10-18 to 2030-10-17). The prefectural term-expiry list's
    # current published edition (as of 2026-08-03) predates the
    # election and still shows the predecessor's expiry, so the stated
    # cross-check against the list is pending its next update; the
    # evidence packet records the full chain and the open question.
    # Kawasaki City's end (2029-11-18) is stated directly in the city
    # election commission's official list of terms of public offices;
    # its start (2025-11-19) follows the same Article 259 proviso
    # chain, anchored by the previous term's expiry (2025-11-18)
    # stated in the commission's election-schedule announcement, and
    # the two values agree.
    # Saitama Prefecture's end (2027-08-30) is stated directly in the
    # prefectural election commission's official term-expiry list; its
    # start (2023-08-31) and end are both also stated day-exact in the
    # Saitama City election commission's official ballot-count table
    # for the 2023 election, and the values agree.
    expected_term_ends = {
        "jp-local-400009": "2029-04-10",
        "jp-local-401307": "2026-12-06",
        "jp-local-401005": "2027-02-19",
        "jp-local-230006": "2027-02-14",
        "jp-local-231002": "2028-11-23",
        "jp-local-232114": "2028-02-18",
        "jp-local-010006": "2027-04-22",
        "jp-local-012041": "2029-09-25",
        "jp-local-011002": "2027-05-01",
        "jp-local-270008": "2027-04-08",
        "jp-local-271004": "2027-04-08",
        "jp-local-271403": "2027-06-08",
        "jp-local-140007": "2027-04-22",
        "jp-local-141003": "2030-10-17",
        "jp-local-141305": "2029-11-18",
        "jp-local-110001": "2027-08-30",
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
        "jp-local-012041": "2025-09-26",
        "jp-local-011002": "2023-05-02",
        "jp-local-270008": "2023-04-09",
        "jp-local-271004": "2026-02-09",
        "jp-local-271403": "2023-06-09",
        "jp-local-140007": "2023-04-23",
        "jp-local-141003": "2026-10-18",
        "jp-local-141305": "2025-11-19",
        "jp-local-110001": "2023-08-31",
    }
    for term in terms:
        assert term["term_start"] == expected_term_starts[term["municipality_id"]]
        if term["municipality_id"] == "jp-local-271004":
            # Osaka City's current term is the residue of the 2023
            # cycle after a resignation and snap re-election, so the
            # four-year arithmetic does not apply: the end is the
            # 2027-04-08 expiry published by the city election
            # commission (asserted in the term-ends test above).
            continue
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
    assert by_municipality["jp-local-011002"]["manifesto_source_ids"] == [
        "sapporo-city-mayor-election-2023-bulletin",
    ]
    # Osaka City's source is the February 2026 snap-election bulletin:
    # Issue #772 chose the most recent election's bulletin as the
    # primary source for the current mayor's promises.
    assert by_municipality["jp-local-271004"]["manifesto_source_ids"] == [
        "osaka-city-mayor-election-2026-bulletin",
    ]
    # Toyota City registers no manifesto source: the 2024 bulletin is
    # not extant as an official web publication and no verifiable
    # candidate publication was found (see the source search record).
    assert by_municipality["jp-local-232114"]["manifesto_source_ids"] == []
    # Asahikawa City registers no manifesto source either: the 2025
    # bulletin has no official web publication and no verifiable
    # candidate publication was found (see the source search record).
    assert by_municipality["jp-local-012041"]["manifesto_source_ids"] == []
    # Osaka Prefecture registers the 2026 re-election bulletin: the
    # promise stage (Issue #772) decided that the promises shown to
    # voters at the most recent election are the appropriate source,
    # even though the term itself started with the 2023 election. The
    # 2023 bulletin remains reachable but unregistered (see the
    # source search record).
    assert by_municipality["jp-local-270008"]["manifesto_source_ids"] == [
        "osaka-pref-governor-election-2026-bulletin",
    ]
    # Sakai City registers no manifesto source either: the 2023
    # bulletin has no official web publication and no verifiable
    # candidate publication was found (see the source search record).
    assert by_municipality["jp-local-271403"]["manifesto_source_ids"] == []
    # Kanagawa Prefecture registers the 2023 bulletin: the promise
    # stage (Issue #798) transcribed the image-only candidate panel
    # from rendered images at multiple resolutions and connected the
    # bulletin to the governor's term.
    assert by_municipality["jp-local-140007"]["manifesto_source_ids"] == [
        "kanagawa-pref-governor-election-2023-bulletin",
    ]
    # Yokohama City's source is the October 2026 vacancy-election
    # bulletin: Issue #798 registered the promises of the mayor elected
    # in that election from the official bulletin itself.
    assert by_municipality["jp-local-141003"]["manifesto_source_ids"] == [
        "yokohama-city-mayor-election-2026-bulletin",
    ]
    # Kawasaki City's source is the 2025 election bulletin as reprinted
    # in the city election commission's official election record
    # (Chapter 8): the standalone bulletin PDF is not extant because
    # the city's election special site is replaced at each election,
    # but the record reprints the bulletin itself and stays reachable
    # on the official site, so the reprint is registered as the source
    # with its provenance stated in the catalog and evidence packets.
    assert by_municipality["jp-local-141305"]["manifesto_source_ids"] == [
        "kawasaki-city-mayor-election-2025-bulletin",
    ]
    # Saitama Prefecture registers the 2023 bulletin: the promise
    # stage (Issue #822) measured the bulletin PDF (the text layer
    # holds only the election commission's boilerplate; the candidate
    # panels are image-only), transcribed Governor Ono's panel from
    # rendered images at multiple resolutions and connected the
    # bulletin to the governor's term.
    assert by_municipality["jp-local-110001"]["manifesto_source_ids"] == [
        "saitama-pref-governor-election-2023-bulletin",
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
