from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

import pypdfium2 as pdfium

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_QUEUE = ROOT / "data/catalog/chiba_current_project_work_item_visual_review_queue.json"
PAGE_PATTERN = re.compile(r"PDF p{1,2}\.\s*(\d+)(?:\s*[-–]\s*(\d+))?")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_pages(source_location: str) -> list[int]:
    match = PAGE_PATTERN.fullmatch(source_location.strip())
    if not match:
        raise ValueError(f"Unsupported source location: {source_location}")

    start = int(match.group(1))
    end = int(match.group(2) or start)
    if end < start:
        raise ValueError(f"Descending page range: {source_location}")
    return list(range(start, end + 1))


def collect_pending(queue: dict) -> list[dict]:
    records: list[dict] = []
    seen: set[str] = set()

    for batch in queue["batches"]:
        projects: dict[str, dict] = {}
        for relative_path in batch["review_paths"]:
            payload = load_json(ROOT / relative_path)
            for project in payload["projects"]:
                projects[project["review_id"]] = project

        for review_id in batch["pending_review_ids"]:
            if review_id in seen:
                raise ValueError(f"Duplicate pending review id: {review_id}")
            seen.add(review_id)
            project = projects[review_id]
            if project["parse_status"] != "pending_visual_column_confirmation":
                raise ValueError(f"Queued project is not pending: {review_id}")
            records.append(
                {
                    "review_id": review_id,
                    "field_code": batch["field_code"],
                    "field_name": batch["field_name"],
                    "project_name": project["project_name"],
                    "source_location": project["source_location"],
                    "pages": parse_pages(project["source_location"]),
                }
            )

    return records


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def render_pages(pdf_path: Path, output_dir: Path, pages: list[int], dpi: int) -> None:
    document = pdfium.PdfDocument(str(pdf_path))
    page_count = len(document)
    scale = dpi / 72.0

    for page_number in pages:
        if page_number < 0 or page_number >= page_count:
            raise ValueError(
                f"Page {page_number} outside PDF range 0-{page_count - 1}"
            )
        page = document[page_number]
        bitmap = page.render(scale=scale)
        image = bitmap.to_pil()
        image.save(output_dir / f"page-{page_number:03d}.png")
        bitmap.close()
        page.close()

    document.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--queue", type=Path, default=DEFAULT_QUEUE)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--dpi", type=int, default=180)
    args = parser.parse_args()

    queue = load_json(args.queue)
    records = collect_pending(queue)
    pages = sorted({page for record in records for page in record["pages"]})

    args.output_dir.mkdir(parents=True, exist_ok=True)
    render_pages(args.pdf, args.output_dir, pages, args.dpi)

    index = {
        "id": "chiba-current-project-work-item-visual-render-index",
        "official_code": queue["official_code"],
        "plan_period": queue["plan_period"],
        "source_url": (
            "https://www.city.chiba.jp/sogoseisaku/shichokoshitsu/hisho/hodo/"
            "documents/20260410-2-2.pdf"
        ),
        "source_sha256": sha256(args.pdf),
        "render_dpi": args.dpi,
        "pending_project_count": len(records),
        "rendered_page_count": len(pages),
        "rendered_pages": pages,
        "projects": records,
        "quality_boundary": (
            "Rendered pages are review evidence only. A queued project remains pending until a human or "
            "visual model confirms the table-column relationships on the rendered official PDF page."
        ),
    }
    (args.output_dir / "index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
