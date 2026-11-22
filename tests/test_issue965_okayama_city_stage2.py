from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
MID = "jp-local-331007"
SOURCES_PATH = ROOT / "data/catalog/okayama_city_project_sources.json"
SELECTION_PATH = ROOT / "data/catalog/okayama_city_priority_project_selection.json"
PROJECTS_PATH = ROOT / "data/reviewed/okayama-city/projects.json"
KPIS_PATH = ROOT / "data/reviewed/okayama-city/project_kpis.json"
PACKETS_PATH = ROOT / "data/reviewed/okayama-city/project_evidence_packets.json"

DIR1 = "基本方向1 こども・子育て・教育"
DIR2 = "基本方向2 協働・多様性"
DIR3 = "基本方向3 健康・福祉"

PILLARS = [
    "基本方向1 こども・子育て・教育",
    "基本方向2 協働・多様性",
    "基本方向3 健康・福祉",
    "基本方向4 産業・交流",
    "基本方向5 歴史・文化・スポーツ",
    "基本方向6 安全・安心",
    "基本方向7 都市・環境",
    "基本方向8 都市経営",
]

EXPECTED_IDS = [
    "jp-local-331007-project-2026-children-youth",
    "jp-local-331007-project-2026-child-rearing",
    "jp-local-331007-project-2026-school-education",
    "jp-local-331007-project-2026-educational-environment",
    "jp-local-331007-project-2026-lifelong-learning",
    "jp-local-331007-project-2026-collaboration-esd",
    "jp-local-331007-project-2026-international-exchange",
    "jp-local-331007-project-2026-human-rights-gender-equality",
    "jp-local-331007-project-2026-health",
    "jp-local-331007-project-2026-welfare",
]

EXPECTED_TITLES = [
    "こども・若者の権利の尊重と、成長・自立の支援（こども・若者）",
    "安心してこどもを生み育てることができる環境づくり（子育て）",
    "知・徳・体の調和のとれた自立に向かって成長する子どもの育成（学校教育）",
    "教育を支える基盤整備及び教育DXの推進（教育環境）",
    "共に学び、つながる社会教育の推進と、生涯にわたる学びの充実（生涯学習）",
    "多様な主体による協働のまちづくり（協働・ESD）",
    "未来を拓く国際交流と多文化共生のまちづくり（国際）",
    "多様性を認め平和を願う人権尊重社会の実現（人権・男女共同参画）",
    "生涯にわたり健康でいきいきと生活できるまちづくり（健康）",
    "ともに生き、ともに支え合う地域共生社会の推進（福祉）",
]

EXPECTED_PARENTS = [DIR1] * 5 + [DIR2] * 3 + [DIR3] * 2

EXPECTED_POLICY_AREAS = [
    "childcare",
    "childcare",
    "education",
    "education",
    "education",
    "governance",
    "governance",
    "governance",
    "health",
    "welfare",
]

# Plan outcome indicators per policy (appendix list, plan pp.196-198);
# indicators published in two parts are registered per part.
EXPECTED_KPI_COUNTS = [5, 3, 10, 3, 4, 4, 2, 3, 4, 3]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validator(name: str) -> Draft202012Validator:
    schema = load(ROOT / "schemas" / name)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def test_okayama_city_project_sources_are_schema_valid() -> None:
    catalog = load(SOURCES_PATH)
    validator("source_catalog.schema.json").validate(catalog)
    ids = [record["id"] for record in catalog["records"]]
    assert len(ids) == len(set(ids)) == 8
    assert all(
        record["municipality_key"] == "okayama-city"
        for record in catalog["records"]
    )


def test_selection_rule_is_plan_listing_order() -> None:
    selection = load(SELECTION_PATH)
    assert selection["municipality_id"] == MID
    assert selection["issue"] == 965
    assert selection["population"]["fiscal_year"] == 2026
    # The population is the policy framework of the 7th Comprehensive
    # Plan's first midterm plan: 30 policies under eight basic
    # directions, with 99 measures below them.
    assert selection["population"]["policy_count"] == 30
    assert selection["population"]["measure_count"] == 99
    assert selection["population"]["group_count"] == 8
    assert selection["selection_rule"]["pillars"] == PILLARS
    assert "金額の大小では選ばない" in selection["selection_rule"]["description"]
    selected = selection["selections"]
    assert [item["project_id"] for item in selected] == EXPECTED_IDS
    assert [item["official_title"] for item in selected] == EXPECTED_TITLES
    assert [item["policy"] for item in selected] == EXPECTED_PARENTS
    assert [item["pillar"] for item in selected] == EXPECTED_PARENTS
    # The plan designates no single bureau per policy, so the
    # department stays unregistered instead of being inferred.
    assert [item["department"] for item in selected] == [None] * 10
    assert selection["expansion_rule"]["total_count"] == 10


def test_new_plan_is_registered_without_borrowing_old_results() -> None:
    # The 7th Comprehensive Plan was enacted on 2026-03-17 and its
    # first annual evaluation (for FY2026) is not yet published.
    # The registration therefore stays on the new plan's framework
    # with the evaluation left null, and never borrows the 6th
    # plan's evaluation results.
    selection = load(SELECTION_PATH)
    description = selection["population"]["description"]
    assert "第七次総合計画" in description
    assert "甲第71号議案" in description
    assert "旧・第六次総合計画の評価結果は流用していない" in description
    for packet in load(PACKETS_PATH):
        claim = next(
            c for c in packet["claims"] if c["field"] == "registration_unit"
        )
        assert "本登録の単位は" in claim["statement"]
        assert "「政策」とした" in claim["statement"]
        evaluation = next(
            c for c in packet["claims"] if c["field"] == "official_evaluation"
        )
        assert "未公表" in evaluation["statement"]
        assert "流用していない" in evaluation["statement"]


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
        assert record["responsible_department"] is None
        assert record["municipality_id"] == MID
        assert record["fiscal_year"] == 2026
        assert record["review_status"] == "reviewed"
        # Promise links were a stage-3 question: Issue #974 connected
        # nine of the mayor's 21 bulletin promises to the seven
        # policies whose subjects match them (inferred links, capped
        # at low confidence); the other three policies stay unlinked.
        expected_promise_links = {
            "jp-local-331007-project-2026-children-youth": [
                "jp-local-331007-executive-2025-10-09-promise-003"
            ],
            "jp-local-331007-project-2026-child-rearing": [
                "jp-local-331007-executive-2025-10-09-promise-001",
                "jp-local-331007-executive-2025-10-09-promise-002",
            ],
            "jp-local-331007-project-2026-school-education": [
                "jp-local-331007-executive-2025-10-09-promise-005",
                "jp-local-331007-executive-2025-10-09-promise-006",
            ],
            "jp-local-331007-project-2026-collaboration-esd": [
                "jp-local-331007-executive-2025-10-09-promise-007"
            ],
            "jp-local-331007-project-2026-human-rights-gender-equality": [
                "jp-local-331007-executive-2025-10-09-promise-004"
            ],
            "jp-local-331007-project-2026-health": [
                "jp-local-331007-executive-2025-10-09-promise-008"
            ],
            "jp-local-331007-project-2026-welfare": [
                "jp-local-331007-executive-2025-10-09-promise-009"
            ],
        }
        assert record["related_promise_ids"] == expected_promise_links.get(
            item["project_id"], []
        )
    areas = [projects[pid]["policy_area"] for pid in EXPECTED_IDS]
    assert areas == EXPECTED_POLICY_AREAS


def test_budget_amounts_are_unregistered_with_reasons() -> None:
    # Neither the plan nor the city's budget publications carry
    # per-policy amounts (the budget documents are aggregated by
    # account and category), so no policy-level amount is registered
    # instead of relabelling figures from another framework.
    for record in load(PROJECTS_PATH):
        assert len(record["budget_records"]) == 1
        budget = record["budget_records"][0]
        assert budget["kind"] == "initial_budget"
        assert budget["fiscal_year"] == 2026
        assert budget["amount_yen"] is None
        assert "未登録とした" in budget["note"]
        assert "0では補完しない" in budget["note"]


def test_official_evaluations_are_unregistered_until_first_cycle() -> None:
    for record in load(PROJECTS_PATH):
        assert record["official_evaluation"] is None
    for packet in load(PACKETS_PATH):
        claim = next(
            c for c in packet["claims"] if c["field"] == "official_evaluation"
        )
        assert "初回" in claim["statement"]
        assert "null" in claim["statement"]


def test_kpis_follow_the_plan_indicator_list() -> None:
    projects = load(PROJECTS_PATH)
    counts = [len(record["kpis"]) for record in projects]
    assert counts == EXPECTED_KPI_COUNTS
    assert sum(counts) == 41
    by_name = {kpi["name"]: kpi for record in projects for kpi in record["kpis"]}
    # Policy 1 foster-care rate is published in two parts.
    infants = by_name["里親委託率（乳幼児）"]
    assert (infants["baseline"], infants["target"], infants["actual"]) == (
        42.5,
        75,
        None,
    )
    assert infants["assessment"] == "not_assessable"
    # Policy 2 waiting children: 236 at baseline, targeted at zero
    # from FY2029 onward (a decreasing indicator).
    waiting = by_name["放課後児童クラブの待機児童数"]
    assert (waiting["baseline"], waiting["target"]) == (236, 0)
    # Policy 3 academic deviation scores carry a textual target.
    japanese = by_name["全国学力・学習状況調査の偏差値（小6国語）"]
    assert japanese["baseline"] == 50
    assert japanese["target"] == "全国平均レベル以上"
    # Policy 9 healthy life expectancy (male), baseline FY2022,
    # target FY2030 in the plan's Reiwa notation.
    health = by_name["健康寿命（男性）"]
    assert (health["baseline"], health["target"]) == (72.3, 73.7)


def test_detailed_kpis_are_schema_valid_and_linked() -> None:
    kpis = load(KPIS_PATH)
    assert len(kpis) == 41
    project_ids = {record["id"] for record in load(PROJECTS_PATH)}
    for kpi in kpis:
        validator("kpi.schema.json").validate(kpi)
        assert kpi["project_id"] in project_ids
        assert kpi["id"].startswith(kpi["project_id"] + "-kpi-")
        assert kpi["assessment"] == "not_assessable"
        assert kpi["actuals"][0]["status"] == "not_published"
        assert kpi["actuals"][0]["value"] is None
        assert "未公表のため未登録" in kpi["definition"]
    waiting = next(
        kpi for kpi in kpis if kpi["name"] == "放課後児童クラブの待機児童数"
    )
    assert waiting["direction"] == "decrease"
    assert waiting["baseline"]["value"] == 236
    assert waiting["baseline"]["period"] == "令和6年度"
    assert waiting["target"]["value"] == 0
    assert waiting["target"]["period"] == "令和9年度以降"
    consultation = next(
        kpi
        for kpi in kpis
        if kpi["name"] == "ESD・市民協働推進センター相談件数"
    )
    assert consultation["baseline"]["period"] == "令和2〜6年度の合計"
    assert consultation["target"]["period"] == "令和8〜12年度の合計"


def test_evidence_packets_are_schema_valid() -> None:
    packets = load(PACKETS_PATH)
    assert len(packets) == 10
    project_ids = {record["id"] for record in load(PROJECTS_PATH)}
    for packet in packets:
        validator("evidence_packet.schema.json").validate(packet)
        assert packet["subject_type"] == "project"
        assert packet["subject_id"] in project_ids
        assert packet["id"] == f"evidence-{packet['subject_id']}"
        fields = {claim["field"] for claim in packet["claims"]}
        assert fields == {
            "registration_unit",
            "official_title",
            "parent_policy",
            "purpose",
            "responsible_department",
            "official_evaluation",
            "budget_records.initial_budget",
            "kpis",
        }
