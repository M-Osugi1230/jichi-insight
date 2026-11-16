"""Staging tests for the Tottori Phase 15 review candidate.

The candidate stays prepared and unpublished until a human checks the
cited primary sources.  These tests pin the package state, the source
catalog, the plan framework, and the verified fiscal values so that a
promotion change has to be deliberate.  The FY2026 initial budget's own
vote details and the FY2024 settlement certification outcome could not
be read from the council's voting-result PDFs by text fetch; a browser
follow-up confirmed both (the budget as bill 6, passed as proposed on
2026-03-19, and bill 106 certified on 2025-10-06, the latter from the
council meeting record because the voting-result PDF omits bills 106
and 107), and these tests pin the confirmed wording and its basis.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_PATH = ROOT / "data" / "candidates" / "tottori-city" / "review_candidate.json"
INVENTORY_PATH = ROOT / "data" / "indexed" / "tottori-city" / "source_inventory.json"
QUEUE_PATH = ROOT / "data" / "catalog" / "phase15_core_capital_review_queue.json"


def _candidate() -> dict:
    return json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))


def _package() -> dict:
    return _candidate()["candidate_package"]


def test_tottori_candidate_is_prepared_with_delegated_review_approved() -> None:
    candidate = _candidate()
    assert candidate["candidate_id"] == "tottori-phase15-review-candidate"
    assert candidate["official_code"] == "312010"
    assert candidate["name_ja"] == "鳥取市"
    assert candidate["status"] == "review_candidate"
    assert candidate["package_state"] == "prepared"
    assert candidate["human_review"]["required"] is True
    assert candidate["human_review"]["status"] == "approved"
    assert candidate["human_review"]["reviewed_at"] == "2026-11-16"
    assert candidate["human_review"]["reviewer_note"]
    # The owner did not review the primary sources personally: on
    # 2026-11-15 the owner explicitly delegated the review to Muse in
    # chat, and the note must record that delegation rather than
    # claiming an owner review.
    assert "委任" in candidate["human_review"]["reviewer_note"]
    assert "レビューはあなたがやってください" in candidate["human_review"]["reviewer_note"]
    assert candidate["publication"]["eligible"] is False


def test_tottori_candidate_sources_match_phase14_inventory() -> None:
    package_sources = {
        source["id"]: source for source in _package()["source_catalog"]["sources"]
    }
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    inventory_sources = {source["id"]: source for source in inventory["sources"]}
    assert set(package_sources) == set(inventory_sources)
    assert set(package_sources) == {
        "tottori-twelfth-plan",
        "tottori-action-plan-progress",
        "tottori-budget-2026",
        "tottori-settlement-2024",
    }
    for source_id, source in package_sources.items():
        assert source["official_url"] == inventory_sources[source_id]["official_url"]
        assert source["official_url"].startswith("https://www.city.tottori.lg.jp/")
        assert source["verification_status"] == "primary_source_live_verified_2026-11-16"


def test_tottori_plan_review_records_framework_and_transition() -> None:
    records = {record["id"]: record for record in _package()["plan_review"]["records"]}
    assert set(records) == {
        "tottori-current-plan-period",
        "tottori-current-policy-structure",
        "tottori-progress-governance-framework",
        "tottori-plan-transition",
        "tottori-fy2024-settlement-linkage",
    }
    period = records["tottori-current-plan-period"]
    assert period["decision"] == "needs_review"
    assert period["title"].startswith("第12次鳥取市総合計画の構成")
    assert "基本構想2026年度～2035年度" in period["value"]
    assert "毎年度見直し" in period["value"]
    transition = records["tottori-plan-transition"]
    assert "第11次鳥取市総合計画" in transition["statement"]
    assert "基本計画2021年度～2025年度" in transition["statement"]
    linkage = records["tottori-fy2024-settlement-linkage"]
    assert linkage["decision"] == "not_assessable"
    assert linkage["fiscal_year"] == 2024


def test_tottori_policy_structure_keeps_four_goals_and_11_policies() -> None:
    plan = _package()["policy_structure"]["current_plan"]
    assert plan["title"].startswith("第12次鳥取市総合計画 基本計画")
    assert plan["vision"] == (
        "一人ひとりが自分の力を発揮でき、支え合いながら "
        "ともに豊かに暮らせる鳥取市〜オアシスとっとり〜"
    )
    assert plan["start_fiscal_year"] == 2026
    assert plan["end_fiscal_year"] == 2030
    assert plan["period_status"] == "verified_fixed_period"
    goal1 = "まちづくりの目標1 未来を創る人材を育み、ひとりひとりが活躍するまち"
    goal2 = "まちづくりの目標2 誰もが自分らしく暮らし続けることができる、持続可能な地域共生のまち"
    goal3 = "まちづくりの目標3 ひと、もの、ことが行きかい、にぎわいあふれるまち"
    goal4 = "まちづくりの目標4 豊かな自然と調和して、安全・安心に暮らせるまち"
    field_names = [field["name_ja"] for field in plan["policy_fields"]]
    assert field_names == [
        f"{goal1}：政策1 こども",
        f"{goal1}：政策2 教育・スポーツ",
        f"{goal2}：政策1 福祉",
        f"{goal2}：政策2 保健・医療",
        f"{goal2}：政策3 人権・共生・協働",
        f"{goal3}：政策1 商工業・農林水産業",
        f"{goal3}：政策2 移住定住・関係人口・観光",
        f"{goal3}：政策3 文化芸術・文化財",
        f"{goal3}：政策4 生活基盤・市街地・中山間地域・交通",
        f"{goal4}：政策1 防災・防犯",
        f"{goal4}：政策2 環境",
    ]
    assert all(field["measures"] == [] for field in plan["policy_fields"])
    principles = "".join(plan["management_principles"])
    assert "実施計画" in principles
    assert "verified_fixed_period" in principles


def test_tottori_fiscal_records_hold_verified_values() -> None:
    records = {record["id"]: record for record in _package()["fiscal_records"]}
    budget = records["jp-local-312010-fiscal-2026-total-expenditure"]
    assert budget["stage"] == "initial_budget"
    assert budget["amount_yen"] == 108_700_000_000
    assert budget["sources"] == ["tottori-budget-2026"]
    assert "骨格予算" in budget["note"]
    assert "108,700,000千円" in budget["note"]
    assert "千円単位" in budget["note"]
    assert "議案第6号" in budget["note"]
    assert "原案可決" in budget["note"]
    assert "2026年3月19日" in budget["note"]
    revenue = records["jp-local-312010-fiscal-2024-total-revenue"]
    assert revenue["stage"] == "settlement"
    assert revenue["amount_yen"] == 113_544_636_161
    assert revenue["sources"] == ["tottori-settlement-2024"]
    assert "議案第106号" in revenue["note"]
    assert "113,544,636,161円" in revenue["note"]
    assert "2025年10月6日" in revenue["note"]
    assert "会議録" in revenue["note"]
    expenditure = records["jp-local-312010-fiscal-2024-total-expenditure"]
    assert expenditure["amount_yen"] == 111_377_983_188
    assert expenditure["sources"] == ["tottori-settlement-2024"]
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 2_166_652_973


def test_tottori_fy2026_budget_lineage_arithmetic() -> None:
    records = {record["id"]: record for record in _package()["fiscal_records"]}
    budget = records["jp-local-312010-fiscal-2026-total-expenditure"]
    # The enacted initial budget total is pinned at thousand-yen
    # precision through the supplementary budget lineage:
    # initial 108,700,000 -> No.1 108,780,802 (+80,802)
    # -> No.2 111,909,475 (+3,128,673) -> No.3 112,616,424 (+706,949).
    assert 108_700_000 + 80_802 == 108_780_802
    assert 108_780_802 + 3_128_673 == 111_909_475
    assert 111_909_475 + 706_949 == 112_616_424
    assert budget["amount_yen"] == 108_700_000 * 1000
    assert "108,780,802千円" in budget["note"]
    assert "111,909,475千円" in budget["note"]
    assert "112,616,424千円" in budget["note"]
    assert "議案第70号" in budget["note"]


def test_tottori_fy2024_settlement_values_and_real_balance() -> None:
    records = {record["id"]: record for record in _package()["fiscal_records"]}
    revenue = records["jp-local-312010-fiscal-2024-total-revenue"]
    expenditure = records["jp-local-312010-fiscal-2024-total-expenditure"]
    # Values pinned from the official settlement book (単位: 円).
    assert revenue["amount_yen"] == 113_544_636_161
    assert expenditure["amount_yen"] == 111_377_983_188
    # 差引残額 (revenue minus expenditure) matches the same book.
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 2_166_652_973
    # 実質収支 is published only at thousand-yen precision in the
    # settlement statement: 2,166,653 - 149,019 = 2,017,634 (千円).
    assert 2_166_653 - 149_019 == 2_017_634
    assert "2,166,652,973円" in expenditure["note"]
    assert "2,017,634千円" in expenditure["note"]
    assert "149,019千円" in expenditure["note"]
    assert "千円精度のまま" in expenditure["note"]


def test_tottori_fy2024_settlement_certification_is_confirmed() -> None:
    text = CANDIDATE_PATH.read_text(encoding="utf-8")
    assert "議案第106号" in text
    # The certification outcome was confirmed by a browser follow-up in
    # the council meeting record of 2025-10-06: the September session's
    # voting-result PDF omits the rows for bills 106 and 107, so the
    # candidate records the certification with the meeting record as
    # its basis and never claims the PDF wording confirmed it.
    assert "認定された" in text
    assert "2025年10月6日" in text
    assert "会議録" in text
    assert "審議結果』PDFには議案第106号・第107号の行" in text
    assert "未確認" not in text
    assert "不認定" not in text
    assert "修正可決" not in text


def test_tottori_fy2026_budget_vote_details_are_confirmed() -> None:
    packets = {packet["id"]: packet for packet in _package()["evidence_packets"]}
    claim = packets["evidence-tottori-city-2026-total-expenditure"]["claims"][0]
    # The initial budget's own vote was confirmed by a browser follow-up
    # in the council's February session voting results: bill 6, passed
    # as proposed (原案可決) by majority on 2026-03-19.
    assert "議案第6号" in claim["statement"]
    assert "原案可決" in claim["statement"]
    assert "2026年3月19日" in claim["statement"]
    assert "未確認" not in claim["statement"]
    assert "108,700,000千円" in claim["statement"]


def test_tottori_evidence_packets_cover_the_three_fiscal_records() -> None:
    packets = {packet["id"]: packet for packet in _package()["evidence_packets"]}
    assert set(packets) == {
        "evidence-tottori-city-2026-total-expenditure",
        "evidence-tottori-city-2024-total-revenue",
        "evidence-tottori-city-2024-total-expenditure",
    }
    for packet in packets.values():
        assert packet["review_status"] == "needs_review"
        assert len(packet["claims"]) == 1
        assert packet["claims"][0]["decision"] == "needs_review"
    budget_claim = packets["evidence-tottori-city-2026-total-expenditure"]["claims"][0]
    assert "骨格予算" in budget_claim["statement"]
    assert "108,700,000千円" in budget_claim["statement"]
    revenue_claim = packets["evidence-tottori-city-2024-total-revenue"]["claims"][0]
    assert "議案第106号" in revenue_claim["statement"]
    assert "113,544,636,161円" in revenue_claim["statement"]
    expenditure_claim = packets["evidence-tottori-city-2024-total-expenditure"]["claims"][0]
    assert "111,377,983,188円" in expenditure_claim["statement"]
    assert "2,017,634千円" in expenditure_claim["statement"]


def test_tottori_progress_review_stays_staging() -> None:
    progress = _package()["progress_review"]
    assert progress["review_status"] == "review_candidate_staging"
    framework = progress["implementation_plan_framework"]
    assert "実施計画" in framework["title"]
    assert "毎年度見直す" in framework["evaluation_structure"]


def test_tottori_promotion_is_reflected_in_review_queue() -> None:
    queue = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
    summary = queue["summary"]
    assert summary["reviewed_complete_count"] == 52
    assert summary["pending_record_review_count"] == 15
    assert summary["next_official_code"] == "342076"
    entry = next(
        item for item in queue["execution_queue"] if item["official_code"] == "312010"
    )
    assert entry["status"] == "reviewed_complete"
    assert entry["completion_path"] == "data/catalog/tottori_phase15_completion.json"
