from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
MID = "jp-local-052019"
SOURCES_PATH = ROOT / "data/catalog/akita_city_project_sources.json"
SELECTION_PATH = ROOT / "data/catalog/akita_city_priority_project_selection.json"
PROJECTS_PATH = ROOT / "data/reviewed/akita-city/projects.json"
KPIS_PATH = ROOT / "data/reviewed/akita-city/project_kpis.json"
PACKETS_PATH = ROOT / "data/reviewed/akita-city/project_evidence_packets.json"

S1 = "地域産業の活力を高め、働きがいのあるしごとの場をつくる"
S2 = "まちの魅力を高め、秋田市への新しいひとの流れをつくる"
S3 = "こども・若者の希望が叶うまちをつくる"
S4 = "誰もが健康でいきいきと暮らせるまちをつくる"
S5 = "災害に強く、安全安心で持続可能なまちをつくる"

EXPECTED_IDS = [
    "jp-local-052019-project-2026-regional-industry",
    "jp-local-052019-project-2026-new-energy-industry",
    "jp-local-052019-project-2026-sustainable-agriculture",
    "jp-local-052019-project-2026-local-employment",
    "jp-local-052019-project-2026-tourism-promotion",
    "jp-local-052019-project-2026-arts-culture-downtown",
    "jp-local-052019-project-2026-top-sports",
    "jp-local-052019-project-2026-city-promotion",
    "jp-local-052019-project-2026-migration-settlement",
    "jp-local-052019-project-2026-childcare-support",
    "jp-local-052019-project-2026-child-environment",
    "jp-local-052019-project-2026-youth-challenge",
    "jp-local-052019-project-2026-lifelong-health",
    "jp-local-052019-project-2026-senior-participation",
    "jp-local-052019-project-2026-community-life-support",
    "jp-local-052019-project-2026-disaster-resilience",
    "jp-local-052019-project-2026-public-transport",
    "jp-local-052019-project-2026-circular-zero-carbon",
]

EXPECTED_TITLES = [
    "地域の強みをいかした産業の育成・創出",
    "新エネルギー関連産業の集積・振興",
    "生産拡大と経営安定化による持続可能な農業の実現",
    "地元への就業機会の拡大と人材確保・育成支援",
    "地域資源の磨き上げと戦略的PRによる観光振興の推進",
    "芸術文化を核としたまちづくりと中心市街地活性化",
    "トップスポーツをいかした活気あるまちづくり",
    "シティプロモーションの推進と関係人口の拡大",
    "移住・定住の促進",
    "安心してこどもを生み育てられる細やかな支援",
    "こどもが健やかに育つ環境の整備",
    "若者の希望と挑戦を応援するまちの推進",
    "生涯を通じた健康づくりの推進",
    "高齢者が活躍できる場の充実と生きがいづくりの推進",
    "多様な生活支援サービスを利用できる地域づくりの推進",
    "災害に強いまちづくりの推進",
    "将来にわたり持続可能な公共交通体系の構築",
    "循環型社会の構築とゼロカーボンの推進",
]

EXPECTED_PARENTS = (
    [f"プラスの循環戦略1 {S1}"] * 4
    + [f"プラスの循環戦略2 {S2}"] * 5
    + [f"プラスの循環戦略3 {S3}"] * 3
    + [f"プラスの循環戦略4 {S4}"] * 3
    + [f"プラスの循環戦略5 {S5}"] * 3
)

EXPECTED_POLICY_AREAS = [
    "industry", "industry", "agriculture", "employment",
    "tourism", "culture", "sports", "other", "other",
    "childcare", "childcare", "other",
    "health", "welfare", "welfare",
    "disaster_prevention", "transport", "environment",
]

# 令和8年度当初予算案の概要「令和8年度のプラスの循環戦略」の
# 重点プログラム単位合計額（全会計ベース、千円）を円に換算したもの。
EXPECTED_BUDGET_YEN = [
    794904000, 352391000, 456493000, 43991000,
    273452000, 104403000, 28363000, 1561040000, 138718000,
    2285469000, 1052187000, 31135000,
    48020000, 263833000, 559100000,
    6864791000, 409637000, 97430000,
]
EXPECTED_BUDGET_TOTAL_YEN = 15365357000

CLAIM_FIELDS = [
    "registration_unit",
    "official_title",
    "parent_policy",
    "purpose",
    "responsible_department",
    "official_evaluation",
    "budget_records.initial_budget",
    "kpis",
]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validator(name: str) -> Draft202012Validator:
    schema = load(ROOT / "schemas" / name)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def test_akita_city_project_sources_are_schema_valid() -> None:
    catalog = load(SOURCES_PATH)
    validator("source_catalog.schema.json").validate(catalog)
    ids = [record["id"] for record in catalog["records"]]
    assert len(ids) == len(set(ids)) == 4
    assert all(
        record["municipality_key"] == "akita-city" for record in catalog["records"]
    )
    assert set(ids) == {
        "akita-city-plan-15th-page",
        "akita-city-plan-15th-promotion-plan",
        "akita-city-plan-15th-guidebook",
        "akita-city-budget-fy2026-overview",
    }


def test_selection_covers_all_programs_in_published_order() -> None:
    selection = load(SELECTION_PATH)
    assert selection["municipality_id"] == MID
    assert selection["issue"] == 1027
    assert selection["population"]["unit"] == "priority_program"
    assert selection["population"]["item_count"] == 18
    assert "金額の大小では選ばない" in selection["selection_rule"]
    selections = selection["selections"]
    assert [s["project_id"] for s in selections] == EXPECTED_IDS
    assert [s["official_title"] for s in selections] == EXPECTED_TITLES
    for i, entry in enumerate(selections, start=1):
        assert f"掲載順{i}番目" in entry["selection_basis"]


def test_projects_match_selection_and_schema() -> None:
    projects = load(PROJECTS_PATH)
    assert len(projects) == 18
    assert [p["id"] for p in projects] == EXPECTED_IDS
    assert [p["official_title"] for p in projects] == EXPECTED_TITLES
    assert [p["parent_policy"] for p in projects] == EXPECTED_PARENTS
    assert [p["policy_area"] for p in projects] == EXPECTED_POLICY_AREAS
    for project in projects:
        validator("project.schema.json").validate(project)
        assert project["municipality_id"] == MID
        assert project["fiscal_year"] == 2026
        assert project["review_status"] == "reviewed"
        assert project["related_promise_ids"] == []


def test_budget_amounts_are_published_program_totals() -> None:
    projects = load(PROJECTS_PATH)
    amounts = []
    for project in projects:
        records = project["budget_records"]
        assert len(records) == 1
        record = records[0]
        assert record["kind"] == "initial_budget"
        assert record["fiscal_year"] == 2026
        assert isinstance(record["amount_yen"], int) and record["amount_yen"] > 0
        assert "全会計ベース" in record["note"]
        amounts.append(record["amount_yen"])
    assert amounts == EXPECTED_BUDGET_YEN
    # 予算概要の総額（153億6,535万7千円）と一致すること。
    assert sum(amounts) == EXPECTED_BUDGET_TOTAL_YEN
    # 戦略別合計も予算概要の印字と一致すること。
    assert sum(amounts[0:4]) == 1647779000
    assert sum(amounts[4:9]) == 2105976000
    assert sum(amounts[9:12]) == 3368791000
    assert sum(amounts[12:15]) == 870953000
    assert sum(amounts[15:18]) == 7371858000


def test_official_evaluation_and_department_are_missing_not_invented() -> None:
    for project in load(PROJECTS_PATH):
        assert project["official_evaluation"] is None
        assert project["responsible_department"] is None
        assert project["target_population"] is None


def test_projects_carry_published_kpis_only() -> None:
    projects = load(PROJECTS_PATH)
    total = sum(len(p["kpis"]) for p in projects)
    assert total == 24
    for project in projects:
        for kpi in project["kpis"]:
            assert kpi["actual"] is None
            assert kpi["assessment"] == "not_assessable"
    by_id = {p["id"]: p for p in projects}
    first = by_id["jp-local-052019-project-2026-regional-industry"]["kpis"]
    assert [(k["name"], k["baseline"], k["target"]) for k in first] == [
        ("企業誘致件数", 37, 80),
        ("起業件数", 222, 378),
    ]
    energy = by_id["jp-local-052019-project-2026-new-energy-industry"]["kpis"][0]
    # 現況値は原典に「0円」と印字された公表値であり、補完ではない。
    assert energy["baseline"] == 0 and energy["target"] == 1900
    youth = by_id["jp-local-052019-project-2026-youth-challenge"]["kpis"][0]
    # 原典の「△332人」「±0人」を数値に正規化したもの。
    assert youth["baseline"] == -332 and youth["target"] == 0
    sports = by_id["jp-local-052019-project-2026-top-sports"]["kpis"][0]
    assert sports["baseline"] == "NH：4,163人、BB：4,128人、NB：725人"
    assert sports["target"] == "NH：5,000人、BB：6,000人、NB：1,000人"


def test_detailed_kpis_are_schema_valid_and_linked() -> None:
    kpis = load(KPIS_PATH)
    projects = load(PROJECTS_PATH)
    assert len(kpis) == 24
    project_ids = {p["id"] for p in projects}
    for kpi in kpis:
        validator("kpi.schema.json").validate(kpi)
        assert kpi["project_id"] in project_ids
        assert kpi["assessment"] == "not_assessable"
        assert kpi["baseline"]["status"] == "available"
        assert kpi["target"]["status"] == "available"
        assert kpi["actuals"] == [
            {
                "period": "令和8年度",
                "source_ids": [
                    "akita-city-plan-15th-page",
                    "akita-city-plan-15th-promotion-plan",
                ],
                "status": "not_published",
                "value": None,
            }
        ]
    waste = next(k for k in kpis if k["id"].endswith("household-waste-per-capita"))
    # ごみ排出量の目標時点は計画期間外の「令和16年度まで」である。
    assert waste["baseline"]["value"] == 476
    assert waste["target"]["value"] == 420
    assert waste["target"]["period"] == "令和16年度まで"
    assert waste["direction"] == "decrease"


def test_evidence_packets_are_schema_valid_with_full_claims() -> None:
    packets = load(PACKETS_PATH)
    projects = load(PROJECTS_PATH)
    assert len(packets) == 18
    assert [p["subject_id"] for p in packets] == [p["id"] for p in projects]
    for packet in packets:
        validator("evidence_packet.schema.json").validate(packet)
        assert packet["id"] == f"evidence-{packet['subject_id']}"
        assert packet["subject_type"] == "project"
        assert packet["review_status"] == "reviewed"
        assert [c["field"] for c in packet["claims"]] == CLAIM_FIELDS
        assert all(c["decision"] == "accepted" for c in packet["claims"])
    first = packets[0]
    unit_claim = first["claims"][0]
    # レビュー委任の経緯が証拠パケットに明記されていること。
    assert "2026年11月15日にClaudeへ委任" in unit_claim["statement"]
    assert "所有者本人のレビューとしては記録しない" in unit_claim["statement"]
