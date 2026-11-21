from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
MID = "jp-local-281000"
SOURCES_PATH = ROOT / "data/catalog/kobe_city_project_sources.json"
SELECTION_PATH = ROOT / "data/catalog/kobe_city_priority_project_selection.json"
PROJECTS_PATH = ROOT / "data/reviewed/kobe-city/projects.json"
KPIS_PATH = ROOT / "data/reviewed/kobe-city/project_kpis.json"
PACKETS_PATH = ROOT / "data/reviewed/kobe-city/project_evidence_packets.json"

D1 = "方向性I 世界と繋がる２つの港「新たな時代の国際都市」へ"
D2 = "方向性II 個性豊かで多様な地域の融合「日常と非日常が交わり続ける都市」へ"
D3 = "方向性III ともに乗り越え育んだ絆「いつまでも幸せを感じ、分かち合える都市」へ"
PILLARS = [D1, D2, D3]

EXPECTED_IDS = [
    "jp-local-281000-project-2026-global-talent-development",
    "jp-local-281000-project-2026-downtown-experience-and-business",
    "jp-local-281000-project-2026-inclusive-challenge-society",
    "jp-local-281000-project-2026-international-city-appeal",
    "jp-local-281000-project-2026-existing-urban-area-renewal",
    "jp-local-281000-project-2026-childrearing-work-balance",
    "jp-local-281000-project-2026-metropolitan-economic-growth",
    "jp-local-281000-project-2026-nature-for-next-generation",
    "jp-local-281000-project-2026-healthy-secure-living",
    "jp-local-281000-project-2026-connected-distinctive-townscape",
]

EXPECTED_TITLES = [
    "多様な交流を通じて世界で活躍する人材の育成を進める",
    "五感を刺激する体験と魅力的なビジネス環境を創出する都心をつくる",
    "多様な主体や団体の協働や支え合いにより、誰もが安心して夢に向かって挑戦できる社会をつくる",
    "新たな時代の国際都市にふさわしい都市の魅力をつくる",
    "ゆとりある上質な暮らしが生まれる既成市街地・ニュータウンの再生を推進する",
    "子育てと仕事の両立を支え、こどもたちの健やかな成長と豊かな感性を育む",
    "圏域経済を牽引する大都市として、神戸経済のさらなる成長と国際競争力を高める",
    "海と山を感じる豊かな自然を次代につなぐ",
    "きめ細かい多様な支援により誰もが安心して健やかに暮らせる環境をつくる",
    "個性豊かなまちなみをつなぎ日常と非日常が交わる都市をつくる",
]

# Round-robin over the three directions in listing order; direction I
# has only three basic policies, so the fourth round takes direction
# II's fourth policy.
EXPECTED_PARENTS = [D1, D2, D3, D1, D2, D3, D1, D2, D3, D2]

EXPECTED_POLICY_AREAS = [
    "education",
    "tourism",
    "other",
    "tourism",
    "housing",
    "childcare",
    "industry",
    "environment",
    "health",
    "transport",
]

# Reverse promise links added by stage 3 of the Hyogo cluster
# (Issue #862): the mayor's promises whose wording/content matches
# each basic policy, inferred and capped at low / inferred.
TERM_ID = "jp-local-281000-executive-2025-11-20"
EXPECTED_RELATED_PROMISES = {
    "jp-local-281000-project-2026-global-talent-development": ["012"],
    "jp-local-281000-project-2026-downtown-experience-and-business": [
        "015"
    ],
    "jp-local-281000-project-2026-inclusive-challenge-society": [
        "023",
        "024",
    ],
    "jp-local-281000-project-2026-international-city-appeal": ["016"],
    "jp-local-281000-project-2026-existing-urban-area-renewal": [
        "019",
        "020",
        "021",
    ],
    "jp-local-281000-project-2026-childrearing-work-balance": [
        "006",
        "007",
        "008",
        "009",
    ],
    "jp-local-281000-project-2026-metropolitan-economic-growth": [
        "011",
        "013",
        "014",
    ],
    "jp-local-281000-project-2026-nature-for-next-generation": [
        "017",
        "022",
    ],
    "jp-local-281000-project-2026-healthy-secure-living": ["010"],
    "jp-local-281000-project-2026-connected-distinctive-townscape": [
        "005",
        "018",
    ],
}

# Number of 主な施策 listed under each selected basic policy in the
# vision's structure table (reposts included, as printed).
EXPECTED_MEASURE_COUNTS = {
    "jp-local-281000-project-2026-global-talent-development": 5,
    "jp-local-281000-project-2026-downtown-experience-and-business": 5,
    "jp-local-281000-project-2026-inclusive-challenge-society": 5,
    "jp-local-281000-project-2026-international-city-appeal": 7,
    "jp-local-281000-project-2026-existing-urban-area-renewal": 4,
    "jp-local-281000-project-2026-childrearing-work-balance": 8,
    "jp-local-281000-project-2026-metropolitan-economic-growth": 12,
    "jp-local-281000-project-2026-nature-for-next-generation": 4,
    "jp-local-281000-project-2026-healthy-secure-living": 8,
    "jp-local-281000-project-2026-connected-distinctive-townscape": 6,
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validator(name: str) -> Draft202012Validator:
    schema = load(ROOT / "schemas" / name)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def test_kobe_city_project_sources_are_schema_valid() -> None:
    catalog = load(SOURCES_PATH)
    validator("source_catalog.schema.json").validate(catalog)
    ids = [record["id"] for record in catalog["records"]]
    assert len(ids) == len(set(ids)) == 5
    assert all(record["municipality_key"] == "kobe-city" for record in catalog["records"])


def test_selection_rule_is_listing_order_by_direction() -> None:
    selection = load(SELECTION_PATH)
    assert selection["municipality_id"] == MID
    assert selection["issue"] == 858
    assert selection["population"]["fiscal_year"] == 2026
    # The population is the Kobe 2030 Vision framework: 3 directions,
    # 14 basic policies and 80 listed measures (62 unique), as printed
    # in the plan's structure table and reviewed in the plan review.
    assert selection["population"]["direction_count"] == 3
    assert selection["population"]["policy_count"] == 14
    assert selection["population"]["measure_count"] == 80
    assert selection["population"]["unique_measure_count"] == 62
    assert selection["population"]["kpi_count"] == 21
    assert selection["selection_rule"]["pillars"] == PILLARS
    assert "金額の大小では選ばない" in selection["selection_rule"]["description"]
    selected = selection["selections"]
    assert [item["project_id"] for item in selected] == EXPECTED_IDS
    assert [item["official_title"] for item in selected] == EXPECTED_TITLES
    assert [item["policy"] for item in selected] == EXPECTED_PARENTS
    assert [item["pillar"] for item in selected] == EXPECTED_PARENTS
    assert selection["expansion_rule"]["total_count"] == 10


def test_registration_unit_is_the_basic_policy() -> None:
    # The registration unit is the basic policy (基本政策): it is the
    # policy unit the plan itself sets under each direction. Measures
    # carry no official evaluation, amount or KPI of their own, 18 of
    # the 80 listed measures are reposts of measures under other
    # policies, and individual projects are not fixed in the plan (they
    # are concretized in each year's budget formulation), so neither
    # the measure nor the project is a registration unit.
    selection = load(SELECTION_PATH)
    assert "登録単位は基本政策とした" in selection["population"]["description"]
    for packet in load(PACKETS_PATH):
        claim = next(c for c in packet["claims"] if c["field"] == "registration_unit")
        assert "計画の構造と進行管理の単位に照らして基本政策を登録単位とした" in claim["statement"]
        assert "重複する" in claim["statement"]


def test_selected_projects_match_records() -> None:
    projects = {record["id"]: record for record in load(PROJECTS_PATH)}
    selection = load(SELECTION_PATH)
    assert len(projects) == 10
    for item in selection["selections"]:
        record = projects[item["project_id"]]
        validator("project.schema.json").validate(record)
        assert record["series_id"] == item["series_id"]
        assert record["official_title"] == item["official_title"]
        assert record["parent_policy"] == item["policy"]
        # The plan documents print no department per basic policy, so
        # both stay explicitly null.
        assert record["responsible_department"] is None
        assert item["department"] is None
        assert record["municipality_id"] == MID
        assert record["fiscal_year"] == 2026
        assert record["review_status"] == "reviewed"
        # Stage 3 (Issue #862) registered the mayor's promises and
        # linked them forward; the reverse links mirror them exactly.
        assert record["related_promise_ids"] == [
            f"{TERM_ID}-promise-{suffix}"
            for suffix in EXPECTED_RELATED_PROMISES[record["id"]]
        ]
    areas = [projects[pid]["policy_area"] for pid in EXPECTED_IDS]
    assert areas == EXPECTED_POLICY_AREAS
    # The purpose of each record lists every measure printed under its
    # basic policy (reposts marked as printed).
    for pid, count in EXPECTED_MEASURE_COUNTS.items():
        assert projects[pid]["purpose"].count("「") >= count


def test_budget_amounts_are_explicitly_unregistered() -> None:
    # Kobe publishes no per-policy FY2026 budget: the vision prints no
    # amounts at any level and individual projects are concretized in
    # each year's budget formulation, so amounts stay null instead
    # of 0.
    for record in load(PROJECTS_PATH):
        assert len(record["budget_records"]) == 1
        budget = record["budget_records"][0]
        assert budget["kind"] == "initial_budget"
        assert budget["fiscal_year"] == 2026
        assert budget["amount_yen"] is None
        assert "未登録とした" in budget["note"]
        assert "0では補完しない" in budget["note"]
        assert "可決" in budget["note"]


def test_official_evaluation_is_explicitly_unregistered() -> None:
    # FY2026 is the first year of the Kobe 2030 Vision; the promotion
    # council has only discussed how to evaluate (2026-11-04), and no
    # completed-year evaluation has been published. The previous plan's
    # evaluations belong to a different framework and are not carried
    # over.
    for record in load(PROJECTS_PATH):
        assert record["official_evaluation"] is None
    packets = load(PACKETS_PATH)
    for packet in packets:
        joined = "".join(packet["open_questions"])
        assert "公式評価は未登録" in joined
        assert "金額は未登録" in joined


def test_kpis_are_explicitly_unregistered() -> None:
    # The 21 KPIs are set per direction (and the Well-Being objective
    # indicator for the plan as a whole), not per basic policy; one KPI
    # is even reposted across directions. Attaching a direction's KPI
    # to one of its policies would misattribute it, so the KPI layer
    # stays explicitly empty (the Chiba City pattern).
    assert load(KPIS_PATH) == []
    for record in load(PROJECTS_PATH):
        assert record["kpis"] == []
    for packet in load(PACKETS_PATH):
        claim = next(c for c in packet["claims"] if c["field"] == "kpis")
        assert "付け替えない" in claim["statement"]
        assert "方向性単位で設定され" in claim["statement"]


def test_evidence_packets_are_schema_valid() -> None:
    packets = load(PACKETS_PATH)
    assert len(packets) == 10
    project_ids = {record["id"] for record in load(PROJECTS_PATH)}
    for packet in packets:
        validator("evidence_packet.schema.json").validate(packet)
        assert packet["subject_type"] == "project"
        assert packet["subject_id"] in project_ids
        assert packet["id"] == f"evidence-{packet['subject_id']}"
