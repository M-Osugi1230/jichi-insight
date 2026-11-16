"""Safety tests for Otsu Phase 15 non-public review candidate."""

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "data/candidates/otsu-city/review_candidate.json"
INVENTORY = ROOT / "data/indexed/otsu-city/source_inventory.json"
SCHEMA = ROOT / "schemas/phase15_review_candidate.schema.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"
WEB_ROOT = ROOT / "apps/web"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_otsu_candidate_validates_and_is_not_published():
    candidate = read(CANDIDATE)
    schema = read(SCHEMA)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = list(validator.iter_errors(candidate))
    assert errors == []
    assert candidate["candidate_id"] == "otsu-phase15-review-candidate"
    assert candidate["phase"] == 15
    assert candidate["official_code"] == "252018"
    assert candidate["name_ja"] == "大津市"
    assert (
        candidate["source_inventory_path"]
        == "data/indexed/otsu-city/source_inventory.json"
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


def test_otsu_sources_match_existing_official_inventory():
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
        source["official_url"].startswith("https://www.city.otsu.lg.jp/")
        for source in sources
    )
    assert all(
        source["verification_status"] == "primary_source_live_verified_2026-11-16"
        for source in sources
    )
    assert all(bool(source["evidence_location"]) for source in sources)
    assert all(bool(source["use_boundary"]) for source in sources)


def test_otsu_prepared_candidate_records_only_verified_fiscal_values():
    candidate = read(CANDIDATE)
    package = candidate["candidate_package"]

    fiscal_records = package["fiscal_records"]
    assert len(fiscal_records) == 3
    by_id = {rec["id"]: rec for rec in fiscal_records}
    assert set(by_id) == {
        "jp-local-252018-fiscal-2026-total-expenditure",
        "jp-local-252018-fiscal-2024-total-revenue",
        "jp-local-252018-fiscal-2024-total-expenditure",
    }
    assert all(rec["municipality_id"] == "jp-local-252018" for rec in fiscal_records)
    assert all(rec["account_type"] == "general" for rec in fiscal_records)
    assert all(rec["value_status"] == "available" for rec in fiscal_records)
    assert all(rec["review_status"] == "needs_review" for rec in fiscal_records)
    assert all(rec["confidence"] == "medium" for rec in fiscal_records)

    # The FY2026 initial budget was submitted to the
    # February 2026 regular session as bill No. 3
    # (議案第3号) on 2026-02-19 and was passed on
    # 2026-03-25, so the budget must not be labelled
    # as a draft proposal (予算案). The council's
    # official bill-result list records the result
    # only as "可決 (多数)" and does not use the
    # wording "原案可決", so the candidate must keep
    # the city's published wording and must not assert
    # 原案可決 anywhere. The amount is the exact
    # sen-yen total published by the city
    # (142,684,000 thousand yen), confirmed in both
    # the official budget book (bill No. 3, Article 1)
    # and the official budget overview summary table.
    budget = by_id["jp-local-252018-fiscal-2026-total-expenditure"]
    assert budget["fiscal_year"] == 2026
    assert budget["stage"] == "initial_budget"
    assert budget["metric"] == "total_expenditure"
    assert budget["metric_label"] == "一般会計当初予算総額"
    assert budget["amount_yen"] == 142684000000
    assert "議案第3号" in budget["note"]
    assert "令和8年3月25日" in budget["note"]
    assert "成立" in budget["note"]
    assert "可決（多数）" in budget["note"]
    assert "『原案可決』とは表記していない" in budget["note"]
    assert "原案可決され" not in budget["note"]

    # The FY2024 settlement totals are published at yen
    # precision in the official settlement book
    # attached to bill No. 110 (general-account
    # summary table), so the yen figures below are the
    # exact published totals. Their difference must
    # equal the balance of 2,976,660,134 yen printed
    # in the settlement book, and the expenditure
    # total plus the carryover and the unused amount
    # must equal the published budget total.
    revenue = by_id["jp-local-252018-fiscal-2024-total-revenue"]
    assert revenue["fiscal_year"] == 2024
    assert revenue["stage"] == "settlement"
    assert revenue["metric"] == "total_revenue"
    assert revenue["amount_yen"] == 146909564029
    expenditure = by_id["jp-local-252018-fiscal-2024-total-expenditure"]
    assert expenditure["fiscal_year"] == 2024
    assert expenditure["stage"] == "settlement"
    assert expenditure["metric"] == "total_expenditure"
    assert expenditure["amount_yen"] == 143932903895
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 2976660134
    assert expenditure["amount_yen"] + 2684839000 + 3581702105 == 150199445000

    # The actual balance (実質収支) is confirmed only
    # at thousand-yen precision in the audit
    # committee's settlement review opinion
    # (2,791,920 thousand yen, after deducting
    # 184,740 thousand yen of resources to be carried
    # forward from the 2,976,660 thousand yen formal
    # balance), so the candidate records it at
    # thousand-yen precision exactly as published and
    # does not synthesise a yen figure.
    assert "2,791,920千円" in revenue["note"]
    assert "184,740千円" in revenue["note"]

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
    # route (bill No. 3, passed on 2026-03-25) with the
    # council's published wording, without asserting
    # the unconfirmed wording 原案可決.
    budget_packet = next(
        pkt
        for pkt in packets
        if pkt["subject_id"] == "jp-local-252018-fiscal-2026-total-expenditure"
    )
    assert "議案第3号" in budget_packet["claims"][0]["statement"]
    assert "成立" in budget_packet["claims"][0]["statement"]
    assert "令和8年3月25日" in budget_packet["claims"][0]["statement"]
    assert "可決（多数）" in budget_packet["claims"][0]["statement"]
    assert "『原案可決』とは表記していない" in budget_packet["claims"][0]["statement"]
    assert "原案可決され" not in budget_packet["claims"][0]["statement"]
    assert "『原案可決』とは記録しない" in budget_packet["claims"][0]["review_note"]

    # The FY2024 settlement certification bill is
    # bill No. 110 (議案第110号). It was submitted to
    # the August 2025 regular session, referred to the
    # Budget and Settlement Standing Committee, and
    # the council's official bill-result list directly
    # records the result as certified (認定 (多数)) on
    # 2025-10-28, so the candidate must record the
    # certification as a confirmed fact with that
    # date, and must never record it as rejected
    # (不認定) in any claim statement.
    revenue_packet = next(
        pkt
        for pkt in packets
        if pkt["subject_id"] == "jp-local-252018-fiscal-2024-total-revenue"
    )
    assert "議案第110号" in revenue_packet["claims"][0]["statement"]
    assert "認定された" in revenue_packet["claims"][0]["statement"]
    assert "令和7年10月28日" in revenue_packet["claims"][0]["statement"]
    assert "不認定" not in revenue_packet["claims"][0]["statement"]
    expenditure_packet = next(
        pkt
        for pkt in packets
        if pkt["subject_id"] == "jp-local-252018-fiscal-2024-total-expenditure"
    )
    assert "議案第110号" in expenditure_packet["claims"][0]["statement"]
    assert "認定された" in expenditure_packet["claims"][0]["statement"]
    assert "不認定" not in expenditure_packet["claims"][0]["statement"]
    assert "議案第110号" in revenue["note"]
    assert "議案第110号" in expenditure["note"]
    assert "令和7年10月28日" in revenue["note"]

    plan_review = package["plan_review"]
    assert plan_review["review_status"] == "pending_record_review"
    decisions = {rec["id"]: rec["decision"] for rec in plan_review["records"]}
    # FY2024 is the final year of the second action
    # plan (FY2021-FY2024), while the current framework
    # is the third action plan (FY2025-FY2028), so the
    # plan version differs and no official total-level
    # mapping from settlement totals to the plan's
    # basic directions, basic policies or measures
    # exists. The linkage therefore stays not
    # assessable.
    assert decisions["otsu-fy2024-settlement-linkage"] == "not_assessable"
    assert all(
        decision in {"needs_review", "not_assessable"}
        for decision in decisions.values()
    )
    period = next(
        rec for rec in plan_review["records"] if rec["id"] == "otsu-current-plan-period"
    )
    assert period["value"] == "2017年度～2028年度"

    # The succession of action plans is recorded only
    # as version chronology, never by retroactively
    # mapping another plan's framework onto prior
    # results.
    transition = next(
        rec for rec in plan_review["records"] if rec["id"] == "otsu-plan-transition"
    )
    assert transition["evidence_role"] == "plan_transition"
    assert "第1期実行計画" in transition["statement"]
    assert "第3期実行計画" in transition["statement"]

    # The current operative plan layer is the third
    # action plan of the Otsu City Comprehensive Plan
    # (FY2025-FY2028), under the Basic Concept
    # (FY2017-FY2028) whose vision is ひと、自然、
    # 歴史の縁で織りなす 住み続けたいまち"大津再生".
    # Its structure is three basic directions, 13
    # basic policies and 32 measures, exactly as
    # published in the official plan overview's
    # structure chart.
    current_plan = package["policy_structure"]["current_plan"]
    assert current_plan["title"] == "大津市総合計画 第3期実行計画"
    assert (
        current_plan["vision"]
        == "ひと、自然、歴史の縁で織りなす 住み続けたいまち“大津再生” "
        "～コンパクトで持続可能なまちへの変革～"
    )
    assert current_plan["start_fiscal_year"] == 2025
    assert current_plan["end_fiscal_year"] == 2028
    fields = current_plan["policy_fields"]
    assert [field["name_ja"] for field in fields] == [
        "基本方針1-基本政策1 子どもの未来が輝くまちにします",
        "基本方針1-基本政策2 心豊かに暮らせる、福祉が充実したまちにします",
        "基本方針1-基本政策3 生き生きと健康に過ごせるまちにします",
        "基本方針1-基本政策4 つながりを大切にし、共に支え合うまちにします",
        "基本方針2-基本政策5 インバウンド観光で人が集い、にぎわうまちにします",
        "基本方針2-基本政策6 自然豊かな景観を守り育て、自然と共生するまちにします",
        "基本方針2-基本政策7 悠久の歴史と文化を大切にし、次代に継承します",
        "基本方針2-基本政策8 スポーツと文化で、生き生きと楽しむまちにします",
        "基本方針3-基本政策9 安心、安全に暮らすことのできるまちにします",
        "基本方針3-基本政策10 コンパクトで質の高い持続可能なまちにします",
        "基本方針3-基本政策11 経済が活性化し、元気なまちにします",
        "基本方針3-基本政策12 再生可能エネルギーの活用とごみの適正処理でクリーンなまちにします",
        "基本方針3-基本政策13 徹底した行財政改革を進め、確かな都市経営を進めます",
    ]
    assert [field["measures"] for field in fields] == [
        ["切れ目のない子育て支援", "子どもを守る仕組みの充実", "子どもの教育の充実"],
        [
            "高齢者の福祉・介護の充実と活躍推進",
            "障害者福祉の充実と社会参加の促進",
            "地域福祉の推進と社会保障制度の安定運営",
        ],
        ["生涯にわたる健康づくりの推進", "地域医療と保健衛生の確保", "生涯学習の推進"],
        ["地域コミュニティの維持・活性化", "人権及び平和意識の高揚と男女共同参画の推進"],
        [
            "観光・MICEの推進",
            "まちの魅力を生かしたにぎわいの創出",
            "多文化共生・国際理解の推進",
        ],
        ["自然環境の保全"],
        ["歴史文化遺産の保存・活用", "古都にふさわしい景観づくり"],
        ["スポーツの推進", "文化・芸術活動の推進"],
        [
            "災害に強いまちづくりの推進",
            "安心して暮らせるまちづくりの推進",
            "ライフラインの確保",
        ],
        ["持続可能で活力ある地域形成", "交通ネットワークの充実", "住環境の整備"],
        ["商工業の振興", "農林水産業の振興", "就労支援と労働環境の充実"],
        ["脱炭素社会の推進", "循環型社会の推進"],
        ["持続可能な行財政運営", "スマート自治体の推進"],
    ]
    assert sum(len(field["measures"]) for field in fields) == 32


def test_otsu_promotion_is_reflected_in_canonical_queue():
    queue = read(QUEUE)
    item = next(
        row for row in queue["execution_queue"] if row["official_code"] == "252018"
    )
    assert item["status"] == "reviewed_complete"
    assert item["completion_path"] == "data/catalog/otsu_phase15_completion.json"
    assert queue["summary"]["reviewed_complete_count"] == 67
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
