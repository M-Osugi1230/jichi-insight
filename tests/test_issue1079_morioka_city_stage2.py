from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
MID = "jp-local-032018"
SOURCES_PATH = ROOT / "data/catalog/morioka_city_project_sources.json"
SELECTION_PATH = ROOT / "data/catalog/morioka_city_priority_project_selection.json"
PROJECTS_PATH = ROOT / "data/reviewed/morioka-city/projects.json"
KPIS_PATH = ROOT / "data/reviewed/morioka-city/project_kpis.json"
PACKETS_PATH = ROOT / "data/reviewed/morioka-city/project_evidence_packets.json"

G1 = "豊かな地域資源が活力を生み出すまちづくり"
G2 = "人を育み未来を選べるまちづくり"
G3 = "人がいきいきとつながり支え合うまちづくり"
G4 = "安全・安心で快適に暮らせるまちづくり"

SLUGS = [
    "commerce-industry", "agriculture-forestry", "employment",
    "attraction-dissemination", "tourism", "history-culture",
    "children-youth", "education", "human-rights-gender", "arts-culture",
    "sports", "lifelong-learning",
    "community-welfare", "elderly-welfare", "disability-welfare",
    "livelihood-support", "health-medical", "community-activation",
    "disaster-resilience", "safe-living", "environment", "compact-city",
    "urban-infrastructure", "urban-environment", "transport-environment",
]
EXPECTED_IDS = [f"{MID}-project-2025-{s}" for s in SLUGS]

EXPECTED_TITLES = [
    "商工業の振興", "農林業の振興", "雇用対策の充実", "魅力の創造・発信",
    "観光の振興", "歴史・文化の継承",
    "子ども・若者への支援", "子どもの教育の充実", "人権尊重・男女共同参画の推進",
    "芸術文化の振興", "スポーツの推進", "生涯学習の推進",
    "地域福祉の推進", "高齢者福祉の充実", "障がい者福祉の充実",
    "生活困窮者への支援", "健康づくり・医療の充実", "地域コミュニティの維持・活性化",
    "災害に強い地域づくり", "安全・安心な暮らしの確保", "環境の保全・創造",
    "コンパクトなまちづくりの推進", "都市基盤施設の維持・強化",
    "快適な都市環境の形成", "交通環境の構築",
]

EXPECTED_PARENTS = (
    [f"基本目標1 {G1}"] * 6 + [f"基本目標2 {G2}"] * 6
    + [f"基本目標3 {G3}"] * 6 + [f"基本目標4 {G4}"] * 7
)

EXPECTED_POLICY_AREAS = [
    "industry", "agriculture", "employment", "other", "tourism", "culture",
    "childcare", "education", "other", "culture", "sports", "education",
    "welfare", "welfare", "welfare", "welfare", "health", "other",
    "disaster_prevention", "safety", "environment", "infrastructure",
    "infrastructure", "infrastructure", "transport",
]

EXPECTED_DEPARTMENTS = [
    "商工労働部", "農林部", "商工労働部", "市長公室", "交流推進部",
    "教育委員会事務局", "子ども未来部", "教育委員会事務局", "総務部",
    "交流推進部", "交流推進部", "教育委員会事務局", "保健福祉部",
    "保健福祉部", "保健福祉部", "保健福祉部", "保健福祉部", "市民部",
    "総務部", "市民部", "環境部", "都市整備部", "建設部", "都市整備部",
    "建設部",
]

EXPECTED_ACHIEVEMENT = [
    27, 43, 3, 77, 23, 35, 30, 29, 33, 49, 40, 23, 7, 99, 13, 50, 46,
    100, 19, 35, 39, 97, 8, 62, 27,
]

# 施策評価シート見出しの事業費（決算額）（千円）を円に換算したもの。
EXPECTED_BUDGET_YEN = [
    3154967000, 3230818000, 193119000, 385648000, 580932000, 576975000,
    25702931000, 8916957000, 98974000, 1003430000, 1184777000, 1264106000,
    1468682000, 34133844000, 11306181000, 8939716000, 37658993000,
    808951000, 5615626000, 295509000, 4627418000, 156512000, 12461035000,
    1958011000, 694068000,
]
# 第4章実績額表の合計とシート見出しが一致しない施策（原典内の不一致）。
# 施策番号 -> (第4章の合計（円）, 差異（千円）)
EXPECTED_BUDGET_DIFFS = {
    2: (3230819000, 1), 4: (385647000, 1), 7: (25702932000, 1),
    9: (98975000, 1), 12: (1264107000, 1), 13: (1468683000, 1),
    14: (34133845000, 1), 16: (8939715000, 1), 19: (5615627000, 1),
    20: (295511000, 2), 21: (4627417000, 1), 23: (12461034000, 1),
}

EXPECTED_KPI_COUNTS = [
    12, 8, 4, 8, 6, 2, 7, 10, 4, 5, 5, 6, 5, 7, 6, 3, 11, 2, 9, 4, 13,
    6, 7, 7, 6,
]

NOT_PUBLISHED_KPIS = {
    "市内IT産業売上高",
    "こどもまんなか応援サポーターの人数",
    "まちづくり評価アンケート調査「子育てに関する経済的な負担が軽減している」と答えた市民の割合",
    "障がい者アンケート調査「障がい福祉に関心がある」と答えた市民の割合",
}

CLAIM_FIELDS = [
    "registration_unit",
    "official_title",
    "parent_policy",
    "purpose",
    "responsible_department",
    "official_evaluation",
    "budget_records.settlement",
    "kpis",
    "review_provenance",
]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validator(name: str) -> Draft202012Validator:
    schema = load(ROOT / "schemas" / name)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def test_morioka_city_project_sources_are_schema_valid() -> None:
    catalog = load(SOURCES_PATH)
    validator("source_catalog.schema.json").validate(catalog)
    ids = [record["id"] for record in catalog["records"]]
    assert len(ids) == len(set(ids)) == 4
    assert all(
        record["municipality_key"] == "morioka-city"
        for record in catalog["records"]
    )
    assert set(ids) == {
        "morioka-city-plan-basic-concept-page",
        "morioka-city-plan-implementation-page",
        "morioka-city-plan-implementation-r8-r10",
        "morioka-city-plan-evaluation-r7",
    }


def test_selection_covers_all_policies_in_published_order() -> None:
    selection = load(SELECTION_PATH)
    assert selection["municipality_id"] == MID
    assert selection["issue"] == 1079
    assert selection["population"]["unit"] == "policy"
    assert selection["population"]["item_count"] == 25
    assert "金額の大小では選ばない" in selection["selection_rule"]
    selections = selection["selections"]
    assert [s["project_id"] for s in selections] == EXPECTED_IDS
    assert [s["official_title"] for s in selections] == EXPECTED_TITLES
    assert [s["department"] for s in selections] == EXPECTED_DEPARTMENTS
    for i, entry in enumerate(selections, start=1):
        assert f"掲載順{i}番目" in entry["selection_basis"]


def test_projects_match_selection_and_schema() -> None:
    projects = load(PROJECTS_PATH)
    assert len(projects) == 25
    assert [p["id"] for p in projects] == EXPECTED_IDS
    assert [p["official_title"] for p in projects] == EXPECTED_TITLES
    assert [p["parent_policy"] for p in projects] == EXPECTED_PARENTS
    assert [p["policy_area"] for p in projects] == EXPECTED_POLICY_AREAS
    for project in projects:
        validator("project.schema.json").validate(project)
        assert project["municipality_id"] == MID
        assert project["fiscal_year"] == 2025
        assert project["review_status"] == "reviewed"
        # 公約との接続は段階3で行う。本段階では接続しない。
        assert project["related_promise_ids"] == []
        # target_population キーの存在が必須（値は未公表のため null）。
        assert "target_population" in project
        assert project["target_population"] is None


def test_departments_and_official_evaluation_are_published_values() -> None:
    projects = load(PROJECTS_PATH)
    assert [p["responsible_department"] for p in projects] == (
        EXPECTED_DEPARTMENTS
    )
    for project, ach in zip(projects, EXPECTED_ACHIEVEMENT, strict=True):
        ev = project["official_evaluation"]
        assert ev is not None
        assert ev["rating"] == f"施策達成度 {ach}点"
        assert "Jichi Insight独自の評価ではない" in ev["note"]


def test_budget_amounts_are_published_settlement_totals() -> None:
    projects = load(PROJECTS_PATH)
    amounts = []
    for i, project in enumerate(projects, start=1):
        records = project["budget_records"]
        assert len(records) == 1
        record = records[0]
        assert record["kind"] == "settlement"
        assert record["fiscal_year"] == 2025
        assert isinstance(record["amount_yen"], int) and record["amount_yen"] > 0
        amounts.append(record["amount_yen"])
        if i in EXPECTED_BUDGET_DIFFS:
            table_yen, diff_sen = EXPECTED_BUDGET_DIFFS[i]
            assert f"{table_yen // 1000:,}千円" in record["note"]
            assert f"{diff_sen}千円の差異" in record["note"]
        else:
            assert "一致することを確認した" in record["note"]
    assert amounts == EXPECTED_BUDGET_YEN
    # シート見出しの合計は第4章の総計（166,418,185千円）と5千円差
    # （各施策の原典内差異の合計）である。
    assert sum(amounts) == 166418180000


def test_projects_carry_published_kpis_only() -> None:
    projects = load(PROJECTS_PATH)
    assert [len(p["kpis"]) for p in projects] == EXPECTED_KPI_COUNTS
    total = sum(len(p["kpis"]) for p in projects)
    assert total == 163
    for project in projects:
        for kpi in project["kpis"]:
            assert kpi["assessment"] == "not_assessable"
            if kpi["name"] in NOT_PUBLISHED_KPIS:
                assert kpi["actual"] is None
            else:
                assert kpi["actual"] is not None
    by_id = {p["id"]: p for p in projects}
    first = by_id[f"{MID}-project-2025-commerce-industry"]["kpis"]
    assert [(k["name"], k["baseline"], k["target"], k["actual"]) for k in first[:3]] == [
        ("市内総生産額　※R5実績値", 688357, 754000, 761060),
        ("法人市民税調定額", 1994, 2311, 2493),
        ("製造品出荷額等　※R6実績値", 122704, 172806, 132635),
    ]
    # 施策5・22では同一指標が2つの小施策に掲載され、原典どおり重複登録する。
    tourism = by_id[f"{MID}-project-2025-tourism"]["kpis"]
    names = [k["name"] for k in tourism]
    assert names.count("年間観光客入込数　※暫定値") == 2
    assert names.count("年間宿泊観光客数") == 2


def test_detailed_kpis_are_schema_valid_and_linked() -> None:
    kpis = load(KPIS_PATH)
    projects = load(PROJECTS_PATH)
    assert len(kpis) == 163
    project_ids = {p["id"] for p in projects}
    for kpi in kpis:
        validator("kpi.schema.json").validate(kpi)
        assert kpi["project_id"] in project_ids
        assert kpi["assessment"] == "not_assessable"
        assert kpi["baseline"]["status"] == "available"
        assert kpi["baseline"]["period"] == "当初値"
        assert kpi["target"]["status"] == "available"
        assert kpi["target"]["period"] == "令和16年度"
        assert len(kpi["actuals"]) == 1
        actual = kpi["actuals"][0]
        assert actual["period"] == "令和7年度"
        if kpi["name"] in NOT_PUBLISHED_KPIS:
            assert actual["status"] == "not_published"
            assert actual["value"] is None
            assert "未公表のため" in kpi["definition"]
        else:
            assert actual["status"] == "available"
            assert actual["value"] is not None
            assert "達成度は" in kpi["definition"]
    by_name = {k["name"]: k for k in kpis}
    # 結合セルの達成度は関係する全指標に共通値として記録する。
    assert "達成度は60点" in by_name[
        "学校内外の機関等で相談・指導を受けている不登校児童生徒の割合（小学校）"
    ]["definition"]
    assert "達成度は60点" in by_name[
        "学校内外の機関等で相談・指導を受けている不登校児童生徒の割合（中学校）"
    ]["definition"]
    assert "達成度は30点" in by_name[
        "盛岡市障がい者スポーツ大会　参加者数"
    ]["definition"]
    waste = by_name["資源率"]
    assert waste["direction"] == "increase"
    co2 = by_name["温室効果ガスの総排出量　※実績値R5"]
    assert co2["direction"] == "decrease"
    assert co2["baseline"]["value"] == 2040
    assert co2["target"]["value"] == 1083


def test_evidence_packets_are_schema_valid_with_full_claims() -> None:
    packets = load(PACKETS_PATH)
    projects = load(PROJECTS_PATH)
    assert len(packets) == 25
    assert [p["subject_id"] for p in packets] == [p["id"] for p in projects]
    for packet in packets:
        validator("evidence_packet.schema.json").validate(packet)
        assert packet["id"] == f"evidence-{packet['subject_id']}"
        assert packet["subject_type"] == "project"
        assert packet["review_status"] == "reviewed"
        assert [c["field"] for c in packet["claims"]] == CLAIM_FIELDS
        assert all(c["decision"] == "accepted" for c in packet["claims"])
    first = packets[0]
    prov = first["claims"][-1]
    # レビュー委任の経緯が証拠パケットに明記されていること。
    assert prov["field"] == "review_provenance"
    assert "2026年11月15日にClaudeへ委任" in prov["statement"]
    assert "所有者本人のレビューとしては記録しない" in prov["statement"]
