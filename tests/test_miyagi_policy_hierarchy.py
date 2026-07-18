import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
HIERARCHY = POLICY / "miyagi_policy_hierarchy.json"
EVIDENCE = POLICY / "miyagi_policy_direction_evidence_packets.json"
SCHEMA = ROOT / "schemas/miyagi_policy_hierarchy.schema.json"
EVIDENCE_SCHEMA = ROOT / "schemas/evidence_packet.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_miyagi_hierarchy_matches_schema_and_exact_counts():
    hierarchy = load(HIERARCHY)
    validator = Draft202012Validator(
        load(SCHEMA),
        format_checker=FormatChecker(),
    )
    assert list(validator.iter_errors(hierarchy)) == []

    directions = hierarchy["directions"]
    policies = [policy for direction in directions for policy in direction["policies"]]
    measures = [measure for policy in policies for measure in policy["measures"]]

    assert len(directions) == 4
    assert len(policies) == 8
    assert len(measures) == 18
    assert len(hierarchy["recovery_support_areas"]) == 4
    assert [direction["display_order"] for direction in directions] == [1, 2, 3, 4]
    assert [policy["policy_number"] for policy in policies] == list(range(1, 9))
    assert [measure["measure_number"] for measure in measures] == list(range(1, 19))


def test_exact_direction_policy_and_measure_boundaries_are_preserved():
    hierarchy = load(HIERARCHY)
    directions = hierarchy["directions"]
    assert [direction["title_original"] for direction in directions] == [
        "富県宮城を支える県内産業の持続的な成長促進",
        "社会全体で支える宮城の子ども・子育て",
        "誰もが安心していきいきと暮らせる地域社会づくり",
        "強靭で自然と調和した県土づくり",
    ]

    policy_numbers_by_direction = [
        [policy["policy_number"] for policy in direction["policies"]]
        for direction in directions
    ]
    measure_numbers_by_direction = [
        [
            measure["measure_number"]
            for policy in direction["policies"]
            for measure in policy["measures"]
        ]
        for direction in directions
    ]
    assert policy_numbers_by_direction == [[1, 2], [3, 4], [5, 6], [7, 8]]
    assert measure_numbers_by_direction == [
        [1, 2, 3, 4, 5],
        [6, 7, 8, 9],
        [10, 11, 12, 13, 14],
        [15, 16, 17, 18],
    ]


def test_recovery_support_areas_remain_outside_eight_policy_hierarchy():
    hierarchy = load(HIERARCHY)
    recovery_titles = [
        area["title_original"] for area in hierarchy["recovery_support_areas"]
    ]
    assert recovery_titles == [
        "生活再建の状況に応じた切れ目のない支援",
        "回復途上にある産業・なりわいの下支え",
        "福島第一原発事故被害への対応",
        "復興事業のフォローアップと成果・教訓の伝承",
    ]

    policy_titles = {
        policy["title_original"]
        for direction in hierarchy["directions"]
        for policy in direction["policies"]
    }
    assert policy_titles.isdisjoint(recovery_titles)
    assert hierarchy["kpi_linkage_status"] == "positions_indexed"
    assert hierarchy["evaluation_linkage_status"] == "sources_indexed"


def test_every_direction_has_one_reviewed_evidence_packet():
    hierarchy = load(HIERARCHY)
    packets = load(EVIDENCE)
    validator = Draft202012Validator(load(EVIDENCE_SCHEMA))

    direction_ids = {direction["id"] for direction in hierarchy["directions"]}
    assert len(packets) == 4
    assert all(list(validator.iter_errors(packet)) == [] for packet in packets)
    assert {packet["subject_id"] for packet in packets} == direction_ids
    assert all(packet["review_status"] == "reviewed" for packet in packets)
    assert all(packet["open_questions"] == [] for packet in packets)
    assert all(len(packet["claims"]) == 2 for packet in packets)
