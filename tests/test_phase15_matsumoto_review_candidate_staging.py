"""Safety tests for Matsumoto Phase 15 non-public review candidate."""

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "data/candidates/matsumoto-city/review_candidate.json"
INVENTORY = ROOT / "data/indexed/matsumoto-city/source_inventory.json"
SCHEMA = ROOT / "schemas/phase15_review_candidate.schema.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"
WEB_ROOT = ROOT / "apps/web"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_matsumoto_candidate_validates_and_is_not_published():
    candidate = read(CANDIDATE)
    schema = read(SCHEMA)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = list(validator.iter_errors(candidate))
    assert errors == []
    assert candidate["candidate_id"] == "matsumoto-phase15-review-candidate"
    assert candidate["phase"] == 15
    assert candidate["official_code"] == "202029"
    assert candidate["name_ja"] == "松本市"
    assert (
        candidate["source_inventory_path"]
        == "data/indexed/matsumoto-city/source_inventory.json"
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


def test_matsumoto_sources_match_existing_official_inventory():
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
        source["official_url"].startswith("https://www.city.matsumoto.nagano.jp/")
        for source in sources
    )
    assert all(
        source["verification_status"] == "primary_source_live_verified_2026-11-16"
        for source in sources
    )
    assert all(bool(source["evidence_location"]) for source in sources)
    assert all(bool(source["use_boundary"]) for source in sources)


def test_matsumoto_prepared_candidate_records_only_verified_fiscal_values():
    candidate = read(CANDIDATE)
    package = candidate["candidate_package"]

    fiscal_records = package["fiscal_records"]
    assert len(fiscal_records) == 3
    by_id = {rec["id"]: rec for rec in fiscal_records}
    assert set(by_id) == {
        "jp-local-202029-fiscal-2026-total-expenditure",
        "jp-local-202029-fiscal-2024-total-revenue",
        "jp-local-202029-fiscal-2024-total-expenditure",
    }
    assert all(rec["municipality_id"] == "jp-local-202029" for rec in fiscal_records)
    assert all(rec["account_type"] == "general" for rec in fiscal_records)
    assert all(rec["value_status"] == "available" for rec in fiscal_records)
    assert all(rec["review_status"] == "needs_review" for rec in fiscal_records)
    assert all(rec["confidence"] == "medium" for rec in fiscal_records)

    # The FY2026 initial budget was submitted to the
    # February 2026 regular council session as bill No. 43
    # (議案第43号) and voted on at the plenary of
    # 2026-03-16 (the agenda of minutes No. 5 lists the
    # committee-chair reports and votes for bills No. 1 to
    # No. 71). The official June 2026 supplementary-budget
    # overview carries the initial amount of 114,980,000
    # thousand yen as the already-enacted base amount, so
    # the budget must not be labelled as a draft proposal
    # (予算案). The amount is the exact sen-yen total of
    # the official initial-budget overview (114,980,000
    # thousand yen, up 4,620,000 thousand yen / 4.2% from
    # FY2025's 110,360,000 thousand yen). The minutes body
    # wording 原案可決 was not directly confirmed, so it
    # must not be asserted anywhere in the budget record.
    budget = by_id["jp-local-202029-fiscal-2026-total-expenditure"]
    assert budget["fiscal_year"] == 2026
    assert budget["stage"] == "initial_budget"
    assert budget["metric"] == "total_expenditure"
    assert budget["metric_label"] == "一般会計当初予算総額"
    assert budget["amount_yen"] == 114980000000
    assert "議案第43号" in budget["note"]
    assert "令和8年3月16日" in budget["note"]
    assert "成立" in budget["note"]
    # The 原案可決 wording itself was not directly
    # confirmed in the minutes body, so the note must
    # carry that disclaimer instead of asserting it.
    assert "直接確認できていない" in budget["note"]

    # The FY2024 settlement totals are published at yen
    # precision in the appendix table of the audit
    # commission's official review opinion (松監事第24号,
    # 2025-08-20), so the yen figures below are the exact
    # published totals. Their difference must equal the
    # published balance (歳入歳出差引額・形式収支) of
    # 2,924,821,106 yen, and the real balance after the
    # carryover source of 421,570,818 yen must equal the
    # published real balance of 2,503,250,288 yen.
    revenue = by_id["jp-local-202029-fiscal-2024-total-revenue"]
    assert revenue["fiscal_year"] == 2024
    assert revenue["stage"] == "settlement"
    assert revenue["metric"] == "total_revenue"
    assert revenue["amount_yen"] == 116331387915
    expenditure = by_id["jp-local-202029-fiscal-2024-total-expenditure"]
    assert expenditure["fiscal_year"] == 2024
    assert expenditure["stage"] == "settlement"
    assert expenditure["metric"] == "total_expenditure"
    assert expenditure["amount_yen"] == 113406566809
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 2924821106
    assert 2924821106 - 421570818 == 2503250288

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
    # route (bill No. 43, voted on 2026-03-16) without
    # asserting the unconfirmed 原案可決 wording.
    budget_packet = next(
        pkt
        for pkt in packets
        if pkt["subject_id"] == "jp-local-202029-fiscal-2026-total-expenditure"
    )
    assert "議案第43号" in budget_packet["claims"][0]["statement"]
    assert "成立" in budget_packet["claims"][0]["statement"]
    assert "原案可決" not in budget_packet["claims"][0]["statement"]

    # The FY2024 settlement was certified as bill No. 18
    # of the September 2025 regular session
    # (議案第18号, covering the general account and the
    # nine special accounts) on 2025-11-04 at the third
    # extraordinary session of 2025, after continued
    # review by the settlement special committee during
    # the recess, per the council's official minutes.
    revenue_packet = next(
        pkt
        for pkt in packets
        if pkt["subject_id"] == "jp-local-202029-fiscal-2024-total-revenue"
    )
    assert "議案第18号" in revenue_packet["claims"][0]["statement"]
    assert "令和7年11月4日" in revenue_packet["claims"][0]["statement"]
    assert "認定" in revenue_packet["claims"][0]["statement"]
    assert "議案第18号" in revenue["note"]
    assert "議案第18号" in expenditure["note"]

    plan_review = package["plan_review"]
    assert plan_review["review_status"] == "pending_record_review"
    decisions = {rec["id"]: rec["decision"] for rec in plan_review["records"]}
    # FY2024 belongs to the eleventh basic plan period
    # (FY2021 to FY2025) under Basic Concept 2030, while
    # the twelfth basic plan only starts in FY2026, and
    # settlement totals are section-level aggregates with
    # no official mapping to individual measures or
    # indicators, so the linkage stays not assessable.
    assert decisions["matsumoto-fy2024-settlement-linkage"] == "not_assessable"
    assert all(
        decision in {"needs_review", "not_assessable"}
        for decision in decisions.values()
    )
    period = next(
        rec
        for rec in plan_review["records"]
        if rec["id"] == "matsumoto-current-plan-period"
    )
    assert period["value"] == "2026年度～2030年度"

    # The eleventh-to-twelfth plan transition is recorded
    # only as a version chronology record, never merged
    # back into the eleventh plan's framework.
    transition = next(
        rec for rec in plan_review["records"] if rec["id"] == "matsumoto-plan-transition"
    )
    assert transition["evidence_role"] == "plan_transition"
    assert "第12次基本計画" in transition["statement"]

    # The current plan is Basic Concept 2030 with the
    # twelfth basic plan (FY2026 to FY2030) as its latter
    # plan. Its policy structure is seven fields holding
    # 47 basic measures, exactly as published in the
    # plan's official field volumes.
    current_plan = package["policy_structure"]["current_plan"]
    assert current_plan["title"] == "松本市基本構想2030・第12次基本計画"
    assert current_plan["start_fiscal_year"] == 2026
    assert current_plan["end_fiscal_year"] == 2030
    assert current_plan["vision"] == "豊かさと幸せに 挑み続ける 三ガク都"
    goals = current_plan["basic_goals"]
    assert [goal["name_ja"] for goal in goals] == [
        "こども・若者・教育",
        "健康・医療・福祉",
        "住民自治・共生",
        "環境・エネルギー",
        "都市基盤・危機管理",
        "経済・産業",
        "文化・観光",
    ]
    assert [goal["measures"] for goal in goals] == [
        [
            "結婚・出産・子育て支援の充実",
            "質の高い保育・幼児教育の実現",
            "個性と多様性を尊重する学校教育の推進",
            "子どもの権利保障と子ども福祉の推進",
            "若者が活躍できる環境づくり",
            "子ども・若者による居場所づくりの支援",
            "地域でともに学び合う生涯学習の実現",
        ],
        [
            "生涯を通じた健康づくりの推進",
            "全ての世代にわたる食育の推進",
            "保健衛生・生活衛生の充実",
            "地域医療・救急医療の体制強化と維持",
            "個々に寄り添う障がい者福祉の充実",
            "一人ひとりが輝ける高齢者福祉の充実",
            "暮らしを守る生活支援の充実",
        ],
        [
            "住民自治の活性化支援",
            "地域福祉活動の推進",
            "地域防災・防犯の推進",
            "若者・子育て世代の移住・定住促進",
            "多様性と人権・平和の尊重",
            "ジェンダー平等社会の実現",
            "国際化・多文化共生の推進",
        ],
        [
            "温室効果ガスの排出量削減の推進",
            "資源循環推進による環境負荷軽減",
            "自然・生活環境の保全",
            "森林の保全・再生・活用",
        ],
        [
            "松本城を核としたまちづくり",
            "中心市街地の再活性",
            "地域交通ネットワークの拡充",
            "自転車活用先進都市の実現",
            "交通需要に即した道路整備",
            "広域交通網の整備推進",
            "バランスの取れた土地利用",
            "水と緑を活かした魅力あるまちづくり",
            "上下水道の基盤強化",
            "危機管理体制の強化",
            "防災・減災対策の推進",
            "将来にわたる公共インフラの整備",
        ],
        [
            "新商都松本の創造",
            "ものづくり産業の再創造",
            "多様な働き方と雇用環境の充実",
            "持続可能な農業の推進",
            "地域特性を活かした新産業の創出",
        ],
        [
            "豊かさを育む文化芸術の推進",
            "歴史・文化遺産の継承と活用",
            "スポーツを楽しむ環境の充実",
            "変化する時代に対応した観光戦略の推進",
            "世界に冠たる山岳リゾートの実現",
        ],
    ]
    assert sum(len(goal["measures"]) for goal in goals) == 47


def test_matsumoto_promotion_is_reflected_in_canonical_queue():
    queue = read(QUEUE)
    item = next(
        row for row in queue["execution_queue"] if row["official_code"] == "202029"
    )
    assert item["status"] == "reviewed_complete"
    assert item["completion_path"] == "data/catalog/matsumoto_phase15_completion.json"
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
