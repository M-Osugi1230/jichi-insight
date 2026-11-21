"""Cluster 8 stage 4: Kobe City assembly registration checks.

Pins the counts and cross-checks for the Kobe City Council data taken
from the September part of the 2nd regular session of Reiwa 8
(2026-09-11 to 2026-10-23 conclusions), the FY2025 political activity
expense reports, and the committee / overseas inspection trips.
"""

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "reviewed" / "kobe-city" / "assembly"
CATALOG = ROOT / "data" / "catalog" / "kobe_city_assembly_sources.json"
ASM = "jp-local-281000-assembly-2023"
SESSION = f"{ASM}-session-2026-09"
INDEPENDENTS = {"平野章三", "上原みなみ"}
FACTION_COUNTS = {
    "自由民主党神戸市会議員団・無所属の会": 15,
    "公明党神戸市会議員団": 12,
    "日本維新の会神戸市会議員団": 12,
    "日本共産党神戸市会議員団": 9,
    "こうべ未来市会議員団": 7,
    "躍動の会神戸市会議員団": 2,
    "つなぐ神戸市会議員団": 2,
    "新しい自民党神戸市会議員団": 2,
}


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def load_schema(name):
    return json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))


def validate(schema_name, records):
    schema = load_schema(schema_name)
    for record in records:
        jsonschema.validate(record, schema)


def test_catalog_is_valid_and_unique():
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    jsonschema.validate(catalog, load_schema("source_catalog.schema.json"))
    records = catalog["records"]
    ids = [entry["id"] for entry in records]
    assert len(ids) == len(set(ids))
    assert all(entry["municipality_key"] == "kobe-city" for entry in records)
    assert len(records) == 44


def test_assembly_record():
    records = load("assembly_records.json")
    validate("assembly.schema.json", records)
    assert len(records) == 1
    record = records[0]
    assert record["id"] == ASM
    assert record["municipality_id"] == "jp-local-281000"
    assert record["seat_count"] == 65
    assert record["term_start"] == "2023-04-30"
    assert record["term_end"] == "2027-04-29"
    # Roster of 2026-08-04: 63 sitting members, 2 seats vacant.
    assert sum(f["member_count"] for f in record["factions"]) == 63
    by_name = {f["name"]: f["member_count"] for f in record["factions"]}
    expected = dict(FACTION_COUNTS)
    expected["無所属"] = 2
    assert by_name == expected


def test_session():
    sessions = load("sessions.json")
    validate("session.schema.json", sessions)
    assert len(sessions) == 1
    session = sessions[0]
    assert session["id"] == SESSION
    assert session["name"] == "令和8年第2回定例市会"
    # The session formally runs to 2026-12-08 (89 days, including the
    # November part); only the September part is registered here.
    assert session["start_date"] == "2026-09-11"
    assert session["end_date"] == "2026-12-08"


def test_proposals():
    proposals = load("proposals.json")
    validate("proposal.schema.json", proposals)
    assert len(proposals) == 79
    kinds = {}
    for p in proposals:
        kinds[p["kind"]] = kinds.get(p["kind"], 0) + 1
    assert kinds == {
        "settlement": 19,
        "budget": 3,
        "ordinance": 4,
        "resolution": 1,
        "personnel": 2,
        "petition": 36,
        "other": 14,
    }
    assert sum(1 for p in proposals if p["submitted_by"] == "executive") == 39
    assert sum(1 for p in proposals if p["submitted_by"] == "member") == 2
    assert (
        sum(1 for p in proposals if p["submitted_by"] == "resident_petition")
        == 36
    )
    assert sum(1 for p in proposals if p["submitted_by"] == "other") == 2
    by_number = {}
    for p in proposals:
        by_number.setdefault(p["proposal_number"], []).append(p)
    # All FY2025 settlements were certified on 2026-10-23.
    for n in range(1, 20):
        p = by_number[f"決算第{n}号"][0]
        assert p["outcome"] == "approved"
        assert p["decided_at"] == "2026-10-23"
        assert p["submitted_at"] == "2026-09-11"
    # Supplementary budgets: nos. 20-21 on 2026-09-17, no. 22 later.
    assert by_number["予算第20号議案"][0]["decided_at"] == "2026-09-17"
    assert by_number["予算第22号議案"][0]["decided_at"] == "2026-10-23"
    assert by_number["予算第22号議案"][0]["submitted_at"] == "2026-10-16"
    # Both petitions to the plenary were rejected.
    for number in ("請願第14号", "請願第15号"):
        assert by_number[number][0]["outcome"] == "rejected"
        assert by_number[number][0]["decided_at"] == "2026-10-23"
    # Petitions decided in committee: 28 rejected, 6 closed without a
    # conclusion (審査打切 -> not_assessable).
    appeals = [p for p in proposals if p["proposal_number"].startswith("陳情")]
    assert len(appeals) == 34
    assert sum(1 for p in appeals if p["outcome"] == "rejected") == 28
    assert sum(1 for p in appeals if p["outcome"] == "not_assessable") == 6
    closed = {p["proposal_number"] for p in appeals if p["outcome"] == "not_assessable"}
    assert closed == {
        "陳情第216号", "陳情第221号", "陳情第234号",
        "陳情第235号", "陳情第240号", "陳情第241号",
    }


def test_votes():
    votes = load("votes.json")
    validate("vote.schema.json", votes)
    proposals = {p["id"]: p for p in load("proposals.json")}
    assert len(votes) == 79
    assert {v["proposal_id"] for v in votes} == set(proposals)
    for vote in votes:
        assert vote["method"] == "unknown"
        assert vote["totals"] is None
        prop = proposals[vote["proposal_id"]]
        assert prop["decided_at"] == vote["vote_date"]
        assert prop["outcome"] == vote["outcome"]
    # Only the election item and the session-length item have no
    # published vote breakdown.
    unpublished = {
        proposals[v["proposal_id"]]["title"]
        for v in votes
        if v["member_vote_availability"] == "not_published"
    }
    assert unpublished == {"西区選挙管理委員及び同補充員選挙の件", "会期決定の件"}
    member_votes = [mv for v in votes for mv in v["member_votes"]]
    assert len(member_votes) == 92
    assert {mv["member_name"] for mv in member_votes} == INDEPENDENTS
    # Plenary votes with a published breakdown carry both independents
    # (43 items x 2; the election and session-length items have none);
    # committee petition votes only ever name 上原みなみ.
    plenary = [
        v for v in votes
        if not proposals[v["proposal_id"]]["proposal_number"].startswith("陳情")
    ]
    assert sum(len(v["member_votes"]) for v in plenary) == 86
    appeals = [
        v for v in votes
        if proposals[v["proposal_id"]]["proposal_number"].startswith("陳情")
    ]
    assert sum(len(v["member_votes"]) for v in appeals) == 6


def test_faction_votes():
    faction_votes = load("faction_votes.json")
    validate("faction_vote.schema.json", faction_votes)
    votes = {v["id"]: v for v in load("votes.json")}
    proposals = {p["id"]: p for p in load("proposals.json")}
    # 43 plenary items x 8 factions = 344; petition items contribute
    # one record per faction sitting on the deciding committee.
    plenary_fv = [
        fv for fv in faction_votes
        if not proposals[votes[fv["vote_id"]]["proposal_id"]][
            "proposal_number"
        ].startswith("陳情")
    ]
    appeal_fv = [fv for fv in faction_votes if fv not in plenary_fv]
    assert len(plenary_fv) == 344
    assert len(appeal_fv) == 203
    assert len(faction_votes) == 547
    for fv in faction_votes:
        assert fv["for_count"] is None
        assert fv["against_count"] is None
        assert fv["member_count"] == FACTION_COUNTS[fv["faction_name"]]
    # Every plenary vote (except the two without a breakdown) has all
    # eight factions.
    for vote in votes.values():
        prop = proposals[vote["proposal_id"]]
        if prop["proposal_number"].startswith("陳情"):
            continue
        count = sum(1 for fv in faction_votes if fv["vote_id"] == vote["id"])
        if vote["member_vote_availability"] == "not_published":
            assert count == 0
        else:
            assert count == 8


def test_divided_votes():
    proposals = {p["proposal_number"]: p for p in load("proposals.json")}
    votes = {v["proposal_id"]: v for v in load("votes.json")}
    faction_votes = load("faction_votes.json")
    short = {
        "自由民主党神戸市会議員団・無所属の会": "自民",
        "公明党神戸市会議員団": "公明",
        "日本維新の会神戸市会議員団": "維新",
        "日本共産党神戸市会議員団": "共産",
        "こうべ未来市会議員団": "こうべ",
        "躍動の会神戸市会議員団": "躍動",
        "つなぐ神戸市会議員団": "つなぐ",
        "新しい自民党神戸市会議員団": "新自民",
    }

    def positions(number):
        vote = votes[proposals[number]["id"]]
        result = {
            short[fv["faction_name"]]: fv["position"]
            for fv in faction_votes
            if fv["vote_id"] == vote["id"]
        }
        result.update(
            {mv["member_name"]: mv["position"] for mv in vote["member_votes"]}
        )
        return result

    # Personnel item (education board): the Communist Party opposed,
    # everyone else supported (9月17日賛否一覧, 号外 row). The two
    # 号外 items share a proposal_number, so search the full list.
    personnel = next(
        p for p in load("proposals.json")
        if p["title"] == "神戸市教育委員会委員任命の件"
    )
    vote = votes[personnel["id"]]
    pos = {
        short[fv["faction_name"]]: fv["position"]
        for fv in faction_votes
        if fv["vote_id"] == vote["id"]
    }
    pos.update({mv["member_name"]: mv["position"] for mv in vote["member_votes"]})
    assert pos["共産"] == "against"
    assert pos["自民"] == "for"
    assert pos["平野章三"] == "for"
    # Budget no. 22: 平野章三 opposed while 上原みなみ supported.
    pos = positions("予算第22号議案")
    assert pos["平野章三"] == "against"
    assert pos["上原みなみ"] == "for"
    assert pos["共産"] == "against"
    # Petition no. 218 (committee): the Communist Party and つなぐ
    # supported adoption; the petition was rejected.
    pos = positions("陳情第218号")
    assert pos["共産"] == "for"
    assert pos["つなぐ"] == "for"
    assert pos["自民"] == "against"
    assert proposals["陳情第218号"]["outcome"] == "rejected"
    # Petition no. 216 was closed (審査打切): every recorded position
    # is the undecidable □ mark, registered as unknown.
    pos = positions("陳情第216号")
    assert pos and all(v == "unknown" for v in pos.values())


def test_expenses():
    expenses = load("political_activity_expenses.json")
    validate("political_activity_expense.schema.json", expenses)
    assert len(expenses) == 13
    assert all(r["fiscal_year"] == 2025 for r in expenses)
    assert sum(1 for r in expenses if r["recipient_type"] == "faction") == 8
    assert sum(1 for r in expenses if r["recipient_type"] == "member") == 5
    assert all(r["receipt_access"] == "online" for r in expenses)
    assert all(r["report_status"] == "published" for r in expenses)
    for record in expenses:
        # Category amounts always sum to the printed expense total,
        # and grant + other income - spent equals the returned amount
        # via the verified source values.
        assert (
            sum(i["amount_yen"] for i in record["breakdown"])
            == record["spent_yen"]
        ), record["recipient_name"]
        assert len(record["breakdown"]) == 10
    by_name = {r["recipient_name"]: r for r in expenses}
    jimin = by_name["自由民主党神戸市会議員団・無所属の会"]
    assert jimin["granted_yen"] == 81780000
    assert jimin["spent_yen"] == 67795000
    assert jimin["returned_yen"] == 13987534
    # Komei values are the corrected ones (2026-08-07 amendment):
    # PR/publicity spending was reduced and the balance grew.
    komei = by_name["公明党神戸市会議員団"]
    assert komei["granted_yen"] == 58800000
    assert komei["spent_yen"] == 54377297
    assert komei["returned_yen"] == 4422703
    # Hirano spent exactly the full income, returning nothing.
    hirano = by_name["平野章三"]
    assert hirano["returned_yen"] == 0
    assert hirano["spent_yen"] == 4561074


def test_inspection_trips():
    trips = load("inspection_trips.json")
    validate("inspection_trip.schema.json", trips)
    assert len(trips) == 18
    domestic = [t for t in trips if t["trip_type"] == "domestic"]
    overseas = [t for t in trips if t["trip_type"] == "overseas"]
    assert len(domestic) == 11
    assert len(overseas) == 7
    assert all(t["cost_status"] == "not_published" for t in trips)
    assert all(t["report_status"] == "published" for t in trips)
    # Committee trip reports name no participants; only the external
    # organisations committee's study trip prints a headcount (13).
    for trip in domestic:
        assert trip["participants"] == []
    counted = [t for t in domestic if t["participant_count"] is not None]
    assert len(counted) == 1
    assert counted[0]["participant_count"] == 13
    assert "外郭団体に関する特別委員会" in counted[0]["title"]
    # The two joint overseas delegations list nine members each.
    joint = [t for t in overseas if t["participant_count"] == 9]
    assert len(joint) == 2
    for trip in joint:
        assert len(trip["participants"]) == 9
        assert all(
            p["funding_status"] == "political_activity_expense"
            for p in trip["participants"]
        )
    korea = [t for t in overseas if t["destinations"][0] == "仁川広域市"]
    assert len(korea) == 4


def test_disclosure_profile():
    profiles = load("disclosure_profiles.json")
    validate("disclosure_profile.schema.json", profiles)
    assert len(profiles) == 1
    items = {item["item"]: item for item in profiles[0]["items"]}
    assert len(items) == 12
    assert items["faction_votes"]["availability"] == "published"
    assert items["member_votes"]["availability"] == "published"
    # Receipts are published online in Kobe, unlike in Chiba.
    assert (
        items["political_activity_expense_receipts"]["availability"]
        == "published"
    )
    assert items["petition_results"]["availability"] == "published"


def test_evidence_packets():
    validate("evidence_packet.schema.json", load("assembly_evidence_packets.json"))
    validate(
        "evidence_packet.schema.json", load("proposal_vote_evidence_packets.json")
    )
    validate("evidence_packet.schema.json", load("expense_evidence_packets.json"))
    validate(
        "evidence_packet.schema.json", load("inspection_evidence_packets.json")
    )
    assembly_packets = load("assembly_evidence_packets.json")
    assert len(assembly_packets) == 1
    assert len(assembly_packets[0]["open_questions"]) == 3
    assert len(load("proposal_vote_evidence_packets.json")) == 79
    assert len(load("expense_evidence_packets.json")) == 13
    assert len(load("inspection_evidence_packets.json")) == 18
    # The Komei packet documents the 2026-08-07 correction.
    expenses = {r["id"]: r for r in load("political_activity_expenses.json")}
    packets = {p["subject_id"]: p for p in load("expense_evidence_packets.json")}
    komei = next(
        r for r in expenses.values() if r["recipient_name"] == "公明党神戸市会議員団"
    )
    statements = " ".join(
        c["statement"] for c in packets[komei["id"]]["claims"]
    )
    assert "修正" in statements
    assert "10,972,148円" in statements
