from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIELD02 = ROOT / "data/reviewed/chiba-city/current_project_work_items_field02.json"
EVIDENCE = ROOT / "data/evidence/chiba_current_project_work_items_field02_evidence.json"
WORK_MANIFEST = ROOT / "data/catalog/chiba_current_project_work_item_review_manifest.json"
POLICY_MANIFEST = ROOT / "data/catalog/chiba_phase13_policy_review_manifest.json"
PLAN_REVIEW = ROOT / "data/reviewed/chiba-city/plan_review.json"


def item(work_item_id: str, name: str, current: str, plan: str, target: str, *, wrapped: bool = False):
    return {
        "work_item_id": work_item_id,
        "item_name": name,
        "current_text": current,
        "plan_text": plan,
        "target_text": target,
        "parse_status": "reviewed_source_wrap_preserved" if wrapped else "reviewed_structured",
    }


PROMOTIONS = {
    "chiba-f02-p001": [
        item(
            "chiba-f02-p001-w001",
            "避難計画の策定及び周知・啓発",
            "高潮対策に係る基本方針策定",
            "高潮避難計画の策定 / 市民向け周知啓発 / 避難訓練の実施2地区",
            "高潮避難計画策定 / 避難訓練の実施2地区",
            wrapped=True,
        )
    ],
    "chiba-f02-p009": [
        item(
            "chiba-f02-p009-w001",
            "亥鼻橋の架替",
            "橋梁下部工",
            "橋梁上部工 / 橋梁下部工 / 道路整備工事",
            "新橋供用開始",
            wrapped=True,
        ),
        item(
            "chiba-f02-p009-w002",
            "のぞみ橋の架替",
            "土質調査・設計",
            "用地取得 / 整地工事 / 仮桟橋設置",
            "工事着手",
            wrapped=True,
        ),
        item("chiba-f02-p009-w003", "路面下空洞調査", "72km", "60km", "132km"),
        item("chiba-f02-p009-w004", "道路の防草対策", "17,000㎡", "28,400㎡", "45,400㎡"),
    ],
    "chiba-f02-p012": [
        item(
            "chiba-f02-p012-w001",
            "管路の耐震化",
            "耐震管率72.6%",
            "整備5.84km / 管網計算、実施設計",
            "耐震管率79.2%",
            wrapped=True,
        ),
        item(
            "chiba-f02-p012-w002",
            "施設の耐震診断（大木戸浄水場）",
            "―",
            "耐震詳細診断",
            "耐震詳細診断",
        ),
    ],
    "chiba-f02-p014": [
        item(
            "chiba-f02-p014-w001",
            "市街地復興の事前準備の検討",
            "復興体制・手順の現状把握及び課題整理",
            "検討 / 方針公表",
            "方針公表",
            wrapped=True,
        )
    ],
    "chiba-f02-p016": [
        item(
            "chiba-f02-p016-w001",
            "消防団アプリの導入",
            "―",
            "仕様検討、試行運用 / 導入・運用",
            "運用",
            wrapped=True,
        )
    ],
    "chiba-f02-p019": [
        item("chiba-f02-p019-w001", "耐震性貯水槽の増設", "7基", "3基", "10基"),
        item("chiba-f02-p019-w002", "防火水槽の長寿命化 / 調査設計", "―", "3基", "3基"),
        item("chiba-f02-p019-w003", "防火水槽の長寿命化 / 補強工事", "―", "2基", "2基"),
        item(
            "chiba-f02-p019-w004",
            "可搬型小型動力ポンプ及び防災器具収納庫の整備",
            "81か所",
            "3か所",
            "84か所",
        ),
    ],
    "chiba-f02-p023": [
        item(
            "chiba-f02-p023-w001",
            "オンライン講習システムの導入・運用",
            "Web会議方式による一部講習の実施",
            "導入検討 / 導入・運用",
            "オンライン運用",
            wrapped=True,
        )
    ],
    "chiba-f02-p026": [
        item(
            "chiba-f02-p026-w001",
            "巡回指導の強化",
            "警備員4人による巡回指導",
            "海浜幕張地区の巡回強化 / 富士見地区の巡回強化",
            "警備員6人による巡回指導",
            wrapped=True,
        )
    ],
    "chiba-f02-p028": [
        item(
            "chiba-f02-p028-w001",
            "安全施設の整備",
            "区画線・防護柵等の整備",
            "整備",
            "区画線・防護柵等の整備",
        ),
        item(
            "chiba-f02-p028-w002",
            "通学路の安全対策",
            "通学路交通安全対策プログラムに基づく合同点検及び対策の実施",
            "実施",
            "通学路交通安全対策プログラムに基づく合同点検及び対策の実施",
        ),
        item("chiba-f02-p028-w003", "バリアフリー整備 / 段差解消", "整備", "整備", "整備"),
        item(
            "chiba-f02-p028-w004",
            "バリアフリー整備 / 視覚障害者誘導用ブロック",
            "整備",
            "整備",
            "整備",
        ),
        item(
            "chiba-f02-p028-w005",
            "バリアフリー整備 / 都賀駅東口エレベーター",
            "設置協議",
            "設計・整備",
            "設置完了",
        ),
        item("chiba-f02-p028-w006", "駅前広場の改良", "整備", "整備", "整備"),
        item("chiba-f02-p028-w007", "ベンチ設置", "整備", "120基", "120基"),
    ],
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, payload):
    path.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")


def patch_field02():
    payload = load(FIELD02)
    projects = {row["review_id"]: row for row in payload["projects"]}
    for review_id, work_items in PROMOTIONS.items():
        project = projects[review_id]
        assert project.get("parse_status") == "pending_visual_column_confirmation"
        project["parse_status"] = "reviewed_structured"
        project.pop("raw_table_text", None)
        project["work_items"] = work_items

    assert sum(len(v) for v in PROMOTIONS.values()) == 22
    assert len(payload["projects"]) == 31
    assert all(row.get("parse_status") != "pending_visual_column_confirmation" for row in payload["projects"])
    assert sum(len(row["work_items"]) for row in payload["projects"]) == 76

    payload["review_status"] = "reviewed_source_capture_and_structuring_complete"
    payload["structured_project_count"] = 31
    payload["pending_visual_column_confirmation_project_count"] = 0
    payload["structured_work_item_count"] = 76
    payload["reconciliation"] = {
        "field02_official_project_count": 31,
        "source_captured_projects": 31,
        "structured_projects": 31,
        "pending_visual_column_confirmation_projects": 0,
        "structured_work_items": 76,
        "pending_review_ids": [],
    }
    payload["quality_boundary"] = (
        "分野2の31事業すべてで公式事業量表をsource captureし、公式PDFレンダリング画像による"
        "視覚確認で残る9事業の列対応を確定した。31/31事業・76 work itemsをcurrent/plan/target列で"
        "structured化済み。複数行セルはsource-wrapとして原文順序を保持し、ダッシュを0へ変換せず、"
        "未確認値を推定しない。"
    )
    dump(FIELD02, payload)


def patch_evidence():
    payload = load(EVIDENCE)
    payload["review_status"] = "reviewed_source_capture_and_structuring_complete"
    payload["structured_project_count"] = 31
    payload["pending_visual_column_confirmation_project_count"] = 0
    payload["structured_work_item_count"] = 76
    payload["pending_visual_column_confirmation"] = []
    payload["visual_confirmed_promotions"] = [
        {
            "review_id": review_id,
            "source_location": location,
            "structured_work_item_count": len(PROMOTIONS[review_id]),
        }
        for review_id, location in [
            ("chiba-f02-p001", "PDF p.33"),
            ("chiba-f02-p009", "PDF pp.35-36"),
            ("chiba-f02-p012", "PDF pp.36-37"),
            ("chiba-f02-p014", "PDF pp.37-38"),
            ("chiba-f02-p016", "PDF p.40"),
            ("chiba-f02-p019", "PDF p.41"),
            ("chiba-f02-p023", "PDF pp.43-44"),
            ("chiba-f02-p026", "PDF pp.44-45"),
            ("chiba-f02-p028", "PDF pp.45-46"),
        ]
    ]
    payload["reconciliation"] = {
        "official_field02_project_count": 31,
        "source_capture_coverage": "31/31",
        "structured_project_coverage": "31/31",
        "structured_work_item_count": 76,
        "pending_project_count": 0,
        "cumulative_source_captured_projects": 61,
        "cumulative_structured_projects": 61,
        "cumulative_structured_work_items": 157,
        "cumulative_pending_visual_projects": 0,
    }
    payload["quality_boundary"] = (
        "分野2の31事業すべてを公式PDFレンダリング画像で再確認し、残る9事業をstructuredへ昇格。"
        "分野1・2の累積61事業は61/61 structured、157 work items、visual-confirmation pending 0。"
        "複数行セルの順序・ダッシュ・増分・状態値は原文どおり保持する。"
    )
    dump(EVIDENCE, payload)


def patch_manifest():
    payload = load(WORK_MANIFEST)
    structuring = payload["work_item_structuring"]
    field02_ids = set(PROMOTIONS)
    structuring["projects_structured"] = 144
    structuring["projects_pending_visual_column_confirmation"] = 45
    structuring["structured_work_items"] = 318
    structuring["pending_review_ids"] = [
        review_id for review_id in structuring["pending_review_ids"] if review_id not in field02_ids
    ]
    assert len(structuring["pending_review_ids"]) == 45
    payload["quality_boundary"] = (
        "事業identity 189/189と全189事業の公式表source captureは完了。144事業・318 work itemsは"
        "current/plan/target列を構造化し、45事業は視覚的列確認待ち。分野1・2は公式PDFレンダリング"
        "画像で残件確認を終え61/61事業をstructured化した。45事業は専用visual review queueで追跡し、"
        "未確認値を推定しない。KGI/KPI・旧計画進捗・予算決算とは別レイヤーを維持する。"
    )
    dump(WORK_MANIFEST, payload)


def patch_policy_manifest():
    payload = load(POLICY_MANIFEST)
    fact = next(row for row in payload["reviewed_facts"] if row["id"] == "chiba-current-project-work-items")
    fact["structured_project_count"] = 144
    fact["pending_visual_column_confirmation_project_count"] = 45
    fact["structured_work_item_count"] = 318
    fact["interpretation_boundary"] = (
        "全189事業の公式表source captureは完了。144事業・318 work itemsはcurrent/plan/targetを構造化済み。"
        "45事業は複数行セルの列境界を視覚確認待ちとして明示し、未確認値を推定しない。分野1・2は"
        "公式PDFレンダリング画像による残件確認を終え61/61事業をstructured化した。"
        "source capture完了をfull structuring完了とは扱わない。"
    )
    payload["remaining_work"][0] = (
        "現行第2次実施計画189事業の事業量source captureは完了。残る45事業を公式PDFの視覚確認で解消し、"
        "確認できたものだけproject-scoped work_itemsへ昇格する。"
    )
    payload["quality_boundary"] = (
        "Phase 13 Chiba review remains in progress beyond the completed project identity and source-capture layers. "
        "Project quantity source capture is 189/189 complete: 144 projects and 318 work items are structured, "
        "while 45 projects remain explicitly pending visual column confirmation. Fields 1 and 2 are fully "
        "structured at 61/61 projects after direct official-PDF rendered-page confirmation. Historical FY2024 "
        "progress remains tied to the 2023-2025 first implementation plan. Budget and settlement states remain "
        "separate. No independent policy-achievement judgment, causal attribution, version linkage, or automatic "
        "cross-city comparability is inferred."
    )
    dump(POLICY_MANIFEST, payload)


def patch_plan_review():
    payload = load(PLAN_REVIEW)
    universe = next(row for row in payload["records"] if row["id"] == "chiba-current-project-universe")
    universe["review_note"] = (
        "189事業のidentity層と事業量source captureは完了。144事業・318 work itemsを構造化、"
        "45事業を視覚列確認待ちとして別管理する。"
    )
    fact = next(row for row in payload["records"] if row["id"] == "chiba-current-project-work-items")
    fact["statement"] = (
        "現行189事業の取組項目、令和7年度末現況、計画内容、令和10年度末目標について全事業のsource captureを完了。"
        "144事業・318 work itemsを構造化し、45事業は複数行セルの列境界を視覚確認待ちとして保持する。"
    )
    fact["structured_project_count"] = 144
    fact["pending_visual_column_confirmation_project_count"] = 45
    fact["structured_work_item_count"] = 318
    fact["review_note"] = (
        "source capture完了と3列構造化完了を分離する。分野1・2は公式PDFレンダリングページ画像で"
        "残件を直接確認し61/61事業をstructured化した。残る45事業は視覚確認なしにcurrent/plan/targetを"
        "推定せず、ダッシュを0へ変換しない。"
    )
    payload["quality_boundary"] = (
        "Chiba Phase 13 has completed 189/189 project identity and project-quantity source capture. "
        "Of the current project quantity layer, 144 projects and 318 work items are structured while 45 projects "
        "remain explicitly pending visual column confirmation. Fields 1 and 2 are fully structured at 61/61 "
        "projects after direct official-PDF rendered-page review. Historical FY2024 progress remains tied to the "
        "2023-2025 first implementation plan. Policy indicators, project quantities, annual progress, budget, "
        "settlement, causal attribution, independent achievement judgments, and cross-city comparability remain "
        "distinct review units."
    )
    payload["next_action"] = (
        "Resolve the remaining 45 project-quantity records pending visual column confirmation against the official "
        "second implementation plan. Promote only visually verified current/plan/2028-target column assignments; "
        "then review versioned linkage between the historical 360-project universe and current 189 projects, "
        "followed by conservative project-level budget/settlement linkage."
    )
    dump(PLAN_REVIEW, payload)


def replace(path: str, replacements: list[tuple[str, str]]):
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    for old, new in replacements:
        if old not in text:
            raise AssertionError(f"missing replacement in {path}: {old}")
        text = text.replace(old, new)
    target.write_text(text, encoding="utf-8")


def patch_tests():
    field02_test = ROOT / "tests/test_phase13_chiba_project_work_items_field02.py"
    field02_test.write_text(
        '''from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT / "data/catalog"
REVIEWED = ROOT / "data/reviewed/chiba-city"
EVD = ROOT / "data/evidence"
IDENTITIES = CAT / "chiba_current_project_identities_field02.json"
REVIEW = REVIEWED / "current_project_work_items_field02.json"
EVIDENCE = EVD / "chiba_current_project_work_items_field02_evidence.json"
MANIFEST = CAT / "chiba_current_project_work_item_review_manifest.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_field02_source_capture_covers_all_31_identity_projects_exactly():
    identities = load(IDENTITIES)["records"]
    projects = load(REVIEW)["projects"]
    identity_pairs = {(row["review_id"], row["project_name"]) for row in identities}
    project_pairs = {(row["review_id"], row["project_name"]) for row in projects}
    assert len(identities) == len(projects) == 31
    assert len({row["review_id"] for row in projects}) == 31
    assert identity_pairs == project_pairs


def test_field02_all_31_projects_are_structured_after_visual_review():
    projects = load(REVIEW)["projects"]
    assert all(row.get("parse_status") != "pending_visual_column_confirmation" for row in projects)
    assert all(row["work_items"] for row in projects)


def test_field02_has_76_unique_complete_work_items():
    work_items = [item for project in load(REVIEW)["projects"] for item in project["work_items"]]
    ids = [item["work_item_id"] for item in work_items]
    assert len(work_items) == len(ids) == len(set(ids)) == 76
    assert all(item["item_name"].strip() for item in work_items)
    assert all(item["current_text"].strip() for item in work_items)
    assert all(item["plan_text"].strip() for item in work_items)
    assert all(item["target_text"].strip() for item in work_items)
    assert {item["parse_status"] for item in work_items} <= {
        "reviewed_structured",
        "reviewed_source_wrap_preserved",
    }


def test_field02_visual_promotions_preserve_confirmed_table_semantics():
    projects = {row["review_id"]: row for row in load(REVIEW)["projects"]}
    assert projects["chiba-f02-p001"]["work_items"][0]["plan_text"] == (
        "高潮避難計画の策定 / 市民向け周知啓発 / 避難訓練の実施2地区"
    )
    assert projects["chiba-f02-p009"]["work_items"][0]["target_text"] == "新橋供用開始"
    assert projects["chiba-f02-p012"]["work_items"][0]["plan_text"] == (
        "整備5.84km / 管網計算、実施設計"
    )
    fire = projects["chiba-f02-p019"]["work_items"]
    assert [row["current_text"] for row in fire] == ["7基", "―", "―", "81か所"]
    assert [row["target_text"] for row in fire] == ["10基", "3基", "2基", "84か所"]
    roads = projects["chiba-f02-p028"]["work_items"]
    assert len(roads) == 7
    assert roads[4]["target_text"] == "設置完了"
    assert roads[6]["plan_text"] == roads[6]["target_text"] == "120基"


def test_field02_evidence_records_complete_visual_resolution():
    evidence = load(EVIDENCE)
    assert evidence["review_status"] == "reviewed_source_capture_and_structuring_complete"
    assert evidence["structured_project_count"] == 31
    assert evidence["pending_visual_column_confirmation_project_count"] == 0
    assert evidence["structured_work_item_count"] == 76
    assert evidence["pending_visual_column_confirmation"] == []
    assert len(evidence["visual_confirmed_promotions"]) == 9
    assert sum(row["structured_work_item_count"] for row in evidence["visual_confirmed_promotions"]) == 22
    assert evidence["reconciliation"]["cumulative_structured_projects"] == 61
    assert evidence["reconciliation"]["cumulative_structured_work_items"] == 157
    assert evidence["reconciliation"]["cumulative_pending_visual_projects"] == 0


def test_field02_manifest_records_completed_field_and_current_totals():
    manifest = load(MANIFEST)
    structuring = manifest["work_item_structuring"]
    assert structuring["projects_structured"] == 144
    assert structuring["projects_pending_visual_column_confirmation"] == 45
    assert structuring["structured_work_items"] == 318
    assert all(
        not review_id.startswith("chiba-f02-")
        for review_id in structuring["pending_review_ids"]
    )
''',
        encoding="utf-8",
    )

    replace(
        "tests/test_phase13_chiba_policy_indicators.py",
        [
            ('assert work_items["structured_project_count"] == 135', 'assert work_items["structured_project_count"] == 144'),
            ('assert work_items["pending_visual_column_confirmation_project_count"] == 54', 'assert work_items["pending_visual_column_confirmation_project_count"] == 45'),
            ('assert work_items["structured_work_item_count"] == 296', 'assert work_items["structured_work_item_count"] == 318'),
            ('assert "54" in review["next_action"]', 'assert "45" in review["next_action"]'),
        ],
    )
    replace(
        "tests/test_phase13_chiba_project_work_item_alignment.py",
        [
            ('"structured_project_count": 135', '"structured_project_count": 144'),
            ('"pending_visual_column_confirmation_project_count": 54', '"pending_visual_column_confirmation_project_count": 45'),
            ('"structured_work_item_count": 296', '"structured_work_item_count": 318'),
            ('== 54', '== 45'),
            ('assert "54" in policy["remaining_work"][0]', 'assert "45" in policy["remaining_work"][0]'),
            ('assert "54" in plan["next_action"]', 'assert "45" in plan["next_action"]'),
        ],
    )
    replace(
        "tests/test_phase13_chiba_project_work_items_field01.py",
        [
            ('== 135', '== 144'),
            ('== 54', '== 45'),
            ('== 296', '== 318'),
        ],
    )
    replace(
        "tests/test_phase13_chiba_project_work_items_field08.py",
        [
            ('== 135', '== 144'),
            ('== 54', '== 45'),
            ('== 296', '== 318'),
        ],
    )

    queue_test = ROOT / "tests/test_phase13_chiba_project_work_item_visual_review_queue.py"
    text = queue_test.read_text(encoding="utf-8")
    text = text.replace("all_54_pending_projects", "all_45_pending_projects")
    text = text.replace("== 54", "== 45")
    text = text.replace("== 135", "== 144")
    text = text.replace("== 296", "== 318")
    text = text.replace('"projects_structured": 135', '"projects_structured": 144')
    text = text.replace('"structured_work_items": 296', '"structured_work_items": 318')
    text = text.replace('"projects_pending_visual_column_confirmation": 54', '"projects_pending_visual_column_confirmation": 45')
    text = text.replace("[\n        0,\n        9,\n        4,", "[\n        0,\n        0,\n        4,")
    text = re.sub(
        r"def test_next_visual_batch_starts_with_field02_official_order\(\):.*?assert \"54事業\" in queue\[\"quality_boundary\"\]",
        '''def test_next_visual_batch_starts_with_field03_official_order():
    queue = load(QUEUE)

    assert queue["execution_order"] == "official_field_and_project_order"
    assert queue["batches"][1]["pending_count"] == 0
    assert queue["batches"][1]["pending_review_ids"] == []
    assert queue["next_batch"] == {
        "field_code": "3",
        "field_name": "健康・福祉",
        "pending_review_ids": [
            "chiba-f03-p004",
            "chiba-f03-p005",
            "chiba-f03-p006",
            "chiba-f03-p007",
        ],
    }
    assert "推定しない" in queue["resolution_rule"]
    assert "45事業" in queue["quality_boundary"]''',
        text,
        flags=re.S,
    )
    queue_test.write_text(text, encoding="utf-8")


def main():
    patch_field02()
    patch_evidence()
    patch_manifest()
    patch_policy_manifest()
    patch_plan_review()
    patch_tests()


if __name__ == "__main__":
    main()
