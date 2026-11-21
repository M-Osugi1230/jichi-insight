from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
MID = "jp-local-041009"
SOURCES_PATH = ROOT / "data/catalog/sendai_city_project_sources.json"
SELECTION_PATH = ROOT / "data/catalog/sendai_city_priority_project_selection.json"
PROJECTS_PATH = ROOT / "data/reviewed/sendai-city/projects.json"
KPIS_PATH = ROOT / "data/reviewed/sendai-city/project_kpis.json"
PACKETS_PATH = ROOT / "data/reviewed/sendai-city/project_evidence_packets.json"

G1 = "杜と水の都プロジェクト"
G2 = "防災環境都市プロジェクト"
G3 = "心の伴走プロジェクト"
G4 = "地域協働プロジェクト"
G5 = "笑顔咲く子どもプロジェクト"
G6 = "ライフデザインプロジェクト"
G7 = "TOHOKU未来プロジェクト"
G8 = "都心創生プロジェクト"
G9 = "市政運営"
PILLARS = [G1, G2, G3, G4, G5, G6, G7, G8, G9]

EXPECTED_IDS = [
    "jp-local-041009-project-2025-new-city-hall-development",
    "jp-local-041009-project-2025-disaster-resilient-city-promotion",
    "jp-local-041009-project-2025-sexual-minorities-and-women-support",
    "jp-local-041009-project-2025-community-partnership-support",
    "jp-local-041009-project-2025-childrearing-support-momentum",
    "jp-local-041009-project-2025-culture-arts-city-appeal",
    "jp-local-041009-project-2025-research-complex-formation",
    "jp-local-041009-project-2025-central-shopping-district-revitalization",
    "jp-local-041009-project-2025-full-digital-city-hall",
    "jp-local-041009-project-2025-kotodai-park-redevelopment",
]

EXPECTED_TITLES = [
    "新本庁舎整備事業",
    "防災環境都市づくり推進事業",
    "性的少数者・困難を抱える女性支援事業",
    "地域づくりパートナーサポート事業",
    "子育て応援の機運醸成事業",
    "文化芸術によるまちの魅力づくり事業",
    "リサーチコンプレックス形成推進事業",
    "中心部商店街活性化促進事業",
    "「Full Digitalの市役所」推進事業",
    "勾当台公園及び周辺再整備事業",
]

# Round-robin over the nine groups in the self-evaluation report's
# listing order; the second round takes group 1's second project.
EXPECTED_PARENTS = [G1, G2, G3, G4, G5, G6, G7, G8, G9, G1]
EXPECTED_REPORT_NUMBERS = [1, 12, 25, 37, 52, 63, 75, 90, 100, 2]

EXPECTED_POLICY_AREAS = [
    "governance",
    "disaster_prevention",
    "welfare",
    "governance",
    "childcare",
    "culture",
    "industry",
    "industry",
    "digital",
    "infrastructure",
]

EXPECTED_DEPARTMENTS = [
    "財政局",
    "まちづくり政策局",
    "市民局",
    "市民局・各区",
    "こども若者局",
    "文化観光局",
    "経済局",
    "経済局",
    "まちづくり政策局",
    "建設局",
]

# The city's own FY2025 self-evaluation marks as printed in the
# report's progress column (verified against the FY2024 report, whose
# marks agree for all 108 projects).
EXPECTED_RATINGS = [
    "○ 予定どおり進んでいる",
    "◎ 予定を上回る成果が出ている",
    "○ 予定どおり進んでいる",
    "○ 予定どおり進んでいる",
    "○ 予定どおり進んでいる",
    "△ 一部にやや遅れが出ている",
    "○ 予定どおり進んでいる",
    "○ 予定どおり進んでいる",
    "○ 予定どおり進んでいる",
    "○ 予定どおり進んでいる",
]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validator(name: str) -> Draft202012Validator:
    schema = load(ROOT / "schemas" / name)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def test_sendai_city_project_sources_are_schema_valid() -> None:
    catalog = load(SOURCES_PATH)
    validator("source_catalog.schema.json").validate(catalog)
    ids = [record["id"] for record in catalog["records"]]
    assert len(ids) == len(set(ids)) == 6
    assert all(
        record["municipality_key"] == "sendai-city" for record in catalog["records"]
    )


def test_selection_rule_is_listing_order_by_group() -> None:
    selection = load(SELECTION_PATH)
    assert selection["municipality_id"] == MID
    assert selection["issue"] == 878
    assert selection["population"]["fiscal_year"] == 2025
    # The population is the implementation plan 2024-2026 framework:
    # 9 groups (8 challenge projects + city administration), 26
    # subsections and 108 projects, as printed in the plan and in the
    # self-evaluation report.
    assert selection["population"]["group_count"] == 9
    assert selection["population"]["challenge_project_count"] == 8
    assert selection["population"]["subsection_count"] == 26
    assert selection["population"]["project_count"] == 108
    assert selection["selection_rule"]["pillars"] == PILLARS
    assert "金額の大小では選ばない" in selection["selection_rule"]["description"]
    selected = selection["selections"]
    assert [item["project_id"] for item in selected] == EXPECTED_IDS
    assert [item["official_title"] for item in selected] == EXPECTED_TITLES
    assert [item["policy"] for item in selected] == EXPECTED_PARENTS
    assert [item["pillar"] for item in selected] == EXPECTED_PARENTS
    assert [item["report_number"] for item in selected] == EXPECTED_REPORT_NUMBERS
    assert selection["expansion_rule"]["total_count"] == 10


def test_registration_unit_is_the_individual_project() -> None:
    # The registration unit is the individual project (事業): the
    # city's progress management attaches its official self-evaluation
    # (◎○△×) per project sheet, with the responsible bureau/section
    # and project content. Groups carry no evaluation, and numeric
    # targets sit at the subsection level, so neither the group nor
    # the subsection is the unit that carries an official evaluation.
    selection = load(SELECTION_PATH)
    assert "登録単位は事業とした" in selection["population"]["description"]
    for packet in load(PACKETS_PATH):
        claim = next(c for c in packet["claims"] if c["field"] == "registration_unit")
        assert "事業を登録単位とした" in claim["statement"]
        assert "公式評価が付く最も小さい単位が事業である" in claim["statement"]


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
        # The sheets print the responsible bureau per project.
        assert record["responsible_department"] == item["department"]
        assert record["municipality_id"] == MID
        assert record["fiscal_year"] == 2025
        assert record["review_status"] == "reviewed"
        # Stage 3 of the Miyagi cluster has not run yet, so no promise
        # links are registered at this stage.
        assert record["related_promise_ids"] == []
    areas = [projects[pid]["policy_area"] for pid in EXPECTED_IDS]
    assert areas == EXPECTED_POLICY_AREAS
    departments = [projects[pid]["responsible_department"] for pid in EXPECTED_IDS]
    assert departments == EXPECTED_DEPARTMENTS


def test_budget_amounts_are_explicitly_unregistered() -> None:
    # Sendai publishes no per-project amounts: neither the
    # implementation plan (which contains no "事業費" entry at all)
    # nor the self-evaluation sheets print amounts, so amounts stay
    # null instead of 0.
    for record in load(PROJECTS_PATH):
        assert len(record["budget_records"]) == 1
        budget = record["budget_records"][0]
        assert budget["kind"] == "initial_budget"
        assert budget["fiscal_year"] == 2025
        assert budget["amount_yen"] is None
        assert "未登録とした" in budget["note"]
        assert "0では補完しない" in budget["note"]


def test_official_evaluation_is_the_citys_self_evaluation() -> None:
    # Each record carries the city's own FY2025 self-evaluation mark
    # as printed in the report, with the report's definition and the
    # stated reason in the note; it is not a Jichi Insight rating.
    projects = {record["id"]: record for record in load(PROJECTS_PATH)}
    ratings = [projects[pid]["official_evaluation"]["rating"] for pid in EXPECTED_IDS]
    assert ratings == EXPECTED_RATINGS
    for record in projects.values():
        evaluation = record["official_evaluation"]
        assert evaluation["direction"] is None
        assert "仙台市の自己評価（令和7年度実施分）" in evaluation["note"]
        assert "Jichi Insight独自の評価ではない" in evaluation["note"]


def test_kpis_are_explicitly_unregistered() -> None:
    # Numeric targets are set per subsection (26), not per project;
    # attaching a subsection's targets to one of its projects would
    # misattribute them, so the KPI layer stays explicitly empty
    # (the Kobe pattern).
    assert load(KPIS_PATH) == []
    for record in load(PROJECTS_PATH):
        assert record["kpis"] == []
    for packet in load(PACKETS_PATH):
        claim = next(c for c in packet["claims"] if c["field"] == "kpis")
        assert "付け替え" in claim["statement"]
        assert "小分類単位で設定される" in claim["statement"]


def test_evidence_packets_are_schema_valid() -> None:
    packets = load(PACKETS_PATH)
    assert len(packets) == 10
    project_ids = {record["id"] for record in load(PROJECTS_PATH)}
    for packet in packets:
        validator("evidence_packet.schema.json").validate(packet)
        assert packet["subject_type"] == "project"
        assert packet["subject_id"] in project_ids
        assert packet["id"] == f"evidence-{packet['subject_id']}"
