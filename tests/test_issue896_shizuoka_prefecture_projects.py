"""Issue #896: Shizuoka Prefecture priority projects (stage 2).

The registration unit is the policy pillar (政策の柱, the twenty-four
middle pillars) of the Shizuoka Prefecture Comprehensive Plan
"Well-being Plan", because the prefecture's annual plan evaluation
report publishes, for each pillar, its outcome indicators with
baseline, current and target values and an A-D grade. The prefecture
publishes no per-pillar rating and no per-pillar amount, so
official_evaluation and amounts stay unregistered; the official
grades attach to the indicators and are converted to the
registration assessment scale (A=achieved, B=mostly_achieved,
C=partially_achieved, D=not_achieved, －=not_assessable).
Indicators whose current value is unpublished carry no value, with
the scheduled publication recorded in the KPI definition.
"""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
MID = "jp-local-220001"
BASE = ROOT / "data" / "reviewed" / "shizuoka-prefecture"

EXPECTED_KPI_COUNTS = {
    "jp-local-220001-project-2025-innovation-next-generation-industry": 3,
    "jp-local-220001-project-2025-decarbonized-society": 3,
    "jp-local-220001-project-2025-tourism-promotion": 2,
    "jp-local-220001-project-2025-child-centered-society": 8,
    "jp-local-220001-project-2025-medical-care-health-longevity": 9,
    "jp-local-220001-project-2025-inclusive-society": 4,
    "jp-local-220001-project-2025-disaster-prevention-mitigation": 6,
    "jp-local-220001-project-2025-administrative-fiscal-reform": 4,
    "jp-local-220001-project-2025-sme-competitiveness-growth": 5,
    "jp-local-220001-project-2025-circular-society": 2,
}
# Grade distribution per pillar as printed in the FY2026 evaluation
# report's summary tables (A / B / C / D / －).
EXPECTED_GRADES = {
    "jp-local-220001-project-2025-innovation-next-generation-industry": (0, 2, 0, 1, 0),
    "jp-local-220001-project-2025-decarbonized-society": (3, 0, 0, 0, 0),
    "jp-local-220001-project-2025-tourism-promotion": (1, 0, 0, 1, 0),
    "jp-local-220001-project-2025-child-centered-society": (3, 1, 3, 0, 1),
    "jp-local-220001-project-2025-medical-care-health-longevity": (1, 0, 1, 1, 6),
    "jp-local-220001-project-2025-inclusive-society": (1, 1, 1, 0, 1),
    "jp-local-220001-project-2025-disaster-prevention-mitigation": (4, 0, 0, 2, 0),
    "jp-local-220001-project-2025-administrative-fiscal-reform": (2, 0, 2, 0, 0),
    "jp-local-220001-project-2025-sme-competitiveness-growth": (1, 1, 1, 0, 2),
    "jp-local-220001-project-2025-circular-society": (1, 0, 0, 0, 1),
}
# Stage 3 (Issue #900) promise links per pillar, in promise order.
_TERM = "jp-local-220001-executive-2024-05-26"
EXPECTED_PROMISE_LINKS = {
    "jp-local-220001-project-2025-innovation-next-generation-industry": [
        f"{_TERM}-promise-002"
    ],
    "jp-local-220001-project-2025-decarbonized-society": [f"{_TERM}-promise-006"],
    "jp-local-220001-project-2025-tourism-promotion": [f"{_TERM}-promise-007"],
    "jp-local-220001-project-2025-child-centered-society": [f"{_TERM}-promise-003"],
    "jp-local-220001-project-2025-medical-care-health-longevity": [
        f"{_TERM}-promise-004"
    ],
    "jp-local-220001-project-2025-inclusive-society": [f"{_TERM}-promise-008"],
    "jp-local-220001-project-2025-disaster-prevention-mitigation": [
        f"{_TERM}-promise-005"
    ],
    "jp-local-220001-project-2025-administrative-fiscal-reform": [
        f"{_TERM}-promise-009"
    ],
    "jp-local-220001-project-2025-sme-competitiveness-growth": [
        f"{_TERM}-promise-002"
    ],
    "jp-local-220001-project-2025-circular-society": [f"{_TERM}-promise-006"],
}
ASSESSMENTS = [
    "achieved",
    "mostly_achieved",
    "partially_achieved",
    "not_achieved",
    "not_assessable",
]


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
        # Stage 3 (Issue #900) linked the governor's manifesto items
        # to the pillars by wording and content (low / inferred cap);
        # every pillar received at least one link.
        assert project["related_promise_ids"] == EXPECTED_PROMISE_LINKS[project["id"]]
        assert len(project["kpis"]) == EXPECTED_KPI_COUNTS[project["id"]]
        grades = tuple(
            sum(1 for k in project["kpis"] if k["assessment"] == a) for a in ASSESSMENTS
        )
        assert grades == EXPECTED_GRADES[project["id"]]
        for kpi in project["kpis"]:
            assert kpi["baseline"] is not None
            assert kpi["target"] is not None
            if kpi["assessment"] == "not_assessable":
                assert kpi["actual"] is None


def test_selection_catalog_covers_population() -> None:
    catalog = _load(ROOT / "data" / "catalog" / "shizuoka_priority_project_selection.json")
    assert catalog["population"]["project_count"] == 24
    codes = [s["pillar_code"] for s in catalog["selections"]]
    assert codes == [
        "Ⅰ-1-1",
        "Ⅰ-2-1",
        "Ⅰ-3-1",
        "Ⅱ-1-1",
        "Ⅱ-2-1",
        "Ⅱ-3-1",
        "Ⅲ-1-1",
        "行政経営",
        "Ⅰ-1-2",
        "Ⅰ-2-2",
    ]
    projects = _load(BASE / "projects.json")
    assert {s["project_id"] for s in catalog["selections"]} == {p["id"] for p in projects}
    assert {s["series_id"] for s in catalog["selections"]} == {p["series_id"] for p in projects}


def test_amounts_and_pillar_evaluation_absent() -> None:
    projects = _load(BASE / "projects.json")
    for project in projects:
        assert project["official_evaluation"] is None
        assert len(project["budget_records"]) == 1
        record = project["budget_records"][0]
        assert record["kind"] == "initial_budget"
        assert record["fiscal_year"] == 2025
        assert record["amount_yen"] is None
        assert "公表していない" in record["note"]


def test_detailed_kpis() -> None:
    kpis = _load(BASE / "project_kpis.json")
    schema = _schema("kpi.schema.json")
    for kpi in kpis:
        jsonschema.validate(kpi, schema)
    assert len(kpis) == 46
    projects = _load(BASE / "projects.json")
    assert {k["project_id"] for k in kpis} == {p["id"] for p in projects}
    not_published = 0
    for kpi in kpis:
        assert len(kpi["actuals"]) == 1
        actual = kpi["actuals"][0]
        if actual["status"] == "not_published":
            not_published += 1
            assert actual["value"] is None
            assert kpi["assessment"] == "not_assessable"
            assert "公表" in kpi["definition"]
        else:
            assert actual["status"] == "available"
            assert actual["value"] is not None
    # Eleven indicators have no published current value in the
    # FY2026 evaluation report (five biennial medical-workforce
    # indicators and six awaiting scheduled publication).
    assert not_published == 11


def test_spot_values_match_evaluation_book() -> None:
    kpis = {k["id"]: k for k in _load(BASE / "project_kpis.json")}
    startup = kpis[
        "jp-local-220001-project-2025-innovation-next-generation-industry-kpi-startup-count"
    ]
    assert startup["baseline"]["value"] == 180
    assert startup["actuals"][0]["value"] == 199
    assert startup["target"]["value"] == 260
    ghg = kpis["jp-local-220001-project-2025-decarbonized-society-kpi-ghg-emission-reduction"]
    assert ghg["baseline"]["value"] == -21.2
    assert ghg["target"]["value"] == -41.0
    retail = kpis["jp-local-220001-project-2025-sme-competitiveness-growth-kpi-retail-sales"]
    assert retail["baseline"]["value"] == 426611900
    assert retail["target"]["value"] == 495216000
    bonds = kpis[
        "jp-local-220001-project-2025-administrative-fiscal-reform-kpi-ordinary-bond-balance"
    ]
    assert bonds["baseline"]["value"] == 15846
    assert bonds["actuals"][0]["value"] == 15835
    stroke = kpis[
        "jp-local-220001-project-2025-medical-care-health-longevity-kpi-stroke-mortality"
    ]
    assert stroke["baseline"]["value"] == "男性109.3、女性64.1"
    assert stroke["target"]["value"] == "男性99.9、女性59.2"


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
    catalog = _load(ROOT / "data" / "catalog" / "shizuoka_project_sources.json")
    jsonschema.validate(catalog, _schema("source_catalog.schema.json"))
    ids = {r["id"] for r in catalog["records"]}
    assert "shizuoka-pref-comprehensive-plan-2025" in ids
    assert "shizuoka-pref-evaluation-fy2026-book" in ids
    assert "shizuoka-pref-plan-evaluation-page" in ids
    assert all(r["municipality_key"] == "shizuoka-prefecture" for r in catalog["records"])
    projects = _load(BASE / "projects.json")
    for project in projects:
        assert set(project["sources"]) <= ids
