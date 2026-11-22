from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
MID = "jp-local-261009"
SOURCES_PATH = ROOT / "data/catalog/kyoto_city_project_sources.json"
SELECTION_PATH = ROOT / "data/catalog/kyoto_city_priority_project_selection.json"
PROJECTS_PATH = ROOT / "data/reviewed/kyoto-city/projects.json"
KPIS_PATH = ROOT / "data/reviewed/kyoto-city/project_kpis.json"
PACKETS_PATH = ROOT / "data/reviewed/kyoto-city/project_evidence_packets.json"

PILLARS = ["うるおい", "活性化", "すこやか", "まちづくり"]

EXPECTED_IDS = [
    "jp-local-261009-project-2025-environment",
    "jp-local-261009-project-2025-human-rights-gender-equality",
    "jp-local-261009-project-2025-civic-life-community",
    "jp-local-261009-project-2025-civic-life-safety",
    "jp-local-261009-project-2025-culture",
    "jp-local-261009-project-2025-sports",
    "jp-local-261009-project-2025-industry-commerce",
    "jp-local-261009-project-2025-tourism",
    "jp-local-261009-project-2025-agriculture-forestry",
    "jp-local-261009-project-2025-universities",
]

EXPECTED_TITLES = [
    "環境",
    "人権・男女共同参画",
    "市民生活とコミュニティ",
    "市民生活の安全",
    "文化",
    "スポーツ",
    "産業・商業",
    "観光",
    "農林業",
    "大学",
]

# The first ten policies of the Kyo Plan 2025 in the plan's listing
# order: policies 1-6 sit under the pillar "うるおい" and policies
# 7-10 under "活性化".
EXPECTED_PILLARS = ["うるおい"] * 6 + ["活性化"] * 4

EXPECTED_DEPARTMENTS = [
    "環境政策局",
    "文化市民局",
    "文化市民局",
    "文化市民局",
    "文化市民局",
    "文化市民局",
    "産業観光局",
    "産業観光局",
    "産業観光局",
    "総合企画局",
]

EXPECTED_POLICY_AREAS = [
    "environment",
    "governance",
    "governance",
    "safety",
    "culture",
    "sports",
    "industry",
    "tourism",
    "agriculture",
    "education",
]

# FY2026 policy evaluation (published 2026-09-17): the official
# comprehensive ratings of policies 1-10. The published tally over
# all 27 policies is A2 / B19 / C6 / D0 / E0.
EXPECTED_RATINGS = {
    "jp-local-261009-project-2025-environment": "B：目的がかなり達成されている",
    "jp-local-261009-project-2025-human-rights-gender-equality": "B：目的がかなり達成されている",
    "jp-local-261009-project-2025-civic-life-community": "C：目的がそこそこ達成されている",
    "jp-local-261009-project-2025-civic-life-safety": "C：目的がそこそこ達成されている",
    "jp-local-261009-project-2025-culture": "B：目的がかなり達成されている",
    "jp-local-261009-project-2025-sports": "C：目的がそこそこ達成されている",
    "jp-local-261009-project-2025-industry-commerce": "A：目的が十分に達成されている",
    "jp-local-261009-project-2025-tourism": "B：目的がかなり達成されている",
    "jp-local-261009-project-2025-agriculture-forestry": "B：目的がかなり達成されている",
    "jp-local-261009-project-2025-universities": "B：目的がかなり達成されている",
}

# Policy-level objective indicators per policy (21 in total).
EXPECTED_KPI_COUNTS = [2, 4, 1, 2, 2, 3, 2, 2, 2, 1]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validator(name: str) -> Draft202012Validator:
    schema = load(ROOT / "schemas" / name)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def test_kyoto_city_project_sources_are_schema_valid() -> None:
    catalog = load(SOURCES_PATH)
    validator("source_catalog.schema.json").validate(catalog)
    ids = [record["id"] for record in catalog["records"]]
    assert len(ids) == len(set(ids)) == 8
    assert all(record["municipality_key"] == "kyoto-city" for record in catalog["records"])


def test_selection_rule_is_plan_listing_order() -> None:
    selection = load(SELECTION_PATH)
    assert selection["municipality_id"] == MID
    assert selection["issue"] == 935
    assert selection["population"]["fiscal_year"] == 2025
    # The population is the policy framework of the Kyo Plan 2025:
    # 27 policies under four pillars, with 114 measures below them.
    assert selection["population"]["policy_count"] == 27
    assert selection["population"]["measure_count"] == 114
    assert selection["population"]["group_count"] == 4
    assert selection["selection_rule"]["pillars"] == PILLARS
    assert "金額の大小では選ばない" in selection["selection_rule"]["description"]
    selected = selection["selections"]
    assert [item["project_id"] for item in selected] == EXPECTED_IDS
    assert [item["official_title"] for item in selected] == EXPECTED_TITLES
    assert [item["policy"] for item in selected] == EXPECTED_PILLARS
    assert [item["pillar"] for item in selected] == EXPECTED_PILLARS
    assert [item["department"] for item in selected] == EXPECTED_DEPARTMENTS
    assert selection["expansion_rule"]["total_count"] == 10


def test_framework_transition_is_documented_without_mapping() -> None:
    # Kyoto City adopted the Kyoto Basic Concept (2026-2050) in
    # December 2025 and runs the New Kyoto Strategy as its action
    # plan, but the FY2026 policy evaluation was still conducted on
    # the Kyo Plan 2025 framework and no official correspondence
    # table between the frameworks is published. The registration
    # therefore stays on the Kyo Plan 2025 framework and never maps
    # policies onto the new framework.
    selection = load(SELECTION_PATH)
    description = selection["population"]["description"]
    assert "京都基本構想" in description
    assert "新京都戦略" in description
    assert "新旧の対応付けは行っていない" in description
    for packet in load(PACKETS_PATH):
        claim = next(c for c in packet["claims"] if c["field"] == "registration_unit")
        assert "本登録の単位は" in claim["statement"]
        assert "「政策」とした" in claim["statement"]
        assert "対応付けは行っていない" in claim["statement"]


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
        assert record["responsible_department"] == item["department"]
        assert record["municipality_id"] == MID
        assert record["fiscal_year"] == 2025
        assert record["review_status"] == "reviewed"
        # Stage 3 (Kyoto cluster) will examine promise links; at
        # this stage nothing is linked.
        assert record["related_promise_ids"] == []
    areas = [projects[pid]["policy_area"] for pid in EXPECTED_IDS]
    assert areas == EXPECTED_POLICY_AREAS


def test_budget_amounts_are_unregistered_with_reasons() -> None:
    # The policy evaluation publications carry no per-policy
    # amounts, and the settlement publications are organised on
    # other frameworks (the New Kyoto Strategy's six policies in
    # the settlement overview, bureaus in the settlement report),
    # so no policy-level amount is registered instead of relabelling
    # figures from another framework.
    for record in load(PROJECTS_PATH):
        assert len(record["budget_records"]) == 1
        budget = record["budget_records"][0]
        assert budget["kind"] == "settlement"
        assert budget["fiscal_year"] == 2025
        assert budget["amount_yen"] is None
        assert "未登録とした" in budget["note"]
        assert "0では補完しない" in budget["note"]


def test_official_evaluations_are_the_city_ratings() -> None:
    for record in load(PROJECTS_PATH):
        evaluation = record["official_evaluation"]
        assert evaluation is not None
        assert evaluation["rating"] == EXPECTED_RATINGS[record["id"]]
        assert "Jichi Insight独自の評価ではない" in evaluation["note"]
        assert "客観指標評価" in evaluation["note"]
        assert "市民生活実感評価" in evaluation["note"]
    for packet in load(PACKETS_PATH):
        claim = next(c for c in packet["claims"] if c["field"] == "official_evaluation")
        assert "総合評価" in claim["statement"]
        assert "A2・B19・C6・D0・E0" in claim["statement"]


def test_kpis_follow_the_published_indicator_grades() -> None:
    projects = load(PROJECTS_PATH)
    counts = [len(record["kpis"]) for record in projects]
    assert counts == EXPECTED_KPI_COUNTS
    assert sum(counts) == 21
    by_name = {kpi["name"]: kpi for record in projects for kpi in record["kpis"]}
    # Policy 1 indicators, FY2026 evaluation grades c and a.
    ghg = by_name["温室効果ガス排出量削減率"]
    assert (ghg["baseline"], ghg["target"], ghg["actual"]) == (27.6, 32.2, 27.7)
    assert ghg["assessment"] == "partially_achieved"
    waste = by_name["ごみ焼却量の削減量"]
    assert (waste["baseline"], waste["target"], waste["actual"]) == (5.1, 3.2, 5.3)
    assert waste["assessment"] == "achieved"
    # Policy 4's consumer indicator was graded e by the city.
    consumer = by_name["消費生活相談件数に占める助言・あっせん解決率"]
    assert (consumer["baseline"], consumer["target"], consumer["actual"]) == (
        99.09,
        99.62,
        98.76,
    )
    assert consumer["assessment"] == "not_achieved"
    # Policy 3's only policy-level indicator is survey-based: no
    # FY2025 actual was published and the FY2026 evaluation left it
    # ungraded, so the actual stays null (never zero-filled) and
    # the assessment is not_assessable; the latest published actual
    # (FY2024, 59.7%) is kept as the baseline.
    community = by_name["地域コミュニティが活性化していると回答した自治会・町内会の割合"]
    assert community["baseline"] == 59.7
    assert community["target"] == 70
    assert community["actual"] is None
    assert community["assessment"] == "not_assessable"


def test_detailed_kpis_are_schema_valid_and_linked() -> None:
    kpis = load(KPIS_PATH)
    assert len(kpis) == 21
    project_ids = {record["id"] for record in load(PROJECTS_PATH)}
    for kpi in kpis:
        validator("kpi.schema.json").validate(kpi)
        assert kpi["project_id"] in project_ids
        assert kpi["id"].startswith(kpi["project_id"] + "-kpi-")
        assert "換算したものである" in kpi["definition"]
    community = next(
        kpi for kpi in kpis if kpi["name"].startswith("地域コミュニティが活性化している")
    )
    assert community["actuals"][0]["status"] == "not_published"
    assert community["actuals"][0]["value"] is None
    assert community["baseline"]["value"] == 59.7


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
            "budget_records.settlement",
            "kpis",
        }
