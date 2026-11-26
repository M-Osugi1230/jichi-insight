from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
MID = "jp-local-062014"
SOURCES_PATH = ROOT / "data/catalog/yamagata_city_project_sources.json"
SELECTION_PATH = ROOT / "data/catalog/yamagata_city_priority_project_selection.json"
PROJECTS_PATH = ROOT / "data/reviewed/yamagata-city/projects.json"
KPIS_PATH = ROOT / "data/reviewed/yamagata-city/project_kpis.json"
PACKETS_PATH = ROOT / "data/reviewed/yamagata-city/project_evidence_packets.json"
REGISTRY_PATH = ROOT / "apps/web/lib/projectRegistry.ts"

THEME1 = "まちをつくる"
THEME2 = "ひとを育む"
THEME3 = "しごとを豊かにする"
THEME4 = "未来へつなげる行政経営"

EXPECTED_IDS = [
    "jp-local-062014-project-2025-public-transport",
    "jp-local-062014-project-2025-urban-development",
    "jp-local-062014-project-2025-central-city-area",
    "jp-local-062014-project-2025-disaster-prevention",
    "jp-local-062014-project-2025-community",
    "jp-local-062014-project-2025-environment",
    "jp-local-062014-project-2025-education",
    "jp-local-062014-project-2025-children",
    "jp-local-062014-project-2025-health",
    "jp-local-062014-project-2025-medical-care",
    "jp-local-062014-project-2025-welfare",
    "jp-local-062014-project-2025-culture",
    "jp-local-062014-project-2025-sports",
    "jp-local-062014-project-2025-commerce-industry",
    "jp-local-062014-project-2025-tourism",
    "jp-local-062014-project-2025-agriculture-forestry",
    "jp-local-062014-project-2025-gender-equality",
    "jp-local-062014-project-2025-city-promotion",
    "jp-local-062014-project-2025-administration",
]

PROMISE_TERM = "jp-local-062014-executive-2023-09-28"
EXPECTED_PROMISE_LINKS = {
    "jp-local-062014-project-2025-public-transport": [
        f"{PROMISE_TERM}-promise-001"
    ],
    "jp-local-062014-project-2025-urban-development": [
        f"{PROMISE_TERM}-promise-007"
    ],
    "jp-local-062014-project-2025-central-city-area": [
        f"{PROMISE_TERM}-promise-006"
    ],
    "jp-local-062014-project-2025-education": [
        f"{PROMISE_TERM}-promise-002"
    ],
    "jp-local-062014-project-2025-children": [
        f"{PROMISE_TERM}-promise-002"
    ],
    "jp-local-062014-project-2025-health": [
        f"{PROMISE_TERM}-promise-005"
    ],
    "jp-local-062014-project-2025-medical-care": [
        f"{PROMISE_TERM}-promise-005"
    ],
    "jp-local-062014-project-2025-welfare": [
        f"{PROMISE_TERM}-promise-005"
    ],
    "jp-local-062014-project-2025-culture": [
        f"{PROMISE_TERM}-promise-006"
    ],
    "jp-local-062014-project-2025-sports": [
        f"{PROMISE_TERM}-promise-005"
    ],
    "jp-local-062014-project-2025-commerce-industry": [
        f"{PROMISE_TERM}-promise-003"
    ],
    "jp-local-062014-project-2025-tourism": [
        f"{PROMISE_TERM}-promise-007"
    ],
    "jp-local-062014-project-2025-agriculture-forestry": [
        f"{PROMISE_TERM}-promise-004"
    ],
}

EXPECTED_TITLES = [
    "公共交通",
    "都市整備",
    "中心市街地",
    "防災",
    "コミュニティ",
    "環境",
    "教育",
    "こども",
    "健康",
    "医療",
    "福祉",
    "文化",
    "スポーツ",
    "商工",
    "観光",
    "農林",
    "男女共同参画",
    "シティプロモーション",
    "行政",
]

# The 19 policy fields sit under four themes in the plan book:
# fields 01-06 under theme I, 07-13 under theme II, 14-18 under
# theme III and field 19 under the administration theme.
EXPECTED_PILLARS = [THEME1] * 6 + [THEME2] * 7 + [THEME3] * 5 + [THEME4]

EXPECTED_POLICY_AREAS = [
    "transport",
    "infrastructure",
    "infrastructure",
    "disaster_prevention",
    "governance",
    "environment",
    "education",
    "childcare",
    "health",
    "health",
    "welfare",
    "culture",
    "sports",
    "industry",
    "tourism",
    "agriculture",
    "governance",
    "other",
    "governance",
]

# Outcome indicators per policy field in the plan book's
# "政策分野別成果指標" list (45 in total across the 19 fields).
EXPECTED_KPI_COUNTS = [1, 2, 1, 2, 1, 2, 3, 3, 4, 1, 2, 2, 1, 3, 3, 3, 3, 3, 5]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validator(name: str) -> Draft202012Validator:
    schema = load(ROOT / "schemas" / name)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def test_yamagata_city_project_sources_are_schema_valid() -> None:
    catalog = load(SOURCES_PATH)
    validator("source_catalog.schema.json").validate(catalog)
    ids = [record["id"] for record in catalog["records"]]
    assert len(ids) == len(set(ids)) == 4
    assert all(record["municipality_key"] == "yamagata-city" for record in catalog["records"])


def test_selection_covers_all_policy_fields_in_listing_order() -> None:
    selection = load(SELECTION_PATH)
    assert selection["municipality_id"] == MID
    assert selection["issue"] == 1025
    assert selection["plan_title"] == "山形市発展計画2030"
    # The population is the plan's framework of 19 policy fields.
    assert selection["population"]["item_count"] == 19
    assert selection["population"]["unit"] == "policy_field"
    assert "金額の大小では選ばない" in selection["selection_rule"]
    selected = selection["selections"]
    assert [item["project_id"] for item in selected] == EXPECTED_IDS
    assert [item["official_title"] for item in selected] == EXPECTED_TITLES
    assert [item["pillar"] for item in selected] == EXPECTED_PILLARS
    assert [item["policy"] for item in selected] == [
        f"政策分野{index:02d}" for index in range(1, 20)
    ]
    # The plan book prints no department per policy field.
    assert all(item["department"] is None for item in selected)


def test_registration_unit_and_framework_limits_are_documented() -> None:
    # The registration unit is the plan's policy field, the unit
    # fixed by the stage-1 plan_review and the unit at which the
    # plan manages progress through its outcome indicators. The
    # stage-0 candidate unit (measure) was rejected after the actual
    # FY2025 results report showed it publishes neither per-measure
    # amount totals nor ratings. No mapping to the previous plan
    # (発展計画2025) is made because no official correspondence
    # table exists.
    selection = load(SELECTION_PATH)
    description = selection["population"]["description"]
    assert "登録単位は政策分野とした" in description
    assert "対応付けは、公式の対応表がないため行っていない" in description
    for packet in load(PACKETS_PATH):
        claim = next(c for c in packet["claims"] if c["field"] == "registration_unit")
        assert "「政策分野」とした" in claim["statement"]
        assert "対応付けは、公式の対応表がないため行っていない" in claim["statement"]


def test_selected_projects_match_records() -> None:
    projects = {record["id"]: record for record in load(PROJECTS_PATH)}
    selection = load(SELECTION_PATH)
    assert len(projects) == 19
    for item in selection["selections"]:
        record = projects[item["project_id"]]
        validator("project.schema.json").validate(record)
        assert record["series_id"] == item["series_id"]
        assert record["official_title"] == item["official_title"]
        assert record["parent_policy"] == item["pillar"]
        assert record["responsible_department"] is None
        assert record["municipality_id"] == MID
        assert record["fiscal_year"] == 2025
        assert record["review_status"] == "reviewed"
        # Stage 3 (Issue #1037) connected the mayoral promises whose
        # wording matches each policy field; all other fields keep an
        # empty list.
        assert record["related_promise_ids"] == EXPECTED_PROMISE_LINKS.get(
            item["project_id"], []
        )
    areas = [projects[pid]["policy_area"] for pid in EXPECTED_IDS]
    assert areas == EXPECTED_POLICY_AREAS


def test_budget_amounts_are_unregistered_with_reasons() -> None:
    # The FY2025 results report prints execution amounts only per
    # individual project (事業); no policy-field total is
    # published, and summing project amounts would not be a
    # published figure, so the amount stays unregistered (null)
    # instead of being fabricated or zero-filled.
    for record in load(PROJECTS_PATH):
        assert len(record["budget_records"]) == 1
        budget = record["budget_records"][0]
        assert budget["kind"] == "settlement"
        assert budget["fiscal_year"] == 2025
        assert budget["amount_yen"] is None
        assert "未登録" in budget["note"]
        assert "0では補完しない" in budget["note"]


def test_official_evaluation_is_null_because_no_rating_is_published() -> None:
    # Yamagata City publishes no rating (達成度区分) per policy
    # field; progress is managed only through the outcome
    # indicators' baselines and targets.
    for record in load(PROJECTS_PATH):
        assert record["official_evaluation"] is None
    for packet in load(PACKETS_PATH):
        claim = next(c for c in packet["claims"] if c["field"] == "official_evaluation")
        assert "公表していないため" in claim["statement"]
        assert "null とした" in claim["statement"]


def test_kpis_use_only_published_baselines_and_targets() -> None:
    projects = load(PROJECTS_PATH)
    counts = [len(record["kpis"]) for record in projects]
    assert counts == EXPECTED_KPI_COUNTS
    assert sum(counts) == 45
    by_name = {kpi["name"]: kpi for record in projects for kpi in record["kpis"]}
    # No FY2025 actuals for the plan's outcome indicators were
    # published as of 2026-11-26, so every actual stays null and
    # every assessment is not_assessable (never zero-filled).
    for kpi in by_name.values():
        assert kpi["actual"] is None
        assert kpi["assessment"] == "not_assessable"
    transit = by_name["公共交通の利用者数"]
    assert (transit["baseline"], transit["target"]) == (11145, 11932)
    # Gender-split figures are kept as the published strings.
    longevity = by_name["健康寿命"]
    assert longevity["baseline"] == "男性：80.70歳、女性：85.07歳"
    assert longevity["target"] == "男性：81.48歳、女性：85.12歳"
    # Qualitative targets are kept as published, not converted
    # into invented numbers.
    fertility = by_name["合計特殊出生率"]
    assert fertility["baseline"] == 1.16
    assert fertility["target"] == "基準値を上回る"
    debt = by_name["実質公債費比率"]
    assert debt["target"] == "地方債同意等基準18％未満"
    # The plan prints negative net-outflow figures with ▲; they
    # are registered as signed numbers.
    outflow = by_name["20代女性の県外転出数（転入者−転出者）"]
    assert (outflow["baseline"], outflow["target"]) == (-464, -314)


def test_detailed_kpis_are_schema_valid_and_linked() -> None:
    kpis = load(KPIS_PATH)
    assert len(kpis) == 45
    project_ids = {record["id"] for record in load(PROJECTS_PATH)}
    for kpi in kpis:
        validator("kpi.schema.json").validate(kpi)
        assert kpi["project_id"] in project_ids
        assert kpi["id"].startswith(kpi["project_id"] + "-kpi-")
        assert kpi["assessment"] == "not_assessable"
        assert kpi["actuals"] == []
        assert "公表を確認できないため" in kpi["definition"]
        # The 2040 target (目標値❷) is recorded in the definition.
        assert "目標値❷" in kpi["definition"]
    ghg = next(kpi for kpi in kpis if kpi["name"] == "市内の温室効果ガス排出量")
    assert ghg["direction"] == "decrease"
    assert ghg["baseline"]["value"] == 1339
    assert ghg["target"]["value"] == 973
    # Its target year is FY2027 (provisional), not 2029.
    assert ghg["target"]["period"] == "令和9年度（暫定）"


def test_evidence_packets_are_schema_valid() -> None:
    packets = load(PACKETS_PATH)
    assert len(packets) == 19
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
            "review_basis",
        }
        # The review rests on the owner's 2026-11-15 delegation to
        # Muse; it is not recorded as the owner's own review.
        basis = next(c for c in packet["claims"] if c["field"] == "review_basis")
        assert "2026年11月15日" in basis["statement"]
        assert "所有者本人のレビューではない" in basis["statement"]
        # The unpublished indicator actuals stay an open question.
        assert any("実績値" in question for question in packet["open_questions"])


def test_web_registry_includes_yamagata_city_projects() -> None:
    registry = REGISTRY_PATH.read_text(encoding="utf-8")
    assert '"yamagata-city": { name: "山形市"' in registry
    assert "yamagata_city_project_sources.json" in registry
    assert "data/reviewed/yamagata-city/projects.json" in registry
