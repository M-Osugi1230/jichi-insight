"""Safety tests for Toyohashi Phase 15 non-public review candidate."""

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "data/candidates/toyohashi-city/review_candidate.json"
INVENTORY = ROOT / "data/indexed/toyohashi-city/source_inventory.json"
SCHEMA = ROOT / "schemas/phase15_review_candidate.schema.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"
WEB_ROOT = ROOT / "apps/web"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_toyohashi_candidate_validates_and_is_not_published():
    candidate = read(CANDIDATE)
    schema = read(SCHEMA)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = list(validator.iter_errors(candidate))
    assert errors == []
    assert candidate["candidate_id"] == "toyohashi-phase15-review-candidate"
    assert candidate["phase"] == 15
    assert candidate["official_code"] == "232017"
    assert candidate["name_ja"] == "豊橋市"
    assert (
        candidate["source_inventory_path"]
        == "data/indexed/toyohashi-city/source_inventory.json"
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


def test_toyohashi_sources_match_existing_official_inventory():
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
        source["official_url"].startswith("https://www.city.toyohashi.lg.jp/")
        for source in sources
    )
    assert all(
        source["verification_status"] == "primary_source_live_verified_2026-11-16"
        for source in sources
    )
    assert all(bool(source["evidence_location"]) for source in sources)
    assert all(bool(source["use_boundary"]) for source in sources)


def test_toyohashi_prepared_candidate_records_only_verified_fiscal_values():
    candidate = read(CANDIDATE)
    package = candidate["candidate_package"]

    fiscal_records = package["fiscal_records"]
    assert len(fiscal_records) == 3
    by_id = {rec["id"]: rec for rec in fiscal_records}
    assert set(by_id) == {
        "jp-local-232017-fiscal-2026-total-expenditure",
        "jp-local-232017-fiscal-2024-total-revenue",
        "jp-local-232017-fiscal-2024-total-expenditure",
    }
    assert all(rec["municipality_id"] == "jp-local-232017" for rec in fiscal_records)
    assert all(rec["account_type"] == "general" for rec in fiscal_records)
    assert all(rec["value_status"] == "available" for rec in fiscal_records)
    assert all(rec["review_status"] == "needs_review" for rec in fiscal_records)
    assert all(rec["confidence"] == "medium" for rec in fiscal_records)

    # The FY2026 initial budget was submitted to the
    # March 2026 regular council session as bill No. 4
    # (議案第4号) and passed as proposed on 2026-03-24
    # per the council's official voting-results list, so
    # the budget must not be labelled as a draft proposal
    # (予算案). The amount is the exact sen-yen total
    # published by the city (165,610,000 thousand yen,
    # up 9,710,000 thousand yen / 6.2% from FY2025's
    # 155,900,000 thousand yen), and the June 2026
    # supplementary-budget material carries the same
    # current-budget total.
    budget = by_id["jp-local-232017-fiscal-2026-total-expenditure"]
    assert budget["fiscal_year"] == 2026
    assert budget["stage"] == "initial_budget"
    assert budget["metric"] == "total_expenditure"
    assert budget["metric_label"] == "一般会計当初予算総額"
    assert budget["amount_yen"] == 165610000000
    assert "議案第4号" in budget["note"]
    assert "令和8年3月24日" in budget["note"]
    assert "原案可決" in budget["note"]
    assert "成立" in budget["note"]

    # The FY2024 settlement totals are published at yen
    # precision in the city's official settlement
    # appendix (account-level table and section summary
    # table agree), so the yen figures below are the
    # exact published totals. Their difference must
    # equal the balance of 2,115,423,672 yen, which is
    # consistent with the published 2,115,424 thousand
    # yen (rounded) in the city's settlement summary.
    revenue = by_id["jp-local-232017-fiscal-2024-total-revenue"]
    assert revenue["fiscal_year"] == 2024
    assert revenue["stage"] == "settlement"
    assert revenue["metric"] == "total_revenue"
    assert revenue["amount_yen"] == 153279132232
    expenditure = by_id["jp-local-232017-fiscal-2024-total-expenditure"]
    assert expenditure["fiscal_year"] == 2024
    assert expenditure["stage"] == "settlement"
    assert expenditure["metric"] == "total_expenditure"
    assert expenditure["amount_yen"] == 151163708560
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 2115423672

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
    # route (bill No. 4, passed as proposed on
    # 2026-03-24).
    budget_packet = next(
        pkt
        for pkt in packets
        if pkt["subject_id"] == "jp-local-232017-fiscal-2026-total-expenditure"
    )
    assert "議案第4号" in budget_packet["claims"][0]["statement"]
    assert "原案可決" in budget_packet["claims"][0]["statement"]
    assert "成立" in budget_packet["claims"][0]["statement"]

    # The FY2024 settlement certification bill (bill
    # No. 95, 議案第95号) was REJECTED (不認定) in the
    # September 2025 regular session. The candidate must
    # record the rejection itself and must never state
    # that the settlement was certified.
    revenue_packet = next(
        pkt
        for pkt in packets
        if pkt["subject_id"] == "jp-local-232017-fiscal-2024-total-revenue"
    )
    assert "議案第95号" in revenue_packet["claims"][0]["statement"]
    assert "不認定" in revenue_packet["claims"][0]["statement"]
    assert "議案第95号" in revenue["note"]
    assert "不認定" in revenue["note"]
    assert "議案第95号" in expenditure["note"]
    assert "不認定" in expenditure["note"]

    plan_review = package["plan_review"]
    assert plan_review["review_status"] == "pending_record_review"
    decisions = {rec["id"]: rec["decision"] for rec in plan_review["records"]}
    # FY2024 sits inside the previous (first-period)
    # basic plan (2021-2025), while the current latter
    # basic plan starts in FY2026, so the plan versions
    # differ and no official total-level mapping from
    # settlement totals to the latter plan's policies or
    # strategies exists; the linkage stays not
    # assessable.
    assert decisions["toyohashi-fy2024-settlement-linkage"] == "not_assessable"
    assert all(
        decision in {"needs_review", "not_assessable"}
        for decision in decisions.values()
    )
    period = next(
        rec
        for rec in plan_review["records"]
        if rec["id"] == "toyohashi-current-plan-period"
    )
    assert period["value"] == "2026年度～2030年度"

    # The transition from the first-period to the
    # latter basic plan is recorded only as a version
    # chronology record, never by retroactively mapping
    # the latter plan's policies onto earlier results.
    transition = next(
        rec for rec in plan_review["records"] if rec["id"] == "toyohashi-plan-transition"
    )
    assert transition["evidence_role"] == "plan_transition"
    assert "後期基本計画" in transition["statement"]

    # The current plan is the latter basic plan of the
    # Sixth Toyohashi City Comprehensive Plan: a
    # fixed-term three-layer plan (basic concept
    # 2021-2030, basic plan, three-year rolling
    # implementation plan) whose field structure is
    # eight fields and 38 policies, exactly as
    # published in the official implementation plan,
    # plus the cross-field Machizukuri Strategy with
    # four individual strategies.
    current_plan = package["policy_structure"]["current_plan"]
    assert current_plan["title"] == "第6次豊橋市総合計画 後期基本計画"
    assert current_plan["vision"] == "未来を担う 人を育むまち・豊橋"
    assert current_plan["start_fiscal_year"] == 2026
    assert current_plan["end_fiscal_year"] == 2030
    fields = current_plan["policy_fields"]
    assert [field["name_ja"] for field in fields] == [
        "豊かな人間性を備え、未来を創る人が育つまち",
        "活力みなぎり、はつらつと働けるまち",
        "命の安全、心の安心が確保されたまち",
        "みんなで支え合い、笑顔で健やかに暮らせるまち",
        "互いを尊重し合い、心豊かに暮らせるまち",
        "魅力にあふれ、いきいきとにぎわいあるまち",
        "自然と共生し、地球環境を大切にするまち",
        "暮らしの基盤が整った、便利で快適なまち",
    ]
    assert [field["measures"] for field in fields] == [
        [
            "子育て支援・児童福祉の充実",
            "学校教育の推進",
            "生涯学習・地域教育の推進",
            "科学教育の推進",
            "子ども・若者の健全育成",
        ],
        [
            "農漁業の振興",
            "商工業の振興",
            "雇用の安定と働き方の充実",
            "三河港の振興",
        ],
        [
            "危機管理の強化と防災・減災の推進",
            "消防・救急救命体制の充実",
            "暮らしの安全確保",
            "生活衛生の確保",
        ],
        [
            "健康づくりの推進",
            "医療の充実",
            "地域福祉の充実",
            "高齢者福祉・介護保険の充実",
            "障害者（児）福祉の充実",
            "生活自立の支援",
        ],
        [
            "文化芸術の振興",
            "スポーツの推進",
            "美術の振興と歴史文化の継承",
            "多文化共生・国際化の推進",
            "市民協働の推進",
            "男女共同参画・性の多様性を尊重する社会づくり",
        ],
        [
            "まちなかの活性化",
            "のんほいパークの魅力向上",
            "シティプロモーションの推進",
            "観光の振興",
        ],
        [
            "気候変動対策の推進",
            "資源循環の推進",
            "自然環境の保全",
            "緑の環境づくり",
        ],
        [
            "都市空間の形成",
            "交通環境の充実",
            "住宅環境の整備",
            "水道水の安定供給",
            "下水の適正処理",
        ],
    ]
    assert sum(len(field["measures"]) for field in fields) == 38
    strategy = current_plan["strategy_layer"]
    assert strategy["title"] == "まちづくり戦略"
    assert [item["name_ja"] for item in strategy["strategies"]] == [
        "安心に包まれた子育て・教育環境づくり",
        "希望に満ちた仕事づくり",
        "定住につながるまちの魅力づくり",
        "暮らしを支える都市空間づくり",
    ]
    assert [item["basic_policies"] for item in strategy["strategies"]] == [
        [
            "子ども・若者の成長を支える環境づくり",
            "未来を創る教育の推進",
            "妊娠、出産、子育てへの包括的支援",
            "地域で子育てを応援する環境づくり",
        ],
        [
            "産業インフラの整備",
            "経営基盤の強化と新たな地域産業の創出",
            "多様な働き方の推進と人材確保・育成",
        ],
        [
            "定住の推進",
            "多様な活動の拠点を生かしたまちの活力創出",
            "地域資源の磨き上げと情報発信",
        ],
        [
            "安全で安心できる暮らしやすいまちの強靭化",
            "便利で快適な住みよいまちの形成",
            "環境に配慮した社会づくり",
        ],
    ]


def test_toyohashi_promotion_is_reflected_in_canonical_queue():
    queue = read(QUEUE)
    item = next(
        row for row in queue["execution_queue"] if row["official_code"] == "232017"
    )
    assert item["status"] == "reviewed_complete"
    assert item["completion_path"] == "data/catalog/toyohashi_phase15_completion.json"
    assert queue["summary"]["reviewed_complete_count"] == 50
    assert queue["summary"]["pending_record_review_count"] == 17
    assert queue["summary"]["next_official_code"] == "332020"


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
