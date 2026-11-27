"""Issue #1038: Akita Prefecture governor promises (cluster 18, stage 3).

The source is the official 2025 Akita Prefecture gubernatorial
election bulletin itself. The prefectural election commission's
current official pages no longer carry the bulletin, so the copy
hosted on the Yurihonjo City official site (the city's guide page
for the gubernatorial election) was downloaded on 2026-11-26
during stage 1 and proven byte-identical to the Wayback Machine
capture of the same URL (15 May 2025; CDX digest
VBYOCD42ZPDQN3KXISMEVLON7J7UPBCX): 1,207,207 bytes, 2 pages,
three candidates, matching the Ministry of Internal Affairs'
official results compilation. For stage 3 the file was
re-downloaded from the registered URL and its SHA-256 matched the
stage-1 value exactly
(680355120c3afb5c17ece4fb9dd63ef086fdd8063953c6630f367a9d2f7d34f8).

Governor Suzuki's panel (page 1, upper right) is a poster: a
strap headline "刷新！偏り・しがらみのない 秋田新時代へ", the main
headline "あきた『ニュートラル』宣言！", five "neutral" rows (関係・
政治・地域間・手法・カーボン) each pairing a label with a complete
directional statement ending in "〜秋田へ", and under the heading
"3つの重点政策 かせぐ・まもる・そだてる" a single undivided list of
ten bulleted items. The five neutral statements are complete
sentences about the prefecture's future and the direction of its
administration -- not topic labels -- so each is registered as one
record with the label kept in the source location; the "3つの
重点政策" heading itself is a topic label and is kept in the
source locations only (the Okayama City precedent). The panel's
left side carries a vertical appeal text ("みなさんの手で、新しい
秋田へ"), a data table of the seven Tohoku/Hokkaido governors, an
endorsement by 167 cross-party local assembly members, the
candidate's profile box, a rally announcement and a QR code; none
of these is a pledge, and the appeal text contains no itemised
policy statement, so zero records come from them. The panel
presents no past achievement as a pledge (the profile is career
history), so zero records were excluded as achievements. None of
the 15 items states a numeric target or a funding method; the
hospital-agency item says a deadline will be set ("期限を切って")
but states no date, so no deadline is registered either. The
bulletin is entirely image-based, so the texts were transcribed
from 200/300 dpi renderings and collated across resolutions.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

TERM_ID = "jp-local-050008-executive-2025-04-20"
BULLETIN_ID = "akita-pref-governor-election-2025-bulletin"
REVIEW_ID = "manifesto-review-jp-local-050008-2025"
SEARCH_ID = "manifesto-source-search-akita-pref-2025"
BULLETIN_SHA256 = "680355120c3afb5c17ece4fb9dd63ef086fdd8063953c6630f367a9d2f7d34f8"
BULLETIN_URL = (
    "https://www.city.yurihonjo.lg.jp/_res/projects/default_project/_page_/001/011/232/"
    "tijikouhou.pdf"
)

# The five neutral statements (panel order) followed by the ten
# bulleted items under "3つの重点政策", transcribed verbatim.
# The strap headline, the main headline, the five labels, the
# "3つの重点政策" heading, the appeal text, the data table, the
# endorsement, the profile and the rally announcement are not
# records. Any wording drift against the bulletin must fail here.
EXPECTED_ORIGINAL_TEXTS: list[str] = [
    "しがらみや縛りがなく、誰もが自由に発言・行動できる秋田へ",
    "政治的に偏らず、一人一人の多様な意見が尊重される秋田へ",
    "県内の都市部と町村部の偏りをなくし、誰もが豊かに暮らせる秋田へ",
    "既存の方法にとらわれず、最新・最善の手法で課題を解決する秋田へ",
    "森林や再エネなどの資源を生かし、日本で最初に脱炭素を実現する秋田へ",
    "看護、介護、保育ではたらく皆さんの所得向上",
    "企業誘致は地元人材の奪い合いでなく、Aターンにつながる高度な職種へシフト",
    "森林環境譲与税とJクレジットを県内で最大活用し、農山村に富を",
    "公共事業発注の公正の担保と平準化",
    "福祉行政全般の脱「お役所仕事」。心をかよわせる現場の意識改革を",
    "地元産エネルギーをふやして生活コストの低い秋田へ",
    "秋田県立病院機構の巨額赤字問題は期限を切って解決へ",
    "小中学校の給食費無償化と地産地消による食育",
    "詰め込み型・画一的・過保護教育からの脱却",
    "高校入試制度の見直しによるスポーツ競技力の復活",
]

EXPECTED_POLICY_AREAS = [
    "fiscal_administrative_reform",
    "universal_city_and_inclusion",
    "universal_city_and_inclusion",
    "fiscal_administrative_reform",
    "environment_and_climate",
    "health_welfare_and_community",
    "industry_and_economy",
    "environment_and_climate",
    "fiscal_administrative_reform",
    "health_welfare_and_community",
    "environment_and_climate",
    "health_welfare_and_community",
    "education_and_human_development",
    "education_and_human_development",
    "education_and_human_development",
]

_MEDICAL = "jp-local-050008-project-2026-medical-nursing-care-system"
_MIGRATION = "jp-local-050008-project-2026-akita-life-migration-employment"
_CHILDREN = "jp-local-050008-project-2026-children-healthy-growth"
EXPECTED_LINKS = {
    f"{TERM_ID}-promise-006": [_MEDICAL],
    f"{TERM_ID}-promise-007": [_MIGRATION],
    f"{TERM_ID}-promise-012": [_MEDICAL],
    f"{TERM_ID}-promise-013": [_CHILDREN],
    f"{TERM_ID}-promise-014": [_CHILDREN],
}
UNLINKED_IDS = {
    f"{TERM_ID}-promise-{index:03d}" for index in range(1, 16)
} - set(EXPECTED_LINKS)


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


def test_all_15_items_registered_verbatim_in_panel_order() -> None:
    items = records()
    assert [record["original_text"] for record in items] == EXPECTED_ORIGINAL_TEXTS
    assert [record["id"] for record in items] == [
        f"{TERM_ID}-promise-{index:03d}" for index in range(1, 16)
    ]
    for record in items:
        assert_valid("schemas/promise.schema.json", record)
        assert record["municipality_id"] == "jp-local-050008"
        assert record["executive_term_id"] == TERM_ID
        assert record["sources"] == [BULLETIN_ID]
        assert record["plain_summary"]
        # The registered copy was proven byte-identical to the
        # Wayback capture of the same official-site URL, so the
        # record-level grading is high.
        assert record["confidence"] == "high"
        assert record["review_status"] == "reviewed"


def test_policy_area_distribution() -> None:
    items = records()
    assert [record["policy_area"] for record in items] == EXPECTED_POLICY_AREAS


def test_no_numeric_content_was_invented() -> None:
    # None of the 15 items states a numeric target or a funding
    # method; the hospital item says a deadline will be set but
    # states no date, so nothing may be registered for them.
    for record in records():
        assert record["statement_type"] == "directional_commitment"
        assert record["baseline"] is None
        assert record["target"] is None
        # The term end is never used as an implicit promise deadline.
        assert record["deadline"] is None
        assert record["funding_statement"] is None
        assert record["change_explanation"] is None


def test_framing_profile_and_labels_were_not_registered() -> None:
    items = records()
    texts = [record["original_text"] for record in items]
    for non_promise_line in (
        # The strap headline and the main headline (framing).
        "刷新！偏り・しがらみのない",
        "ニュートラル』宣言",
        # The appeal text (a prose call for support).
        "みなさんの手で",
        "全国最下位は秋田県の定位置ではありません",
        "お力を貸して下さい",
        # The data table of the seven governors.
        "就任時平均",
        "佐竹 敬久",
        # The endorsement by 167 local assembly members.
        "超党派地方議員",
        "推薦します",
        # The profile box (the candidate's career history).
        "京都大学法学部卒業",
        "司法書士",
        "秋田県議会議員初当選",
        # The rally announcement.
        "ミルハス",
        # The three focus-policy labels are topic labels, kept in
        # the source locations, not registered as records.
        "かせぐ",
        "まもる",
        "そだてる",
    ):
        assert all(non_promise_line not in text for text in texts)


def test_progress_states_are_evidence_gated() -> None:
    # No official evaluation tied to these promises themselves
    # has been published, so nothing is scored: every item
    # stays not_assessable, linked or not.
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
        for project in load_json("data/reviewed/akita-prefecture/projects.json")
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
        # The bulletin provenance (official document; the copy on
        # the Yurihonjo City official site is byte-identical to
        # the Wayback capture of the same URL, and the stage-3
        # re-download hash-matched the stage-1 registration)
        # travels with every item.
        assert "選挙公報" in provenance["statement"]
        assert BULLETIN_SHA256 in provenance["statement"]
        assert "high" in provenance["statement"]
        assert set(provenance["source_ids"]) == {BULLETIN_ID}
        assert packet["open_questions"]
        # The review-basis claim records that the review/promotion
        # judgement rests on the owner's 2026-11-15 delegation to
        # Muse and is not the owner's own review.
        basis = next(
            claim for claim in packet["claims"] if claim["field"] == "review_basis"
        )
        assert basis["decision"] == "accepted"
        assert "2026-11-15" in basis["review_note"]
        assert "所有者本人のレビューではない" in basis["review_note"]


def test_bulletin_source_record_points_at_the_verified_copy() -> None:
    catalog = load_json("data/catalog/executive_sources.json")
    assert catalog["version"] == "0.69.0"
    assert len(catalog["records"]) == 206
    bulletin = next(r for r in catalog["records"] if r["id"] == BULLETIN_ID)
    assert bulletin["municipality_key"] == "akita-prefecture"
    assert bulletin["organization"].startswith("秋田県選挙管理委員会")
    assert bulletin["url"] == BULLETIN_URL
    assert BULLETIN_SHA256 in bulletin["notes"]


def test_review_search_and_term_reflect_the_registration() -> None:
    reviews = load_json("data/entities/executives/manifesto_reviews.json")
    review = next(record for record in reviews if record["id"] == REVIEW_ID)
    assert_valid("schemas/manifesto_review.schema.json", review)
    assert review["source_id"] == BULLETIN_ID
    assert review["review_scope"] == "candidate_panel"
    assert review["statement_boundary"] == "mixed"
    assert review["segmentation_status"] == "segmented"
    assert review["promise_records_created"] == 15
    assert "2026-11-15" in review["review_note"]
    assert "所有者本人のレビューとしては記録しない" in review["review_note"]

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
    assert term["term_start"] == "2025-04-20"
    assert term["term_end"] == "2029-04-19"


def test_manifesto_review_has_an_evidence_packet() -> None:
    packets = load_json(
        "data/entities/executives/manifesto_review_evidence_packets.json"
    )
    packet = next(p for p in packets if p["subject_id"] == REVIEW_ID)
    assert packet["id"] == "evidence-akita-pref-2025-manifesto-review"
    assert packet["subject_type"] == "manifesto_review"
    assert_valid("schemas/evidence_packet.schema.json", packet)
    fields = [claim["field"] for claim in packet["claims"]]
    assert "segmentation_status" in fields
    assert "source_provenance" in fields
    provenance = next(
        claim for claim in packet["claims"] if claim["field"] == "source_provenance"
    )
    assert BULLETIN_SHA256 in provenance["statement"]
    basis = next(
        claim for claim in packet["claims"] if claim["field"] == "review_basis"
    )
    assert "所有者本人のレビューではない" in basis["review_note"]
    assert packet["open_questions"]
