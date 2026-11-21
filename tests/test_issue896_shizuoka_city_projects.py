from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
MID = "jp-local-221007"
SOURCES_PATH = ROOT / "data/catalog/shizuoka_city_project_sources.json"
SELECTION_PATH = ROOT / "data/catalog/shizuoka_city_priority_project_selection.json"
PROJECTS_PATH = ROOT / "data/reviewed/shizuoka-city/projects.json"
KPIS_PATH = ROOT / "data/reviewed/shizuoka-city/project_kpis.json"
PACKETS_PATH = ROOT / "data/reviewed/shizuoka-city/project_evidence_packets.json"

F1 = "共生・福祉・健康"
F2 = "防災・消防・防犯"
F3 = "こども・子育て"
F4 = "教育・人づくり"
F5 = "経済・産業"
F6 = "観光・スポーツ・文化"
F7 = "都市・社会基盤"
F8 = "環境・森林"
F9 = "行政経営"
PILLARS = [F1, F2, F3, F4, F5, F6, F7, F8, F9]

EXPECTED_IDS = [
    "jp-local-221007-project-2026-community-association-support",
    "jp-local-221007-project-2026-disaster-resilient-infrastructure",
    "jp-local-221007-project-2026-work-childcare-balance",
    "jp-local-221007-project-2026-personalized-learning-environment",
    "jp-local-221007-project-2026-corporate-site-development",
    "jp-local-221007-project-2026-tourism-consumption",
    "jp-local-221007-project-2026-underused-land-utilization",
    "jp-local-221007-project-2026-decarbonization-behavior-change",
    "jp-local-221007-project-2026-public-facility-optimization",
    "jp-local-221007-project-2026-citizen-activity-support",
]

EXPECTED_TITLES = [
    "地域コミュニティの中核である自治会・町内会における誰もが参加しやすい組織づくりを下支えし、住民同士のつながりを強化します",
    "被害の最小化と早期の復旧・復興が可能となる社会基盤を整備します",
    "子育て当事者の負担を軽減し、仕事と子育てが両立できる環境を整備します",
    "こどもが主体となり、一人ひとりに合った学習を進め学びに向かえるような学習環境を整えます",
    "農地として活用されない未利用・低利用農地の集約等により、企業用地を創出します",
    "静岡市ならではの魅力を堪能できる食や体験などを充実させることで観光消費を増加させます",
    "地域のニーズに応じた土地利用の再設計を進めることで、低利用地を効率的・効果的に活用します",
    "住宅・建築物の省エネ化や再エネ設備の導入支援のほか、企業等と連携した新たなサービスの提供等により社会全体の行動変容を促進します",
    "公共施設の配置を見直し、社会的需要に対する公共施設の供給量を適正化します",
    "地域課題の解決に取り組む市民活動の輪を広げ、地域の力で共に支え合う社会づくりを下支えします",
]

# Round-robin over the nine fields in the implementation plan's
# listing order; each field contributes its first policy's first
# measure, and the second round takes field 1's second measure.
EXPECTED_PILLARS = [F1, F2, F3, F4, F5, F6, F7, F8, F9, F1]

EXPECTED_PARENTS = [
    "（地域活動・市民活動）地域社会のつながりを深め、市民が支え合うまちにします",
    "（防災・減災）<事前防災>社会基盤が整備された自然災害に強いまちにします",
    "（子育て）子育てする誰もが、安心して子育てでき、こどもが健やかに成長できるまちにします",
    "（学びの充実）こどもたちが、それぞれに最も適した学びに向かい、多様な仲間と関わりながら探究を深めることができるまちにします",
    "（企業誘致・留置）企業誘致・留置が促進され、地域の経済的活力が高まり、新たな働く場を得ることができるまちにします",
    "（観光）市内の観光消費が拡大することによって所得の増加や魅力ある雇用が生み出されているまちにします",
    "（まちづくり）多様な交流と投資を呼び込む活力ある「まち」を形成し、その成果が市民生活の豊かさや未来への希望につながるまちにします",
    "（脱炭素社会）エネルギー消費を抑えつつ再生可能エネルギーを導入・活用し、暮らしの快適さと地域経済の活性化を両立できるまちにします",
    "（社会共有資産）社会共有資産が活用され、市民の経済的利益や利便性が向上するまちにします",
    "（地域活動・市民活動）地域社会のつながりを深め、市民が支え合うまちにします",
]

EXPECTED_POLICY_AREAS = [
    "governance",
    "disaster_prevention",
    "childcare",
    "education",
    "industry",
    "tourism",
    "infrastructure",
    "environment",
    "governance",
    "governance",
]

EXPECTED_KPI_COUNTS = [3, 4, 4, 4, 1, 2, 1, 1, 1, 2]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validator(name: str) -> Draft202012Validator:
    schema = load(ROOT / "schemas" / name)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def test_shizuoka_city_project_sources_are_schema_valid() -> None:
    catalog = load(SOURCES_PATH)
    validator("source_catalog.schema.json").validate(catalog)
    ids = [record["id"] for record in catalog["records"]]
    assert len(ids) == len(set(ids)) == 2
    assert all(
        record["municipality_key"] == "shizuoka-city" for record in catalog["records"]
    )


def test_selection_rule_is_listing_order_by_field() -> None:
    selection = load(SELECTION_PATH)
    assert selection["municipality_id"] == MID
    assert selection["issue"] == 896
    assert selection["population"]["fiscal_year"] == 2026
    # The population is the 5th comprehensive plan's implementation
    # plan framework: 9 fields, 45 policies and 101 measures, as
    # printed in the plan.
    assert selection["population"]["field_count"] == 9
    assert selection["population"]["policy_count"] == 45
    assert selection["population"]["measure_count"] == 101
    assert selection["selection_rule"]["pillars"] == PILLARS
    assert "金額の大小では選ばない" in selection["selection_rule"]["description"]
    selected = selection["selections"]
    assert [item["project_id"] for item in selected] == EXPECTED_IDS
    assert [item["official_title"] for item in selected] == EXPECTED_TITLES
    assert [item["policy"] for item in selected] == EXPECTED_PARENTS
    assert [item["pillar"] for item in selected] == EXPECTED_PILLARS
    assert selection["expansion_rule"]["total_count"] == 10


def test_registration_unit_is_the_measure() -> None:
    # The registration unit is the measure (施策): the implementation
    # plan sets outcome KPIs per measure and states that evaluation
    # and verification are carried out per measure. Amounts exist
    # only per initiative (five-year totals), and initiatives marked
    # with a star belong to several measures, so neither the
    # initiative nor the policy is the unit that carries the KPIs and
    # the evaluation framework.
    selection = load(SELECTION_PATH)
    assert "登録単位は施策とした" in selection["population"]["description"]
    for packet in load(PACKETS_PATH):
        claim = next(c for c in packet["claims"] if c["field"] == "registration_unit")
        assert "施策を登録単位とした" in claim["statement"]
        assert "KPIと評価・検証の単位が施策である" in claim["statement"]


def test_selected_projects_match_records() -> None:
    projects = {record["id"]: record for record in load(PROJECTS_PATH)}
    selection = load(SELECTION_PATH)
    assert len(projects) == 10
    for item in selection["selections"]:
        record = projects[item["project_id"]]
        validator("project.schema.json").validate(record)
        assert record["series_id"] == item["series_id"]
        assert record["official_title"] == item["official_title"]
        assert record["parent_policy"] == item["policy"]
        # The plan prints responsible sections per initiative, not
        # per measure, so the department stays unregistered.
        assert record["responsible_department"] is None
        assert record["municipality_id"] == MID
        assert record["fiscal_year"] == 2026
        assert record["review_status"] == "reviewed"
        # Stage 3 of the Shizuoka cluster has not run yet, so no
        # promise links are registered at this stage.
        assert record["related_promise_ids"] == []
    areas = [projects[pid]["policy_area"] for pid in EXPECTED_IDS]
    assert areas == EXPECTED_POLICY_AREAS


def test_budget_amounts_are_explicitly_unregistered() -> None:
    # Shizuoka publishes no per-measure amounts: the implementation
    # plan prints amounts only per initiative, as five-year totals
    # (2026-2030) of investment expenses with soft initiatives shown
    # as a dash, so measure amounts stay null instead of 0 and the
    # initiative totals are never summed into a measure amount.
    for record in load(PROJECTS_PATH):
        assert len(record["budget_records"]) == 1
        budget = record["budget_records"][0]
        assert budget["kind"] == "initial_budget"
        assert budget["fiscal_year"] == 2026
        assert budget["amount_yen"] is None
        assert "未登録とした" in budget["note"]
        assert "0では補完しない" in budget["note"]
        assert "取組単位" in budget["note"]


def test_official_evaluation_is_not_yet_published() -> None:
    # FY2026 is the plan's first year; the plan's evaluation and
    # verification framework exists, but no results are published
    # yet, so the evaluation stays null (the Kobe pattern).
    for record in load(PROJECTS_PATH):
        assert record["official_evaluation"] is None
    for packet in load(PACKETS_PATH):
        claim = next(c for c in packet["claims"] if c["field"] == "official_evaluation")
        assert "公表されていない" in claim["statement"]


def test_kpis_are_the_measures_outcome_indicators() -> None:
    # Outcome KPIs are set per measure in the implementation plan;
    # each registered KPI carries the printed current value and the
    # 2030 target, with no actuals published yet.
    kpis = load(KPIS_PATH)
    assert len(kpis) == 23
    projects = {record["id"]: record for record in load(PROJECTS_PATH)}
    counts = [len(projects[pid]["kpis"]) for pid in EXPECTED_IDS]
    assert counts == EXPECTED_KPI_COUNTS
    by_project: dict[str, list] = {}
    for kpi in kpis:
        validator("kpi.schema.json").validate(kpi)
        by_project.setdefault(kpi["project_id"], []).append(kpi)
        assert kpi["assessment"] == "not_assessable"
        assert kpi["baseline"]["status"] == "available"
        assert kpi["target"]["status"] == "available"
        assert kpi["actuals"][0]["status"] == "not_published"
    for pid, embedded in ((p["id"], p["kpis"]) for p in projects.values()):
        detailed = by_project[pid]
        assert [k["name"] for k in detailed] == [k["name"] for k in embedded]
        for det, emb in zip(detailed, embedded, strict=True):
            assert det["baseline"]["value"] == emb["baseline"]
            assert det["target"]["value"] == emb["target"]
            assert emb["actual"] is None
            assert emb["assessment"] == "not_assessable"


def test_evidence_packets_are_schema_valid() -> None:
    packets = load(PACKETS_PATH)
    assert len(packets) == 10
    project_ids = {record["id"] for record in load(PROJECTS_PATH)}
    for packet in packets:
        validator("evidence_packet.schema.json").validate(packet)
        assert packet["subject_type"] == "project"
        assert packet["subject_id"] in project_ids
        assert packet["id"] == f"evidence-{packet['subject_id']}"
