import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
HIERARCHY = ROOT / "data/entities/policy/miyagi_policy_hierarchy.json"
SCHEMA = ROOT / "schemas/prefecture_policy_measure_hierarchy.schema.json"
INVENTORY = ROOT / "data/catalog/miyagi_policy_source_inventory.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_hierarchy_matches_three_level_schema():
    validator = Draft202012Validator(
        load(SCHEMA),
        format_checker=FormatChecker(),
    )
    assert list(validator.iter_errors(load(HIERARCHY))) == []


def test_hierarchy_has_exact_four_eight_eighteen_structure():
    hierarchy = load(HIERARCHY)
    directions = hierarchy["directions"]
    policies = [
        policy
        for direction in directions
        for policy in direction["policies"]
    ]
    measures = [
        measure
        for policy in policies
        for measure in policy["measures"]
    ]

    assert [direction["display_order"] for direction in directions] == [1, 2, 3, 4]
    assert [policy["policy_number"] for policy in policies] == list(range(1, 9))
    assert [measure["measure_number"] for measure in measures] == list(range(1, 19))
    assert len({direction["id"] for direction in directions}) == 4
    assert len({policy["id"] for policy in policies}) == 8
    assert len({measure["id"] for measure in measures}) == 18


def test_exact_direction_and_policy_titles_are_preserved():
    hierarchy = load(HIERARCHY)
    directions = hierarchy["directions"]
    policies = [
        policy
        for direction in directions
        for policy in direction["policies"]
    ]

    assert [direction["title_original"] for direction in directions] == [
        "富県宮城を支える県内産業の持続的な成長促進",
        "社会全体で支える宮城の子ども・子育て",
        "誰もが安心していきいきと暮らせる地域社会づくり",
        "強靱で自然と調和した県土づくり",
    ]
    assert [policy["title_original"] for policy in policies] == [
        "全産業で，先進的取組と連携によって新しい価値をつくる",
        "産業人材の育成と産業基盤の活用によって持続的な成長の基礎をつくる",
        "子ども・子育てを社会全体で切れ目なく応援する環境をつくる",
        "社会を生き，未来を切りひらく力をはぐくむ教育環境をつくる",
        "一人ひとりがいきいきと豊かに生活できる環境をつくる",
        "健康で，安全安心に暮らせる地域をつくる",
        "自然と人間が共存共栄する社会をつくる",
        "世代を超えて安全で信頼のある強くしなやかな県土をつくる",
    ]


def test_exact_measure_titles_and_policy_membership_are_preserved():
    hierarchy = load(HIERARCHY)
    policies = {
        policy["policy_number"]: policy
        for direction in hierarchy["directions"]
        for policy in direction["policies"]
    }
    measures = {
        measure["measure_number"]: measure["title_original"]
        for policy in policies.values()
        for measure in policy["measures"]
    }

    assert [measure["measure_number"] for measure in policies[1]["measures"]] == [
        1,
        2,
        3,
    ]
    assert [measure["measure_number"] for measure in policies[2]["measures"]] == [
        4,
        5,
    ]
    assert [measure["measure_number"] for measure in policies[6]["measures"]] == [
        12,
        13,
        14,
    ]
    assert [measure["measure_number"] for measure in policies[8]["measures"]] == [
        17,
        18,
    ]
    assert measures[1].startswith("産学官連携によるものづくり産業等の発展")
    assert measures[9] == "安心して学び続けることができる教育体制の整備"
    assert measures[18] == "生活を支える社会資本の整備，維持・管理体制の充実"


def test_reconstruction_support_is_parallel_not_policy_nine():
    hierarchy = load(HIERARCHY)
    parallel = hierarchy["parallel_domains"]
    policy_numbers = [
        policy["policy_number"]
        for direction in hierarchy["directions"]
        for policy in direction["policies"]
    ]

    assert policy_numbers == list(range(1, 9))
    assert [domain["display_order"] for domain in parallel] == [1, 2, 3, 4]
    assert [domain["title_original"] for domain in parallel] == [
        "生活再建の状況に応じた切れ目のない支援",
        "回復途上にある産業・なりわいの下支え",
        "福島第一原発事故被害への対応",
        "復興事業のフォローアップと成果・教訓の伝承",
    ]
    assert all("別枠" in domain["relationship_note"] for domain in parallel)


def test_hierarchy_sources_exist_in_reviewed_inventory():
    hierarchy = load(HIERARCHY)
    inventory = load(INVENTORY)
    sources = {source["id"]: source for source in inventory["sources"]}

    assert set(hierarchy["plan_source_ids"]) <= set(sources)
    assert all(
        sources[source_id]["review_status"] == "verified"
        for source_id in hierarchy["plan_source_ids"]
    )
    assert hierarchy["plan_period_start"] == 2021
    assert hierarchy["plan_period_end"] == 2030
    assert "10か年" in hierarchy["plan_period_original"]


def test_hierarchy_does_not_infer_progress_or_evaluation():
    hierarchy = load(HIERARCHY)
    assert hierarchy["progress_linkage_status"] == "not_linked"
    assert hierarchy["evaluation_status"] == "not_assessed"
    assert hierarchy["review_status"] == "reviewed"
    assert hierarchy["confidence"] == "high"
