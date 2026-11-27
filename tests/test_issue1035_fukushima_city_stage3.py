"""Issue #1035: register Fukushima City mayor's election-bulletin promises.

The promises come from the official election bulletin (選挙公報)
issued by the Fukushima City election commission for the 16 November
2025 mayoral election, which elected Baba Yuki.  The bulletin is a
single sheet holding only the three candidate panels (the panels are
images), so the registered texts were transcribed visually from
rendered pages at 200dpi and 300dpi and cross-checked.  The Baba
panel presents three numbered priorities with two check-marked items
each (6 items) and a speech-bubble set of basic-policy keywords
headed 「8つの基本方針」; nine keywords are printed despite the
"eight" in the heading, and all nine are registered as printed.  The
priority titles are topic labels, so following the Okayama City and
Niigata City precedents they are not registered as records of their
own and are kept in source_location; the keyword bubbles have no
sub-items and are themselves the policy statements, so following the
keyword-item precedents they are registered individually.  The panel
carries no past-achievements section (zero exclusions).  The PDF was
re-downloaded from the commission's current official page at stage 3
and its size matched the stage-1 record (3,735,050 bytes; SHA-256
68fc3fd24732db9c7577978404b66137bbcf7485f4cb7865b1c7aae72aa57155).
The source search record itself was already registered at stage 1
(manifesto-source-search-fukushima-city-2025) and is updated here to
reflect the stage-3 completion.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

BULLETIN_ID = "fukushima-city-mayor-election-2025-bulletin"
BULLETIN_URL = (
    "https://www.city.fukushima.fukushima.jp/material/files/group/73/"
    "kouhousityo1109.pdf"
)
SHA256 = "68fc3fd24732db9c7577978404b66137bbcf7485f4cb7865b1c7aae72aa57155"
TERM_ID = "jp-local-072010-executive-2025-12-08"
SEARCH_ID = "manifesto-source-search-fukushima-city-2025"
REVIEW_ID = "manifesto-review-jp-local-072010-2025"

PROJ = "jp-local-072010-project-2025-"

PRIORITY_SECTIONS = [
    "「3つの最優先事項」1「データ行政の確立」",
    "「3つの最優先事項」1「データ行政の確立」",
    "「3つの最優先事項」2「成功体験づくり」",
    "「3つの最優先事項」2「成功体験づくり」",
    "「3つの最優先事項」3「駅前再開発の再整理」",
    "「3つの最優先事項」3「駅前再開発の再整理」",
]

# (original_text, plain_summary, policy_area, linked project suffix,
#  statement_type)
EXPECTED = [
    ("データブックで福島市を見える化",
     "データブックで福島市を見える化する。",
     "fiscal_administrative_reform", "ict-transformation",
     "directional_commitment"),
    ("行政手続きの簡素化",
     "行政手続きを簡素化する。",
     "fiscal_administrative_reform", "ict-transformation",
     "directional_commitment"),
    ("学習センター・支所の強化",
     "学習センター・支所を強化する。",
     "education_and_human_development", "citizen-co-creation",
     "directional_commitment"),
    ("県都として、県と市の連携強化",
     "県都として、県と市の連携を強化する。",
     "fiscal_administrative_reform", None,
     "directional_commitment"),
    ("駅周辺の動線を含めた計画最適化",
     "駅周辺の動線を含めて計画を最適化する。",
     "urban_development_and_tourism", "lively-city",
     "directional_commitment"),
    ("優先整備エリアの段階的完成",
     "優先整備エリアを段階的に完成させる。",
     "urban_development_and_tourism", "lively-city",
     "directional_commitment"),
    ("給食費の無償化",
     "給食費を無償化する。",
     "education_and_human_development", "childcare-education",
     "specific_commitment"),
    ("クマ対策",
     "クマ対策に取り組む。",
     "safety_and_disaster_prevention", None,
     "directional_commitment"),
    ("文化芸術の共創",
     "文化芸術の共創を進める。",
     "urban_development_and_tourism", "culture-arts",
     "directional_commitment"),
    ("メガソーラー",
     "メガソーラーを基本方針の一つとして掲げる。",
     "environment_and_climate", None,
     "directional_commitment"),
    ("シルバーパスポート",
     "シルバーパスポートを基本方針の一つとして掲げる。",
     "health_welfare_and_community", "health-medical-welfare",
     "directional_commitment"),
    ("夜間動物医療体制",
     "夜間動物医療体制を整える。",
     "health_welfare_and_community", None,
     "directional_commitment"),
    ("ゴミ集積所",
     "ゴミ集積所を基本方針の一つとして掲げる。",
     "environment_and_climate", "decarbonization-circular",
     "directional_commitment"),
    ("ママパパ孤独対策",
     "ママパパの孤独対策に取り組む。",
     "childcare_and_childrearing", "childcare-education",
     "directional_commitment"),
    ("防災",
     "防災に取り組む。",
     "safety_and_disaster_prevention", "disaster-measures",
     "directional_commitment"),
]

EXPECTED_LINKS = {
    PROJ + suffix: [
        f"{TERM_ID}-promise-{index:03d}"
        for index, (_, _, _, link, _) in enumerate(EXPECTED, start=1)
        if link == suffix
    ]
    for suffix in {
        link for (_, _, _, link, _) in EXPECTED if link is not None
    }
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


def expected_location(index: int) -> str:
    if index <= 6:
        section = PRIORITY_SECTIONS[index - 1]
        item_no = 1 if index % 2 == 1 else 2
        return f"選挙公報1ページ目・馬場ゆうき候補欄の{section}の項目{item_no}"
    return f"選挙公報1ページ目・馬場ゆうき候補欄の「8つの基本方針」の項目{index - 6}"


def test_fifteen_promises_in_panel_order() -> None:
    records = promises()
    assert len(records) == 15
    for index, (record, expected) in enumerate(
        zip(records, EXPECTED, strict=True), start=1
    ):
        text, summary, area, link, stype = expected
        assert record["id"] == f"{TERM_ID}-promise-{index:03d}"
        assert record["municipality_id"] == "jp-local-072010"
        assert record["original_text"] == text
        assert record["plain_summary"] == summary
        assert record["policy_area"] == area
        assert record["source_location"] == expected_location(index)
        assert record["statement_type"] == stype
        assert record["baseline"] is None
        assert record["target"] is None
        assert record["deadline"] is None
        assert record["funding_statement"] is None
        assert record["change_explanation"] is None
        assert record["progress_state"] == "not_assessable"
        assert record["assessability"] == (
            "assessable" if stype == "specific_commitment"
            else "partially_assessable"
        )
        assert record["controllability"] == "medium"
        assert record["review_status"] == "reviewed"
        assert record["confidence"] == "high"
        assert record["sources"] == [BULLETIN_ID]
        assert record["related_project_ids"] == (
            [PROJ + link] if link else []
        )


def test_policy_area_distribution() -> None:
    counts = Counter(record["policy_area"] for record in promises())
    assert counts == Counter(
        {
            "fiscal_administrative_reform": 3,
            "education_and_human_development": 2,
            "urban_development_and_tourism": 3,
            "safety_and_disaster_prevention": 2,
            "environment_and_climate": 2,
            "health_welfare_and_community": 2,
            "childcare_and_childrearing": 1,
        }
    )


def test_no_fabricated_numbers_and_no_non_promise_text() -> None:
    texts = [record["original_text"] for record in promises()]
    for record in promises():
        assert record["target"] is None
        assert record["deadline"] is None
    joined = "\n".join(texts)
    # Headings, the introductory essay, the Web-policy pointer and
    # the profile tags are not promises; the panel has no
    # past-achievements section at all.
    for fragment in (
        "ともに前へ",
        "安心と挑戦の福島市",
        "危機感を抱きます",
        "衆議院議員を辞し",
        "2000人を超える対話",
        "詳しい政策はWebから",
        "めばえ",
        "福大附属",
        "福高生徒会長",
        "アオウゼ事業統括",
        "こども食堂マイスター",
        "平成初前衆議院議員",
        "データ行政の確立",
        "成功体験づくり",
        "駅前再開発の再整理",
    ):
        assert fragment not in joined
    # The unlinked promises record why no stage-2 measure fits.
    for index in (4, 8, 10, 12):
        record = promises()[index - 1]
        assert record["related_project_ids"] == []
        assert "事業接続は行っていない" in record["extraction_note"]


def test_project_links_bidirectional_and_capped() -> None:
    records = {record["id"]: record for record in promises()}
    linked = [
        record for record in records.values() if record["related_project_ids"]
    ]
    assert len(linked) == 11
    projects = {
        project["id"]: project
        for project in load_json("data/reviewed/fukushima-city/projects.json")
    }
    for project_id, promise_ids in EXPECTED_LINKS.items():
        assert projects[project_id]["related_promise_ids"] == promise_ids
        for promise_id in promise_ids:
            assert records[promise_id]["related_project_ids"] == [project_id]
    packets = packet_index()
    for record in linked:
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
        assert any(
            "low / inferred" in question for question in packet["open_questions"]
        ) or any(
            "公式な対応付け" in question for question in packet["open_questions"]
        )
        assert "low / inferred" in record["extraction_note"]


def test_packets_cover_provenance_and_boundary() -> None:
    packets = packet_index()
    for record in promises():
        packet = packets[record["id"]]
        assert packet["id"] == (
            "evidence-fukushima-city-2025-"
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
        boundary = next(
            claim
            for claim in packet["claims"]
            if claim["field"] == "original_text"
        )
        assert "プロフィールタグ" in boundary["review_note"]
        assert "実績として提示された項目はない" in boundary["review_note"]


def test_bulletin_source_and_term_connection() -> None:
    catalog = load_json("data/catalog/executive_sources.json")
    assert catalog["version"] == "0.69.0"
    assert len(catalog["records"]) == 213
    source = next(
        record for record in catalog["records"] if record["id"] == BULLETIN_ID
    )
    assert source["municipality_key"] == "fukushima-city"
    assert source["organization"] == "福島市選挙管理委員会"
    assert source["category"] == "election"
    assert source["url"] == BULLETIN_URL
    assert source["availability"] == "published"
    assert source["review_status"] == "reviewed"
    assert source["confidence"] == "high"
    assert SHA256 in source["notes"]
    assert "公約レコード15件" in source["notes"]

    terms = load_json("data/entities/executives/executive_terms.json")
    term = next(record for record in terms if record["id"] == TERM_ID)
    assert term["person_name"] == "馬場 雄基"
    assert term["election_date"] == "2025-11-16"
    assert term["term_start"] == "2025-12-08"
    assert term["term_end"] == "2029-12-07"
    assert term["manifesto_source_ids"] == [BULLETIN_ID]
    assert BULLETIN_ID in term["sources"]


def test_search_and_review_records() -> None:
    searches = load_json(
        "data/entities/executives/manifesto_source_searches.json"
    )
    search = next(record for record in searches if record["id"] == SEARCH_ID)
    assert search["executive_term_id"] == TERM_ID
    assert search["result_status"] == "source_registered"
    assert search["manifesto_source_ids_found"] == [BULLETIN_ID]
    assert search["nonexistence_claim"] is False
    assert search["confidence"] == "high"
    assert BULLETIN_ID in search["checked_source_ids"]
    # The stage-1 search record now records the stage-3 completion.
    assert SHA256 in search["review_note"]
    assert "公約レコード15件" in search["review_note"]

    reviews = load_json("data/entities/executives/manifesto_reviews.json")
    review = next(record for record in reviews if record["id"] == REVIEW_ID)
    assert review["executive_term_id"] == TERM_ID
    assert review["source_id"] == BULLETIN_ID
    assert review["candidate_name"] == "馬場 雄基"
    assert review["review_scope"] == "candidate_panel"
    assert review["statement_boundary"] == "mixed"
    assert review["segmentation_status"] == "segmented"
    assert review["promise_records_created"] == 15
    assert "除外した実績項目は0件" in review["review_note"]
    assert "印字されたキーワードは9件" in review["review_note"]

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
    assert all(
        "段階3で行う" not in question
        for question in packet["open_questions"]
    )

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
    assert "除外は0件" in segmentation["review_note"]
    provenance = next(
        claim
        for claim in review_packet["claims"]
        if claim["field"] == "source_provenance"
    )
    assert SHA256 in provenance["statement"]
