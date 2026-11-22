"""Issue #974: Okayama cluster stage 3 — Okayama Prefecture governor.

Stage 3 re-checked the 2024 gubernatorial election bulletin for
Governor Ibaragi Ryuta's current term (2024-11-12 to 2028-11-11).
The bulletin was issued and was published on the prefectural
election commission's homepage during the election — the
commission's official election report (結果調, August 2025) records
in Chapter "5 選挙公報" that both candidates applied, 787,000
copies were printed, and the bulletin was posted on the commission
homepage from about 22:00 on 11 October 2024. But the report
reprints only the bulletin's covers (the voting-hours guidance
faces), not the candidates' manuscript pages; the commission's
current election page carries no bulletin link; the election
special site (kentijisenkyor6.pref.okayama.jp) is unreachable; and
web searches located no 2024 bulletin PDF or page (the 2020
bulletin page, by contrast, is still live on the official site).
The stage-3 archive re-check (Wayback Machine and other web
archives) could not be completed through the available route —
the archives returned no usable response — so the survival of an
archived copy remains undetermined rather than disproven.

Following the Toyota City, Asahikawa City and Sakai City
precedents, the search record is therefore closed as
no_stable_primary_source_found: no manifesto source is connected
to the term and no promise records are created. This records an
unlocated source, not a claim that no manifesto exists
(nonexistence_claim stays false), and the next actions keep the
re-check routes open.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

TERM_ID = "jp-local-330001-executive-2024-11-12"
SEARCH_ID = "manifesto-source-search-okayama-pref-2024"
PACKET_ID = "evidence-manifesto-source-search-okayama-pref-2024"
REPORT_SOURCE_ID = "okayama-pref-governor-election-2024-report"


def load_json(path: str) -> Any:
    with (ROOT / path).open(encoding="utf-8") as handle:
        return json.load(handle)


def okayama_term() -> dict[str, Any]:
    terms = load_json("data/entities/executives/executive_terms.json")
    matches = [term for term in terms if term["id"] == TERM_ID]
    assert len(matches) == 1
    return matches[0]


def okayama_search() -> dict[str, Any]:
    searches = load_json("data/entities/executives/manifesto_source_searches.json")
    matches = [s for s in searches if s["id"] == SEARCH_ID]
    assert len(matches) == 1
    return matches[0]


def test_governor_term_registers_no_manifesto_source_or_promises() -> None:
    term = okayama_term()

    assert term["municipality_id"] == "jp-local-330001"
    assert term["office"] == "governor"
    assert term["person_name"] == "伊原木 隆太"
    assert term["term_start"] == "2024-11-12"
    assert term["term_end"] == "2028-11-11"
    # No verifiable primary source for the 2024 promises was
    # located, so the term stays unconnected and its stage-1
    # source list is untouched by stage 3.
    assert term["manifesto_source_ids"] == []
    assert term["sources"] == [
        "okayama-pref-governor-proposal-2025",
        "okayama-pref-term-list",
        "okayama-pref-governor-election-2024-results",
        "okayama-pref-governor-election-2024-overview",
        "okayama-pref-governor-election-2024",
    ]

    promises = load_json("data/entities/executives/promises.json")
    assert [p for p in promises if p["executive_term_id"] == TERM_ID] == []
    # The Okayama governor registration itself created no promise
    # records. (The registry total has since grown through other
    # municipalities' stage-3 registrations.)
    assert len(promises) == 492

    reviews = load_json("data/entities/executives/manifesto_reviews.json")
    assert [r for r in reviews if r["executive_term_id"] == TERM_ID] == []


def test_search_record_is_closed_as_no_stable_primary_source_found() -> None:
    search = okayama_search()

    assert search["executive_term_id"] == TERM_ID
    assert search["searched_at"] == "2026-11-23"
    assert search["result_status"] == "no_stable_primary_source_found"
    assert search["manifesto_source_ids_found"] == []
    assert search["nonexistence_claim"] is False
    assert search["review_status"] == "reviewed"
    assert search["confidence"] == "high"
    # The official election report was added to the checked sources
    # in stage 3; every checked source must be a registered one.
    assert REPORT_SOURCE_ID in search["checked_source_ids"]
    assert len(search["checked_source_ids"]) == 6

    note = search["review_note"]
    # The report proves issuance and election-period homepage
    # publication, but reprints only the bulletin's covers.
    assert "結果調" in note
    assert "787,000部" in note
    assert "表紙・裏表紙" in note
    # The special site is unreachable and no bulletin PDF or page
    # was located by web search.
    assert "kentijisenkyor6.pref.okayama.jp" in note
    assert "到達不可" in note
    # The archive re-check is honestly recorded as incomplete,
    # never as a completed negative.
    assert "完遂して確認できていない" in note
    # Private mirrors and press questionnaires are not primary
    # sources, and the outcome is not a nonexistence claim.
    assert "原典として採用しない" in note
    assert "公約が存在しないという主張ではない" in note

    actions = " ".join(search["next_actions"])
    assert "Wayback Machine" in actions
    assert "紙の選挙公報" in actions
    assert "音声読み上げ対応データ" in actions
    assert "2028年" in actions


def test_search_evidence_packet_records_the_stage3_basis() -> None:
    packets = load_json(
        "data/entities/executives/manifesto_source_search_evidence_packets.json"
    )
    matches = [p for p in packets if p["id"] == PACKET_ID]
    assert len(matches) == 1
    packet = matches[0]

    assert packet["subject_type"] == "manifesto_source_search"
    assert packet["subject_id"] == SEARCH_ID
    assert packet["review_status"] == "reviewed"
    assert {claim["field"] for claim in packet["claims"]} == {
        "checked_source_ids",
        "manifesto_source_ids_found",
        "result_status",
    }
    assert all(claim["decision"] == "accepted" for claim in packet["claims"])

    found_claim = next(
        claim for claim in packet["claims"] if claim["field"] == "manifesto_source_ids_found"
    )
    assert found_claim["source_ids"] == [REPORT_SOURCE_ID]
    assert "787,000部" in found_claim["statement"]

    status_claim = next(
        claim for claim in packet["claims"] if claim["field"] == "result_status"
    )
    assert "no_stable_primary_source_found" in status_claim["statement"]

    questions = " ".join(packet["open_questions"])
    assert "音声読み上げ対応データ" in questions
    assert "Webアーカイブ" in questions
    assert "紙の選挙公報" in questions


def test_election_report_source_is_registered_in_the_catalog() -> None:
    catalog = load_json("data/catalog/executive_sources.json")

    # The stage-3 registration of the election report is the only
    # catalog addition: version 0.60.0 / 172 records.
    assert catalog["version"] == "0.60.0"
    assert len(catalog["records"]) == 172
    assert len({record["id"] for record in catalog["records"]}) == 172

    matches = [r for r in catalog["records"] if r["id"] == REPORT_SOURCE_ID]
    assert len(matches) == 1
    source = matches[0]
    assert source["municipality_key"] == "okayama-prefecture"
    assert source["organization"] == "岡山県選挙管理委員会"
    assert source["category"] == "election"
    assert (
        source["url"]
        == "https://www.pref.okayama.lg.jp/uploaded/life/993819_9575903_misc.pdf"
    )
    assert source["source_kind"] == "document"
    assert source["availability"] == "published"
    assert source["review_status"] == "reviewed"
    assert source["confidence"] == "high"
    # The catalog note itself states the limit of the evidence:
    # the report reprints the covers only, never the candidates'
    # manuscript pages.
    assert "候補者の原稿面は再録されていない" in source["notes"]
