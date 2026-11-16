"""Safety tests for Tsu Phase 15 non-public review candidate."""

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "data/candidates/tsu-city/review_candidate.json"
INVENTORY = ROOT / "data/indexed/tsu-city/source_inventory.json"
SCHEMA = ROOT / "schemas/phase15_review_candidate.schema.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"
WEB_ROOT = ROOT / "apps/web"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_tsu_candidate_validates_and_is_not_published():
    candidate = read(CANDIDATE)
    schema = read(SCHEMA)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = list(validator.iter_errors(candidate))
    assert errors == []
    assert candidate["candidate_id"] == "tsu-phase15-review-candidate"
    assert candidate["phase"] == 15
    assert candidate["official_code"] == "242012"
    assert candidate["name_ja"] == "津市"
    assert (
        candidate["source_inventory_path"]
        == "data/indexed/tsu-city/source_inventory.json"
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


def test_tsu_sources_match_existing_official_inventory():
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
        source["official_url"].startswith("https://www.info.city.tsu.mie.jp/")
        for source in sources
    )
    assert all(
        source["verification_status"] == "primary_source_live_verified_2026-11-16"
        for source in sources
    )
    assert all(bool(source["evidence_location"]) for source in sources)
    assert all(bool(source["use_boundary"]) for source in sources)


def test_tsu_prepared_candidate_records_only_verified_fiscal_values():
    candidate = read(CANDIDATE)
    package = candidate["candidate_package"]

    fiscal_records = package["fiscal_records"]
    assert len(fiscal_records) == 3
    by_id = {rec["id"]: rec for rec in fiscal_records}
    assert set(by_id) == {
        "jp-local-242012-fiscal-2026-total-expenditure",
        "jp-local-242012-fiscal-2024-total-revenue",
        "jp-local-242012-fiscal-2024-total-expenditure",
    }
    assert all(rec["municipality_id"] == "jp-local-242012" for rec in fiscal_records)
    assert all(rec["account_type"] == "general" for rec in fiscal_records)
    assert all(rec["value_status"] == "available" for rec in fiscal_records)
    assert all(rec["review_status"] == "needs_review" for rec in fiscal_records)
    assert all(rec["confidence"] == "medium" for rec in fiscal_records)

    # The FY2026 initial budget was submitted to the
    # February-March 2026 council session as bill
    # No. 39 (議案第39号) on 2026-02-27 and, per the
    # council's official voting-result table for the
    # first regular session of 2026 and the plenary
    # minutes of 2026-03-26, was passed as proposed
    # (原案可決) by majority vote on 2026-03-26, so the
    # budget must not be labelled as a draft proposal
    # (予算案). The amount is the exact sen-yen total
    # published by the city (124,187,000 thousand yen),
    # confirmed in both the official budget book
    # (bill No. 39, Article 1) and the official budget
    # overview (account summary table).
    budget = by_id["jp-local-242012-fiscal-2026-total-expenditure"]
    assert budget["fiscal_year"] == 2026
    assert budget["stage"] == "initial_budget"
    assert budget["metric"] == "total_expenditure"
    assert budget["metric_label"] == "一般会計当初予算総額"
    assert budget["amount_yen"] == 124187000000
    assert "議案第39号" in budget["note"]
    assert "令和8年3月26日" in budget["note"]
    assert "成立" in budget["note"]
    assert "原案可決" in budget["note"]

    # The FY2024 settlement totals are published at yen
    # precision in the city's official settlement book
    # (general-account statement), so the yen figures
    # below are the exact published totals. Their
    # difference must equal the balance of 466,767,600
    # yen recorded in the official statement on the
    # actual balance (実質収支に関する調書).
    revenue = by_id["jp-local-242012-fiscal-2024-total-revenue"]
    assert revenue["fiscal_year"] == 2024
    assert revenue["stage"] == "settlement"
    assert revenue["metric"] == "total_revenue"
    assert revenue["amount_yen"] == 123307646176
    expenditure = by_id["jp-local-242012-fiscal-2024-total-expenditure"]
    assert expenditure["fiscal_year"] == 2024
    assert expenditure["stage"] == "settlement"
    assert expenditure["metric"] == "total_expenditure"
    assert expenditure["amount_yen"] == 122840878576
    assert revenue["amount_yen"] - expenditure["amount_yen"] == 466767600

    # The actual balance (実質収支) is published at yen
    # precision in the settlement appendix's statement
    # on the actual balance (175,738,909 yen, after
    # deducting 291,028,691 yen of resources to be
    # carried forward from the 466,767,600 yen
    # balance), so the candidate records it at yen
    # precision exactly as published.
    assert "175,738,909円" in revenue["note"]
    assert "291,028,691円" in revenue["note"]

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
    # route (bill No. 39, passed as proposed on
    # 2026-03-26).
    budget_packet = next(
        pkt
        for pkt in packets
        if pkt["subject_id"] == "jp-local-242012-fiscal-2026-total-expenditure"
    )
    assert "議案第39号" in budget_packet["claims"][0]["statement"]
    assert "成立" in budget_packet["claims"][0]["statement"]
    assert "原案可決" in budget_packet["claims"][0]["statement"]
    assert "令和8年3月26日" in budget_packet["claims"][0]["statement"]

    # The FY2024 settlement certification bill is
    # 認定第1号. It was submitted to the third regular
    # session of 2025, referred to the Settlement
    # Special Committee, and the council's official
    # voting-result table for that session directly
    # records the result as certified (認定) on
    # 2025-09-25, so the candidate must record the
    # certification as a confirmed fact with that
    # date, and must never record it as rejected
    # (不認定).
    revenue_packet = next(
        pkt
        for pkt in packets
        if pkt["subject_id"] == "jp-local-242012-fiscal-2024-total-revenue"
    )
    assert "認定第1号" in revenue_packet["claims"][0]["statement"]
    assert "認定された" in revenue_packet["claims"][0]["statement"]
    assert "令和7年9月25日" in revenue_packet["claims"][0]["statement"]
    assert "不認定" not in revenue_packet["claims"][0]["statement"]
    expenditure_packet = next(
        pkt
        for pkt in packets
        if pkt["subject_id"] == "jp-local-242012-fiscal-2024-total-expenditure"
    )
    assert "認定第1号" in expenditure_packet["claims"][0]["statement"]
    assert "認定された" in expenditure_packet["claims"][0]["statement"]
    assert "不認定" not in expenditure_packet["claims"][0]["statement"]
    assert "認定第1号" in revenue["note"]
    assert "認定第1号" in expenditure["note"]
    assert "令和7年9月25日" in revenue["note"]

    plan_review = package["plan_review"]
    assert plan_review["review_status"] == "pending_record_review"
    decisions = {rec["id"]: rec["decision"] for rec in plan_review["records"]}
    # FY2024 is a settlement inside the Second Basic
    # Plan period (FY2018-FY2027), so the plan version
    # is the same, but no official total-level mapping
    # from settlement totals to the plan's goals,
    # basic policies or policies exists. The linkage
    # therefore stays not assessable.
    assert decisions["tsu-fy2024-settlement-linkage"] == "not_assessable"
    assert all(
        decision in {"needs_review", "not_assessable"}
        for decision in decisions.values()
    )
    period = next(
        rec for rec in plan_review["records"] if rec["id"] == "tsu-current-plan-period"
    )
    assert period["value"] == "2018年度～2027年度"

    # The transition from the preceding plans to the
    # current plan, and the formulation of the next
    # plan, are recorded only as version chronology
    # records, never by retroactively mapping another
    # plan's framework onto prior results.
    transition = next(
        rec for rec in plan_review["records"] if rec["id"] == "tsu-plan-transition"
    )
    assert transition["evidence_role"] == "plan_transition"
    assert "前期基本計画" in transition["statement"]
    assert "次期津市総合計画" in transition["statement"]

    # The current operative plan layer is the Second
    # Basic Plan of the Tsu City Comprehensive Plan
    # (FY2018-FY2027), under the Basic Concept, which
    # has no fixed period and whose vision is 笑顔が
    # あふれ幸せに暮らせる県都 津市. Its structure is
    # six goals plus the cross-cutting block, 19 basic
    # policies and 53 policies, exactly as published
    # in the official plan book's structure chart.
    current_plan = package["policy_structure"]["current_plan"]
    assert current_plan["title"] == "津市総合計画 第2次基本計画"
    assert (
        current_plan["vision"]
        == "笑顔があふれ幸せに暮らせる県都 津市 ～夢や希望、明るい未来が広がるまちへ～"
    )
    assert current_plan["start_fiscal_year"] == 2018
    assert current_plan["end_fiscal_year"] == 2027
    fields = current_plan["policy_fields"]
    assert [field["name_ja"] for field in fields] == [
        "目標1-基本政策1 安心して子どもを生み育てられる環境の充実",
        "目標1-基本政策2 子どもたちの生きる力を育み成長を支える環境の充実",
        "目標2-基本政策1 社会の変化に対応した福祉の充実",
        "目標2-基本政策2 健康づくりの推進と医療体制の充実",
        "目標3-基本政策1 いざという時の備えの強化",
        "目標3-基本政策2 防犯・交通安全対策の強化",
        "目標4-基本政策1 環境にやさしい社会の形成",
        "目標4-基本政策2 持続可能な都市基盤の整備",
        "目標4-基本政策3 快適に暮らせる都市空間の形成",
        "目標5-基本政策1 生涯を通じた学びの推進",
        "目標5-基本政策2 スポーツや文化の輪が広がる社会の形成",
        "目標5-基本政策3 つながり広がるコミュニティの醸成",
        "目標5-基本政策4 誰もが尊重され暮らしやすい社会の実現",
        "目標6-基本政策1 働ける・働きたくなる環境の整備",
        "目標6-基本政策2 地域に根付く商工業の振興",
        "目標6-基本政策3 食の安定と暮らしを支える農林水産業の振興",
        "目標6-基本政策4 交流人口の拡大",
        "将来像の実現に向けて-1 市民の思いや願いに応える市役所",
        "将来像の実現に向けて-2 高みをめざす行政経営",
    ]
    assert [field["measures"] for field in fields] == [
        ["出会い・結婚・出産しやすい環境づくり", "子育て支援の充実"],
        ["幼児教育・保育の充実", "学校教育の充実", "健やかな育ちへの支援"],
        [
            "地域包括ケアシステムの確立",
            "地域福祉の充実",
            "高齢者福祉の充実",
            "障がい者（児）福祉の充実",
            "低所得者福祉の充実",
        ],
        ["健康づくりの推進", "地域医療・救急医療体制の充実", "公的医療保険の安定運営"],
        ["防災・減災施策の強化", "災害に強いまちづくりの推進", "消防力の強化"],
        ["防犯対策と消費者保護の強化", "交通安全対策の強化"],
        ["環境を守り継承する社会の形成", "循環型社会形成の推進"],
        [
            "安全な水の安定供給",
            "生活排水対策等の推進",
            "生活道路の整備",
            "居住環境の整備",
            "港湾・海岸堤防の整備",
        ],
        [
            "良好な景観の形成",
            "緑化の推進と公園緑地の整備",
            "都市機能の整備",
            "道路ネットワークの整備",
            "公共交通の充実",
        ],
        ["生涯学習の推進", "高等教育機関との連携・充実"],
        ["スポーツの振興", "文化の振興"],
        [
            "市民活動の促進",
            "地域コミュニティの活性化",
            "国際・国内交流と多文化共生の推進",
        ],
        [
            "人権・平和施策の推進",
            "ユニバーサルデザインのまちづくりの推進",
            "男女共同参画の推進",
        ],
        ["勤労者福祉の充実", "雇用の創出・拡大"],
        ["工業の振興", "商業の振興"],
        ["農業の振興", "林業の振興", "水産業の振興"],
        ["観光の振興", "シティプロモーションの推進"],
        ["積極的な対話と連携によるまちづくり", "地域の立場に立ち続ける地域連携"],
        ["効率的で効果的な行政経営", "健全な財政運営"],
    ]
    assert sum(len(field["measures"]) for field in fields) == 53


def test_tsu_promotion_is_reflected_in_canonical_queue():
    queue = read(QUEUE)
    item = next(
        row for row in queue["execution_queue"] if row["official_code"] == "242012"
    )
    assert item["status"] == "reviewed_complete"
    assert item["completion_path"] == "data/catalog/tsu_phase15_completion.json"
    assert queue["summary"]["reviewed_complete_count"] == 60
    assert queue["summary"]["pending_record_review_count"] == 7
    assert queue["summary"]["next_official_code"] == "412015"


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
