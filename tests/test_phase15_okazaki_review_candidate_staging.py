"""Safety tests for Okazaki Phase 15 non-public review candidate."""

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "data/candidates/okazaki-city/review_candidate.json"
INVENTORY = ROOT / "data/indexed/okazaki-city/source_inventory.json"
SCHEMA = ROOT / "schemas/phase15_review_candidate.schema.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"
WEB_ROOT = ROOT / "apps/web"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_okazaki_candidate_validates_and_is_not_published():
    candidate = read(CANDIDATE)
    schema = read(SCHEMA)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = list(validator.iter_errors(candidate))
    assert errors == []
    assert candidate["candidate_id"] == "okazaki-phase15-review-candidate"
    assert candidate["phase"] == 15
    assert candidate["official_code"] == "232025"
    assert candidate["name_ja"] == "岡崎市"
    assert (
        candidate["source_inventory_path"]
        == "data/indexed/okazaki-city/source_inventory.json"
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


def test_okazaki_sources_match_existing_official_inventory():
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
        source["official_url"].startswith("https://www.city.okazaki.lg.jp/")
        for source in sources
    )
    assert all(
        source["verification_status"] == "primary_source_live_verified_2026-11-16"
        for source in sources
    )
    assert all(bool(source["evidence_location"]) for source in sources)
    assert all(bool(source["use_boundary"]) for source in sources)


def test_okazaki_prepared_candidate_records_only_verified_fiscal_values():
    candidate = read(CANDIDATE)
    package = candidate["candidate_package"]

    fiscal_records = package["fiscal_records"]
    assert len(fiscal_records) == 3
    by_id = {rec["id"]: rec for rec in fiscal_records}
    assert set(by_id) == {
        "jp-local-232025-fiscal-2026-total-expenditure",
        "jp-local-232025-fiscal-2024-total-revenue",
        "jp-local-232025-fiscal-2024-total-expenditure",
    }
    assert all(rec["municipality_id"] == "jp-local-232025" for rec in fiscal_records)
    assert all(rec["account_type"] == "general" for rec in fiscal_records)
    assert all(rec["value_status"] == "available" for rec in fiscal_records)
    assert all(rec["review_status"] == "needs_review" for rec in fiscal_records)
    assert all(rec["confidence"] == "medium" for rec in fiscal_records)

    # The FY2026 initial budget was submitted to the
    # March 2026 regular council session as bill No. 56
    # (第56号議案), referred to the Budget and Settlement
    # Committee, and voted on the session's final day,
    # 2026-03-23, per the official session agendas, so
    # the budget must not be labelled as a draft proposal
    # (予算案). The amount is the exact sen-yen total
    # published by the city (154,850,000 thousand yen,
    # up 1,160,000 thousand yen / 0.8% from FY2025's
    # 153,690,000 thousand yen). The March 2026 voting
    # results list itself was not retrieved, so the
    # candidate must keep the 原案可決 wording explicitly
    # unconfirmed instead of asserting it.
    budget = by_id["jp-local-232025-fiscal-2026-total-expenditure"]
    assert budget["fiscal_year"] == 2026
    assert budget["stage"] == "initial_budget"
    assert budget["metric"] == "total_expenditure"
    assert budget["metric_label"] == "一般会計当初予算総額"
    assert budget["amount_yen"] == 154850000000
    assert "第56号議案" in budget["note"]
    assert "令和8年3月23日" in budget["note"]
    assert "成立" in budget["note"]
    assert "未確認" in budget["note"]

    # The FY2024 settlement totals are published at yen
    # precision in the city's official settlement
    # overview (summary table and account-level table
    # agree), so the yen figures below are the exact
    # published totals. Their difference must equal the
    # published balance of 9,256,197,154 yen, and the
    # real balance after carryover funding is
    # 6,459,331,285 yen.
    revenue = by_id["jp-local-232025-fiscal-2024-total-revenue"]
    assert revenue["fiscal_year"] == 2024
    assert revenue["stage"] == "settlement"
    assert revenue["metric"] == "total_revenue"
    assert revenue["amount_yen"] == 157798763028
    expenditure = by_id["jp-local-232025-fiscal-2024-total-expenditure"]
    assert expenditure["fiscal_year"] == 2024
    assert expenditure["stage"] == "settlement"
    assert expenditure["metric"] == "total_expenditure"
    assert expenditure["amount_yen"] == 148542565874
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 9256197154

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
    # route (bill No. 56, voted on 2026-03-23) while
    # keeping the unconfirmed voting-result wording
    # explicit.
    budget_packet = next(
        pkt
        for pkt in packets
        if pkt["subject_id"] == "jp-local-232025-fiscal-2026-total-expenditure"
    )
    assert "第56号議案" in budget_packet["claims"][0]["statement"]
    assert "成立" in budget_packet["claims"][0]["statement"]
    assert "未確認" in budget_packet["claims"][0]["statement"]

    # The FY2024 settlement certification bill
    # (認定第1号) was CERTIFIED (認定) on 2025-09-30 in
    # the September 2025 regular session per the
    # council's official voting-results list. The
    # candidate must record the certification itself.
    revenue_packet = next(
        pkt
        for pkt in packets
        if pkt["subject_id"] == "jp-local-232025-fiscal-2024-total-revenue"
    )
    assert "認定第1号" in revenue_packet["claims"][0]["statement"]
    assert "認定された" in revenue_packet["claims"][0]["statement"]
    assert "令和7年9月30日" in revenue_packet["claims"][0]["statement"]
    assert "認定第1号" in revenue["note"]
    assert "認定第1号" in expenditure["note"]

    plan_review = package["plan_review"]
    assert plan_review["review_status"] == "pending_record_review"
    decisions = {rec["id"]: rec["decision"] for rec in plan_review["records"]}
    # FY2024 sits inside the Future Investment Plan's
    # first period (2021-2025), while the current
    # latter period starts in FY2026, so the plan
    # versions differ and no official total-level
    # mapping from settlement totals to the latter
    # plan's initiatives or packages exists; the
    # linkage stays not assessable.
    assert decisions["okazaki-fy2024-settlement-linkage"] == "not_assessable"
    assert all(
        decision in {"needs_review", "not_assessable"}
        for decision in decisions.values()
    )
    period = next(
        rec
        for rec in plan_review["records"]
        if rec["id"] == "okazaki-current-plan-period"
    )
    assert period["value"] == "2026年度～2030年度"

    # The transition from the Future Investment Plan's
    # first period to its latter period is recorded
    # only as a version chronology record, never by
    # retroactively mapping the latter plan's
    # initiatives onto earlier results.
    transition = next(
        rec for rec in plan_review["records"] if rec["id"] == "okazaki-plan-transition"
    )
    assert transition["evidence_role"] == "plan_transition"
    assert "後期" in transition["statement"]

    # The current plan is the latter plan of the
    # Seventh Okazaki City Comprehensive Plan:
    # Comprehensive Policy Guidelines (ten-year
    # guidelines looking thirty years ahead, target
    # year 2050), the Future Investment Plan, and
    # individual plans. Its field structure is ten
    # fields and 54 main initiatives, exactly as
    # published in the official plan document, plus
    # the four cross-field Future Investment Packages.
    current_plan = package["policy_structure"]["current_plan"]
    assert current_plan["title"] == "第7次岡崎市総合計画 後期計画"
    assert current_plan["vision"] == "一歩先の暮らしで三河を拓く 中枢・中核都市おかざき"
    assert current_plan["start_fiscal_year"] == 2026
    assert current_plan["end_fiscal_year"] == 2030
    fields = current_plan["policy_fields"]
    assert [field["name_ja"] for field in fields] == [
        "暮らしを支える都市づくり（都市インフラ）",
        "暮らしを守る強靭な都市づくり（防災・強靭化）",
        "持続可能な循環型の都市づくり（環境・農山村）",
        "多様な主体が協働・活躍できる社会づくり（地域社会）",
        "健康で生きがいをもって活躍できる社会づくり（保健・医療・福祉）",
        "女性や子どもがいきいきと輝ける社会づくり（子育て・男女共同参画）",
        "誰もが学び活躍できる社会づくり（教育・文化）",
        "商業と観光が成長産業となる地域経済づくり（商業・観光）",
        "ものづくりが柱でありつづける地域経済づくり（工業）",
        "スマートでスリムな行政運営の確立（行政・パートナーシップ）",
    ]
    assert [field["measures"] for field in fields] == [
        [
            "経済成長を呼び込む土地利用の誘導・推進",
            "将来を見据えた持続可能な都市政策の推進",
            "安全・円滑・快適な交通環境の整備",
            "居心地が良く歩きたくなるまちなかの形成",
            "小さな拠点の形成による地域づくりの推進",
            "ライフステージに応じた居住環境の創出",
            "魅力あふれる都市空間の形成",
        ],
        [
            "被災者ニーズに応じた支援体制の構築",
            "多様な主体と連携した受援体制の構築・強化",
            "防災意識の浸透（自助の推進）",
            "自主防災活動組織の担い手育成・活動体制の支援（共助の推進）",
            "氾濫・浸水被害を防ぐための対策の推進",
            "地震に強い都市づくりの推進",
        ],
        [
            "市内経済の成長と連動した環境保全の推進",
            "脱炭素化に向けた再エネの導入・省エネ化の促進",
            "農林業経営の効率化・高収益化の推進",
            "森林や農地の維持確保",
        ],
        [
            "町内会支援機能の充実",
            "地域活動への参画の支援",
            "市民活動への支援",
            "多様性と包摂性による多文化共生の地域づくり",
        ],
        [
            "地域福祉の推進",
            "障がい者が自分らしく生きるための支援",
            "高齢者を支える地域包括ケアの推進",
            "急増する高齢者に対応する医療・福祉の提供体制の構築",
            "健康寿命の延伸と健康格差の縮小に向けた取組推進",
        ],
        [
            "安心して楽しみながら子育てができる環境づくり",
            "保育・幼児教育の質・量の確保",
            "放課後の居場所づくり",
            "公立保育園民営化による民間活力の導入",
            "誰もが働きやすい社会環境づくり",
        ],
        [
            "こども一人ひとりを大切にした教育の推進",
            "多様な教育的ニーズへの対応",
            "社会課題に柔軟に対応した学び環境の実現",
            "スポーツを通じた地域づくりの推進",
            "豊かな文化の維持継承",
            "スポーツや文化を通じた地域経済の活性化",
        ],
        [
            "魅力あふれる商業・サービス業の活性化",
            "広域観光交流拠点を中心としたまちづくり",
            "イベントとの連携による地域経済の活性化",
            "魅力的な観光コンテンツによる観光振興",
            "中小企業・小規模事業者の魅力向上支援",
            "事業活動を支える柔軟な働き方や潜在労働力の活躍推進",
        ],
        [
            "工業集積の促進",
            "スタートアップの促進と新たなビジネスモデルの創出支援",
            "中小企業・小規模事業者の振興",
            "成長分野へのチャレンジ支援",
        ],
        [
            "柔軟で機動的な行政システムの構築",
            "DXの推進による行政サービスの最適化",
            "技術革新を意識した地域社会のDXの促進",
            "持続可能な公共施設の最適化",
            "もっと岡崎を好きになる魅力発信",
            "シェアリングの推進による新価値の創造",
            "規制緩和や産官学連携による地域活性化",
        ],
    ]
    assert sum(len(field["measures"]) for field in fields) == 54
    strategy = current_plan["strategy_layer"]
    assert strategy["title"] == "未来投資パッケージ"
    assert [item["name_ja"] for item in strategy["strategies"]] == [
        "未来のまちパッケージ",
        "未来のひとパッケージ",
        "未来のしごとパッケージ",
        "未来のパートナーシップパッケージ",
    ]


def test_okazaki_promotion_is_reflected_in_canonical_queue():
    queue = read(QUEUE)
    item = next(
        row for row in queue["execution_queue"] if row["official_code"] == "232025"
    )
    assert item["status"] == "reviewed_complete"
    assert item["completion_path"] == "data/catalog/okazaki_phase15_completion.json"
    assert queue["summary"]["reviewed_complete_count"] == 56
    assert queue["summary"]["pending_record_review_count"] == 11
    assert queue["summary"]["next_official_code"] == "372013"


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
