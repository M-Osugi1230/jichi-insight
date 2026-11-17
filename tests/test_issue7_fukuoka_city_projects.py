from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

PROJECTS_PATH = "data/reviewed/fukuoka-city/projects.json"
KPIS_PATH = "data/reviewed/fukuoka-city/project_kpis.json"
PACKETS_PATH = "data/reviewed/fukuoka-city/project_evidence_packets.json"
SOURCES_PATH = "data/catalog/fukuoka_city_project_sources.json"
SELECTION_PATH = "data/catalog/fukuoka_city_priority_project_selection.json"

UNIVERSAL = "jp-local-401307-project-2025-universal-city-promotion"
CHILD = "jp-local-401307-project-2025-child-rights-voice-support"
POINTS = "jp-local-401307-project-2025-fukuoka-points"
FOREST = "jp-local-401307-project-2025-rich-forest-development"
FOOD = "jp-local-401307-project-2025-food-universal-hospitality"
DOWNTOWN = "jp-local-401307-project-2025-downtown-redevelopment-promotion"
SME = "jp-local-401307-project-2025-sme-management-base-strengthening"
PORT = "jp-local-401307-project-2025-port-sales-hakata"
CHILDREARING = "jp-local-401307-project-2025-community-childrearing-support"
WATERFRONT = "jp-local-401307-project-2025-waterfront-redevelopment"

PILOT_IDS = [UNIVERSAL, CHILD, POINTS]
SCALE_IDS = [FOREST, FOOD, DOWNTOWN, SME, PORT, CHILDREARING, WATERFRONT]


def load_json(path: str) -> Any:
    with (ROOT / path).open(encoding="utf-8") as handle:
        return json.load(handle)


def assert_valid(schema_path: str, instance: Any) -> None:
    validator = Draft202012Validator(
        load_json(schema_path),
        format_checker=FormatChecker(),
    )
    errors = list(validator.iter_errors(instance))
    assert errors == [], "; ".join(error.message for error in errors)


def projects_by_id() -> dict[str, Any]:
    return {record["id"]: record for record in load_json(PROJECTS_PATH)}


def test_fukuoka_city_projects_match_schemas() -> None:
    assert_valid("schemas/source_catalog.schema.json", load_json(SOURCES_PATH))
    for record in load_json(PROJECTS_PATH):
        assert_valid("schemas/project.schema.json", record)
    for record in load_json(KPIS_PATH):
        assert_valid("schemas/kpi.schema.json", record)
    for packet in load_json(PACKETS_PATH):
        assert_valid("schemas/evidence_packet.schema.json", packet)


def test_selection_rule_and_population() -> None:
    selection = load_json(SELECTION_PATH)
    # The population is defined as an intersection because Fukuoka City has
    # no single official priority-project list and no current project-level
    # administrative evaluation system.
    assert "重要施策に掲載された事業 ∩ 施策評価の対象事業" in selection["population"]["description"]
    assert selection["population"]["fiscal_year"] == 2025
    assert selection["population"]["policy_count"] == 30
    assert selection["scope"] == "expanded"
    assert selection["expansion_rule"]["added_count"] == 7
    assert selection["expansion_rule"]["total_count"] == 10
    selections = selection["selections"]
    assert len(selections) == 10
    assert [item["project_id"] for item in selections] == PILOT_IDS + SCALE_IDS
    assert [item["pillar"] for item in selections[:3]] == [
        "目標1 一人ひとりが心豊かに暮らし、自分らしく輝いている",
        "目標2 すべての子ども・若者が夢を描きながら健やかに成長している",
        "目標3 地域の人々がつながり、支え合い、安全・安心に暮らしている",
    ]
    assert [item["pillar"] for item in selections[3:]] == [
        "目標4 人と自然が共生し、身近に潤いと安らぎが感じられる",
        "目標5 磨かれた魅力に人々が集い、活力に満ちている",
        "目標6 都市機能が充実し、多くの人や企業から選ばれている",
        "目標7 チャレンジ精神と新たな価値の創造により、地域経済が活性化している",
        "目標8 アジアのモデル都市として世界とつながり、国際的な存在感がある",
        "目標2 すべての子ども・若者が夢を描きながら健やかに成長している",
        "目標6 都市機能が充実し、多くの人や企業から選ばれている",
    ]
    projects = projects_by_id()
    for item in selections:
        record = projects[item["project_id"]]
        assert record["series_id"] == item["series_id"]
        assert record["official_title"] == item["official_title"]
        assert record["fiscal_year"] == 2025
        assert record["review_status"] == "reviewed"
    skipped = selection["skipped"]
    # The first-listed project of policy 3-1 could not be connected to a
    # project-level budget figure, so the rule moved to the next project and
    # the skip is on record.
    assert skipped[0]["official_title"] == "共創の地域づくり"
    assert "束ね" in skipped[0]["reason"]
    # In the scale-up, the first-listed projects of policies 4-1, 5-1 and
    # 8-1 (and the runner-up of 8-1) also failed the intersection condition;
    # every skip stays on record with its reason.
    assert [item["official_title"] for item in skipped[1:]] == [
        "生物多様性の確保",
        "海辺を生かした観光振興",
        "博多港の物流・人流機能の強化",
        "博多港におけるカーボンニュートラルポートの形成",
        "人権教育・啓発",
        "性的マイノリティへの支援",
        "バリアフリーのまちづくり",
        "インクルーシブな子ども広場の整備・運営",
        "障がい者スポーツセンターの機能強化",
        "男女共同参画の推進",
        "女性活躍の推進",
        "困難を抱える女性への支援",
        "外国人の生活環境づくり",
        "医療の国際化",
    ]
    skipped_titles = {item["official_title"] for item in skipped}
    assert skipped_titles.isdisjoint(
        {record["official_title"] for record in projects.values()}
    )


def test_project_budget_records_and_stage_honesty() -> None:
    projects = projects_by_id()
    expected = {
        UNIVERSAL: 7_893_000,
        CHILD: 30_809_000,
        POINTS: 60_718_000,
        FOREST: 442_644_000,
        FOOD: 22_643_000,
        DOWNTOWN: 55_007_000,
        SME: 171_456_950_000,
        PORT: 150_154_000,
        CHILDREARING: 36_591_233_000,
        WATERFRONT: 22_000_000,
    }
    assert set(projects) == set(expected)
    for project_id, initial in expected.items():
        records = projects[project_id]["budget_records"]
        # Settlement amounts are not registered: the per-project settlement
        # briefing documents could not be obtained, and the gap is stated in
        # the evidence packets instead of being filled from other documents.
        assert [item["kind"] for item in records] == ["initial_budget"]
        record = records[0]
        assert record["amount_yen"] == initial
        assert record["fiscal_year"] == 2025
        # The amounts come from initial-budget-proposal documents; the note
        # must keep that stage explicit and never claim enacted figures.
        assert "当初予算案" in record["note"]
        assert "成立値とは扱わない" in record["note"]


def test_kpi_baseline_target_actual_are_separated() -> None:
    kpis = {record["id"]: record for record in load_json(KPIS_PATH)}
    assert len(kpis) == 10
    for record in kpis.values():
        project = projects_by_id()[record["project_id"]]
        assert record["review_status"] == "reviewed"
        assert record["causality_note"]
        embedded = {item["name"]: item for item in project["kpis"]}
        summary = embedded[record["name"]]
        assert summary["baseline"] == record["baseline"]["value"]
        assert summary["target"] == record["target"]["value"]
        assert summary["assessment"] == record["assessment"]

    awareness = kpis[f"{UNIVERSAL}-kpi-universal-design-awareness"]
    assert awareness["baseline"]["value"] == 62.7
    assert awareness["target"]["value"] == 70
    assert awareness["actuals"][0]["value"] == 66.2
    assert awareness["actuals"][0]["period"] == "2025年度"
    assert awareness["assessment"] == "in_progress"

    voice = kpis[f"{CHILD}-kpi-children-voice-not-valued-share"]
    assert voice["direction"] == "decrease"
    # The baseline is 5.3% (FY2023) and the latest value is 9.7%: the
    # indicator worsened, matching the city's official D rating. The two
    # values must never be swapped.
    assert voice["baseline"]["value"] == 5.3
    assert voice["baseline"]["period"] == "2023年度"
    assert voice["target"]["value"] == "3％未満"
    assert voice["actuals"][0]["value"] == 9.7
    assert voice["assessment"] == "not_achieved"

    districts = kpis[f"{POINTS}-kpi-point-adoption-districts"]
    assert districts["baseline"]["value"] == 9
    assert districts["target"]["value"] == 100
    assert districts["actuals"][0]["value"] == 64
    assert districts["assessment"] == "in_progress"


def test_scale_up_kpis() -> None:
    kpis = {record["id"]: record for record in load_json(KPIS_PATH)}

    forest = kpis[f"{FOREST}-kpi-broadleaf-replanting-area"]
    # The progress text in the sheet ties 17ha to FY2024 and 41ha to FY2025.
    assert forest["baseline"] == {
        "period": "2024年度",
        "value": 17,
        "status": "available",
        "source_ids": ["fukuoka-city-plan-evaluation-goal4-fy2025"],
    }
    assert forest["target"]["value"] == 112
    assert forest["actuals"][0]["value"] == 41
    assert forest["actuals"][0]["period"] == "2025年度"
    assert forest["assessment"] == "in_progress"

    food = kpis[f"{FOOD}-kpi-foreign-visitor-food-diversity-satisfaction"]
    assert food["baseline"]["value"] == 58.7
    assert food["target"]["value"] == 80
    assert food["actuals"][0]["value"] == 66.6
    assert food["assessment"] == "in_progress"

    tenjin = kpis[f"{DOWNTOWN}-kpi-tenjin-bigbang-completed-buildings"]
    assert tenjin["baseline"]["value"] == 58
    assert tenjin["baseline"]["period"] == "2023年度"
    assert tenjin["target"]["value"] == 70
    assert tenjin["target"]["period"] == "2026年度"
    # The FY2025 actual already exceeds the FY2026 target; the city's
    # published figures are recorded as they are.
    assert tenjin["actuals"][0]["value"] == 85
    assert tenjin["assessment"] == "in_progress"

    hakata = kpis[f"{DOWNTOWN}-kpi-hakata-connected-completed-buildings"]
    assert hakata["baseline"]["value"] == 22
    assert hakata["target"]["value"] == 30
    assert hakata["actuals"][0]["value"] == 30
    assert hakata["assessment"] == "in_progress"

    sme = kpis[f"{SME}-kpi-corporate-taxpayer-count"]
    assert sme["baseline"]["value"] == 65499
    assert sme["baseline"]["period"] == "2023年度"
    assert sme["target"]["value"] == 73000
    # The latest published value is the FY2024 figure, not a FY2025 one.
    assert sme["actuals"][0]["value"] == 67768
    assert sme["actuals"][0]["period"] == "2024年度"
    assert sme["assessment"] == "in_progress"

    burden = kpis[f"{CHILDREARING}-kpi-youth-child-mental-burden-share"]
    assert burden["direction"] == "decrease"
    # Lower is better: 44.8% (FY2023) improved to 27.1%, and the city's
    # target is stated qualitatively as "decrease". The baseline and the
    # latest value must never be swapped.
    assert burden["baseline"]["value"] == 44.8
    assert burden["baseline"]["period"] == "2023年度"
    assert burden["target"]["value"] == "減少"
    assert burden["actuals"][0]["value"] == 27.1
    assert burden["assessment"] == "in_progress"

    continued = kpis[f"{WATERFRONT}-kpi-continued-implementation"]
    # The city designates "continued implementation" as this project's
    # indicator and publishes no numeric baseline, target or actual; the
    # record keeps them explicitly unavailable instead of inventing values.
    assert continued["baseline"]["status"] == "not_applicable"
    assert continued["baseline"]["value"] is None
    assert continued["target"]["status"] == "not_applicable"
    assert continued["target"]["value"] is None
    assert continued["actuals"][0]["status"] == "not_published"
    assert continued["actuals"][0]["value"] is None
    assert continued["assessment"] == "not_assessable"
    assert continued["direction"] == "not_applicable"


def test_port_sales_project_has_no_kpi_and_says_so() -> None:
    projects = projects_by_id()
    # The policy evaluation sheet publishes no indicator for this project;
    # the project record keeps the KPI list empty rather than promoting a
    # progress figure from the narrative into a KPI.
    assert projects[PORT]["kpis"] == []
    kpis = load_json(KPIS_PATH)
    assert all(record["project_id"] != PORT for record in kpis)
    packets = {packet["subject_id"]: packet for packet in load_json(PACKETS_PATH)}
    kpi_claims = [
        claim for claim in packets[PORT]["claims"] if claim["field"] == "kpis"
    ]
    assert len(kpi_claims) == 1
    assert "掲載がない" in kpi_claims[0]["statement"]


def test_official_evaluation_is_the_citys_policy_level_not_ours() -> None:
    projects = projects_by_id()
    expected_ratings = {
        UNIVERSAL: "概ね順調",
        CHILD: "概ね順調",
        POINTS: "概ね順調",
        FOREST: "概ね順調",
        FOOD: "順調",
        DOWNTOWN: "概ね順調",
        SME: "概ね順調",
        PORT: "概ね順調",
        CHILDREARING: "概ね順調",
        WATERFRONT: "概ね順調",
    }
    for project_id, rating in expected_ratings.items():
        evaluation = projects[project_id]["official_evaluation"]
        assert evaluation["rating"] == rating
        # Fukuoka City evaluates policies, not individual projects; the note
        # must say so and must not present the rating as our own judgement.
        assert "施策単位" in evaluation["note"]
        assert "Jichi Insight独自の評価ではない" in evaluation["note"]
        # Promises are Issue #8: no fabricated links.
        assert projects[project_id]["related_promise_ids"] == []


def test_every_project_has_an_evidence_packet_and_known_sources() -> None:
    source_ids = {record["id"] for record in load_json(SOURCES_PATH)["records"]}
    packets = {packet["subject_id"]: packet for packet in load_json(PACKETS_PATH)}
    assert set(packets) == set(projects_by_id())
    for packet in packets.values():
        assert packet["subject_type"] == "project"
        assert packet["review_status"] == "reviewed"
        for claim in packet["claims"]:
            assert set(claim["source_ids"]) <= source_ids
        # Unregistered settlement amounts and contract/assembly/audit links
        # stay explicit open questions.
        assert any("決算額は未登録" in question for question in packet["open_questions"])
        assert any("未登録" in question for question in packet["open_questions"])
    for record in projects_by_id().values():
        assert set(record["sources"]) <= source_ids
    for record in load_json(KPIS_PATH):
        assert set(record["sources"]) <= source_ids


def test_budget_source_availability_is_honest() -> None:
    sources = {record["id"]: record for record in load_json(SOURCES_PATH)["records"]}
    # The General Affairs Bureau briefing was submitted to the assembly
    # committee, but its official URL now returns 404; the record must not
    # claim it is still published.
    briefing = sources["fukuoka-city-budget-briefing-general-affairs-fy2025"]
    assert briefing["availability"] == "not_found"
    assert "Internet Archive" in briefing["notes"]
    # The same applies to the Economy and Housing bureau briefings used in
    # the scale-up.
    for source_id in (
        "fukuoka-city-budget-briefing-economy-fy2025",
        "fukuoka-city-budget-briefing-housing-fy2025",
    ):
        record = sources[source_id]
        assert record["availability"] == "not_found"
        assert "Internet Archive" in record["notes"]
        assert "当初予算案" in record["notes"]
    book = sources["fukuoka-city-budget-proposal-book1-fy2025"]
    assert book["availability"] == "published"
    assert "当初予算案" in book["notes"]
    # The evaluation sheets for goals 4-8 are still published.
    for goal in range(4, 9):
        record = sources[f"fukuoka-city-plan-evaluation-goal{goal}-fy2025"]
        assert record["availability"] == "published"
