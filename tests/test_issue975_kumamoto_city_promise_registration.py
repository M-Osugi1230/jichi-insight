"""Issue #975: 熊本市長（大西一史・2026年選挙公報）の段階3公約登録の検証。

原典は市の公式URLの Wayback Machine 保存コピー（単一保存）のみで、原典性は
保存元URL・ファイルサイズと段階0記録の一致・候補者と公式開票結果との一致で担保する。
公約は2026年12月3日開始の新任期（未登録）のIDを参照し、現任期 term の
manifesto_source_ids は空のまま維持されることをあわせて検証する。
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXECUTIVES = ROOT / "data" / "entities" / "executives"
TERM_ID = "jp-local-431001-executive-2026-12-03"
CURRENT_TERM_ID = "jp-local-431001-executive-2022-12-03"
BULLETIN_ID = "kumamoto-city-mayor-election-2026-bulletin"
SHA256 = "25c13cba040dcb9f6469d3c6df57512cbdf32eca013ef9adb0f66c7506335ca3"

DISASTER = "jp-local-431001-project-2024-disaster-prevention-mitigation"
TRANSPORT = "jp-local-431001-project-2024-wide-area-transport-network"
EDUCATION = "jp-local-431001-project-2024-child-centered-education"
CHILDCARE = "jp-local-431001-project-2024-child-growth-family-support"

EXPECTED_TEXTS = [
    "災害・復興政策を貫く原則は、『制度に被災者を合わせるのではなく、被災者に制度を合わせる。待つ支援から、見つけて届ける支援へ。』です。発災前は住宅と都市を強くする。発災時は確実に生命を守る。避難中は健康と尊厳を守る。発災後は制度からこぼれる人を出さず、生活再建まで伴走します。",
    "慢性的な課題である主要幹線道路のピンポイント渋滞対策やボトルネック解消を強力に進めます。また、発災時には緊急車両の優先通行や広域からの物資輸送・避難誘導をスムーズに行える防災交通システムの構築を目指します。",
    "上下水道管路、浄水・配水施設、道路、橋梁、法面、学校、保育所、福祉施設、市営住宅、文化施設の耐震化・老朽化対策を進めます。",
    "全市立小中学校の体育館等について、空調設備（エアコン）は令和9年度末までの整備完了を目標に整備します。",
    "こども医療費助成、多子世帯への保育料等支援、子育て応援ギフト等を充実します。学校給食費については、任期中の中学校までの完全無償化を目指します。",
    "子育てと仕事を両立させる社会の実現のため、テレワークや短時間勤務など多様な働き方を先進的に導入している『子育て支援優良企業』を広く周知し、社会全体で子育てを支える機運醸成を図ります。",
    "公共交通の速達性と定時性を抜本的に高め、道路を拡幅することなく既存の道路空間を最大限に活用するため、市電の軌道敷をバスやBRTも走行できる公共交通専用走行空間として活用する検討に着手します。",
    "熊本地域の貴重な財産である、良質で豊富な地下水を次世代に確実に継承するために、熊本市地下水保全条例の見直しを行うなど地下水保全対策に取り組みます。",
    "大規模災害時に市役所そのものが機能を失えば、市民の生命と暮らしを守る災害対応にも重大な支障が生じます。大規模災害が起きても、司令塔（市役所）が止まらない。災害対策本部が機能し続ける。現在、耐震改修、減築、災害対策機能の整備、新庁舎整備など、複数の選択肢について専門家による検証を進めています。必要な機能は確実に守り、削ることのできる規模とコストは徹底して削ります。目指すのは『立派な市役所』ではありません。どのような災害が起きても市民を守るために機能し続ける、強い防災拠点です。",
]

EXPECTED_LINKS = {
    1: [DISASTER],
    2: [TRANSPORT],
    3: [DISASTER],
    4: [EDUCATION],
    5: [CHILDCARE],
    6: [CHILDCARE],
    7: [TRANSPORT],
    8: [],
    9: [DISASTER],
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def promise_id(index: int) -> str:
    return f"{TERM_ID}-promise-{index:03d}"


def test_bulletin_source_registered_from_single_wayback_capture() -> None:
    catalog = load_json(ROOT / "data" / "catalog" / "executive_sources.json")
    assert catalog["version"] == "0.64.0"
    assert len(catalog["records"]) == 185
    assert len(catalog["records"]) == 185
    by_id = {record["id"]: record for record in catalog["records"]}
    bulletin = by_id[BULLETIN_ID]
    assert bulletin["municipality_key"] == "kumamoto-city"
    assert bulletin["category"] == "election"
    assert bulletin["organization"] == "熊本市選挙管理委員会／保存は Internet Archive"
    assert bulletin["url"] == (
        "https://web.archive.org/web/20261102235209/"
        "https://www.city.kumamoto.jp/kiji00373652/3_73652_523075_up_xnlivmyb.pdf"
    )
    assert "1,895,508バイト" in bulletin["notes"]
    assert SHA256 in bulletin["notes"]


def test_current_term_keeps_empty_manifesto_sources() -> None:
    terms = load_json(EXECUTIVES / "executive_terms.json")
    assert len(terms) == 40
    by_id = {term["id"]: term for term in terms}
    # 新任期は開始前（2026-12-03）のため term レコード自体を登録しない。
    assert TERM_ID not in by_id
    current = by_id[CURRENT_TERM_ID]
    assert current["person_name"] == "大西 一史"
    assert current["term_start"] == "2022-12-03"
    assert current["term_end"] == "2026-12-02"
    # 現任期は2022年選挙に基づくため、2026年公報は接続しない。
    assert current["manifesto_source_ids"] == []


def test_search_and_review_records() -> None:
    searches = load_json(EXECUTIVES / "manifesto_source_searches.json")
    assert len(searches) == 40
    search = {record["id"]: record for record in searches}[
        "manifesto-source-search-kumamoto-city-2026"
    ]
    assert search["executive_term_id"] == TERM_ID
    assert search["result_status"] == "source_registered"
    assert search["manifesto_source_ids_found"] == [BULLETIN_ID]
    assert "kumamoto-city-mayor-election-results-2026" in search["checked_source_ids"]
    assert "kumamoto-pref-mayor-term-expiry-list" in search["checked_source_ids"]
    assert search["nonexistence_claim"] is False
    assert "manifesto_source_ids へ接続する" in search["review_note"]

    reviews = load_json(EXECUTIVES / "manifesto_reviews.json")
    assert len(reviews) == 32
    review = {record["id"]: record for record in reviews}[
        "manifesto-review-jp-local-431001-2026"
    ]
    assert review["executive_term_id"] == TERM_ID
    assert review["source_id"] == BULLETIN_ID
    assert review["candidate_name"] == "大西 一史"
    assert review["review_scope"] == "candidate_panel"
    assert review["statement_boundary"] == "mixed"
    assert review["segmentation_status"] == "segmented"
    assert review["promise_records_created"] == 9
    # 候補欄に実績提示項目はないため、実績を理由とする除外は0件である。
    assert "実績提示を理由とする除外は0件" in review["review_note"]


def test_promises_registered_from_bulletin_panel() -> None:
    promises = load_json(EXECUTIVES / "promises.json")
    assert len(promises) == 492
    own = [p for p in promises if p["executive_term_id"] == TERM_ID]
    assert [p["id"] for p in own] == [promise_id(i) for i in range(1, 10)]
    for index, promise in enumerate(own, start=1):
        assert promise["municipality_id"] == "jp-local-431001"
        assert promise["original_text"] == EXPECTED_TEXTS[index - 1]
        assert promise["sources"] == [BULLETIN_ID]
        assert promise["review_status"] == "reviewed"
        assert promise["confidence"] == "high"
        assert promise["related_project_ids"] == EXPECTED_LINKS[index]
        # 新任期は開始前のため、全件 not_started とする。
        assert promise["progress_state"] == "not_started"
        # deadline は全公約で未使用の項目であり、任期満了日も期限として登録しない。
        assert promise["deadline"] is None
        assert promise["funding_statement"] is None
    by_id = {p["id"]: p for p in own}
    # 〈9/150〉は整備対象と達成時期が明示された specific_commitment。
    gym = by_id[promise_id(4)]
    assert gym["statement_type"] == "specific_commitment"
    assert gym["assessability"] == "assessable"
    assert gym["target"] is not None and "令和9年度末" in gym["target"]
    # 〈28/150〉の給食費無償化は公報が「任期中」と明示する目標として target に登録する。
    lunch = by_id[promise_id(5)]
    assert lunch["target"] is not None and "完全無償化" in lunch["target"]
    for index in (1, 2, 3, 6, 7, 8, 9):
        assert by_id[promise_id(index)]["statement_type"] == "directional_commitment"
        assert by_id[promise_id(index)]["assessability"] == "partially_assessable"
    # 番号付き抜粋項目の extraction_note には全マニフェストの項目番号を保持する。
    for index, number in ((2, 2), (3, 8), (4, 9), (5, 28), (6, 30), (7, 64), (8, 113)):
        assert f"〈{number}/150〉" in by_id[promise_id(index)]["extraction_note"]


def test_promise_evidence_packets_document_provenance_and_term_handover() -> None:
    packets = load_json(EXECUTIVES / "promise_evidence_packets.json")
    assert len(packets) == 492
    own = {p["subject_id"]: p for p in packets if p["subject_id"].startswith(TERM_ID)}
    assert set(own) == {promise_id(i) for i in range(1, 10)}
    for index, packet in own.items():
        number = int(index.rsplit("-", 1)[1])
        assert packet["id"] == f"evidence-kumamoto-city-2026-promise-{number:03d}"
        fields = [claim["field"] for claim in packet["claims"]]
        assert fields[:2] == ["original_text", "source_provenance"]
        provenance = packet["claims"][1]["statement"]
        assert "Wayback Machine 保存コピー（2026年11月2日保存）" in provenance
        assert SHA256 in provenance
        assert "1,895,508バイト" in provenance
        # 新任期 term 登録時に manifesto_source_ids へ接続する旨を全パケットに明記する。
        assert any("manifesto_source_ids へ接続する" in q for q in packet["open_questions"])
        if EXPECTED_LINKS[number]:
            assert fields[2] == "related_project_ids"
            link_claim = packet["claims"][2]
            assert link_claim["decision"] == "needs_review"
            assert "low / inferred" in link_claim["review_note"]
        else:
            assert len(packet["claims"]) == 2
            assert any("接続は行っていない" in q for q in packet["open_questions"])


def test_search_and_review_evidence_packets() -> None:
    search_packets = load_json(EXECUTIVES / "manifesto_source_search_evidence_packets.json")
    assert len(search_packets) == 40
    packet = {p["id"]: p for p in search_packets}[
        "evidence-manifesto-source-search-kumamoto-city-2026"
    ]
    assert packet["subject_id"] == "manifesto-source-search-kumamoto-city-2026"
    assert [c["field"] for c in packet["claims"]] == [
        "checked_source_ids",
        "manifesto_source_ids_found",
        "result_status",
    ]
    assert any("manifesto_source_ids へ接続する" in q for q in packet["open_questions"])

    review_packets = load_json(EXECUTIVES / "manifesto_review_evidence_packets.json")
    assert len(review_packets) == 32
    review_packet = {p["id"]: p for p in review_packets}[
        "evidence-kumamoto-city-2026-manifesto-review"
    ]
    assert review_packet["subject_id"] == "manifesto-review-jp-local-431001-2026"
    assert [c["field"] for c in review_packet["claims"]] == [
        "source_location",
        "segmentation_status",
        "source_provenance",
    ]
    assert any("空のまま維持する" in q for q in review_packet["open_questions"])


def test_project_reverse_links() -> None:
    projects = load_json(ROOT / "data" / "reviewed" / "kumamoto-city" / "projects.json")
    by_id = {p["id"]: p for p in projects}
    assert by_id[DISASTER]["related_promise_ids"] == [
        promise_id(1),
        promise_id(3),
        promise_id(9),
    ]
    assert by_id[TRANSPORT]["related_promise_ids"] == [promise_id(2), promise_id(7)]
    assert by_id[EDUCATION]["related_promise_ids"] == [promise_id(4)]
    assert by_id[CHILDCARE]["related_promise_ids"] == [promise_id(5), promise_id(6)]
    linked = {DISASTER, TRANSPORT, EDUCATION, CHILDCARE}
    for project_id, project in by_id.items():
        if project_id not in linked:
            assert project["related_promise_ids"] == []
