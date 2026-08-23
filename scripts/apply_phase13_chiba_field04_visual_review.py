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

FIELD04_REVIEW = REVIEWED / "current_project_work_items_field04.json"
FIELD04_EVIDENCE = EVD / "chiba_current_project_work_items_field04_evidence.json"
WORK_ITEM_MANIFEST = CAT / "chiba_current_project_work_item_review_manifest.json"
POLICY_MANIFEST = CAT / "chiba_phase13_policy_review_manifest.json"
PLAN_REVIEW = REVIEWED / "plan_review.json"
QUEUE_BUILDER = ROOT / "scripts/build_chiba_work_item_visual_review_queue.py"

FIELD04_PROMOTIONS = {
    "chiba-f04-p001": [
        {
            "work_item_id": "chiba-f04-p001-w001",
            "item_name": "エンゼルヘルパー派遣事業の支援サービス拡充",
            "current_text": "実施",
            "plan_text": "多胎児を妊娠・出産し、かつ早産となった家庭を対象にした利用期間の延長 / 利用条件の緩和（子の入院時の利用 / 外出支援）",
            "target_text": "支援拡充",
            "parse_status": "reviewed_source_wrap_preserved",
        }
    ],
    "chiba-f04-p016": [
        {
            "work_item_id": "chiba-f04-p016-w001",
            "item_name": "西部児童相談所大規模改修",
            "current_text": "―",
            "plan_text": "改修整備計画策定 / 基本設計 / 実施設計 / 機能移転検討",
            "target_text": "実施設計完了",
            "parse_status": "reviewed_source_wrap_preserved",
        }
    ],
    "chiba-f04-p017": [
        {
            "work_item_id": "chiba-f04-p017-w001",
            "item_name": "新東部児童相談所等の整備",
            "current_text": "基本設計完了 / 実施設計着手",
            "plan_text": "実施設計 / 機能移転検討 / 新築工事",
            "target_text": "本体工事完了",
            "parse_status": "reviewed_source_wrap_preserved",
        }
    ],
    "chiba-f04-p019": [
        {
            "work_item_id": "chiba-f04-p019-w001",
            "item_name": "「（仮称）千葉市英語教育スタンダード」の策定・運用",
            "current_text": "試行版に基づく授業実施 / 課題整理",
            "plan_text": "試行版に基づく授業実施 / 全校運用実施",
            "target_text": "全校運用実施",
            "parse_status": "reviewed_source_wrap_preserved",
        },
        {
            "work_item_id": "chiba-f04-p019-w002",
            "item_name": "生成ＡＩスピーキングソフト導入・活用方法検討",
            "current_text": "実証事業 2校",
            "plan_text": "実証事業 3校 / 研究発表 / 全中学校へ導入",
            "target_text": "全中学校へ導入",
            "parse_status": "reviewed_source_wrap_preserved",
        },
    ],
    "chiba-f04-p021": [
        {
            "work_item_id": "chiba-f04-p021-w001",
            "item_name": "冷暖房設備の設計",
            "current_text": "実施設計59校",
            "plan_text": "基本設計・実施設計108校",
            "target_text": "実施設計 全校完了",
            "parse_status": "reviewed_structured",
        },
        {
            "work_item_id": "chiba-f04-p021-w002",
            "item_name": "冷暖房設備の整備工事",
            "current_text": "整備工事30校",
            "plan_text": "整備工事110校",
            "target_text": "整備工事140校完了",
            "parse_status": "reviewed_structured",
        },
    ],
    "chiba-f04-p022": [
        {
            "work_item_id": "chiba-f04-p022-w001",
            "item_name": "ＣＡＢＩＮＥＴ整備計画の策定",
            "current_text": "―",
            "plan_text": "技術動向や現状の問題点等の調査・分析 / 整備計画策定",
            "target_text": "ＣＡＢＩＮＥＴ調達契約完了",
            "parse_status": "reviewed_source_wrap_preserved",
        }
    ],
    "chiba-f04-p025": [
        {
            "work_item_id": "chiba-f04-p025-w001",
            "item_name": "学校適正規模・適正配置の推進",
            "current_text": "実施方針改訂",
            "plan_text": "実施方針改訂等の周知 / 実施",
            "target_text": "実施",
            "parse_status": "reviewed_source_wrap_preserved",
        }
    ],
    "chiba-f04-p026": [
        {
            "work_item_id": "chiba-f04-p026-w001",
            "item_name": "既存施設の一部解体（プール、武道場ほか）",
            "current_text": "実施設計",
            "plan_text": "解体工事",
            "target_text": "解体工事完了",
            "parse_status": "reviewed_structured",
        },
        {
            "work_item_id": "chiba-f04-p026-w002",
            "item_name": "校舎及び体育館の改修",
            "current_text": "―",
            "plan_text": "基本設計 / 実施設計 / 大規模改造工事",
            "target_text": "大規模改造工事",
            "parse_status": "reviewed_source_wrap_preserved",
        },
    ],
}

FIELD04_PROMOTION_METADATA = [
    ("chiba-f04-p001", "在宅の子育て家庭への支援", "PDF p.66", 1),
    ("chiba-f04-p016", "西部児童相談所の大規模改修", "PDF p.72", 1),
    (
        "chiba-f04-p017",
        "新東部児童相談所及び発達に係る相談支援機関等の整備",
        "PDF p.72",
        1,
    ),
    ("chiba-f04-p019", "外国語教育の推進", "PDF p.75", 2),
    ("chiba-f04-p021", "市立学校の体育館冷暖房設備の整備", "PDF p.76", 2),
    ("chiba-f04-p022", "第4次ＣＡＢＩＮＥＴの整備", "PDF p.76", 1),
    ("chiba-f04-p025", "学校適正規模・適正配置", "PDF p.77", 1),
    ("chiba-f04-p026", "学びの多様化学校の整備", "PDF p.78", 2),
]

FIELD04_TEST = '''from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT / "data/catalog"
REVIEWED = ROOT / "data/reviewed/chiba-city"
EVD = ROOT / "data/evidence"
IDENTITIES = CAT / "chiba_current_project_identities_field04.json"
REVIEW = REVIEWED / "current_project_work_items_field04.json"
EVIDENCE = EVD / "chiba_current_project_work_items_field04_evidence.json"
MANIFEST = CAT / "chiba_current_project_work_item_review_manifest.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_field04_source_capture_covers_all_34_identity_projects_exactly():
    identities = load(IDENTITIES)["records"]
    projects = load(REVIEW)["projects"]
    identity_pairs = {(row["review_id"], row["project_name"]) for row in identities}
    project_pairs = {(row["review_id"], row["project_name"]) for row in projects}

    assert len(identities) == len(projects) == 34
    assert len({row["review_id"] for row in projects}) == 34
    assert identity_pairs == project_pairs


def test_field04_measure_codes_and_source_locations_match_identity_layer():
    identities = {row["review_id"]: row for row in load(IDENTITIES)["records"]}
    for project in load(REVIEW)["projects"]:
        identity = identities[project["review_id"]]
        assert project["measure_code"] == identity["measure_code"]
        assert project["source_location"] == identity["source_location"]


def test_field04_all_34_projects_are_structured_after_visual_review():
    projects = load(REVIEW)["projects"]

    assert all(
        row.get("parse_status") != "pending_visual_column_confirmation"
        for row in projects
    )
    assert all(row["work_items"] for row in projects)


def test_field04_has_64_unique_complete_work_items():
    work_items = [
        item
        for project in load(REVIEW)["projects"]
        for item in project["work_items"]
    ]
    ids = [item["work_item_id"] for item in work_items]

    assert len(work_items) == len(ids) == len(set(ids)) == 64
    assert all(item["item_name"].strip() for item in work_items)
    assert all(item["current_text"].strip() for item in work_items)
    assert all(item["plan_text"].strip() for item in work_items)
    assert all(item["target_text"].strip() for item in work_items)
    assert {item["parse_status"] for item in work_items} <= {
        "reviewed_structured",
        "reviewed_source_wrap_preserved",
    }


def test_field04_visual_promotions_preserve_confirmed_table_semantics():
    projects = {row["review_id"]: row for row in load(REVIEW)["projects"]}

    helper = projects["chiba-f04-p001"]["work_items"][0]
    assert helper["current_text"] == "実施"
    assert helper["plan_text"] == (
        "多胎児を妊娠・出産し、かつ早産となった家庭を対象にした利用期間の延長 / "
        "利用条件の緩和（子の入院時の利用 / 外出支援）"
    )
    assert helper["target_text"] == "支援拡充"

    west = projects["chiba-f04-p016"]["work_items"][0]
    assert west["current_text"] == "―"
    assert west["plan_text"] == "改修整備計画策定 / 基本設計 / 実施設計 / 機能移転検討"
    assert west["target_text"] == "実施設計完了"

    east = projects["chiba-f04-p017"]["work_items"][0]
    assert east["current_text"] == "基本設計完了 / 実施設計着手"
    assert east["plan_text"] == "実施設計 / 機能移転検討 / 新築工事"
    assert east["target_text"] == "本体工事完了"

    english = projects["chiba-f04-p019"]["work_items"]
    assert english[0]["current_text"] == "試行版に基づく授業実施 / 課題整理"
    assert english[0]["plan_text"] == "試行版に基づく授業実施 / 全校運用実施"
    assert english[0]["target_text"] == "全校運用実施"
    assert english[1]["current_text"] == "実証事業 2校"
    assert english[1]["plan_text"] == "実証事業 3校 / 研究発表 / 全中学校へ導入"
    assert english[1]["target_text"] == "全中学校へ導入"

    hvac = projects["chiba-f04-p021"]["work_items"]
    assert (hvac[0]["current_text"], hvac[0]["plan_text"], hvac[0]["target_text"]) == (
        "実施設計59校",
        "基本設計・実施設計108校",
        "実施設計 全校完了",
    )
    assert (hvac[1]["current_text"], hvac[1]["plan_text"], hvac[1]["target_text"]) == (
        "整備工事30校",
        "整備工事110校",
        "整備工事140校完了",
    )

    cabinet = projects["chiba-f04-p022"]["work_items"][0]
    assert cabinet["current_text"] == "―"
    assert cabinet["plan_text"] == "技術動向や現状の問題点等の調査・分析 / 整備計画策定"
    assert cabinet["target_text"] == "ＣＡＢＩＮＥＴ調達契約完了"

    placement = projects["chiba-f04-p025"]["work_items"][0]
    assert placement["current_text"] == "実施方針改訂"
    assert placement["plan_text"] == "実施方針改訂等の周知 / 実施"
    assert placement["target_text"] == "実施"

    diverse = projects["chiba-f04-p026"]["work_items"]
    assert (diverse[0]["current_text"], diverse[0]["plan_text"], diverse[0]["target_text"]) == (
        "実施設計",
        "解体工事",
        "解体工事完了",
    )
    assert diverse[1]["current_text"] == "―"
    assert diverse[1]["plan_text"] == "基本設計 / 実施設計 / 大規模改造工事"
    assert diverse[1]["target_text"] == "大規模改造工事"


def test_field04_existing_increment_annual_and_transition_semantics_remain_intact():
    projects = {row["review_id"]: row for row in load(REVIEW)["projects"]}

    childcare = projects["chiba-f04-p005"]["work_items"]
    assert childcare[0]["current_text"] == "54か所"
    assert childcare[0]["plan_text"] == "5か所増"
    assert childcare[0]["target_text"] == "59か所"
    assert childcare[5]["plan_text"] == "2件/年"

    temporary = projects["chiba-f04-p008"]["work_items"][0]
    assert temporary["current_text"] == "77か所（一般型33か所、余裕活用型44か所）"
    assert temporary["target_text"] == "86か所（一般型36か所、余裕活用型50か所）"

    club = projects["chiba-f04-p031"]["work_items"][0]
    assert club["current_text"] == "実証事業実施 / 課題整理・在り方検討"
    assert club["plan_text"] == club["target_text"] == "本格実施"

    support = projects["chiba-f04-p033"]["work_items"][2]
    assert support["current_text"] == "20校"
    assert support["plan_text"] == "4校増"
    assert support["target_text"] == "14校（アフタースクール10校移行）"


def test_field04_dash_variants_are_preserved_not_converted_to_zero():
    work_items = [
        item
        for project in load(REVIEW)["projects"]
        for item in project["work_items"]
    ]
    dash_items = [item for item in work_items if item["current_text"] in {"―", "－"}]

    assert len(dash_items) >= 15
    assert all(item["current_text"] != "0" for item in dash_items)


def test_field04_evidence_records_complete_visual_resolution():
    evidence = load(EVIDENCE)
    promotions = evidence["visual_confirmed_promotions"]

    assert evidence["review_status"] == "reviewed_source_capture_and_structuring_complete"
    assert evidence["structured_project_count"] == 34
    assert evidence["pending_visual_column_confirmation_project_count"] == 0
    assert evidence["structured_work_item_count"] == 64
    assert evidence["pending_visual_column_confirmation"] == []
    assert len(promotions) == 8
    assert sum(row["structured_work_item_count"] for row in promotions) == 11
    assert evidence["reconciliation"]["cumulative_structured_projects"] == 113
    assert evidence["reconciliation"]["cumulative_structured_work_items"] == 254
    assert evidence["reconciliation"]["cumulative_pending_visual_projects"] == 0


def test_field04_manifest_records_completed_field_and_current_progress():
    manifest = load(MANIFEST)
    structuring = manifest["work_item_structuring"]

    assert structuring["projects_structured"] >= 156
    assert structuring["projects_pending_visual_column_confirmation"] <= 33
    assert structuring["structured_work_items"] >= 339
    assert all(
        not review_id.startswith("chiba-f04-")
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


def promote_field04() -> None:
    payload = load_json(FIELD04_REVIEW)
    require(payload["structured_project_count"] == 26, "Unexpected field04 structured pre-state")
    require(
        payload["pending_visual_column_confirmation_project_count"] == 8,
        "Unexpected field04 pending pre-state",
    )
    require(payload["structured_work_item_count"] == 53, "Unexpected field04 work-item pre-state")

    by_id = {row["review_id"]: row for row in payload["projects"]}
    require(set(FIELD04_PROMOTIONS) <= set(by_id), "Field04 promotion IDs missing")

    for review_id, work_items in FIELD04_PROMOTIONS.items():
        project = by_id[review_id]
        require(
            project.get("parse_status") == "pending_visual_column_confirmation",
            f"{review_id} is not pending as expected",
        )
        project["parse_status"] = "reviewed_structured"
        project.pop("raw_table_text", None)
        project["work_items"] = work_items

    payload["review_status"] = "reviewed_source_capture_and_structuring_complete"
    payload["structured_project_count"] = 34
    payload["pending_visual_column_confirmation_project_count"] = 0
    payload["structured_work_item_count"] = 64
    payload["quality_boundary"] = (
        "分野4の34 identityすべてについて公式表をsource captureし、8件の視覚確認待ちも"
        "公式PDFレンダリング画像で列対応を直接確認した。34/34事業・64 work itemsを"
        "current/plan/target列で構造化済み。複数行セルは原文順序を保持し、ダッシュを0へ"
        "変換しない。再掲事業はidentity母集団へ重複追加しない。"
    )
    write_json(FIELD04_REVIEW, payload)


def update_field04_evidence() -> None:
    evidence = load_json(FIELD04_EVIDENCE)
    evidence["review_status"] = "reviewed_source_capture_and_structuring_complete"
    evidence["structured_project_count"] = 34
    evidence["pending_visual_column_confirmation_project_count"] = 0
    evidence["structured_work_item_count"] = 64
    evidence["pending_visual_column_confirmation"] = []
    evidence["visual_confirmed_promotions"] = [
        {
            "review_id": review_id,
            "project_name": project_name,
            "source_location": source_location,
            "structured_work_item_count": work_item_count,
        }
        for review_id, project_name, source_location, work_item_count in FIELD04_PROMOTION_METADATA
    ]
    evidence["reconciliation"] = {
        "official_field04_project_count": 34,
        "source_capture_coverage": "34/34",
        "structured_project_coverage": "34/34",
        "structured_work_item_count": 64,
        "pending_project_count": 0,
        "cumulative_source_captured_projects": 113,
        "cumulative_structured_projects": 113,
        "cumulative_structured_work_items": 254,
        "cumulative_pending_visual_projects": 0,
    }
    evidence["quality_boundary"] = (
        "分野4の34事業すべての公式事業量表を確認し、PDF p.66, p.72, p.75-78の"
        "レンダリング画像で8保留事業のcurrent/plan/target列を直接確定した。分野1～4"
        "累計113事業は全件structured、254 work items、visual-confirmation pending 0。"
        "複数行セルはsource-wrapとして順序を保持し、ダッシュや原表上の計画関係を補正しない。"
    )
    write_json(FIELD04_EVIDENCE, evidence)


def update_work_item_manifest() -> None:
    manifest = load_json(WORK_ITEM_MANIFEST)
    structuring = manifest["work_item_structuring"]
    require(structuring["projects_structured"] == 148, "Unexpected global structured pre-state")
    require(
        structuring["projects_pending_visual_column_confirmation"] == 41,
        "Unexpected global pending pre-state",
    )
    require(structuring["structured_work_items"] == 328, "Unexpected global work-item pre-state")

    pending = [
        review_id
        for review_id in structuring["pending_review_ids"]
        if not review_id.startswith("chiba-f04-")
    ]
    require(len(pending) == 33, "Unexpected post-field04 pending ID count")
    structuring["projects_structured"] = 156
    structuring["projects_pending_visual_column_confirmation"] = 33
    structuring["structured_work_items"] = 339
    structuring["pending_review_ids"] = pending
    manifest["quality_boundary"] = (
        "事業identity 189/189と全189事業の公式表source captureは完了。156事業・339 work "
        "itemsはcurrent/plan/target列を構造化し、33事業は視覚的列確認待ち。分野1～4は"
        "公式PDFレンダリング画像で残件確認を終え113/113事業をstructured化した。33事業は"
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
    fact["structured_project_count"] = 156
    fact["pending_visual_column_confirmation_project_count"] = 33
    fact["structured_work_item_count"] = 339
    fact["interpretation_boundary"] = (
        "全189事業の公式表source captureは完了。156事業・339 work itemsはcurrent/plan/targetを"
        "構造化済み。33事業は複数行セルの列境界を視覚確認待ちとして明示し、未確認値を推定しない。"
        "分野1～4は公式PDFレンダリング画像による残件確認を終え113/113事業をstructured化した。"
        "source capture完了をfull structuring完了とは扱わない。"
    )
    manifest["remaining_work"][0] = (
        "現行第2次実施計画189事業の事業量source captureは完了。残る33事業を公式PDFの"
        "視覚確認で解消し、確認できたものだけproject-scoped work_itemsへ昇格する。"
    )
    manifest["quality_boundary"] = (
        "Phase 13 Chiba review remains in progress beyond the completed project identity and "
        "source-capture layers. Project quantity source capture is 189/189 complete: 156 projects "
        "and 339 work items are structured, while 33 projects remain explicitly pending visual "
        "column confirmation. Fields 1 through 4 are fully structured at 113/113 projects after "
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
        "189事業のidentity層と事業量source captureは完了。156事業・339 work itemsを構造化、"
        "33事業を視覚列確認待ちとして別管理する。"
    )

    work_items = next(
        row for row in review["records"] if row["id"] == "chiba-current-project-work-items"
    )
    work_items["statement"] = (
        "現行189事業の取組項目、令和7年度末現況、計画内容、令和10年度末目標について全事業の"
        "source captureを完了。156事業・339 work itemsを構造化し、33事業は複数行セルの列境界を"
        "視覚確認待ちとして保持する。"
    )
    work_items["structured_project_count"] = 156
    work_items["pending_visual_column_confirmation_project_count"] = 33
    work_items["structured_work_item_count"] = 339
    work_items["review_note"] = (
        "source capture完了と3列構造化完了を分離する。分野1～4は公式PDFレンダリングページ画像で"
        "残件を直接確認し113/113事業をstructured化した。残る33事業は視覚確認なしに"
        "current/plan/targetを推定せず、ダッシュを0へ変換しない。"
    )
    review["quality_boundary"] = (
        "Chiba Phase 13 has completed 189/189 project identity and project-quantity source capture. "
        "Of the current project quantity layer, 156 projects and 339 work items are structured while "
        "33 projects remain explicitly pending visual column confirmation. Fields 1 through 4 are "
        "fully structured at 113/113 projects after direct official-PDF rendered-page review. "
        "Historical FY2024 progress remains tied to the 2023-2025 first implementation plan. Policy "
        "indicators, project quantities, annual progress, budget, settlement, causal attribution, "
        "independent achievement judgments, and cross-city comparability remain distinct review units."
    )
    review["next_action"] = (
        "Resolve the remaining 33 project-quantity records pending visual column confirmation against "
        "the official second implementation plan. Promote only visually verified current/plan/2028-target "
        "column assignments; then review versioned linkage between the historical 360-project universe "
        "and current 189 projects, followed by conservative project-level budget/settlement linkage."
    )
    write_json(PLAN_REVIEW, review)


def update_tests() -> None:
    (TESTS / "test_phase13_chiba_project_work_items_field04.py").write_text(
        FIELD04_TEST,
        encoding="utf-8",
    )

    alignment = TESTS / "test_phase13_chiba_project_work_item_alignment.py"
    text = alignment.read_text(encoding="utf-8")
    text = replace_once(text, '"structured_project_count": 148,', '"structured_project_count": 156,', "alignment structured count")
    text = replace_once(text, '"pending_visual_column_confirmation_project_count": 41,', '"pending_visual_column_confirmation_project_count": 33,', "alignment pending count")
    text = replace_once(text, '"structured_work_item_count": 328,', '"structured_work_item_count": 339,', "alignment work-item count")
    text = replace_once(text, '== 41\n', '== 33\n', "alignment pending length")
    text = replace_once(
        text,
        "def test_chiba_field03_completion_advances_visual_review_to_field04():",
        "def test_chiba_field04_completion_advances_visual_review_to_field05():",
        "alignment test name",
    )
    text = replace_once(text, 'assert "41" in policy["remaining_work"][0]', 'assert "33" in policy["remaining_work"][0]', "alignment policy remaining")
    text = replace_once(text, 'assert "41" in plan["next_action"]', 'assert "33" in plan["next_action"]', "alignment plan remaining")
    text = replace_once(
        text,
        'not review_id.startswith(("chiba-f01-", "chiba-f02-", "chiba-f03-"))',
        'not review_id.startswith(("chiba-f01-", "chiba-f02-", "chiba-f03-", "chiba-f04-"))',
        "alignment completed field prefixes",
    )
    alignment.write_text(text, encoding="utf-8")

    queue_test = TESTS / "test_phase13_chiba_project_work_item_visual_review_queue.py"
    text = queue_test.read_text(encoding="utf-8")
    text = text.replace("all_41_pending_projects", "all_33_pending_projects")
    text = replace_once(text, "== 41\n", "== 33\n", "queue total pending count")
    text = replace_once(
        text,
        "        0,\n        0,\n        0,\n        8,\n        4,\n        9,\n        10,\n        10,",
        "        0,\n        0,\n        0,\n        0,\n        4,\n        9,\n        10,\n        10,",
        "queue batch counts",
    )
    text = replace_once(
        text,
        'assert sum(batch["pending_count"] for batch in queue["batches"]) == 41',
        'assert sum(batch["pending_count"] for batch in queue["batches"]) == 33',
        "queue batch sum",
    )
    text = replace_once(text, "assert len(structured_ids) == 148", "assert len(structured_ids) == 156", "queue structured IDs")
    text = replace_once(text, '"projects_structured": 148,', '"projects_structured": 156,', "queue source structured")
    text = replace_once(text, '"structured_work_items": 328,', '"structured_work_items": 339,', "queue source work items")
    text = replace_once(text, '"projects_pending_visual_column_confirmation": 41,', '"projects_pending_visual_column_confirmation": 33,', "queue source pending")
    start = text.index("def test_next_visual_batch_starts_with_field04_official_order():")
    text = text[:start] + '''def test_next_visual_batch_starts_with_field05_official_order():
    queue = load(QUEUE)

    assert queue["execution_order"] == "official_field_and_project_order"
    assert all(batch["pending_count"] == 0 for batch in queue["batches"][:4])
    assert queue["next_batch"] == {
        "field_code": "5",
        "field_name": "地域社会",
        "pending_review_ids": [
            "chiba-f05-p001",
            "chiba-f05-p003",
            "chiba-f05-p006",
            "chiba-f05-p007",
        ],
    }
    assert "推定しない" in queue["resolution_rule"]
    assert "33事業" in queue["quality_boundary"]
'''
    queue_test.write_text(text, encoding="utf-8")

    policy_test = TESTS / "test_phase13_chiba_policy_indicators.py"
    text = policy_test.read_text(encoding="utf-8")
    text = replace_once(
        text,
        "def test_chiba_plan_review_reflects_field03_visual_completion():",
        "def test_chiba_plan_review_reflects_field04_visual_completion():",
        "policy test name",
    )
    text = replace_once(text, '== 148\n', '== 156\n', "policy test structured")
    text = replace_once(text, '== 41\n', '== 33\n', "policy test pending")
    text = replace_once(text, '== 328\n', '== 339\n', "policy test work items")
    text = replace_once(text, 'assert "41" in review["next_action"]', 'assert "33" in review["next_action"]', "policy next action")
    policy_test.write_text(text, encoding="utf-8")


def validate() -> None:
    field04 = load_json(FIELD04_REVIEW)
    work_manifest = load_json(WORK_ITEM_MANIFEST)
    policy = load_json(POLICY_MANIFEST)
    plan = load_json(PLAN_REVIEW)

    field04_items = [
        item for project in field04["projects"] for item in project["work_items"]
    ]
    require(len(field04_items) == 64, "Field04 should contain 64 work items")
    require(
        all(
            project.get("parse_status") != "pending_visual_column_confirmation"
            for project in field04["projects"]
        ),
        "Field04 still contains a pending project",
    )

    structuring = work_manifest["work_item_structuring"]
    require(structuring["projects_structured"] == 156, "Global structured count should be 156")
    require(
        structuring["projects_pending_visual_column_confirmation"] == 33,
        "Global pending count should be 33",
    )
    require(structuring["structured_work_items"] == 339, "Global work-item count should be 339")
    require(len(structuring["pending_review_ids"]) == 33, "Pending ID count should be 33")
    require(
        all(not review_id.startswith("chiba-f04-") for review_id in structuring["pending_review_ids"]),
        "Field04 ID remains in global pending list",
    )

    policy_fact = next(
        row for row in policy["reviewed_facts"] if row["id"] == "chiba-current-project-work-items"
    )
    plan_fact = next(
        row for row in plan["records"] if row["id"] == "chiba-current-project-work-items"
    )
    for fact in (policy_fact, plan_fact):
        require(fact["structured_project_count"] == 156, "Control layer structured mismatch")
        require(
            fact["pending_visual_column_confirmation_project_count"] == 33,
            "Control layer pending mismatch",
        )
        require(fact["structured_work_item_count"] == 339, "Control layer work-item mismatch")


def main() -> None:
    promote_field04()
    update_field04_evidence()
    update_work_item_manifest()
    update_policy_manifest()
    update_plan_review()
    update_tests()
    subprocess.run([sys.executable, str(QUEUE_BUILDER)], cwd=ROOT, check=True)
    validate()


if __name__ == "__main__":
    main()
