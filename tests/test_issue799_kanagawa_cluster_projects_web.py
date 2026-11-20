"""Issue #799: Kanagawa cluster priority-project Web integration."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "apps/web"
REGISTRY = (WEB / "lib/projectRegistry.ts").read_text(encoding="utf-8")
INDEX = (WEB / "app/projects/page.tsx").read_text(encoding="utf-8")
REVIEW = (WEB / "components/ProjectReview.tsx").read_text(encoding="utf-8")
DISCOVERY = (WEB / "lib/municipalityDiscovery.ts").read_text(encoding="utf-8")
EXPORT = (ROOT / "scripts/validate_static_export.py").read_text(encoding="utf-8")


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_registry_adds_three_reviewed_areas_without_replacing_existing_ones():
    for slug in (
        "fukuoka-prefecture", "fukuoka-city", "kitakyushu-city",
        "aichi-prefecture", "nagoya-city", "toyota-city",
        "hokkaido-prefecture", "sapporo-city", "asahikawa-city",
        "osaka-prefecture", "osaka-city", "sakai-city",
        "kanagawa-prefecture", "yokohama-city", "kawasaki-city",
    ):
        assert f'"{slug}":' in REGISTRY
    for prefix in ("kanagawa", "yokohama", "kawasaki"):
        assert f"{prefix}Projects" in REGISTRY
        assert f"{prefix}Kpis" in REGISTRY
        assert f"{prefix}Evidence" in REGISTRY
        assert f"{prefix}ProjectSources" in REGISTRY
        assert f"{prefix}Selection" in REGISTRY
    assert '"kanagawa-prefecture" | "yokohama-city" | "kawasaki-city"' in REGISTRY


def test_projects_index_exposes_all_three_registered_areas_and_disclosure_units():
    assert "15自治体の Reviewed 事業レコード" in INDEX
    for slug, name in (
        ("kanagawa-prefecture", "神奈川県"),
        ("yokohama-city", "横浜市"),
        ("kawasaki-city", "川崎市"),
    ):
        assert f'"{slug}"' in REGISTRY
        assert f'name: "{name}"' in REGISTRY
    assert "area.name}｜登録事業" in INDEX
    assert "登録単位：施策群" in INDEX
    assert "億円単位の公表値（1億円未満切捨て）" in INDEX
    assert "第4期実施計画の事務事業から選定した10件" in INDEX
    assert "evidencePacket?.claims" in INDEX
    assert "金額・公式評価の公表状況と欠損理由" in INDEX


def test_kanagawa_project_amount_precision_and_official_evaluation_are_preserved():
    projects = load("data/reviewed/kanagawa-prefecture/projects.json")
    packets = load("data/reviewed/kanagawa-prefecture/project_evidence_packets.json")
    assert len(projects) == 20
    assert len({project["series_id"] for project in projects}) == 10
    assert all(project["municipality_id"] == "jp-local-140007" for project in projects)
    assert all(project["official_evaluation"] is not None for project in projects)
    assert all(
        "億円単位" in budget["note"]
        and "決算額は公表されていない" in budget["note"]
        for project in projects for budget in project["budget_records"]
    )
    assert len(packets) == len(projects)
    assert "kanagawa-prefecture" in REVIEW
    assert "1億円未満切捨て" in REVIEW


def test_yokohama_measure_group_unit_and_missing_reasons_are_visible():
    projects = load("data/reviewed/yokohama-city/projects.json")
    selection = load("data/catalog/yokohama_city_priority_project_selection.json")
    packets = load("data/reviewed/yokohama-city/project_evidence_packets.json")
    assert len(projects) == 10
    assert selection["population"]["measure_group_count"] == 33
    assert all(project["official_evaluation"] is None for project in projects)
    for project in projects:
        budget = project["budget_records"][0]
        assert budget["amount_yen"] is None
        assert "施策群単位の金額は公表していない" in budget["note"]
    for packet in packets:
        evaluation = next(
            claim for claim in packet["claims"]
            if claim["field"] == "official_evaluation"
        )
        assert "施策群単位の公式評価は公表されていない" in evaluation["statement"]
    assert "yokohama-city" in REVIEW
    assert "横浜市の登録単位は施策群です" in REVIEW


def test_kawasaki_fourth_plan_budget_and_evaluation_gaps_are_visible():
    projects = load("data/reviewed/kawasaki-city/projects.json")
    packets = load("data/reviewed/kawasaki-city/project_evidence_packets.json")
    assert len(projects) == 10
    assert all(project["official_evaluation"] is None for project in projects)
    for project in projects:
        budget = project["budget_records"][0]
        assert budget["amount_yen"] is None
        assert "未登録とした" in budget["note"]
        assert "0では補完しない" in budget["note"]
    for packet in packets:
        claims = {claim["field"]: claim["statement"] for claim in packet["claims"]}
        assert "公式評価は未登録" in claims["official_evaluation"]
        assert "未登録" in claims["budget_records.initial_budget"]
    assert "kawasaki-city" in REVIEW
    assert "第4期実施計画に対応する事業別当初予算額" in REVIEW


def test_discovery_gates_are_official_code_and_reviewed_record_scoped():
    for municipality, code in (
        ("kanagawaMunicipality", "kanagawa-prefecture"),
        ("yokohamaMunicipality", "yokohama-city"),
        ("kawasakiMunicipality", "kawasaki-city"),
    ):
        assert f"officialCode === {municipality}.official_code" in DISCOVERY
        assert f'projectRegistry["{code}"].projects.some' in DISCOVERY
        assert f"project.municipality_id === {municipality}.id" in DISCOVERY
    assert "finance: false, promises: false, assembly: false, projects: hasProjects" in DISCOVERY


def test_static_export_requires_all_cluster_detail_pages_and_scoped_copy():
    assert "def kanagawa_cluster_project_detail_files()" in EXPORT
    assert "kanagawa_cluster_project_detail_files()" in EXPORT
    assert "def validate_kanagawa_cluster_sections()" in EXPORT
    assert "validate_kanagawa_cluster_sections()" in EXPORT
    for phrase in (
        "15自治体の Reviewed 事業レコード",
        "登録単位：施策群",
        "億円単位の公表値",
        "第4期実施計画",
    ):
        assert phrase in EXPORT
