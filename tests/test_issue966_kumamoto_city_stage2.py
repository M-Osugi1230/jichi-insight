from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
MID = "jp-local-431001"
SOURCES_PATH = ROOT / "data/catalog/kumamoto_city_project_sources.json"
SELECTION_PATH = ROOT / "data/catalog/kumamoto_city_priority_project_selection.json"
PROJECTS_PATH = ROOT / "data/reviewed/kumamoto-city/projects.json"
KPIS_PATH = ROOT / "data/reviewed/kumamoto-city/project_kpis.json"
PACKETS_PATH = ROOT / "data/reviewed/kumamoto-city/project_evidence_packets.json"

VISION1 = "こどもが輝き、若者が希望を抱くまち"
VISION2 = "市民に愛され、世界に選ばれる、持続的な発展を実現するまち"
VISION3 = "市民生活を守る強くしなやかなまち"
VISIONS = [
    VISION1,
    VISION2,
    VISION3,
    "だれもが自分らしくいきいきと生活できるまち",
    "豊かな環境を未来につなぐまち",
    "すべての市民がより良い暮らしを営むまち",
    "安全で良好な都市基盤が整備されたまち",
    "市民に信頼される市役所",
]

EXPECTED_IDS = [
    "jp-local-431001-project-2024-child-growth-family-support",
    "jp-local-431001-project-2024-support-children-families-in-difficulty",
    "jp-local-431001-project-2024-child-centered-education",
    "jp-local-431001-project-2024-human-resource-development",
    "jp-local-431001-project-2024-semiconductor-and-sme-promotion",
    "jp-local-431001-project-2024-urban-brand",
    "jp-local-431001-project-2024-exchange-population-vitality",
    "jp-local-431001-project-2024-wide-area-transport-network",
    "jp-local-431001-project-2024-agriculture-fisheries-promotion",
    "jp-local-431001-project-2024-disaster-prevention-mitigation",
]

# Stage 3 (Issue #975) linked the 2026 mayoral promises to four of
# the ten series. The promises reference the term starting
# 2026-12-03, which is registered once it starts (Issue #706).
_FUTURE_TERM = "jp-local-431001-executive-2026-12-03"
EXPECTED_PROMISE_LINKS = {
    "jp-local-431001-project-2024-child-growth-family-support": [
        f"{_FUTURE_TERM}-promise-005",
        f"{_FUTURE_TERM}-promise-006",
    ],
    "jp-local-431001-project-2024-child-centered-education": [
        f"{_FUTURE_TERM}-promise-004",
    ],
    "jp-local-431001-project-2024-wide-area-transport-network": [
        f"{_FUTURE_TERM}-promise-002",
        f"{_FUTURE_TERM}-promise-007",
    ],
    "jp-local-431001-project-2024-disaster-prevention-mitigation": [
        f"{_FUTURE_TERM}-promise-001",
        f"{_FUTURE_TERM}-promise-003",
        f"{_FUTURE_TERM}-promise-009",
    ],
}

EXPECTED_TITLES = [
    "すべてのこどもの健やかな成長と家庭の幸せへの支援",
    "困難な状況にあるこどもや子育て家庭への支援",
    "こどもを主体とした教育の推進",
    "まちを支える人材の確保・育成",
    "半導体関連産業等への新たな投資の後押しや中小企業等の振興",
    "世界を魅了する都市ブランド力の向上",
    "交流人口拡大によるにぎわいの創出",
    "広域交通ネットワークの形成による物流・人流の円滑化",
    "活力と魅力に満ちた持続可能な農水産業の振興",
    "防災・減災の推進",
]

# The first ten measures of the 8th Comprehensive Plan in listing
# order: measures 1-1 to 1-4 sit under vision 1, measures 2-1 to 2-5
# under vision 2 and measure 3-1 under vision 3.
EXPECTED_PILLARS = [VISION1] * 4 + [VISION2] * 5 + [VISION3]

EXPECTED_DEPARTMENTS = [
    "健康福祉局、こども局、区役所、教育委員会事務局",
    "文化市民局、健康福祉局、こども局、区役所、教育委員会事務局",
    "教育委員会事務局",
    "政策局、文化市民局、健康福祉局、経済観光局、農水局、都市建設局",
    "経済観光局",
    "文化市民局、環境局、経済観光局、都市建設局",
    "政策局、経済観光局",
    "経済観光局、都市建設局",
    "農水局、農業委員会事務局",
    "政策局、健康福祉局、都市建設局、消防局、上下水道局、教育委員会事務局",
]

EXPECTED_POLICY_AREAS = [
    "childcare",
    "welfare",
    "education",
    "employment",
    "industry",
    "tourism",
    "tourism",
    "transport",
    "agriculture",
    "disaster_prevention",
]

# Outcome indicators per measure in the FY2024 administrative
# evaluation indicator list (43 in total across the ten measures).
EXPECTED_KPI_COUNTS = [3, 4, 9, 2, 3, 5, 4, 4, 5, 4]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validator(name: str) -> Draft202012Validator:
    schema = load(ROOT / "schemas" / name)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def test_kumamoto_city_project_sources_are_schema_valid() -> None:
    catalog = load(SOURCES_PATH)
    validator("source_catalog.schema.json").validate(catalog)
    ids = [record["id"] for record in catalog["records"]]
    assert len(ids) == len(set(ids)) == 7
    assert all(
        record["municipality_key"] == "kumamoto-city" for record in catalog["records"]
    )


def test_selection_rule_is_plan_listing_order() -> None:
    selection = load(SELECTION_PATH)
    assert selection["municipality_id"] == MID
    assert selection["issue"] == 966
    assert selection["population"]["fiscal_year"] == 2024
    # The population is the measure framework of the 8th
    # Comprehensive Plan: 32 measures under eight visions.
    assert selection["population"]["policy_count"] == 32
    assert selection["population"]["group_count"] == 8
    assert selection["selection_rule"]["pillars"] == VISIONS
    assert "金額の大小では選ばない" in selection["selection_rule"]["description"]
    selected = selection["selections"]
    assert [item["project_id"] for item in selected] == EXPECTED_IDS
    assert [item["official_title"] for item in selected] == EXPECTED_TITLES
    assert [item["policy"] for item in selected] == EXPECTED_PILLARS
    assert [item["pillar"] for item in selected] == EXPECTED_PILLARS
    assert [item["department"] for item in selected] == EXPECTED_DEPARTMENTS
    assert selection["expansion_rule"]["total_count"] == 10


def test_registration_unit_and_framework_limits_are_documented() -> None:
    # The registration unit is the plan's "measure" (施策), the unit
    # at which the city's administrative evaluation publishes an
    # evaluation sheet and indicator progress grades. The settlement
    # report is organised by bureau, not by the plan framework, and
    # no official correspondence table is published, so no mapping
    # between the plan framework and settlement figures is made.
    selection = load(SELECTION_PATH)
    description = selection["population"]["description"]
    assert "登録単位は「施策」とした" in description
    assert "対応付けは行っていない" in description
    assert "令和7年度行政評価の公表は" in description
    for packet in load(PACKETS_PATH):
        claim = next(c for c in packet["claims"] if c["field"] == "registration_unit")
        assert "本登録の単位は" in claim["statement"]
        assert "「施策」とした" in claim["statement"]
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
        assert record["fiscal_year"] == 2024
        assert record["review_status"] == "reviewed"
        # Stage 3 (Issue #975) registered the 2026 mayoral promises
        # and linked them to the series below (confidence low /
        # inferred); every other series remains unlinked.
        assert record["related_promise_ids"] == EXPECTED_PROMISE_LINKS.get(
            item["project_id"], []
        )
    areas = [projects[pid]["policy_area"] for pid in EXPECTED_IDS]
    assert areas == EXPECTED_POLICY_AREAS


def test_budget_amounts_are_unregistered_with_reasons() -> None:
    # The administrative evaluation publications carry no
    # per-measure amounts, and the settlement report is organised by
    # bureau rather than by the plan framework, so no measure-level
    # amount is registered instead of relabelling figures from
    # another framework.
    for record in load(PROJECTS_PATH):
        assert len(record["budget_records"]) == 1
        budget = record["budget_records"][0]
        assert budget["kind"] == "settlement"
        assert budget["fiscal_year"] == 2024
        assert budget["amount_yen"] is None
        assert "未登録とした" in budget["note"]
        assert "0では補完しない" in budget["note"]


def test_official_evaluation_is_null_because_no_single_rating_exists() -> None:
    # Kumamoto City's administrative evaluation publishes no single
    # rating per measure: only per-indicator progress grades and
    # narrative evaluations by department. The registration keeps
    # official_evaluation null instead of inventing a rating.
    for record in load(PROJECTS_PATH):
        assert record["official_evaluation"] is None
    for packet in load(PACKETS_PATH):
        claim = next(c for c in packet["claims"] if c["field"] == "official_evaluation")
        assert "単一の評定" in claim["statement"]
        assert "null とした" in claim["statement"]
        assert "令和6年度行政評価（2025年9月16日公表）" in claim["statement"]


def test_kpis_follow_the_published_indicator_grades() -> None:
    projects = load(PROJECTS_PATH)
    counts = [len(record["kpis"]) for record in projects]
    assert counts == EXPECTED_KPI_COUNTS
    assert sum(counts) == 43
    by_name = {kpi["name"]: kpi for record in projects for kpi in record["kpis"]}
    # Measure 1-1: the total fertility rate was graded × (stalled).
    # Its published figures lag one year (baseline cell carries the
    # FY2022 value, the FY2024 actual cell the FY2023 value).
    tfr = by_name["合計特殊出生率"]
    assert (tfr["baseline"], tfr["target"], tfr["actual"]) == (1.43, 1.55, 1.32)
    assert tfr["assessment"] == "not_achieved"
    # Measure 2-1: gross city product was graded ○ (on track); the
    # baseline is the FY2022 estimate published in the plan.
    gcp = by_name["市内総生産（試算値）"]
    assert (gcp["baseline"], gcp["target"], gcp["actual"]) == (2726, 3093, 2845)
    assert gcp["assessment"] == "achieved"
    # Measure 2-2: no FY2024 actual was published for the share of
    # citizens who feel they have cultural/tourism assets to be
    # proud of, and the city left the indicator ungraded, so the
    # actual stays null (never zero-filled).
    pride = by_name["誇れる文化・観光資源があると感じる市民の割合"]
    assert pride["baseline"] == 93.9
    assert pride["target"] == 100
    assert pride["actual"] is None
    assert pride["assessment"] == "not_assessable"
    # Measure 2-3: the dissemination count likewise has no values in
    # the FY2024 evaluation list; its baseline is the FY2022 figure
    # published in the plan book (33).
    dissemination = by_name[
        "海外諸都市、国際機関などとのネットワークを活用して、熊本市の魅力を発信した件数"
    ]
    assert dissemination["baseline"] == 33
    assert dissemination["actual"] is None
    assert dissemination["assessment"] == "not_assessable"
    # Measure 2-5: the suppression-rate indicator has a qualitative
    # target ("推計値より10％抑制") and the city recorded the FY2024
    # result as the string "達成"; both are kept as published.
    suppression = by_name["認定農業者数の減少の抑制率"]
    assert suppression["baseline"] is None
    assert suppression["target"] == "推計値より10％抑制"
    assert suppression["actual"] == "達成"
    assert suppression["assessment"] == "achieved"
    farmers = by_name["認定農業者数"]
    assert (farmers["baseline"], farmers["actual"]) == (1460, 1499)
    assert farmers["target"] == "1,330以上"


def test_detailed_kpis_are_schema_valid_and_linked() -> None:
    kpis = load(KPIS_PATH)
    assert len(kpis) == 43
    project_ids = {record["id"] for record in load(PROJECTS_PATH)}
    for kpi in kpis:
        validator("kpi.schema.json").validate(kpi)
        assert kpi["project_id"] in project_ids
        assert kpi["id"].startswith(kpi["project_id"] + "-kpi-")
        assert "換算したものである" in kpi["definition"]
    pride = next(
        kpi for kpi in kpis if kpi["name"].startswith("誇れる文化・観光資源がある")
    )
    assert pride["actuals"][0]["status"] == "not_published"
    assert pride["actuals"][0]["value"] is None
    assert pride["baseline"]["value"] == 93.9
    suppression = next(kpi for kpi in kpis if kpi["name"] == "認定農業者数の減少の抑制率")
    assert suppression["baseline"]["status"] == "not_published"
    assert suppression["baseline"]["value"] is None
    assert suppression["actuals"][0]["value"] == "達成"


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
        # The unpublished FY2025 administrative evaluation stays an
        # open question on every packet.
        assert any(
            "令和7年度行政評価" in question for question in packet["open_questions"]
        )
