"""Contract tests for the Kawasaki City assembly registration (Issue #804).

The 2026 3rd regular session publishes its vote results as per-category
PDF tables whose columns are the five factions plus the five unaffiliated
members by name, with the literal cell values 賛成 / 反対 / 退席.
Political activity expenses have no web publication at all (the ordinance
provides only in-person inspection at the speaker's office), so the
expense file is an intentional empty list backed by a gap packet.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "reviewed" / "kawasaki-city" / "assembly"
ASSEMBLY_ID = "jp-local-141305-assembly-2023"
SESSION_ID = "jp-local-141305-assembly-2023-session-2026-3"

FACTION_COUNTS = {
    "自由民主党川崎市議会議員団": 16,
    "みらい川崎市議会議員団": 14,
    "公明党川崎市議会議員団": 11,
    "日本共産党川崎市議会議員団": 8,
    "あしたの川崎・日本維新の会川崎市議会議員団": 5,
}
INDEPENDENTS = ["三浦恵美", "飯田満", "三宅隆介", "月本琢也", "吉沢章子"]


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def assert_valid(schema_rel: str, instance: object) -> None:
    schema = load_json(ROOT / schema_rel)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(instance), key=lambda e: list(e.path))
    assert errors == [], f"{schema_rel}: {[e.message for e in errors]}"


def catalog_record_ids() -> set[str]:
    ids: set[str] = set()
    for path in (ROOT / "data" / "catalog").glob("*.json"):
        value = load_json(path)
        if isinstance(value, dict) and isinstance(value.get("records"), list):
            ids.update(
                record["id"]
                for record in value["records"]
                if isinstance(record, dict) and isinstance(record.get("id"), str)
            )
    return ids


def test_kawasaki_catalog_is_valid() -> None:
    catalog = load_json(ROOT / "data" / "catalog" / "kawasaki_city_assembly_sources.json")
    assert_valid("schemas/source_catalog.schema.json", catalog)
    assert catalog["version"] == "0.1.0"
    assert catalog["scope"] == "pilot"
    assert len(catalog["records"]) == 16
    assert len({r["id"] for r in catalog["records"]}) == 16
    assert {r["municipality_key"] for r in catalog["records"]} == {"kawasaki-city"}


def test_kawasaki_assembly_and_session_match_contracts() -> None:
    records = load_json(BASE / "assembly_records.json")
    sessions = load_json(BASE / "sessions.json")
    packets = load_json(BASE / "assembly_evidence_packets.json")

    assert len(records) == 1
    assembly = records[0]
    assert_valid("schemas/assembly.schema.json", assembly)
    assert assembly["id"] == ASSEMBLY_ID
    assert assembly["municipality_id"] == "jp-local-141305"
    # Term end is printed day-exact by the city election commission; the
    # start is the day after the previous term expired (2023-05-02).
    assert assembly["term_start"] == "2023-05-03"
    assert assembly["term_end"] == "2027-05-02"
    assert assembly["seat_count"] == 60
    # 59 sitting members (one vacancy), including the five unaffiliated.
    assert sum(f["member_count"] for f in assembly["factions"]) == 59
    assert len(assembly["committees"]) == 9

    assert len(sessions) == 1
    assert_valid("schemas/session.schema.json", sessions[0])
    assert sessions[0]["id"] == SESSION_ID
    assert sessions[0]["start_date"] == "2026-08-31"
    assert sessions[0]["end_date"] == "2026-10-13"

    assert {p["subject_type"] for p in packets} == {
        "assembly",
        "session",
        "disclosure_profile",
    }
    for packet in packets:
        assert_valid("schemas/evidence_packet.schema.json", packet)


def test_kawasaki_proposals_match_contract() -> None:
    proposals = load_json(BASE / "proposals.json")
    packets = load_json(BASE / "proposal_vote_evidence_packets.json")
    known_sources = catalog_record_ids()

    assert len(proposals) == 69
    kinds = Counter(p["kind"] for p in proposals)
    assert kinds == {
        "ordinance": 24,
        "settlement": 19,
        "budget": 8,
        "personnel": 4,
        "resolution": 6,
        "amendment": 1,
        "petition": 1,
        "other": 6,
    }
    outcomes = Counter(p["outcome"] for p in proposals)
    assert outcomes == {"approved": 59, "rejected": 5, "not_assessable": 5}
    for proposal in proposals:
        assert_valid("schemas/proposal.schema.json", proposal)
        assert proposal["assembly_id"] == ASSEMBLY_ID
        assert proposal["session_id"] == SESSION_ID
        assert proposal["related_fiscal_record_ids"] == []
        for source_id in proposal["sources"]:
            assert source_id in known_sources
    by_number = {p["proposal_number"]: p for p in proposals}
    # All 56 mayor-submitted bills were approved in some printed form.
    for n in range(106, 162):
        assert by_number[f"議案第{n}号"]["outcome"] == "approved"
    # Only bill 160 (personnel consent) was decided on the opening day.
    assert by_number["議案第160号"]["decided_at"] == "2026-08-31"
    assert by_number["議案第161号"]["decided_at"] == "2026-10-13"
    # The supplementary resolution and the amendment hang off their bills.
    supplementary = by_number["附帯決議案（議案第120号）"]
    assert supplementary["outcome"] == "approved"
    assert supplementary["parent_proposal_id"] == by_number["議案第120号"]["id"]
    amendment = by_number["修正案（議案第115号）"]
    assert amendment["outcome"] == "rejected"
    assert amendment["parent_proposal_id"] == by_number["議案第115号"]["id"]
    # The petition is the only item with a known submission date (the
    # acceptance list prints it); its vote is on adoption, and it failed.
    petition = by_number["請願第40号"]
    assert petition["submitted_at"] == "2026-06-03"
    assert petition["outcome"] == "rejected"
    for proposal in proposals:
        if proposal["id"] != petition["id"]:
            assert proposal["submitted_at"] is None
    # Reports carry no vote and no decision date in the official list.
    reports = [p for p in proposals if p["proposal_number"].startswith("報告第")]
    assert len(reports) == 5
    for report in reports:
        assert report["outcome"] == "not_assessable"
        assert report["decided_at"] is None
    assert len([p for p in packets if p["subject_type"] == "proposal"]) == 69


def test_kawasaki_votes_match_contract() -> None:
    proposals = load_json(BASE / "proposals.json")
    votes = load_json(BASE / "votes.json")
    faction_votes = load_json(BASE / "faction_votes.json")
    packets = load_json(BASE / "proposal_vote_evidence_packets.json")
    by_number = {p["proposal_number"]: p for p in proposals}
    vote_by_proposal = {v["proposal_id"]: v for v in votes}

    assert len(votes) == 64
    assert len([p for p in packets if p["subject_type"] == "vote"]) == 64
    for proposal in proposals:
        if proposal["outcome"] == "not_assessable":
            assert proposal["id"] not in vote_by_proposal
    abstained_total = 0
    for vote in votes:
        assert_valid("schemas/vote.schema.json", vote)
        # The five unaffiliated members are printed by name, so their
        # positions are registered as member votes; the voting method is
        # not stated and no totals are reconstructed.
        assert vote["member_vote_availability"] == "published"
        assert vote["method"] == "unknown"
        assert vote["totals"] is None
        assert [m["member_name"] for m in vote["member_votes"]] == INDEPENDENTS
        assert vote["vote_date"] in ("2026-08-31", "2026-10-13")
        abstained_total += sum(
            1 for m in vote["member_votes"] if m["position"] == "abstained"
        )
    # 退席 is printed only for bill 120 and its supplementary resolution,
    # for 飯田満 and 三宅隆介 in both.
    assert abstained_total == 4

    assert len(faction_votes) == 320
    fv_by_vote: dict[str, list[dict]] = {}
    for fv in faction_votes:
        assert_valid("schemas/faction_vote.schema.json", fv)
        fv_by_vote.setdefault(fv["vote_id"], []).append(fv)
    assert len(fv_by_vote) == 64
    for rows in fv_by_vote.values():
        assert len(rows) == 5
        assert {r["faction_name"]: r["member_count"] for r in rows} == FACTION_COUNTS

    def against_factions(number: str) -> set[str]:
        vote = vote_by_proposal[by_number[number]["id"]]
        return {
            r["faction_name"] for r in fv_by_vote[vote["id"]] if r["position"] == "against"
        }

    def member_positions(number: str) -> dict[str, str]:
        vote = vote_by_proposal[by_number[number]["id"]]
        return {m["member_name"]: m["position"] for m in vote["member_votes"]}

    # Bill 115 (funeral ordinance): Communists, Kawasaki-Ishin and all
    # five unaffiliated members against. The inventory note had this
    # pattern swapped with bill 133; the vote table governs.
    assert against_factions("議案第115号") == {
        "日本共産党川崎市議会議員団",
        "あしたの川崎・日本維新の会川崎市議会議員団",
    }
    assert set(member_positions("議案第115号").values()) == {"against"}
    # Bill 133 (general-account supplementary budget): Communists only.
    assert against_factions("議案第133号") == {"日本共産党川崎市議会議員団"}
    assert set(member_positions("議案第133号").values()) == {"for"}
    # Bill 120 and its supplementary resolution share the same pattern,
    # including the two 退席 (registered as abstained).
    for number in ("議案第120号", "附帯決議案（議案第120号）"):
        positions = member_positions(number)
        assert positions["飯田満"] == "abstained"
        assert positions["三宅隆介"] == "abstained"
        assert positions["三浦恵美"] == "against"
    # Bill 141 settlement: 三宅隆介 and 月本琢也 also against.
    positions141 = member_positions("議案第141号")
    assert positions141["三宅隆介"] == "against"
    assert positions141["月本琢也"] == "against"
    assert positions141["三浦恵美"] == "for"
    # Opinion paper 15: LDP and Kawasaki-Ishin against.
    assert against_factions("意見書案第15号") == {
        "自由民主党川崎市議会議員団",
        "あしたの川崎・日本維新の会川崎市議会議員団",
    }
    # Opinion papers 16 and 17: only the Communists in favour.
    for number in ("意見書案第16号", "意見書案第17号"):
        vote = vote_by_proposal[by_number[number]["id"]]
        fors = {
            r["faction_name"] for r in fv_by_vote[vote["id"]] if r["position"] == "for"
        }
        assert fors == {"日本共産党川崎市議会議員団"}
    # Opinion paper 18: only the five unaffiliated members in favour.
    assert set(member_positions("意見書案第18号").values()) == {"for"}
    assert against_factions("意見書案第18号") == set(FACTION_COUNTS)
    # Petition 40: adoption supported by the Communists only.
    vote40 = vote_by_proposal[by_number["請願第40号"]["id"]]
    fors40 = {
        r["faction_name"] for r in fv_by_vote[vote40["id"]] if r["position"] == "for"
    }
    assert fors40 == {"日本共産党川崎市議会議員団"}


def test_kawasaki_expenses_are_an_explicit_gap() -> None:
    expenses = load_json(BASE / "political_activity_expenses.json")
    packets = load_json(BASE / "expense_evidence_packets.json")

    # No reports, receipts or amounts are published on the web: the
    # ordinance (Art. 15) provides only in-person inspection, so the
    # expense list is intentionally empty and a gap packet records the
    # statutory system instead of amounts.
    assert expenses == []
    assert len(packets) == 1
    packet = packets[0]
    assert_valid("schemas/evidence_packet.schema.json", packet)
    assert packet["subject_type"] == "assembly"
    assert packet["subject_id"] == ASSEMBLY_ID


def test_kawasaki_inspection_trips_match_contract() -> None:
    trips = load_json(BASE / "inspection_trips.json")
    packets = load_json(BASE / "inspection_evidence_packets.json")

    assert len(trips) == 3
    assert len(packets) == 3
    assert {p["subject_id"] for p in packets} == {t["id"] for t in trips}
    counts = {t["id"].rsplit("-", 1)[-1]: t["participant_count"] for t in trips}
    assert counts == {"asia": 10, "oceania": 11, "europe": 10}
    for trip in trips:
        assert_valid("schemas/inspection_trip.schema.json", trip)
        assert trip["assembly_id"] == ASSEMBLY_ID
        assert trip["trip_type"] == "overseas"
        assert len(trip["participants"]) == trip["participant_count"]
        # Reports are published on the web; costs are printed nowhere.
        assert trip["report_status"] == "published"
        assert trip["cost_status"] == "not_published"
        assert trip["total_cost_yen"] is None
        assert trip["cost_per_person_yen"] is None
    for packet in packets:
        assert_valid("schemas/evidence_packet.schema.json", packet)


def test_kawasaki_disclosure_profile() -> None:
    profiles = load_json(BASE / "disclosure_profiles.json")
    assert len(profiles) == 1
    profile = profiles[0]
    assert_valid("schemas/disclosure_profile.schema.json", profile)
    assert profile["assembly_id"] == ASSEMBLY_ID
    items = {item["item"]: item for item in profile["items"]}
    assert len(items) == 11
    # Faction votes are published for every voted item.
    assert items["faction_votes"]["availability"] == "published"
    assert items["faction_votes"]["granularity"] == "faction"
    # Member votes are published only for the five unaffiliated members,
    # who appear as named columns in the official table.
    assert items["member_votes"]["availability"] == "published"
    assert items["member_votes"]["granularity"] == "member"
    # Expense reports and receipts are inspection-only, never on the web.
    assert items["political_activity_expense_reports"]["availability"] == "not_published"
    assert items["political_activity_expense_receipts"]["availability"] == "not_published"
    # Overseas delegation reports are published; domestic committee trips
    # have no systematic publication (noted on the item).
    assert items["inspection_trip_reports"]["availability"] == "published"
