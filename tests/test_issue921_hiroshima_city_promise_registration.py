"""Issue #921: Hiroshima City mayor promises (cluster 11, stage 3).

The source is the official 2023 Hiroshima City mayoral election
bulletin itself. During the election period the bulletin PDF was
published on the city's official site (uploaded/attachment/
208510.pdf, linked from the city's election page "令和5年4月9日執行
広島市長選挙の候補者一覧表及び選挙公報" as "広島市長選挙・選挙広報"),
but the current site carries no path to it and the old URL returns
404, so the registered copy is the Wayback Machine capture of the
city's official URL (4 April 2023). That PDF has only one 200
capture, so unlike the Sendai / Shizuoka City precedents the
archived copy cannot be corroborated by a digest match across
captures; instead its authenticity rests on three points: the
capture was taken from the city's official URL during the
election period, the archived official index page names the file
"広島市長選挙・選挙広報 [PDFファイル／1.46MB]" and that size matches
the downloaded file (1,526,285 bytes), and the three candidates
printed in the bulletin match the city's official candidate list
and the official results in the "選挙の記録（別冊3）". Mayor
Matsui's panel (page 1, lower half) is a poster: the headline
"世界に誇れる『まち』広島をめざして" above three perspectives
(「鳥の目」「虫の目」「心の目」), a declaration sentence and his
profile box (career history: Labour Ministry / MHLW official,
mayor since 2011), and three numbered pillars whose fourteen
bulleted items are the pledges (1. 活力とにぎわいのまち = 5 items,
2. ワーク・ライフバランスのまち = 6 items, 3. 平和への思いを共有
するまち = 3 items). Each bullet stands as a policy statement on
its own, so the fourteen records follow the Chiba City / Sendai
precedent of one record per item; the pillar headings are topic
labels, not verb-phrase commitments, so they are kept in the
source locations rather than registered (the Hamamatsu precedent
registered headings only because they were verb phrases). The
headline, the three perspectives, the declaration, the closing
slogan and the profile are framing or career history, not
promises, and the panel carries no achievements list. None of
the fourteen items states a numeric target, a deadline or a
funding method, so all fourteen are directional commitments with
no target registered. The bulletin is entirely image-based (a
text extraction of the whole PDF yields only form feeds), so the
texts were transcribed from 200/300 dpi renderings and collated
across resolutions.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

TERM_ID = "jp-local-341002-executive-2023-04-12"
BULLETIN_ID = "hiroshima-city-mayor-election-2023-bulletin"
REVIEW_ID = "manifesto-review-jp-local-341002-2023"
SEARCH_ID = "manifesto-source-search-hiroshima-city-2023"

# The fourteen bulleted items of Mayor Matsui's panel in the
# official 2023 election bulletin (page 1), transcribed verbatim
# in document order. The headline, the three perspectives, the
# declaration, the closing slogan and the profile box are not
# records. Any wording drift against the bulletin must fail here.
EXPECTED_ORIGINAL_TEXTS: list[str] = [
    "広島都心（広島駅・紙屋町・八丁堀・中央公園・基町）の大改造",
    "都心周辺部（商工センター・西風新都・西広島駅）の大改造",
    "中山間地・島しょ部の魅力あふれる資源を活かした振興策",
    "広島城リニューアル G7広島サミット開催を契機に観光客拡大",
    "AI・IoTや省エネ機器導入など次世代変革に向けた産業支援",
    "「お互い様」の心で豊かに暮らしていける「地域共生社会」",
    "すべての子供が個性や能力をのばし健やかに成長できる環境づくり",
    "「スポーツ王国広島」としてトップレベルの国際大会誘致",
    "シンフォニーホールも視野に音楽に触れられる日常",
    "豪雨災害からの復興と被災経験を活かした安心で快適なくらし",
    "省エネルギー対策、再生可能エネルギー促進などの地球温暖化対策",
    "被爆体験をもとに「ヒロシマの心」を国内外に発信",
    "G7広島サミットで各国首脳が被爆の実相に触れる機会を確保",
    "世界の為政者に来広を働きかける「迎える平和」を推進",
]

EXPECTED_POLICY_AREAS = [
    "urban_development_and_tourism",
    "urban_development_and_tourism",
    "urban_development_and_tourism",
    "urban_development_and_tourism",
    "industry_and_economy",
    "universal_city_and_inclusion",
    "childcare_and_childrearing",
    "urban_development_and_tourism",
    "urban_development_and_tourism",
    "safety_and_disaster_prevention",
    "environment_and_climate",
    "international_engagement",
    "international_engagement",
    "international_engagement",
]

EXPECTED_LINKS = {
    f"{TERM_ID}-promise-001": [
        "jp-local-341002-project-2025-urban-centrality"
    ],
    f"{TERM_ID}-promise-002": [
        "jp-local-341002-project-2025-urban-centrality"
    ],
    f"{TERM_ID}-promise-005": [
        "jp-local-341002-project-2025-economic-promotion"
    ],
    f"{TERM_ID}-promise-006": [
        "jp-local-341002-project-2025-social-welfare"
    ],
    f"{TERM_ID}-promise-007": [
        "jp-local-341002-project-2025-social-welfare"
    ],
}
# The remaining nine items have no stage-2 series whose subject
# matches them (no series for rural/island revitalisation,
# tourism, sports, culture, disaster recovery, environment or
# peace diplomacy), so they stay unlinked -- see the records'
# extraction notes.
UNLINKED_IDS = {
    f"{TERM_ID}-promise-{index:03d}"
    for index in (3, 4, 8, 9, 10, 11, 12, 13, 14)
}


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


def records() -> list[dict[str, Any]]:
    return [
        record
        for record in load_json("data/entities/executives/promises.json")
        if record["executive_term_id"] == TERM_ID
    ]


def packets_by_subject() -> dict[str, dict[str, Any]]:
    packets = load_json("data/entities/executives/promise_evidence_packets.json")
    return {
        packet["subject_id"]: packet
        for packet in packets
        if packet["subject_id"].startswith(TERM_ID)
    }


def test_all_14_items_registered_verbatim_in_document_order() -> None:
    items = records()
    assert [record["original_text"] for record in items] == EXPECTED_ORIGINAL_TEXTS
    assert [record["id"] for record in items] == [
        f"{TERM_ID}-promise-{index:03d}" for index in range(1, 15)
    ]
    for record in items:
        assert_valid("schemas/promise.schema.json", record)
        assert record["municipality_id"] == "jp-local-341002"
        assert record["executive_term_id"] == TERM_ID
        assert record["sources"] == [BULLETIN_ID]
        assert record["plain_summary"]
        # The source is the official election bulletin itself (the
        # top of the source hierarchy); the registered copy is the
        # archived copy of the city's official election-period URL,
        # corroborated as described in the module docstring, so
        # the record-level grading is high.
        assert record["confidence"] == "high"
        assert record["review_status"] == "reviewed"


def test_policy_area_distribution() -> None:
    items = records()
    assert [record["policy_area"] for record in items] == EXPECTED_POLICY_AREAS


def test_no_numeric_content_was_invented() -> None:
    # None of the fourteen items states a numeric target, a
    # deadline or a funding method; nothing may be registered
    # for them.
    for record in records():
        assert record["statement_type"] == "directional_commitment"
        assert record["baseline"] is None
        assert record["target"] is None
        # The term end is never used as an implicit promise deadline.
        assert record["deadline"] is None
        assert record["funding_statement"] is None
        assert record["change_explanation"] is None


def test_framing_and_profile_were_not_registered() -> None:
    items = records()
    texts = [record["original_text"] for record in items]
    for non_promise_line in (
        # The headline and the declaration (framing statements).
        "世界に誇れる",
        "果敢に挑戦します",
        # The three perspectives (framing labels).
        "鳥の目",
        "虫の目",
        "心の目",
        # The closing slogan.
        "地域社会を目指そう",
        # The profile box (the candidate's career history).
        "昭和28年",
        "労働省入省",
        "中央労働委員会事務局長",
        "広島市長就任",
        # The pillar headings are topic labels, kept in the
        # source locations, not registered as records.
        "活力とにぎわいのまち",
        "ワーク・ライフバランスのまち",
        "平和への思いを共有するまち",
    ):
        assert all(non_promise_line not in text for text in texts)


def test_progress_states_are_evidence_gated() -> None:
    # No official evaluation tied to these promises has been
    # published, so nothing is scored: every item stays
    # not_assessable, linked or not.
    for record in records():
        assert record["progress_state"] == "not_assessable"


def test_project_links_are_exact_bidirectional_and_capped() -> None:
    items = {record["id"]: record for record in records()}
    for promise_id, project_ids in EXPECTED_LINKS.items():
        assert items[promise_id]["related_project_ids"] == project_ids
    for record in items.values():
        if record["id"] not in EXPECTED_LINKS:
            assert record["related_project_ids"] == []

    projects = {
        project["id"]: project
        for project in load_json("data/reviewed/hiroshima-city/projects.json")
    }
    for promise_id, project_ids in EXPECTED_LINKS.items():
        for project_id in project_ids:
            assert promise_id in projects[project_id]["related_promise_ids"]
    linked_promise_ids = {
        promise_id
        for project in projects.values()
        for promise_id in project["related_promise_ids"]
    }
    assert linked_promise_ids == set(EXPECTED_LINKS)

    packets = packets_by_subject()
    for promise_id in EXPECTED_LINKS:
        claims = {claim["field"]: claim for claim in packets[promise_id]["claims"]}
        link_claim = claims["related_project_ids"]
        assert link_claim["decision"] == "needs_review"
        assert "low / inferred" in link_claim["review_note"]


def test_unlinked_promises_state_the_reason() -> None:
    items = {record["id"]: record for record in records()}
    for promise_id in UNLINKED_IDS:
        note = items[promise_id]["extraction_note"] or ""
        assert "事業接続は行っていない" in note
        packet = packets_by_subject()[promise_id]
        assert packet["open_questions"]


def test_every_promise_has_one_packet_with_provenance() -> None:
    items = records()
    packets = packets_by_subject()
    assert set(packets) == {record["id"] for record in items}
    for record in items:
        packet = packets[record["id"]]
        assert_valid("schemas/evidence_packet.schema.json", packet)
        fields = [claim["field"] for claim in packet["claims"]]
        assert "original_text" in fields
        provenance = next(
            claim for claim in packet["claims"] if claim["field"] == "source_provenance"
        )
        # The bulletin provenance (official document, the city's
        # official URL deleted from the current site, the single
        # archived capture corroborated by the archived official
        # index page, file size and candidate list, image-based
        # panel transcribed from renderings) travels with every
        # item.
        assert "選挙公報" in provenance["statement"]
        assert "Wayback" in provenance["statement"]
        assert "high" in provenance["statement"]
        assert set(provenance["source_ids"]) == {BULLETIN_ID}
        assert packet["open_questions"]


def test_bulletin_source_record_points_at_the_archived_pdf() -> None:
    catalog = load_json("data/catalog/executive_sources.json")
    assert catalog["version"] == "0.46.0"
    assert len(catalog["records"]) == 135
    bulletin = next(r for r in catalog["records"] if r["id"] == BULLETIN_ID)
    assert bulletin["municipality_key"] == "hiroshima-city"
    assert bulletin["organization"].startswith("広島市選挙管理委員会")
    # The live official URL is deleted (404); the registered URL
    # is the Wayback capture of that same official URL, and the
    # notes record the single-capture situation and the three
    # corroboration points, including the Wayback digest and the
    # downloaded file's SHA-256.
    assert bulletin["url"] == (
        "https://web.archive.org/web/20230404234705/"
        "https://www.city.hiroshima.lg.jp/uploaded/attachment/208510.pdf"
    )
    assert "6WDGBCMGPXGNI7IGUVQF36KDPVV5763L" in bulletin["notes"]
    assert (
        "bbe4548fed69ea52370643890205697d9b4513b3650989df509673fa99f57e51"
        in bulletin["notes"]
    )


def test_review_search_and_term_reflect_the_registration() -> None:
    reviews = load_json("data/entities/executives/manifesto_reviews.json")
    review = next(record for record in reviews if record["id"] == REVIEW_ID)
    assert_valid("schemas/manifesto_review.schema.json", review)
    assert review["source_id"] == BULLETIN_ID
    assert review["review_scope"] == "candidate_panel"
    assert review["statement_boundary"] == "mixed"
    assert review["segmentation_status"] == "segmented"
    assert review["promise_records_created"] == 14

    searches = load_json("data/entities/executives/manifesto_source_searches.json")
    search = next(record for record in searches if record["id"] == SEARCH_ID)
    assert_valid("schemas/manifesto_source_search.schema.json", search)
    assert search["result_status"] == "source_registered"
    assert search["manifesto_source_ids_found"] == [BULLETIN_ID]
    assert BULLETIN_ID in search["checked_source_ids"]
    assert search["nonexistence_claim"] is False

    terms = load_json("data/entities/executives/executive_terms.json")
    term = next(record for record in terms if record["id"] == TERM_ID)
    assert term["manifesto_source_ids"] == [BULLETIN_ID]
    assert BULLETIN_ID in term["sources"]
    assert term["term_start"] == "2023-04-12"
    assert term["term_end"] == "2027-04-11"
