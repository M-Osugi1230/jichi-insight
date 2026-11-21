from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
MID = "jp-local-121002"
SOURCES_PATH = ROOT / "data/catalog/chiba_city_project_sources.json"
SELECTION_PATH = ROOT / "data/catalog/chiba_city_priority_project_selection.json"
PROJECTS_PATH = ROOT / "data/reviewed/chiba-city/projects.json"
KPIS_PATH = ROOT / "data/reviewed/chiba-city/project_kpis.json"
PACKETS_PATH = ROOT / "data/reviewed/chiba-city/project_evidence_packets.json"

PILLARS = [
    "分野1 環境・自然",
    "分野2 安全・安心",
    "分野3 健康・福祉",
    "分野4 子ども・教育",
    "分野5 地域社会",
    "分野6 文化芸術・スポーツ",
    "分野7 都市・交通",
    "分野8 地域経済",
]

EXPECTED_IDS = [
    "jp-local-121002-project-2026-decarbonization-environmental-conservation",
    "jp-local-121002-project-2026-disaster-resilient-infrastructure",
    "jp-local-121002-project-2026-healthy-living",
    "jp-local-121002-project-2026-childbearing-and-childrearing",
    "jp-local-121002-project-2026-diversity-and-participation",
    "jp-local-121002-project-2026-culture-and-arts",
    "jp-local-121002-project-2026-sustainable-attractive-city",
    "jp-local-121002-project-2026-local-industry",
    "jp-local-121002-project-2026-greenery-and-waterside",
    "jp-local-121002-project-2026-collaborative-disaster-preparedness",
]

EXPECTED_TITLES = [
    "脱炭素化などの地球環境保全を進め、持続可能な社会を創る",
    "災害に強いまちの基盤を整備する",
    "健やかに暮らせる社会を創る",
    "子どもを産み・育てやすい環境を創る",
    "誰もが個性を活かし活躍できる環境を創る",
    "文化芸術が生まれ、広がる環境を創る",
    "持続可能で魅力あるまちづくりを進める",
    "地域の産業を支え・育てる",
    "緑と水辺を身近に感じ、愛着の持てる環境を創る",
    "多様な主体の連携による防災力を高める",
]

# First policy of each of the eight fields, then the second policy of
# fields 1 and 2 (the listing-order cycle continues).
EXPECTED_PARENTS = PILLARS + [PILLARS[0], PILLARS[1]]

EXPECTED_POLICY_AREAS = [
    "environment",
    "disaster_prevention",
    "health",
    "childcare",
    "other",
    "culture",
    "infrastructure",
    "industry",
    "environment",
    "disaster_prevention",
]

# Reverse promise links added by Stage 3 (Issue #842): the mayor's
# bulletin promises connected to each policy by wording and content
# only (inferred, capped at low / inferred). Policies not listed here
# carry no links.
_TERM = "jp-local-121002-executive-2025-03-21"
EXPECTED_PROMISE_LINKS = {
    "jp-local-121002-project-2026-disaster-resilient-infrastructure": [
        f"{_TERM}-promise-018",
    ],
    "jp-local-121002-project-2026-healthy-living": [
        f"{_TERM}-promise-014",
        f"{_TERM}-promise-015",
    ],
    "jp-local-121002-project-2026-childbearing-and-childrearing": [
        f"{_TERM}-promise-002",
        f"{_TERM}-promise-003",
        f"{_TERM}-promise-008",
    ],
    "jp-local-121002-project-2026-diversity-and-participation": [
        f"{_TERM}-promise-016",
        f"{_TERM}-promise-025",
    ],
    "jp-local-121002-project-2026-culture-and-arts": [
        f"{_TERM}-promise-022",
        f"{_TERM}-promise-023",
        f"{_TERM}-promise-024",
    ],
    "jp-local-121002-project-2026-sustainable-attractive-city": [
        f"{_TERM}-promise-011",
        f"{_TERM}-promise-012",
    ],
    "jp-local-121002-project-2026-local-industry": [
        f"{_TERM}-promise-004",
    ],
    "jp-local-121002-project-2026-greenery-and-waterside": [
        f"{_TERM}-promise-010",
    ],
    "jp-local-121002-project-2026-collaborative-disaster-preparedness": [
        f"{_TERM}-promise-019",
        f"{_TERM}-promise-020",
    ],
}

# Primary-identity project counts per selected policy, aggregated from
# the already-reviewed project identity catalogs (measure codes X-Y-*).
EXPECTED_PROJECT_COUNTS = {
    "jp-local-121002-project-2026-decarbonization-environmental-conservation": 17,
    "jp-local-121002-project-2026-disaster-resilient-infrastructure": 12,
    "jp-local-121002-project-2026-healthy-living": 7,
    "jp-local-121002-project-2026-childbearing-and-childrearing": 17,
    "jp-local-121002-project-2026-diversity-and-participation": 4,
    "jp-local-121002-project-2026-culture-and-arts": 9,
    "jp-local-121002-project-2026-sustainable-attractive-city": 16,
    "jp-local-121002-project-2026-local-industry": 9,
    "jp-local-121002-project-2026-greenery-and-waterside": 13,
    "jp-local-121002-project-2026-collaborative-disaster-preparedness": 3,
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validator(name: str) -> Draft202012Validator:
    schema = load(ROOT / "schemas" / name)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def test_chiba_city_project_sources_are_schema_valid() -> None:
    catalog = load(SOURCES_PATH)
    validator("source_catalog.schema.json").validate(catalog)
    ids = [record["id"] for record in catalog["records"]]
    assert len(ids) == len(set(ids)) == 7
    assert all(record["municipality_key"] == "chiba-city" for record in catalog["records"])


def test_selection_rule_is_listing_order_by_field() -> None:
    selection = load(SELECTION_PATH)
    assert selection["municipality_id"] == MID
    assert selection["issue"] == 839
    assert selection["population"]["fiscal_year"] == 2026
    # The population is the 2nd Implementation Plan framework: 8 fields,
    # 23 policies, 67 measures and 189 unique projects, as printed in the
    # plan's policy-structure table and reviewed in the plan review.
    assert selection["population"]["field_count"] == 8
    assert selection["population"]["policy_count"] == 23
    assert selection["population"]["measure_count"] == 67
    assert selection["population"]["project_count"] == 189
    assert selection["selection_rule"]["pillars"] == PILLARS
    assert "金額の大小では選ばない" in selection["selection_rule"]["description"]
    selected = selection["selections"]
    assert [item["project_id"] for item in selected] == EXPECTED_IDS
    assert [item["official_title"] for item in selected] == EXPECTED_TITLES
    assert [item["policy"] for item in selected] == EXPECTED_PARENTS
    assert [item["pillar"] for item in selected] == EXPECTED_PARENTS
    assert selection["expansion_rule"]["total_count"] == 10


def test_registration_unit_is_the_policy() -> None:
    # The registration unit is the policy (政策): it is the unit the
    # city's policy evaluation rates (three steps, after the
    # implementation-plan period ends). Measures carry no official
    # evaluation, amount or indicator of their own, and the 189 projects
    # are already registered in the work-item layer, so they are not
    # duplicated here.
    selection = load(SELECTION_PATH)
    assert "登録単位は政策とした" in selection["population"]["description"]
    for packet in load(PACKETS_PATH):
        claim = next(c for c in packet["claims"] if c["field"] == "registration_unit")
        assert "公式評価が付く単位が政策である" in claim["statement"]
        assert "重複登録しない" in claim["statement"]


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
        # The plan documents print no department per policy (departments
        # appear only per project), so both stay explicitly null.
        assert record["responsible_department"] is None
        assert item["department"] is None
        assert record["municipality_id"] == MID
        assert record["fiscal_year"] == 2026
        assert record["review_status"] == "reviewed"
        # Stage 3 (Issue #842) connected the mayor's bulletin promises
        # to the policies by wording and content only; the reverse
        # links below are the full extent of those connections.
        assert record["related_promise_ids"] == EXPECTED_PROMISE_LINKS.get(
            record["id"], []
        )
    areas = [projects[pid]["policy_area"] for pid in EXPECTED_IDS]
    assert areas == EXPECTED_POLICY_AREAS
    # The purpose of each record states the verified primary-identity
    # project count of its policy.
    for pid, count in EXPECTED_PROJECT_COUNTS.items():
        assert f"計画事業（重複を除く）{count}件" in projects[pid]["purpose"]


def test_budget_amounts_are_explicitly_unregistered() -> None:
    # Chiba publishes no per-policy FY2026 budget: the implementation
    # plan prints no amounts at any level and the budget documents are
    # aggregated by account and category, so amounts stay null instead
    # of 0.
    for record in load(PROJECTS_PATH):
        assert len(record["budget_records"]) == 1
        budget = record["budget_records"][0]
        assert budget["kind"] == "initial_budget"
        assert budget["fiscal_year"] == 2026
        assert budget["amount_yen"] is None
        assert "未登録とした" in budget["note"]
        assert "0では補完しない" in budget["note"]
        assert "原案可決" in budget["note"]


def test_official_evaluation_is_explicitly_unregistered() -> None:
    # The policy evaluation runs after the implementation-plan period
    # ends; FY2026 is the first year of the 2nd plan, and no evaluation
    # of the current basic plan (including the 1st plan period) has been
    # published at all. Old plans' evaluations belong to a different
    # framework and are not carried over.
    for record in load(PROJECTS_PATH):
        assert record["official_evaluation"] is None
    packets = load(PACKETS_PATH)
    for packet in packets:
        joined = "".join(packet["open_questions"])
        assert "公式評価は未登録" in joined
        assert "金額は未登録" in joined


def test_kpis_are_explicitly_unregistered() -> None:
    # Indicators (KGI/KPI) are set per field, not per policy, and are
    # already registered in current_policy_indicators.json. Attaching a
    # field's indicators to one of its policies would misattribute them,
    # so the KPI layer stays explicitly empty (the Kawasaki pattern).
    assert load(KPIS_PATH) == []
    for record in load(PROJECTS_PATH):
        assert record["kpis"] == []
    for packet in load(PACKETS_PATH):
        claim = next(c for c in packet["claims"] if c["field"] == "kpis")
        assert "付け替えない" in claim["statement"]
        assert "current_policy_indicators.json" in claim["statement"]
