"""Issue #858: Hyogo Prefecture priority projects (stage 2).

The registration unit is the numbered policy item of the third-term
Hyogo Regional Creation Strategy. The prefecture publishes no per-item
budget total (the action plans price individual main projects only),
no per-item rating (the A-D achievement grades attach to indicators),
and no per-item indicators (the 187 indicators are set per direction),
so amounts, official_evaluation and KPIs stay unregistered with the
reasons recorded in the evidence packets.
"""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
MID = "jp-local-280003"
BASE = ROOT / "data" / "reviewed" / "hyogo-prefecture"


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
    # Stage 2 registered no promise links; stage 3 (Issue #862)
    # connected six governor promises to four of the series, and
    # the reverse links are pinned here (the forward direction is
    # pinned by the stage-3 registration test).
    expected_links = {
        "jp-local-280003-project-2025-next-generation-education": [
            "jp-local-280003-executive-2024-11-17-promise-001",
            "jp-local-280003-executive-2024-11-17-promise-002",
            "jp-local-280003-executive-2024-11-17-promise-004",
        ],
        "jp-local-280003-project-2025-educational-environment": [
            "jp-local-280003-executive-2024-11-17-promise-001",
            "jp-local-280003-executive-2024-11-17-promise-003",
        ],
        "jp-local-280003-project-2025-marriage-support": [
            "jp-local-280003-executive-2024-11-17-promise-005",
        ],
        "jp-local-280003-project-2025-local-industry-development": [
            "jp-local-280003-executive-2024-11-17-promise-009",
        ],
    }
    for project in projects:
        assert project["municipality_id"] == MID
        assert project["fiscal_year"] == 2025
        assert project["review_status"] == "reviewed"
        assert project["related_promise_ids"] == expected_links.get(project["id"], [])


def test_selection_catalog_covers_population() -> None:
    catalog = _load(ROOT / "data" / "catalog" / "hyogo_priority_project_selection.json")
    assert catalog["population"]["project_count"] == 66
    codes = [s["measure_code"] for s in catalog["selections"]]
    assert codes == [
        "1-多様な学びの充実-1",
        "2-セーフティネットの構築-1",
        "3-多様性を尊重する社会づくり-1",
        "4-移住・定住の促進-1",
        "5-地域資源の維持・発展-1",
        "6-新たな産業の創出-1",
        "7-出会いから子育てへの支援-1",
        "8-生活機能の維持確保-1",
        "1-多様な学びの充実-2",
        "2-セーフティネットの構築-2",
    ]
    projects = _load(BASE / "projects.json")
    assert {s["project_id"] for s in catalog["selections"]} == {p["id"] for p in projects}
    assert {s["series_id"] for s in catalog["selections"]} == {p["series_id"] for p in projects}


def test_amounts_evaluation_and_kpis_absent() -> None:
    projects = _load(BASE / "projects.json")
    for project in projects:
        assert project["official_evaluation"] is None
        assert project["kpis"] == []
        assert len(project["budget_records"]) == 1
        record = project["budget_records"][0]
        assert record["kind"] == "initial_budget"
        assert record["fiscal_year"] == 2025
        assert record["amount_yen"] is None
        assert "公表していない" in record["note"]
    assert _load(BASE / "project_kpis.json") == []


def test_evidence_packets_cover_projects() -> None:
    packets = _load(BASE / "project_evidence_packets.json")
    schema = _schema("evidence_packet.schema.json")
    for packet in packets:
        jsonschema.validate(packet, schema)
    projects = _load(BASE / "projects.json")
    assert {p["subject_id"] for p in packets} == {p["id"] for p in projects}
    for packet in packets:
        fields = {c["field"] for c in packet["claims"]}
        assert {
            "registration_unit",
            "official_title",
            "selection",
            "purpose",
            "budget_records",
            "official_evaluation",
            "kpis",
        } <= fields
        assert all(c["decision"] == "accepted" for c in packet["claims"])


def test_project_sources_catalog() -> None:
    catalog = _load(ROOT / "data" / "catalog" / "hyogo_project_sources.json")
    jsonschema.validate(catalog, _schema("source_catalog.schema.json"))
    ids = {r["id"] for r in catalog["records"]}
    assert "hyogo-pref-regional-revitalization-strategy-3rd-document" in ids
    assert "hyogo-pref-regional-revitalization-strategy-report-fy2025" in ids
    assert "hyogo-pref-regional-revitalization-strategy-action-plan-fy2026" in ids
    assert all(r["municipality_key"] == "hyogo-prefecture" for r in catalog["records"])
    projects = _load(BASE / "projects.json")
    for project in projects:
        assert set(project["sources"]) <= ids
