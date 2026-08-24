from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "data/catalog/chiba_current_project_work_item_review_manifest.json"
DEFAULT_OUTPUT = ROOT / "data/catalog/chiba_current_project_work_item_visual_review_queue.json"

FIELD_NAMES = {
    "1": "環境・自然",
    "2": "安全・安心",
    "3": "健康・福祉",
    "4": "子ども・教育",
    "5": "地域社会",
    "6": "文化芸術・スポーツ",
    "7": "都市・交通",
    "8": "地域経済",
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def field_code_from_review_id(review_id: str) -> str:
    prefix = "chiba-f"
    if not review_id.startswith(prefix):
        raise ValueError(f"Unexpected Chiba review id: {review_id}")
    return str(int(review_id[len(prefix) : len(prefix) + 2]))


def collect_pending_projects(manifest: dict) -> dict[str, list[dict]]:
    pending_by_field = {field_code: [] for field_code in FIELD_NAMES}
    seen: set[str] = set()

    for relative_path in manifest["review_paths"]:
        review_path = ROOT / relative_path
        review = load_json(review_path)
        for project in review["projects"]:
            if project.get("parse_status") != "pending_visual_column_confirmation":
                continue
            review_id = project["review_id"]
            if review_id in seen:
                raise ValueError(f"Duplicate pending review id: {review_id}")
            seen.add(review_id)
            field_code = field_code_from_review_id(review_id)
            pending_by_field[field_code].append(
                {
                    "review_id": review_id,
                    "project_name": project["project_name"],
                    "source_location": project["source_location"],
                    "raw_table_text": project["raw_table_text"],
                    "review_path": relative_path,
                }
            )

    for projects in pending_by_field.values():
        projects.sort(key=lambda row: row["review_id"])
    return pending_by_field


def build_queue(manifest: dict) -> dict:
    pending_by_field = collect_pending_projects(manifest)
    pending_ids = [
        project["review_id"]
        for field_code in FIELD_NAMES
        for project in pending_by_field[field_code]
    ]
    manifest_pending_ids = manifest["work_item_structuring"]["pending_review_ids"]
    if set(pending_ids) != set(manifest_pending_ids):
        missing = sorted(set(manifest_pending_ids) - set(pending_ids))
        extra = sorted(set(pending_ids) - set(manifest_pending_ids))
        raise ValueError(
            "Pending queue does not reconcile with work-item manifest: "
            f"missing={missing}, extra={extra}"
        )

    batches = []
    for field_code, field_name in FIELD_NAMES.items():
        projects = pending_by_field[field_code]
        review_paths = list(dict.fromkeys(row["review_path"] for row in projects))
        batches.append(
            {
                "field_code": field_code,
                "field_name": field_name,
                "pending_count": len(projects),
                "review_paths": review_paths,
                "pending_review_ids": [row["review_id"] for row in projects],
            }
        )

    source_capture = manifest["work_item_source_capture"]
    structuring = manifest["work_item_structuring"]
    pending_count = structuring["projects_pending_visual_column_confirmation"]
    first_nonempty = next(
        (batch for batch in batches if batch["pending_count"] > 0),
        None,
    )
    is_complete = pending_count == 0

    if is_complete and manifest_pending_ids:
        raise ValueError("Completed visual-review queue still has pending review IDs")
    if not is_complete and first_nonempty is None:
        raise ValueError("Pending visual-review count is nonzero but no batch is available")

    next_batch = None
    if first_nonempty is not None:
        next_batch = {
            "field_code": first_nonempty["field_code"],
            "field_name": first_nonempty["field_name"],
            "pending_review_ids": first_nonempty["pending_review_ids"],
        }

    if is_complete:
        quality_boundary = (
            "189/189 source capture完了後の視覚確認キューは全件解消済み。"
            "全189事業のcurrent/plan/target列対応がstructuredへ昇格され、"
            "pending visual confirmationは0。キュー完了は政策成果・達成度・因果効果の"
            "判定を意味しない。"
        )
    else:
        quality_boundary = (
            "このキューは未確認値を埋めるための推測リストではなく、189/189 source capture"
            f"完了後に残る{pending_count}事業の視覚確認作業を漏れなく追跡する制御ファイル。"
            "キュー登録自体はstructured昇格を意味しない。"
        )

    return {
        "id": "chiba-current-project-work-item-visual-review-queue",
        "phase": 13,
        "official_code": manifest["official_code"],
        "name_ja": manifest["name_ja"],
        "plan_period": manifest["plan_period"],
        "status": "complete" if is_complete else "ready_for_visual_confirmation",
        "source_id": manifest["source_id"],
        "source_capture": {
            "project_universe": manifest["project_universe"],
            "projects_source_captured": source_capture["projects_reviewed"],
            "projects_structured": structuring["projects_structured"],
            "structured_work_items": structuring["structured_work_items"],
            "projects_pending_visual_column_confirmation": pending_count,
            "projects_not_yet_source_captured": structuring[
                "projects_not_yet_source_captured"
            ],
        },
        "resolution_rule": (
            "公式PDFの該当ページを視覚確認し、取組項目・令和7年度末現況・計画内容・"
            "令和10年度末目標の列対応が一意に確認できた事業だけをstructuredへ昇格する。"
            "複数行セル、結合セル、ページ跨ぎで列対応が不明な場合はpendingのまま保持し、"
            "値・順序・単位を推定しない。"
        ),
        "promotion_requirements": [
            "project identity、source_location、公式PDF該当ページが一致すること",
            (
                "各work itemのitem_name、current_text、plan_text、target_textを"
                "視覚的に列対応できること"
            ),
            "ダッシュや空欄を数値0へ変換しないこと",
            "増分・年間値・累積値・状態値を原文の意味のまま保持すること",
            (
                "昇格後に当該reviewファイル、evidence、work-item manifest、"
                "Phase 13 control layers、testsの件数を同期すること"
            ),
        ],
        "batches": batches,
        "execution_order": "official_field_and_project_order",
        "next_batch": next_batch,
        "quality_boundary": quality_boundary,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    manifest = load_json(MANIFEST_PATH)
    queue = build_queue(manifest)
    serialized = json.dumps(queue, ensure_ascii=False, separators=(",", ":")) + "\n"

    output_path = args.output
    if not output_path.is_absolute():
        output_path = ROOT / output_path

    if args.check:
        existing = load_json(output_path)
        if existing != queue:
            raise SystemExit(
                "Visual review queue is stale. Run "
                "python scripts/build_chiba_work_item_visual_review_queue.py"
            )
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
