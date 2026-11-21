"""Issue #904: 静岡クラスター段階4・浜松市議会の登録を固定する。

対象は令和8年第3回定例会（2026年9月7日〜10月26日）。賛否は市の議員賛否一覧による
議員個人別の公式公表が正本であり、議長（渥美誠）は全件で議決不参加（excused）と
して登録する。発議案（意見書）は番号と議員別賛否が公表されないため、番号を
推測で割り当てず票も作らない。陳情は本会期中に議会運営委員会で審査され不採択と
なった第12〜14号のみを登録する。
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "reviewed" / "hamamatsu-city" / "assembly"
CATALOG = ROOT / "data" / "catalog" / "hamamatsu_city_assembly_sources.json"
ASSEMBLY_ID = "jp-local-221309-assembly-2023"
SESSION_ID = f"{ASSEMBLY_ID}-session-2026-3"


def load(name: str) -> list[dict]:
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def test_assembly_record() -> None:
    records = load("assembly_records.json")
    assert len(records) == 1
    record = records[0]
    assert record["id"] == ASSEMBLY_ID
    assert record["municipality_id"] == "jp-local-221309"
    assert record["name"] == "浜松市議会"
    assert record["seats"] == 46
    assert record["members_count"] == 44
    assert record["chair_name"] == "渥美誠"
    assert record["vice_chair_name"] == "平野岳子"
    assert record["term_start"] == "2023-05-01"
    assert record["term_end"] == "2027-04-30"
    factions = {f["name"]: f["member_count"] for f in record["factions"]}
    assert factions == {
        "自由民主党浜松": 23,
        "公明党": 5,
        "市民クラブ": 6,
        "創造浜松・国民民主党浜松": 5,
        "日本共産党浜松市議団": 3,
        "浜松市政向上委員会": 1,
        "市民サポート浜松": 1,
    }
    assert sum(factions.values()) == 44


def test_session_record() -> None:
    sessions = load("sessions.json")
    assert len(sessions) == 1
    session = sessions[0]
    assert session["id"] == SESSION_ID
    assert session["name"] == "令和8年第3回定例会（9月定例会）"
    assert session["starts_on"] == "2026-09-07"
    assert session["ends_on"] == "2026-10-26"


def test_proposals_cover_plenary_opinions_and_petitions() -> None:
    proposals = load("proposals.json")
    assert len(proposals) == 69
    kinds = Counter(p["kind"] for p in proposals)
    assert kinds == {
        "budget": 5,
        "ordinance": 12,
        "other": 28,
        "settlement": 15,
        "personnel": 2,
        "resolution": 4,
        "petition": 3,
    }
    by_number = {p["proposal_number"]: p for p in proposals}
    first = by_number["第91号議案"]
    assert first["title"] == "令和８年度浜松市一般会計補正予算（第４号）"
    assert first["submitted_at"] == "2026-09-07"
    assert first["decided_at"] == "2026-09-14"
    assert first["outcome"] == "approved"
    settlement = by_number["認第4号"]
    assert settlement["title"] == "令和７年度浜松市一般会計歳入歳出決算"
    assert settlement["submitted_at"] == "2026-09-14"
    assert settlement["decided_at"] == "2026-10-26"
    assert settlement["outcome"] == "approved"
    # 令和7年度決算は全件が同会期で認定されている。
    settlements = [p for p in proposals if p["kind"] == "settlement"]
    assert len(settlements) == 15
    assert all(p["outcome"] == "approved" for p in settlements)
    personnel = by_number["選第5号"]
    assert personnel["decided_at"] == "2026-09-28"
    assert personnel["outcome"] == "approved"
    # 意見書は番号が公表されないため推測で割り当てない。
    opinions = [p for p in proposals if p["kind"] == "resolution"]
    assert {p["title"] for p in opinions} == {
        "大規模データセンターに関わる法整備を求める意見書",
        "化学物質過敏症に関する対策強化を求める意見書",
        "市街化調整区域における廃校等公共施設の利活用推進及び規制緩和等を求める意見書",
        "孤立妊産婦と乳幼児の命を守る法整備を求める意見書",
    }
    assert all(p["proposal_number"] == "発議案" for p in opinions)
    assert all(p["decided_at"] == "2026-10-26" for p in opinions)
    # 陳情は本会期中に委員会審査で不採択となった3件のみ。審査日は公表されない。
    petitions = [p for p in proposals if p["kind"] == "petition"]
    assert {p["proposal_number"] for p in petitions} == {"陳情第12号", "陳情第13号", "陳情第14号"}
    assert all(p["outcome"] == "rejected" for p in petitions)
    assert all(p["submitted_at"] == "2026-08-21" for p in petitions)
    assert all(p["decided_at"] is None for p in petitions)


def test_votes_are_member_level_with_chair_excused() -> None:
    proposals = {p["id"]: p for p in load("proposals.json")}
    votes = load("votes.json")
    assert len(votes) == 62
    assert {v["proposal_id"] for v in votes} == {
        p["id"] for p in proposals.values() if p["kind"] != "resolution" and p["kind"] != "petition"
    }
    member_votes = [mv for v in votes for mv in v["member_votes"]]
    assert len(member_votes) == 62 * 44
    positions = Counter(mv["position"] for mv in member_votes)
    assert positions == {"for": 2642, "against": 24, "excused": 62}
    # 議長は全件で議決不参加。
    chair = [mv for mv in member_votes if mv["member_name"] == "渥美誠"]
    assert len(chair) == 62
    assert all(mv["position"] == "excused" for mv in chair)
    # 表決方法は公表資料にないため unknown に統一する。
    assert {v["method"] for v in votes} == {"unknown"}
    assert {v["member_vote_availability"] for v in votes} == {"published"}
    for vote in votes:
        assert vote["vote_date"] == proposals[vote["proposal_id"]]["decided_at"]
        assert vote["outcome"] == "approved"
        assert len(vote["member_votes"]) == 44
        counted = Counter(
            mv["position"] for mv in vote["member_votes"] if mv["position"] != "excused"
        )
        assert vote["totals"] == {
            "for": counted.get("for", 0),
            "against": counted.get("against", 0),
            "abstained": counted.get("abstained", 0),
            "absent": counted.get("absent", 0),
        }


def test_divided_votes_are_the_eight_recorded_items() -> None:
    proposals = {p["id"]: p for p in load("proposals.json")}
    votes = load("votes.json")
    divided = {
        proposals[v["proposal_id"]]["proposal_number"]
        for v in votes
        if v["totals"]["against"] > 0
    }
    assert divided == {
        "第91号議案",
        "第98号議案",
        "第99号議案",
        "第101号議案",
        "認第2号",
        "認第4号",
        "認第7号",
        "認第13号",
    }
    for vote in votes:
        if vote["totals"]["against"]:
            assert vote["totals"] == {"for": 40, "against": 3, "abstained": 0, "absent": 0}
            opponents = {
                mv["member_name"] for mv in vote["member_votes"] if mv["position"] == "against"
            }
            assert opponents == {"酒井豊実", "小黒啓子", "北島定"}


def test_no_faction_votes_because_member_votes_are_the_publication() -> None:
    assert load("faction_votes.json") == []


def test_political_activity_expenses_fy2025() -> None:
    expenses = load("political_activity_expenses.json")
    assert len(expenses) == 7
    assert {e["fiscal_year"] for e in expenses} == {2025}
    assert {e["recipient_type"] for e in expenses} == {"faction"}
    assert sum(e["granted_yen"] for e in expenses) == 80_700_000
    assert sum(e["spent_yen"] for e in expenses) == 67_887_533
    assert sum(e["returned_yen"] for e in expenses) == 12_945_902
    for expense in expenses:
        assert sum(b["amount_yen"] for b in expense["breakdown"]) == expense["spent_yen"]
        assert len(expense["breakdown"]) == 10
    by_name = {e["recipient_name"]: e for e in expenses}
    jimin = by_name["自由民主党浜松"]
    assert jimin["granted_yen"] == 41_400_000
    assert jimin["spent_yen"] == 32_989_533
    assert jimin["returned_yen"] == 8_443_331
    # 創造浜松は支出が収入を上回り、返納額は預金利息分のみが公表値どおり。
    sozo = by_name["創造浜松・国民民主党浜松"]
    assert sozo["granted_yen"] == 9_000_000
    assert sozo["spent_yen"] == 9_075_930
    assert sozo["returned_yen"] == 4_095


def test_inspection_trips_are_an_explicit_gap() -> None:
    assert load("inspection_trips.json") == []
    assert load("inspection_evidence_packets.json") == []
    profiles = load("disclosure_profiles.json")
    assert len(profiles) == 1
    items = {i["item"]: i for i in profiles[0]["items"]}
    assert items["inspection_trip_reports"]["availability"] == "not_published"
    assert items["member_votes"]["availability"] == "published"
    assert items["faction_votes"]["availability"] == "not_published"
    assert items["petition_results"]["availability"] == "published"


def test_evidence_packets_record_open_questions() -> None:
    packets = load("assembly_evidence_packets.json")
    assert len(packets) == 1
    assert packets[0]["subject_id"] == ASSEMBLY_ID
    assert len(packets[0]["open_questions"]) >= 3
    vote_packets = load("proposal_vote_evidence_packets.json")
    assert len(vote_packets) == 1
    assert vote_packets[0]["subject_id"] == SESSION_ID
    expense_packets = load("expense_evidence_packets.json")
    assert len(expense_packets) == 1


def test_source_catalog_is_registered() -> None:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    ids = {r["id"] for r in catalog["records"]}
    assert len(catalog["records"]) == 13
    assert "hamamatsu-city-assembly-member-votes-2026-3" in ids
    assert "hamamatsu-city-assembly-seimu-fy2025" in ids
    used = set()
    for name in (
        "assembly_records.json",
        "sessions.json",
        "proposals.json",
        "votes.json",
        "political_activity_expenses.json",
        "disclosure_profiles.json",
    ):
        for record in load(name):
            used.update(record["sources"])
    assert used <= ids
