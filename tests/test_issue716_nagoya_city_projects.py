from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

PROJECTS_PATH = "data/reviewed/nagoya-city/projects.json"
KPIS_PATH = "data/reviewed/nagoya-city/project_kpis.json"
PACKETS_PATH = "data/reviewed/nagoya-city/project_evidence_packets.json"
SOURCES_PATH = "data/catalog/nagoya_city_project_sources.json"
SELECTION_PATH = "data/catalog/nagoya_city_priority_project_selection.json"

WOMEN = "jp-local-231002-project-2025-women-advancement-in-employment"
BARRIER_FREE = "jp-local-231002-project-2025-private-railway-station-barrier-free"
WAITLIST = "jp-local-231002-project-2025-childcare-waitlist-countermeasures"
AREA = "jp-local-231002-project-2025-area-support-nursery-schools"
BREAKER = "jp-local-231002-project-2025-seismic-breaker-installation"
SUPPORT = "jp-local-231002-project-2025-disaster-area-support-and-exchange"
SRT = "jp-local-231002-project-2025-srt-new-surface-transit"
SUMAIRU = "jp-local-231002-project-2025-kodomo-sumairu-housing-project"
SAKAE = "jp-local-231002-project-2025-sakae-district-project"
KANAYAMA = "jp-local-231002-project-2025-kanayama-station-area-project"

ROUND1_IDS = [WOMEN, WAITLIST, BREAKER, SRT, SAKAE]
ROUND2_IDS = [BARRIER_FREE, AREA, SUPPORT, SUMAIRU, KANAYAMA]

VISION1 = "都市像1 人権が尊重され、誰もがいきいきと暮らし、活躍できる都市"
VISION2 = "都市像2 安心して子育てができ、子どもや若者が豊かに育つ都市"
VISION3 = "都市像3 人が支え合い、災害に強く安心・安全に暮らせる都市"
VISION4 = "都市像4 快適な都市環境と自然が調和した都市"
VISION5 = "都市像5 魅力と活力にあふれ、世界から人や企業をひきつける、開かれた都市"


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


def test_nagoya_city_projects_match_schemas() -> None:
    assert_valid("schemas/source_catalog.schema.json", load_json(SOURCES_PATH))
    for record in load_json(PROJECTS_PATH):
        assert_valid("schemas/project.schema.json", record)
    for record in load_json(KPIS_PATH):
        assert_valid("schemas/kpi.schema.json", record)
    for packet in load_json(PACKETS_PATH):
        assert_valid("schemas/evidence_packet.schema.json", packet)


def test_selection_rule_and_population() -> None:
    selection = load_json(SELECTION_PATH)
    # The population is defined as an intersection because Nagoya City has
    # no single official priority-project list.
    assert "総合計画2028の計画掲載事業 ∩ 主な施策等一覧" in selection["population"]["description"]
    assert selection["population"]["fiscal_year"] == 2025
    assert selection["population"]["policy_count"] == 42
    assert selection["issue"] == 716
    assert selection["scope"] == "expanded"
    assert selection["expansion_rule"]["added_count"] == 5
    assert selection["expansion_rule"]["total_count"] == 10
    selections = selection["selections"]
    assert len(selections) == 10
    # Round 1 takes the first qualifying project of each of the five city
    # visions in display order; round 2 continues the same walk.
    assert [item["project_id"] for item in selections] == ROUND1_IDS + ROUND2_IDS
    pillars = [VISION1, VISION2, VISION3, VISION4, VISION5]
    assert [item["pillar"] for item in selections[:5]] == pillars
    assert [item["pillar"] for item in selections[5:]] == pillars
    projects = projects_by_id()
    for item in selections:
        record = projects[item["project_id"]]
        assert record["series_id"] == item["series_id"]
        assert record["official_title"] == item["official_title"]
        assert record["fiscal_year"] == 2025
        assert record["review_status"] == "reviewed"
    skipped = selection["skipped"]
    skipped_titles = {item["official_title"] for item in skipped}
    # Projects whose budget counterpart was partial, split across items, or
    # shared with another project stay on record as skipped.
    assert "配偶者からの暴力被害者等の支援" in skipped_titles
    assert "出会いや結婚の希望をかなえる支援" in skipped_titles
    assert "水防法改正等に伴うハザードマップ等の周知・啓発" in skipped_titles
    assert "キャッシュレス化による市バス・地下鉄の利便性の向上" in skipped_titles
    assert "民間建築物の耐震化" in skipped_titles
    assert skipped_titles.isdisjoint(
        {record["official_title"] for record in projects.values()}
    )


def test_project_budget_records_and_stage_honesty() -> None:
    projects = projects_by_id()
    expected = {
        WOMEN: 11_538_000,
        BARRIER_FREE: 332_977_000,
        WAITLIST: 1_552_115_000,
        AREA: 29_327_000,
        BREAKER: 140_940_000,
        SUPPORT: 41_192_000,
        SRT: 107_700_000,
        SUMAIRU: 32_114_000,
        SAKAE: 459_929_000,
        KANAYAMA: 204_000_000,
    }
    assert set(projects) == set(expected)
    for project_id, initial in expected.items():
        records = projects[project_id]["budget_records"]
        # Settlement amounts are not registered: no official per-project
        # settlement figures could be confirmed, and the gap is stated in
        # the evidence packets instead of being filled from other documents.
        assert [item["kind"] for item in records] == ["initial_budget"]
        record = records[0]
        assert record["amount_yen"] == initial
        assert record["fiscal_year"] == 2025
        # The amounts come from the budget-publication documents issued
        # with the initial budget proposal; the note must keep that stage
        # explicit and never claim enacted figures.
        assert "予算案段階の公表資料" in record["note"]
        assert "成立値とは扱わない" in record["note"]
    # The waiting-list countermeasure amount is limited by the source
    # itself to new facility development; the note must keep that scope.
    waitlist_note = projects[WAITLIST]["budget_records"][0]["note"]
    assert "新たな整備費等" in waitlist_note
    assert "保育士確保支援事業等の額は含まない" in waitlist_note


def test_kpi_baseline_target_actual_are_separated() -> None:
    kpis = {record["id"]: record for record in load_json(KPIS_PATH)}
    assert len(kpis) == 10
    for record in kpis.values():
        project = projects_by_id()[record["project_id"]]
        assert record["review_status"] == "reviewed"
        assert record["causality_note"]
        embedded = {item["name"]: item for item in project["kpis"]}
        summary = embedded[record["name"]]
        assert summary["baseline"] == record["baseline"]["value"]
        assert summary["target"] == record["target"]["value"]
        assert summary["actual"] == record["actuals"][0]["value"]
        assert summary["assessment"] == record["assessment"]

    women = kpis[f"{WOMEN}-kpi-women-advancement-certified-companies"]
    assert women["baseline"]["value"] == 245
    assert women["target"]["value"] == 345
    assert women["actuals"][0]["value"] == 270
    assert women["assessment"] == "in_progress"
    assert "市の達成状況はB" in women["definition"]

    waitlist = kpis[f"{WAITLIST}-kpi-childcare-waitlist-count"]
    assert waitlist["direction"] == "maintain"
    # The waiting-list count is dated April 1 of the following year in the
    # source; the printed reference dates are kept, never swapped.
    assert waitlist["baseline"] == {
        "period": "令和6年4月1日",
        "value": 0,
        "status": "available",
        "source_ids": ["nagoya-city-plan-progress-fy2025-pdf"],
    }
    assert waitlist["actuals"][0]["period"] == "令和8年4月1日"
    assert waitlist["target"]["period"] == "令和11年4月1日"
    # The FY2028 target (zero) is already met and maintained.
    assert waitlist["assessment"] == "achieved"

    srt = kpis[f"{SRT}-kpi-public-transport-convenience-share"]
    # The FY2025 actual fell below the plan-adoption value and the city
    # grades the indicator D; the record follows the city's classification.
    assert srt["baseline"]["value"] == 84.9
    assert srt["actuals"][0]["value"] == 84.7
    assert srt["target"]["value"] == 86
    assert srt["assessment"] == "not_achieved"
    assert "市の達成状況はD" in srt["definition"]

    sakae = kpis[f"{SAKAE}-kpi-major-stations-passengers"]
    # The implementation report's "FY2025 actual" column carries the FY2024
    # figure for this indicator; the periods are recorded as printed.
    assert sakae["baseline"]["value"] == 91
    assert sakae["baseline"]["period"] == "令和4年度"
    assert sakae["actuals"][0]["value"] == 98
    assert sakae["actuals"][0]["period"] == "令和6年度"
    assert sakae["target"]["value"] == 114
    assert sakae["target"]["period"] == "令和9年度"


def test_official_evaluation_is_the_citys_project_level_not_ours() -> None:
    projects = projects_by_id()
    expected_ratings = {
        WOMEN: "☆☆☆（順調に進ちょくした）",
        BARRIER_FREE: "☆☆☆☆（特に順調に進ちょくした）",
        WAITLIST: "☆☆☆（順調に進ちょくした）",
        AREA: "☆☆☆☆（特に順調に進ちょくした）",
        BREAKER: "☆☆☆（順調に進ちょくした）",
        SUPPORT: "☆☆☆☆（特に順調に進ちょくした）",
        SRT: "☆☆☆☆（特に順調に進ちょくした）",
        SUMAIRU: "☆☆☆☆（特に順調に進ちょくした）",
        SAKAE: "☆☆☆☆（特に順調に進ちょくした）",
        KANAYAMA: "☆☆☆☆（特に順調に進ちょくした）",
    }
    for project_id, rating in expected_ratings.items():
        evaluation = projects[project_id]["official_evaluation"]
        assert evaluation["rating"] == rating
        # Nagoya City publishes a per-project progress classification; the
        # note must say so and must not present the rating as our own.
        assert "事業単位" in evaluation["note"]
        assert "Jichi Insight独自の評価ではない" in evaluation["note"]
        # Nagoya mayoral promises are not registered yet (stage 3), so no
        # project claims a promise link.
        assert projects[project_id]["related_promise_ids"] == []


def test_every_project_has_an_evidence_packet_and_known_sources() -> None:
    source_ids = {record["id"] for record in load_json(SOURCES_PATH)["records"]}
    packets = {packet["subject_id"]: packet for packet in load_json(PACKETS_PATH)}
    assert set(packets) == set(projects_by_id())
    for packet in packets.values():
        assert packet["subject_type"] == "project"
        assert packet["review_status"] == "reviewed"
        for claim in packet["claims"]:
            assert set(claim["source_ids"]) <= source_ids
        # Unregistered settlement amounts stay explicit open questions.
        assert any("決算額は未登録" in question for question in packet["open_questions"])
        assert any("未登録" in question for question in packet["open_questions"])
    for record in projects_by_id().values():
        assert set(record["sources"]) <= source_ids
    for record in load_json(KPIS_PATH):
        assert set(record["sources"]) <= source_ids


def test_budget_source_availability_is_honest() -> None:
    sources = {record["id"]: record for record in load_json(SOURCES_PATH)["records"]}
    for record in sources.values():
        assert record["availability"] == "published"
        assert record["municipality_key"] == "nagoya-city"
    # The measures list is a budget-proposal-stage publication: its detail
    # pages reference the draft budget book, and the catalog says so.
    page = sources["nagoya-city-budget-measures-fy2025-page"]
    assert "予算案段階" in page["notes"]
