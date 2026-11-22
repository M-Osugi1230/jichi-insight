from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
MID = "jp-local-341003"
SOURCES_PATH = ROOT / "data/catalog/hiroshima_city_project_sources.json"
SELECTION_PATH = ROOT / "data/catalog/hiroshima_city_priority_project_selection.json"
PROJECTS_PATH = ROOT / "data/reviewed/hiroshima-city/projects.json"
KPIS_PATH = ROOT / "data/reviewed/hiroshima-city/project_kpis.json"
PACKETS_PATH = ROOT / "data/reviewed/hiroshima-city/project_evidence_packets.json"

D1 = "総務関係"
D2 = "民生関係"
D3 = "衛生関係"
D4 = "経済関係"
D5 = "建設関係"
D6 = "消防関係"
D7 = "教育関係"
PILLARS = [D1, D2, D3, D4, D5, D6, D7]

EXPECTED_IDS = [
    "jp-local-341003-project-2025-city-tax",
    "jp-local-341003-project-2025-social-welfare",
    "jp-local-341003-project-2025-public-health-hygiene",
    "jp-local-341003-project-2025-economic-promotion",
    "jp-local-341003-project-2025-roads-and-bridges",
    "jp-local-341003-project-2025-fire-service",
    "jp-local-341003-project-2025-schools",
    "jp-local-341003-project-2025-urban-centrality",
    "jp-local-341003-project-2025-long-term-care-insurance",
    "jp-local-341003-project-2025-atomic-bomb-survivor-measures",
]

# Stage 3 (Issue #921) linked five of Mayor Matsui's fourteen
# bulletin promises back to three series (inference capped at
# low / inferred; the stage-3 test pins the forward links).
_MAYOR_TERM = "jp-local-341002-executive-2023-04-12"
EXPECTED_PROMISE_LINKS = {
    "jp-local-341003-project-2025-social-welfare": [
        f"{_MAYOR_TERM}-promise-006",
        f"{_MAYOR_TERM}-promise-007",
    ],
    "jp-local-341003-project-2025-economic-promotion": [
        f"{_MAYOR_TERM}-promise-005",
    ],
    "jp-local-341003-project-2025-urban-centrality": [
        f"{_MAYOR_TERM}-promise-001",
        f"{_MAYOR_TERM}-promise-002",
    ],
}

EXPECTED_TITLES = [
    "市税等について",
    "社会福祉について",
    "保健衛生について",
    "経済の振興について",
    "道路、橋りょうについて",
    "消防について",
    "学校について",
    "中枢性の強化について",
    "介護保険事業について",
    "原爆被爆者対策について",
]

# Round-robin over the seven divisions (関係) of the FY2025 "Major
# Policy Outcomes" in the document's listing order; each division
# contributes its first chapter, and the second round takes the
# second chapters of the first three divisions.
EXPECTED_PILLARS = [D1, D2, D3, D4, D5, D6, D7, D1, D2, D3]

EXPECTED_POLICY_AREAS = [
    "finance",
    "welfare",
    "health",
    "industry",
    "infrastructure",
    "safety",
    "education",
    "governance",
    "welfare",
    "welfare",
]

# Only two chapters carry a printed total that covers the whole
# chapter: chapter 6 (a single table with a printed grand total) and
# chapter 24 (the long-term care insurance special account, whose
# printed expenditure total covers the whole chapter). Every other
# chapter stays unregistered instead of summing partial figures.
EXPECTED_AMOUNTS = {
    "jp-local-341003-project-2025-urban-centrality": 68519000,
    "jp-local-341003-project-2025-long-term-care-insurance": 108090374000,
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validator(name: str) -> Draft202012Validator:
    schema = load(ROOT / "schemas" / name)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def test_hiroshima_city_project_sources_are_schema_valid() -> None:
    catalog = load(SOURCES_PATH)
    validator("source_catalog.schema.json").validate(catalog)
    ids = [record["id"] for record in catalog["records"]]
    assert len(ids) == len(set(ids)) == 12
    assert all(
        record["municipality_key"] == "hiroshima-city" for record in catalog["records"]
    )


def test_selection_rule_is_listing_order_by_division() -> None:
    selection = load(SELECTION_PATH)
    assert selection["municipality_id"] == MID
    assert selection["issue"] == 918
    assert selection["population"]["fiscal_year"] == 2025
    # The population is the chapter framework of the FY2025 "Major
    # Policy Outcomes": seven divisions and 47 policy chapters
    # (chapters 5-51), with the four summary sections excluded.
    assert selection["population"]["division_count"] == 7
    assert selection["population"]["chapter_count"] == 47
    assert selection["population"]["excluded_summary_count"] == 4
    assert selection["selection_rule"]["pillars"] == PILLARS
    assert "金額の大小では選ばない" in selection["selection_rule"]["description"]
    selected = selection["selections"]
    assert [item["project_id"] for item in selected] == EXPECTED_IDS
    assert [item["official_title"] for item in selected] == EXPECTED_TITLES
    assert [item["policy"] for item in selected] == EXPECTED_PILLARS
    assert [item["pillar"] for item in selected] == EXPECTED_PILLARS
    assert selection["expansion_rule"]["total_count"] == 10


def test_framework_mismatch_with_basic_plan_is_documented() -> None:
    # The outcomes document is organised by budget divisions, not by
    # the 6th basic plan's framework (six chapters, eighteen
    # sections), and no official correspondence table exists. The
    # registration therefore uses the document's own divisions as
    # pillars and never maps chapters onto the plan's framework.
    selection = load(SELECTION_PATH)
    description = selection["population"]["description"]
    assert "第6次広島市基本計画の体系" in description
    assert "一致しない" in description
    assert "対応表は" in description
    for packet in load(PACKETS_PATH):
        claim = next(c for c in packet["claims"] if c["field"] == "registration_unit")
        assert "本登録の単位は" in claim["statement"]
        assert "の章（第○「○○について」）とした" in claim["statement"]
        assert "とは一致せず" in claim["statement"]


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
        # The document does not name a responsible bureau per
        # chapter, so the department stays unregistered.
        assert record["responsible_department"] is None
        assert record["municipality_id"] == MID
        assert record["fiscal_year"] == 2025
        assert record["review_status"] == "reviewed"
        # Stage 3 (Issue #921) linked the mayor's bulletin
        # promises back to three of the series; the exact links
        # are pinned by the stage-3 test. All other series stay
        # unlinked.
        assert record["related_promise_ids"] == EXPECTED_PROMISE_LINKS.get(
            record["id"], []
        )
    areas = [projects[pid]["policy_area"] for pid in EXPECTED_IDS]
    assert areas == EXPECTED_POLICY_AREAS


def test_budget_amounts_follow_the_printed_totals() -> None:
    # Settlement amounts are registered only where the document
    # prints a total covering the whole chapter. Partial totals
    # (per item or per category) are never summed or relabelled:
    # the notes of the legend state that figures marked with an
    # asterisk are duplicated in other items, so summing would
    # double-count.
    for record in load(PROJECTS_PATH):
        assert len(record["budget_records"]) == 1
        budget = record["budget_records"][0]
        assert budget["kind"] == "settlement"
        assert budget["fiscal_year"] == 2025
        expected = EXPECTED_AMOUNTS.get(record["id"])
        assert budget["amount_yen"] == expected
        if expected is None:
            assert "未登録とした" in budget["note"]
            assert "0では補完しない" in budget["note"]


def test_official_evaluation_is_unregistered() -> None:
    # The outcomes document has no rating scale per chapter; results
    # are narrative (programmes, amounts, counts). Following the
    # Hamamatsu pattern, the structured evaluation stays null and
    # the absence is documented, never read as non-achievement.
    for record in load(PROJECTS_PATH):
        assert record["official_evaluation"] is None
    for packet in load(PACKETS_PATH):
        claim = next(c for c in packet["claims"] if c["field"] == "official_evaluation")
        assert "評定区分（達成度等の区分）は設けられていない" in claim["statement"]


def test_kpis_are_not_connected_across_frameworks() -> None:
    # The implementation plan (2025-2030) verifies KPIs under the
    # basic plan's framework. The outcomes document's chapters belong
    # to a different framework and no official correspondence table
    # exists, so no KPIs are connected (the Kobe empty-file pattern).
    assert load(KPIS_PATH) == []
    for record in load(PROJECTS_PATH):
        assert record["kpis"] == []
    for packet in load(PACKETS_PATH):
        claim = next(c for c in packet["claims"] if c["field"] == "kpis")
        assert "公式対応表は公表されておらず" in claim["statement"]
        assert "未登録（0件）とした" in claim["statement"]


def test_evidence_packets_are_schema_valid() -> None:
    packets = load(PACKETS_PATH)
    assert len(packets) == 10
    project_ids = {record["id"] for record in load(PROJECTS_PATH)}
    for packet in packets:
        validator("evidence_packet.schema.json").validate(packet)
        assert packet["subject_type"] == "project"
        assert packet["subject_id"] in project_ids
        assert packet["id"] == f"evidence-{packet['subject_id']}"
