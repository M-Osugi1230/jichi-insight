from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

TERM_ID = "jp-local-401005-executive-2023-02-20"
SITE_ID = "kitakyushu-mayor-candidate-2023-official-site"
ARCHIVE_ID = "kitakyushu-mayor-candidate-2023-official-site-archive"
BULLETIN_ID = "kitakyushu-mayor-election-2023-bulletin"
MANIFESTO_ID = "kitakyushu-mayor-candidate-2023-manifesto-v13-archive"

CATALOG_PATHS = [
    "data/catalog/official_sources.json",
    "data/catalog/fukuoka_finance_sources.json",
    "data/catalog/fukuoka_city_finance_sources.json",
    "data/catalog/kitakyushu_finance_sources.json",
    "data/catalog/kitakyushu_project_sources.json",
    "data/catalog/fukuoka_assembly_sources.json",
    "data/catalog/executive_sources.json",
]


def load_json(path: str) -> Any:
    with (ROOT / path).open(encoding="utf-8") as handle:
        return json.load(handle)


def assert_valid(schema_path: str, instance: Any) -> None:
    validator = Draft202012Validator(
        load_json(schema_path),
        format_checker=FormatChecker(),
    )
    errors = list(validator.iter_errors(instance))
    assert errors == [], "; ".join(error.message for error in errors)


def source_ids() -> set[str]:
    return {
        source["id"]
        for path in CATALOG_PATHS
        for source in load_json(path)["records"]
    }


def kitakyushu_search() -> dict[str, Any]:
    searches = load_json("data/entities/executives/manifesto_source_searches.json")
    return next(
        search for search in searches if search["executive_term_id"] == TERM_ID
    )


def test_candidate_manifesto_sources_are_registered() -> None:
    catalog = load_json("data/catalog/executive_sources.json")
    assert_valid("schemas/source_catalog.schema.json", catalog)
    by_id = {record["id"]: record for record in catalog["records"]}

    site = by_id[SITE_ID]
    assert site["url"] == "https://takeuchi-kazuhisa.com/"
    assert site["availability"] == "published"

    archive = by_id[ARCHIVE_ID]
    assert archive["url"] == (
        "https://web.archive.org/web/20230111091207/https://takeuchi-kazuhisa.com/"
    )
    # The archive record must not pretend the manifesto text was verified:
    # it records that the snapshot exists but its text is not yet extracted.
    assert "未実施" in archive["notes"]
    assert "まだ作成していない" in archive["notes"]

    manifesto = by_id[MANIFESTO_ID]
    assert manifesto["url"] == (
        "https://web.archive.org/web/20230111091302/"
        "https://takeuchi-kazuhisa.com/cmsmin/wp-content/uploads/2022/12/"
        "takevision0111_v13_keiryou.pdf"
    )
    assert manifesto["availability"] == "published"
    # The version caveat must stay attached to the source: v13 is the
    # 2023-01-11 published version, the V15 diff is unverified, and v13
    # must not be presented as the final version.
    assert "V15" in manifesto["notes"]
    assert "未検証" in manifesto["notes"]
    assert "最終版とは扱わない" in manifesto["notes"]


def test_followup_search_records_archive_without_overstating() -> None:
    search = kitakyushu_search()
    assert_valid("schemas/manifesto_source_search.schema.json", search)
    assert search["searched_at"] == "2026-11-17"
    assert search["result_status"] == "source_registered"
    assert search["manifesto_source_ids_found"] == [
        BULLETIN_ID,
        SITE_ID,
        ARCHIVE_ID,
        MANIFESTO_ID,
    ]
    assert set(search["checked_source_ids"]) <= source_ids()
    assert search["nonexistence_claim"] is False
    assert search["next_actions"]

    packets = load_json(
        "data/entities/executives/manifesto_source_search_evidence_packets.json"
    )
    packet = next(
        packet for packet in packets if packet["subject_id"] == search["id"]
    )
    assert_valid("schemas/evidence_packet.schema.json", packet)
    assert packet["open_questions"]
    for claim in packet["claims"]:
        assert set(claim["source_ids"]) <= source_ids()


def test_term_manifesto_sources_include_segmented_manifesto() -> None:
    # The term lists manifesto sources whose text extraction and
    # segmentation review are complete. The election bulletin was first;
    # the candidate manifesto (v13) joined it once its full text was
    # extracted from the archived policy PDF and segmented into the
    # 34 small items (manifesto-review-jp-local-401005-2023-v13).
    terms = load_json("data/entities/executives/executive_terms.json")
    term = next(term for term in terms if term["id"] == TERM_ID)
    assert term["manifesto_source_ids"] == [BULLETIN_ID, MANIFESTO_ID]


def test_promise_registry_holds_the_verified_manifesto_items() -> None:
    # Promise records exist only because the primary text was verified
    # against the archived candidate publication; nothing was created
    # from news quotes or third-party summaries. Scoped to this term:
    # the registry also holds other terms' records.
    promises = [
        promise
        for promise in load_json("data/entities/executives/promises.json")
        if promise["executive_term_id"] == TERM_ID
    ]
    packets = load_json("data/entities/executives/promise_evidence_packets.json")
    assert len(promises) == 34
    # One packet per registered promise across all terms:
    # 34 Kitakyushu + 6 Fukuoka City + 9 Fukuoka Prefecture
    # + 10 Aichi Prefecture + 17 Nagoya City (Issue #722)
    # + 13 Sapporo City + 15 Hokkaido Prefecture (Issue #749)
    # + 7 Osaka Prefecture + 5 Osaka City (Issue #772)
    # + 33 Kanagawa Prefecture + 12 Yokohama City
    # + 13 Kawasaki City (Issue #798)
    # + 12 Saitama Prefecture + 26 Kawaguchi City + 12 Saitama City
    # (Issue #822)
    # + 25 Chiba Prefecture + 25 Chiba City (Issue #842)
    # + 18 Hyogo Prefecture and 28 Kobe City (Issue #862)
    # + 4 Miyagi Prefecture and 4 Sendai City (Issue #881)
    # + 9 Shizuoka Prefecture, 10 Hamamatsu City and 3 Shizuoka
    # City (Issue #900)
    # + 14 Hiroshima Prefecture and 14 Hiroshima City (Issue #921)
    # + 29 Kyoto Prefecture and + 38 Kyoto City (Issue #938)
    # + 17 Niigata City (Issue #973)
    # + 21 Okayama City (Issue #974)
    # + 9 Kumamoto City (Issue #975)
    # + 5 Akita City (Issue #1039)
    # + 15 Fukushima City (Issue #1035)
    # + 7 Yamagata City (Issue #1037)
    # + 11 Yamagata Prefecture (Issue #1036)
    # + 15 Akita Prefecture (Issue #1038)
    # + 35 Fukushima Prefecture (Issue #1034)
    # + 6 Iwate Prefecture (Issue #1086)
    # + 11 Aomori Prefecture (Issue #1087).
    assert len(packets) == 597
    for promise in promises:
        assert promise["sources"] == [MANIFESTO_ID]


def test_promise_records_and_project_links_are_consistent() -> None:
    all_promises = load_json("data/entities/executives/promises.json")
    promises = [
        promise
        for promise in all_promises
        if promise["executive_term_id"] == TERM_ID
    ]
    promise_ids = {promise["id"] for promise in promises}
    packets = [
        packet
        for packet in load_json(
            "data/entities/executives/promise_evidence_packets.json"
        )
        if packet["subject_id"] in promise_ids
    ]
    projects = load_json("data/reviewed/kitakyushu-city/projects.json")
    known_sources = source_ids()

    projects_by_id = {project["id"]: project for project in projects}
    promises_by_id = {promise["id"]: promise for promise in promises}

    for promise in promises:
        assert_valid("schemas/promise.schema.json", promise)
        assert promise["executive_term_id"] == TERM_ID
        assert set(promise["sources"]) <= known_sources
        for project_id in promise["related_project_ids"]:
            assert project_id in projects_by_id
            assert promise["id"] in projects_by_id[project_id]["related_promise_ids"]

    for packet in packets:
        assert_valid("schemas/evidence_packet.schema.json", packet)
        assert packet["subject_type"] == "promise"
        assert packet["subject_id"] in promises_by_id

    for project in projects:
        for promise_id in project["related_promise_ids"]:
            assert promise_id in promises_by_id
            assert project["id"] in promises_by_id[promise_id]["related_project_ids"]
