import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
HIERARCHY_PATH = ROOT / "data/entities/policy/hokkaido_policy_hierarchy.json"
EVIDENCE_PATH = (
    ROOT / "data/entities/policy/hokkaido_policy_direction_evidence_packets.json"
)
SCHEMA_PATH = ROOT / "schemas/prefecture_policy_hierarchy.schema.json"
EVIDENCE_SCHEMA_PATH = ROOT / "schemas/evidence_packet.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(schema_path: Path, value):
    validator = Draft202012Validator(
        load(schema_path),
        format_checker=FormatChecker(),
    )
    return list(validator.iter_errors(value))


def test_hokkaido_policy_hierarchy_matches_schema():
    hierarchy = load(HIERARCHY_PATH)
    assert validate(SCHEMA_PATH, hierarchy) == []


def test_hokkaido_hierarchy_preserves_three_directions_and_eighteen_fields():
    hierarchy = load(HIERARCHY_PATH)
    directions = hierarchy["directions"]

    assert [direction["display_order"] for direction in directions] == [1, 2, 3]
    assert [direction["title_original"] for direction in directions] == [
        "潜在力発揮による成長",
        "誰もが可能性を発揮できる社会と安全・安心なくらし",
        "各地域の持続的な発展",
    ]
    assert [len(direction["fields"]) for direction in directions] == [6, 6, 6]
    assert sum(len(direction["fields"]) for direction in directions) == 18
    assert all(
        [field["display_order"] for field in direction["fields"]]
        == list(range(1, 7))
        for direction in directions
    )


def test_hokkaido_policy_field_titles_preserve_official_order():
    hierarchy = load(HIERARCHY_PATH)
    fields_by_direction = [
        [field["title_original"] for field in direction["fields"]]
        for direction in hierarchy["directions"]
    ]

    assert fields_by_direction == [
        [
            "食",
            "観光",
            "ゼロカーボン",
            "デジタル",
            "ものづくり・成長分野",
            "産業活性化・業種横断分野",
        ],
        [
            "子ども・子育て",
            "教育・学び",
            "医療・福祉",
            "就業・就労環境",
            "中小企業・商業",
            "安全・安心",
        ],
        [
            "地域づくり",
            "グローバル化",
            "北海道の強靱化",
            "社会経済の基盤整備",
            "自然・環境",
            "歴史・文化・スポーツ",
        ],
    ]


def test_hokkaido_plan_period_preserves_approximate_end_boundary():
    hierarchy = load(HIERARCHY_PATH)

    assert hierarchy["plan_period_start"] == 2024
    assert hierarchy["plan_period_end"] is None
    assert hierarchy["plan_period_original"] == "2024（令和6）年度から概ね10年間"
    assert hierarchy["review_status"] == "reviewed"
    assert hierarchy["confidence"] == "high"
    assert hierarchy["progress_linkage_status"] == "not_linked"
    assert hierarchy["evaluation_status"] == "not_assessed"


def test_hokkaido_direction_evidence_covers_every_direction():
    hierarchy = load(HIERARCHY_PATH)
    evidence_packets = load(EVIDENCE_PATH)
    direction_ids = {direction["id"] for direction in hierarchy["directions"]}

    assert len(evidence_packets) == 3
    assert all(
        validate(EVIDENCE_SCHEMA_PATH, packet) == []
        for packet in evidence_packets
    )
    assert {packet["subject_id"] for packet in evidence_packets} == direction_ids
    assert all(packet["subject_type"] == "policy_direction" for packet in evidence_packets)
    assert all(packet["review_status"] == "reviewed" for packet in evidence_packets)
    assert all(len(packet["claims"]) == 3 for packet in evidence_packets)
    assert all(
        {claim["decision"] for claim in packet["claims"]} == {"accepted"}
        for packet in evidence_packets
    )


def test_hokkaido_hierarchy_sources_exist_and_no_evaluation_is_inferred():
    hierarchy = load(HIERARCHY_PATH)
    catalog = load(ROOT / "data/catalog/policy_sources.json")
    source_ids = {source["id"] for source in catalog["records"]}

    assert set(hierarchy["plan_source_ids"]) <= source_ids
    assert hierarchy["evaluation_status"] == "not_assessed"
    assert "score" not in hierarchy
    assert "progress_rate" not in hierarchy
