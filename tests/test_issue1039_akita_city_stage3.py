"""Issue #1039: register Akita City mayor's election-bulletin promises.

The promises come from the official election bulletin (選挙公報)
issued by the Akita City election commission for the 6 April 2025
mayoral election, which elected Numaya Jun.  The bulletin PDF is
extant on the commission's current official page (「選挙公報」, updated
2026-03-12) and was re-downloaded on 2026-11-27; its size matches the
stage-1 download (1,916,335 bytes, SHA-256
b46d60ade4262414beffb077fbfff1c20c4538ed3471cb337a4effb2e8b9f4d7).
The candidate panels are images with no text layer, so the
registered texts were transcribed visually from rendered pages at
200dpi and 300dpi and cross-checked.  The Numaya panel presents a
headline (「30万都市の復活へ 市民の皆さまとの約束」) with five numbered
promise items, plus a message column and a profile column; following
the Niigata City precedent, the headline, the catch copy, the message
and the profile are not registered as records.  The panel has no
past-achievements section (the candidate was a challenger), so the
number of achievement-based exclusions is zero.  Item 1 combines two
statements in a single numbered item and is kept as one record,
following the boundary printed in the source.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

BULLETIN_ID = "akita-city-mayor-election-2025-bulletin"
BULLETIN_URL = (
    "https://www.city.akita.lg.jp/_res/projects/default_project/"
    "_page_/001/050/242/r07_senkyokouhou_sityousen.pdf"
)
SHA256 = "b46d60ade4262414beffb077fbfff1c20c4538ed3471cb337a4effb2e8b9f4d7"
TERM_ID = "jp-local-052019-executive-2025-04-12"
SEARCH_ID = "manifesto-source-search-akita-city-2025"
REVIEW_ID = "manifesto-review-jp-local-052019-2025"

PROJ = "jp-local-052019-project-2026-"

# (original_text, plain_summary, policy_area, statement_type,
#  assessability, controllability, baseline, target, linked project)
EXPECTED = [
    ("物価高騰などへの家計支援とゴミ袋有料化の検証・見直し",
     "物価高騰などへの家計支援を行い、ゴミ袋有料化を検証し、見直す。",
     "environment_and_climate", "directional_commitment",
     "partially_assessable", "shared", None, None,
     "circular-zero-carbon"),
    ("給食費・医療費・保育料の完全無償化を実現",
     "給食費・医療費・保育料の完全無償化を実現する。",
     "childcare_and_childrearing", "specific_commitment",
     "assessable", "shared", None, None,
     "childcare-support"),
    ("高校生・大学生の地元就職応援金を支給",
     "高校生・大学生に地元就職応援金を支給する。",
     "industry_and_economy", "specific_commitment",
     "assessable", "high", None, None,
     "local-employment"),
    ("年平均3.4件から20件へ企業誘致を現在の5倍に",
     "企業誘致を年平均3.4件から20件へ増やし、現在の5倍にする。",
     "industry_and_economy", "specific_commitment",
     "assessable", "medium", "年平均3.4件", "年20件（現在の5倍）",
     "regional-industry"),
    ("ハード・ソフト両面での防災対策の強化とスピードアップ",
     "ハード・ソフト両面で防災対策を強化し、スピードアップする。",
     "safety_and_disaster_prevention", "directional_commitment",
     "partially_assessable", "high", None, None,
     "disaster-resilience"),
]

EXPECTED_LINKS = {
    PROJ + link: [f"{TERM_ID}-promise-{index:03d}"]
    for index, (*_, link) in enumerate(EXPECTED, start=1)
}


def load_json(relative: str):
    with (ROOT / relative).open(encoding="utf-8") as handle:
        return json.load(handle)


def promises() -> list[dict]:
    return [
        record
        for record in load_json("data/entities/executives/promises.json")
        if record["executive_term_id"] == TERM_ID
    ]


def packet_index() -> dict[str, dict]:
    return {
        packet["subject_id"]: packet
        for packet in load_json(
            "data/entities/executives/promise_evidence_packets.json"
        )
    }


def test_five_promises_in_panel_order() -> None:
    records = promises()
    assert len(records) == 5
    for index, (record, expected) in enumerate(
        zip(records, EXPECTED, strict=True), start=1
    ):
        (text, summary, area, stype, assess, control,
         baseline, target, link) = expected
        assert record["id"] == f"{TERM_ID}-promise-{index:03d}"
        assert record["municipality_id"] == "jp-local-052019"
        assert record["original_text"] == text
        assert record["plain_summary"] == summary
        assert record["policy_area"] == area
        assert record["source_location"] == (
            "選挙公報1ページ目・沼谷純候補欄"
            f"「30万都市の復活へ 市民の皆さまとの約束」の項目{index}"
        )
        assert record["statement_type"] == stype
        assert record["baseline"] == baseline
        assert record["target"] == target
        assert record["deadline"] is None
        assert record["funding_statement"] is None
        assert record["change_explanation"] is None
        assert record["progress_state"] == "not_assessable"
        assert record["assessability"] == assess
        assert record["controllability"] == control
        assert record["review_status"] == "reviewed"
        assert record["confidence"] == "high"
        assert record["sources"] == [BULLETIN_ID]
        assert record["related_project_ids"] == [PROJ + link]


def test_policy_area_distribution() -> None:
    counts = Counter(record["policy_area"] for record in promises())
    assert counts == Counter(
        {
            "environment_and_climate": 1,
            "childcare_and_childrearing": 1,
            "industry_and_economy": 2,
            "safety_and_disaster_prevention": 1,
        }
    )


def test_no_fabricated_numbers_and_no_non_promise_text() -> None:
    texts = [record["original_text"] for record in promises()]
    # Only item 4 carries figures printed in the panel (年平均3.4件,
    # 20件, 5倍); they are recorded as baseline/target of that item
    # only, and no other record invents numbers or deadlines.
    for record in promises():
        assert record["deadline"] is None
        if not record["id"].endswith("promise-004"):
            assert record["baseline"] is None
            assert record["target"] is None
    joined = "\n".join(texts)
    # Headline, catch copy, message column and profile lines are not
    # promises; the rival candidate's panel is not registered either.
    for fragment in (
        "30万都市の復活へ",
        "停滞から、前進へ",
        "市民の皆さまとの約束",
        "私たちが暮らす秋田市は",
        "多選の弊害",
        "政界から引退する覚悟",
        "仁井田小学校",
        "秋田大学教育学部",
        "県議会議員を経て",
        "ほづみもとむ",
        "市民との約束2025",
        "日本一 子育てしやすいまちづくり",
    ):
        assert fragment not in joined
    # Item 1 keeps its two statements in one record, as printed.
    first = promises()[0]
    assert "家計支援" in first["original_text"]
    assert "ゴミ袋有料化の検証・見直し" in first["original_text"]
    assert "1レコードとして保持した" in first["extraction_note"]
    # The household-support half of item 1 has no linked program;
    # the packet records that explicitly.
    packet = packet_index()[first["id"]]
    assert any(
        "この部分は未接続である" in question
        for question in packet["open_questions"]
    )


def test_project_links_bidirectional_and_capped() -> None:
    records = {record["id"]: record for record in promises()}
    projects = {
        project["id"]: project
        for project in load_json("data/reviewed/akita-city/projects.json")
    }
    assert len(projects) == 18
    for project_id, promise_ids in EXPECTED_LINKS.items():
        assert projects[project_id]["related_promise_ids"] == promise_ids
        for promise_id in promise_ids:
            assert records[promise_id]["related_project_ids"] == [project_id]
    for project_id, project in projects.items():
        if project_id not in EXPECTED_LINKS:
            assert project["related_promise_ids"] == []
    packets = packet_index()
    for record in records.values():
        packet = packets[record["id"]]
        link_claims = [
            claim
            for claim in packet["claims"]
            if claim["field"] == "related_project_ids"
        ]
        assert len(link_claims) == 1
        claim = link_claims[0]
        assert claim["decision"] == "needs_review"
        assert "low / inferred" in claim["review_note"]
        assert "low / inferred" in record["extraction_note"]


def test_packets_cover_provenance_and_boundary() -> None:
    packets = packet_index()
    for record in promises():
        packet = packets[record["id"]]
        assert packet["id"] == (
            "evidence-akita-city-2025-"
            + record["id"].removeprefix(TERM_ID + "-")
        )
        assert packet["subject_type"] == "promise"
        assert packet["review_status"] == "reviewed"
        fields = [claim["field"] for claim in packet["claims"]]
        assert "original_text" in fields
        provenance = next(
            claim
            for claim in packet["claims"]
            if claim["field"] == "source_provenance"
        )
        assert SHA256 in provenance["statement"]
        assert "200dpi" in provenance["statement"]
        # The review is the owner's 2026-11-15 delegation to Muse,
        # never the owner's own review.
        assert "所有者本人のレビューではない" in provenance["review_note"]
        boundary = next(
            claim
            for claim in packet["claims"]
            if claim["field"] == "original_text"
        )
        assert "実績の切り分けによる除外は0件" in boundary["review_note"]
        assert "プロフィール欄" in boundary["review_note"]


def test_bulletin_source_and_term_connection() -> None:
    catalog = load_json("data/catalog/executive_sources.json")
    # The bulletin source was already registered at stage 1; stage 3
    # only extends its notes, so the catalog size and version stand.
    assert catalog["version"] == "0.69.0"
    assert len(catalog["records"]) == 213
    source = next(
        record for record in catalog["records"] if record["id"] == BULLETIN_ID
    )
    assert source["municipality_key"] == "akita-city"
    assert source["organization"] == "秋田市選挙管理委員会"
    assert source["category"] == "election"
    assert source["url"] == BULLETIN_URL
    assert source["availability"] == "published"
    assert source["review_status"] == "reviewed"
    assert source["confidence"] == "high"
    assert SHA256 in source["notes"]
    assert "1,916,335バイト" in source["notes"]

    terms = load_json("data/entities/executives/executive_terms.json")
    term = next(record for record in terms if record["id"] == TERM_ID)
    assert term["person_name"] == "沼谷 純"
    assert term["election_date"] == "2025-04-06"
    assert term["term_start"] == "2025-04-12"
    assert term["term_end"] == "2029-04-11"
    assert term["manifesto_source_ids"] == [BULLETIN_ID]
    assert BULLETIN_ID in term["sources"]


def test_search_and_review_records() -> None:
    searches = load_json(
        "data/entities/executives/manifesto_source_searches.json"
    )
    assert len(searches) == 45
    search = next(record for record in searches if record["id"] == SEARCH_ID)
    assert search["executive_term_id"] == TERM_ID
    # Stage 1 left the search follow_up_required; stage 3 closes it.
    assert search["result_status"] == "source_registered"
    assert search["manifesto_source_ids_found"] == [BULLETIN_ID]
    assert search["nonexistence_claim"] is False
    assert search["confidence"] == "high"
    assert BULLETIN_ID in search["checked_source_ids"]
    assert SHA256 in search["review_note"]
    assert "公約レコード5件を作成し" in search["review_note"]

    reviews = load_json("data/entities/executives/manifesto_reviews.json")
    assert len(reviews) == 38
    review = next(record for record in reviews if record["id"] == REVIEW_ID)
    assert review["executive_term_id"] == TERM_ID
    assert review["source_id"] == BULLETIN_ID
    assert review["candidate_name"] == "沼谷 純"
    assert review["review_scope"] == "candidate_panel"
    assert review["statement_boundary"] == "mixed"
    assert review["segmentation_status"] == "segmented"
    assert review["promise_records_created"] == 5
    assert review["last_reviewed_at"] == "2026-11-27"
    assert "除外した実績項目は0件" in review["review_note"]
    assert "分割しなかった" in review["review_note"]

    search_packets = {
        packet["subject_id"]: packet
        for packet in load_json(
            "data/entities/executives/"
            "manifesto_source_search_evidence_packets.json"
        )
    }
    packet = search_packets[SEARCH_ID]
    assert packet["subject_type"] == "manifesto_source_search"
    assert packet["review_status"] == "reviewed"
    status_claim = next(
        claim for claim in packet["claims"] if claim["field"] == "result_status"
    )
    assert "source_registered" in status_claim["statement"]
    assert "所有者本人のレビューではない" in status_claim["review_note"]

    review_packets = {
        packet["subject_id"]: packet
        for packet in load_json(
            "data/entities/executives/manifesto_review_evidence_packets.json"
        )
    }
    review_packet = review_packets[REVIEW_ID]
    assert review_packet["subject_type"] == "manifesto_review"
    segmentation = next(
        claim
        for claim in review_packet["claims"]
        if claim["field"] == "segmentation_status"
    )
    assert "除外は0件" in segmentation["statement"]
    provenance = next(
        claim
        for claim in review_packet["claims"]
        if claim["field"] == "source_provenance"
    )
    assert SHA256 in provenance["statement"]
    assert "所有者本人のレビューではない" in provenance["review_note"]


def test_registry_totals_after_registration() -> None:
    all_promises = load_json("data/entities/executives/promises.json")
    assert len(all_promises) == 580
    packets = load_json(
        "data/entities/executives/promise_evidence_packets.json"
    )
    assert len(packets) == 580
    assert {packet["subject_id"] for packet in packets} == {
        record["id"] for record in all_promises
    }
