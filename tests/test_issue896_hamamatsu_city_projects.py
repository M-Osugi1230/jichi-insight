from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schemas"
SOURCES_PATH = ROOT / "data/catalog/hamamatsu_city_project_sources.json"
SELECTION_PATH = ROOT / "data/catalog/hamamatsu_city_priority_project_selection.json"
PROJECTS_PATH = ROOT / "data/reviewed/hamamatsu-city/projects.json"
KPIS_PATH = ROOT / "data/reviewed/hamamatsu-city/project_kpis.json"
PACKETS_PATH = ROOT / "data/reviewed/hamamatsu-city/project_evidence_packets.json"

MUNICIPALITY_ID = "jp-local-221309"
EVAL_PAGE = "hamamatsu-city-field-plans-2025-evaluation-page"
IMPL_PDF = "hamamatsu-city-implementation-plan-2025-pdf"
INDICATORS = "hamamatsu-city-basic-plan-indicators-page"

FIELDS = [
    "産業経済",
    "こども・教育",
    "安全・安心・快適",
    "環境・くらし",
    "健康・福祉",
    "文化・スポーツ",
    "地方自治",
]

EXPECTED_SELECTIONS = [
    ("01-01-01", "世界を市場とする産業・サービスの創造"),
    ("02-01-01", "全てのこども・若者が健やかで幸せに成長できるまちづくり"),
    ("03-01-01", "みんなの力で自然災害から生き残る"),
    ("04-01-01", "カーボンニュートラル・脱炭素社会の実現"),
    ("05-01-01", "関係機関との連携による包括的な支援の推進"),
    ("06-01-01", "文化、芸術、歴史の魅力に触れ、学び、楽しむ機会、場の提供"),
    ("07-01-01", "市民とともに歩む未来を見据えた行政運営"),
    ("01-02-01", "スタートアップ・エコシステムの構築"),
    ("02-02-01", "自分や浜松の未来を創る人づくり"),
    ("03-02-01", "市民が集う活力ある都市づくり"),
]


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_schema(name: str) -> dict:
    return load_json(SCHEMA_DIR / name)


def test_source_catalog_records_are_valid_and_complete() -> None:
    schema = load_schema("source_catalog.schema.json")
    catalog = load_json(SOURCES_PATH)
    jsonschema.validate(catalog, schema)
    sources = catalog["records"]
    assert len(sources) == 7
    for source in sources:
        assert source["municipality_key"] == "hamamatsu-city"
        assert source["organization"] == "浜松市"
        assert source["review_status"] == "reviewed"
    ids = {s["id"] for s in sources}
    assert EVAL_PAGE in ids
    assert IMPL_PDF in ids
    assert INDICATORS in ids
    assert "hamamatsu-city-implementation-evaluation-2025-report" in ids


def test_selection_rule_rotates_plan_fields_in_official_order() -> None:
    selection = load_json(SELECTION_PATH)
    assert selection["issue"] == 896
    assert selection["scope"] == "expanded"
    assert selection["selection_rule"]["pillars"] == FIELDS
    assert "金額の大小では選ばない" in selection["selection_rule"]["description"]
    selections = selection["selections"]
    assert len(selections) == 10
    assert [s["pillar"] for s in selections[:7]] == FIELDS
    assert [s["pillar"] for s in selections[7:]] == FIELDS[:3]
    assert [(s["management_number"], s["official_title"]) for s in selections] == (
        EXPECTED_SELECTIONS
    )
    for s in selections:
        assert "金額の大小では選んでいない" in s["selection_basis"]


def test_registration_unit_is_the_basic_policy() -> None:
    selection = load_json(SELECTION_PATH)
    population = selection["population"]
    assert population["field_count"] == 7
    assert population["basic_policy_count"] == 25
    assert population["policy_count"] == 125
    assert population["outcome_indicator_count"] == 38
    assert "登録単位は基本政策とした" in population["description"]
    assert "公式評価が付く単位が基本政策" in population["description"]
    packets = load_json(PACKETS_PATH)
    for packet in packets:
        unit_claims = [c for c in packet["claims"] if c["field"] == "registration_unit"]
        assert len(unit_claims) == 1
        assert "基本政策（7分野・25件）" in unit_claims[0]["statement"]
        assert "公式評価が付く単位が基本政策" in unit_claims[0]["statement"]


def test_projects_match_selection_and_use_fiscal_year_2025() -> None:
    selection = load_json(SELECTION_PATH)
    projects = load_json(PROJECTS_PATH)
    schema = load_schema("project.schema.json")
    assert len(projects) == 10
    selected = {s["project_id"]: s for s in selection["selections"]}
    assert {p["id"] for p in projects} == set(selected)
    for project in projects:
        jsonschema.validate(project, schema)
        assert project["municipality_id"] == MUNICIPALITY_ID
        assert project["fiscal_year"] == 2025
        assert project["review_status"] == "reviewed"
        assert project["series_id"] == selected[project["id"]]["series_id"]
        assert project["official_title"] == selected[project["id"]]["official_title"]
        assert project["parent_policy"] == selected[project["id"]]["pillar"]
        assert EVAL_PAGE in project["sources"]
        assert IMPL_PDF in project["sources"]


def test_amounts_are_explicitly_missing_not_zero_filled() -> None:
    projects = load_json(PROJECTS_PATH)
    for project in projects:
        assert len(project["budget_records"]) == 1
        record = project["budget_records"][0]
        assert record["kind"] == "initial_budget"
        assert record["fiscal_year"] == 2025
        assert record["amount_yen"] is None
        assert "確認できず、未登録とした" in record["note"]
        assert "0では補完しない" in record["note"]


def test_official_evaluation_is_null_and_narrative_is_preserved_in_packets() -> None:
    # The city publishes the FY2025 evaluation only as narrative text in the
    # basic-policy sheets; no rating scale exists, so the structured field
    # stays null and the narrative is preserved in the evidence packets.
    projects = load_json(PROJECTS_PATH)
    packets = {p["subject_id"]: p for p in load_json(PACKETS_PATH)}
    for project in projects:
        assert project["official_evaluation"] is None
        claims = [
            c
            for c in packets[project["id"]]["claims"]
            if c["field"] == "official_evaluation"
        ]
        assert len(claims) == 1
        statement = claims[0]["statement"]
        assert "評定区分" in statement
        assert "null とした" in statement
        assert "市の評価であり、Jichi Insight独自の評価ではない" in statement
        assert len(statement) > 300


def test_kpis_are_outcome_indicators_with_published_baseline_and_target() -> None:
    kpis = load_json(KPIS_PATH)
    schema = load_schema("kpi.schema.json")
    assert len(kpis) == 18
    projects = {p["id"]: p for p in load_json(PROJECTS_PATH)}
    for kpi in kpis:
        jsonschema.validate(kpi, schema)
        assert kpi["project_id"] in projects
        assert kpi["sources"] == [INDICATORS]
        assert kpi["assessment"] == "not_assessable"
        assert kpi["actuals"] == []
        assert kpi["baseline"]["source_ids"] == [INDICATORS]
        assert kpi["target"]["source_ids"] == [INDICATORS]
        inline = {k["name"]: k for k in projects[kpi["project_id"]]["kpis"]}
        assert kpi["name"] in inline
        assert inline[kpi["name"]]["baseline"] == kpi["baseline"]["value"]
        assert inline[kpi["name"]]["target"] == kpi["target"]["value"]
        assert inline[kpi["name"]]["assessment"] == "not_assessable"
    by_name = {k["name"]: k for k in kpis}
    gross = by_name["市内総生産額（実質）"]
    assert gross["baseline"]["value"] == 32270
    assert gross["target"]["value"] == 38170
    ghg = by_name["市域の温室効果ガス排出量"]
    assert ghg["baseline"]["value"] == 4279.4
    assert ghg["target"]["value"] == 2137.8
    waitlisted = by_name["保育所等利用待機児童数"]
    assert waitlisted["baseline"]["value"] == 0
    assert waitlisted["target"]["value"] == 0
    assert waitlisted["direction"] == "maintain"
    achievement = by_name["基本計画の成果指標全体の達成度"]
    assert achievement["baseline"]["value"] is None
    assert achievement["baseline"]["status"] == "not_published"
    assert achievement["target"]["value"] == "全指標達成"


def test_project_packets_are_schema_valid_and_traceable() -> None:
    packets = load_json(PACKETS_PATH)
    schema = load_schema("evidence_packet.schema.json")
    projects = load_json(PROJECTS_PATH)
    assert len(packets) == len(projects) == 10
    expected_fields = {
        "registration_unit",
        "official_title",
        "parent_policy",
        "purpose",
        "official_evaluation",
        "budget_records.initial_budget",
        "kpis",
        "responsible_department",
    }
    for packet in packets:
        jsonschema.validate(packet, schema)
        assert packet["subject_type"] == "project"
        assert {c["field"] for c in packet["claims"]} == expected_fields
        assert any("金額は未登録" in q for q in packet["open_questions"])
        assert any("評定区分は公表されていない" in q for q in packet["open_questions"])
