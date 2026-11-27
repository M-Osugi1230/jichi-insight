"""Issue #1086: register Iwate governor's election-bulletin promises.

The promises come from the election bulletin (選挙公報) issued by
the Iwate Prefectural election commission for the 3 September 2023
gubernatorial election, which re-elected Tasso Takuya to a fifth
term.  The prefectural commission's current official page no longer
carries the bulletin, so a digest match against the official
original was not possible.  Registration therefore uses the copy of
the same bulletin held on the Go2Senkyo CDN, whose content was
verified at stage 1 (Issue #1070) and whose file was re-downloaded
at stage 3 and hash-matched against the stage-1 verified copy
(SHA-256 f3aaa408eb193158adff848019cb1dec29130e525b0253bdc7ee3d98f88a71a7).
The candidate panel presents the "Manifesto+39" digest as six
thematic blocks, each a headline statement plus three to four
checked detail lines; following the Yamagata City precedent, each
block is registered as one record with the headline and its details
joined by newlines.  The bulletin prints only a digest: the 39
policies themselves are not itemised in the bulletin (details are
referred to the candidate's website), so no per-policy records are
created.  The panel headline, the vertical message text and the
footnote explaining the plan relationship are not promise records.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

BULLETIN_ID = "iwate-pref-governor-election-2023-bulletin"
BULLETIN_URL = (
    "https://prod-cdn.go2senkyo.com/public/senkyo_koho/24278/"
    "20230903岩手県知事選挙.pdf"
)
SHA256 = "f3aaa408eb193158adff848019cb1dec29130e525b0253bdc7ee3d98f88a71a7"
TERM_ID = "jp-local-030007-executive-2023-09-11"
SEARCH_ID = "manifesto-source-search-iwate-pref-2023"
REVIEW_ID = "manifesto-review-jp-local-030007-2023"

PROJ = "jp-local-030007-project-2019-"

# (original_text, plain_summary, policy_area, linked project suffixes)
EXPECTED = [
    (
        "全国トップクラスの支援策がスタート、家庭・地域・経済の好循環へ\n"
        "3歳未満の保育料 ▶ 第2子から無料（所得制限なし）\n"
        "子ども医療費 負担軽減 ▶ 高校生まで対象拡大（現物給付）\n"
        "子育て支援 ▶ 子育て施策のフル稼働と一層の拡充へ\n"
        "教育 ▶ バランスのとれた学校教育、学力の育成へICTの効果的活用",
        "子育て支援と教育を拡充し、家庭・地域・経済の好循環を目指す。3歳未満の保育料を第2子から無料（所得制限なし）とし、子ども医療費の負担軽減の対象を高校生まで拡大する（現物給付）。子育て施策のフル稼働と一層の拡充を図り、バランスのとれた学校教育と学力の育成へICTの効果的活用を進める。",
        "childcare_and_childrearing",
        ["family-childrearing", "education"],
    ),
    (
        "農林水産業、ものづくり、観光産業、GX、DXと岩手の特性を強みへ\n"
        "中小企業 ▶ 採用・賃上げ、働き方改革、施設整備への支援拡充\n"
        "産業人材 ▶ 産業技術短期大学校を県北地域に新設\n"
        "農林水産業 ▶ トップセールスによる販路拡大、輸出促進\n"
        "観光 ▶ いま世界的に注目される盛岡を起点に県内全体へ誘客拡大",
        "農林水産業、ものづくり、観光産業、GX、DXと岩手の特性を強みにする。中小企業の採用・賃上げ、働き方改革、施設整備への支援を拡充し、産業技術短期大学校を県北地域に新設する。農林水産業はトップセールスによる販路拡大と輸出促進を、観光は世界的に注目される盛岡を起点に県内全体への誘客拡大を図る。",
        "industry_and_economy",
        ["work-income"],
    ),
    (
        "全国的にリードしてきた地域医療を守る取組をさらに強化へ\n"
        "全県的な医療提供体制の拡充 ▶ 周産期医療の強化、県立病院体制の充実\n"
        "リハビリテーションセンター ▶ サテライト施設を沿岸地域に整備\n"
        "スポーツ医科学センターを新設 ▶ 競技スポーツ・介護予防等推進\n"
        "「地域医療基本法（仮称）」 ▶ 医師確保に向け、新法早期制定を国に働きかけ",
        "地域医療を守る取組をさらに強化する。全県的な医療提供体制の拡充として周産期医療の強化と県立病院体制の充実を図り、リハビリテーションセンターのサテライト施設を沿岸地域に整備する。スポーツ医科学センターを新設して競技スポーツ・介護予防等を推進し、医師確保に向け「地域医療基本法（仮称）」の早期制定を国に働きかける。",
        "health_welfare_and_community",
        ["health-leisure"],
    ),
    (
        "県民一人ひとりが「幸福」を追求し、実感できる社会の創出へ\n"
        "若者女性活躍 ▶ 「若者カフェ」を設置、女性活躍推進へ環境づくり\n"
        "パートナーシップ制度 ▶ 導入する市町村を県が積極的に支援\n"
        "結婚支援 ▶ 結婚サポートセンター「i-サポ」の活用で成婚数向上へ\n"
        "障がい者支援施設「中山の園」 ▶ インクルーシブの視点から整備",
        "県民一人ひとりが「幸福」を追求し、実感できる社会を創出する。「若者カフェ」を設置し女性活躍推進へ環境づくりを進め、パートナーシップ制度を導入する市町村を県が積極的に支援する。結婚サポートセンター「i-サポ」の活用で成婚数向上を図り、障がい者支援施設「中山の園」をインクルーシブの視点から整備する。",
        "universal_city_and_inclusion",
        ["participation"],
    ),
    (
        "省エネルギー・再生可能エネルギー推進でハイレベルな目標達成へ\n"
        "温室効果ガス削減目標 57%（2013→2030）の達成（国の目標46%）\n"
        "農林水産業の振興 ▶ 岩手の強みを活かしたCO2吸収源対策の推進\n"
        "三陸沖に洋上風力発電・波力発電の導入促進 ▶ 港湾エリア整備、産業の集積、"
        "観光・レジャー産業の創出",
        "省エネルギー・再生可能エネルギーの推進でハイレベルな目標達成を目指す。温室効果ガス削減目標57%（2013→2030、国の目標46%）の達成を掲げ、岩手の強みを活かしたCO2吸収源対策を推進する。三陸沖に洋上風力発電・波力発電の導入を促進し、港湾エリア整備、産業の集積、観光・レジャー産業の創出につなげる。",
        "environment_and_climate",
        ["natural-environment"],
    ),
    (
        "復興事業の成果を活かし「新しい三陸・岩手」の創造へ\n"
        "復興、その先へ。 ▶ 三陸振興をプロデュースする「まちづくり会社」設立\n"
        "日本海溝・千島海溝沿いの巨大地震 ▶ 命を守る防災・減災対策\n"
        "沿岸と内陸を結ぶ路線 ▶ 道路ネットワーク（北・北道路等）の整備・強化\n"
        "ILCの実現 ▶ 国際的な議論を主導するよう政府に積極的な働きかけ",
        "復興事業の成果を活かし「新しい三陸・岩手」の創造を目指す。三陸振興をプロデュースする「まちづくり会社」を設立し、日本海溝・千島海溝沿いの巨大地震に備える防災・減災対策を進める。沿岸と内陸を結ぶ道路ネットワークの整備・強化を図り、ILCの実現に向けて国際的な議論を主導するよう政府に積極的な働きかけを行う。",
        "transport_infrastructure",
        ["social-infrastructure", "safety"],
    ),
]

BLOCK_LABELS = [
    "はぐくむ（子育て支援・教育）",
    "はたらく（産業振興・働き方改革と所得向上）",
    "いきる（地域医療と命・健康）",
    "つながる（若者女性活躍・参画・ジェンダー）",
    "まもる（環境・地球温暖化対策）",
    "ひらく（復興・社会基盤整備）",
]

EXPECTED_LINKS = {
    PROJ + "family-childrearing": [f"{TERM_ID}-promise-001"],
    PROJ + "education": [f"{TERM_ID}-promise-001"],
    PROJ + "work-income": [f"{TERM_ID}-promise-002"],
    PROJ + "health-leisure": [f"{TERM_ID}-promise-003"],
    PROJ + "participation": [f"{TERM_ID}-promise-004"],
    PROJ + "natural-environment": [f"{TERM_ID}-promise-005"],
    PROJ + "social-infrastructure": [f"{TERM_ID}-promise-006"],
    PROJ + "safety": [f"{TERM_ID}-promise-006"],
}


def load_json(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def promises() -> list[dict]:
    records = [
        record
        for record in load_json("data/entities/executives/promises.json")
        if record["executive_term_id"] == TERM_ID
    ]
    return sorted(records, key=lambda record: record["id"])


def packet_index() -> dict[str, dict]:
    return {
        packet["subject_id"]: packet
        for packet in load_json(
            "data/entities/executives/promise_evidence_packets.json"
        )
    }


def test_six_promises_in_panel_order() -> None:
    records = promises()
    assert len(records) == 6
    for index, (record, expected) in enumerate(
        zip(records, EXPECTED, strict=True), start=1
    ):
        text, summary, area, links = expected
        assert record["id"] == f"{TERM_ID}-promise-{index:03d}"
        assert record["municipality_id"] == "jp-local-030007"
        assert record["original_text"] == text
        assert record["plain_summary"] == summary
        assert record["policy_area"] == area
        assert record["source_location"] == (
            "選挙公報2ページ目・たっそ拓也候補欄の「マニフェスト＋39」"
            f"ダイジェストの主題ブロック「{BLOCK_LABELS[index - 1]}」"
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
            "childcare_and_childrearing": 1,
            "industry_and_economy": 1,
            "health_welfare_and_community": 1,
            "universal_city_and_inclusion": 1,
            "environment_and_climate": 1,
            "transport_infrastructure": 1,
        }
    )


def test_no_non_promise_panel_content() -> None:
    joined = "\n".join(record["original_text"] for record in promises())
    # Panel headline, the vertical message text, the footnote and the
    # profile are framing statements, not promise records; the other
    # candidate's panel is out of scope as well.  The bulletin prints
    # only a digest, so the 39 policies are not itemised anywhere in
    # the registered texts.
    for fragment in (
        "希望郷いわて",
        "県民の『生活』と『幸福』のために",
        "人口減少・少子化に立ち向かい",
        "誰ひとり取り残さない",
        "大攻勢をかける次の4年間",
        "たっそ拓也プロフィール",
        "県民の知恵と力を合わせて作った",
        "千葉じゅんこ",
        "新しい岩手をつくる",
    ):
        assert fragment not in joined
    # The only numeric target in the six blocks sits inside the
    # environment block's detail lines; it is not a block-level
    # target, so target/deadline/funding stay null on every record.
    for record in promises():
        assert record["target"] is None
        assert record["deadline"] is None
        assert record["funding_statement"] is None
    assert "57%" in promises()[4]["original_text"]


def test_project_links_bidirectional_and_capped() -> None:
    records = {record["id"]: record for record in promises()}
    linked = [
        record for record in records.values() if record["related_project_ids"]
    ]
    assert len(linked) == 6
    projects = {
        project["id"]: project
        for project in load_json("data/reviewed/iwate-prefecture/projects.json")
    }
    for project_id, promise_ids in EXPECTED_LINKS.items():
        assert projects[project_id]["related_promise_ids"] == promise_ids
    unlinked = [
        project_id
        for project_id, project in projects.items()
        if project["related_promise_ids"] == []
    ]
    assert len(unlinked) == 10 - len(EXPECTED_LINKS)
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
            "evidence-iwate-pref-2023-"
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
        assert "希望郷いわて" in boundary["review_note"]
        assert "6つの主題ブロック" in boundary["review_note"]


def test_bulletin_source_and_term_connection() -> None:
    catalog = load_json("data/catalog/executive_sources.json")
    # The bulletin source was registered at stage 1; stage 3 adds no
    # catalog record for Iwate Prefecture.  (The catalog total itself
    # moved on with the Morioka stage-3 registration, PR #1091; the
    # global version and count pins live in the shared catalog tests.)
    iwate_ids = sorted(
        record["id"]
        for record in catalog["records"]
        if record["id"].startswith("iwate-pref-")
    )
    assert iwate_ids == [
        "iwate-pref-governor",
        "iwate-pref-governor-election-2023-ballot-count",
        "iwate-pref-governor-election-2023-bulletin",
        "iwate-pref-governor-election-2023-winner-notice",
        "iwate-pref-governor-term-list",
        "iwate-pref-mayor-term-expiry-list",
    ]
    source = next(
        record for record in catalog["records"] if record["id"] == BULLETIN_ID
    )
    assert source["municipality_key"] == "iwate-prefecture"
    assert source["organization"] == "岩手県選挙管理委員会"
    assert source["category"] == "election"
    assert source["url"] == BULLETIN_URL
    assert source["availability"] == "published"
    assert source["review_status"] == "reviewed"
    assert source["confidence"] == "high"
    assert SHA256 in source["notes"]
    assert "ダイジェストによる原典との同一性照合は行えていない" in source["notes"]

    terms = load_json("data/entities/executives/executive_terms.json")
    term = next(record for record in terms if record["id"] == TERM_ID)
    assert term["person_name"] == "達増 拓也"
    assert term["election_date"] == "2023-09-03"
    assert term["term_start"] == "2023-09-11"
    assert term["term_end"] == "2027-09-10"
    assert term["manifesto_source_ids"] == [BULLETIN_ID]
    assert BULLETIN_ID in term["sources"]


def test_search_and_review_records() -> None:
    searches = load_json(
        "data/entities/executives/manifesto_source_searches.json"
    )
    assert len(searches) == 47
    search = next(record for record in searches if record["id"] == SEARCH_ID)
    assert search["executive_term_id"] == TERM_ID
    assert search["result_status"] == "source_registered"
    assert search["manifesto_source_ids_found"] == [BULLETIN_ID]
    assert search["nonexistence_claim"] is False
    assert search["confidence"] == "high"
    assert BULLETIN_ID in search["checked_source_ids"]
    assert SHA256 in search["review_note"]
    assert "ダイジェストによる原典との同一性照合は行えていない" in search["review_note"]

    reviews = load_json("data/entities/executives/manifesto_reviews.json")
    assert len(reviews) == 40
    review = next(record for record in reviews if record["id"] == REVIEW_ID)
    assert review["executive_term_id"] == TERM_ID
    assert review["source_id"] == BULLETIN_ID
    assert review["candidate_name"] == "達増 拓也"
    assert review["review_scope"] == "candidate_panel"
    assert review["statement_boundary"] == "mixed"
    assert review["segmentation_status"] == "segmented"
    assert review["promise_records_created"] == 6
    assert "ダイジェスト" in review["review_note"]
    assert "39政策の全項目は公報に掲載されていない" in review["review_note"]
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
    assert len(review_packets) == 40
    review_packet = review_packets[REVIEW_ID]
    assert review_packet["id"] == "evidence-iwate-pref-2023-manifesto-review"
    assert review_packet["subject_type"] == "manifesto_review"
    segmentation = next(
        claim
        for claim in review_packet["claims"]
        if claim["field"] == "segmentation_status"
    )
    assert "6件" in segmentation["statement"]
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
    assert len(all_promises) == 597
    all_packets = load_json(
        "data/entities/executives/promise_evidence_packets.json"
    )
    assert len(all_packets) == 597
    assert {packet["subject_id"] for packet in all_packets} == {
        record["id"] for record in all_promises
    }
