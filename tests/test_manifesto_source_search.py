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

    assert len(searches) == 41
    assert {search["executive_term_id"] for search in searches} == {
        "jp-local-062014-executive-2023-09-28",
        "jp-local-400009-executive-2025-04-14",
        "jp-local-401307-executive-2022-12-07",
        "jp-local-401005-executive-2023-02-20",
        "jp-local-230006-executive-2023-02-15",
        "jp-local-231002-executive-2024-11-24",
        "jp-local-232114-executive-2024-02-19",
        "jp-local-012041-executive-2025-09-26",
        "jp-local-011002-executive-2023-05-02",
        "jp-local-010006-executive-2023-04-23",
        "jp-local-270008-executive-2023-04-09",
        "jp-local-271004-executive-2026-02-09",
        "jp-local-271403-executive-2023-06-09",
        "jp-local-141003-executive-2026-10-18",
        "jp-local-140007-executive-2023-04-23",
        "jp-local-141305-executive-2025-11-19",
        "jp-local-110001-executive-2023-08-31",
        "jp-local-111007-executive-2025-05-27",
        "jp-local-112038-executive-2026-02-09",
        "jp-local-120006-executive-2025-04-05",
        "jp-local-121002-executive-2025-03-21",
        "jp-local-280003-executive-2024-11-17",
        "jp-local-281000-executive-2025-11-20",
        "jp-local-041009-executive-2025-08-22",
        "jp-local-040002-executive-2025-11-21",
        "jp-local-220001-executive-2024-05-26",
        "jp-local-221309-executive-2023-05-01",
        "jp-local-221007-executive-2023-04-13",
        "jp-local-341002-executive-2023-04-12",
        "jp-local-340006-executive-2025-11-29",
        "jp-local-260002-executive-2026-04-16",
        "jp-local-261009-executive-2024-02-25",
        "jp-local-330001-executive-2024-11-12",
        "jp-local-150002-executive-2026-06-10",
        "jp-local-151009-executive-2026-11-18",
        "jp-local-331007-executive-2025-10-09",
        "jp-local-431001-executive-2026-12-03",
        "jp-local-430005-executive-2024-04-16",
        "jp-local-052019-executive-2025-04-12",
        "jp-local-050008-executive-2025-04-20",
        "jp-local-072010-executive-2025-12-08",
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
    # Thirty-two searches have registered a primary source (Fukuoka
    # Prefecture, Fukuoka City, Kitakyushu City, Aichi Prefecture,
    # Nagoya City, Sapporo City, Hokkaido, Osaka Prefecture, Osaka
    # City, Kanagawa Prefecture, Yokohama City, Kawasaki City,
    # Saitama Prefecture, Saitama City, Kawaguchi City, Chiba
    # Prefecture, Chiba City, Hyogo Prefecture, Kobe City,
    # Miyagi Prefecture, Sendai City, Shizuoka Prefecture,
    # Hamamatsu City, Shizuoka City, Hiroshima Prefecture,
    # Hiroshima City, Kyoto Prefecture, Kyoto City, Niigata City,
    # Okayama City, Kumamoto City and Yamagata City, each closed by its
    # official election bulletin (the Sendai, Shizuoka City,
    # Hiroshima City and Kumamoto City bulletins survive only as archived copies
    # of the cities' official election-period URLs; the Akita
    # Prefecture bulletin survives as a copy on the Yurihonjo City
    # official site, proven byte-identical to the Wayback Machine
    # capture of that copy taken on 2025-05-15; the Okayama
    # City bulletin survives as a CDN copy proven byte-identical
    # to the archived capture of the city's official URL by a
    # SHA-1 digest match; the Yamagata City bulletin survives as
    # a CDN copy whose content was verified against the official
    # election page and result report after the city's official
    # PDF was removed (no archived capture of the official URL
    # survives, so no digest match was possible); the Kyoto
    # Prefecture bulletin is registered as the candidate-submitted
    # manuscript published as audio-readable data);
    # Kawasaki's bulletin is registered as reprinted in the city
    # election commission's official election record).
    # Six searches remain exceptions:
    # Toyota City (the 2024 bulletin is not extant as an official web
    # publication), Asahikawa City (the 2025 bulletin has no official
    # web publication), Sakai City (the 2023 bulletin has no official
    # web publication), Okayama Prefecture (the 2024 bulletin was
    # published on the election commission's homepage during the
    # election, but the current official page no longer links to it,
    # the election special site is unreachable, the commission's
    # official election report reprints only the bulletin's covers,
    # and the stage-3 archive re-check could not be completed) and
    # Niigata Prefecture (the 2026 bulletin was
    # distributed on paper only; the commission's election record is
    # still in preparation and no archived copy of the official
    # election-period sites survives) and Kumamoto Prefecture (the
    # 2024 bulletin was published on the election commission's
    # website during the election period, but the pages were
    # deleted and no archived copy of the bulletin page itself
    # could be located in the Wayback Machine, the National Diet
    # Library's WARP or the other archives checked); in all six
    # cases no verifiable
    # candidate publication was found, so their terms register no
    # manifesto source. The safety invariant still applies to any
    # record that reports no source: it must not claim found sources.
    assert len(missing) == 6
    assert {search["executive_term_id"] for search in missing} == {
        "jp-local-232114-executive-2024-02-19",
        "jp-local-012041-executive-2025-09-26",
        "jp-local-271403-executive-2023-06-09",
        "jp-local-330001-executive-2024-11-12",
        "jp-local-150002-executive-2026-06-10",
        "jp-local-430005-executive-2024-04-16",
    }
    assert all(search["manifesto_source_ids_found"] == [] for search in missing)

    prefecture = next(
        search
        for search in searches
        if search["executive_term_id"] == "jp-local-400009-executive-2025-04-14"
    )
    assert prefecture["result_status"] == "source_registered"
    assert prefecture["manifesto_source_ids_found"] == [
        "fukuoka-pref-governor-election-2025-bulletin",
    ]

    registered = next(
        search
        for search in searches
        if search["executive_term_id"] == "jp-local-401005-executive-2023-02-20"
    )
    assert registered["result_status"] == "source_registered"
    assert registered["manifesto_source_ids_found"] == [
        "kitakyushu-mayor-election-2023-bulletin",
        "kitakyushu-mayor-candidate-2023-official-site",
        "kitakyushu-mayor-candidate-2023-official-site-archive",
        "kitakyushu-mayor-candidate-2023-manifesto-v13-archive",
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

    # Kumamoto City's 2026 search (Issue #975) references the term
    # starting 2026-12-03, which is registered only once it starts
    # (Issue #706); until then it is the single permitted forward
    # reference.
    pending_term_ids = {"jp-local-431001-executive-2026-12-03"}
    assert {search["executive_term_id"] for search in searches} <= (
        term_ids | pending_term_ids
    )
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
