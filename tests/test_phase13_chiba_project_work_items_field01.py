from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT / "data/catalog"
REVIEWED = ROOT / "data/reviewed/chiba-city"
EVD = ROOT / "data/evidence"
IDENTITIES = CAT / "chiba_current_project_identities_field01.json"
PART01 = REVIEWED / "current_project_work_items_field01_part01.json"
PART02 = REVIEWED / "current_project_work_items_field01_part02.json"
EVIDENCE = EVD / "chiba_current_project_work_items_field01_evidence.json"
MANIFEST = CAT / "chiba_current_project_work_item_review_manifest.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def combined_projects():
    return load(PART01)["projects"] + load(PART02)["projects"]


def test_field01_source_capture_covers_all_30_identity_projects_exactly():
    identities = load(IDENTITIES)["records"]
    projects = combined_projects()
    identity_pairs = {(row["review_id"], row["project_name"]) for row in identities}
    project_pairs = {(row["review_id"], row["project_name"]) for row in projects}

    assert len(identities) == 30
    assert len(projects) == 30
    assert len({row["review_id"] for row in projects}) == 30
    assert identity_pairs == project_pairs


def test_field01_measure_codes_and_source_locations_match_identity_layer():
    identities = {row["review_id"]: row for row in load(IDENTITIES)["records"]}

    for project in combined_projects():
        identity = identities[project["review_id"]]
        assert project["measure_code"] == identity["measure_code"]
        assert project["source_location"].startswith("PDF p")


def test_field01_all_30_projects_are_structured_after_visual_review():
    projects = combined_projects()
    pending = [
        row
        for row in projects
        if row.get("parse_status") == "pending_visual_column_confirmation"
    ]

    assert len(projects) == 30
    assert pending == []


def test_field01_structured_work_items_have_complete_raw_source_columns():
    work_items = [item for project in combined_projects() for item in project["work_items"]]
    ids = [item["work_item_id"] for item in work_items]

    assert len(work_items) == 81
    assert len(ids) == len(set(ids)) == 81
    assert all(item["item_name"].strip() for item in work_items)
    assert all(item["current_text"].strip() for item in work_items)
    assert all(item["plan_text"].strip() for item in work_items)
    assert all(item["target_text"].strip() for item in work_items)
    assert {item["parse_status"] for item in work_items} <= {
        "reviewed_structured",
        "reviewed_source_wrap_preserved",
    }


def test_field01_preserves_annual_increment_and_cumulative_semantics_as_text():
    projects = {row["review_id"]: row for row in combined_projects()}
    p002 = {item["work_item_id"]: item for item in projects["chiba-f01-p002"]["work_items"]}
    p008 = projects["chiba-f01-p008"]["work_items"][0]

    assert p002["chiba-f01-p002-w001"] == {
        "work_item_id": "chiba-f01-p002-w001",
        "item_name": "事業者向け省エネルギー設備導入に係る補助",
        "current_text": "15件/年",
        "plan_text": "10件増",
        "target_text": "25件/年",
        "parse_status": "reviewed_structured",
    }
    assert p008["current_text"] == "65.48ha"
    assert p008["plan_text"] == "6ha拡大"
    assert p008["target_text"] == "71.48ha"


def test_field01_dash_current_values_are_preserved_not_converted_to_zero():
    projects = {row["review_id"]: row for row in combined_projects()}
    dash_items = [
        item
        for project in projects.values()
        for item in project["work_items"]
        if item["current_text"] == "―"
    ]

    assert len(dash_items) >= 4
    assert all(item["current_text"] != "0" for item in dash_items)


def test_field01_visual_confirmed_projects_preserve_exact_rows():
    projects = {row["review_id"]: row for row in combined_projects()}
    park = projects["chiba-f01-p018"]
    minato = projects["chiba-f01-p020"]
    zoo = projects["chiba-f01-p026"]
    river = projects["chiba-f01-p029"]

    assert len(park["work_items"]) == 4
    assert park["work_items"][1] == {
        "work_item_id": "chiba-f01-p018-w002",
        "item_name": "遊びゾーン整備 / 拡張区域整備",
        "current_text": "拡張用地引渡し",
        "plan_text": "測量・基本設計 / 実施設計 / 施設整備",
        "target_text": "拡張区域整備完了",
        "parse_status": "reviewed_structured",
    }
    assert park["work_items"][3]["target_text"] == (
        "多目的広場実施設計完了 / 関係者との意見交換実施 / サウンディング調査完了"
    )

    assert minato["work_items"] == [
        {
            "work_item_id": "chiba-f01-p020-w001",
            "item_name": "みなと公園の再整備",
            "current_text": "再整備に向けたワークショップ実施",
            "plan_text": "再整備基本計画策定 / 基本設計 / サウンディング調査",
            "target_text": "再整備基本計画策定 / サウンディング調査*",
            "parse_status": "reviewed_structured",
        }
    ]

    assert len(zoo["work_items"]) == 7
    assert zoo["work_items"][0]["target_text"] == "オープン"
    assert zoo["work_items"][3]["item_name"] == "アニマルウェルフェア*基準への適合"
    assert zoo["work_items"][6]["plan_text"] == (
        "外来生物の駆除及び水質モニタリング 196回 / ボランティア育成 20人 / "
        "展示物整備・飼育管理"
    )
    assert zoo["work_items"][6]["target_text"] == zoo["work_items"][6]["plan_text"]

    assert len(river["work_items"]) == 4
    assert river["work_items"][0] == {
        "work_item_id": "chiba-f01-p029-w001",
        "item_name": "花見川の利活用 / 花見川千本桜緑地の活性化",
        "current_text": "利活用社会実験実施 / トライアルサウンディング",
        "plan_text": (
            "利活用社会実験実施 / トライアルサウンディング / 民間活力導入可能性調査"
        ),
        "target_text": "利活用社会実験実施 / 利活用方針の策定",
        "parse_status": "reviewed_structured",
    }


def test_field01_evidence_reconciles_source_capture_and_structuring():
    evidence = load(EVIDENCE)

    assert evidence["review_status"] == "reviewed_source_capture_and_structuring_complete"
    assert evidence["identity_project_count"] == 30
    assert evidence["source_captured_project_count"] == 30
    assert evidence["structured_project_count"] == 30
    assert evidence["pending_visual_column_confirmation_project_count"] == 0
    assert evidence["structured_work_item_count"] == 81
    assert evidence["pending_visual_column_confirmation"] == []
    assert evidence["reconciliation"] == {
        "official_field01_project_count": 30,
        "source_capture_coverage": "30/30",
        "structured_project_coverage": "30/30",
        "structured_work_item_count": 81,
        "pending_project_count": 0,
    }
    promotions = {row["review_id"]: row for row in evidence["visual_confirmed_promotions"]}
    assert set(promotions) == {
        "chiba-f01-p018",
        "chiba-f01-p020",
        "chiba-f01-p026",
        "chiba-f01-p029",
    }
    assert promotions["chiba-f01-p018"]["structured_work_item_count"] == 4
    assert promotions["chiba-f01-p020"]["structured_work_item_count"] == 1
    assert promotions["chiba-f01-p026"]["structured_work_item_count"] == 7
    assert promotions["chiba-f01-p029"]["structured_work_item_count"] == 4


def test_field01_work_item_manifest_records_completed_field():
    manifest = load(MANIFEST)
    capture = manifest["work_item_source_capture"]
    structuring = manifest["work_item_structuring"]

    assert manifest["project_universe"] == 189
    assert manifest["project_identity_coverage"] == {"reviewed": 189, "remaining": 0}
    assert capture["projects_reviewed"] == 189
    assert capture["field_counts_reviewed"]["environment_nature"] == 30
    assert structuring["projects_structured"] == 135
    assert structuring["projects_pending_visual_column_confirmation"] == 54
    assert structuring["projects_not_yet_source_captured"] == 0
    assert structuring["structured_work_items"] == 296
    assert all(
        not review_id.startswith("chiba-f01-")
        for review_id in structuring["pending_review_ids"]
    )
