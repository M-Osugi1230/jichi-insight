"""Safety tests for Gifu Phase 15 non-public review candidate."""

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "data/candidates/gifu-city/review_candidate.json"
INVENTORY = ROOT / "data/indexed/gifu-city/source_inventory.json"
SCHEMA = ROOT / "schemas/phase15_review_candidate.schema.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"
WEB_ROOT = ROOT / "apps/web"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_gifu_candidate_validates_and_is_not_published():
    candidate = read(CANDIDATE)
    schema = read(SCHEMA)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = list(validator.iter_errors(candidate))
    assert errors == []
    assert candidate["candidate_id"] == "gifu-phase15-review-candidate"
    assert candidate["phase"] == 15
    assert candidate["official_code"] == "212016"
    assert candidate["name_ja"] == "岐阜市"
    assert (
        candidate["source_inventory_path"]
        == "data/indexed/gifu-city/source_inventory.json"
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


def test_gifu_sources_match_existing_official_inventory():
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
        source["official_url"].startswith("https://www.city.gifu.lg.jp/")
        for source in sources
    )
    assert all(
        source["verification_status"] == "primary_source_live_verified_2026-11-16"
        for source in sources
    )
    assert all(bool(source["evidence_location"]) for source in sources)
    assert all(bool(source["use_boundary"]) for source in sources)


def test_gifu_prepared_candidate_records_only_verified_fiscal_values():
    candidate = read(CANDIDATE)
    package = candidate["candidate_package"]

    fiscal_records = package["fiscal_records"]
    assert len(fiscal_records) == 3
    by_id = {rec["id"]: rec for rec in fiscal_records}
    assert set(by_id) == {
        "jp-local-212016-fiscal-2026-total-expenditure",
        "jp-local-212016-fiscal-2024-total-revenue",
        "jp-local-212016-fiscal-2024-total-expenditure",
    }
    assert all(rec["municipality_id"] == "jp-local-212016" for rec in fiscal_records)
    assert all(rec["account_type"] == "general" for rec in fiscal_records)
    assert all(rec["value_status"] == "available" for rec in fiscal_records)
    assert all(rec["review_status"] == "needs_review" for rec in fiscal_records)
    assert all(rec["confidence"] == "medium" for rec in fiscal_records)

    # The FY2026 initial budget was submitted to the
    # March 2026 regular council session as bill No. 1
    # (第1号議案) and passed as proposed on 2026-03-27
    # per the council's official voting-results list, so
    # the budget must not be labelled as a draft proposal
    # (予算案). The amount is the exact sen-yen total of
    # the official initial-budget booklet (200,680,000
    # thousand yen, up 3,580,000 thousand yen / 1.82%
    # from FY2025's 197,100,000 thousand yen), and the
    # official budget explanatory book carries the same
    # revenue and expenditure totals.
    budget = by_id["jp-local-212016-fiscal-2026-total-expenditure"]
    assert budget["fiscal_year"] == 2026
    assert budget["stage"] == "initial_budget"
    assert budget["metric"] == "total_expenditure"
    assert budget["metric_label"] == "一般会計当初予算総額"
    assert budget["amount_yen"] == 200680000000
    assert "第1号議案" in budget["note"]
    assert "令和8年3月27日" in budget["note"]
    assert "原案のとおり可決" in budget["note"]
    assert "成立" in budget["note"]

    # The FY2024 settlement totals are published at yen
    # precision in the city's official settlement-by-
    # account table, so the yen figures below are the
    # exact published totals. Their difference must
    # equal the published balance (歳入歳出差引額) of
    # 6,686,174,381 yen. The revenue total also matches
    # the section-level revenue table of the official
    # general-account settlement document.
    revenue = by_id["jp-local-212016-fiscal-2024-total-revenue"]
    assert revenue["fiscal_year"] == 2024
    assert revenue["stage"] == "settlement"
    assert revenue["metric"] == "total_revenue"
    assert revenue["amount_yen"] == 198779091770
    expenditure = by_id["jp-local-212016-fiscal-2024-total-expenditure"]
    assert expenditure["fiscal_year"] == 2024
    assert expenditure["stage"] == "settlement"
    assert expenditure["metric"] == "total_expenditure"
    assert expenditure["amount_yen"] == 192092917389
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 6686174381

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
    # route (bill No. 1, passed as proposed on
    # 2026-03-27).
    budget_packet = next(
        pkt
        for pkt in packets
        if pkt["subject_id"] == "jp-local-212016-fiscal-2026-total-expenditure"
    )
    assert "第1号議案" in budget_packet["claims"][0]["statement"]
    assert "原案のとおり可決" in budget_packet["claims"][0]["statement"]
    assert "成立" in budget_packet["claims"][0]["statement"]

    # The FY2024 settlement was certified as bill
    # No. 107 of the September 2025 regular session
    # (第107号議案, covering the general account and
    # the special accounts) on 2025-09-25, per the
    # council's official voting-results list.
    revenue_packet = next(
        pkt
        for pkt in packets
        if pkt["subject_id"] == "jp-local-212016-fiscal-2024-total-revenue"
    )
    assert "第107号議案" in revenue_packet["claims"][0]["statement"]
    assert "令和7年9月25日" in revenue_packet["claims"][0]["statement"]
    assert "認定" in revenue_packet["claims"][0]["statement"]
    assert "第107号議案" in revenue["note"]
    assert "第107号議案" in expenditure["note"]

    plan_review = package["plan_review"]
    assert plan_review["review_status"] == "pending_record_review"
    decisions = {rec["id"]: rec["decision"] for rec in plan_review["records"]}
    # FY2024 sits inside the concept period (third year
    # of the concept, first year of the 2024-2027
    # strategy), but settlement totals are account- and
    # section-level aggregates and the concept's
    # indicators are citizen-survey based, so no
    # official total-level mapping to the concept's
    # fields, indicators, or strategy KPIs exists and
    # the linkage stays not assessable.
    assert decisions["gifu-fy2024-settlement-linkage"] == "not_assessable"
    assert all(
        decision in {"needs_review", "not_assessable"}
        for decision in decisions.values()
    )
    period = next(
        rec
        for rec in plan_review["records"]
        if rec["id"] == "gifu-current-framework-period"
    )
    assert period["value"] == "2022年度開始・固定終期なし（2040年頃を見据える）"

    # The revision of the concept is recorded only as a
    # transition chronology record, never as the revised
    # framework itself.
    transition = next(
        rec for rec in plan_review["records"] if rec["id"] == "gifu-plan-revision-transition"
    )
    assert transition["evidence_role"] == "plan_transition"
    assert "改定" in transition["statement"]

    # The current framework is the Gifu City Future
    # City-Building Concept: a vision-type framework
    # with no fixed end year (a horizon of around 2040
    # with five-year reviews), not a fixed-term layered
    # comprehensive plan. Its policy structure is four
    # basic approaches and five policy fields, exactly
    # as published in the concept's official text, plus
    # the subordinate Future Creation Comprehensive
    # Strategy (FY2024 to FY2027, three pillars).
    framework = package["policy_structure"]["current_framework"]
    assert framework["title"] == "岐阜市未来のまちづくり構想"
    assert framework["vision"] == "人がつながる 創造が生まれる しなやかさのあるまち"
    assert framework["start_fiscal_year"] == 2022
    assert framework["end_fiscal_year"] is None
    assert framework["period_status"] == "no_fixed_end"
    assert framework["basic_approaches"] == [
        "オール岐阜のまちづくり",
        "シビックプライドの醸成",
        "DXと脱炭素化",
        "持続可能で選ばれるまち",
    ]
    fields = framework["policy_fields"]
    assert [field["name_ja"] for field in fields] == [
        "教育・子育て",
        "健康・福祉・医療",
        "市民協働・防災・環境",
        "産業・労働・交流",
        "都市基盤整備・交通・中心市街地活性化",
    ]
    assert [field["indicators"] for field in fields] == [
        [
            "子育てしやすい",
            "子どもたちの教育環境が充実している",
            "生涯にわたり文化・芸術活動やスポーツ活動などに取り組みやすい",
        ],
        [
            "元気で長生きできる",
            "高齢者や障がいのある方が暮らしやすい",
            "医療環境が充実",
        ],
        [
            "自治会などの地域活動が盛ん",
            "災害に対して安全",
            "省エネやごみの減量など環境に配慮",
        ],
        [
            "企業などが新事業を展開しやすい",
            "就労環境に恵まれている",
            "観光資源が豊か",
        ],
        [
            "道路や公園などの都市基盤が整っている",
            "コミュニティバスなどの公共交通が便利",
            "中心市街地のにぎわいが高まっている",
        ],
    ]
    strategy = framework["strategy_layer"]
    assert strategy["title"] == "岐阜市未来創生総合戦略"
    assert strategy["start_fiscal_year"] == 2024
    assert strategy["end_fiscal_year"] == 2027
    assert strategy["pillars"] == ["ひとの創生", "しごとの創生", "まちの創生"]


def test_gifu_promotion_is_reflected_in_canonical_queue():
    queue = read(QUEUE)
    item = next(
        row for row in queue["execution_queue"] if row["official_code"] == "212016"
    )
    assert item["status"] == "reviewed_complete"
    assert item["completion_path"] == "data/catalog/gifu_phase15_completion.json"
    assert queue["summary"]["reviewed_complete_count"] == 57
    assert queue["summary"]["pending_record_review_count"] == 10
    assert queue["summary"]["next_official_code"] == "382019"


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
