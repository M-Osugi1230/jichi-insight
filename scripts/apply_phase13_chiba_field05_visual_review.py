from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT / "data/catalog"
REVIEWED = ROOT / "data/reviewed/chiba-city"
EVD = ROOT / "data/evidence"
TESTS = ROOT / "tests"

FIELD05_REVIEW = REVIEWED / "current_project_work_items_field05.json"
FIELD05_EVIDENCE = EVD / "chiba_current_project_work_items_field05_evidence.json"
WORK_ITEM_MANIFEST = CAT / "chiba_current_project_work_item_review_manifest.json"
POLICY_MANIFEST = CAT / "chiba_phase13_policy_review_manifest.json"
PLAN_REVIEW = REVIEWED / "plan_review.json"
QUEUE_BUILDER = ROOT / "scripts/build_chiba_work_item_visual_review_queue.py"

PROMOTIONS = {
    "chiba-f05-p001": [
        {
            "work_item_id": "chiba-f05-p001-w001",
            "item_name": "フェアトレードタウンの認定取得",
            "current_text": "認定申請に向けた準備",
            "plan_text": "認定申請",
            "target_text": "認定取得",
            "parse_status": "reviewed_structured",
        },
        {
            "work_item_id": "chiba-f05-p001-w002",
            "item_name": "フェアトレード産品取扱店の周知",
            "current_text": "フェアトレード産品取扱店の調査",
            "plan_text": "ポスター・ステッカー・のぼり作成",
            "target_text": "ポスター・ステッカー・のぼり作成",
            "parse_status": "reviewed_source_wrap_preserved",
        },
        {
            "work_item_id": "chiba-f05-p001-w003",
            "item_name": "組織・団体内でのフェアトレードの普及",
            "current_text": "―",
            "plan_text": "出前講座3回/年 / 販売会2回/年",
            "target_text": "出前講座3回/年 / 販売会2回/年",
            "parse_status": "reviewed_source_wrap_preserved",
        },
        {
            "work_item_id": "chiba-f05-p001-w004",
            "item_name": "千葉市フェアトレード推進員制度（仮称）の設置",
            "current_text": "―",
            "plan_text": "制度創設 / 推進員認定20人",
            "target_text": "推進員認定20人",
            "parse_status": "reviewed_source_wrap_preserved",
        },
    ],
    "chiba-f05-p003": [
        {
            "work_item_id": "chiba-f05-p003-w001",
            "item_name": "困難な問題を抱える女性への支援",
            "current_text": "アウトリーチ支援（訪問） / 電話及びＳＮＳ相談 / 居場所の確保",
            "plan_text": "アウトリーチ支援（巡回等）、自立支援・アフターケアの拡充、ステップハウスの運営 / 関係機関連携会議の開催2回/年",
            "target_text": "困難な問題を抱える女性への支援体制の強化 / 関係機関連携会議の開催2回/年",
            "parse_status": "reviewed_source_wrap_preserved",
        }
    ],
    "chiba-f05-p006": [
        {
            "work_item_id": "chiba-f05-p006-w001",
            "item_name": "複合施設整備",
            "current_text": "実施設計",
            "plan_text": "建築工事 / 外構工事",
            "target_text": "建築工事、外構工事",
            "parse_status": "reviewed_source_wrap_preserved",
        }
    ],
    "chiba-f05-p007": [
        {
            "work_item_id": "chiba-f05-p007-w001",
            "item_name": "新複合施設の建設",
            "current_text": "―",
            "plan_text": "基本設計 / 実施設計 / 建築工事",
            "target_text": "建築工事",
            "parse_status": "reviewed_source_wrap_preserved",
        },
        {
            "work_item_id": "chiba-f05-p007-w002",
            "item_name": "土気市民センターの解体工事",
            "current_text": "―",
            "plan_text": "解体設計 / 解体工事",
            "target_text": "解体工事完了",
            "parse_status": "reviewed_source_wrap_preserved",
        },
    ],
}

PROMOTION_METADATA = [
    ("chiba-f05-p001", "フェアトレードの推進", "PDF p.84", 4),
    ("chiba-f05-p003", "困難な問題を抱える女性への支援", "PDF p.85", 1),
    ("chiba-f05-p006", "千城台公民館・若葉図書館再整備", "PDF p.88", 1),
    (
        "chiba-f05-p007",
        "土気公民館・土気市民センター・土気いきいきセンターの再整備",
        "PDF p.88",
        2,
    ),
]

FIELD05_TEST = '''from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT / "data/catalog"
REVIEWED = ROOT / "data/reviewed/chiba-city"
EVD = ROOT / "data/evidence"
IDENTITIES = CAT / "chiba_current_project_identities_field05.json"
REVIEW = REVIEWED / "current_project_work_items_field05.json"
EVIDENCE = EVD / "chiba_current_project_work_items_field05_evidence.json"
MANIFEST = CAT / "chiba_current_project_work_item_review_manifest.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_field05_source_capture_covers_all_seven_identity_projects_exactly():
    identities = load(IDENTITIES)["records"]
    projects = load(REVIEW)["projects"]
    identity_pairs = {(row["review_id"], row["project_name"]) for row in identities}
    project_pairs = {(row["review_id"], row["project_name"]) for row in projects}

    assert len(identities) == len(projects) == 7
    assert len({row["review_id"] for row in projects}) == 7
    assert identity_pairs == project_pairs


def test_field05_measure_codes_and_source_locations_match_identity_layer():
    identities = {row["review_id"]: row for row in load(IDENTITIES)["records"]}
    for project in load(REVIEW)["projects"]:
        identity = identities[project["review_id"]]
        assert project["measure_code"] == identity["measure_code"]
        assert project["source_location"] == identity["source_location"]


def test_field05_all_projects_are_structured_after_visual_review():
    projects = load(REVIEW)["projects"]
    assert len(projects) == 7
    assert all(
        row.get("parse_status") != "pending_visual_column_confirmation"
        for row in projects
    )
    assert all(row["work_items"] for row in projects)


def test_field05_has_13_unique_complete_work_items():
    work_items = [
        item
        for project in load(REVIEW)["projects"]
        for item in project["work_items"]
    ]
    ids = [item["work_item_id"] for item in work_items]

    assert len(work_items) == len(ids) == len(set(ids)) == 13
    assert all(item["item_name"].strip() for item in work_items)
    assert all(item["current_text"].strip() for item in work_items)
    assert all(item["plan_text"].strip() for item in work_items)
    assert all(item["target_text"].strip() for item in work_items)
    assert {item["parse_status"] for item in work_items} <= {
        "reviewed_structured",
        "reviewed_source_wrap_preserved",
    }


def test_field05_visual_promotions_preserve_confirmed_table_semantics():
    projects = {row["review_id"]: row for row in load(REVIEW)["projects"]}

    fair = projects["chiba-f05-p001"]["work_items"]
    assert (fair[0]["current_text"], fair[0]["plan_text"], fair[0]["target_text"]) == (
        "認定申請に向けた準備",
        "認定申請",
        "認定取得",
    )
    assert fair[1]["current_text"] == "フェアトレード産品取扱店の調査"
    assert fair[1]["plan_text"] == fair[1]["target_text"] == "ポスター・ステッカー・のぼり作成"
    assert fair[2]["current_text"] == "―"
    assert fair[2]["plan_text"] == fair[2]["target_text"] == "出前講座3回/年 / 販売会2回/年"
    assert fair[3]["current_text"] == "―"
    assert fair[3]["plan_text"] == "制度創設 / 推進員認定20人"
    assert fair[3]["target_text"] == "推進員認定20人"

    support = projects["chiba-f05-p003"]["work_items"][0]
    assert support["current_text"] == "アウトリーチ支援（訪問） / 電話及びＳＮＳ相談 / 居場所の確保"
    assert support["plan_text"] == (
        "アウトリーチ支援（巡回等）、自立支援・アフターケアの拡充、ステップハウスの運営 / "
        "関係機関連携会議の開催2回/年"
    )
    assert support["target_text"] == (
        "困難な問題を抱える女性への支援体制の強化 / 関係機関連携会議の開催2回/年"
    )

    chishiro = projects["chiba-f05-p006"]["work_items"][0]
    assert chishiro["current_text"] == "実施設計"
    assert chishiro["plan_text"] == "建築工事 / 外構工事"
    assert chishiro["target_text"] == "建築工事、外構工事"

    toke = projects["chiba-f05-p007"]["work_items"]
    assert (toke[0]["current_text"], toke[0]["plan_text"], toke[0]["target_text"]) == (
        "―",
        "基本設計 / 実施設計 / 建築工事",
        "建築工事",
    )
    assert (toke[1]["current_text"], toke[1]["plan_text"], toke[1]["target_text"]) == (
        "―",
        "解体設計 / 解体工事",
        "解体工事完了",
    )


def test_field05_existing_annual_increment_and_compound_program_semantics_remain_intact():
    projects = {row["review_id"]: row for row in load(REVIEW)["projects"]}
    women = projects["chiba-f05-p002"]["work_items"][0]
    foreign = projects["chiba-f05-p004"]["work_items"]
    association = projects["chiba-f05-p005"]["work_items"][0]

    assert women["current_text"] == "―"
    assert women["plan_text"] == "デジタル人材養成講座の開催1回/年 / 企業マッチング支援1回/年"
    assert women["target_text"] == "デジタル人材育成養成講座の開催1回/年 / 企業マッチング支援1回/年"
    assert foreign[2]["plan_text"] == (
        "通訳派遣45件増/年 / 翻訳対応20件増/年 / 災害時語学ボランティア派遣12回/年 / "
        "多言語防災ガイドブック作成"
    )
    assert foreign[2]["target_text"] == foreign[2]["plan_text"]
    assert association["current_text"] == "検討"
    assert association["plan_text"] == association["target_text"] == "1回/年"


def test_field05_dash_current_values_remain_missing_state_not_zero():
    work_items = [
        item
        for project in load(REVIEW)["projects"]
        for item in project["work_items"]
    ]
    dash_items = [item for item in work_items if item["current_text"] == "―"]
    assert len(dash_items) == 7
    assert all(item["current_text"] != "0" for item in dash_items)


def test_field05_evidence_records_complete_visual_resolution():
    evidence = load(EVIDENCE)
    promotions = evidence["visual_confirmed_promotions"]

    assert evidence["review_status"] == "reviewed_source_capture_and_structuring_complete"
    assert evidence["structured_project_count"] == 7
    assert evidence["pending_visual_column_confirmation_project_count"] == 0
    assert evidence["structured_work_item_count"] == 13
    assert evidence["pending_visual_column_confirmation"] == []
    assert len(promotions) == 4
    assert sum(row["structured_work_item_count"] for row in promotions) == 8
    assert evidence["reconciliation"] == {
        "official_field05_project_count": 7,
        "source_capture_coverage": "7/7",
        "structured_project_coverage": "7/7",
        "structured_work_item_count": 13,
        "pending_project_count": 0,
        "cumulative_source_captured_projects": 120,
        "cumulative_structured_projects": 120,
        "cumulative_structured_work_items": 267,
        "cumulative_pending_visual_projects": 0,
    }


def test_field05_manifest_records_completed_field_and_current_progress():
    structuring = load(MANIFEST)["work_item_structuring"]
    assert structuring["projects_structured"] >= 160
    assert structuring["projects_pending_visual_column_confirmation"] <= 29
    assert structuring["structured_work_items"] >= 347
    assert all(
        not review_id.startswith("chiba-f05-")
        for review_id in structuring["pending_review_ids"]
    )
'''


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    require(count == 1, f"Expected exactly one {label} replacement, found {count}")
    return text.replace(old, new)


def promote_field05() -> None:
    payload = load_json(FIELD05_REVIEW)
    require(payload["structured_project_count"] == 3, "Unexpected field05 structured pre-state")
    require(payload["pending_visual_column_confirmation_project_count"] == 4, "Unexpected field05 pending pre-state")
    require(payload["structured_work_item_count"] == 5, "Unexpected field05 work-item pre-state")

    by_id = {row["review_id"]: row for row in payload["projects"]}
    for review_id, work_items in PROMOTIONS.items():
        project = by_id[review_id]
        require(project.get("parse_status") == "pending_visual_column_confirmation", f"{review_id} is not pending")
        project["parse_status"] = "reviewed_structured"
        project.pop("raw_table_text", None)
        project["work_items"] = work_items

    payload["review_status"] = "reviewed_source_capture_and_structuring_complete"
    payload["structured_project_count"] = 7
    payload["pending_visual_column_confirmation_project_count"] = 0
    payload["structured_work_item_count"] = 13
    payload["quality_boundary"] = (
        "分野5の7 identityすべてについて公式表をsource captureし、4件の視覚確認待ちも公式PDF"
        "レンダリング画像で列対応を直接確認した。7/7事業・13 work itemsをcurrent/plan/target列で"
        "構造化済み。複数行セルは原文順序を保持し、ダッシュを0へ変換しない。"
    )
    write_json(FIELD05_REVIEW, payload)


def update_field05_evidence() -> None:
    evidence = load_json(FIELD05_EVIDENCE)
    evidence["review_status"] = "reviewed_source_capture_and_structuring_complete"
    evidence["structured_project_count"] = 7
    evidence["pending_visual_column_confirmation_project_count"] = 0
    evidence["structured_work_item_count"] = 13
    evidence["pending_visual_column_confirmation"] = []
    evidence["visual_confirmed_promotions"] = [
        {
            "review_id": review_id,
            "project_name": project_name,
            "source_location": source_location,
            "structured_work_item_count": count,
        }
        for review_id, project_name, source_location, count in PROMOTION_METADATA
    ]
    evidence["reconciliation"] = {
        "official_field05_project_count": 7,
        "source_capture_coverage": "7/7",
        "structured_project_coverage": "7/7",
        "structured_work_item_count": 13,
        "pending_project_count": 0,
        "cumulative_source_captured_projects": 120,
        "cumulative_structured_projects": 120,
        "cumulative_structured_work_items": 267,
        "cumulative_pending_visual_projects": 0,
    }
    evidence["quality_boundary"] = (
        "分野5の7事業すべての公式事業量表を確認し、PDF p.84, p.85, p.88のレンダリング画像で"
        "4保留事業のcurrent/plan/target列を直接確定した。分野1～5累計120事業は全件structured、"
        "267 work items、visual-confirmation pending 0。未確認値の推定やダッシュの0変換は行わない。"
    )
    write_json(FIELD05_EVIDENCE, evidence)


def update_work_item_manifest() -> None:
    manifest = load_json(WORK_ITEM_MANIFEST)
    structuring = manifest["work_item_structuring"]
    require(structuring["projects_structured"] == 156, "Unexpected global structured pre-state")
    require(structuring["projects_pending_visual_column_confirmation"] == 33, "Unexpected global pending pre-state")
    require(structuring["structured_work_items"] == 339, "Unexpected global work-item pre-state")

    pending = [review_id for review_id in structuring["pending_review_ids"] if not review_id.startswith("chiba-f05-")]
    require(len(pending) == 29, "Unexpected post-field05 pending ID count")
    structuring["projects_structured"] = 160
    structuring["projects_pending_visual_column_confirmation"] = 29
    structuring["structured_work_items"] = 347
    structuring["pending_review_ids"] = pending
    manifest["quality_boundary"] = (
        "事業identity 189/189と全189事業の公式表source captureは完了。160事業・347 work itemsは"
        "current/plan/target列を構造化し、29事業は視覚的列確認待ち。分野1～5は公式PDFレンダリング"
        "画像で残件確認を終え120/120事業をstructured化した。29事業は専用visual review queueで"
        "追跡し、未確認値を推定しない。KGI/KPI・旧計画進捗・予算決算とは別レイヤーを維持する。"
    )
    write_json(WORK_ITEM_MANIFEST, manifest)


def update_policy_manifest() -> None:
    manifest = load_json(POLICY_MANIFEST)
    fact = next(row for row in manifest["reviewed_facts"] if row["id"] == "chiba-current-project-work-items")
    fact["structured_project_count"] = 160
    fact["pending_visual_column_confirmation_project_count"] = 29
    fact["structured_work_item_count"] = 347
    fact["interpretation_boundary"] = (
        "全189事業の公式表source captureは完了。160事業・347 work itemsはcurrent/plan/targetを"
        "構造化済み。29事業は複数行セルの列境界を視覚確認待ちとして明示し、未確認値を推定しない。"
        "分野1～5は公式PDFレンダリング画像による残件確認を終え120/120事業をstructured化した。"
    )
    manifest["remaining_work"][0] = (
        "現行第2次実施計画189事業の事業量source captureは完了。残る29事業を公式PDFの視覚確認で"
        "解消し、確認できたものだけproject-scoped work_itemsへ昇格する。"
    )
    manifest["quality_boundary"] = (
        "Phase 13 Chiba review remains in progress beyond the completed project identity and source-capture "
        "layers. Project quantity source capture is 189/189 complete: 160 projects and 347 work items are "
        "structured, while 29 projects remain explicitly pending visual column confirmation. Fields 1 through "
        "5 are fully structured at 120/120 projects after direct official-PDF rendered-page confirmation. "
        "Historical FY2024 progress remains tied to the 2023-2025 first implementation plan. Budget and "
        "settlement states remain separate. No independent policy-achievement judgment, causal attribution, "
        "version linkage, or automatic cross-city comparability is inferred."
    )
    write_json(POLICY_MANIFEST, manifest)


def update_plan_review() -> None:
    review = load_json(PLAN_REVIEW)
    universe = next(row for row in review["records"] if row["id"] == "chiba-current-project-universe")
    universe["review_note"] = (
        "189事業のidentity層と事業量source captureは完了。160事業・347 work itemsを構造化、"
        "29事業を視覚列確認待ちとして別管理する。"
    )
    work_items = next(row for row in review["records"] if row["id"] == "chiba-current-project-work-items")
    work_items["statement"] = (
        "現行189事業の取組項目、令和7年度末現況、計画内容、令和10年度末目標について全事業の"
        "source captureを完了。160事業・347 work itemsを構造化し、29事業は複数行セルの列境界を"
        "視覚確認待ちとして保持する。"
    )
    work_items["structured_project_count"] = 160
    work_items["pending_visual_column_confirmation_project_count"] = 29
    work_items["structured_work_item_count"] = 347
    work_items["review_note"] = (
        "source capture完了と3列構造化完了を分離する。分野1～5は公式PDFレンダリングページ画像で"
        "残件を直接確認し120/120事業をstructured化した。残る29事業は視覚確認なしに"
        "current/plan/targetを推定せず、ダッシュを0へ変換しない。"
    )
    review["quality_boundary"] = (
        "Chiba Phase 13 has completed 189/189 project identity and project-quantity source capture. Of the "
        "current project quantity layer, 160 projects and 347 work items are structured while 29 projects remain "
        "explicitly pending visual column confirmation. Fields 1 through 5 are fully structured at 120/120 "
        "projects after direct official-PDF rendered-page review. Historical FY2024 progress remains tied to "
        "the 2023-2025 first implementation plan. Policy indicators, project quantities, annual progress, "
        "budget, settlement, causal attribution, independent achievement judgments, and cross-city comparability "
        "remain distinct review units."
    )
    review["next_action"] = (
        "Resolve the remaining 29 project-quantity records pending visual column confirmation against the official "
        "second implementation plan. Promote only visually verified current/plan/2028-target column assignments; "
        "then review versioned linkage between the historical 360-project universe and current 189 projects, "
        "followed by conservative project-level budget/settlement linkage."
    )
    write_json(PLAN_REVIEW, review)


def update_tests() -> None:
    (TESTS / "test_phase13_chiba_project_work_items_field05.py").write_text(FIELD05_TEST, encoding="utf-8")

    alignment = TESTS / "test_phase13_chiba_project_work_item_alignment.py"
    text = alignment.read_text(encoding="utf-8")
    text = replace_once(text, '"structured_project_count": 156,', '"structured_project_count": 160,', "alignment structured")
    text = replace_once(text, '"pending_visual_column_confirmation_project_count": 33,', '"pending_visual_column_confirmation_project_count": 29,', "alignment pending")
    text = replace_once(text, '"structured_work_item_count": 339,', '"structured_work_item_count": 347,', "alignment work items")
    text = replace_once(text, '== 33\n', '== 29\n', "alignment pending length")
    text = replace_once(text, "test_chiba_field04_completion_advances_visual_review_to_field05", "test_chiba_field05_completion_advances_visual_review_to_field06", "alignment test name")
    text = replace_once(text, 'assert "33" in policy["remaining_work"][0]', 'assert "29" in policy["remaining_work"][0]', "alignment remaining")
    text = replace_once(text, 'assert "33" in plan["next_action"]', 'assert "29" in plan["next_action"]', "alignment next action")
    text = replace_once(
        text,
        'not review_id.startswith(("chiba-f01-", "chiba-f02-", "chiba-f03-", "chiba-f04-"))',
        'not review_id.startswith(("chiba-f01-", "chiba-f02-", "chiba-f03-", "chiba-f04-", "chiba-f05-"))',
        "alignment completed fields",
    )
    alignment.write_text(text, encoding="utf-8")

    queue_test = TESTS / "test_phase13_chiba_project_work_item_visual_review_queue.py"
    text = queue_test.read_text(encoding="utf-8")
    text = text.replace("all_33_pending_projects", "all_29_pending_projects")
    text = replace_once(text, 'assert len(queued_ids) == len(set(queued_ids)) == 33', 'assert len(queued_ids) == len(set(queued_ids)) == 29', "queue total")
    text = replace_once(text, "        4,\n        9,\n        10,\n        10,", "        0,\n        9,\n        10,\n        10,", "queue field counts")
    text = replace_once(text, 'assert sum(batch["pending_count"] for batch in queue["batches"]) == 33', 'assert sum(batch["pending_count"] for batch in queue["batches"]) == 29', "queue sum")
    text = replace_once(text, "assert len(structured_ids) == 156", "assert len(structured_ids) == 160", "queue structured ids")
    text = replace_once(text, '"projects_structured": 156,', '"projects_structured": 160,', "queue source structured")
    text = replace_once(text, '"structured_work_items": 339,', '"structured_work_items": 347,', "queue source work items")
    text = replace_once(text, '"projects_pending_visual_column_confirmation": 33,', '"projects_pending_visual_column_confirmation": 29,', "queue source pending")
    start = text.index("def test_next_visual_batch_starts_with_field05_official_order():")
    text = text[:start] + '''def test_next_visual_batch_starts_with_field06_official_order():
    queue = load(QUEUE)

    assert queue["execution_order"] == "official_field_and_project_order"
    assert all(batch["pending_count"] == 0 for batch in queue["batches"][:5])
    assert queue["next_batch"] == {
        "field_code": "6",
        "field_name": "文化芸術・スポーツ",
        "pending_review_ids": [
            "chiba-f06-p001",
            "chiba-f06-p002",
            "chiba-f06-p004",
            "chiba-f06-p006",
            "chiba-f06-p007",
            "chiba-f06-p009",
            "chiba-f06-p011",
            "chiba-f06-p013",
            "chiba-f06-p014",
        ],
    }
    assert "推定しない" in queue["resolution_rule"]
    assert "29事業" in queue["quality_boundary"]
'''
    queue_test.write_text(text, encoding="utf-8")

    policy_test = TESTS / "test_phase13_chiba_policy_indicators.py"
    text = policy_test.read_text(encoding="utf-8")
    text = replace_once(text, "test_chiba_plan_review_reflects_field04_visual_completion", "test_chiba_plan_review_reflects_field05_visual_completion", "policy test name")
    text = replace_once(text, '== 156\n', '== 160\n', "policy structured")
    text = replace_once(text, '== 33\n', '== 29\n', "policy pending")
    text = replace_once(text, '== 339\n', '== 347\n', "policy work items")
    text = replace_once(text, 'assert "33" in review["next_action"]', 'assert "29" in review["next_action"]', "policy next action")
    policy_test.write_text(text, encoding="utf-8")


def validate() -> None:
    field05 = load_json(FIELD05_REVIEW)
    items = [item for project in field05["projects"] for item in project["work_items"]]
    require(len(items) == 13, "Field05 should contain 13 work items")
    require(all(project.get("parse_status") != "pending_visual_column_confirmation" for project in field05["projects"]), "Field05 still pending")

    structuring = load_json(WORK_ITEM_MANIFEST)["work_item_structuring"]
    require(structuring["projects_structured"] == 160, "Global structured should be 160")
    require(structuring["projects_pending_visual_column_confirmation"] == 29, "Global pending should be 29")
    require(structuring["structured_work_items"] == 347, "Global work items should be 347")
    require(len(structuring["pending_review_ids"]) == 29, "Pending ID count should be 29")
    require(all(not review_id.startswith("chiba-f05-") for review_id in structuring["pending_review_ids"]), "Field05 remains pending")


def main() -> None:
    promote_field05()
    update_field05_evidence()
    update_work_item_manifest()
    update_policy_manifest()
    update_plan_review()
    update_tests()
    subprocess.run([sys.executable, str(QUEUE_BUILDER)], cwd=ROOT, check=True)
    validate()


if __name__ == "__main__":
    main()
