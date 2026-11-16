"""Safety tests for Kanazawa Phase 15 non-public review candidate."""

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "data/candidates/kanazawa-city/review_candidate.json"
INVENTORY = ROOT / "data/indexed/kanazawa-city/source_inventory.json"
SCHEMA = ROOT / "schemas/phase15_review_candidate.schema.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"
WEB_ROOT = ROOT / "apps/web"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_kanazawa_candidate_validates_and_is_not_published():
    candidate = read(CANDIDATE)
    schema = read(SCHEMA)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = list(validator.iter_errors(candidate))
    assert errors == []
    assert candidate["candidate_id"] == "kanazawa-phase15-review-candidate"
    assert candidate["phase"] == 15
    assert candidate["official_code"] == "172014"
    assert candidate["name_ja"] == "金沢市"
    assert (
        candidate["source_inventory_path"]
        == "data/indexed/kanazawa-city/source_inventory.json"
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


def test_kanazawa_sources_match_existing_official_inventory():
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
        source["official_url"].startswith("https://www4.city.kanazawa.lg.jp/")
        for source in sources
    )
    assert all(
        source["verification_status"] == "primary_source_live_verified_2026-11-16"
        for source in sources
    )
    assert all(bool(source["evidence_location"]) for source in sources)
    assert all(bool(source["use_boundary"]) for source in sources)


def test_kanazawa_prepared_candidate_records_only_verified_fiscal_values():
    candidate = read(CANDIDATE)
    package = candidate["candidate_package"]

    fiscal_records = package["fiscal_records"]
    assert len(fiscal_records) == 3
    by_id = {rec["id"]: rec for rec in fiscal_records}
    assert set(by_id) == {
        "jp-local-172014-fiscal-2026-total-expenditure",
        "jp-local-172014-fiscal-2024-total-revenue",
        "jp-local-172014-fiscal-2024-total-expenditure",
    }
    assert all(rec["municipality_id"] == "jp-local-172014" for rec in fiscal_records)
    assert all(rec["account_type"] == "general" for rec in fiscal_records)
    assert all(rec["value_status"] == "available" for rec in fiscal_records)
    assert all(rec["review_status"] == "needs_review" for rec in fiscal_records)
    assert all(rec["confidence"] == "medium" for rec in fiscal_records)

    # The FY2026 initial budget was enacted by a vote of the
    # February 2026 regular monthly council session, and its
    # outline was published in the official city gazette
    # (告示第56号, 2026-03-11) under Article 219(2) of the
    # Local Autonomy Act, so it must not be labelled as a
    # draft proposal (予算案). The amount is the exact sen-yen
    # total in the official budget overview (207,800,000千円).
    # The bill number and the exact vote date could not be
    # confirmed in the primary sources consulted, so the
    # record must keep them explicitly unidentified instead
    # of inventing them.
    budget = by_id["jp-local-172014-fiscal-2026-total-expenditure"]
    assert budget["fiscal_year"] == 2026
    assert budget["stage"] == "initial_budget"
    assert budget["metric"] == "total_expenditure"
    assert budget["metric_label"] == "一般会計当初予算総額"
    assert budget["amount_yen"] == 207800000000
    assert "告示第56号" in budget["note"]
    assert "議案番号と議決日は" in budget["note"]
    assert "特定していない" in budget["note"]

    # The FY2024 settlement totals are published at yen
    # precision in the city's official settlement summary
    # table (単位 円), so the yen figures below are the exact
    # published totals. Their difference must equal the
    # published balance (歳入歳出差引残額) of 8,476,976,027
    # yen, and they must be consistent with the sen-yen table
    # on the accounting division page.
    revenue = by_id["jp-local-172014-fiscal-2024-total-revenue"]
    assert revenue["fiscal_year"] == 2024
    assert revenue["stage"] == "settlement"
    assert revenue["metric"] == "total_revenue"
    assert revenue["amount_yen"] == 218624336395
    expenditure = by_id["jp-local-172014-fiscal-2024-total-expenditure"]
    assert expenditure["fiscal_year"] == 2024
    assert expenditure["stage"] == "settlement"
    assert expenditure["metric"] == "total_expenditure"
    assert expenditure["amount_yen"] == 210147360368
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 8476976027

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

    # The FY2026 budget claim must record the enactment route
    # (February 2026 session vote and gazette publication)
    # while keeping the bill number and vote date open.
    budget_packet = next(
        pkt
        for pkt in packets
        if pkt["subject_id"] == "jp-local-172014-fiscal-2026-total-expenditure"
    )
    assert "2月定例月議会" in budget_packet["claims"][0]["statement"]
    assert "成立" in budget_packet["claims"][0]["statement"]
    assert any(
        "議案番号" in question for question in budget_packet["open_questions"]
    )

    # The FY2024 settlement was certified as certification
    # bill No. 1 (認定第1号) at the December 2025 regular
    # monthly council session, per the council's official
    # deliberation results; the exact certification date is
    # not printed there and stays an open question.
    revenue_packet = next(
        pkt
        for pkt in packets
        if pkt["subject_id"] == "jp-local-172014-fiscal-2024-total-revenue"
    )
    assert "認定第1号" in revenue_packet["claims"][0]["statement"]
    assert "12月定例月議会" in revenue_packet["claims"][0]["statement"]
    assert "認定" in revenue_packet["claims"][0]["statement"]
    assert "認定第1号" in revenue["note"]
    assert "認定第1号" in expenditure["note"]
    assert any("認定日" in question for question in revenue_packet["open_questions"])

    plan_review = package["plan_review"]
    assert plan_review["review_status"] == "pending_record_review"
    decisions = {rec["id"]: rec["decision"] for rec in plan_review["records"]}
    # FY2024 is the first year of the plan period, but
    # settlement totals are section-level aggregates with no
    # official mapping to individual policies or KPIs, so
    # the linkage stays explicitly not assessable.
    assert decisions["kanazawa-fy2024-settlement-linkage"] == "not_assessable"
    assert all(
        decision in {"needs_review", "not_assessable"}
        for decision in decisions.values()
    )
    period = next(
        rec
        for rec in plan_review["records"]
        if rec["id"] == "kanazawa-current-plan-period"
    )
    assert period["value"] == "2024年度～2033年度"

    # The plan's revisions (February 2025 and June 2026) are
    # recorded only as a version chronology record, never
    # merged back into the original plan's framework.
    transition = next(
        rec
        for rec in plan_review["records"]
        if rec["id"] == "kanazawa-plan-revision-chronology"
    )
    assert transition["evidence_role"] == "plan_transition"
    assert "令和8年6月改訂" in transition["statement"]

    # The current plan is the Future Co-Creation Plan
    # (未来共創計画), a single ten-year action plan under the
    # city vision (FY2024 to FY2033). Its basic goals are the
    # five basic policies of the city vision, and the
    # measures under each goal are its policy directions
    # (21 in total), exactly as published in the plan's main
    # text (June 2026 revised edition); the individual
    # measures/projects under each policy direction are not
    # enumerated here.
    current_plan = package["policy_structure"]["current_plan"]
    assert current_plan["title"] == "未来共創計画"
    assert current_plan["start_fiscal_year"] == 2024
    assert current_plan["end_fiscal_year"] == 2033
    assert current_plan["vision"] == "未来を拓く世界の共創文化都市・金沢"
    goals = current_plan["basic_goals"]
    assert [goal["name_ja"] for goal in goals] == [
        "世界に誇る伝統と創造の文化が息づくまち ～魅力づくり～",
        "多様な人々が共生し、心豊かに暮らせるまち ～暮らしづくり～",
        "共に学び、未来を創る人を育むまち ～人づくり～",
        "創造・変革により成長するまち ～仕事づくり～",
        "活力と個性があふれ、安全で持続可能なまち ～都市づくり～",
    ]
    assert [goal["measures"] for goal in goals] == [
        [
            "誰もが文化芸術に親しむことができる環境の充実",
            "歴史と伝統に培われた文化の継承・発展",
            "まちの品格を高める新たな文化の創造",
            "世界の人々が憧れ滞在したくなる都市ブランド力の向上",
        ],
        [
            "多様な主体の協働による元気で活力あふれる地域コミュニティの醸成",
            "誰もが安心して共に暮らせる地域社会の実現",
            "心身ともに健やかに暮らせる健康都市の推進",
            "人と自然が共生する地球にやさしい生活環境の形成",
        ],
        [
            "妊娠・出産から子どもの成長に合わせた切れ目のない支援",
            "すべての子どもの可能性を引き出し生きる力を育む教育の実践",
            "学都の強みを生かした次代の担い手育成",
            "学びの文化の形成と情操教育の推進",
        ],
        [
            "地域経済をけん引する新たな産業の創出・育成",
            "あらゆる世代の多様な人材の活躍と働き方の推進",
            "にぎわいのある商業環境の形成とものづくり産業の継承・発展",
            "次代につなぐ魅力ある農林水産業の振興",
        ],
        [
            "魅力あふれる中心市街地の活性化",
            "歴史や自然と調和した都市景観の形成",
            "人と活力の還流による地域の再生",
            "市民生活を支える交通ネットワークの確保",
            "災害に強く効率的で質の高い都市運営の実践",
        ],
    ]


def test_kanazawa_promotion_is_reflected_in_canonical_queue():
    queue = read(QUEUE)
    item = next(
        row for row in queue["execution_queue"] if row["official_code"] == "172014"
    )
    assert item["status"] == "reviewed_complete"
    assert item["completion_path"] == "data/catalog/kanazawa_phase15_completion.json"
    assert queue["summary"]["reviewed_complete_count"] == 34
    assert queue["summary"]["pending_record_review_count"] == 33
    assert queue["summary"]["next_official_code"] == "252018"


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
