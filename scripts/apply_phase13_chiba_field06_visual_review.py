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

FIELD06_REVIEW = REVIEWED / "current_project_work_items_field06.json"
FIELD06_EVIDENCE = EVD / "chiba_current_project_work_items_field06_evidence.json"
WORK_ITEM_MANIFEST = CAT / "chiba_current_project_work_item_review_manifest.json"
POLICY_MANIFEST = CAT / "chiba_phase13_policy_review_manifest.json"
PLAN_REVIEW = REVIEWED / "plan_review.json"
QUEUE_BUILDER = ROOT / "scripts/build_chiba_work_item_visual_review_queue.py"

PROMOTIONS = {
    "chiba-f06-p001": [
        {
            "work_item_id": "chiba-f06-p001-w001",
            "item_name": "緑町公園アートパークプロジェクト",
            "current_text": "事業者決定",
            "plan_text": "公園整備等 / イベント実施",
            "target_text": "公園整備完了 / イベント実施",
            "parse_status": "reviewed_source_wrap_preserved",
        },
        {
            "work_item_id": "chiba-f06-p001-w002",
            "item_name": "花見川団地商店街北街区におけるアーティスト・イン・レジデンス",
            "current_text": "事業者決定",
            "plan_text": "アーティスト・イン・レジデンス準備 / アーティスト・イン・レジデンス運営",
            "target_text": "アーティスト・イン・レジデンス運営",
            "parse_status": "reviewed_source_wrap_preserved",
        },
    ],
    "chiba-f06-p002": [
        {
            "work_item_id": "chiba-f06-p002-w001",
            "item_name": "千葉国際芸術祭の開催",
            "current_text": "千葉国際芸術祭2025の実施",
            "plan_text": "千葉開府900年企画の実施 / トリエンナーレ形式による定期開催",
            "target_text": "トリエンナーレ形式による定期開催",
            "parse_status": "reviewed_source_wrap_preserved",
        }
    ],
    "chiba-f06-p004": [
        {
            "work_item_id": "chiba-f06-p004-w001",
            "item_name": "市民会館の整備",
            "current_text": "基本計画修正",
            "plan_text": "基本計画修正 / 基本設計 / 実施設計",
            "target_text": "実施設計",
            "parse_status": "reviewed_source_wrap_preserved",
        },
        {
            "work_item_id": "chiba-f06-p004-w002",
            "item_name": "用地取得",
            "current_text": "―",
            "plan_text": "用地測量・境界確定 / 不動産鑑定",
            "target_text": "不動産鑑定",
            "parse_status": "reviewed_source_wrap_preserved",
        },
    ],
    "chiba-f06-p006": [
        {
            "work_item_id": "chiba-f06-p006-w001",
            "item_name": "史跡整備（第２期）",
            "current_text": "検討",
            "plan_text": "基本計画策定 / 基本設計 / 実施設計",
            "target_text": "史跡整備基本計画策定 / 北貝塚貝層断面観覧施設実施設計完了 / 史跡環境整備実施設計完了",
            "parse_status": "reviewed_source_wrap_preserved",
        }
    ],
    "chiba-f06-p007": [
        {
            "work_item_id": "chiba-f06-p007-w001",
            "item_name": "新博物館の整備",
            "current_text": "事業者決定",
            "plan_text": "基本設計 / 実施設計 / 工事 / 解体工事",
            "target_text": "工事",
            "parse_status": "reviewed_source_wrap_preserved",
        },
        {
            "work_item_id": "chiba-f06-p007-w002",
            "item_name": "周辺環境の整備",
            "current_text": "（連絡歩道橋及び周遊路）測量 / 不動産鑑定",
            "plan_text": "（連絡歩道橋及び周遊路）用地取得・設計・工事 / わくわく検討委員会運営 / （歩道改良）予備設計 / （歩道改良）詳細設計",
            "target_text": "（連絡歩道橋及び周遊路）工事 / （歩道改良）詳細設計",
            "parse_status": "reviewed_source_wrap_preserved",
        },
    ],
    "chiba-f06-p009": [
        {
            "work_item_id": "chiba-f06-p009-w001",
            "item_name": "『千葉市史史料編近現代』第３巻の刊行",
            "current_text": "編集",
            "plan_text": "編集 / 刊行",
            "target_text": "刊行",
            "parse_status": "reviewed_source_wrap_preserved",
        },
        {
            "work_item_id": "chiba-f06-p009-w002",
            "item_name": "『千葉市史』通史編の編集",
            "current_text": "編集",
            "plan_text": "編集",
            "target_text": "編集",
            "parse_status": "reviewed_structured",
        },
    ],
    "chiba-f06-p011": [
        {
            "work_item_id": "chiba-f06-p011-w001",
            "item_name": "北谷津温水プールの建替え",
            "current_text": "PFI導入可能性調査",
            "plan_text": "事業者選定 / 基本設計 / 実施設計 / 整備工事",
            "target_text": "整備工事",
            "parse_status": "reviewed_source_wrap_preserved",
        },
        {
            "work_item_id": "chiba-f06-p011-w002",
            "item_name": "千葉公園水泳プールの改築",
            "current_text": "基礎調査",
            "plan_text": "基礎調査",
            "target_text": "基礎調査",
            "parse_status": "reviewed_structured",
        },
    ],
    "chiba-f06-p013": [
        {
            "work_item_id": "chiba-f06-p013-w001",
            "item_name": "アリーナ整備",
            "current_text": "基本協定締結",
            "plan_text": "アドバイザリー業務委託 / 事業者選定 / 基盤整備支援 / 民間事業者による整備",
            "target_text": "民間事業者による整備",
            "parse_status": "reviewed_source_wrap_preserved",
        }
    ],
    "chiba-f06-p014": [
        {
            "work_item_id": "chiba-f06-p014-w001",
            "item_name": "スポーツ大会の誘致",
            "current_text": "負担金支援１件/年",
            "plan_text": "負担金支援１件/年 / 補助金制度創設 / 補助金支援２件/年",
            "target_text": "負担金支援１件/年 / 補助金支援２件/年",
            "parse_status": "reviewed_source_wrap_preserved",
        }
    ],
}

PROMOTION_METADATA = [
    ("chiba-f06-p001", "アートのまちづくりの推進", "PDF p.90", 2),
    ("chiba-f06-p002", "千葉国際芸術祭の定期開催", "PDF p.91", 1),
    ("chiba-f06-p004", "市民会館の再整備", "PDF p.91", 2),
    ("chiba-f06-p006", "加曽利貝塚の史跡整備", "PDF p.92", 1),
    ("chiba-f06-p007", "特別史跡加曽利貝塚新博物館の整備", "PDF p.93", 2),
    ("chiba-f06-p009", "千葉市史編さん事業の推進", "PDF p.93", 2),
    ("chiba-f06-p011", "市民プールの更新", "PDF p.94", 2),
    ("chiba-f06-p013", "アルティーリ千葉新アリーナの整備支援", "PDF p.95", 1),
    ("chiba-f06-p014", "国際・全国的な大規模スポーツ大会の開催・支援", "PDF p.96", 1),
]

FIELD06_TEST = '''from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT / "data/catalog"
REVIEWED = ROOT / "data/reviewed/chiba-city"
EVD = ROOT / "data/evidence"
IDENTITIES = CAT / "chiba_current_project_identities_field06.json"
REVIEW = REVIEWED / "current_project_work_items_field06.json"
EVIDENCE = EVD / "chiba_current_project_work_items_field06_evidence.json"
MANIFEST = CAT / "chiba_current_project_work_item_review_manifest.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_field06_source_capture_covers_all_15_identity_projects_exactly():
    identities = load(IDENTITIES)["records"]
    projects = load(REVIEW)["projects"]
    assert len(identities) == len(projects) == 15
    assert {(row["review_id"], row["project_name"]) for row in identities} == {
        (row["review_id"], row["project_name"]) for row in projects
    }


def test_field06_measure_codes_and_source_locations_match_identity_layer():
    identities = {row["review_id"]: row for row in load(IDENTITIES)["records"]}
    for project in load(REVIEW)["projects"]:
        identity = identities[project["review_id"]]
        assert project["measure_code"] == identity["measure_code"]
        assert project["source_location"] == identity["source_location"]


def test_field06_all_projects_are_structured_after_visual_review():
    projects = load(REVIEW)["projects"]
    assert len(projects) == 15
    assert all(
        row.get("parse_status") != "pending_visual_column_confirmation"
        for row in projects
    )
    assert all(row["work_items"] for row in projects)


def test_field06_has_23_unique_complete_work_items():
    work_items = [
        item
        for project in load(REVIEW)["projects"]
        for item in project["work_items"]
    ]
    ids = [item["work_item_id"] for item in work_items]
    assert len(work_items) == len(ids) == len(set(ids)) == 23
    assert all(item["item_name"].strip() for item in work_items)
    assert all(item["current_text"].strip() for item in work_items)
    assert all(item["plan_text"].strip() for item in work_items)
    assert all(item["target_text"].strip() for item in work_items)


def test_field06_visual_promotions_preserve_confirmed_table_semantics():
    projects = {row["review_id"]: row for row in load(REVIEW)["projects"]}

    art = projects["chiba-f06-p001"]["work_items"]
    assert art[0]["current_text"] == "事業者決定"
    assert art[0]["plan_text"] == "公園整備等 / イベント実施"
    assert art[0]["target_text"] == "公園整備完了 / イベント実施"
    assert art[1]["current_text"] == "事業者決定"
    assert art[1]["target_text"] == "アーティスト・イン・レジデンス運営"

    festival = projects["chiba-f06-p002"]["work_items"][0]
    assert festival["current_text"] == "千葉国際芸術祭2025の実施"
    assert festival["plan_text"] == (
        "千葉開府900年企画の実施 / トリエンナーレ形式による定期開催"
    )
    assert festival["target_text"] == "トリエンナーレ形式による定期開催"

    hall = projects["chiba-f06-p004"]["work_items"]
    assert hall[0]["current_text"] == "基本計画修正"
    assert hall[0]["plan_text"] == "基本計画修正 / 基本設計 / 実施設計"
    assert hall[0]["target_text"] == "実施設計"
    assert hall[1]["current_text"] == "―"
    assert hall[1]["plan_text"] == "用地測量・境界確定 / 不動産鑑定"
    assert hall[1]["target_text"] == "不動産鑑定"

    site = projects["chiba-f06-p006"]["work_items"][0]
    assert site["current_text"] == "検討"
    assert site["plan_text"] == "基本計画策定 / 基本設計 / 実施設計"
    assert site["target_text"] == (
        "史跡整備基本計画策定 / 北貝塚貝層断面観覧施設実施設計完了 / "
        "史跡環境整備実施設計完了"
    )

    museum = projects["chiba-f06-p007"]["work_items"]
    assert museum[0]["current_text"] == "事業者決定"
    assert museum[0]["plan_text"] == "基本設計 / 実施設計 / 工事 / 解体工事"
    assert museum[0]["target_text"] == "工事"
    assert museum[1]["current_text"] == "（連絡歩道橋及び周遊路）測量 / 不動産鑑定"
    assert museum[1]["target_text"] == (
        "（連絡歩道橋及び周遊路）工事 / （歩道改良）詳細設計"
    )

    history = projects["chiba-f06-p009"]["work_items"]
    assert (history[0]["current_text"], history[0]["plan_text"], history[0]["target_text"]) == (
        "編集",
        "編集 / 刊行",
        "刊行",
    )
    assert (history[1]["current_text"], history[1]["plan_text"], history[1]["target_text"]) == (
        "編集",
        "編集",
        "編集",
    )

    pools = projects["chiba-f06-p011"]["work_items"]
    assert pools[0]["current_text"] == "PFI導入可能性調査"
    assert pools[0]["plan_text"] == "事業者選定 / 基本設計 / 実施設計 / 整備工事"
    assert pools[0]["target_text"] == "整備工事"
    assert pools[1]["current_text"] == pools[1]["plan_text"] == pools[1]["target_text"] == "基礎調査"

    arena = projects["chiba-f06-p013"]["work_items"][0]
    assert arena["current_text"] == "基本協定締結"
    assert arena["plan_text"] == (
        "アドバイザリー業務委託 / 事業者選定 / 基盤整備支援 / 民間事業者による整備"
    )
    assert arena["target_text"] == "民間事業者による整備"

    events = projects["chiba-f06-p014"]["work_items"][0]
    assert events["current_text"] == "負担金支援１件/年"
    assert events["plan_text"] == "負担金支援１件/年 / 補助金制度創設 / 補助金支援２件/年"
    assert events["target_text"] == "負担金支援１件/年 / 補助金支援２件/年"


def test_field06_existing_annual_increment_and_state_semantics_remain_intact():
    projects = {row["review_id"]: row for row in load(REVIEW)["projects"]}
    museum = projects["chiba-f06-p008"]["work_items"]
    para = projects["chiba-f06-p010"]["work_items"]
    top = projects["chiba-f06-p012"]["work_items"][0]
    urban = projects["chiba-f06-p015"]["work_items"][0]

    assert museum[0]["current_text"] == "―"
    assert museum[1]["target_text"] == "開催1回/年"
    assert para[1]["current_text"] == "1回/年"
    assert para[1]["plan_text"] == para[1]["target_text"] == "2回/年"
    assert top["current_text"] == "100校/年"
    assert top["plan_text"] == "3校/年増"
    assert top["target_text"] == "109校/年"
    assert urban["current_text"] == "―"
    assert urban["plan_text"] == urban["target_text"] == "1回"


def test_field06_evidence_records_complete_visual_resolution():
    evidence = load(EVIDENCE)
    promotions = evidence["visual_confirmed_promotions"]
    assert evidence["review_status"] == "reviewed_source_capture_and_structuring_complete"
    assert evidence["structured_project_count"] == 15
    assert evidence["pending_visual_column_confirmation_project_count"] == 0
    assert evidence["structured_work_item_count"] == 23
    assert evidence["pending_visual_column_confirmation"] == []
    assert len(promotions) == 9
    assert sum(row["structured_work_item_count"] for row in promotions) == 14
    assert evidence["reconciliation"] == {
        "official_field06_project_count": 15,
        "source_capture_coverage": "15/15",
        "structured_project_coverage": "15/15",
        "structured_work_item_count": 23,
        "pending_project_count": 0,
        "cumulative_source_captured_projects": 135,
        "cumulative_structured_projects": 135,
        "cumulative_structured_work_items": 290,
        "cumulative_pending_visual_projects": 0,
    }


def test_field06_manifest_records_completed_field_and_current_progress():
    structuring = load(MANIFEST)["work_item_structuring"]
    assert structuring["projects_structured"] >= 169
    assert structuring["projects_pending_visual_column_confirmation"] <= 20
    assert structuring["structured_work_items"] >= 361
    assert all(
        not review_id.startswith("chiba-f06-")
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


def promote_field06() -> None:
    payload = load_json(FIELD06_REVIEW)
    require(payload["structured_project_count"] == 6, "Unexpected field06 structured pre-state")
    require(
        payload["pending_visual_column_confirmation_project_count"] == 9,
        "Unexpected field06 pending pre-state",
    )
    require(payload["structured_work_item_count"] == 9, "Unexpected field06 work-item pre-state")

    by_id = {row["review_id"]: row for row in payload["projects"]}
    for review_id, work_items in PROMOTIONS.items():
        project = by_id[review_id]
        require(
            project.get("parse_status") == "pending_visual_column_confirmation",
            f"{review_id} is not pending",
        )
        project["parse_status"] = "reviewed_structured"
        project.pop("raw_table_text", None)
        project["work_items"] = work_items

    payload["review_status"] = "reviewed_source_capture_and_structuring_complete"
    payload["structured_project_count"] = 15
    payload["pending_visual_column_confirmation_project_count"] = 0
    payload["structured_work_item_count"] = 23
    payload["quality_boundary"] = (
        "分野6の15 identityすべてについて公式表をsource captureし、9件の視覚確認待ちも"
        "公式PDFレンダリング画像で列対応を直接確認した。15/15事業・23 work itemsを"
        "current/plan/target列で構造化済み。複数行セルは原文順序を保持し、ダッシュを0へ"
        "変換しない。分野横断再掲はidentity母集団へ重複追加しない。"
    )
    write_json(FIELD06_REVIEW, payload)


def update_field06_evidence() -> None:
    evidence = load_json(FIELD06_EVIDENCE)
    evidence["review_status"] = "reviewed_source_capture_and_structuring_complete"
    evidence["structured_project_count"] = 15
    evidence["pending_visual_column_confirmation_project_count"] = 0
    evidence["structured_work_item_count"] = 23
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
        "official_field06_project_count": 15,
        "source_capture_coverage": "15/15",
        "structured_project_coverage": "15/15",
        "structured_work_item_count": 23,
        "pending_project_count": 0,
        "cumulative_source_captured_projects": 135,
        "cumulative_structured_projects": 135,
        "cumulative_structured_work_items": 290,
        "cumulative_pending_visual_projects": 0,
    }
    evidence["quality_boundary"] = (
        "分野6の15事業すべての公式事業量表を確認し、PDF p.90-96のレンダリング画像で"
        "9保留事業のcurrent/plan/target列を直接確定した。分野1～6累計135事業は全件"
        "structured、290 work items、visual-confirmation pending 0。未確認値の推定や"
        "ダッシュの0変換は行わない。"
    )
    write_json(FIELD06_EVIDENCE, evidence)


def update_work_item_manifest() -> None:
    manifest = load_json(WORK_ITEM_MANIFEST)
    structuring = manifest["work_item_structuring"]
    require(structuring["projects_structured"] == 160, "Unexpected global structured pre-state")
    require(
        structuring["projects_pending_visual_column_confirmation"] == 29,
        "Unexpected global pending pre-state",
    )
    require(structuring["structured_work_items"] == 347, "Unexpected global work-item pre-state")

    pending = [
        review_id
        for review_id in structuring["pending_review_ids"]
        if not review_id.startswith("chiba-f06-")
    ]
    require(len(pending) == 20, "Unexpected post-field06 pending ID count")
    structuring["projects_structured"] = 169
    structuring["projects_pending_visual_column_confirmation"] = 20
    structuring["structured_work_items"] = 361
    structuring["pending_review_ids"] = pending
    manifest["quality_boundary"] = (
        "事業identity 189/189と全189事業の公式表source captureは完了。169事業・361 work "
        "itemsはcurrent/plan/target列を構造化し、20事業は視覚的列確認待ち。分野1～6は"
        "公式PDFレンダリング画像で残件確認を終え135/135事業をstructured化した。20事業は"
        "専用visual review queueで追跡し、未確認値を推定しない。KGI/KPI・旧計画進捗・"
        "予算決算とは別レイヤーを維持する。"
    )
    write_json(WORK_ITEM_MANIFEST, manifest)


def update_policy_manifest() -> None:
    manifest = load_json(POLICY_MANIFEST)
    fact = next(
        row
        for row in manifest["reviewed_facts"]
        if row["id"] == "chiba-current-project-work-items"
    )
    fact["structured_project_count"] = 169
    fact["pending_visual_column_confirmation_project_count"] = 20
    fact["structured_work_item_count"] = 361
    fact["interpretation_boundary"] = (
        "全189事業の公式表source captureは完了。169事業・361 work itemsはcurrent/plan/targetを"
        "構造化済み。20事業は複数行セルの列境界を視覚確認待ちとして明示し、未確認値を推定しない。"
        "分野1～6は公式PDFレンダリング画像による残件確認を終え135/135事業をstructured化した。"
    )
    manifest["remaining_work"][0] = (
        "現行第2次実施計画189事業の事業量source captureは完了。残る20事業を公式PDFの"
        "視覚確認で解消し、確認できたものだけproject-scoped work_itemsへ昇格する。"
    )
    manifest["quality_boundary"] = (
        "Phase 13 Chiba review remains in progress beyond the completed project identity and "
        "source-capture layers. Project quantity source capture is 189/189 complete: 169 projects "
        "and 361 work items are structured, while 20 projects remain explicitly pending visual "
        "column confirmation. Fields 1 through 6 are fully structured at 135/135 projects after "
        "direct official-PDF rendered-page confirmation. Historical FY2024 progress remains tied "
        "to the 2023-2025 first implementation plan. Budget and settlement states remain separate. "
        "No independent policy-achievement judgment, causal attribution, version linkage, or "
        "automatic cross-city comparability is inferred."
    )
    write_json(POLICY_MANIFEST, manifest)


def update_plan_review() -> None:
    review = load_json(PLAN_REVIEW)
    universe = next(
        row for row in review["records"] if row["id"] == "chiba-current-project-universe"
    )
    universe["review_note"] = (
        "189事業のidentity層と事業量source captureは完了。169事業・361 work itemsを構造化、"
        "20事業を視覚列確認待ちとして別管理する。"
    )
    work_items = next(
        row for row in review["records"] if row["id"] == "chiba-current-project-work-items"
    )
    work_items["statement"] = (
        "現行189事業の取組項目、令和7年度末現況、計画内容、令和10年度末目標について全事業の"
        "source captureを完了。169事業・361 work itemsを構造化し、20事業は複数行セルの列境界を"
        "視覚確認待ちとして保持する。"
    )
    work_items["structured_project_count"] = 169
    work_items["pending_visual_column_confirmation_project_count"] = 20
    work_items["structured_work_item_count"] = 361
    work_items["review_note"] = (
        "source capture完了と3列構造化完了を分離する。分野1～6は公式PDFレンダリングページ画像で"
        "残件を直接確認し135/135事業をstructured化した。残る20事業は視覚確認なしに"
        "current/plan/targetを推定せず、ダッシュを0へ変換しない。"
    )
    review["quality_boundary"] = (
        "Chiba Phase 13 has completed 189/189 project identity and project-quantity source capture. "
        "Of the current project quantity layer, 169 projects and 361 work items are structured while "
        "20 projects remain explicitly pending visual column confirmation. Fields 1 through 6 are "
        "fully structured at 135/135 projects after direct official-PDF rendered-page review. "
        "Historical FY2024 progress remains tied to the 2023-2025 first implementation plan. Policy "
        "indicators, project quantities, annual progress, budget, settlement, causal attribution, "
        "independent achievement judgments, and cross-city comparability remain distinct review units."
    )
    review["next_action"] = (
        "Resolve the remaining 20 project-quantity records pending visual column confirmation against "
        "the official second implementation plan. Promote only visually verified current/plan/2028-target "
        "column assignments; then review versioned linkage between the historical 360-project universe "
        "and current 189 projects, followed by conservative project-level budget/settlement linkage."
    )
    write_json(PLAN_REVIEW, review)


def update_tests() -> None:
    (TESTS / "test_phase13_chiba_project_work_items_field06.py").write_text(
        FIELD06_TEST,
        encoding="utf-8",
    )

    alignment = TESTS / "test_phase13_chiba_project_work_item_alignment.py"
    text = alignment.read_text(encoding="utf-8")
    text = replace_once(text, '"structured_project_count": 160,', '"structured_project_count": 169,', "alignment structured")
    text = replace_once(text, '"pending_visual_column_confirmation_project_count": 29,', '"pending_visual_column_confirmation_project_count": 20,', "alignment pending")
    text = replace_once(text, '"structured_work_item_count": 347,', '"structured_work_item_count": 361,', "alignment work items")
    text = replace_once(text, '== 29\n', '== 20\n', "alignment pending length")
    text = replace_once(text, "test_chiba_field05_completion_advances_visual_review_to_field06", "test_chiba_field06_completion_advances_visual_review_to_field07", "alignment test name")
    text = replace_once(text, 'assert "29" in policy["remaining_work"][0]', 'assert "20" in policy["remaining_work"][0]', "alignment remaining")
    text = replace_once(text, 'assert "29" in plan["next_action"]', 'assert "20" in plan["next_action"]', "alignment next action")
    text = replace_once(
        text,
        '        "chiba-f05-",\n    )',
        '        "chiba-f05-",\n        "chiba-f06-",\n    )',
        "alignment completed fields",
    )
    alignment.write_text(text, encoding="utf-8")

    queue_test = TESTS / "test_phase13_chiba_project_work_item_visual_review_queue.py"
    text = queue_test.read_text(encoding="utf-8")
    text = text.replace("all_29_pending_projects", "all_20_pending_projects")
    text = replace_once(text, '== 29\n', '== 20\n', "queue total pending count")
    text = replace_once(
        text,
        "        9,\n        10,\n        10,",
        "        0,\n        10,\n        10,",
        "queue field counts",
    )
    text = replace_once(
        text,
        'assert sum(batch["pending_count"] for batch in queue["batches"]) == 29',
        'assert sum(batch["pending_count"] for batch in queue["batches"]) == 20',
        "queue batch sum",
    )
    text = replace_once(text, "assert len(structured_ids) == 160", "assert len(structured_ids) == 169", "queue structured IDs")
    text = replace_once(text, '"projects_structured": 160,', '"projects_structured": 169,', "queue source structured")
    text = replace_once(text, '"structured_work_items": 347,', '"structured_work_items": 361,', "queue source work items")
    text = replace_once(text, '"projects_pending_visual_column_confirmation": 29,', '"projects_pending_visual_column_confirmation": 20,', "queue source pending")
    start = text.index("def test_next_visual_batch_starts_with_field06_official_order():")
    text = text[:start] + '''def test_next_visual_batch_starts_with_field07_official_order():
    queue = load(QUEUE)

    assert queue["execution_order"] == "official_field_and_project_order"
    assert all(batch["pending_count"] == 0 for batch in queue["batches"][:6])
    assert queue["next_batch"] == {
        "field_code": "7",
        "field_name": "都市・交通",
        "pending_review_ids": [
            "chiba-f07-p006",
            "chiba-f07-p007",
            "chiba-f07-p011",
            "chiba-f07-p013",
            "chiba-f07-p017",
            "chiba-f07-p022",
            "chiba-f07-p023",
            "chiba-f07-p025",
            "chiba-f07-p029",
            "chiba-f07-p032",
        ],
    }
    assert "推定しない" in queue["resolution_rule"]
    assert "20事業" in queue["quality_boundary"]
'''
    queue_test.write_text(text, encoding="utf-8")

    policy_test = TESTS / "test_phase13_chiba_policy_indicators.py"
    text = policy_test.read_text(encoding="utf-8")
    text = replace_once(text, "test_chiba_plan_review_reflects_field05_visual_completion", "test_chiba_plan_review_reflects_field06_visual_completion", "policy test name")
    text = replace_once(text, '== 160\n', '== 169\n', "policy structured")
    text = replace_once(text, '== 29\n', '== 20\n', "policy pending")
    text = replace_once(text, '== 347\n', '== 361\n', "policy work items")
    text = replace_once(text, 'assert "29" in review["next_action"]', 'assert "20" in review["next_action"]', "policy next action")
    policy_test.write_text(text, encoding="utf-8")


def validate() -> None:
    field06 = load_json(FIELD06_REVIEW)
    items = [item for project in field06["projects"] for item in project["work_items"]]
    require(len(items) == 23, "Field06 should contain 23 work items")
    require(
        all(
            project.get("parse_status") != "pending_visual_column_confirmation"
            for project in field06["projects"]
        ),
        "Field06 still contains a pending project",
    )

    structuring = load_json(WORK_ITEM_MANIFEST)["work_item_structuring"]
    require(structuring["projects_structured"] == 169, "Global structured should be 169")
    require(
        structuring["projects_pending_visual_column_confirmation"] == 20,
        "Global pending should be 20",
    )
    require(structuring["structured_work_items"] == 361, "Global work items should be 361")
    require(len(structuring["pending_review_ids"]) == 20, "Pending ID count should be 20")
    require(
        all(
            not review_id.startswith("chiba-f06-")
            for review_id in structuring["pending_review_ids"]
        ),
        "Field06 remains pending",
    )


def main() -> None:
    promote_field06()
    update_field06_evidence()
    update_work_item_manifest()
    update_policy_manifest()
    update_plan_review()
    update_tests()
    subprocess.run([sys.executable, str(QUEUE_BUILDER)], cwd=ROOT, check=True)
    validate()


if __name__ == "__main__":
    main()
