"""Issue #974: Okayama City mayor promises (cluster 14, stage 3).

The source is the official 2025 Okayama City mayoral election
bulletin itself. During the election period the bulletin PDF was
published as an attachment (kouhou01.pdf) to the city election
commission's bulletin guide page on the city's official site; the
live official URL is now 404, and the Wayback Machine capture of
the official URL (21 September 2025, the proclamation day, CDX
digest YYYYSS5ZCNRWRI6XUE7FSIIPFRXTSFXM) cannot be replayed -- it
redirects to the 19 February 2026 capture of the same URL, which
is the city's 404 page. The identical bulletin copy served by the
go2senkyo CDN was therefore downloaded on 2026-11-23 and its
SHA-1 digest matched the Wayback CDX digest exactly, proving it
is byte-identical to the file published at the official URL
(3,489,450 bytes, 2 pages, four candidates, matching the city's
official results; SHA-256
bf3cc6f129aeb018226cdc20097ca5aa10281a398da9c64cc3bd7649df91b602).
Mayor Omori's panel (page 1, upper right) is a poster: the
headline "大森まさおは、市民と一緒に考え、一緒に行動します。", a
diagram titled "大森市政12年間で創りあげた岡山市の総合力を高める
好循環" (the three pillars of city administration -- 住みやすさ,
力強さ, 安全・安心 -- feeding an expansion of the city's economy
and rising incomes), six headings under the three pillars whose
bulleted items are the pledges (安心して子育てができ、誰もが輝く
まち = 4 items, 未来を拓く人材を育むまち = 3 items, いきいきと
住み続けられるまち = 2 items, 活力にあふれ国内外の人を惹きつける
産業・農業・観光のまち = 4 items, 魅力と活力あふれるまちづくり
地域づくり = 4 items, 安心して住み続けられるまち = 4 items) and
his profile box (career history: born in Okayama City in 1954,
Tokyo University law graduate, Construction Ministry official,
Kumamoto prefectural planning director, Cabinet Office and MLIT
policy coordinators, MLIT National Land Policy Bureau director
general, first elected mayor in 2013). Each bullet stands as a
policy statement on its own, so the 21 records follow the Chiba
City / Sendai / Hiroshima City / Kyoto City precedent of one
record per item, registered in the panel's visual reading order
(the three pillars in their presented order). The six headings
are topic labels (all are "〜まち" / "〜地域づくり" noun phrases,
not verb-phrase commitments), so they are kept in the source
locations rather than registered (the Hamamatsu precedent
registered headings only because they were verb phrases). The
headline, the virtuous-cycle diagram and the profile are
framing or career history, not promises; the diagram invokes
the comprehensive strength "built up" over twelve years of the
Omori administration, but no bulleted item presents a past
achievement as a pledge, so zero records were excluded as
achievements. None of the 21 items states a numeric target, a
deadline or a funding method, so all 21 are directional
commitments with no target registered. The bulletin is entirely
image-based (a text extraction of the whole PDF yields no
characters), so the texts were transcribed from 200/400 dpi
renderings and collated across resolutions.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

TERM_ID = "jp-local-331007-executive-2025-10-09"
BULLETIN_ID = "okayama-city-mayor-election-2025-bulletin"
REVIEW_ID = "manifesto-review-jp-local-331007-2025"
SEARCH_ID = "manifesto-source-search-okayama-city-2025"
BULLETIN_SHA256 = "bf3cc6f129aeb018226cdc20097ca5aa10281a398da9c64cc3bd7649df91b602"
BULLETIN_URL = (
    "https://prod-cdn.go2senkyo.com/public/senkyo_koho/25556/"
    "20251005%E5%B2%A1%E5%B1%B1%E5%B8%82%E9%95%B7%E9%81%B8%E6%8C%99.pdf"
)

# The 21 bulleted items of Mayor Omori's panel in the official
# 2025 election bulletin (page 1), transcribed verbatim in the
# panel's reading order. The headline, the virtuous-cycle
# diagram, the six headings and the profile box are not records.
# Any wording drift against the bulletin must fail here.
EXPECTED_ORIGINAL_TEXTS: list[str] = [
    "放課後児童クラブの待機児童解消",
    "質の高い子育て環境づくり",
    "困難を抱える子ども・若者やその家庭への支援",
    "女性や子ども、若者をはじめ誰もが活躍できるまちづくり",
    "「自らの個性を磨き、選択と挑戦を繰り返すことができる子ども」の育成",
    "個に応じた支援の充実（不登校の子どもや障害等がある子ども等への支援の充実）",
    "多様な主体によるESDの推進、SDGsの理念「誰一人取り残さない」社会の実現",
    "健康寿命延伸と生涯活躍できる社会の推進（ポジティブ・ヘルス・オカヤマの推進）",
    "医療・介護・福祉が充実したまち",
    "戦略的な産業振興（中小企業等支援、企業立地の推進、創業支援）",
    "多彩な農林水産物のブランド力強化と担い手育成",
    "固有の歴史・文化遺産を活かした観光誘客の推進",
    "コンベンション誘致、戦略的なプロモーション",
    "まちを楽しむ（岡山城西の丸周辺広場整備、石山公園再整備、路面電車の充実、緑のボリュームアップ等）",
    "魅力と活力のある地域づくり（地域振興基金等を活用した経済、歴史・文化、生活の向上）",
    "交通ネットワークの充実（公共交通の充実、生活交通の確保、道路ネットワークの整備）",
    (
        "文化・芸術・スポーツ振興による誇りと一体感の創出、トップチームの試合環境整備"
        "（岡山芸術創造劇場ハレノワの活用、トップチーム支援）"
    ),
    "地域の安全性を高める対策（生活道路の整備、用水路等の転落防止対策、防犯カメラ・防犯灯設置支援）",
    "インフラの老朽化対策",
    "災害に強いまちづくり（浸水対策（旭川ダムの再生など）、自主防災組織の活性化）",
    "脱炭素型の都市の実現、循環型社会の構築",
]

EXPECTED_POLICY_AREAS = [
    "childcare_and_childrearing",
    "childcare_and_childrearing",
    "childcare_and_childrearing",
    "universal_city_and_inclusion",
    "education_and_human_development",
    "education_and_human_development",
    "education_and_human_development",
    "health_welfare_and_community",
    "health_welfare_and_community",
    "industry_and_economy",
    "industry_and_economy",
    "urban_development_and_tourism",
    "urban_development_and_tourism",
    "urban_development_and_tourism",
    "urban_development_and_tourism",
    "transport_infrastructure",
    "urban_development_and_tourism",
    "safety_and_disaster_prevention",
    "transport_infrastructure",
    "safety_and_disaster_prevention",
    "environment_and_climate",
]

_PROJECT = "jp-local-331007-project-2026-"
EXPECTED_LINKS = {
    f"{TERM_ID}-promise-001": [_PROJECT + "child-rearing"],
    f"{TERM_ID}-promise-002": [_PROJECT + "child-rearing"],
    f"{TERM_ID}-promise-003": [_PROJECT + "children-youth"],
    f"{TERM_ID}-promise-004": [_PROJECT + "human-rights-gender-equality"],
    f"{TERM_ID}-promise-005": [_PROJECT + "school-education"],
    f"{TERM_ID}-promise-006": [_PROJECT + "school-education"],
    f"{TERM_ID}-promise-007": [_PROJECT + "collaboration-esd"],
    f"{TERM_ID}-promise-008": [_PROJECT + "health"],
    f"{TERM_ID}-promise-009": [_PROJECT + "welfare"],
}
# The remaining twelve items have no stage-2 policy whose subject
# matches them (the ten registered policies all belong to the
# plan's basic directions on children/child-rearing/education,
# collaboration/diversity and health/welfare; none covers
# industry, agriculture, tourism, city promotion, transport,
# urban development, public safety, disaster prevention or the
# environment), so they stay unlinked -- see the records'
# extraction notes.
UNLINKED_IDS = {
    f"{TERM_ID}-promise-{index:03d}" for index in range(10, 22)
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


def test_all_21_items_registered_verbatim_in_panel_order() -> None:
    items = records()
    assert [record["original_text"] for record in items] == EXPECTED_ORIGINAL_TEXTS
    assert [record["id"] for record in items] == [
        f"{TERM_ID}-promise-{index:03d}" for index in range(1, 22)
    ]
    for record in items:
        assert_valid("schemas/promise.schema.json", record)
        assert record["municipality_id"] == "jp-local-331007"
        assert record["executive_term_id"] == TERM_ID
        assert record["sources"] == [BULLETIN_ID]
        assert record["plain_summary"]
        # The source is the official election bulletin itself
        # (the top of the source hierarchy); the registered copy
        # was proven byte-identical to the file published at the
        # city's official URL by the Wayback CDX digest match, so
        # the record-level grading is high.
        assert record["confidence"] == "high"
        assert record["review_status"] == "reviewed"


def test_policy_area_distribution() -> None:
    items = records()
    assert [record["policy_area"] for record in items] == EXPECTED_POLICY_AREAS


def test_no_numeric_content_was_invented() -> None:
    # None of the 21 items states a numeric target, a deadline
    # or a funding method; nothing may be registered for them.
    for record in records():
        assert record["statement_type"] == "directional_commitment"
        assert record["baseline"] is None
        assert record["target"] is None
        # The term end is never used as an implicit promise deadline.
        assert record["deadline"] is None
        assert record["funding_statement"] is None
        assert record["change_explanation"] is None


def test_framing_profile_and_headings_were_not_registered() -> None:
    items = records()
    texts = [record["original_text"] for record in items]
    for non_promise_line in (
        # The headline (a framing statement).
        "市民と一緒に考え",
        # The virtuous-cycle diagram (the administration's
        # framing, including its reference to the strength
        # "built up" over the past twelve years).
        "好循環",
        "市内経済の拡大",
        "収入増加",
        # The profile box (the candidate's career history).
        "東京大学法学部",
        "建設省入省",
        "熊本県企画課長",
        "国土政策局長",
        # The six headings are topic labels, kept in the source
        # locations, not registered as records.
        "安心して子育てができ、誰もが輝くまち",
        "未来を拓く人材を育むまち",
        "いきいきと住み続けられるまち",
        "活力にあふれ国内外の人を惹きつける産業・農業・観光のまち",
        "魅力と活力あふれるまちづくり地域づくり",
        "安心して住み続けられるまち",
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
        for project in load_json("data/reviewed/okayama-city/projects.json")
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
        # The bulletin provenance (official document; the live
        # official URL is 404 and the Wayback capture cannot be
        # replayed, but the go2senkyo copy's SHA-1 digest matches
        # the Wayback CDX digest of the official URL's capture,
        # and the panel was transcribed from renderings) travels
        # with every item.
        assert "選挙公報" in provenance["statement"]
        assert BULLETIN_SHA256 in provenance["statement"]
        assert "high" in provenance["statement"]
        assert set(provenance["source_ids"]) == {BULLETIN_ID}
        assert packet["open_questions"]


def test_bulletin_source_record_points_at_the_digest_verified_copy() -> None:
    catalog = load_json("data/catalog/executive_sources.json")
    assert catalog["version"] == "0.69.0"
    assert len(catalog["records"]) == 206
    assert len(catalog["records"]) == 206
    bulletin = next(r for r in catalog["records"] if r["id"] == BULLETIN_ID)
    assert bulletin["municipality_key"] == "okayama-city"
    assert bulletin["organization"].startswith("岡山市選挙管理委員会")
    # The live official URL is 404 and the Wayback capture of it
    # cannot be replayed, so the registered URL is the go2senkyo
    # CDN copy whose SHA-1 digest matches the Wayback CDX digest
    # of the official URL's 2025-09-21 capture; the notes record
    # the full provenance chain and the SHA-256 of the file.
    assert bulletin["url"] == BULLETIN_URL
    assert BULLETIN_SHA256 in bulletin["notes"]
    assert "kouhou01.pdf" in bulletin["notes"]


def test_review_search_and_term_reflect_the_registration() -> None:
    reviews = load_json("data/entities/executives/manifesto_reviews.json")
    review = next(record for record in reviews if record["id"] == REVIEW_ID)
    assert_valid("schemas/manifesto_review.schema.json", review)
    assert review["source_id"] == BULLETIN_ID
    assert review["review_scope"] == "candidate_panel"
    assert review["statement_boundary"] == "mixed"
    assert review["segmentation_status"] == "segmented"
    assert review["promise_records_created"] == 21

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
    assert term["term_start"] == "2025-10-09"
    assert term["term_end"] == "2029-10-08"
