"""Issue #975: Kumamoto governor manifesto source search (cluster 15, stage 3).

The 2024 Kumamoto gubernatorial election bulletin was issued
and distributed on paper from 2024-03-11 (Kuma Village election
commission's official page), and it was also viewable on the
Kumamoto Prefectural Election Commission's website during the
election period (the Ozu Town and Koshi City election
commissions' official pages both state this). The
election-period commission pages (soshiki/147/198406.html and
198564.html, linked from the Ozu Town page) have since been
deleted from the live site (404 as of 2026-11-23), the current
results page carries no bulletin link, and no archived copy of
the bulletin text could be located: the National Diet Library's
WARP holds captures of the prefecture's election pages but not
of the two election-period pages or the bulletin PDF (the
prefecture-domain bulletin corpus was checked in full), the
municipal pages preserved in WARP carry no bulletin text,
archive.today holds no snapshot, the Wayback Machine could not
be reached from the search environment (403) and the Common
Crawl index did not respond (504), so their holdings remain
unverified. The candidate's own website (kimura-takashi.jp,
named in the gazette's candidate-filing notice) is not an
election-commission publication and is not adopted as a
primary source, and neither are press questionnaires. The
search is therefore registered as
no_stable_primary_source_found with nonexistence_claim false,
and no promise records are created for the term.

The proclamation date, left open at stage 1, is now confirmed
directly in the prefectural gazette: Kumamoto Prefecture
Gazette extra no. 10 (2024-03-07), election commission notice
no. 5, fixes the election day at 2024-03-24 and is dated
2024-03-07 (5 pages, 889,024 bytes, SHA-256
e4908e03ab2aeb6894e4b4dbb7483eb88d96c96815e8fe7ebfcacd7a73480880).
Extra no. 12 of the same day carries the returning officer's
notice no. 2 listing the four candidates in filing order
(Miyagawa Kazuhiko, Koyama Seishi, Mouri Hidenori, Kimura
Takashi), all filed on 2024-03-07, which matches the
commission's official ballot-count document. The gazette is
registered as a source and the term packet records the
proclamation claim.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

MUNICIPALITY_ID = "jp-local-430005"
TERM_ID = "jp-local-430005-executive-2024-04-16"
SEARCH_ID = "manifesto-source-search-kumamoto-pref-2024"
SEARCH_PACKET_ID = "evidence-manifesto-source-search-kumamoto-pref-2024"
GAZETTE_ID = "kumamoto-pref-governor-election-2024-gazette"
TERM_PACKET_ID = "evidence-kumamoto-pref-current-governor-term"


def load_json(path: str) -> Any:
    with (ROOT / path).open(encoding="utf-8") as handle:
        return json.load(handle)


def validation_errors(schema_path: str, instance: Any) -> list[str]:
    validator = Draft202012Validator(
        load_json(schema_path),
        format_checker=FormatChecker(),
    )
    return [error.message for error in validator.iter_errors(instance)]


def test_gazette_source_is_registered() -> None:
    catalog = load_json("data/catalog/executive_sources.json")
    assert validation_errors("schemas/source_catalog.schema.json", catalog) == []
    # The catalog stands at version 0.57.0 / 169 records: the
    # Niigata stage-3 registration (issue #973) added three records
    # over the stage-2 baseline (0.55.0 / 165) and this gazette
    # record adds one more.
    assert catalog["version"] == "0.57.0"
    assert len(catalog["records"]) == 169
    assert len({record["id"] for record in catalog["records"]}) == 169

    gazette = next(r for r in catalog["records"] if r["id"] == GAZETTE_ID)
    assert gazette["municipality_key"] == "kumamoto-prefecture"
    assert gazette["organization"] == "熊本県選挙管理委員会"
    assert gazette["category"] == "election"
    assert gazette["title"] == "熊本県公報 号外第10号（令和6年3月7日）"
    assert gazette["url"] == (
        "https://www.pref.kumamoto.jp/uploaded/attachment/242106.pdf"
    )
    assert gazette["review_status"] == "reviewed"
    assert gazette["confidence"] == "high"
    # The notes pin the document facts verified against the PDF
    # itself and the same-day candidate-filing notice.
    assert "889,024バイト" in gazette["notes"]
    assert (
        "e4908e03ab2aeb6894e4b4dbb7483eb88d96c96815e8fe7ebfcacd7a73480880"
        in gazette["notes"]
    )
    assert "告示第5号" in gazette["notes"]
    assert "242244.pdf" in gazette["notes"]


def test_search_is_registered_as_no_stable_primary_source() -> None:
    searches = load_json("data/entities/executives/manifesto_source_searches.json")
    assert len(searches) == 34
    search = next(s for s in searches if s["id"] == SEARCH_ID)
    assert validation_errors("schemas/manifesto_source_search.schema.json", search) == []
    assert search["executive_term_id"] == TERM_ID
    assert search["searched_at"] == "2026-11-23"
    assert search["result_status"] == "no_stable_primary_source_found"
    assert search["manifesto_source_ids_found"] == []
    # The safety boundary: a search that found no source must not
    # claim the source does not exist.
    assert search["nonexistence_claim"] is False
    assert search["review_status"] == "reviewed"
    assert set(search["checked_source_ids"]) == {
        "kumamoto-pref-governor",
        "kumamoto-pref-term-list",
        "kumamoto-pref-governor-election-2024-ballot-count",
        "kumamoto-pref-governor-election-2024-turnout",
        "kumamoto-pref-governor-inauguration-2024",
        GAZETTE_ID,
    }
    # The review note records both halves of the finding: the
    # bulletin was published online during the election period,
    # and no verifiable copy survives in the archives checked.
    assert "大津町" in search["review_note"]
    assert "WARP" in search["review_note"]
    assert "Wayback Machine" in search["review_note"]
    assert "公約は未登録" in search["review_note"]
    assert search["next_actions"]


def test_search_evidence_packet_is_complete() -> None:
    packets = load_json(
        "data/entities/executives/manifesto_source_search_evidence_packets.json"
    )
    assert len(packets) == 34
    packet = next(p for p in packets if p["id"] == SEARCH_PACKET_ID)
    assert validation_errors("schemas/evidence_packet.schema.json", packet) == []
    assert packet["subject_type"] == "manifesto_source_search"
    assert packet["subject_id"] == SEARCH_ID
    assert {claim["field"] for claim in packet["claims"]} == {
        "checked_source_ids",
        "manifesto_source_ids_found",
        "result_status",
    }
    assert all(claim["decision"] == "accepted" for claim in packet["claims"])
    # The unverified archive routes stay open, per project rules.
    assert packet["open_questions"]
    assert any("Wayback Machine" in q for q in packet["open_questions"])


def test_no_promises_or_review_are_created_for_the_term() -> None:
    promises = load_json("data/entities/executives/promises.json")
    assert len(promises) == 445
    assert all(p["executive_term_id"] != TERM_ID for p in promises)

    reviews = load_json("data/entities/executives/manifesto_reviews.json")
    assert len(reviews) == 29
    assert all(r["executive_term_id"] != TERM_ID for r in reviews)

    terms = load_json("data/entities/executives/executive_terms.json")
    term = next(t for t in terms if t["id"] == TERM_ID)
    assert term["municipality_id"] == MUNICIPALITY_ID
    # No manifesto source is connected: the bulletin could not be
    # secured as a verifiable primary source.
    assert term["manifesto_source_ids"] == []
    assert GAZETTE_ID in term["sources"]


def test_term_packet_records_proclamation_and_keeps_bulletin_open() -> None:
    packets = load_json("data/entities/executives/evidence_packets.json")
    packet = next(p for p in packets if p["id"] == TERM_PACKET_ID)
    assert validation_errors("schemas/evidence_packet.schema.json", packet) == []

    proclamation = next(
        c for c in packet["claims"] if c["field"] == "election_proclamation_date"
    )
    assert proclamation["source_ids"] == [GAZETTE_ID]
    assert proclamation["decision"] == "accepted"
    assert "2024年3月7日" in proclamation["statement"]
    assert "告示第5号" in proclamation["statement"]
    # The candidate set in the gazette filing notice matches the
    # commission's official ballot-count document.
    assert "宮川一彦・幸山政史・毛利秀徳・きむら敬" in proclamation["statement"]

    # The stage-1 proclamation question is resolved; only the
    # bulletin question remains, updated with the stage-3 outcome.
    assert len(packet["open_questions"]) == 1
    question = packet["open_questions"][0]
    assert "no_stable_primary_source_found" in question
    assert "manifesto_source_ids" in question
