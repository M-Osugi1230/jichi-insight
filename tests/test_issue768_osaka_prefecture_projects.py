"""Issue #768: Osaka Prefecture priority projects (stage 2, cluster 4).

The population is the 52 governor priority projects listed in the second part
of the Osaka Prefecture basic policy for FY2026 (府政運営の基本方針2026).
Ten series are selected by walking the three pillars in order and, within
each pillar, taking the first listed project of each priority field. Amounts
are the sums of the component budget programs published in the official
知事重点事業一覧 (大阪府施策集), which prints no per-item total; the FY2026
general account budget itself was enacted on 2026-03-24, so the amounts are
post-enactment initial budget figures.
"""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "reviewed" / "osaka-prefecture"
SELECTION_PATH = ROOT / "data" / "catalog" / "osaka_priority_project_selection.json"
SOURCES_PATH = ROOT / "data" / "catalog" / "osaka_project_sources.json"

EXPECTED_AMOUNTS = {
    "最先端技術の実装化の加速": 50_000_000,
    "物価高騰の影響を受ける府民・事業者への支援": 51_395_409_000,
    "高等学校等授業料無償化": 13_857_593_000,
    "万博を契機とした戦略的国際交流の推進": 234_593_000,
    "災害対応力の強化": 3_158_889_000,
    "グローバル人材の育成": 574_223_000,
    "成長産業を支える人材の育成": 163_159_000,
    "SDGsの推進": 10_756_000,
    "不登校等の児童・生徒への支援の充実": 1_608_662_000,
    "大阪の魅力の磨き上げ・発信": 4_946_075_000,
}


def _load(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def _schema(name: str) -> dict:
    return _load(ROOT / "schemas" / name)


def test_osaka_project_sources_schema_and_ids() -> None:
    catalog = _load(SOURCES_PATH)
    validator = Draft202012Validator(_schema("source_catalog.schema.json"))
    errors = sorted(validator.iter_errors(catalog), key=lambda e: list(e.path))
    assert not errors, [e.message for e in errors]

    ids = [record["id"] for record in catalog["records"]]
    assert len(ids) == len(set(ids)) == 7
    assert set(ids) == {
        "osaka-pref-basic-policy-2026",
        "osaka-pref-priority-projects-fy2026-page",
        "osaka-pref-priority-projects-fy2026-pdf",
        "osaka-pref-priority-projects-fy2026-xlsx",
        "osaka-pref-budget-overview-fy2026",
        "osaka-pref-assembly-budget-vote-fy2026",
        "osaka-pref-budget-proposal-release-fy2026",
    }
    assert all(record["municipality_key"] == "osaka-prefecture" for record in catalog["records"])


def test_osaka_priority_projects_match_selection_catalog_and_schema() -> None:
    projects = _load(DATA / "projects.json")
    selection = _load(SELECTION_PATH)
    validator = Draft202012Validator(_schema("project.schema.json"))
    errors = []
    for project in projects:
        errors.extend(validator.iter_errors(project))
    assert not errors, [e.message for e in errors]

    assert selection["population"]["project_count"] == 52
    assert selection["population"]["fiscal_year"] == 2026
    assert len(selection["selections"]) == 10
    assert len(selection["skipped"]) == 42
    selected_ids = {s["project_id"] for s in selection["selections"]}
    assert {p["id"] for p in projects} == selected_ids
    assert len({p["series_id"] for p in projects}) == 10
    assert {p["municipality_id"] for p in projects} == {"jp-local-270008"}
    for entry in selection["selections"]:
        project = next(p for p in projects if p["id"] == entry["project_id"])
        assert project["official_title"] == entry["official_title"]
        assert project["parent_policy"] == entry["field"]
        assert project["series_id"] == entry["series_id"]


def test_osaka_amounts_are_fy2026_component_sums() -> None:
    projects = _load(DATA / "projects.json")
    assert {p["official_title"] for p in projects} == set(EXPECTED_AMOUNTS)
    for project in projects:
        assert project["fiscal_year"] == 2026
        assert len(project["budget_records"]) == 1
        record = project["budget_records"][0]
        assert record["kind"] == "initial_budget"
        assert record["fiscal_year"] == 2026
        assert record["amount_yen"] == EXPECTED_AMOUNTS[project["official_title"]]
        assert "構成予算事業" in record["note"]
        assert "成立後の当初予算額" in record["note"]


def test_osaka_price_rise_amount_excludes_uchisu_component() -> None:
    projects = _load(DATA / "projects.json")
    project = next(
        p for p in projects if p["official_title"] == "物価高騰の影響を受ける府民・事業者への支援"
    )
    note = project["budget_records"][0]["note"]
    assert "内数" in note
    assert "中小企業向け融資資金貸付金" in note


def test_osaka_no_official_evaluation_and_kpis_empty() -> None:
    projects = _load(DATA / "projects.json")
    for project in projects:
        assert project["official_evaluation"] is None
        assert project["kpis"] == []
        assert project["related_promise_ids"] == []
    assert _load(DATA / "project_kpis.json") == []


def test_osaka_projects_have_reviewed_evidence_packets() -> None:
    projects = _load(DATA / "projects.json")
    packets = _load(DATA / "project_evidence_packets.json")
    source_ids = {record["id"] for record in _load(SOURCES_PATH)["records"]}
    by_subject = {packet["subject_id"]: packet for packet in packets}
    assert set(by_subject) == {p["id"] for p in projects}
    for packet in packets:
        assert packet["review_status"] == "reviewed"
        fields = {claim["field"] for claim in packet["claims"]}
        assert {
            "official_title",
            "parent_policy",
            "purpose",
            "budget_records.initial_budget",
        } <= fields
        for claim in packet["claims"]:
            assert claim["source_ids"]
            assert set(claim["source_ids"]) <= source_ids
        joined = "\n".join(packet["open_questions"])
        assert "公式評価" in joined and "KPI" in joined
    price_rise = next(
        p for p in projects if p["official_title"] == "物価高騰の影響を受ける府民・事業者への支援"
    )
    joined = "\n".join(by_subject[price_rise["id"]]["open_questions"])
    assert "内数" in joined


def test_osaka_selection_rule_covers_pillars_in_order() -> None:
    selection = _load(SELECTION_PATH)
    pillars = selection["selection_rule"]["pillars"]
    assert len(pillars) == 3
    seen = [s["pillar"] for s in selection["selections"]]
    # The rotation visits pillar 1, 2, 3, then pillar 1 again, and so on.
    unique = list(dict.fromkeys(seen))
    assert len(unique) == 3
    for clean, actual in zip(pillars, unique, strict=True):
        assert clean in actual
    expected_cycle = [unique[0], unique[1], unique[2]] * 3 + [unique[0]]
    assert seen == expected_cycle
    for entry in selection["selections"]:
        assert "先頭" in entry["selection_basis"]
    for skipped in selection["skipped"]:
        assert skipped["reason"]
    reach = [s for s in selection["skipped"] if s["official_title"] == "成長の拠点となるまちづくり"]
    assert len(reach) == 1
    assert "到達" in reach[0]["reason"]
