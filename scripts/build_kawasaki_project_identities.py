from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data/catalog"
EVIDENCE = ROOT / "data/evidence"
STRUCTURE = CATALOG / "kawasaki_current_policy_structure.json"
OUTPUT = CATALOG / "kawasaki_current_project_identities.json"
EVIDENCE_OUTPUT = EVIDENCE / "kawasaki_current_project_identities_evidence.json"

MEASURE_RE = re.compile(r"^施策\s*([1-5]-\d-\d)(?:\s+.*)?$")
PROJECT_NAME_EXCEPTIONS = {
    "川崎病院の運営",
    "井田病院の運営",
    "多摩病院の運営管理",
    "児童福祉施設等の指導・監査",
}
EXPECTED_PROJECT_COUNT = 350
EXPECTED_MEASURE_COUNT = 48
EXPECTED_MAIN_ACTION_COUNT = 235


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def column_for_left(left: float) -> int | None:
    if 20 <= left < 285:
        return 0
    if 285 <= left < 550:
        return 1
    if 550 <= left < 810:
        return 2
    return None


def load_cells(tsv_path: Path) -> list[dict]:
    grouped: dict[tuple[int, int, float], list[tuple[float, str]]] = {}

    with tsv_path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            if row["level"] != "5":
                continue
            text = row["text"].strip()
            if not text or text.startswith("###"):
                continue

            left = float(row["left"])
            column = column_for_left(left)
            if column is None:
                continue

            page = int(row["page_num"])
            if page < 6 or page > 9:
                continue

            top = round(float(row["top"]), 1)
            grouped.setdefault((page, column, top), []).append((left, text))

    cells = []
    for (page, column, top), words in grouped.items():
        text = " ".join(value for _, value in sorted(words))
        cells.append(
            {
                "page": page,
                "column": column,
                "top": top,
                "text": " ".join(text.split()),
            }
        )
    return cells


def expected_measure_codes() -> list[str]:
    structure = load_json(STRUCTURE)
    codes = [
        measure["measure_code"]
        for basic_policy in structure["basic_policies"]
        for policy in basic_policy["policies"]
        for measure in policy["measures"]
    ]
    if len(codes) != EXPECTED_MEASURE_COUNT or len(set(codes)) != len(codes):
        raise ValueError("Kawasaki structure must contain 48 unique measure codes")
    return codes


def is_project_name(text: str) -> bool:
    return (
        "事業" in text
        or "業務" in text
        or text in PROJECT_NAME_EXCEPTIONS
    )


def parse_projects(cells: list[dict]) -> list[dict]:
    projects: list[dict] = []

    for column in range(3):
        current_measure: str | None = None
        pending_main_action = False
        sequence_by_measure: Counter[str] = Counter()

        ordered = sorted(
            (cell for cell in cells if cell["column"] == column),
            key=lambda cell: (cell["page"], cell["top"]),
        )

        for cell in ordered:
            text = cell["text"]

            measure_match = MEASURE_RE.match(text)
            if measure_match:
                current_measure = measure_match.group(1)
                pending_main_action = False
                continue

            if text == "○":
                pending_main_action = True
                continue

            if current_measure is None:
                pending_main_action = False
                continue

            if text.startswith(("基本政策", "政策")):
                pending_main_action = False
                continue

            is_main_action = pending_main_action or text.startswith("○")
            pending_main_action = False
            project_name = text.lstrip("○").strip()

            if not is_project_name(project_name):
                continue

            sequence_by_measure[current_measure] += 1
            sequence = sequence_by_measure[current_measure]
            booklet_page = cell["page"] + 156

            projects.append(
                {
                    "review_id": (
                        f"kawasaki-m{current_measure}-p{sequence:03d}"
                    ),
                    "measure_code": current_measure,
                    "project_name": project_name,
                    "main_action": is_main_action,
                    "source_id": "kawasaki-fourth-implementation-plan-official-pdf",
                    "source_pdf_page": cell["page"],
                    "source_booklet_page": booklet_page,
                    "source_location": (
                        f"資料編 冊子p.{booklet_page} "
                        f"（資料編分割PDF p.{cell['page']}）"
                    ),
                    "review_status": "reviewed_identity",
                }
            )

    return projects


def validate_projects(projects: list[dict]) -> None:
    expected_codes = set(expected_measure_codes())
    actual_codes = {row["measure_code"] for row in projects}
    review_ids = [row["review_id"] for row in projects]
    names = [row["project_name"] for row in projects]

    if len(projects) != EXPECTED_PROJECT_COUNT:
        raise ValueError(
            f"Kawasaki project count {len(projects)} != {EXPECTED_PROJECT_COUNT}"
        )
    if actual_codes != expected_codes:
        missing = sorted(expected_codes - actual_codes)
        extra = sorted(actual_codes - expected_codes)
        raise ValueError(
            f"Kawasaki measure coverage mismatch: missing={missing}, extra={extra}"
        )
    if len(set(review_ids)) != len(review_ids):
        raise ValueError("Duplicate Kawasaki project review_id detected")
    if len(set(names)) != len(names):
        raise ValueError("Duplicate Kawasaki project name detected")
    if sum(row["main_action"] for row in projects) != EXPECTED_MAIN_ACTION_COUNT:
        raise ValueError(
            "Kawasaki main-action count must remain "
            f"{EXPECTED_MAIN_ACTION_COUNT}"
        )


def build(tsv_path: Path, pdf_path: Path) -> tuple[dict, dict]:
    cells = load_cells(tsv_path)
    projects = parse_projects(cells)
    validate_projects(projects)

    counts = Counter(row["measure_code"] for row in projects)
    pdf_digest = sha256(pdf_path)

    payload = {
        "id": "kawasaki-current-project-identities-2026-2029",
        "phase": 13,
        "official_code": "141305",
        "name_ja": "川崎市",
        "plan_period": "2026年度～2029年度",
        "source_id": "kawasaki-fourth-implementation-plan-official-pdf",
        "source_pdf_sha256": pdf_digest,
        "review_status": "reviewed_complete_350_project_identities",
        "project_universe_count": EXPECTED_PROJECT_COUNT,
        "measure_coverage_count": EXPECTED_MEASURE_COUNT,
        "main_action_count": EXPECTED_MAIN_ACTION_COUNT,
        "measure_project_counts": dict(sorted(counts.items())),
        "records": projects,
        "quality_boundary": (
            "第4期実施計画資料編の事務事業一覧をPDF座標で3列に分離し、"
            "48施策すべてを確認したうえで350事務事業identityを全件レビューした。"
            "○印235件は『政策体系別の取組』の主な取組として別フラグで保持し、"
            "主な取組ではない115件を削除しない。事務事業identityから成果指標、"
            "予算、執行、決算、因果効果、政策達成度を推測しない。"
        ),
    }

    evidence = {
        "id": "kawasaki-current-project-identities-evidence",
        "subject_type": "project_identity_universe",
        "source_id": "kawasaki-fourth-implementation-plan-official-pdf",
        "source_pdf_sha256": pdf_digest,
        "source_page_range": {
            "split_pdf_start": 6,
            "split_pdf_end": 9,
            "booklet_start": 162,
            "booklet_end": 165,
        },
        "extraction_method": (
            "pdftotext -tsv; word boxes split into three content columns by x "
            "coordinate; rows ordered by PDF page and y coordinate; measure "
            "headings establish the current 施策 identity; standalone ○ markers "
            "carry to the immediately following project row."
        ),
        "reconciliation": {
            "official_project_universe_count": 350,
            "reviewed_project_identity_count": len(projects),
            "official_measure_count": 48,
            "reviewed_measure_coverage_count": len(counts),
            "main_action_count": sum(row["main_action"] for row in projects),
            "unique_project_name_count": len({row["project_name"] for row in projects}),
            "count_matches_official": len(projects) == 350,
        },
        "records": [
            {
                "review_id": row["review_id"],
                "measure_code": row["measure_code"],
                "project_name": row["project_name"],
                "source_location": row["source_location"],
            }
            for row in projects
        ],
        "quality_boundary": (
            "PDF layout extraction is accepted only when the 350-project total, "
            "all 48 measure identities, unique review IDs, unique project names, "
            "and 235 main-action markers reconcile simultaneously."
        ),
    }
    return payload, evidence


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tsv", type=Path, required=True)
    parser.add_argument("--pdf", type=Path, required=True)
    args = parser.parse_args()

    payload, evidence = build(args.tsv, args.pdf)
    write_json(OUTPUT, payload)
    write_json(EVIDENCE_OUTPUT, evidence)


if __name__ == "__main__":
    main()
