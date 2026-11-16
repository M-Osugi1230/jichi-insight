"""Safety tests for Ichinomiya Phase 15 non-public review candidate."""

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "data/candidates/ichinomiya-city/review_candidate.json"
INVENTORY = ROOT / "data/indexed/ichinomiya-city/source_inventory.json"
SCHEMA = ROOT / "schemas/phase15_review_candidate.schema.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"
WEB_ROOT = ROOT / "apps/web"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_ichinomiya_candidate_validates_and_is_not_published():
    candidate = read(CANDIDATE)
    schema = read(SCHEMA)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = list(validator.iter_errors(candidate))
    assert errors == []
    assert candidate["candidate_id"] == "ichinomiya-phase15-review-candidate"
    assert candidate["phase"] == 15
    assert candidate["official_code"] == "232033"
    assert candidate["name_ja"] == "一宮市"
    assert (
        candidate["source_inventory_path"]
        == "data/indexed/ichinomiya-city/source_inventory.json"
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


def test_ichinomiya_sources_match_existing_official_inventory():
    candidate = read(CANDIDATE)
    inventory = read(INVENTORY)
    sources = candidate["candidate_package"]["source_catalog"]["sources"]
    expected = inventory["sources"]
    assert len(sources) == len(expected) == 5
    assert {source["id"] for source in sources} == {
        source["id"] for source in expected
    }
    actual_urls = {(source["id"], source["official_url"]) for source in sources}
    assert actual_urls == {
        (source["id"], source["official_url"]) for source in expected
    }
    assert all(
        source["official_url"].startswith("https://www.city.ichinomiya.aichi.jp/")
        for source in sources
    )
    assert all(
        source["verification_status"] == "primary_source_live_verified_2026-11-16"
        for source in sources
    )
    assert all(bool(source["evidence_location"]) for source in sources)
    assert all(bool(source["use_boundary"]) for source in sources)


def test_ichinomiya_prepared_candidate_records_only_verified_fiscal_values():
    candidate = read(CANDIDATE)
    package = candidate["candidate_package"]

    fiscal_records = package["fiscal_records"]
    assert len(fiscal_records) == 3
    by_id = {rec["id"]: rec for rec in fiscal_records}
    assert set(by_id) == {
        "jp-local-232033-fiscal-2026-total-expenditure",
        "jp-local-232033-fiscal-2024-total-revenue",
        "jp-local-232033-fiscal-2024-total-expenditure",
    }
    assert all(rec["municipality_id"] == "jp-local-232033" for rec in fiscal_records)
    assert all(rec["account_type"] == "general" for rec in fiscal_records)
    assert all(rec["value_status"] == "available" for rec in fiscal_records)
    assert all(rec["review_status"] == "needs_review" for rec in fiscal_records)
    assert all(rec["confidence"] == "medium" for rec in fiscal_records)

    # The FY2026 initial budget was submitted to the
    # March 2026 regular council session as mayoral
    # bill No. 3 (議案第3号), referred to the four
    # standing committees, and the city's official
    # split-vote list records the result as passed
    # (可決); the session agenda (No. 4) places the
    # bill on 2026-03-23, so the budget must not be
    # labelled as a draft proposal (予算案). The amount
    # is the exact sen-yen total published by the city
    # (146,740,000 thousand yen, up 2,430,000 thousand
    # yen / 1.7% from FY2025's 144,310,000 thousand
    # yen), confirmed in both the official budget
    # overview and the enacted budget book. The city's
    # published result wording is simply 可決, so the
    # candidate must keep the 原案可決 wording
    # explicitly unconfirmed instead of asserting it.
    budget = by_id["jp-local-232033-fiscal-2026-total-expenditure"]
    assert budget["fiscal_year"] == 2026
    assert budget["stage"] == "initial_budget"
    assert budget["metric"] == "total_expenditure"
    assert budget["metric_label"] == "一般会計当初予算総額"
    assert budget["amount_yen"] == 146740000000
    assert "議案第3号" in budget["note"]
    assert "令和8年3月23日" in budget["note"]
    assert "成立" in budget["note"]
    assert "可決" in budget["note"]
    assert "未確認" in budget["note"]

    # The FY2024 settlement totals are published at yen
    # precision in the city's official settlement book
    # (summary table and general-account statement
    # agree), so the yen figures below are the exact
    # published totals. Their difference must equal the
    # published balance of 6,449,107,846 yen.
    revenue = by_id["jp-local-232033-fiscal-2024-total-revenue"]
    assert revenue["fiscal_year"] == 2024
    assert revenue["stage"] == "settlement"
    assert revenue["metric"] == "total_revenue"
    assert revenue["amount_yen"] == 150057354584
    expenditure = by_id["jp-local-232033-fiscal-2024-total-expenditure"]
    assert expenditure["fiscal_year"] == 2024
    assert expenditure["stage"] == "settlement"
    assert expenditure["metric"] == "total_expenditure"
    assert expenditure["amount_yen"] == 143608246738
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 6449107846

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
    # route (bill No. 3, passed on 2026-03-23) while
    # keeping the unconfirmed voting-result wording
    # explicit.
    budget_packet = next(
        pkt
        for pkt in packets
        if pkt["subject_id"] == "jp-local-232033-fiscal-2026-total-expenditure"
    )
    assert "議案第3号" in budget_packet["claims"][0]["statement"]
    assert "成立" in budget_packet["claims"][0]["statement"]
    assert "可決" in budget_packet["claims"][0]["statement"]
    assert "未確認" in budget_packet["claims"][0]["statement"]

    # The FY2024 settlement certification bill
    # (認定第4号) was submitted on 2025-09-29 and
    # referred to committees for recess review. The
    # council's official bill-and-result list for the
    # December 2025 regular session (議案・議決結果一覧
    # (令和7年12月定例会), published by the council
    # secretariat on the city domain) records bill
    # 認定4 as certified (認定) with vote date
    # 2025-12-01, the session's opening day, whose
    # finalized agenda also lists the bill. The
    # candidate must therefore record the certification
    # and its date as verified, and the settlement
    # book's real-balance statement (実質収支に関する
    # 調書) fixes the FY2024 real balance at 6,207,237
    # thousand yen (thousand-yen precision, rounded),
    # which must be kept at that published precision
    # rather than synthesised into an exact yen figure.
    revenue_packet = next(
        pkt
        for pkt in packets
        if pkt["subject_id"] == "jp-local-232033-fiscal-2024-total-revenue"
    )
    assert "認定第4号" in revenue_packet["claims"][0]["statement"]
    assert "令和7年12月1日" in revenue_packet["claims"][0]["statement"]
    assert "認定された" in revenue_packet["claims"][0]["statement"]
    assert "6,207,237千円" in revenue_packet["claims"][0]["statement"]
    assert "未確認" not in revenue_packet["claims"][0]["statement"]
    expenditure_packet = next(
        pkt
        for pkt in packets
        if pkt["subject_id"] == "jp-local-232033-fiscal-2024-total-expenditure"
    )
    assert "認定第4号" in expenditure_packet["claims"][0]["statement"]
    assert "令和7年12月1日" in expenditure_packet["claims"][0]["statement"]
    assert "認定された" in expenditure_packet["claims"][0]["statement"]
    assert "認定第4号" in revenue["note"]
    assert "認定第4号" in expenditure["note"]
    assert "令和7年12月1日" in revenue["note"]
    assert "認定された" in revenue["note"]
    assert "6,207,237千円" in revenue["note"]
    assert "未確認" not in revenue["note"]
    assert "令和7年12月1日" in expenditure["note"]
    assert "認定された" in expenditure["note"]
    # The certification result and the real balance are
    # confirmed, so no settlement packet may keep an open
    # question asking for their confirmation.
    for pkt in (revenue_packet, expenditure_packet):
        assert all("議決結果" not in q for q in pkt["open_questions"])
        assert all("実質収支" not in q for q in pkt["open_questions"])
    settlement_source = next(
        source
        for source in package["source_catalog"]["sources"]
        if source["id"] == "ichinomiya-settlement-2024"
    )
    assert "令和7年12月1日" in settlement_source["use_boundary"]
    assert "未確認" not in settlement_source["use_boundary"]

    plan_review = package["plan_review"]
    assert plan_review["review_status"] == "pending_record_review"
    decisions = {rec["id"]: rec["decision"] for rec in plan_review["records"]}
    # FY2024 sits inside the latter basic plan period
    # (2023-2027), so the plan version is the same, but
    # no official total-level mapping from settlement
    # totals to the plan's policies or indicators
    # exists; the linkage stays not assessable.
    assert decisions["ichinomiya-fy2024-settlement-linkage"] == "not_assessable"
    assert all(
        decision in {"needs_review", "not_assessable"}
        for decision in decisions.values()
    )
    period = next(
        rec
        for rec in plan_review["records"]
        if rec["id"] == "ichinomiya-current-plan-period"
    )
    assert period["value"] == "2023年度～2027年度"

    # The transition to the Eighth Comprehensive Plan
    # (under preparation) is recorded only as a version
    # chronology record, never by retroactively mapping
    # the next plan's framework onto current results.
    transition = next(
        rec for rec in plan_review["records"] if rec["id"] == "ichinomiya-plan-transition"
    )
    assert transition["evidence_role"] == "plan_transition"
    assert "第8次" in transition["statement"]

    # The current plan is the latter basic plan of the
    # Seventh Ichinomiya City Comprehensive Plan
    # (basic concept 2018-2027 with five plans and two
    # managements; latter basic plan 2023-2027). Its
    # structure is seven groups and 35 policies,
    # exactly as published in the official plan and
    # the FY2025 administrative evaluation report.
    current_plan = package["policy_structure"]["current_plan"]
    assert current_plan["title"] == "第7次一宮市総合計画 後期基本計画"
    assert current_plan["vision"] == "木曽の清流に映え、心ふれあう躍動都市 一宮"
    assert current_plan["start_fiscal_year"] == 2023
    assert current_plan["end_fiscal_year"] == 2027
    fields = current_plan["policy_fields"]
    assert [field["name_ja"] for field in fields] == [
        "プラン1 健やかにいきる",
        "プラン2 快適にくらす",
        "プラン3 安全・安心を高める",
        "プラン4 活力を生みだす",
        "プラン5 未来の人財を育てる",
        "マネジメント1 人を呼び込む ～シティプロモーション～",
        "マネジメント2 持続可能で未来につなげる",
    ]
    assert [field["measures"] for field in fields] == [
        [
            "健康寿命の長いまちづくりに取り組みます",
            "安心して子育てができる環境をつくります",
            "適切な医療を受けられる体制を整えます",
            "高齢者が安心していきいきと暮らせるよう支援します",
            "障害者福祉の充実を図ります",
        ],
        [
            "ごみを適正に処理し資源のリサイクルを推進します",
            "地球温暖化防止に取り組みます",
            "環境教育を推進します",
            "水と緑を活かしたまちをつくります",
            "良好な生活環境を確保します",
            "総合的な住宅対策に取り組みます",
            "公共交通網の整備を進めます",
            "歩行者や自転車が安全に通行できる交通環境を整備します",
        ],
        [
            "災害に強い社会基盤整備を進めます",
            "自主防災力の向上を図ります",
            "火災や救急に対する体制の強化を進めます",
            "交通事故を減らす取組を進めます",
            "防犯対策を進めます",
        ],
        [
            "既存産業や次世代産業の育成を支援します",
            "意欲を持って働けるよう就労支援を進めます",
            "女性の活躍できる環境をつくります",
            "魅力があり持続的発展性のある農業を支援します",
            "幹線道路の整備を進めます",
        ],
        [
            "子どもから青少年まで健全に育つ環境をつくります",
            "学校教育施設を整備します",
            "特色ある教育活動を実施します",
            "する・みる・ささえるスポーツ活動を支援します",
            "歴史・文化に親しめる環境を整えます",
        ],
        [
            "子育て世代に選ばれるまちをつくります",
            "訪れてみたいまち、交流が盛んなまちをつくります",
        ],
        [
            "健全な財政運営に努めます",
            "公共施設の適切な維持管理に努めます",
            "情報通信技術（ICT）を積極的に利活用します",
            "適切な情報発信を行います",
            "市民との協働を進めます",
        ],
    ]
    assert sum(len(field["measures"]) for field in fields) == 35


def test_ichinomiya_promotion_is_reflected_in_canonical_queue():
    queue = read(QUEUE)
    item = next(
        row for row in queue["execution_queue"] if row["official_code"] == "232033"
    )
    assert item["status"] == "reviewed_complete"
    assert item["completion_path"] == "data/catalog/ichinomiya_phase15_completion.json"
    assert queue["summary"]["reviewed_complete_count"] == 52
    assert queue["summary"]["pending_record_review_count"] == 15
    assert queue["summary"]["next_official_code"] == "342076"


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
