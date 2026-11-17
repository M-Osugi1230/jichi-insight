from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

PROJECTS_PATH = "data/reviewed/fukuoka-prefecture/projects.json"
KPIS_PATH = "data/reviewed/fukuoka-prefecture/project_kpis.json"
PACKETS_PATH = "data/reviewed/fukuoka-prefecture/project_evidence_packets.json"
SOURCES_PATH = "data/catalog/fukuoka_project_sources.json"
SELECTION_PATH = "data/catalog/fukuoka_priority_project_selection.json"

MIRAI = "jp-local-400009-project-2025-mirai-kodomo-challenge"
HITORI = "jp-local-400009-project-2025-single-parent-employment-support"
KANSHO = "jp-local-400009-project-2025-infectious-disease-prevention"
CARGO = "jp-local-400009-project-2025-kitakyushu-airport-cargo"
SEISHONEN = "jp-local-400009-project-2025-youth-international-exchange"
HATARAKI = "jp-local-400009-project-2025-work-style-improvement"
FUSHIN = "jp-local-400009-project-2025-rubella-antibody-test"
TECH = "jp-local-400009-project-2025-technology-talent"
DANSEI = "jp-local-400009-project-2025-male-childcare-leave"
YOBO = "jp-local-400009-project-2025-vaccination-revaccination"

PILLAR1 = "世界を視野に、未来を見据えて成長し、発展する"
PILLAR2 = "誰もが住み慣れたところで働き、長く元気に暮らし、子どもを安心して産み育てることができる"
PILLAR3 = "感染症や災害に負けない強靭な社会をつくる"
PILLAR4 = "将来の発展を支える基盤をつくる"


def load_json(path: str) -> Any:
    with (ROOT / path).open(encoding="utf-8") as handle:
        return json.load(handle)


def assert_valid(schema_path: str, instance: Any) -> None:
    validator = Draft202012Validator(
        load_json(schema_path),
        format_checker=FormatChecker(),
    )
    errors = list(validator.iter_errors(instance))
    assert errors == [], "; ".join(error.message for error in errors)


def projects_by_id() -> dict[str, Any]:
    return {record["id"]: record for record in load_json(PROJECTS_PATH)}


def kpis_by_id() -> dict[str, Any]:
    return {record["id"]: record for record in load_json(KPIS_PATH)}


def test_fukuoka_prefecture_projects_match_schemas() -> None:
    assert_valid("schemas/source_catalog.schema.json", load_json(SOURCES_PATH))
    for record in load_json(PROJECTS_PATH):
        assert_valid("schemas/project.schema.json", record)
    for record in load_json(KPIS_PATH):
        assert_valid("schemas/kpi.schema.json", record)
    for packet in load_json(PACKETS_PATH):
        assert_valid("schemas/evidence_packet.schema.json", packet)


def test_selection_rule_and_population() -> None:
    selection = load_json(SELECTION_PATH)
    assert selection["population"]["project_count"] == 266
    assert selection["population"]["fiscal_year"] == 2025
    assert selection["scope"] == "expanded"
    assert selection["expansion_rule"]["added_count"] == 7
    assert selection["expansion_rule"]["total_count"] == 10
    selections = selection["selections"]
    assert len(selections) == 10
    # Pilot round: one project per pillar, the first listed under the
    # pillar's first initiative in the official plan-system index.
    assert [item["evaluation_number"] for item in selections[:3]] == [46, 84, 66]
    assert [item["project_id"] for item in selections[:3]] == [MIRAI, HITORI, KANSHO]
    # Scale round: pillar 4's head project, then the next listed projects
    # of pillars 1-3 in listing order, cycling through the pillars.
    assert [item["evaluation_number"] for item in selections[3:]] == [
        19,
        47,
        104,
        67,
        128,
        105,
        68,
    ]
    assert [item["pillar"] for item in selections] == [
        PILLAR1,
        PILLAR2,
        PILLAR3,
        PILLAR4,
        PILLAR1,
        PILLAR2,
        PILLAR3,
        PILLAR1,
        PILLAR2,
        PILLAR3,
    ]
    assert all(item["selection_round"] == "scale" for item in selections[3:])
    # Projects that only appear in the policy pre-evaluation (政策事前評価)
    # are outside the 266-project population and must not be selected;
    # the skips are documented in the selection record itself.
    selected_titles = {item["official_title"] for item in selections}
    for skipped in (
        "高等専修学校における学びの継続支援事業（私立専修学校各種学校補助金）",
        "北九州空港旅客路線再生事業",
        "戦略的道路整備に向けた交通ビッグデータ分析事業",
    ):
        assert skipped not in selected_titles
    documented = selection["expansion_rule"]["description"] + "".join(
        item["selection_basis"] for item in selections
    )
    for skipped in (
        "高等専修学校における学びの継続支援事業",
        "北九州空港旅客路線再生事業",
        "戦略的道路整備に向けた交通ビッグデータ分析事業",
    ):
        assert skipped in documented
    projects = projects_by_id()
    assert len(projects) == 10
    for item in selections:
        record = projects[item["project_id"]]
        assert record["series_id"] == item["series_id"]
        assert record["official_title"] == item["official_title"]
        assert record["fiscal_year"] == 2025
        assert record["review_status"] == "reviewed"


def test_project_budget_records_and_draft_stage_honesty() -> None:
    projects = projects_by_id()
    expected = {
        MIRAI: (118_155_000, 258_445_000, 284_117_000),
        HITORI: (40_795_000, 75_866_000, 52_365_000),
        KANSHO: (65_512_000, 86_006_000, 85_963_000),
        CARGO: (270_518_000, 647_804_000, 693_500_000),
        SEISHONEN: (3_143_000, 3_820_000, 3_820_000),
        HATARAKI: (8_850_000, 3_340_000, 3_475_000),
        FUSHIN: (10_126_000, 6_156_000, 6_152_000),
        TECH: (50_394_000, 43_138_000, 67_783_000),
        DANSEI: (24_167_000, 17_557_000, None),
        YOBO: (641_000, 7_098_000, 7_004_000),
    }
    assert set(projects) == set(expected)
    for project_id, (settlement, initial, draft) in expected.items():
        records = {
            (item["kind"], item["fiscal_year"]): item
            for item in projects[project_id]["budget_records"]
        }
        assert records[("settlement", 2024)]["amount_yen"] == settlement
        assert records[("initial_budget", 2025)]["amount_yen"] == initial
        if draft is None:
            # The terminated project has no FY2026 figure in the sheet
            # (printed as "-"); no record may be fabricated for it.
            assert ("initial_budget", 2026) not in records
            continue
        assert records[("initial_budget", 2026)]["amount_yen"] == draft
        # The FY2026 figure printed in the evaluation sheets is the draft
        # budget amount (per the report's own note); the note must say so and
        # must never present it as the enacted budget.
        draft_note = records[("initial_budget", 2026)]["note"]
        assert "予算案の額" in draft_note
        assert "成立後の当初予算額とは扱わない" in draft_note


def test_kpi_baseline_target_actual_are_separated() -> None:
    kpis = kpis_by_id()
    assert len(kpis) == 13
    projects = projects_by_id()
    for record in kpis.values():
        project = projects[record["project_id"]]
        assert record["review_status"] == "reviewed"
        assert record["causality_note"]
        embedded = {item["name"]: item for item in project["kpis"]}
        summary = embedded[record["name"]]
        baseline_value = None if record["baseline"] is None else record["baseline"]["value"]
        assert summary["baseline"] == baseline_value
        assert summary["target"] == record["target"]["value"]
        assert summary["assessment"] == record["assessment"]

    mirai = kpis[f"{MIRAI}-kpi-activity-municipalities"]
    assert mirai["baseline"]["value"] == 0
    assert mirai["baseline"]["period"] == "令和4年度"
    assert mirai["target"]["value"] == 60
    assert mirai["target"]["period"] == "令和6年度"
    assert [item["value"] for item in mirai["actuals"]] == [39, 46, 49]
    assert mirai["assessment"] == "not_achieved"

    rate = kpis[f"{HITORI}-kpi-employment-rate"]
    assert rate["baseline"]["value"] == 74.7
    assert rate["baseline"]["period"] == "令和元年度"
    assert rate["target"]["value"] == 77.7
    assert [item["value"] for item in rate["actuals"]] == [62.0, 66.0, 68.4, None]
    # The FY2025 actual was still being surveyed in the source: not
    # published, never filled with an estimate.
    assert rate["actuals"][-1]["status"] == "not_published"
    assert rate["assessment"] == "not_achieved"

    placements = kpis[f"{HITORI}-kpi-job-placements"]
    assert placements["baseline"]["value"] == 903
    # The target is a five-year cumulative figure, never an annual one.
    assert placements["target"]["value"] == 5000
    assert placements["target"]["period"] == "令和4年度～令和8年度累計"
    cumulative = placements["actuals"][-1]
    assert cumulative["period"] == "令和4年度～令和6年度累計"
    assert cumulative["value"] == 2249
    annual = [item["value"] for item in placements["actuals"][:3]]
    assert annual == [603, 819, 827]
    assert sum(annual) == cumulative["value"]
    assert placements["assessment"] == "in_progress"

    for suffix in ("designated-beds", "negative-pressure-beds"):
        beds = kpis[f"{KANSHO}-kpi-{suffix}"]
        assert beds["direction"] == "maintain"
        assert beds["baseline"]["value"] == 66
        assert beds["target"]["value"] == 66
        assert [item["value"] for item in beds["actuals"]] == [66, 66, 66, 66, 66]
        assert beds["assessment"] == "achieved"


def test_scale_up_kpis() -> None:
    kpis = kpis_by_id()

    cargo = kpis[f"{CARGO}-kpi-air-cargo-volume"]
    assert cargo["baseline"]["value"] == 17_466
    assert cargo["target"]["value"] == 37_427
    assert cargo["target"]["period"] == "令和6年度"
    assert [item["value"] for item in cargo["actuals"]] == [17_466, 12_144, 36_688]
    assert cargo["assessment"] == "not_achieved"

    # The exchange participation rates have no baseline in the source and
    # several years were never conducted; nothing is filled in.
    japan = kpis[f"{SEISHONEN}-kpi-participation-rate-japan"]
    assert japan["baseline"] is None
    assert japan["target"]["value"] == 100
    assert [item["value"] for item in japan["actuals"]] == [None] * 5
    assert [item["status"] for item in japan["actuals"]] == [
        "not_applicable",
        "not_applicable",
        "not_applicable",
        "not_applicable",
        "not_published",
    ]
    china = kpis[f"{SEISHONEN}-kpi-participation-rate-china"]
    assert china["baseline"] is None
    assert [item["value"] for item in china["actuals"]] == [None, None, None, 94, None]
    assert china["assessment"] == "not_achieved"

    registrations = kpis[f"{HATARAKI}-kpi-new-registrations"]
    assert registrations["baseline"]["value"] == 244
    # The headline target is the five-year cumulative figure; the annual
    # actuals stay annual and the cumulative actual is their sum.
    assert registrations["target"]["value"] == 1500
    assert registrations["target"]["period"] == "令和4年度～令和8年度累計"
    annual = [item["value"] for item in registrations["actuals"][:4]]
    assert annual == [244, 426, 537, 132]
    assert registrations["actuals"][3]["period"] == "令和7年度（9月時点）"
    cumulative = registrations["actuals"][-1]
    assert cumulative["period"] == "令和4年度～令和6年度累計"
    assert cumulative["value"] == sum(annual[:3]) == 1207
    assert registrations["assessment"] == "in_progress"

    crs = kpis[f"{FUSHIN}-kpi-crs-cases"]
    assert crs["direction"] == "maintain"
    assert crs["baseline"]["value"] == 0
    assert crs["target"]["value"] == 0
    # The FY2025 figure in the sheet is a projection (見込), not an actual,
    # so the actuals stop at FY2024.
    assert [item["period"] for item in crs["actuals"]] == [
        "令和3年度",
        "令和4年度",
        "令和5年度",
        "令和6年度",
    ]
    assert [item["value"] for item in crs["actuals"]] == [0, 0, 0, 0]
    assert crs["assessment"] == "achieved"

    mindset = kpis[f"{TECH}-kpi-mindset-change-rate"]
    assert mindset["baseline"]["value"] == 87.8
    assert mindset["target"]["value"] == 80
    assert [item["value"] for item in mindset["actuals"]] == [87.8, 85.1, None]
    assert mindset["actuals"][-1]["status"] == "not_published"
    assert mindset["assessment"] == "achieved"

    leave = kpis[f"{DANSEI}-kpi-male-leave-rate"]
    assert leave["baseline"]["value"] == 48.4
    assert leave["target"]["value"] == 53.8
    assert leave["target"]["period"] == "令和6年度"
    assert [item["value"] for item in leave["actuals"]] == [48.4, 48.2, 59.1, None]
    assert leave["actuals"][-1]["status"] == "not_published"
    assert leave["assessment"] == "achieved"

    adopting = kpis[f"{YOBO}-kpi-adopting-municipalities"]
    assert adopting["baseline"]["value"] == 6
    assert adopting["baseline"]["period"] == "令和元年度"
    assert adopting["target"]["value"] == 60
    assert [item["value"] for item in adopting["actuals"]] == [6, 12, 26, 37, 48, 55, 57]
    assert adopting["assessment"] == "not_achieved"


def test_official_evaluation_is_the_prefectures_not_ours() -> None:
    projects = projects_by_id()
    expected_ratings = {
        MIRAI: "継続（改善）",
        HITORI: "継続（縮小）",
        KANSHO: "継続（一部改善）",
        CARGO: "継続（一部改善）",
        SEISHONEN: "継続（改善）",
        HATARAKI: "継続（一部改善）",
        FUSHIN: "継続（一部改善）",
        TECH: "継続（改善）",
        DANSEI: "終了（完了）",
        YOBO: "継続（一部改善）",
    }
    assert set(projects) == set(expected_ratings)
    for project_id, rating in expected_ratings.items():
        record = projects[project_id]
        assert record["official_evaluation"]["rating"] == rating
        expected_direction = "終了" if project_id == DANSEI else "継続"
        assert record["official_evaluation"]["direction"] == expected_direction
        assert "Jichi Insight独自の評価ではない" in record["official_evaluation"]["note"]
        # Promises are Issue #8: no fabricated links.
        assert record["related_promise_ids"] == []


def test_every_project_has_an_evidence_packet_and_known_sources() -> None:
    source_ids = {record["id"] for record in load_json(SOURCES_PATH)["records"]}
    assert "fukuoka-admin-eval-fy2025-sheets-p298-433" in source_ids
    packets = {packet["subject_id"]: packet for packet in load_json(PACKETS_PATH)}
    assert set(packets) == set(projects_by_id())
    for project_id, packet in packets.items():
        assert packet["subject_type"] == "project"
        assert packet["review_status"] == "reviewed"
        for claim in packet["claims"]:
            assert set(claim["source_ids"]) <= source_ids
        # Unregistered contract/assembly/audit links stay explicit open questions.
        assert any("未登録" in question for question in packet["open_questions"])
        if project_id == DANSEI:
            # The terminated project has no FY2026 budget figure at all.
            assert any("「－」" in question for question in packet["open_questions"])
        else:
            # The draft status of the FY2026 budget figure stays an open question.
            assert any("予算案の額" in question for question in packet["open_questions"])
    for record in projects_by_id().values():
        assert set(record["sources"]) <= source_ids
    for record in load_json(KPIS_PATH):
        assert set(record["sources"]) <= source_ids


def test_parent_policy_and_target_population_honesty() -> None:
    projects = projects_by_id()
    assert projects[MIRAI]["parent_policy"] == "次代を担う「人財」の育成"
    assert projects[HITORI]["parent_policy"] == "雇用対策の充実、魅力ある職場づくり"
    assert projects[KANSHO]["parent_policy"] == "感染症対策の推進"
    assert projects[CARGO]["parent_policy"] == "生活と産業の発展を支える社会基盤の整備"
    assert projects[SEISHONEN]["parent_policy"] == "次代を担う「人財」の育成"
    # The work-style project is cross-listed under initiatives 8, 11 and 25;
    # the sheet lists initiative 8 first, so that is the parent policy.
    assert projects[HATARAKI]["parent_policy"] == "中小企業の振興"
    assert projects[FUSHIN]["parent_policy"] == "感染症対策の推進"
    assert projects[TECH]["parent_policy"] == "次代を担う「人財」の育成"
    assert projects[DANSEI]["parent_policy"] == "雇用対策の充実、魅力ある職場づくり"
    assert projects[YOBO]["parent_policy"] == "感染症対策の推進"
    # The infectious-disease and airport-cargo sheets state no separate
    # target population; they stay null instead of being inferred.
    assert projects[KANSHO]["target_population"] is None
    assert projects[CARGO]["target_population"] is None
    assert projects[MIRAI]["target_population"] == "次代を担うこどもたち"
    assert projects[SEISHONEN]["target_population"] == "県内青少年"
