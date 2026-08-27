from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data/catalog"
EVIDENCE = ROOT / "data/evidence"
MANIFEST = CATALOG / "chiba_historical_project_identity_review_manifest.json"

FIELD_META = {
    1: {"name": "環境・自然", "official_count": 53, "printed_start": 16, "printed_end": 36},
    2: {"name": "安全・安心", "official_count": 57, "printed_start": 37, "printed_end": 57},
    3: {"name": "健康・福祉", "official_count": 46, "printed_start": 58, "printed_end": 80},
    4: {"name": "子ども・教育", "official_count": 46, "printed_start": 81, "printed_end": 102},
    5: {"name": "地域社会", "official_count": 23, "printed_start": 103, "printed_end": 113},
    6: {"name": "文化芸術・スポーツ", "official_count": 25, "printed_start": 114, "printed_end": 124},
    7: {"name": "都市・交通", "official_count": 78, "printed_start": 125, "printed_end": 161},
    8: {"name": "地域経済", "official_count": 32, "printed_start": 162, "printed_end": 180},
}

HEADING_RE = re.compile(r"^(.*?)\s{5,}([^\s].*)$")
MEASURE_RE = re.compile(
    r"^\s*[１２３４５６７８1-8][－-][１２３４５６７８1-8][－-]"
    r"[１２３４５６７８９０0-9]+\s+(.+)$"
)
DEPARTMENT_SUFFIX_RE = re.compile(
    r"(課|室|事務所|センター|動物公園|博物館|図書館|学校|保健所|消防署|"
    r"区役所|市民会館|市場|農政センター)"
    r"(?:、.*(?:課|室|事務所|センター|動物公園|博物館|図書館|学校|保健所|"
    r"消防署|区役所|市民会館|市場|農政センター))*$"
)
FULLWIDTH_TRANSLATION = str.maketrans("１２３４５６７８９０－", "1234567890-")
FOOTNOTE_RE = re.compile(r"\s*P\d+\s*")
MARKER_RE = re.compile(r"【[^】]+】")


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )


def normalize_project_name(raw: str) -> str:
    text = MARKER_RE.sub("", raw)
    text = FOOTNOTE_RE.sub("", text)
    return " ".join(text.split()).strip()


def parse_field(path: Path, field_number: int) -> tuple[list[dict], list[dict]]:
    meta = FIELD_META[field_number]
    pages = path.read_text(encoding="utf-8").split("\f")
    expected_pages = meta["printed_end"] - meta["printed_start"] + 1
    if len(pages) not in {expected_pages, expected_pages + 1}:
        raise ValueError(
            f"Field {field_number}: expected {expected_pages} pages, got {len(pages)}"
        )

    current_measure: str | None = None
    candidates: list[dict] = []
    for page_offset, page_text in enumerate(pages[:expected_pages]):
        printed_page = meta["printed_start"] + page_offset
        for line in page_text.splitlines():
            if MEASURE_RE.match(line):
                current_measure = line.strip().split()[0].translate(FULLWIDTH_TRANSLATION)

            match = HEADING_RE.match(line.rstrip())
            if not match:
                continue
            left, right = (part.strip() for part in match.groups())
            if not left or re.search(r"[0-9０-９]", right):
                continue
            if not DEPARTMENT_SUFFIX_RE.search(right):
                continue
            if current_measure is None:
                raise ValueError(
                    f"Field {field_number}: project heading before measure: {left!r}"
                )

            candidates.append(
                {
                    "measure_code": current_measure,
                    "project_name": normalize_project_name(left),
                    "source_heading_text": left,
                    "responsible_departments": right.split("、"),
                    "source_printed_page": printed_page,
                    "source_location": f"PDF p.{printed_page + 3}",
                    "source_physical_page": printed_page + 4,
                    "new_in_first_plan": "新規" in left,
                    "is_repost": "【再掲" in left,
                }
            )

    primary_candidates = [row for row in candidates if not row["is_repost"]]
    repost_candidates = [row for row in candidates if row["is_repost"]]
    return primary_candidates, repost_candidates


def build_reviewed_identity_payload(
    field_number: int,
    primary_candidates: list[dict],
    repost_candidates: list[dict],
    pdf_sha256: str,
) -> dict:
    meta = FIELD_META[field_number]
    if len(primary_candidates) != meta["official_count"]:
        raise ValueError(
            f"Field {field_number}: candidate primary count {len(primary_candidates)} "
            f"does not match official count {meta['official_count']}"
        )

    names = [row["project_name"] for row in primary_candidates]
    if len(names) != len(set(names)):
        duplicates = sorted({name for name in names if names.count(name) > 1})
        raise ValueError(f"Field {field_number}: duplicate primary names: {duplicates}")

    records = []
    primary_by_name: dict[str, str] = {}
    for index, row in enumerate(primary_candidates, start=1):
        review_id = f"chiba-hf{field_number:02d}-p{index:03d}"
        record = {key: value for key, value in row.items() if key != "is_repost"}
        record.update({"review_id": review_id, "primary_identity": True})
        records.append(record)
        primary_by_name[row["project_name"]] = review_id

    displayed_reposts = []
    for row in repost_candidates:
        same_field_primary = primary_by_name.get(row["project_name"])
        repost = {key: value for key, value in row.items() if key != "is_repost"}
        repost["repost_type"] = (
            "same_field_repost" if same_field_primary else "cross_field_repost_pending_primary_review"
        )
        repost["primary_review_id"] = same_field_primary
        repost["decision"] = (
            "do_not_duplicate_identity"
            if same_field_primary
            else f"exclude_from_field{field_number:02d}_unique_{meta['official_count']}_and_resolve_primary_in_later_field_review"
        )
        displayed_reposts.append(repost)

    return {
        "id": f"chiba-historical-project-identities-field{field_number:02d}",
        "official_code": "121002",
        "plan_period": "2023年度～2025年度",
        "field_code": str(field_number),
        "field_name": meta["name"],
        "official_unique_project_count": meta["official_count"],
        "identity_review_status": (
            f"reviewed_complete_{meta['official_count']}_of_{meta['official_count']}_unique_projects"
        ),
        "source_id": "chiba-implementation-plan-2023-2025-full-pdf",
        "source_pdf_sha256": pdf_sha256,
        "id_semantics": (
            "review_id is a Jichi Insight stable historical review identifier and is not "
            "claimed to be an official Chiba project code."
        ),
        "source_location_semantics": (
            "source_location uses the repository zero-based PDF page-index convention; "
            "source_printed_page preserves the booklet page and source_physical_page is "
            "the 1-based physical PDF page."
        ),
        "records": records,
        "displayed_reposts": displayed_reposts,
        "quality_boundary": (
            f"第1次実施計画Field {field_number}のlayout-preserving公式PDF抽出から、"
            f"計画事業見出しと担当課をレビューし、再掲を除く{meta['official_count']}件が"
            "総論の公式分野別事業数と一致することを確認。再掲表示は一次identityへ重複計上せず、"
            "他分野一次掲載が未レビューの再掲はprimary未解決のまま保持する。"
        ),
    }


def build_evidence(payload: dict) -> dict:
    records = payload["records"]
    reposts = payload["displayed_reposts"]
    field_number = int(payload["field_code"])
    meta = FIELD_META[field_number]
    return {
        "id": f"chiba-historical-project-identities-field{field_number:02d}-evidence",
        "official_code": "121002",
        "plan_period": "2023年度～2025年度",
        "field_code": str(field_number),
        "field_name": meta["name"],
        "source_id": payload["source_id"],
        "source_pdf_sha256": payload["source_pdf_sha256"],
        "review_status": "reviewed_complete_historical_project_identities",
        "official_unique_project_count": meta["official_count"],
        "reviewed_unique_project_count": len(records),
        "displayed_repost_count": len(reposts),
        "printed_page_range": f"{meta['printed_start']}-{meta['printed_end']}",
        "pdf_index_range": f"{meta['printed_start'] + 3}-{meta['printed_end'] + 3}",
        "physical_page_range": f"{meta['printed_start'] + 4}-{meta['printed_end'] + 4}",
        "identity_path": (
            f"data/catalog/chiba_historical_project_identities_field{field_number:02d}.json"
        ),
        "reconciliation": {
            "official_unique_project_count": meta["official_count"],
            "reviewed_unique_project_count": len(records),
            "displayed_repost_count": len(reposts),
            "count_matches_official": len(records) == meta["official_count"],
        },
        "quality_boundary": payload["quality_boundary"],
    }


def update_manifest(
    parsed_counts: dict[int, tuple[int, int]], reviewed_fields: list[int]
) -> None:
    manifest = load_json(MANIFEST)
    field_rows = {int(row["field_code"]): row for row in manifest["field_review_order"]}
    reviewed_paths = []
    reviewed_total = 0

    for field_number, meta in FIELD_META.items():
        field_row = field_rows[field_number]
        field_row["official_unique_project_count"] = meta["official_count"]
        primary_count, repost_count = parsed_counts[field_number]
        field_row["candidate_extraction"] = {
            "primary_heading_candidates": primary_count,
            "repost_heading_candidates": repost_count,
            "matches_official_unique_count": primary_count == meta["official_count"],
        }
        if field_number in reviewed_fields:
            field_row["reviewed_unique_projects"] = meta["official_count"]
            field_row["identity_path"] = (
                f"data/catalog/chiba_historical_project_identities_field{field_number:02d}.json"
            )
            field_row["status"] = "reviewed_complete"
            reviewed_paths.append(field_row["identity_path"])
            reviewed_total += meta["official_count"]
        elif field_row.get("status") == "reviewed_complete":
            reviewed_total += field_row["reviewed_unique_projects"]
            reviewed_paths.append(field_row["identity_path"])

    manifest["historical_identity_coverage"] = {
        "reviewed": reviewed_total,
        "remaining": manifest["historical_project_universe"] - reviewed_total,
    }
    manifest["historical_identity_paths"] = reviewed_paths
    next_pending = next(
        row for row in manifest["field_review_order"] if row["status"] != "reviewed_complete"
    )
    manifest["next_action"] = (
        f"Field {next_pending['field_code']}（{next_pending['field_name']}）の抽出候補を公式PDF"
        "レイアウトと照合し、公式分野別事業数に不足する見出しを特定したうえで、"
        "再掲を除いた一次identityだけをreviewedへ昇格する。"
    )
    manifest["quality_boundary"] = (
        f"旧第1次計画360事業のうち{reviewed_total}件をidentity review済み。"
        f"残り{360 - reviewed_total}件を完了するまで360→189のversioned linkageはblocked。"
        "候補抽出件数が公式分野別事業数と一致しない分野は不足見出しを解消するまで昇格しない。"
        "名称一致・類似だけで継続・改称・統合・分割・廃止を確定しない。"
    )
    write_json(MANIFEST, manifest)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--fields", type=int, nargs="+", required=True)
    args = parser.parse_args()

    invalid = sorted(set(args.fields) - set(FIELD_META))
    if invalid:
        raise SystemExit(f"Unsupported field numbers: {invalid}")

    sha_line = (args.input_dir / "sha256.txt").read_text(encoding="utf-8").strip()
    pdf_sha256 = sha_line.split()[0]
    if not re.fullmatch(r"[0-9a-f]{64}", pdf_sha256):
        raise ValueError("Invalid PDF SHA-256 evidence")

    parsed: dict[int, tuple[list[dict], list[dict]]] = {}
    parsed_counts: dict[int, tuple[int, int]] = {}
    for field_number in FIELD_META:
        primary, reposts = parse_field(
            args.input_dir / f"field{field_number:02d}.txt", field_number
        )
        parsed[field_number] = (primary, reposts)
        parsed_counts[field_number] = (len(primary), len(reposts))

    for field_number in args.fields:
        primary, reposts = parsed[field_number]
        payload = build_reviewed_identity_payload(
            field_number, primary, reposts, pdf_sha256
        )
        write_json(
            CATALOG / f"chiba_historical_project_identities_field{field_number:02d}.json",
            payload,
        )
        write_json(
            EVIDENCE / f"chiba_historical_project_identities_field{field_number:02d}_evidence.json",
            build_evidence(payload),
        )

    update_manifest(parsed_counts, sorted(set(args.fields)))


if __name__ == "__main__":
    main()
