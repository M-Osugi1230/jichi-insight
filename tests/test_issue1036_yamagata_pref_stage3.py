"""Issue #1036: register Yamagata governor's election-bulletin promises.

The promises come from the official election bulletin (選挙公報) for
the 26 January 2025 Yamagata gubernatorial election, which
re-elected Yoshimura Mieko.  The bulletin itself is not published
as a standalone file; it survives as reprinted verbatim in part 6
(「6 選挙公報」, printed pages 104-105) of the prefectural election
commission's official election record (『山形県知事選挙及び山形県
議会議員補欠選挙の記録』), whose PDF is served from the
prefecture's current official site.  The candidate panels are
images with no text layer, so the registered texts were transcribed
visually from rendered pages at 200dpi and 300dpi and
cross-checked.  The panel presents five "challenges" with 11 bullet
items, plus a profile section (career and family) that is excluded
from the promise records; the panel carries no past-achievements
section.  The challenge headlines are slogan-style topic labels,
so following the Kyoto City and Niigata City precedent they are not
registered as records of their own and are kept in source_location.
The stage-3 download of the part-6 PDF is recorded by SHA-256
50380a71b65b21479e9b4ffb3db24d4f5fff99d538530401829ffdc6c85f30be
(3,217,787 bytes, 18 pages for the whole part 6).
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

BULLETIN_ID = "yamagata-pref-governor-election-2025-bulletin"
BULLETIN_URL = "https://www.pref.yamagata.jp/documents/44535/06_r7chiji_6hen.pdf"
SHA256 = "50380a71b65b21479e9b4ffb3db24d4f5fff99d538530401829ffdc6c85f30be"
TERM_ID = "jp-local-060003-executive-2025-02-14"
SEARCH_ID = "manifesto-source-search-yamagata-pref-2025"
REVIEW_ID = "manifesto-review-jp-local-060003-2025"

PROJ = "jp-local-060003-project-2025-"

CHALLENGES = [
    "チャレンジ1「県民が幸せを実感できる山形県」",
    "チャレンジ2「安全安心に暮らせる山形県」",
    "チャレンジ3「誰もがいきいきと働ける山形県」",
    "チャレンジ4「関係人口と交流人口の拡大による元気な山形県」",
    "チャレンジ5「県民一人ひとりが輝く山形県」",
]
# (challenge index, item number within the challenge)
POSITIONS = [
    (1, 1), (1, 2),
    (2, 1), (2, 2), (2, 3),
    (3, 1), (3, 2),
    (4, 1), (4, 2),
    (5, 1), (5, 2),
]

# (original_text, plain_summary, policy_area, statement_type,
#  linked project suffix)
EXPECTED = [
    ("県立博物館の移転整備",
     "県立博物館の移転整備を行う。",
     "education_and_human_development", "specific_commitment",
     "lifelong-learning"),
    ("子育てに要する経済的負担の軽減（出産費用、保育料、高校授業料など）",
     "出産費用、保育料、高校授業料など、子育てに要する経済的負担を軽減する。",
     "childcare_and_childrearing", "directional_commitment", None),
    ("令和6年7月の豪雨災害からの迅速な復旧・復興",
     "令和6年7月の豪雨災害から迅速な復旧・復興を進める。",
     "safety_and_disaster_prevention", "directional_commitment",
     "crisis-management"),
    ("「未来に伝える山形の宝」事業を拡大し、市町村のコミュニティ維持政策の実行支援",
     "「未来に伝える山形の宝」事業を拡大し、市町村のコミュニティ維持政策の実行を支援する。",
     "health_welfare_and_community", "specific_commitment", None),
    ("米沢トンネル（仮称）の実現に尽力",
     "米沢トンネル（仮称）の実現に尽力する。",
     "transport_infrastructure", "specific_commitment",
     "transport-network"),
    ("スタートアップ支援・事業承継支援",
     "スタートアップ支援と事業承継支援を行う。",
     "industry_and_economy", "directional_commitment",
     "regional-industry-sme-growth"),
    ("地域農業を支える多様な担い手の育成・確保（若者、女性、半農半Xなど）",
     "若者、女性、半農半Xなど、地域農業を支える多様な担い手を育成・確保する。",
     "industry_and_economy", "directional_commitment",
     "agricultural-workforce-foundation"),
    ("庄内空港・山形空港の滑走路延長等の機能強化による県内誘客の促進",
     "庄内空港・山形空港の滑走路延長等の機能強化により、県内への誘客を促進する。",
     "transport_infrastructure", "specific_commitment",
     "transport-network"),
    ("農業や医療・福祉などの関係機関との連携による「職」「住」セットの移住マッチングの推進",
     "農業や医療・福祉などの関係機関との連携により、「職」と「住」をセットにした移住マッチングを推進する。",
     "urban_development_and_tourism", "directional_commitment", None),
    ("多文化共生社会の実現（外国人材の受入れ・定着の拡大）",
     "外国人材の受入れ・定着の拡大により、多文化共生社会を実現する。",
     "universal_city_and_inclusion", "directional_commitment", None),
    ("高齢者の活躍促進（生涯現役の実現）",
     "生涯現役の実現に向け、高齢者の活躍を促進する。",
     "health_welfare_and_community", "directional_commitment", None),
]

EXPECTED_LINKS = {
    PROJ + suffix: [
        f"{TERM_ID}-promise-{index:03d}"
        for index, (_, _, _, _, link) in enumerate(EXPECTED, start=1)
        if link == suffix
    ]
    for suffix in {
        link for (_, _, _, _, link) in EXPECTED if link is not None
    }
}


def load_json(relative: str) -> Any:
    with (ROOT / relative).open(encoding="utf-8") as handle:
        return json.load(handle)


def assert_valid(schema_path: str, instance: Any) -> None:
    validator = Draft202012Validator(
        load_json(schema_path),
        format_checker=FormatChecker(),
    )
    errors = list(validator.iter_errors(instance))
    assert errors == [], "; ".join(error.message for error in errors)


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


def test_eleven_promises_in_panel_order() -> None:
    records = promises()
    assert len(records) == 11
    for index, (record, expected, position) in enumerate(
        zip(records, EXPECTED, POSITIONS, strict=True), start=1
    ):
        text, summary, area, statement_type, link = expected
        challenge, item_no = position
        assert record["id"] == f"{TERM_ID}-promise-{index:03d}"
        assert record["municipality_id"] == "jp-local-060003"
        assert record["original_text"] == text
        assert record["plain_summary"] == summary
        assert record["policy_area"] == area
        assert record["statement_type"] == statement_type
        assert record["source_location"] == (
            "選挙公報104ページ（『選挙の記録』第6編「6 選挙公報」）・"
            f"吉村みえこ候補欄の{CHALLENGES[challenge - 1]}の項目{item_no}"
        )
        assert record["baseline"] is None
        assert record["target"] is None
        assert record["deadline"] is None
        assert record["funding_statement"] is None
        assert record["change_explanation"] is None
        assert record["progress_state"] == "not_assessable"
        assert record["assessability"] == "partially_assessable"
        assert record["controllability"] == "medium"
        assert record["review_status"] == "reviewed"
        assert record["confidence"] == "high"
        assert record["sources"] == [BULLETIN_ID]
        assert record["related_project_ids"] == (
            [PROJ + link] if link else []
        )
        assert_valid("schemas/promise.schema.json", record)


def test_totals_grew_by_eleven() -> None:
    all_promises = load_json("data/entities/executives/promises.json")
    assert len(all_promises) == 530
    packets = load_json("data/entities/executives/promise_evidence_packets.json")
    assert len(packets) == 530


def test_policy_area_distribution() -> None:
    counts = Counter(record["policy_area"] for record in promises())
    assert counts == Counter(
        {
            "education_and_human_development": 1,
            "childcare_and_childrearing": 1,
            "safety_and_disaster_prevention": 1,
            "health_welfare_and_community": 2,
            "transport_infrastructure": 2,
            "industry_and_economy": 2,
            "urban_development_and_tourism": 1,
            "universal_city_and_inclusion": 1,
        }
    )


def test_no_fabricated_numbers_and_no_profile_text() -> None:
    texts = [record["original_text"] for record in promises()]
    # No item carries its own numeric target, deadline or funding
    # statement; the only date in the panel's items (令和6年7月)
    # identifies the disaster being recovered from, not a deadline.
    for record in promises():
        assert record["target"] is None
        assert record["deadline"] is None
        assert record["funding_statement"] is None
    joined = "\n".join(texts)
    # Headlines, slogan, header copy and profile lines are not
    # promises; the other candidate's panel is not registered.
    for fragment in (
        "チャレンジ5.0",
        "県民の皆様の幸せ、県土発展のために",
        "県民の皆様とともに",
        "お茶の水女子大学",
        "行政書士",
        "大江町",
        "現在4期目",
        "長男家族と同居",
        "金山",
    ):
        assert fragment not in joined
    # The unlinked promises record why no stage-2 policy fits.
    for index in (2, 4, 9, 10, 11):
        record = promises()[index - 1]
        assert record["related_project_ids"] == []
        assert "事業接続は行っていない" in record["extraction_note"]


def test_project_links_bidirectional_and_capped() -> None:
    records = {record["id"]: record for record in promises()}
    linked = [
        record for record in records.values() if record["related_project_ids"]
    ]
    assert len(linked) == 6
    projects = {
        project["id"]: project
        for project in load_json("data/reviewed/yamagata-prefecture/projects.json")
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
            "公式な対応付け" in question for question in packet["open_questions"]
        )
        assert "low / inferred" in record["extraction_note"]


def test_packets_cover_provenance_and_boundary() -> None:
    packets = packet_index()
    for record in promises():
        packet = packets[record["id"]]
        assert packet["id"] == (
            "evidence-yamagata-pref-2025-"
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
        assert "第6編" in provenance["statement"]
        boundary = next(
            claim
            for claim in packet["claims"]
            if claim["field"] == "original_text"
        )
        assert "プロフィール欄" in boundary["review_note"]
        assert "実績欄" in boundary["review_note"]


def test_bulletin_source_and_term_connection() -> None:
    catalog = load_json("data/catalog/executive_sources.json")
    assert catalog["version"] == "0.68.0"
    assert len(catalog["records"]) == 203
    source = next(
        record for record in catalog["records"] if record["id"] == BULLETIN_ID
    )
    assert source["municipality_key"] == "yamagata-prefecture"
    assert source["organization"] == "山形県選挙管理委員会"
    assert source["category"] == "election"
    assert source["url"] == BULLETIN_URL
    assert source["availability"] == "published"
    assert source["review_status"] == "reviewed"
    assert source["confidence"] == "high"
    # The stage-3 note records the re-download and the file hash.
    assert SHA256 in source["notes"]
    assert "公約11件" in source["notes"]

    terms = load_json("data/entities/executives/executive_terms.json")
    term = next(record for record in terms if record["id"] == TERM_ID)
    assert term["person_name"] == "吉村 美栄子"
    assert term["election_date"] == "2025-01-26"
    assert term["term_start"] == "2025-02-14"
    assert term["term_end"] == "2029-02-13"
    assert term["manifesto_source_ids"] == [BULLETIN_ID]
    assert BULLETIN_ID in term["sources"]


def test_search_and_review_records() -> None:
    searches = load_json(
        "data/entities/executives/manifesto_source_searches.json"
    )
    assert len(searches) == 43
    search = next(record for record in searches if record["id"] == SEARCH_ID)
    assert_valid("schemas/manifesto_source_search.schema.json", search)
    assert search["executive_term_id"] == TERM_ID
    assert search["searched_at"] == "2026-11-27"
    assert search["result_status"] == "source_registered"
    assert search["manifesto_source_ids_found"] == [BULLETIN_ID]
    assert search["nonexistence_claim"] is False
    assert search["confidence"] == "high"
    assert BULLETIN_ID in search["checked_source_ids"]
    assert SHA256 in search["review_note"]
    assert "318,364票" in search["review_note"]

    reviews = load_json("data/entities/executives/manifesto_reviews.json")
    assert len(reviews) == 36
    review = next(record for record in reviews if record["id"] == REVIEW_ID)
    assert_valid("schemas/manifesto_review.schema.json", review)
    assert review["executive_term_id"] == TERM_ID
    assert review["source_id"] == BULLETIN_ID
    assert review["candidate_name"] == "吉村 美栄子"
    assert review["review_scope"] == "candidate_panel"
    assert review["statement_boundary"] == "mixed"
    assert review["segmentation_status"] == "segmented"
    assert review["promise_records_created"] == 11
    assert review["reason_codes"] == ["biography_and_policy_combined"]
    assert "除外は0件" in review["review_note"]
    assert "チャレンジ5.0" in review["review_note"]

    search_packets = {
        packet["subject_id"]: packet
        for packet in load_json(
            "data/entities/executives/"
            "manifesto_source_search_evidence_packets.json"
        )
    }
    assert len(search_packets) == 43
    packet = search_packets[SEARCH_ID]
    assert packet["subject_type"] == "manifesto_source_search"
    assert packet["review_status"] == "reviewed"
    result_claim = next(
        claim for claim in packet["claims"] if claim["field"] == "result_status"
    )
    # The review is a delegated review by Muse under the owner's
    # 2026-11-15 delegation, not the owner's own review.
    assert "所有者本人のレビューではない" in result_claim["review_note"]

    review_packets = {
        packet["subject_id"]: packet
        for packet in load_json(
            "data/entities/executives/manifesto_review_evidence_packets.json"
        )
    }
    assert len(review_packets) == 36
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
