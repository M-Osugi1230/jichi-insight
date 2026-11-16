"""Safety tests for Toyota Phase 15 non-public review candidate."""

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "data/candidates/toyota-city/review_candidate.json"
INVENTORY = ROOT / "data/indexed/toyota-city/source_inventory.json"
SCHEMA = ROOT / "schemas/phase15_review_candidate.schema.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"
WEB_ROOT = ROOT / "apps/web"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_toyota_candidate_validates_and_is_not_published():
    candidate = read(CANDIDATE)
    schema = read(SCHEMA)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = list(validator.iter_errors(candidate))
    assert errors == []
    assert candidate["candidate_id"] == "toyota-phase15-review-candidate"
    assert candidate["phase"] == 15
    assert candidate["official_code"] == "232114"
    assert candidate["name_ja"] == "豊田市"
    assert (
        candidate["source_inventory_path"]
        == "data/indexed/toyota-city/source_inventory.json"
    )
    assert (ROOT / candidate["source_inventory_path"]).is_file()
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


def test_toyota_sources_match_existing_official_inventory():
    candidate = read(CANDIDATE)
    inventory = read(INVENTORY)
    sources = candidate["candidate_package"]["source_catalog"]["sources"]
    expected = inventory["sources"]
    assert len(sources) == len(expected) == 4
    assert {source["id"] for source in sources} == {
        source["id"] for source in expected
    }
    actual_urls = {(source["id"], source["official_url"]) for source in sources}
    assert actual_urls == {
        (source["id"], source["official_url"]) for source in expected
    }
    assert all(
        source["official_url"].startswith("https://www.city.toyota.aichi.jp/")
        for source in sources
    )
    assert all(
        source["verification_status"] == "primary_source_live_verified_2026-11-16"
        for source in sources
    )
    assert all(bool(source["evidence_location"]) for source in sources)
    assert all(bool(source["use_boundary"]) for source in sources)


def test_toyota_prepared_candidate_records_only_verified_fiscal_values():
    candidate = read(CANDIDATE)
    package = candidate["candidate_package"]

    fiscal_records = package["fiscal_records"]
    assert len(fiscal_records) == 3
    by_id = {rec["id"]: rec for rec in fiscal_records}
    assert set(by_id) == {
        "jp-local-232114-fiscal-2026-total-expenditure",
        "jp-local-232114-fiscal-2024-total-revenue",
        "jp-local-232114-fiscal-2024-total-expenditure",
    }
    assert all(rec["municipality_id"] == "jp-local-232114" for rec in fiscal_records)
    assert all(rec["account_type"] == "general" for rec in fiscal_records)
    assert all(rec["value_status"] == "available" for rec in fiscal_records)
    assert all(rec["review_status"] == "needs_review" for rec in fiscal_records)
    assert all(rec["confidence"] == "medium" for rec in fiscal_records)

    # The FY2026 initial budget was submitted to the
    # February-March 2026 council session as bill
    # No. 45 (議案第45号) on 2026-02-20 and, per the
    # council's official voting-result table for the
    # March 2026 regular session, was passed as
    # proposed (原案可決) on 2026-03-18 after referral
    # to the Budget and Settlement Committee, so the
    # budget must not be labelled as a draft proposal
    # (予算案). The amount is the exact sen-yen total
    # published by the city (211,800,000 thousand yen),
    # confirmed in both the official budget book
    # (Article 1) and the official budget overview
    # (2,118 hundred million yen). In the council
    # table the result and date cells for bill 45 use
    # the ditto mark, which resolves to the table's
    # explicit first entry (bill No. 5, 原案可決 on
    # R8.3.18); the candidate records this reading
    # explicitly instead of hiding it.
    budget = by_id["jp-local-232114-fiscal-2026-total-expenditure"]
    assert budget["fiscal_year"] == 2026
    assert budget["stage"] == "initial_budget"
    assert budget["metric"] == "total_expenditure"
    assert budget["metric_label"] == "一般会計当初予算総額"
    assert budget["amount_yen"] == 211800000000
    assert "議案第45号" in budget["note"]
    assert "令和8年3月18日" in budget["note"]
    assert "成立" in budget["note"]
    assert "原案可決" in budget["note"]

    # The FY2024 settlement totals are published at yen
    # precision in the city's official settlement book
    # (general-account statement), so the yen figures
    # below are the exact published totals. Their
    # difference must equal the published balance of
    # 17,058,632,730 yen, and both totals are
    # consistent with the audit committee's published
    # sen-yen figures (revenue 246,602,085 thousand
    # yen, expenditure 229,543,452 thousand yen).
    revenue = by_id["jp-local-232114-fiscal-2024-total-revenue"]
    assert revenue["fiscal_year"] == 2024
    assert revenue["stage"] == "settlement"
    assert revenue["metric"] == "total_revenue"
    assert revenue["amount_yen"] == 246602084906
    expenditure = by_id["jp-local-232114-fiscal-2024-total-expenditure"]
    assert expenditure["fiscal_year"] == 2024
    assert expenditure["stage"] == "settlement"
    assert expenditure["metric"] == "total_expenditure"
    assert expenditure["amount_yen"] == 229543452176
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 17058632730

    # The actual balance (実質収支) is confirmed only
    # at sen-yen precision from the audit committee's
    # published settlement-balance summary
    # (8,192,990 thousand yen), so the candidate must
    # keep it at that precision and must not present a
    # synthesized yen figure.
    assert "8,192,990千円" in revenue["note"]
    assert "千円精度のまま" in revenue["note"]

    packets = package["evidence_packets"]
    assert {pkt["subject_id"] for pkt in packets} == set(by_id)
    assert all(pkt["subject_type"] == "fiscal_record" for pkt in packets)
    assert all(pkt["review_status"] == "needs_review" for pkt in packets)
    assert all(pkt["claims"] for pkt in packets)
    assert all(
        claim["decision"] == "needs_review" and bool(claim["location_note"])
        for pkt in packets
        for claim in pkt["claims"]
    )

    # The FY2026 budget claim must record the enactment
    # route (bill No. 45, passed as proposed on
    # 2026-03-18).
    budget_packet = next(
        pkt
        for pkt in packets
        if pkt["subject_id"] == "jp-local-232114-fiscal-2026-total-expenditure"
    )
    assert "議案第45号" in budget_packet["claims"][0]["statement"]
    assert "成立" in budget_packet["claims"][0]["statement"]
    assert "原案可決" in budget_packet["claims"][0]["statement"]
    assert "令和8年3月18日" in budget_packet["claims"][0]["statement"]

    # The FY2024 settlement certification bill is
    # styled 承認第4号 in Toyota (not 認定第X号). It was
    # submitted on 2025-08-29, referred to the Budget
    # and Settlement Committee, and the council's
    # official voting-result table for the September
    # 2025 regular session directly records the result
    # as certified (認定) on 2025-09-24, so the
    # candidate must record the certification as a
    # confirmed fact with that date, and must never
    # record it as rejected (不認定).
    revenue_packet = next(
        pkt
        for pkt in packets
        if pkt["subject_id"] == "jp-local-232114-fiscal-2024-total-revenue"
    )
    assert "承認第4号" in revenue_packet["claims"][0]["statement"]
    assert "認定された" in revenue_packet["claims"][0]["statement"]
    assert "令和7年9月24日" in revenue_packet["claims"][0]["statement"]
    assert "不認定" not in revenue_packet["claims"][0]["statement"]
    expenditure_packet = next(
        pkt
        for pkt in packets
        if pkt["subject_id"] == "jp-local-232114-fiscal-2024-total-expenditure"
    )
    assert "承認第4号" in expenditure_packet["claims"][0]["statement"]
    assert "認定された" in expenditure_packet["claims"][0]["statement"]
    assert "承認第4号" in revenue["note"]
    assert "承認第4号" in expenditure["note"]
    assert "令和7年9月24日" in revenue["note"]

    plan_review = package["plan_review"]
    assert plan_review["review_status"] == "pending_record_review"
    decisions = {rec["id"]: rec["decision"] for rec in plan_review["records"]}
    # FY2024 is a settlement of the Eighth
    # Comprehensive Plan period, while the current
    # (Ninth) plan starts in FY2025, so the plan
    # version differs; no official total-level mapping
    # from settlement totals to the strategy's goals
    # or policies exists either. The linkage therefore
    # stays not assessable.
    assert decisions["toyota-fy2024-settlement-linkage"] == "not_assessable"
    assert all(
        decision in {"needs_review", "not_assessable"}
        for decision in decisions.values()
    )
    period = next(
        rec for rec in plan_review["records"] if rec["id"] == "toyota-current-plan-period"
    )
    assert period["value"] == "2025年度～2029年度"

    # The transition from the Eighth to the Ninth
    # Comprehensive Plan is recorded only as a version
    # chronology record, never by retroactively mapping
    # the next plan's framework onto prior results.
    transition = next(
        rec for rec in plan_review["records"] if rec["id"] == "toyota-plan-transition"
    )
    assert transition["evidence_role"] == "plan_transition"
    assert "第8次" in transition["statement"]
    assert "第9次" in transition["statement"]

    # The current operative plan layer is the Mirai
    # Realization Strategy 2030 of the Ninth Toyota
    # City Comprehensive Plan (FY2025-FY2029), under
    # the long-term Mirai Concept whose vision is
    # つながる つくる 暮らし楽しむまち・とよた. Its
    # structure is five action goals and 30 policies,
    # exactly as published in the official plan book.
    current_plan = package["policy_structure"]["current_plan"]
    assert current_plan["title"] == "第9次豊田市総合計画 ミライ実現戦略2030"
    assert current_plan["vision"] == "つながる つくる 暮らし楽しむまち・とよた"
    assert current_plan["start_fiscal_year"] == 2025
    assert current_plan["end_fiscal_year"] == 2029
    fields = current_plan["policy_fields"]
    assert [field["name_ja"] for field in fields] == [
        "取組目標① こどもが多様な生き方・暮らし方を選択できる",
        "取組目標② 誰もがつながり合いの中で安心して自分らしく暮らすことができる",
        "取組目標③ 産業中枢都市として深化し続ける",
        "取組目標④ 将来を展望した都市環境の形成を進める",
        "取組目標⑤ 脱炭素社会の実現に挑戦する",
    ]
    assert [field["measures"] for field in fields] == [
        [
            "地域資源を生かした「遊び・学び・体験」の機会の充実",
            "自ら考え判断する力を育む教育の推進",
            "多様な学びに対応した最適な教育環境づくり",
            "大人の学び・活躍を支援する機会の充実",
            "「クルマのまち」の更なる魅力の向上",
            "まちの歴史・文化・芸術や自然等をミライにつなぐ取組の推進",
            "身近な地域の魅力を知り、生かす機会の充実",
            "テーマやターゲットに応じた戦略的な情報の発信",
        ],
        [
            "結婚・出産・子育て支援の充実",
            "保育ニーズへの対応と良好な幼児教育・保育環境づくり",
            "配慮が必要なこどもへの支援",
            "地域活動の持続可能性の向上",
            "多様でゆるやかな「つながり合い」の創出の促進",
        ],
        [
            "ミライを支える産業の創出と育成",
            "積極的な起業・創業の支援",
            "産業用地の創出",
            "市内事業者の持続可能性の向上に向けた取組の支援",
            "多様な人材の活躍と柔軟な働き方を実現する人材戦略への支援",
        ],
        [
            "都市部の利便性の高い暮らし環境の充実",
            "山村部の持続可能な暮らしの仕組みづくり",
            "社会環境の変化に適応する暮らし機能の最適化",
            "多様な人をひきつける中心市街地の魅力の向上",
            "都市間・拠点間の連携を支える交通ネットワークの強化",
            "地域力発揮による防災力の強化",
            "防災・減災を支える基盤づくり",
            "暮らしを守る自然環境の適正な保全",
        ],
        [
            "脱炭素社会の実現に向けた市民の行動の促進",
            "脱炭素社会の実現に向けた事業者の取組の促進",
            "脱炭素社会の実現を先導する公共の取組の推進",
            "水素社会の実現に向けた取組の推進",
        ],
    ]
    assert sum(len(field["measures"]) for field in fields) == 30


def test_toyota_promotion_is_reflected_in_canonical_queue():
    queue = read(QUEUE)
    item = next(
        row for row in queue["execution_queue"] if row["official_code"] == "232114"
    )
    assert item["status"] == "reviewed_complete"
    assert item["completion_path"] == "data/catalog/toyota_phase15_completion.json"
    assert queue["summary"]["reviewed_complete_count"] == 63
    assert queue["summary"]["pending_record_review_count"] == 4
    assert queue["summary"]["next_official_code"] == "442011"


def test_public_web_does_not_import_candidate_staging():
    violations = []
    for path in WEB_ROOT.rglob("*"):
        if (
            path.is_file()
            and path.suffix in {".ts", ".tsx", ".js", ".mjs"}
            and "data/candidates" in path.read_text(encoding="utf-8")
        ):
            violations.append(str(path.relative_to(ROOT)))
    assert violations == []
