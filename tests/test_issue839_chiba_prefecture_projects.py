"""Issue #839: Chiba Prefecture priority projects (stage 2).

The prefecture's policy-evaluation forms (様式2 施策評価シート) publish a
per-measure budget total (September-supplemented budget basis) and a
settlement total, but no per-measure rating. Amounts are therefore
registered as budget_records and official_evaluation stays null with the
reason recorded; KPI assessments map the published FY2025 progress rate
mechanically.
"""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
MID = "jp-local-120006"
BASE = ROOT / "data" / "reviewed" / "chiba-prefecture"

TERM_ID = "jp-local-120006-executive-2025-04-05"
PROJECT = "jp-local-120006-project-2025-{}"
# Reverse links added by stage 3 (Issue #842): the governor's
# promises registered from the 2025 election bulletin that the
# stage-3 registration connected to each series.
EXPECTED_PROMISE_LINKS = {
    PROJECT.format("disaster-response-strengthening"): [
        f"{TERM_ID}-promise-001",
        f"{TERM_ID}-promise-003",
    ],
    PROJECT.format("disaster-resilient-community-development"): [
        f"{TERM_ID}-promise-001",
        f"{TERM_ID}-promise-002",
    ],
    PROJECT.format("new-industry-and-business-attraction"): [
        f"{TERM_ID}-promise-012",
        f"{TERM_ID}-promise-013",
        f"{TERM_ID}-promise-014",
    ],
    PROJECT.format("core-industry-promotion"): [
        f"{TERM_ID}-promise-015",
    ],
    PROJECT.format("growing-medical-demand"): [
        f"{TERM_ID}-promise-005",
        f"{TERM_ID}-promise-006",
    ],
    PROJECT.format("childrearing-environment"): [
        f"{TERM_ID}-promise-008",
        f"{TERM_ID}-promise-009",
    ],
    PROJECT.format("diversity-inclusive-society"): [
        f"{TERM_ID}-promise-021",
        f"{TERM_ID}-promise-022",
    ],
}


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _schema(name: str):
    return _load(ROOT / "schemas" / name)


def test_projects_validate_against_schema() -> None:
    projects = _load(BASE / "projects.json")
    schema = _schema("project.schema.json")
    for project in projects:
        jsonschema.validate(project, schema)
    assert len(projects) == 10
    for project in projects:
        assert project["municipality_id"] == MID
        assert project["fiscal_year"] == 2025
        assert project["review_status"] == "reviewed"
        # Stage 3 (Issue #842) added the governor's promise links to
        # six of the ten series; the exact links are pinned by
        # test_issue842_chiba_governor_promise_registration.py.
        assert project["related_promise_ids"] == EXPECTED_PROMISE_LINKS.get(
            project["id"], []
        )


def test_selection_catalog_covers_population() -> None:
    catalog = _load(ROOT / "data" / "catalog" / "chiba_priority_project_selection.json")
    assert catalog["population"]["project_count"] == 41
    numbers = [s["measure_number"] for s in catalog["selections"]]
    assert numbers == [1, 2, 7, 8, 19, 20, 23, 24, 30, 34]
    projects = _load(BASE / "projects.json")
    assert {s["project_id"] for s in catalog["selections"]} == {p["id"] for p in projects}
    assert {s["series_id"] for s in catalog["selections"]} == {p["series_id"] for p in projects}


def test_amounts_registered_evaluation_absent() -> None:
    projects = _load(BASE / "projects.json")
    for project in projects:
        assert project["official_evaluation"] is None
        kinds = [b["kind"] for b in project["budget_records"]]
        assert kinds == ["revised_budget", "settlement"]
        for record in project["budget_records"]:
            assert record["amount_yen"] > 0
    by_slug = {p["id"].rsplit("-", 1)[-1]: p for p in projects}
    first = next(p for p in projects if p["official_title"] == "激甚化する災害への対応力強化")
    amounts = {b["kind"]: b["amount_yen"] for b in first["budget_records"]}
    assert amounts == {"revised_budget": 69_126_528_000, "settlement": 56_532_677_000}
    assert by_slug  # keep linters quiet about the helper


def test_kpis_validate_and_assessments_follow_progress_rate() -> None:
    kpis = _load(BASE / "project_kpis.json")
    schema = _schema("kpi.schema.json")
    for kpi in kpis:
        jsonschema.validate(kpi, schema)
    assert len(kpis) == 26
    projects = {p["id"]: p for p in _load(BASE / "projects.json")}
    for kpi in kpis:
        assert kpi["project_id"] in projects
        inline = {k["name"]: k for k in projects[kpi["project_id"]]["kpis"]}
        assert inline[kpi["name"]]["assessment"] == kpi["assessment"]
        assert "機械的な対応付け" in kpi["definition"]
    by_name = {k["name"]: k for k in kpis}
    assert by_name["被災者支援システムの導入市町村数"]["assessment"] == "achieved"
    assert by_name["被災者支援システムの導入市町村数"]["actuals"][0]["value"] == 22
    assert by_name["無電柱化の事業着手した延長"]["assessment"] == "not_achieved"
    unknown = by_name["県内製造品出荷額等"]
    assert unknown["assessment"] == "not_assessable"
    assert unknown["actuals"][0]["status"] == "not_published"
    assert unknown["actuals"][0]["value"] is None


def test_evidence_packets_cover_projects() -> None:
    packets = _load(BASE / "project_evidence_packets.json")
    schema = _schema("evidence_packet.schema.json")
    for packet in packets:
        jsonschema.validate(packet, schema)
    projects = _load(BASE / "projects.json")
    assert {p["subject_id"] for p in packets} == {p["id"] for p in projects}
    for packet in packets:
        fields = {c["field"] for c in packet["claims"]}
        assert {"official_title", "selection", "purpose", "budget_records",
                "official_evaluation", "kpis"} <= fields
        assert all(c["decision"] == "accepted" for c in packet["claims"])


def test_project_sources_catalog() -> None:
    catalog = _load(ROOT / "data" / "catalog" / "chiba_project_sources.json")
    jsonschema.validate(catalog, _schema("source_catalog.schema.json"))
    ids = {r["id"] for r in catalog["records"]}
    assert "chiba-pref-comprehensive-plan-document" in ids
    assert "chiba-pref-plan-costs-fy2025" in ids
    assert all(r["municipality_key"] == "chiba-prefecture" for r in catalog["records"])
    projects = _load(BASE / "projects.json")
    for project in projects:
        assert set(project["sources"]) <= ids
