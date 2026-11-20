"""Issue #818: Saitama Prefecture priority projects (cluster 6, stage 2).

The population is the 54 field-level measures of the current five-year
plan (FY2022-FY2026), organised under twelve courses. Ten series are
selected by round-robin over the twelve courses in official listing
order, taking the first measure of each course -- the first round alone
yields ten series (measures 1, 5, 11, 16, 19, 25, 28, 32, 38, 41), so
the first measures of courses 11 and 12 are not registered. Selection
is never by amount. Each series is registered as four yearly records
(FY2022-FY2025), one per annual policy evaluation.

The evaluations publish no measure-level amounts and no per-measure
official rating, so amounts and official evaluations are null with the
reason stated; the per-indicator official judgements (annual-target
symbols) are mapped mechanically onto the KPI assessments.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

PROJECTS_PATH = "data/reviewed/saitama-prefecture/projects.json"
KPIS_PATH = "data/reviewed/saitama-prefecture/project_kpis.json"
PACKETS_PATH = "data/reviewed/saitama-prefecture/project_evidence_packets.json"
SOURCES_PATH = "data/catalog/saitama_project_sources.json"
SELECTION_PATH = "data/catalog/saitama_priority_project_selection.json"

MID = "jp-local-110001"
YEARS = [2022, 2023, 2024, 2025]
# slug -> (measure number, official title, needle, KPI count in a normal year)
SLUGS = {
    "crisis-management-disaster-prevention": (
        1, "危機管理・防災体制の再構築", "災害・危機に強い埼玉の構築", 3),
    "crime-prevention-investigation": (
        5, "防犯対策の推進と捜査活動の強化", "県民の暮らしの安心確保", 1),
    "elderly-community-care": (
        11, "地域で高齢者が安心して暮らせる社会づくり", "介護・医療体制の充実", 2),
    "declining-birthrate-measures": (
        16, "きめ細かな少子化対策の推進", "子育てに希望が持てる社会の実現", 1),
    "academic-ability-independence": (
        19, "確かな学力と自立する力の育成", "未来を創る子供たちの育成", 2),
    "lifelong-health": (
        25, "生涯を通じた健康の確保", "人生100年を見据えたシニア活躍の推進", 4),
    "employment-support-environment": (
        28, "就業支援と雇用環境の改善", "誰もが活躍し共に生きる社会の実現", 2),
    "multicultural-coexistence": (
        32, "多文化共生と国際交流のSAITAMAづくり",
        "支え合い魅力あふれる地域社会の構築", 2),
    "livable-community-development": (
        38, "住み続けられるまちづくり", "未来を見据えた社会基盤の創造", 2),
    "green-conservation-creation": (
        41, "みどりの保全と創出", "豊かな自然と共生する社会の実現", 2),
}
# KPI detail records per year: FY2024 carries both the replaced and the
# replacement indicator for measure 16, hence one extra record.
EXPECTED_KPI_TOTALS = {2022: 21, 2023: 21, 2024: 22, 2025: 21}

# Reverse links added by the stage-3 promise registration (Issue #822):
# only the FY2025 records carry them, mirroring the promise records.
_TERM = "jp-local-110001-executive-2023-08-31"
EXPECTED_PROMISE_LINKS = {
    f"{MID}-project-2025-livable-community-development": [
        f"{_TERM}-promise-001",
        f"{_TERM}-promise-002",
    ],
    f"{MID}-project-2025-employment-support-environment": [
        f"{_TERM}-promise-009",
    ],
    f"{MID}-project-2025-elderly-community-care": [
        f"{_TERM}-promise-011",
    ],
    f"{MID}-project-2025-declining-birthrate-measures": [
        f"{_TERM}-promise-012",
    ],
}


def load_json(relative: str) -> Any:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def assert_valid(schema_path: str, instance: Any) -> None:
    schema = load_json(schema_path)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(instance), key=lambda e: e.path)
    assert not errors, "\n".join(
        f"{list(error.path)}: {error.message}" for error in errors
    )


def projects() -> list[dict[str, Any]]:
    return load_json(PROJECTS_PATH)


def project(year: int, slug: str) -> dict[str, Any]:
    pid = f"{MID}-project-{year}-{slug}"
    matches = [p for p in projects() if p["id"] == pid]
    assert len(matches) == 1, pid
    return matches[0]


def kpi_of(year: int, slug: str, suffix: str) -> dict[str, Any]:
    kid = f"{MID}-project-{year}-{slug}-kpi-{suffix}"
    matches = [k for k in load_json(KPIS_PATH) if k["id"] == kid]
    assert len(matches) == 1, kid
    return matches[0]


def test_schemas() -> None:
    for record in projects():
        assert_valid("schemas/project.schema.json", record)
    for record in load_json(KPIS_PATH):
        assert_valid("schemas/kpi.schema.json", record)
    for record in load_json(PACKETS_PATH):
        assert_valid("schemas/evidence_packet.schema.json", record)
    assert_valid("schemas/source_catalog.schema.json", load_json(SOURCES_PATH))


def test_population_and_selection() -> None:
    catalog = load_json(SELECTION_PATH)
    assert catalog["municipality_id"] == MID
    assert catalog["population"]["project_count"] == 54
    assert len(catalog["selection_rule"]["pillars"]) == 12
    selections = catalog["selections"]
    assert len(selections) == 10
    assert [s["measure_number"] for s in selections] == [1, 5, 11, 16, 19, 25, 28, 32, 38, 41]
    assert [s["series_id"] for s in selections] == [
        f"{MID}-project-series-{slug}" for slug in SLUGS
    ]


def test_series_and_yearly_records() -> None:
    records = projects()
    assert len(records) == 40
    assert {p["series_id"] for p in records} == {
        f"{MID}-project-series-{slug}" for slug in SLUGS
    }
    for slug, (_number, title, needle, _count) in SLUGS.items():
        for year in YEARS:
            record = project(year, slug)
            assert record["municipality_id"] == MID
            assert record["fiscal_year"] == year
            assert record["official_title"] == title
            assert record["parent_policy"] == needle
            assert record["review_status"] == "reviewed"
            # Stage 3 (Issue #822) added the governor's promise links
            # to the FY2025 records of four series; every other record
            # stays unlinked.
            assert record["related_promise_ids"] == EXPECTED_PROMISE_LINKS.get(
                record["id"], []
            )
            assert record["sources"][0] == "saitama-pref-five-year-plan-part2"
            assert record["sources"][1] == f"saitama-pref-policy-evaluation-fy{year}"


def test_amounts_and_official_evaluation_are_null() -> None:
    for record in projects():
        assert record["official_evaluation"] is None
        assert len(record["budget_records"]) == 1
        budget = record["budget_records"][0]
        assert budget["amount_yen"] is None
        assert "0では補完しない" in budget["note"]


def test_kpi_counts() -> None:
    details = load_json(KPIS_PATH)
    assert len(details) == 85
    for year, total in EXPECTED_KPI_TOTALS.items():
        yearly = [k for k in details if f"-project-{year}-" in k["project_id"]]
        assert len(yearly) == total, year
    for slug, (_n, _t, _needle, count) in SLUGS.items():
        for year in YEARS:
            record = project(year, slug)
            expected = count + 1 if (
                slug == "declining-birthrate-measures" and year == 2024
            ) else count
            assert len(record["kpis"]) == expected, (slug, year)
            inline_names = [k["name"] for k in record["kpis"]]
            detail_names = [
                k["name"] for k in details if k["project_id"] == record["id"]
            ]
            assert inline_names == detail_names, (slug, year)


def test_indicator_replacement_measure16() -> None:
    # The total fertility rate is registered for FY2022-FY2024 only; the
    # replacement indicator appears from FY2024 and is the only one in
    # FY2025. No cross-version mapping is made.
    for year in (2022, 2023, 2024):
        kpi_of(year, "declining-birthrate-measures", "total-fertility-rate")
    fy2025_ids = [
        k["id"] for k in load_json(KPIS_PATH)
        if k["project_id"].endswith("2025-declining-birthrate-measures")
    ]
    assert fy2025_ids == [
        f"{MID}-project-2025-declining-birthrate-measures-kpi-child-friendly-society-rate"
    ]
    old = kpi_of(2024, "declining-birthrate-measures", "total-fertility-rate")
    assert old["assessment"] == "not_assessable"  # printed as "-" in FY2024
    new = kpi_of(2025, "declining-birthrate-measures", "child-friendly-society-rate")
    assert new["baseline"]["value"] == 21.1
    assert new["actuals"][0]["value"] == 18.7
    assert new["target"]["value"] == 30.0
    assert new["assessment"] == "not_achieved"


def test_spot_values() -> None:
    ind1 = kpi_of(2025, "crisis-management-disaster-prevention",
                  "voluntary-disaster-organization-rate")
    assert ind1["baseline"]["value"] == 91.4
    assert ind1["actuals"][0]["value"] == 93.2
    assert ind1["actuals"][0]["period"] == "令和6年度"
    assert ind1["target"]["value"] == 94.6
    assert ind1["assessment"] == "partially_achieved"
    assert "最終目標値は96.0（令和8年度）" in ind1["definition"]

    ind12 = kpi_of(2025, "crime-prevention-investigation",
                   "penal-code-offenses-per-thousand")
    assert ind12["direction"] == "decrease"
    assert ind12["actuals"][0]["value"] == 7.3
    assert ind12["assessment"] == "not_achieved"
    ind12_fy2022 = kpi_of(2022, "crime-prevention-investigation",
                          "penal-code-offenses-per-thousand")
    assert ind12_fy2022["actuals"][0]["value"] == 5.7
    assert ind12_fy2022["assessment"] == "achieved"

    ind22 = kpi_of(2025, "elderly-community-care",
                   "long-term-care-certification-rate-75-79")
    assert ind22["target"]["value"] == "10.9未満"
    assert ind22["actuals"][0]["value"] == 11.2

    ind57 = kpi_of(2025, "employment-support-environment", "employment-rate")
    assert ind57["actuals"][0]["value"] == 63.1
    assert ind57["assessment"] == "achieved"
    # The FY2022-FY2023 final target (61.7) differs from FY2024 onward
    # (62.2) because of the rolling revision; each year is as printed.
    assert "最終目標値は61.7（令和8年）" in kpi_of(
        2023, "employment-support-environment", "employment-rate")["definition"]
    assert "最終目標値は62.2（令和8年）" in ind57["definition"]

    ind75 = kpi_of(2025, "livable-community-development",
                   "super-city-project-municipalities")
    assert ind75["actuals"][0]["value"] == 63
    assert "最終目標値は全市町村（63）（令和8年度末）" in ind75["definition"]
    ind75_fy2022 = kpi_of(2022, "livable-community-development",
                          "super-city-project-municipalities")
    assert "最終目標値は46（令和8年度末）" in ind75_fy2022["definition"]

    # Indicators without a published baseline keep it unpublished.
    ind65 = kpi_of(2025, "multicultural-coexistence",
                   "multicultural-coexistence-supporters")
    assert ind65["baseline"]["status"] == "not_published"
    assert ind65["baseline"]["value"] is None
    assert ind65["actuals"][0]["value"] == 4467

    # Indicators without an annual target in FY2022 have no target.
    ind2 = kpi_of(2022, "crisis-management-disaster-prevention",
                  "disaster-awareness-activity-rate")
    assert "target" not in ind2
    assert ind2["assessment"] == "not_assessable"


def test_packets() -> None:
    packets = load_json(PACKETS_PATH)
    assert len(packets) == 40
    subject_ids = {p["id"] for p in projects()}
    assert {p["subject_id"] for p in packets} == subject_ids
    for packet in packets:
        fields = {c["field"] for c in packet["claims"]}
        assert {"official_title", "selection", "purpose", "budget_records",
                "official_evaluation", "kpis"} <= fields
        assert any("related_promise_ids" in q for q in packet["open_questions"])


def test_sources_catalog() -> None:
    catalog = load_json(SOURCES_PATH)
    ids = [r["id"] for r in catalog["records"]]
    assert len(ids) == len(set(ids)) == 7
    assert "saitama-pref-five-year-plan-part2" in ids
    for year in YEARS:
        assert f"saitama-pref-policy-evaluation-fy{year}" in ids
    for record in catalog["records"]:
        assert record["municipality_key"] == "saitama-prefecture"
        assert record["url"].startswith("https://www.pref.saitama.lg.jp/")
