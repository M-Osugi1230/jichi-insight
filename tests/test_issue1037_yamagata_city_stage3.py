"""Issue #1037: register Yamagata City mayor's election-bulletin promises.

The promises come from the election bulletin (選挙公報) issued by
the Yamagata City election commission for the 10 September 2023
mayoral election, which re-elected Sato Takahiro to a third term.
The official PDF that was posted on the city's election page during
the election is now a 404 and the Wayback Machine holds only a 404
capture of that URL, so a digest match against the official original
was not possible.  Registration therefore uses the copy of the same
bulletin held on the Go2Senkyo CDN, whose content was verified
against the city's official election page and result report at
stage 1 (Issue #1014) and whose file was re-downloaded at stage 3
and hash-matched against the stage-1 verified copy (SHA-256
b7633c048c0f9add22f7c09e7598beff697d2755e5be6c58c9bc2c95fc868e88).
The candidate panel presents seven numbered items, each a bold
heading plus two to four "・" detail lines; following the Shizuoka
City precedent, each numbered item is registered as one record with
the heading and its details joined by newlines.  The panel headline,
the vision statement and the boxed closing statement (a summary
restating item 3 and the vision) are not promise records.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

BULLETIN_ID = "yamagata-city-mayor-election-2023-bulletin"
BULLETIN_URL = (
    "https://prod-cdn.go2senkyo.com/public/senkyo_koho/23596/"
    "r5sityoukouhou.pdf"
)
OFFICIAL_URL = (
    "https://www.city.yamagata-yamagata.lg.jp/_res/projects/"
    "default_project/_page_/001/012/073/r5sityousenkyokouhou3.pdf"
)
SHA256 = "b7633c048c0f9add22f7c09e7598beff697d2755e5be6c58c9bc2c95fc868e88"
TERM_ID = "jp-local-062014-executive-2023-09-28"
SEARCH_ID = "manifesto-source-search-yamagata-city-2023"
REVIEW_ID = "manifesto-review-jp-local-062014-2023"

PROJ = "jp-local-062014-project-2025-"

# (original_text, plain_summary, policy_area, linked project suffixes)
EXPECTED = [
    (
        "公共交通の充実による持続可能なまちづくり\n"
        "・地域コミュニティ交通のモデル事業推進と各地区への横展開\n"
        "・循環バス北くるりん、南くるりんの創設と山形駅〜蔵王駅間の新駅の建設\n"
        "・やまがたMaas「らくのる」を活用した地域交通DXの推進",
        "公共交通を充実させ、持続可能なまちづくりを進める。地域コミュニティ交通のモデル事業を各地区へ広げ、循環バス「北くるりん」「南くるりん」の創設と山形駅〜蔵王駅間の新駅建設、やまがたMaas「らくのる」による地域交通DXを推進する。",
        "transport_infrastructure",
        ["public-transport"],
    ),
    (
        "子育て支援の強化と新時代の教育環境づくり\n"
        "・高校生までの医療費完全無償化や、市民やNPOと連携したきめ細かな子育て支援体制の推進\n"
        "・教育ソフトの活用など、教育DXによる児童生徒の特性に合った学びの実現\n"
        "・学校部活動を地域、スポーツ・文化団体と連携しさらに充実",
        "子育て支援を強化し、新時代の教育環境を整える。高校生までの医療費完全無償化や市民・NPOと連携した子育て支援体制を進め、教育DXによる特性に合った学びの実現と、地域と連携した学校部活動の充実を図る。",
        "childcare_and_childrearing",
        ["children", "education"],
    ),
    (
        "地域経済のコロナ禍からの回復とさらなる活性化\n"
        "・建設中の新産業団地への企業誘致による経済活性化と雇用の創出\n"
        "・地元企業の売り上げ増進支援と起業創業の促進でチャンスの多いまちへ",
        "地域経済のコロナ禍からの回復とさらなる活性化を図る。新産業団地への企業誘致による経済活性化と雇用の創出を進め、地元企業の売り上げ増進支援と起業創業の促進に取り組む。",
        "industry_and_economy",
        ["commerce-industry"],
    ),
    (
        "戦略的で持続可能な農業の構築\n"
        "・戦略農産物の団地化・農業DX化のさらなる推進で強い農業へ\n"
        "・鳥獣被害対策の体制強化と中山間に適した農業の構築\n"
        "・各地区の農地の将来像「目標地図」の作成と担い手づくり",
        "戦略的で持続可能な農業を構築する。戦略農産物の団地化と農業DX化をさらに進めて強い農業を目指し、鳥獣被害対策の体制強化と中山間に適した農業の構築、各地区の農地の将来像「目標地図」の作成と担い手づくりを進める。",
        "industry_and_economy",
        ["agriculture-forestry"],
    ),
    (
        "市民の健康増進と地域福祉の充実\n"
        "・SUKSK（スクスク）生活の推進やスポーツ施設の充実による市民の健康寿命延伸\n"
        "・市立病院済生館と診療所の連携による、安心の地域医療\n"
        "・地区ごとの通いの場、健康づくり、相談の拠点等安心の地域づくり\n"
        "・誰もが分け隔てなく暮らせるインクルーシブなまちづくり",
        "市民の健康増進と地域福祉を充実させる。SUKSK（スクスク）生活の推進やスポーツ施設の充実による健康寿命の延伸、市立病院済生館と診療所の連携による地域医療、地区ごとの通いの場や相談の拠点等の整備、インクルーシブなまちづくりを進める。",
        "health_welfare_and_community",
        ["health", "sports", "medical-care", "welfare"],
    ),
    (
        "中心市街地の活性化と文化創造都市事業の推進\n"
        "・旧大沼・市立病院済生館の再開発、御殿堰を活かしたまちづくり、新市民会館の建設、千歳館の観光施設としての活用などにより「歩くほど幸せになるまち」へ\n"
        "・やまがたクリエイティブシティセンターQ1のさらなる積極活用と新たな価値の創造\n"
        "・歴史資産や文化財の積極活用と芸術祭の開催等による市民の活動機会の増加",
        "中心市街地の活性化と文化創造都市事業を推進する。旧大沼・市立病院済生館の再開発、御殿堰を活かしたまちづくり、新市民会館の建設、千歳館の観光施設としての活用を進め、やまがたクリエイティブシティセンターQ1の積極活用と新たな価値の創造、歴史資産や文化財の積極活用と芸術祭の開催等による市民の活動機会の増加を図る。",
        "urban_development_and_tourism",
        ["central-city-area", "culture"],
    ),
    (
        "交流人口の増加によるまちの賑わいづくり\n"
        "・山形駅東口への観光案内所、道の駅「やまがた蔵王」の設置等による交流人口増\n"
        "・蔵王・山寺・中心市街地の観光地整備と体験型観光の推進\n"
        "・やまがたPAスマートインター、山形中山道路、山形南道路など交通網の充実",
        "交流人口の増加によるまちの賑わいづくりを進める。山形駅東口への観光案内所と道の駅「やまがた蔵王」の設置で交流人口を増やし、蔵王・山寺・中心市街地の観光地整備と体験型観光の推進、やまがたPAスマートインター・山形中山道路・山形南道路など交通網の充実を図る。",
        "urban_development_and_tourism",
        ["tourism", "urban-development"],
    ),
]

HEADINGS = [
    "公共交通の充実による持続可能なまちづくり",
    "子育て支援の強化と新時代の教育環境づくり",
    "地域経済のコロナ禍からの回復とさらなる活性化",
    "戦略的で持続可能な農業の構築",
    "市民の健康増進と地域福祉の充実",
    "中心市街地の活性化と文化創造都市事業の推進",
    "交流人口の増加によるまちの賑わいづくり",
]

EXPECTED_LINKS: dict[str, list[str]] = {}
for _index, (_, _, _, _links) in enumerate(EXPECTED, start=1):
    for _suffix in _links:
        EXPECTED_LINKS.setdefault(PROJ + _suffix, []).append(
            f"{TERM_ID}-promise-{_index:03d}"
        )


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


def test_seven_promises_in_panel_order() -> None:
    records = promises()
    assert len(records) == 7
    for index, (record, expected) in enumerate(
        zip(records, EXPECTED, strict=True), start=1
    ):
        text, summary, area, links = expected
        assert record["id"] == f"{TERM_ID}-promise-{index:03d}"
        assert record["municipality_id"] == "jp-local-062014"
        assert record["original_text"] == text
        assert record["plain_summary"] == summary
        assert record["policy_area"] == area
        assert record["source_location"] == (
            f"選挙公報1ページ目・さとう孝弘候補欄の項目{index}"
            f"（{HEADINGS[index - 1]}）"
        )
        assert record["statement_type"] == "directional_commitment"
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
        assert record["related_project_ids"] == [PROJ + s for s in links]


def test_policy_area_distribution() -> None:
    counts = Counter(record["policy_area"] for record in promises())
    assert counts == Counter(
        {
            "transport_infrastructure": 1,
            "childcare_and_childrearing": 1,
            "industry_and_economy": 2,
            "health_welfare_and_community": 1,
            "urban_development_and_tourism": 2,
        }
    )


def test_no_non_promise_panel_content() -> None:
    joined = "\n".join(record["original_text"] for record in promises())
    # Panel headline, vision statement and the boxed closing summary
    # are framing statements, not promise records; the other
    # candidate's panel is out of scope as well.
    for fragment in (
        "市民と共に",
        "希望の山形へ",
        "健康医療先進都市",
        "のビジョンのもと",
        "3期目も全力で働きます",
        "まずはコロナ禍からの再起動",
        "プレミアム商品券",
        "インバウンド誘客",
        "どの世代も心豊かに暮らせる山形市を目指し",
        "渡辺ゆり子",
        "学校給食費を無料に",
        "物価高騰からくらし守る",
    ):
        assert fragment not in joined
    # No numeric targets, deadlines or funding figures are stated in
    # the seven items.
    for record in promises():
        assert record["target"] is None
        assert record["deadline"] is None
        assert record["funding_statement"] is None


def test_project_links_bidirectional_and_capped() -> None:
    records = {record["id"]: record for record in promises()}
    linked = [
        record for record in records.values() if record["related_project_ids"]
    ]
    assert len(linked) == 7
    projects = {
        project["id"]: project
        for project in load_json("data/reviewed/yamagata-city/projects.json")
    }
    for project_id, promise_ids in EXPECTED_LINKS.items():
        assert projects[project_id]["related_promise_ids"] == promise_ids
    unlinked = [
        project_id
        for project_id, project in projects.items()
        if project["related_promise_ids"] == []
    ]
    assert len(unlinked) == 19 - len(EXPECTED_LINKS)
    packets = packet_index()
    for record in linked:
        packet = packets[record["id"]]
        link_claims = [
            claim
            for claim in packet["claims"]
            if claim["field"] == "related_project_ids"
        ]
        assert len(link_claims) == len(record["related_project_ids"])
        for claim in link_claims:
            assert claim["decision"] == "needs_review"
            assert "low / inferred" in claim["review_note"]
        assert "low / inferred" in record["extraction_note"]


def test_packets_cover_provenance_and_limitation() -> None:
    packets = packet_index()
    for record in promises():
        packet = packets[record["id"]]
        assert packet["id"] == (
            "evidence-yamagata-city-2023-"
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
        assert "ダイジェスト照合はできていない" in provenance["statement"]
        assert "150dpi" in provenance["statement"]
        boundary = next(
            claim
            for claim in packet["claims"]
            if claim["field"] == "original_text"
        )
        assert "市民と共に 希望の山形へ！" in boundary["review_note"]
        assert "結びの文章" in boundary["review_note"]


def test_bulletin_source_and_term_connection() -> None:
    catalog = load_json("data/catalog/executive_sources.json")
    # The bulletin source was registered at stage 1; stage 3 adds no
    # catalog record, so the version and count are unchanged.
    assert catalog["version"] == "0.68.0"
    assert len(catalog["records"]) == 203
    source = next(
        record for record in catalog["records"] if record["id"] == BULLETIN_ID
    )
    assert source["municipality_key"] == "yamagata-city"
    assert source["organization"] == "山形市選挙管理委員会"
    assert source["category"] == "election"
    assert source["url"] == BULLETIN_URL
    assert source["availability"] == "published"
    assert source["review_status"] == "reviewed"
    assert source["confidence"] == "high"
    assert SHA256 in source["notes"]
    assert OFFICIAL_URL in source["notes"]
    assert "ダイジェスト照合はできなかった" in source["notes"]

    terms = load_json("data/entities/executives/executive_terms.json")
    term = next(record for record in terms if record["id"] == TERM_ID)
    assert term["person_name"] == "佐藤 孝弘"
    assert term["election_date"] == "2023-09-10"
    assert term["term_start"] == "2023-09-28"
    assert term["term_end"] == "2027-09-27"
    assert term["manifesto_source_ids"] == [BULLETIN_ID]
    assert BULLETIN_ID in term["sources"]


def test_search_and_review_records() -> None:
    searches = load_json(
        "data/entities/executives/manifesto_source_searches.json"
    )
    assert len(searches) == 43
    search = next(record for record in searches if record["id"] == SEARCH_ID)
    assert search["executive_term_id"] == TERM_ID
    assert search["result_status"] == "source_registered"
    assert search["manifesto_source_ids_found"] == [BULLETIN_ID]
    assert search["nonexistence_claim"] is False
    assert search["confidence"] == "high"
    assert BULLETIN_ID in search["checked_source_ids"]
    assert SHA256 in search["review_note"]
    assert "ダイジェスト照合はできなかった" in search["review_note"]

    reviews = load_json("data/entities/executives/manifesto_reviews.json")
    assert len(reviews) == 38
    review = next(record for record in reviews if record["id"] == REVIEW_ID)
    assert review["executive_term_id"] == TERM_ID
    assert review["source_id"] == BULLETIN_ID
    assert review["candidate_name"] == "佐藤 孝弘"
    assert review["review_scope"] == "candidate_panel"
    assert review["statement_boundary"] == "mixed"
    assert review["segmentation_status"] == "segmented"
    assert review["promise_records_created"] == 7
    assert "結びの文章" in review["review_note"]
    assert "プレミアム商品券" in review["review_note"]
    assert "所有者本人のレビューとしては記録しない" in review["review_note"]

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

    review_packets = {
        packet["subject_id"]: packet
        for packet in load_json(
            "data/entities/executives/manifesto_review_evidence_packets.json"
        )
    }
    assert len(review_packets) == 38
    review_packet = review_packets[REVIEW_ID]
    assert review_packet["id"] == "evidence-yamagata-city-2023-manifesto-review"
    assert review_packet["subject_type"] == "manifesto_review"
    segmentation = next(
        claim
        for claim in review_packet["claims"]
        if claim["field"] == "segmentation_status"
    )
    assert "7件" in segmentation["statement"]
    provenance = next(
        claim
        for claim in review_packet["claims"]
        if claim["field"] == "source_provenance"
    )
    assert SHA256 in provenance["statement"]
    assert "ダイジェスト照合はできていない" in provenance["statement"]
    authority = next(
        claim
        for claim in review_packet["claims"]
        if claim["field"] == "review_authority"
    )
    assert "所有者本人のレビューとしては記録しない" in authority["statement"]


def test_registry_totals() -> None:
    all_promises = load_json("data/entities/executives/promises.json")
    assert len(all_promises) == 580
    all_packets = load_json(
        "data/entities/executives/promise_evidence_packets.json"
    )
    assert len(all_packets) == 580
    assert {packet["subject_id"] for packet in all_packets} == {
        record["id"] for record in all_promises
    }
