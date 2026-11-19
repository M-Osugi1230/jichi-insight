"""Safety tests for Nagano Phase 15 non-public review candidate."""

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "data/candidates/nagano-city/review_candidate.json"
INVENTORY = ROOT / "data/indexed/nagano-city/source_inventory.json"
SCHEMA = ROOT / "schemas/phase15_review_candidate.schema.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"
WEB_ROOT = ROOT / "apps/web"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_nagano_candidate_validates_and_is_not_published():
    candidate = read(CANDIDATE)
    schema = read(SCHEMA)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = list(validator.iter_errors(candidate))
    assert errors == []
    assert candidate["candidate_id"] == "nagano-phase15-review-candidate"
    assert candidate["phase"] == 15
    assert candidate["official_code"] == "202010"
    assert candidate["name_ja"] == "長野市"
    assert (
        candidate["source_inventory_path"]
        == "data/indexed/nagano-city/source_inventory.json"
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


def test_nagano_sources_match_existing_official_inventory():
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
        source["official_url"].startswith("https://www.city.nagano.nagano.jp/")
        for source in sources
    )
    assert all(
        source["verification_status"] == "primary_source_live_verified_2026-11-16"
        for source in sources
    )
    assert all(bool(source["evidence_location"]) for source in sources)
    assert all(bool(source["use_boundary"]) for source in sources)


def test_nagano_prepared_candidate_records_only_verified_fiscal_values():
    candidate = read(CANDIDATE)
    package = candidate["candidate_package"]

    fiscal_records = package["fiscal_records"]
    assert len(fiscal_records) == 3
    by_id = {rec["id"]: rec for rec in fiscal_records}
    assert set(by_id) == {
        "jp-local-202010-fiscal-2026-total-expenditure",
        "jp-local-202010-fiscal-2024-total-revenue",
        "jp-local-202010-fiscal-2024-total-expenditure",
    }
    assert all(rec["municipality_id"] == "jp-local-202010" for rec in fiscal_records)
    assert all(rec["account_type"] == "general" for rec in fiscal_records)
    assert all(rec["value_status"] == "available" for rec in fiscal_records)
    assert all(rec["review_status"] == "needs_review" for rec in fiscal_records)
    assert all(rec["confidence"] == "medium" for rec in fiscal_records)

    # The FY2026 initial budget was enacted as bill No. 1
    # (議案第1号) at the March 2026 regular council session,
    # passed as proposed (原案可決) on 2026-03-23, so it must
    # not be labelled as a draft proposal (予算案). The amount
    # is the exact sen-yen total stated in Article 1 and
    # Table 1 of the official budget book (195,220,000千円,
    # up 2,100,000千円 from FY2025's 193,120,000千円).
    budget = by_id["jp-local-202010-fiscal-2026-total-expenditure"]
    assert budget["fiscal_year"] == 2026
    assert budget["stage"] == "initial_budget"
    assert budget["metric"] == "total_expenditure"
    assert budget["metric_label"] == "一般会計当初予算総額"
    assert budget["amount_yen"] == 195220000000
    assert "議案第1号" in budget["note"]
    assert "令和8年3月23日" in budget["note"]
    assert "原案可決" in budget["note"]

    # The FY2024 settlement totals are published at yen
    # precision in the audit commission's official review
    # opinion (7監査第40号), so the yen figures below are
    # the exact published totals. Their difference must
    # equal the published balance (歳入歳出差引額・形式収支)
    # of 4,247,193,994 yen, and the real balance after the
    # carryover source of 1,610,940,000 yen must equal the
    # published real balance of 2,636,253,994 yen.
    revenue = by_id["jp-local-202010-fiscal-2024-total-revenue"]
    assert revenue["fiscal_year"] == 2024
    assert revenue["stage"] == "settlement"
    assert revenue["metric"] == "total_revenue"
    assert revenue["amount_yen"] == 170949499030
    expenditure = by_id["jp-local-202010-fiscal-2024-total-expenditure"]
    assert expenditure["fiscal_year"] == 2024
    assert expenditure["stage"] == "settlement"
    assert expenditure["metric"] == "total_expenditure"
    assert expenditure["amount_yen"] == 166702305036
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 4247193994
    assert 4247193994 - 1610940000 == 2636253994

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
    # route (bill No. 1, passed as proposed on 2026-03-23).
    budget_packet = next(
        pkt
        for pkt in packets
        if pkt["subject_id"] == "jp-local-202010-fiscal-2026-total-expenditure"
    )
    assert "議案第1号" in budget_packet["claims"][0]["statement"]
    assert "原案可決" in budget_packet["claims"][0]["statement"]
    assert "成立" in budget_packet["claims"][0]["statement"]

    # The FY2024 settlement was certified as certification
    # No. 2 (認定第2号, covering the general and special
    # accounts) on 2025-09-30, per the council's official
    # deliberation results for the September 2025 regular
    # session.
    revenue_packet = next(
        pkt
        for pkt in packets
        if pkt["subject_id"] == "jp-local-202010-fiscal-2024-total-revenue"
    )
    assert "認定第2号" in revenue_packet["claims"][0]["statement"]
    assert "令和7年9月30日" in revenue_packet["claims"][0]["statement"]
    assert "認定" in revenue_packet["claims"][0]["statement"]
    assert "認定第2号" in revenue["note"]
    assert "認定第2号" in expenditure["note"]

    plan_review = package["plan_review"]
    assert plan_review["review_status"] == "pending_record_review"
    decisions = {rec["id"]: rec["decision"] for rec in plan_review["records"]}
    # FY2024 is the eighth year of the plan period, but
    # settlement totals are section-level aggregates with no
    # official mapping to individual policies or indicators,
    # so the linkage stays explicitly not assessable.
    assert decisions["nagano-fy2024-settlement-linkage"] == "not_assessable"
    assert all(
        decision in {"needs_review", "not_assessable"}
        for decision in decisions.values()
    )
    period = next(
        rec for rec in plan_review["records"] if rec["id"] == "nagano-current-plan-period"
    )
    assert period["value"] == "2017年度～2026年度"

    # The next plan (from FY2027) is recorded only as a
    # version chronology record, never merged back into the
    # fifth plan's framework.
    transition = next(
        rec
        for rec in plan_review["records"]
        if rec["id"] == "nagano-next-plan-transition"
    )
    assert transition["evidence_role"] == "plan_transition"
    assert "次期長野市総合計画" in transition["statement"]

    # The current plan is the Fifth Nagano City
    # Comprehensive Plan (basic concept FY2017 to FY2026,
    # latter basic plan FY2022 to FY2026). Its policy
    # structure is seven fields holding 22 policies, exactly
    # as published in the plan's official framework chart;
    # the 55 measures of the latter basic plan are not
    # enumerated here.
    current_plan = package["policy_structure"]["current_plan"]
    assert current_plan["title"] == "第五次長野市総合計画"
    assert current_plan["start_fiscal_year"] == 2017
    assert current_plan["end_fiscal_year"] == 2026
    assert current_plan["vision"] == "幸せ実感都市『ながの』〜“オールながの”で未来を創造しよう〜"
    goals = current_plan["basic_goals"]
    assert [goal["name_ja"] for goal in goals] == [
        "行政経営分野（行政経営の方針）",
        "保健・福祉分野（人にやさしく人がいきいき暮らすまち「ながの」）",
        "環境分野（人と自然が共生するまち「ながの」）",
        "防災・安全分野（安全で安心して暮らせるまち「ながの」）",
        "教育・文化分野（豊かな心を育み人と文化が輝くまち「ながの」）",
        "産業・経済分野（産業の活力とにぎわいのあふれるまち「ながの」）",
        "都市整備分野（快適に暮らし活動できるコンパクトなまち「ながの」）",
    ]
    assert [goal["measures"] for goal in goals] == [
        [
            "市民が主役のまちづくりの推進",
            "将来にわたり持続可能な行財政運営の確立",
        ],
        [
            "少子化対策、切れ目ない子ども・子育て支援",
            "生きがいのある豊かな高齢社会の形成",
            "だれもが自分らしく暮らせる社会の形成",
            "安心して暮らせる健康づくりの推進",
            "人権を尊ぶ明るい社会の形成",
        ],
        [
            "環境に負荷をかけない持続可能な社会の形成",
            "自然と調和した心地よい暮らしづくりの推進",
        ],
        [
            "災害に強いまちづくりの推進",
            "安心して暮らせる安全社会の構築",
        ],
        [
            "未来を切り拓く人材の育成と環境の整備",
            "豊かな人生を送るための学習機会の提供",
            "魅力あふれる文化の創造と継承",
            "スポーツを軸としたまちづくりの推進",
            "国際交流・多文化共生の推進",
        ],
        [
            "魅力を活かした観光の振興",
            "活力ある農林業の振興",
            "特色を活かした商工業の振興",
            "安定した就労の促進",
        ],
        [
            "いきいきと暮らせる魅力あるまちづくりの推進",
            "拠点をつなぐネットワークの充実",
        ],
    ]


def test_nagano_promotion_is_reflected_in_canonical_queue():
    queue = read(QUEUE)
    item = next(
        row for row in queue["execution_queue"] if row["official_code"] == "202010"
    )
    assert item["status"] == "reviewed_complete"
    assert item["completion_path"] == "data/catalog/nagano_phase15_completion.json"
    assert queue["summary"]["reviewed_complete_count"] == 68
    assert queue["summary"]["pending_record_review_count"] == 0
    assert queue["summary"]["next_official_code"] is None


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
