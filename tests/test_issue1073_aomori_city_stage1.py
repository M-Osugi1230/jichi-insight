"""Issue #1073: Aomori cluster stage 1 (Aomori City).

Aomori City's FY2022-FY2024 ordinary-account settlements were
already registered under the fiscal-detail expansion programme
(Issue #691), so stage 1 covers only the thousand-yen verification
of the FY2026 initial budget (the registered total matches the
itemised statement exactly, and the local tax is added), the
registration of Mayor Nishi Hideki's current term (a vacancy
election under Article 114, so the term runs four years from the
election day under the main text of Article 259), and the
manifesto source search (the 2023 election bulletin's location
could not be confirmed, so it is recorded honestly as not found;
the full search is stage 3).
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data/reviewed/aomori-city"
MID = "jp-local-022012"
TERM_ID = "jp-local-022012-executive-2023-06-04"
SEARCH_ID = "manifesto-source-search-aomori-city-2023"


def load_json(relative_path: str | Path):
    path = ROOT / relative_path if isinstance(relative_path, str) else relative_path
    return json.loads(path.read_text(encoding="utf-8"))


def test_aomori_city_identity() -> None:
    municipality = load_json(BASE / "municipality.json")

    assert municipality["id"] == MID
    assert municipality["official_code"] == "022012"
    assert municipality["name_ja"] == "青森市"
    assert municipality["municipality_type"] == "core_city"
    assert municipality["data_status"] == "reviewed"


def test_aomori_settlements_were_already_registered() -> None:
    # Stage 1 does not touch the Issue #691 settlements.
    records = load_json(BASE / "settlement_records.json")
    assert len(records) == 51
    assert {record["fiscal_year"] for record in records} == {2022, 2023, 2024}
    packets = load_json(BASE / "settlement_evidence_packets.json")
    assert {packet["subject_id"] for packet in packets} == {
        record["id"] for record in records
    }


def test_aomori_fy2026_budget_verified_and_local_tax_added() -> None:
    records = {r["id"]: r for r in load_json(BASE / "fiscal_records.json")}
    packets = load_json(BASE / "evidence_packets.json")
    assert {p["subject_id"] for p in packets} == set(records)

    # The FY2026 initial-budget total was registered from the
    # million-yen overview; stage 1 verified it against the
    # thousand-yen itemised statement in the same official
    # document (page 26), whose revenue items (23 categories) and
    # expenditure items (14 categories) each sum to exactly
    # 133,510,000 thousand yen, so the registered value is
    # unchanged and no discrepancy was found.
    total = records["jp-local-022012-fiscal-2026-total-expenditure"]
    assert total["amount_yen"] == 133_510_000_000

    # The FY2026 local tax was missing and is added. Bill No. 2
    # passed as proposed (原案可決, majority, 2026-03-24), so the
    # printed proposal value is the enacted value. The June
    # supplementary book (Bill for Supplementary Budget No. 4)
    # also prints the city tax pre-supplement amount as the same
    # 35,906,529 thousand yen with a zero supplement.
    local_tax = records["jp-local-022012-fiscal-2026-local-tax"]
    assert local_tax["stage"] == "initial_budget"
    assert local_tax["metric"] == "local_tax"
    assert local_tax["amount_yen"] == 35_906_529_000
    assert local_tax["sources"] == [
        "aomori-budget-2026-pdf",
        "aomori-budget-2026-council",
    ]
    assert "原案可決" in local_tax["note"]
    revenue_items = [
        35_906_529,  # 市税
        966_170,  # 地方譲与税
        80_089,  # 利子割交付金
        149_096,  # 配当割交付金
        178_903,  # 株式等譲渡所得割交付金
        537_066,  # 法人事業税交付金
        8_523_988,  # 地方消費税交付金
        19_394,  # ゴルフ場利用税交付金
        1,  # 環境性能割交付金
        3_026,  # 国有提供施設等所在市助成交付金
        434_252,  # 地方特例交付金
        29_221_805,  # 地方交付税
        30_193,  # 交通安全対策特別交付金
        371_588,  # 分担金及び負担金
        1_538_360,  # 使用料及び手数料
        28_427_035,  # 国庫支出金
        11_691_248,  # 県支出金
        389_193,  # 財産収入
        1_979_315,  # 寄附金
        4_339_133,  # 繰入金
        1,  # 繰越金
        3_534_915,  # 諸収入
        5_188_700,  # 市債
    ]
    assert sum(revenue_items) * 1000 == total["amount_yen"]


def test_aomori_mayor_term_and_votes() -> None:
    terms = load_json("data/entities/executives/executive_terms.json")
    term = next(t for t in terms if t["municipality_id"] == MID)
    assert term["id"] == TERM_ID
    assert term["person_name"] == "西 秀記"
    # The 2023 election filled the vacancy left by the previous
    # mayor's resignation (Article 114), so under the main text of
    # Article 259 the term runs four years from the election day.
    assert term["term_start"] == "2023-06-04"
    # The expiry is stated directly in the Aomori Prefectural
    # Election Commission's official term-expiry list (2026-11-25
    # edition: 青森市 R9.6.3), which stage 0 had left as an open
    # question and stage 1 resolved.
    assert term["term_end"] == "2027-06-03"
    assert term["election_date"] == "2023-06-04"
    # The bulletin could not be located, so no manifesto source is
    # connected at stage 1 (full search is stage 3).
    assert term["manifesto_source_ids"] == []
    assert len([t for t in terms if t["municipality_id"] == MID]) == 1

    packets = load_json("data/entities/executives/evidence_packets.json")
    packet = next(p for p in packets if p["subject_id"] == term["id"])
    claims = {claim["field"]: claim for claim in packet["claims"]}
    # The vote count has no field on the term record; it is kept in
    # the evidence packet (57,062 votes in the 2023 election per
    # the prefectural election commission's official record,
    # cross-checked against the city commission's result page; the
    # four candidates' votes sum to the valid-vote total 132,334).
    assert "57,062票" in claims["election_date"]["statement"]
    assert "132,334" in claims["election_date"]["statement"]
    assert claims["term_end"]["source_ids"] == [
        "aomori-pref-mayor-term-expiry-list"
    ]
    assert packet["open_questions"]


def test_aomori_manifesto_search_records_not_found() -> None:
    searches = load_json("data/entities/executives/manifesto_source_searches.json")
    search = next(s for s in searches if s["id"] == SEARCH_ID)
    assert search["executive_term_id"] == TERM_ID
    # The bulletin issuance ordinance exists, but the bulletin
    # itself could not be located on the current official pages,
    # in the prefectural election record (which reprints no
    # bulletin) or in the Wayback Machine captures checked at
    # stage 1; this is not a claim of nonexistence.
    assert search["result_status"] == "no_stable_primary_source_found"
    assert search["manifesto_source_ids_found"] == []
    assert search["nonexistence_claim"] is False
    assert "aomori-city-election-bulletin-ordinance" in search["checked_source_ids"]

    packets = load_json(
        "data/entities/executives/manifesto_source_search_evidence_packets.json"
    )
    packet = next(p for p in packets if p["subject_id"] == SEARCH_ID)
    assert packet["review_status"] == "reviewed"
    assert packet["open_questions"]
