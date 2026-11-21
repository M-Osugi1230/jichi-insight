"""Issue #878: Miyagi Prefecture priority projects (stage 2).

The registration unit is the measure (施策, the eighteen 取組) of the
Shin-Miyagi Future Vision, because the prefecture's policy-evaluation
system publishes a measure evaluation — rating and target-indicator
achievement — for each measure every year. Amounts follow the
published form: the FY2025 evaluation printed each measure's FY2024
settlement total, while the FY2026 evaluation prints no per-measure
total, so FY2025 amounts stay unregistered. FY2025 indicator actuals
are graph-only in the FY2026 evaluation book and stay unregistered;
the prefecture's A-D achievement grades are converted to the
registration assessment scale and the published rates are quoted in
each detailed KPI's definition.
"""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
MID = "jp-local-040002"
BASE = ROOT / "data" / "reviewed" / "miyagi-prefecture"

EXPECTED_RATINGS = {
    "jp-local-040002-project-2025-academia-industry-new-industry": "おおむね順調",
    "jp-local-040002-project-2025-social-participation": "おおむね順調",
    "jp-local-040002-project-2025-health-medical-care-sustainability": "おおむね順調",
    "jp-local-040002-project-2025-disaster-risk-reduction": "おおむね順調",
    "jp-local-040002-project-2025-industrial-human-resources": "おおむね順調",
    "jp-local-040002-project-2025-tourism-commerce-promotion": "順調",
    "jp-local-040002-project-2025-industrial-infrastructure": "順調",
    "jp-local-040002-project-2025-child-rearing-support-environment": "やや遅れている",
    "jp-local-040002-project-2025-future-ready-education-skills": "やや遅れている",
    "jp-local-040002-project-2025-low-environmental-impact-society": "やや遅れている",
}
EXPECTED_KPI_COUNTS = {
    "jp-local-040002-project-2025-academia-industry-new-industry": 6,
    "jp-local-040002-project-2025-industrial-human-resources": 10,
    "jp-local-040002-project-2025-child-rearing-support-environment": 6,
    "jp-local-040002-project-2025-future-ready-education-skills": 19,
    "jp-local-040002-project-2025-social-participation": 9,
    "jp-local-040002-project-2025-health-medical-care-sustainability": 9,
    "jp-local-040002-project-2025-low-environmental-impact-society": 7,
    "jp-local-040002-project-2025-disaster-risk-reduction": 7,
    "jp-local-040002-project-2025-tourism-commerce-promotion": 5,
    "jp-local-040002-project-2025-industrial-infrastructure": 7,
}
EXPECTED_FY2024_SETTLEMENTS = {
    "jp-local-040002-project-2025-academia-industry-new-industry": 5243993000,
    "jp-local-040002-project-2025-tourism-commerce-promotion": 2499149000,
    "jp-local-040002-project-2025-industrial-human-resources": 106591111000,
    "jp-local-040002-project-2025-industrial-infrastructure": 20372324000,
    "jp-local-040002-project-2025-child-rearing-support-environment": 5662236000,
    "jp-local-040002-project-2025-future-ready-education-skills": 276731000,
    "jp-local-040002-project-2025-social-participation": 643535000,
    "jp-local-040002-project-2025-health-medical-care-sustainability": 1732405000,
    "jp-local-040002-project-2025-low-environmental-impact-society": 3564167000,
    "jp-local-040002-project-2025-disaster-risk-reduction": 33517882000,
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
        # Promise links arrive in stage 3 (Issue #881): the
        # semiconductor-attraction promise links to the new-industry
        # measure and the hospital-reorganisation promise to the
        # medical-care measure; all other series stay unlinked.
        expected_links = {
            "jp-local-040002-project-2025-academia-industry-new-industry": [
                "jp-local-040002-executive-2025-11-21-promise-002"
            ],
            "jp-local-040002-project-2025-health-medical-care-sustainability": [
                "jp-local-040002-executive-2025-11-21-promise-004"
            ],
        }
        assert project["related_promise_ids"] == expected_links.get(project["id"], [])
        assert project["official_evaluation"]["rating"] == EXPECTED_RATINGS[project["id"]]
        assert len(project["kpis"]) == EXPECTED_KPI_COUNTS[project["id"]]
        for kpi in project["kpis"]:
            assert kpi["baseline"] is not None
            assert kpi["target"] is not None
        # FY2025 actuals are graph-only in the FY2026 evaluation book.
        # The midterm plan (February 2026 revision) prints FY2025
        # values numerically for fifteen education indicators of
        # measure 8 only; those are registered, all others stay null.
        non_null = [k for k in project["kpis"] if k["actual"] is not None]
        if project["id"].endswith("future-ready-education-skills"):
            assert len(non_null) == 15
        else:
            assert non_null == []


def test_selection_catalog_covers_population() -> None:
    catalog = _load(ROOT / "data" / "catalog" / "miyagi_priority_project_selection.json")
    assert catalog["population"]["project_count"] == 18
    codes = [s["measure_code"] for s in catalog["selections"]]
    assert codes == [
        "施策1",
        "施策4",
        "施策6",
        "施策8",
        "施策10",
        "施策12",
        "施策15",
        "施策17",
        "施策2",
        "施策5",
    ]
    projects = _load(BASE / "projects.json")
    assert {s["project_id"] for s in catalog["selections"]} == {p["id"] for p in projects}
    assert {s["series_id"] for s in catalog["selections"]} == {p["series_id"] for p in projects}


def test_budget_records_follow_published_form() -> None:
    projects = _load(BASE / "projects.json")
    for project in projects:
        records = project["budget_records"]
        assert len(records) == 2
        fy2024, fy2025 = records
        assert fy2024["kind"] == "settlement"
        assert fy2024["fiscal_year"] == 2024
        assert fy2024["amount_yen"] == EXPECTED_FY2024_SETTLEMENTS[project["id"]]
        assert fy2025["kind"] == "settlement"
        assert fy2025["fiscal_year"] == 2025
        assert fy2025["amount_yen"] is None
        assert "施策単位の決算額合計を公表しておらず" in fy2025["note"]


def test_detailed_kpis() -> None:
    kpis = _load(BASE / "project_kpis.json")
    schema = _schema("kpi.schema.json")
    for kpi in kpis:
        jsonschema.validate(kpi, schema)
    assert len(kpis) == 85
    projects = _load(BASE / "projects.json")
    assert {k["project_id"] for k in kpis} == {p["id"] for p in projects}
    available_fy2025 = 0
    for kpi in kpis:
        fy2025 = [a for a in kpi["actuals"] if a["period"] == "令和7年度"]
        assert len(fy2025) == 1
        if fy2025[0]["status"] == "available":
            available_fy2025 += 1
            assert fy2025[0]["value"] is not None
            assert kpi["project_id"].endswith("future-ready-education-skills")
        else:
            assert fy2025[0]["status"] == "not_published"
            assert fy2025[0]["value"] is None
        assert "達成率" in kpi["definition"]
        assert "達成度は" in kpi["definition"]
    assert available_fy2025 == 15


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
            "responsible_department",
            "budget_records",
            "official_evaluation",
            "kpis",
        } <= fields
        assert all(c["decision"] == "accepted" for c in packet["claims"])


def test_project_sources_catalog() -> None:
    catalog = _load(ROOT / "data" / "catalog" / "miyagi_project_sources.json")
    jsonschema.validate(catalog, _schema("source_catalog.schema.json"))
    ids = {r["id"] for r in catalog["records"]}
    assert "miyagi-pref-future-vision" in ids
    assert "miyagi-pref-midterm-implementation-plan-2026" in ids
    assert "miyagi-pref-evaluation-system" in ids
    assert "miyagi-pref-evaluation-fy2026-book" in ids
    assert "miyagi-pref-evaluation-fy2025-book" in ids
    assert all(r["municipality_key"] == "miyagi-prefecture" for r in catalog["records"])
    projects = _load(BASE / "projects.json")
    for project in projects:
        assert set(project["sources"]) <= ids
