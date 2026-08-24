from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT / "data/catalog"
REVIEWED = ROOT / "data/reviewed/chiba-city"
EVD = ROOT / "data/evidence"

IDENTITIES = CAT / "chiba_current_project_identities_field08.json"
REVIEW = REVIEWED / "current_project_work_items_field08.json"
EVIDENCE = EVD / "chiba_current_project_work_items_field08_evidence.json"
MANIFEST = CAT / "chiba_current_project_work_item_review_manifest.json"
QUEUE = CAT / "chiba_current_project_work_item_visual_review_queue.json"
POLICY_MANIFEST = CAT / "chiba_phase13_policy_review_manifest.json"
PLAN_REVIEW = REVIEWED / "plan_review.json"
QUEUE_BUILDER = ROOT / "scripts/build_chiba_work_item_visual_review_queue.py"

FIELD08_TEST = ROOT / "tests/test_phase13_chiba_project_work_items_field08.py"
QUEUE_TEST = ROOT / "tests/test_phase13_chiba_project_work_item_visual_review_queue.py"
ALIGNMENT_TEST = ROOT / "tests/test_phase13_chiba_project_work_item_alignment.py"
POLICY_TEST = ROOT / "tests/test_phase13_chiba_policy_indicators.py"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, payload) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )


def item(name: str, current: str, plan: str, target: str, wrapped: bool = False):
    return {
        "item_name": name,
        "current_text": current,
        "plan_text": plan,
        "target_text": target,
        "parse_status": "reviewed_source_wrap_preserved" if wrapped else "reviewed_structured",
    }


PROMOTIONS = {
    "chiba-f08-p004": [
        item(
            "販売力向上支援の強化",
            "販売力向上支援",
            "制度拡充 / 助成６件",
            "制度拡充 / 助成６件",
            True,
        )
    ],
    "chiba-f08-p006": [
        item(
            "市場施設の再整備",
            "検討",
            "事業者公募・選定 / 調査・設計",
            "再整備の着工",
            True,
        )
    ],
    "chiba-f08-p008": [
        item(
            "人手不足業種の資格取得費用助成",
            "50件/年",
            "10件/年増 / 対象資格の拡充",
            "60件/年 / 対象資格の拡充",
            True,
        ),
        item(
            "中小企業の研修費用助成",
            "通常支援10件/年 / 拡充支援20件/年",
            "制度の見直し / 見直し後の拡充支援20件/年",
            "制度の見直し / 見直し後の拡充支援20件/年",
            True,
        ),
        item(
            "高校生向けキャリア形成支援",
            "―",
            "セミナー開催２回/年",
            "セミナー開催２回/年",
        ),
    ],
    "chiba-f08-p009": [
        item(
            "高校生海外・国内派遣プログラム",
            "事前国内研修プログラムの実施",
            "高校生海外・国内派遣プログラムの実施２回 / 事前国内研修プログラムの実施１回",
            "プログラムの定着 / １年目：国内研修 / ２年目：海外・国内派遣 / 研修の２か年プログラム",
            True,
        ),
        item(
            "プログラム内容の改良",
            "プログラム７件 / 出前授業９校",
            "プログラムの改良１件/年",
            "プログラムの改良１件/年",
            True,
        ),
    ],
    "chiba-f08-p010": [
        item(
            "異業種連携による観光コンテンツの造成",
            "３件/年",
            "１件/年増",
            "４件/年",
        ),
        item(
            "スポーツツーリズムの推進",
            "―",
            "サポーターおもてなし事業の実施",
            "サポーターおもてなし事業の実施",
        ),
        item(
            "グリーンツーリズムの推進",
            "イベント開催・出展２回/年",
            "サイクリングマップの改訂 / イベント開催・出展回数１回/年増",
            "千葉市里山サイクリングマップの改訂 / イベント開催・出展３回/年",
            True,
        ),
        item(
            "若者参画による観光プランの造成",
            "―",
            "造成",
            "造成",
        ),
    ],
    "chiba-f08-p011": [
        item(
            "インセンティブ施策の強化（団体旅行者）",
            "インバウンド団体バスツアー造成支援金交付数30件/年",
            "ＯＴＡサイトでの市内ツアー販売支援事業15件",
            "ＯＴＡサイトでの市内ツアー販売支援事業５件/年",
        ),
        item(
            "インバウンド向けプロモーションの実施",
            "現状分析と課題整理",
            "千葉市観光ビジョン策定とそれに基づくプロモーション施策の検討 / プロモーション施策の実施",
            "プロモーション施策の実施",
            True,
        ),
    ],
    "chiba-f08-p013": [
        item(
            "アフターコンベンション補助の拡充及び造成・ＰＲ",
            "―",
            "補助拡充 / 造成・ＰＲ",
            "補助拡充",
            True,
        ),
        item(
            "ビッグデータの活用による観光客動向分析",
            "―",
            "分析結果を踏まえた取組み",
            "観光客動向分析実施",
        ),
    ],
    "chiba-f08-p014": [
        item(
            "販路拡大支援",
            "カタログギフト制作",
            "有力店での販売会１回/年 / カタログギフトの自走 / バイヤー・消費者ツアー各１回/年",
            "有力店での販売会１回/年 / カタログギフトの自走 / バイヤー・消費者ツアーの実施 各１回/年",
            True,
        ),
        item(
            "ブランド認知度向上",
            "認定証授与式及び販売会の実施 / プロモーション支援５件/年",
            "認定証授与式＆販売会の規模拡大 / プロモーション支援５件/年増",
            "認定証授与式＆販売会の規模拡大 / プロモーション支援10件/年",
            True,
        ),
        item(
            "認定品の創出支援",
            "６次産業化商品開発補助１件/年",
            "６次産業化商品開発補助１件/年増",
            "６次産業化商品開発補助２件/年",
        ),
    ],
    "chiba-f08-p021": [
        item(
            "道路整備",
            "道路1,471m",
            "下水道施設整備 / 道路160m",
            "道路1,631m",
            True,
        )
    ],
    "chiba-f08-p022": [
        item(
            "千葉市森林振興ビジョンの策定とこれに基づいた森林整備",
            "―",
            "基礎調査及び森林評価 / 施業内容設計 / 森林整備",
            "森林整備",
            True,
        ),
        item(
            "放置竹林対策",
            "活動組織支援２組織",
            "竹粉砕機貸出の実施 / 活動組織用粉砕機購入補助３台 / 活動組織支援２組織増",
            "竹粉砕機貸出の実施 / 活動組織用粉砕機購入補助３台 / 活動組織支援４組織",
            True,
        ),
    ],
}

PRINTED_PAGE_BY_PENDING = {
    "chiba-f08-p004": 123,
    "chiba-f08-p006": 123,
    "chiba-f08-p008": 124,
    "chiba-f08-p009": 124,
    "chiba-f08-p010": 126,
    "chiba-f08-p011": 127,
    "chiba-f08-p013": 128,
    "chiba-f08-p014": 129,
    "chiba-f08-p021": 133,
    "chiba-f08-p022": 133,
}


def normalize_source_location(row: dict) -> None:
    match = re.fullmatch(r"PDF p\.(\d+)", row["source_location"])
    if match is None:
        raise ValueError(f"Unexpected source location: {row['source_location']}")
    printed = int(match.group(1))
    row["source_printed_page"] = printed
    row["source_location"] = f"PDF p.{printed + 3}"


def normalize_identity_layer(payload: dict) -> None:
    for row in payload["records"]:
        normalize_source_location(row)
    for row in payload.get("displayed_reposts", []):
        normalize_source_location(row)
        if row.get("repost_type") == "same_field_repost":
            match = re.match(r"PDF p\.(\d+)(.*)", row.get("primary_source_location", ""))
            if match:
                row["primary_source_location"] = f"PDF p.{int(match.group(1)) + 3}{match.group(2)}"


def promote_review(payload: dict) -> None:
    projects = {row["review_id"]: row for row in payload["projects"]}
    assert set(PROMOTIONS).issubset(projects)

    for project in payload["projects"]:
        normalize_source_location(project)

    for review_id, work_items in PROMOTIONS.items():
        project = projects[review_id]
        assert project["parse_status"] == "pending_visual_column_confirmation"
        assert project["source_printed_page"] == PRINTED_PAGE_BY_PENDING[review_id]
        project["parse_status"] = "reviewed_structured"
        project.pop("raw_table_text", None)
        project["work_items"] = []
        for index, source_item in enumerate(work_items, start=1):
            record = dict(source_item)
            record["work_item_id"] = f"{review_id}-w{index:03d}"
            project["work_items"].append(record)

    all_items = [item for project in payload["projects"] for item in project["work_items"]]
    assert len(payload["projects"]) == 22
    assert len(all_items) == 48
    assert not [
        project
        for project in payload["projects"]
        if project["parse_status"] == "pending_visual_column_confirmation"
    ]

    payload["review_status"] = "reviewed_source_capture_and_structuring_complete"
    payload["structured_project_count"] = 22
    payload["pending_visual_column_confirmation_project_count"] = 0
    payload["structured_work_item_count"] = 48
    payload["quality_boundary"] = (
        "分野8の22事業すべての公式事業量表を確認し、最後の10事業はSHA-256固定済み公式PDFから"
        "再レンダリングした実ページを直接確認してcurrent/plan/target列を確定した。22/22事業・"
        "48 work itemsをstructured化し、visual-confirmation pendingは0。印刷ページとPDF実ページの"
        "ずれを明示し、既存source_location規則へ正規化した。増分・年間値・工程状態・ダッシュは"
        "原文の意味を保持し、独自達成度へ変換しない。"
    )


def update_evidence(payload: dict, review_payload: dict) -> None:
    projects = {row["review_id"]: row for row in review_payload["projects"]}
    payload["review_status"] = "reviewed_source_capture_and_structuring_complete"
    payload["structured_project_count"] = 22
    payload["pending_visual_column_confirmation_project_count"] = 0
    payload["structured_work_item_count"] = 48
    payload["pending_visual_column_confirmation"] = []
    payload["reconciliation"] = {
        "official_field08_project_count": 22,
        "source_capture_coverage": "22/22",
        "structured_project_coverage": "22/22",
        "structured_work_item_count": 48,
        "pending_project_count": 0,
        "cumulative_source_captured_projects": 189,
        "cumulative_structured_projects": 189,
        "cumulative_structured_work_items": 406,
        "cumulative_pending_visual_projects": 0,
    }
    payload["quality_boundary"] = (
        "分野8の22事業すべての公式事業量表を確認し、残る10事業はSHA-256固定済み公式PDFの"
        "再レンダリング実ページを直接確認して列対応を確定した。これにより分野1～8累計189/189事業、"
        "406 work itemsをstructured化し、visual-confirmation pendingは0となった。再掲を重複identity"
        "として数えず、ダッシュを0へ変換せず、政策成果・因果効果・達成度を事業量から推定しない。"
    )
    payload["source_location_semantics"] = (
        "source_location follows the repository's existing zero-based PDF page-index convention; "
        "source_printed_page preserves the page number printed in the official booklet. For this PDF, "
        "Field 8 printed pages map to source_location index printed+3 and pdftoppm physical page printed+4."
    )
    payload["source_printed_page_range"] = "121-133"
    payload["source_pdf_index_range"] = "124-136"
    payload["visual_confirmed_promotions"] = [
        {
            "review_id": review_id,
            "project_name": projects[review_id]["project_name"],
            "source_location": projects[review_id]["source_location"],
            "source_printed_page": PRINTED_PAGE_BY_PENDING[review_id],
            "rendered_physical_page": PRINTED_PAGE_BY_PENDING[review_id] + 4,
            "structured_work_item_count": len(PROMOTIONS[review_id]),
        }
        for review_id in PROMOTIONS
    ]


def update_manifest(payload: dict) -> None:
    payload["work_item_structuring"] = {
        "projects_structured": 189,
        "projects_pending_visual_column_confirmation": 0,
        "projects_not_yet_source_captured": 0,
        "structured_work_items": 406,
        "pending_review_ids": [],
    }
    payload["quality_boundary"] = (
        "事業identity 189/189、全189事業の公式表source capture、current/plan/target列の構造化を"
        "すべて完了。189事業・406 work itemsは公式PDFに基づきstructured化され、視覚的列確認待ちは0。"
        "分野1～8の必要箇所は公式PDFレンダリング画像で直接確認した。visual review queueはcomplete。"
        "KGI/KPI・旧計画進捗・予算決算・政策成果は別レイヤーを維持する。"
    )


def update_policy_manifest(payload: dict) -> None:
    fact = next(row for row in payload["reviewed_facts"] if row["id"] == "chiba-current-project-work-items")
    fact["structured_project_count"] = 189
    fact["pending_visual_column_confirmation_project_count"] = 0
    fact["structured_work_item_count"] = 406
    fact["review_status"] = "reviewed_source_capture_and_structuring_complete"
    fact["interpretation_boundary"] = (
        "全189事業の公式表source captureとcurrent/plan/target構造化を完了し、406 work itemsを保持。"
        "分野1～8の曖昧な複数行セルは公式PDFレンダリングで直接確認し、visual pendingは0。"
        "事業量を独自達成度・政策成果・因果効果へ変換しない。"
    )
    payload["remaining_work"] = [
        "旧第1次実施計画360事業と現行189事業の継続・改称・統合・分割は名称だけで推測せずversioned linkageとして別レビューする。",
        "予算・決算の個別事業費と計画事業の接続は公式識別子・名称・所管・年度を確認できたものだけ昇格する。",
    ]
    payload["quality_boundary"] = (
        "Phase 13 Chiba review remains in progress beyond the completed current project identity, policy "
        "indicator, and project work-item structuring layers. Project quantity source capture and structuring "
        "are 189/189 complete with 406 work items and zero pending visual confirmations. Historical FY2024 "
        "progress remains tied to the 2023-2025 first implementation plan. Budget and settlement states remain "
        "separate. No independent policy-achievement judgment, causal attribution, version linkage, or automatic "
        "cross-city comparability is inferred."
    )


def update_plan_review(payload: dict) -> None:
    payload["review_status"] = "review_in_progress_current_project_work_items_complete"
    universe = next(row for row in payload["records"] if row["id"] == "chiba-current-project-universe")
    universe["review_note"] = (
        "189事業のidentity層、事業量source capture、current/plan/target構造化を完了。"
        "189事業・406 work itemsをレビュー済み。"
    )

    fact = next(row for row in payload["records"] if row["id"] == "chiba-current-project-work-items")
    fact["statement"] = (
        "現行189事業の取組項目、令和7年度末現況、計画内容、令和10年度末目標について全事業の"
        "source captureと列構造化を完了。189事業・406 work itemsを公式PDF確認済みデータとして保持する。"
    )
    fact["structured_project_count"] = 189
    fact["pending_visual_column_confirmation_project_count"] = 0
    fact["structured_work_item_count"] = 406
    fact["decision"] = "accepted_complete_source_capture_and_structuring"
    fact["review_note"] = (
        "source captureと3列構造化を全189事業で完了。分野1～8の曖昧な複数行セルは公式PDF"
        "レンダリングページを直接確認し、ダッシュを0へ変換せず原文の状態を保持した。"
    )
    payload["quality_boundary"] = (
        "Chiba Phase 13 has completed 189/189 current project identity, project-quantity source capture, and "
        "current/plan/target structuring with 406 work items and zero pending visual confirmations. Historical "
        "FY2024 progress remains tied to the 2023-2025 first implementation plan. Policy indicators, project "
        "quantities, annual progress, budget, settlement, causal attribution, independent achievement judgments, "
        "and cross-city comparability remain distinct review units."
    )
    payload["next_action"] = (
        "Review versioned linkage between the historical 360-project universe and current 189 projects without "
        "name-only inference, followed by conservative project-level budget/settlement linkage using only "
        "officially verifiable identifiers, names, departments, and fiscal years."
    )


def replace_function(source: str, name: str, replacement: str) -> str:
    marker = f"def {name}("
    start = source.find(marker)
    if start < 0:
        raise ValueError(f"Function not found: {name}")
    next_def = source.find("\ndef ", start + 1)
    end = len(source) if next_def < 0 else next_def + 1
    return source[:start] + replacement.rstrip() + "\n\n" + source[end:]


def update_tests() -> None:
    source = FIELD08_TEST.read_text(encoding="utf-8")
    source = replace_function(
        source,
        "test_field08_retains_12_structured_and_10_pending_until_its_visual_review",
        '''def test_field08_is_fully_structured_after_visual_review():
    projects = load(REVIEW)["projects"]
    pending = [
        row
        for row in projects
        if row["parse_status"] == "pending_visual_column_confirmation"
    ]
    assert len(projects) == 22
    assert pending == []
    assert all(row["work_items"] for row in projects)
    assert all(row["source_location"] == f"PDF p.{row['source_printed_page'] + 3}" for row in projects)''',
    )
    source = source.replace("== len(set(ids)) == 27", "== len(set(ids)) == 48")
    source = replace_function(
        source,
        "test_field08_preserves_representative_source_semantics",
        '''def test_field08_preserves_representative_source_semantics():
    projects = {row["review_id"]: row for row in load(REVIEW)["projects"]}
    sales = projects["chiba-f08-p004"]["work_items"][0]
    market = projects["chiba-f08-p006"]["work_items"][0]
    tourism = projects["chiba-f08-p010"]["work_items"][2]
    inbound = projects["chiba-f08-p011"]["work_items"][0]
    forest = projects["chiba-f08-p022"]["work_items"][1]

    assert sales["plan_text"] == "制度拡充 / 助成６件"
    assert market["plan_text"] == "事業者公募・選定 / 調査・設計"
    assert tourism["target_text"] == "千葉市里山サイクリングマップの改訂 / イベント開催・出展３回/年"
    assert inbound["current_text"] == "インバウンド団体バスツアー造成支援金交付数30件/年"
    assert inbound["plan_text"] == "ＯＴＡサイトでの市内ツアー販売支援事業15件"
    assert inbound["target_text"] == "ＯＴＡサイトでの市内ツアー販売支援事業５件/年"
    assert forest["target_text"].endswith("活動組織支援４組織")''',
    )
    source = replace_function(
        source,
        "test_field08_evidence_closes_source_capture_to_189_of_189",
        '''def test_field08_evidence_closes_source_capture_to_189_of_189():
    evidence = load(EVIDENCE)

    assert evidence["identity_project_count"] == 22
    assert evidence["source_captured_project_count"] == 22
    assert evidence["structured_project_count"] == 22
    assert evidence["pending_visual_column_confirmation_project_count"] == 0
    assert evidence["structured_work_item_count"] == 48
    assert evidence["reconciliation"]["cumulative_source_captured_projects"] == 189
    assert evidence["reconciliation"]["cumulative_structured_projects"] == 189
    assert evidence["reconciliation"]["cumulative_structured_work_items"] == 406
    assert len(evidence["visual_confirmed_promotions"]) == 10''',
    )
    source = replace_function(
        source,
        "test_work_item_manifest_keeps_source_capture_complete_as_visual_review_advances",
        '''def test_work_item_manifest_records_full_structuring_completion():
    manifest = load(MANIFEST)
    capture = manifest["work_item_source_capture"]
    structuring = manifest["work_item_structuring"]

    assert manifest["project_universe"] == 189
    assert manifest["project_identity_coverage"] == {"reviewed": 189, "remaining": 0}
    assert capture["projects_reviewed"] == 189
    assert capture["projects_remaining"] == 0
    assert sum(capture["field_counts_reviewed"].values()) == 189
    assert structuring == {
        "projects_structured": 189,
        "projects_pending_visual_column_confirmation": 0,
        "projects_not_yet_source_captured": 0,
        "structured_work_items": 406,
        "pending_review_ids": [],
    }
    assert manifest["next_field"] is None''',
    )
    FIELD08_TEST.write_text(source, encoding="utf-8")

    source = QUEUE_TEST.read_text(encoding="utf-8")
    source = replace_function(
        source,
        "test_visual_review_queue_reconciles_all_10_pending_projects",
        '''def test_visual_review_queue_is_complete_with_zero_pending_projects():
    queue = load(QUEUE)
    manifest = load(MANIFEST)
    queued_ids = [
        review_id
        for batch in queue["batches"]
        for review_id in batch["pending_review_ids"]
    ]

    assert queue["status"] == "complete"
    assert queued_ids == []
    assert manifest["work_item_structuring"]["pending_review_ids"] == []
    assert [batch["pending_count"] for batch in queue["batches"]] == [0] * 8
    assert queue["next_batch"] is None''',
    )
    source = replace_function(
        source,
        "test_every_queued_id_resolves_to_pending_raw_evidence",
        '''def test_no_project_remains_pending_raw_evidence():
    manifest = load(MANIFEST)
    projects = projects_by_id(manifest["review_paths"])
    assert len(projects) == 189
    assert all(
        project.get("parse_status") != "pending_visual_column_confirmation"
        for project in projects.values()
    )''',
    )
    source = replace_function(
        source,
        "test_visual_queue_contains_no_structured_project",
        '''def test_all_projects_are_structured_when_visual_queue_is_complete():
    queue = load(QUEUE)
    manifest = load(MANIFEST)
    all_projects = projects_by_id(manifest["review_paths"])
    assert queue["status"] == "complete"
    assert len(all_projects) == 189
    assert all(project["work_items"] for project in all_projects.values())''',
    )
    source = replace_function(
        source,
        "test_visual_queue_preserves_completed_source_capture_totals",
        '''def test_visual_queue_preserves_completed_source_capture_totals():
    queue = load(QUEUE)
    assert queue["source_capture"] == {
        "project_universe": 189,
        "projects_source_captured": 189,
        "projects_structured": 189,
        "structured_work_items": 406,
        "projects_pending_visual_column_confirmation": 0,
        "projects_not_yet_source_captured": 0,
    }''',
    )
    source = replace_function(
        source,
        "test_next_visual_batch_starts_with_field08_official_order",
        '''def test_completed_visual_queue_has_no_next_batch():
    queue = load(QUEUE)

    assert queue["execution_order"] == "official_field_and_project_order"
    assert all(batch["pending_count"] == 0 for batch in queue["batches"])
    assert queue["next_batch"] is None
    assert queue["status"] == "complete"
    assert "pending visual confirmationは0" in queue["quality_boundary"]''',
    )
    QUEUE_TEST.write_text(source, encoding="utf-8")

    source = ALIGNMENT_TEST.read_text(encoding="utf-8")
    source = replace_function(
        source,
        "test_chiba_project_work_item_progress_reconciles_across_control_layers",
        '''def test_chiba_project_work_item_progress_reconciles_across_control_layers():
    policy = load(POLICY_MANIFEST)
    plan = load(PLAN_REVIEW)
    work_manifest = load(WORK_ITEM_MANIFEST)
    policy_fact = next(
        row for row in policy["reviewed_facts"] if row["id"] == "chiba-current-project-work-items"
    )
    plan_fact = next(
        row for row in plan["records"] if row["id"] == "chiba-current-project-work-items"
    )
    structuring = work_manifest["work_item_structuring"]

    expected = {
        "source_captured_project_count": 189,
        "structured_project_count": 189,
        "pending_visual_column_confirmation_project_count": 0,
        "structured_work_item_count": 406,
    }
    for key, value in expected.items():
        assert policy_fact[key] == value
        assert plan_fact[key] == value

    assert structuring["projects_structured"] == 189
    assert structuring["projects_pending_visual_column_confirmation"] == 0
    assert structuring["structured_work_items"] == 406
    assert structuring["projects_not_yet_source_captured"] == 0
    assert structuring["pending_review_ids"] == []''',
    )
    source = replace_function(
        source,
        "test_chiba_source_capture_completion_does_not_claim_full_structuring",
        '''def test_chiba_source_capture_and_structuring_are_both_complete():
    policy = load(POLICY_MANIFEST)
    work_manifest = load(WORK_ITEM_MANIFEST)
    fact = next(
        row for row in policy["reviewed_facts"] if row["id"] == "chiba-current-project-work-items"
    )

    assert fact["review_status"] == "reviewed_source_capture_and_structuring_complete"
    assert fact["source_captured_project_count"] == 189
    assert fact["structured_project_count"] == fact["project_universe"] == 189
    assert fact["pending_visual_column_confirmation_project_count"] == 0
    assert work_manifest["next_field"] is None
    assert work_manifest["work_item_structuring"]["pending_review_ids"] == []''',
    )
    source = replace_function(
        source,
        "test_chiba_field07_completion_advances_visual_review_to_field08",
        '''def test_chiba_field08_completion_advances_to_versioned_and_fiscal_linkage():
    policy = load(POLICY_MANIFEST)
    plan = load(PLAN_REVIEW)
    work_manifest = load(WORK_ITEM_MANIFEST)

    assert len(policy["remaining_work"]) == 2
    assert "versioned linkage" in policy["remaining_work"][0]
    assert "予算・決算" in policy["remaining_work"][1]
    assert "versioned linkage" in plan["next_action"]
    assert "budget/settlement linkage" in plan["next_action"]
    assert work_manifest["work_item_structuring"]["pending_review_ids"] == []''',
    )
    ALIGNMENT_TEST.write_text(source, encoding="utf-8")

    source = POLICY_TEST.read_text(encoding="utf-8")
    source = replace_function(
        source,
        "test_chiba_plan_review_reflects_field07_visual_completion",
        '''def test_chiba_plan_review_reflects_complete_project_work_item_structuring():
    review = load(PLAN_REVIEW)
    work_items = next(
        row for row in review["records"] if row["id"] == "chiba-current-project-work-items"
    )

    assert review["review_status"] == "review_in_progress_current_project_work_items_complete"
    assert work_items["source_captured_project_count"] == 189
    assert work_items["structured_project_count"] == 189
    assert work_items["pending_visual_column_confirmation_project_count"] == 0
    assert work_items["structured_work_item_count"] == 406
    assert work_items["decision"] == "accepted_complete_source_capture_and_structuring"
    assert "versioned linkage" in review["next_action"]
    assert "406 work items" in review["quality_boundary"]''',
    )
    POLICY_TEST.write_text(source, encoding="utf-8")


def main() -> None:
    identities = load(IDENTITIES)
    review = load(REVIEW)
    evidence = load(EVIDENCE)
    manifest = load(MANIFEST)
    policy = load(POLICY_MANIFEST)
    plan = load(PLAN_REVIEW)

    normalize_identity_layer(identities)
    promote_review(review)
    update_evidence(evidence, review)
    update_manifest(manifest)
    update_policy_manifest(policy)
    update_plan_review(plan)

    dump(IDENTITIES, identities)
    dump(REVIEW, review)
    dump(EVIDENCE, evidence)
    dump(MANIFEST, manifest)
    dump(POLICY_MANIFEST, policy)
    dump(PLAN_REVIEW, plan)

    update_tests()

    # The builder now supports pending=0 and produces status=complete / next_batch=null.
    import subprocess
    import sys

    subprocess.run([sys.executable, str(QUEUE_BUILDER)], cwd=ROOT, check=True)
    queue = load(QUEUE)
    assert queue["status"] == "complete"
    assert queue["next_batch"] is None
    assert queue["source_capture"]["projects_structured"] == 189
    assert queue["source_capture"]["structured_work_items"] == 406
    assert queue["source_capture"]["projects_pending_visual_column_confirmation"] == 0


if __name__ == "__main__":
    main()
