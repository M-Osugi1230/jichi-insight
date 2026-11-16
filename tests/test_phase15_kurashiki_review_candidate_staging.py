"""Staging tests for the Kurashiki Phase 15 review candidate.

The candidate stays prepared and unpublished until a human checks the
cited primary sources.  These tests pin the package state, the source
catalog, the plan framework, and the verified fiscal values so that a
promotion change has to be deliberate.  The FY2026 initial budget vote
(bill 26, adopted as proposed on 2026-03-18) and the FY2024 settlement
certification (bill 135, certified on 2025-09-24) were both read
directly from the council's official bill/result tables, so the
candidate records both outcomes in the primary sources' own wording.
The FY2024 settlement totals are published at yen precision in the
audit commissioners' opinion, so they are pinned at that precision.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_PATH = ROOT / "data" / "candidates" / "kurashiki-city" / "review_candidate.json"
INVENTORY_PATH = ROOT / "data" / "indexed" / "kurashiki-city" / "source_inventory.json"
QUEUE_PATH = ROOT / "data" / "catalog" / "phase15_core_capital_review_queue.json"


def _candidate() -> dict:
    return json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))


def _package() -> dict:
    return _candidate()["candidate_package"]


def test_kurashiki_candidate_is_prepared_with_delegated_review_approved() -> None:
    candidate = _candidate()
    assert candidate["candidate_id"] == "kurashiki-phase15-review-candidate"
    assert candidate["official_code"] == "332020"
    assert candidate["name_ja"] == "倉敷市"
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


def test_kurashiki_candidate_sources_match_phase14_inventory() -> None:
    package_sources = {
        source["id"]: source for source in _package()["source_catalog"]["sources"]
    }
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    inventory_sources = {source["id"]: source for source in inventory["sources"]}
    assert set(package_sources) == set(inventory_sources)
    assert set(package_sources) == {
        "kurashiki-seventh-plan",
        "kurashiki-administrative-evaluation-2025",
        "kurashiki-budget-2026",
        "kurashiki-settlement-2024",
    }
    for source_id, source in package_sources.items():
        assert source["official_url"] == inventory_sources[source_id]["official_url"]
        assert source["official_url"].startswith("https://www.city.kurashiki.okayama.jp/")
        assert source["verification_status"] == "primary_source_live_verified_2026-11-16"


def test_kurashiki_plan_review_records_framework_and_transition() -> None:
    records = {record["id"]: record for record in _package()["plan_review"]["records"]}
    assert set(records) == {
        "kurashiki-current-plan-period",
        "kurashiki-current-policy-structure",
        "kurashiki-progress-governance-framework",
        "kurashiki-plan-transition",
        "kurashiki-fy2024-settlement-linkage",
    }
    period = records["kurashiki-current-plan-period"]
    assert period["decision"] == "needs_review"
    assert period["title"].startswith("倉敷市第七次総合計画の構成")
    assert "基本構想・基本計画2021年度～2030年度" in period["value"]
    assert "毎年度見直し" in period["value"]
    transition = records["kurashiki-plan-transition"]
    assert "2021年度に開始した" in transition["statement"]
    assert "未確認" in transition["statement"]
    linkage = records["kurashiki-fy2024-settlement-linkage"]
    assert linkage["decision"] == "not_assessable"
    assert linkage["fiscal_year"] == 2024


def test_kurashiki_policy_structure_keeps_five_fields_and_44_outcomes() -> None:
    plan = _package()["policy_structure"]["current_plan"]
    assert plan["title"].startswith("倉敷市第七次総合計画")
    assert plan["vision"] == (
        "豊かな自然と紡がれた歴史・文化を次代へ繋ぎ "
        "人と人との絆と慈しみの心で地域を結ぶまち倉敷"
    )
    assert plan["start_fiscal_year"] == 2021
    assert plan["end_fiscal_year"] == 2030
    assert plan["period_status"] == "verified_fixed_period"
    field1 = "子ども・子育て・教育"
    field2 = "文化・産業"
    field3 = "生活環境・防災・都市基盤"
    field4 = "保健・医療・福祉"
    field5 = "SDGs・市民協働・コミュニティ・行財政"
    field_names = [field["name_ja"] for field in plan["policy_fields"]]
    assert field_names == [
        f"{field1}：1-1 だれもがその人らしさ（個性）を尊重され、幸せに暮らしていくことができている",
        f"{field1}：1-2 人の痛みを、子どもたちが実感としてわかっている",
        f"{field1}：1-3 教員の資質が保たれ、教員と子どもが心豊かな人間関係を築き、"
        "学校教育が充実している",
        f"{field1}：1-4 子どもたちが自然にふれながら、健やかに育っている",
        f"{field1}：1-5 安心できる環境のもとで出産・子育てができている",
        f"{field1}：1-6 仕事と家庭の両立ができ、親が子どもとふれあう時間をもつことができている",
        f"{field1}：1-7 学校・園、地域、家庭が連携して、子どもたちが困窮することなく、"
        "安心して学び、成長できる環境となっている",
        f"{field1}：1-8 障がいの有無にかかわらず、等しく保育・教育を受けることができている",
        f"{field1}：1-9 興味があることを、だれもが、気軽に学ぶことができている",
        f"{field2}：2-1 生活の中に個性的で魅力的な文化芸術が息づいている",
        f"{field2}：2-2 世代を超えて受け継がれてきた歴史文化や伝統が大切に継承され、輝いている",
        f"{field2}：2-3 生活の中で、日常的かつ気軽にスポーツに親しむことができている",
        f"{field2}：2-4 心に充足感やゆとりをもち、家庭と仕事の調和がとれている",
        f"{field2}：2-5 産業競争力が高く、多様な人材が働く機会に恵まれ、"
        "将来の暮らしに希望をもつことができている",
        f"{field2}：2-6 商業の活性化が地域に活力を生み、"
        "時代の流れに対応したビジネスの創出や起業が進んでいる",
        f"{field2}：2-7 将来にわたり持続可能な魅力ある農業や漁業が営まれている",
        f"{field2}：2-8 倉敷の魅力を国内外にＰＲし、たくさんの人が訪れるようになっている",
        f"{field3}：3-1 自然環境が守られ、環境と経済・社会とのバランスが保たれている",
        f"{field3}：3-2 水と空気と大地がきれいで、環境負荷の少ないまちがつくられている",
        f"{field3}：3-3 リデュース（ごみの発生抑制）、リユース（再使用）、"
        "リサイクル（ごみの再生利用）が徹底され、環境に配慮した循環型社会が形成されている",
        f"{field3}：3-4 脱炭素社会の実現に向け、だれもが地球温暖化対策を推進している",
        f"{field3}：3-5 行政と市民、企業などが連携し、"
        "防災・減災対策や感染症対策などを積極的に進めるとともに、だれもが命を守る意識をもっている",
        f"{field3}：3-6 常に安全でおいしい水が届き、安心して暮らすことができている",
        f"{field3}：3-7 だれもが安全で快適に移動できる道路環境となっている",
        f"{field3}：3-8 市中心部の拠点性が高まるとともに、"
        "各地域・地区の中心部の利便性が向上するまちづくりが行われている",
        f"{field3}：3-9 便利に公共交通が利用でき、その周辺に住まいや生活に必要な施設が集まっている",
        f"{field3}：3-10 地域の特色が生かされ、自然と調和した、"
        "だれもが住みやすい生活環境となっている",
        f"{field3}：3-11 先人から受け継いだ歴史的・魅力的な景観が、市内各地で守られている",
        f"{field3}：3-12 犯罪が少なく、安心して暮らしている",
        f"{field4}：4-1 だれもが自分の健康に関心をもち、健康づくりに自ら取り組んでいる",
        f"{field4}：4-2 豊かな自然の恵みにより食べ物がおいしく、健全な食生活が実現されている",
        f"{field4}：4-3 市内のどこに住んでいても、だれもが安心して、医療を受けられている",
        f"{field4}：4-4 障がい者が積極的に社会参加でき、"
        "地域の人と安心してともに暮らせるようになっている",
        f"{field4}：4-5 様々な事情により困窮している人が、自立できるよう地域で支え合っている",
        f"{field4}：4-6 高齢者が地域で安心して暮らすことができている",
        f"{field4}：4-7 尊厳が守られながら必要な介護サービスを受けることができている",
        f"{field4}：4-8 高齢者が生きがいをもって活動している",
        f"{field5}：5-1 地域やコミュニティの中で、だれもが互いに助け合い、支え合って暮らしている",
        f"{field5}：5-2 ボランティア・NPOなどの市民主体の活動が活発に行われている",
        f"{field5}：5-3 行政が市民の意見を踏まえ、施策の検討、効果的な実施、評価・検証を行い、"
        "改善を図っている",
        f"{field5}：5-4 市民が安全で快適に、公共施設を利用している",
        f"{field5}：5-5 市役所が市民の身近な窓口として課題解決に向けて責任をもって対応している",
        f"{field5}：5-6 だれもが快適で活力に満ちた生活ができるよう、先端技術が生活に溶けこんでいる",
        f"{field5}：5-7 持続可能な地域をめざすSDGsの理念を、だれもが理解し、行動している",
    ]
    assert all(field["measures"] == [] for field in plan["policy_fields"])
    principles = "".join(plan["management_principles"])
    assert "実施計画" in principles
    assert "行政評価" in principles
    assert "verified_fixed_period" in principles


def test_kurashiki_fiscal_records_hold_verified_values() -> None:
    records = {record["id"]: record for record in _package()["fiscal_records"]}
    budget = records["jp-local-332020-fiscal-2026-total-expenditure"]
    assert budget["stage"] == "initial_budget"
    assert budget["amount_yen"] == 222_767_966_000
    assert budget["sources"] == ["kurashiki-budget-2026"]
    assert "議案第26号" in budget["note"]
    assert "222,767,966千円" in budget["note"]
    assert "原案可決" in budget["note"]
    assert "千円単位" in budget["note"]
    revenue = records["jp-local-332020-fiscal-2024-total-revenue"]
    assert revenue["stage"] == "settlement"
    assert revenue["amount_yen"] == 232_345_729_550
    assert revenue["sources"] == ["kurashiki-settlement-2024"]
    assert "議案第135号" in revenue["note"]
    assert "232,345,729,550円" in revenue["note"]
    assert "2025年9月24日" in revenue["note"]
    expenditure = records["jp-local-332020-fiscal-2024-total-expenditure"]
    assert expenditure["amount_yen"] == 225_142_008_893
    assert expenditure["sources"] == ["kurashiki-settlement-2024"]
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 7_203_720_657


def test_kurashiki_fy2024_settlement_values_and_real_balance() -> None:
    records = {record["id"]: record for record in _package()["fiscal_records"]}
    revenue = records["jp-local-332020-fiscal-2024-total-revenue"]
    expenditure = records["jp-local-332020-fiscal-2024-total-expenditure"]
    # Values pinned from the audit commissioners' settlement opinion,
    # whose summary tables are published at yen precision.
    assert revenue["amount_yen"] == 232_345_729_550
    assert expenditure["amount_yen"] == 225_142_008_893
    # 形式収支 (revenue minus expenditure) matches the opinion's table.
    assert 232_345_729_550 - 225_142_008_893 == 7_203_720_657
    # 実質収支 at the same published precision:
    # 7,203,720,657 - 1,400,067,591 = 5,803,653,066 (yen).
    assert 7_203_720_657 - 1_400_067_591 == 5_803_653_066
    assert "7,203,720,657円" in expenditure["note"]
    assert "5,803,653,066円" in expenditure["note"]
    assert "1,400,067,591円" in expenditure["note"]
    assert "円単位の公表値のまま" in expenditure["note"]


def test_kurashiki_fy2024_settlement_certification_wording() -> None:
    text = CANDIDATE_PATH.read_text(encoding="utf-8")
    assert "議案第135号" in text
    assert "認定" in text
    # Bill 135 was certified on 2025-09-24; the candidate must not carry
    # the opposite outcome or an amended-adoption wording.
    assert "不認定" not in text
    assert "修正可決" not in text
    assert "修正議決" not in text


def test_kurashiki_fy2026_budget_vote_wording() -> None:
    packets = {packet["id"]: packet for packet in _package()["evidence_packets"]}
    claim = packets["evidence-kurashiki-city-2026-total-expenditure"]["claims"][0]
    # Bill 26 was adopted as proposed; the claim keeps the primary
    # source's own wording and the thousand-yen precision.
    assert "原案可決" in claim["statement"]
    assert "議案第26号" in claim["statement"]
    assert "222,767,966千円" in claim["statement"]


def test_kurashiki_evidence_packets_cover_the_three_fiscal_records() -> None:
    packets = {packet["id"]: packet for packet in _package()["evidence_packets"]}
    assert set(packets) == {
        "evidence-kurashiki-city-2026-total-expenditure",
        "evidence-kurashiki-city-2024-total-revenue",
        "evidence-kurashiki-city-2024-total-expenditure",
    }
    for packet in packets.values():
        assert packet["review_status"] == "needs_review"
        assert len(packet["claims"]) == 1
        assert packet["claims"][0]["decision"] == "needs_review"
    budget_claim = packets["evidence-kurashiki-city-2026-total-expenditure"]["claims"][0]
    assert "原案可決" in budget_claim["statement"]
    assert "222,767,966千円" in budget_claim["statement"]
    revenue_claim = packets["evidence-kurashiki-city-2024-total-revenue"]["claims"][0]
    assert "議案第135号" in revenue_claim["statement"]
    assert "232,345,729,550円" in revenue_claim["statement"]
    expenditure_claim = packets["evidence-kurashiki-city-2024-total-expenditure"]["claims"][0]
    assert "225,142,008,893円" in expenditure_claim["statement"]
    assert "5,803,653,066円" in expenditure_claim["statement"]


def test_kurashiki_progress_review_stays_staging() -> None:
    progress = _package()["progress_review"]
    assert progress["review_status"] == "review_candidate_staging"
    framework = progress["implementation_plan_framework"]
    assert "実施計画" in framework["title"]
    assert "行政評価" in framework["evaluation_structure"]


def test_kurashiki_promotion_is_reflected_in_review_queue() -> None:
    queue = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
    summary = queue["summary"]
    assert summary["reviewed_complete_count"] == 56
    assert summary["pending_record_review_count"] == 11
    assert summary["next_official_code"] == "372013"
    entry = next(
        item for item in queue["execution_queue"] if item["official_code"] == "332020"
    )
    assert entry["status"] == "reviewed_complete"
    assert entry["completion_path"] == "data/catalog/kurashiki_phase15_completion.json"
