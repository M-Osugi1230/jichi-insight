from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT / "data/catalog"
REVIEWED = ROOT / "data/reviewed/chiba-city"
EVD = ROOT / "data/evidence"
IDENTITIES = CAT / "chiba_current_project_identities_field07.json"
REVIEW = REVIEWED / "current_project_work_items_field07.json"
EVIDENCE = EVD / "chiba_current_project_work_items_field07_evidence.json"
MANIFEST = CAT / "chiba_current_project_work_item_review_manifest.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_field07_source_capture_covers_all_32_identity_projects_exactly():
    identities = load(IDENTITIES)["records"]
    projects = load(REVIEW)["projects"]
    assert len(identities) == len(projects) == 32
    assert {(row["review_id"], row["project_name"]) for row in identities} == {
        (row["review_id"], row["project_name"]) for row in projects
    }


def test_field07_source_locations_are_normalized_without_losing_printed_pages():
    identities = {row["review_id"]: row for row in load(IDENTITIES)["records"]}
    review = load(REVIEW)
    assert "zero-based PDF page-index" in review["source_location_semantics"]

    for project in review["projects"]:
        identity = identities[project["review_id"]]
        assert project["measure_code"] == identity["measure_code"]
        assert project["source_location"] == identity["source_location"]
        assert project["source_printed_page"] == identity["source_printed_page"]
        page_index = int(project["source_location"].removeprefix("PDF p."))
        assert page_index == project["source_printed_page"] + 3


def test_field07_all_32_projects_are_structured_after_visual_review():
    projects = load(REVIEW)["projects"]
    assert len(projects) == 32
    assert all(
        row["parse_status"] != "pending_visual_column_confirmation" for row in projects
    )
    assert all(row["work_items"] for row in projects)


def test_field07_has_68_unique_complete_work_items():
    work_items = [
        item for project in load(REVIEW)["projects"] for item in project["work_items"]
    ]
    ids = [item["work_item_id"] for item in work_items]
    assert len(work_items) == len(ids) == len(set(ids)) == 68
    assert all(item["item_name"].strip() for item in work_items)
    assert all(item["current_text"].strip() for item in work_items)
    assert all(item["plan_text"].strip() for item in work_items)
    assert all(item["target_text"].strip() for item in work_items)


def test_field07_visual_promotions_preserve_representative_table_semantics():
    projects = {row["review_id"]: row for row in load(REVIEW)["projects"]}

    station = projects["chiba-f07-p006"]["work_items"]
    assert station[0]["current_text"] == (
        "グランドデザイン改定（案）作成 / （仮）中央公園プロムナード周辺の"
        "まちづくりビジョン（案）作成 / 社会実験"
    )
    assert station[1]["target_text"] == "実施設計完了"
    assert station[2]["plan_text"] == station[2]["target_text"] == (
        "中プロ・デザインラボの開催4回/年"
    )

    transit = projects["chiba-f07-p017"]["work_items"]
    assert transit[0]["target_text"] == (
        "生活交通バス路線維持、先行エリアでのバス路線の見直し"
    )
    assert transit[1]["current_text"] == "２種免許取得支援 50人/年"
    assert transit[5]["current_text"] == "―"
    assert transit[5]["plan_text"] == transit[5]["target_text"] == "3社"

    bicycle = projects["chiba-f07-p022"]["work_items"]
    assert bicycle[0]["plan_text"] == "46箇所"
    assert bicycle[1]["current_text"] == "自転車レーン等整備88.9km"
    assert bicycle[1]["plan_text"] == "予備設計1.8km / 詳細設計3.3km / 整備9km"
    assert bicycle[1]["target_text"] == "自転車レーン等整備97.9km"

    water = projects["chiba-f07-p029"]["work_items"][0]
    assert water["current_text"] == "― / ―"
    assert water["plan_text"] == "管網計算・実施設計 / 配水管の整備2.3km（富田町他）"
    assert water["target_text"] == "配水管の整備2.3km"

    sewer = projects["chiba-f07-p032"]["work_items"][0]
    assert sewer["current_text"] == "水処理躯体改築４箇所・移設１箇所"
    assert "沈砂池・ポンプ棟実施設計（中央処理区）" in sewer["plan_text"]
    assert sewer["target_text"].endswith("雨水滞水池・分配槽撤去２箇所")


def test_field07_existing_distance_increment_and_annual_semantics_remain_intact():
    projects = {row["review_id"]: row for row in load(REVIEW)["projects"]}
    kemigawa = projects["chiba-f07-p003"]["work_items"][0]
    special_zone = projects["chiba-f07-p024"]["work_items"][1]
    housing = projects["chiba-f07-p027"]["work_items"][0]
    sewer = projects["chiba-f07-p030"]["work_items"][0]

    assert (kemigawa["current_text"], kemigawa["plan_text"], kemigawa["target_text"]) == (
        "14,642m",
        "1,292m",
        "15,934m",
    )
    assert (
        special_zone["current_text"],
        special_zone["plan_text"],
        special_zone["target_text"],
    ) == (
        "11件",
        "３件増",
        "14件",
    )
    assert (housing["current_text"], housing["plan_text"], housing["target_text"]) == (
        "７件/年",
        "５件/年増",
        "12件/年",
    )
    assert (sewer["current_text"], sewer["plan_text"], sewer["target_text"]) == (
        "12,607ha",
        "5.0ha",
        "12,612ha",
    )


def test_field07_evidence_records_complete_visual_resolution():
    evidence = load(EVIDENCE)
    promotions = evidence["visual_confirmed_promotions"]
    assert evidence["review_status"] == "reviewed_source_capture_and_structuring_complete"
    assert evidence["structured_project_count"] == 32
    assert evidence["pending_visual_column_confirmation_project_count"] == 0
    assert evidence["structured_work_item_count"] == 68
    assert evidence["pending_visual_column_confirmation"] == []
    assert len(promotions) == 10
    assert sum(row["structured_work_item_count"] for row in promotions) == 24
    assert evidence["reconciliation"] == {
        "official_field07_project_count": 32,
        "source_capture_coverage": "32/32",
        "structured_project_coverage": "32/32",
        "structured_work_item_count": 68,
        "pending_project_count": 0,
        "cumulative_source_captured_projects": 167,
        "cumulative_structured_projects": 167,
        "cumulative_structured_work_items": 358,
        "cumulative_pending_visual_projects": 0,
    }


def test_field07_manifest_advances_visual_review_to_final_field_only():
    manifest = load(MANIFEST)
    structuring = manifest["work_item_structuring"]
    assert structuring["projects_structured"] == 179
    assert structuring["projects_pending_visual_column_confirmation"] == 10
    assert structuring["structured_work_items"] == 385
    assert len(structuring["pending_review_ids"]) == 10
    assert all(
        review_id.startswith("chiba-f08-")
        for review_id in structuring["pending_review_ids"]
    )
