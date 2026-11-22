"""Issue #973: register Niigata City mayor's election-bulletin promises.

The promises come from the official election bulletin (選挙公報)
issued by the Niigata City election commission for the 25 October
2026 mayoral election, which re-elected Nakahara Yaichi.  The
bulletin is a scanned document (the candidate panels are images with
no text layer), so the registered texts were transcribed visually
from rendered pages at 150dpi and 300dpi and cross-checked.  The
candidate panel presents three pillars with 17 bullet items, plus a
clearly labelled past-achievements section (「2期8年の主な実績」, 10
items) that is excluded from the promise records.  The pillar
headlines are slogan-style topic labels, so following the Kyoto City
precedent they are not registered as records of their own and are
kept in source_location.  The 2026 PDF was re-downloaded from the
commission's current official page and hash-matched against the
stage-0 copy (SHA-256
dfea42ed4bcbf64a3d47f2be88990a17f3c2ef1bc3d3ce0b607c77ba770810ca).
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

BULLETIN_ID = "niigata-city-mayor-election-2026-bulletin"
BULLETIN_URL = (
    "https://www.city.niigata.lg.jp/shisei/senkyo/oshirase/sityou/"
    "r8sityousenkyo.files/2026kouhousiken.pdf"
)
SHA256 = "dfea42ed4bcbf64a3d47f2be88990a17f3c2ef1bc3d3ce0b607c77ba770810ca"
TERM_ID = "jp-local-151009-executive-2026-11-18"
SEARCH_ID = "manifesto-source-search-niigata-city-2026"
REVIEW_ID = "manifesto-review-jp-local-151009-2026"

PROJ = "jp-local-151009-project-2025-"

# (original_text, plain_summary, policy_area, linked project suffix)
EXPECTED = [
    ("アリーナを新設し市民に新たな楽しみや感動を与えます",
     "アリーナを新設し、市民に新たな楽しみや感動を与える。",
     "urban_development_and_tourism", "urban-functions-hub"),
    ("起業・創業などのチャレンジを全力で応援します",
     "起業・創業などのチャレンジを全力で応援する。",
     "industry_and_economy", "business-growth"),
    ("アニメ産業の拠点として発展を目指します",
     "アニメ産業の拠点として発展を目指す。",
     "industry_and_economy", "business-growth"),
    ("食関連企業の集積などフードテック分野の拠点形成を目指します",
     "食関連企業の集積など、フードテック分野の拠点形成を目指す。",
     "industry_and_economy", "business-growth"),
    ("攻めの観光で交流人口、関係人口を拡大させます",
     "攻めの観光で交流人口・関係人口を拡大させる。",
     "urban_development_and_tourism", "exchange-population"),
    ("米、野菜、果物など市産農産物をもっと全国にPRします",
     "米・野菜・果物など市産農産物を全国にもっとPRする。",
     "industry_and_economy", "profitable-agriculture"),
    ("若者の出会いの場や新たに結婚した人たちの新生活を一層支援します",
     "若者の出会いの場や、新たに結婚した人たちの新生活を一層支援する。",
     "childcare_and_childrearing", "childcare-talent"),
    ("希望する人が安心して妊娠、出産、子育てができるよう切れ目なく取り組みます",
     "希望する人が安心して妊娠・出産・子育てができるよう、切れ目なく取り組む。",
     "childcare_and_childrearing", "childcare-talent"),
    ("「小1の壁」解消に向け放課後児童クラブの預かり時間延長などを実施します",
     "「小1の壁」解消に向け、放課後児童クラブの預かり時間延長などを実施する。",
     "childcare_and_childrearing", "childcare-talent"),
    ("子どもの遊び場、学習スペースなど子どもの居場所づくりを一層推進します",
     "子どもの遊び場・学習スペースなど、子どもの居場所づくりを一層推進する。",
     "childcare_and_childrearing", "childcare-talent"),
    ("小中学校等の体育館の空調整備を進めます",
     "小中学校等の体育館の空調整備を進める。",
     "education_and_human_development", "childcare-talent"),
    ("いきいきとした生活に向けフレイル予防を推進します",
     "いきいきとした生活に向け、フレイル予防を推進する。",
     "health_welfare_and_community", "inclusive-society"),
    ("高齢者向けワクチン予防接種助成をさらに充実させます",
     "高齢者向けワクチン予防接種助成をさらに充実させる。",
     "health_welfare_and_community", None),
    ("買い物や通院が困難な地域の課題解決に取り組みます",
     "買い物や通院が困難な地域の課題解決に取り組む。",
     "health_welfare_and_community", "inclusive-society"),
    ("「踊り文化」や「マンガ・アニメ文化」を生かしたまちづくりを推進します",
     "「踊り文化」や「マンガ・アニメ文化」を生かしたまちづくりを推進する。",
     "urban_development_and_tourism", "exchange-population"),
    ("地震や大雨、大雪などの災害にしっかりと備えるまちづくりを進めます",
     "地震や大雨、大雪などの災害にしっかりと備えるまちづくりを進める。",
     "safety_and_disaster_prevention", "disaster-resilient-city"),
    ("液状化対策事業の住民負担軽減を含む事業要件を見直します",
     "液状化対策事業の住民負担軽減を含む事業要件を見直す。",
     "safety_and_disaster_prevention", "disaster-resilient-city"),
]

PILLARS = [
    "柱1「若者や女性を応援し夢や希望をもてるまち」",
    "柱2「みんなで支える子育てのまち」「子どもの豊かな学びを支えるまち」",
    "柱3「誰もがいきいきと安心して暮らせ誇りがもてるまち」",
]

# Past achievements presented in the panel's 「2期8年の主な実績」
# section; none of them may appear as promise records.
ACHIEVEMENTS = [
    "財政集中改革で危機的状況から回復",
    "新型コロナワクチン接種率全国3位",
    "妊産婦医療費助成の所得制限撤廃",
    "産後ケア助成を政令市トップレベルに引き上げ",
    "こども医療費助成を高校3年生まで拡充",
    "中学校の全員給食化",
    "にいがた2km企業誘致50社以上",
    "新潟駅高架化、駅下バスターミナル運用開始",
    "バスタ新潟、万代島ルート線沼垂道路、新潟西道路事業化",
    "越後線上所駅設置",
]

EXPECTED_LINKS = {
    PROJ + suffix: [
        f"{TERM_ID}-promise-{index:03d}"
        for index, (_, _, _, link) in enumerate(EXPECTED, start=1)
        if link == suffix
    ]
    for suffix in {
        link for (_, _, _, link) in EXPECTED if link is not None
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


def test_seventeen_promises_in_panel_order() -> None:
    records = promises()
    assert len(records) == 17
    for index, (record, expected) in enumerate(
        zip(records, EXPECTED, strict=True), start=1
    ):
        text, summary, area, link = expected
        assert record["id"] == f"{TERM_ID}-promise-{index:03d}"
        assert record["municipality_id"] == "jp-local-151009"
        assert record["original_text"] == text
        assert record["plain_summary"] == summary
        assert record["policy_area"] == area
        pillar = PILLARS[0 if index <= 6 else 1 if index <= 11 else 2]
        item_no = index if index <= 6 else index - 6 if index <= 11 else index - 11
        assert record["source_location"] == (
            f"選挙公報1ページ目・中原八一候補欄の{pillar}の項目{item_no}"
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
        assert record["related_project_ids"] == (
            [PROJ + link] if link else []
        )


def test_policy_area_distribution() -> None:
    counts = Counter(record["policy_area"] for record in promises())
    assert counts == Counter(
        {
            "childcare_and_childrearing": 4,
            "education_and_human_development": 1,
            "industry_and_economy": 4,
            "urban_development_and_tourism": 3,
            "health_welfare_and_community": 3,
            "safety_and_disaster_prevention": 2,
        }
    )


def test_no_fabricated_numbers_and_no_achievements() -> None:
    texts = [record["original_text"] for record in promises()]
    # The only figures in the panel sit in the achievements section
    # (接種率全国3位, 50社以上) and the profile; the promise items
    # carry no numbers, targets or deadlines of their own.
    for record in promises():
        assert record["target"] is None
        assert record["deadline"] is None
    joined = "\n".join(texts)
    for achievement in ACHIEVEMENTS:
        assert achievement not in joined
    # Panel headings, slogan and profile lines are not promises.
    for fragment in (
        "輝きを増す新潟",
        "市政をもっと前へ",
        "実行・実現力",
        "実現に全力",
        "明治大学",
        "新潟西高校",
        "国土交通大臣政務官",
        "昭和34年",
    ):
        assert fragment not in joined
    # The unlinked promise records why no stage-2 strategy fits.
    unlinked = promises()[12]
    assert unlinked["id"].endswith("promise-013")
    assert "予防接種助成" in unlinked["extraction_note"]
    assert "事業接続は行っていない" in unlinked["extraction_note"]


def test_project_links_bidirectional_and_capped() -> None:
    records = {record["id"]: record for record in promises()}
    linked = [
        record for record in records.values() if record["related_project_ids"]
    ]
    assert len(linked) == 16
    projects = {
        project["id"]: project
        for project in load_json("data/reviewed/niigata-city/projects.json")
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
            "evidence-niigata-city-2026-"
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
        assert "150dpi" in provenance["statement"]
        boundary = next(
            claim
            for claim in packet["claims"]
            if claim["field"] == "original_text"
        )
        assert "2期8年の主な実績" in boundary["review_note"]
        assert "プロフィール欄" in boundary["review_note"]


def test_bulletin_source_and_term_connection() -> None:
    catalog = load_json("data/catalog/executive_sources.json")
    assert catalog["version"] == "0.60.0"
    assert len(catalog["records"]) == 172
    source = next(
        record for record in catalog["records"] if record["id"] == BULLETIN_ID
    )
    assert source["municipality_key"] == "niigata-city"
    assert source["organization"] == "新潟市選挙管理委員会"
    assert source["category"] == "election"
    assert source["url"] == BULLETIN_URL
    assert source["availability"] == "published"
    assert source["review_status"] == "reviewed"
    assert source["confidence"] == "high"
    assert SHA256 in source["notes"]

    terms = load_json("data/entities/executives/executive_terms.json")
    term = next(record for record in terms if record["id"] == TERM_ID)
    assert term["person_name"] == "中原 八一"
    assert term["election_date"] == "2026-10-25"
    assert term["term_start"] == "2026-11-18"
    assert term["term_end"] == "2030-11-17"
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
    assert SHA256 in search["review_note"]

    reviews = load_json("data/entities/executives/manifesto_reviews.json")
    review = next(record for record in reviews if record["id"] == REVIEW_ID)
    assert review["executive_term_id"] == TERM_ID
    assert review["source_id"] == BULLETIN_ID
    assert review["candidate_name"] == "中原 八一"
    assert review["review_scope"] == "candidate_panel"
    assert review["statement_boundary"] == "mixed"
    assert review["segmentation_status"] == "segmented"
    assert review["promise_records_created"] == 17
    assert "除外した実績項目は10件" in review["review_note"]
    for achievement in ACHIEVEMENTS:
        assert achievement in review["review_note"]

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
    review_packet = review_packets[REVIEW_ID]
    assert review_packet["subject_type"] == "manifesto_review"
    segmentation = next(
        claim
        for claim in review_packet["claims"]
        if claim["field"] == "segmentation_status"
    )
    assert "除外は10件" in segmentation["statement"]
    provenance = next(
        claim
        for claim in review_packet["claims"]
        if claim["field"] == "source_provenance"
    )
    assert SHA256 in provenance["statement"]
