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
    6: {
        "name": "文化芸術・スポーツ",
        "official_count": 25,
        "printed_start": 114,
        "printed_end": 124,
    },
    7: {"name": "都市・交通", "official_count": 78, "printed_start": 125, "printed_end": 161},
    8: {"name": "地域経済", "official_count": 32, "printed_start": 162, "printed_end": 180},
}

HEADING_RE = re.compile(r"^(.*?)\s{5,}([^\s].*)$")
MEASURE_RE = re.compile(
    r"^\s*[１２３４５６７８1-8][－-][１２３４５６７８1-8][－-]"
    r"[１２３４５６７８９０0-9]+\s+(.+)$"
)
DEPARTMENT_SUFFIX_RE = re.compile(
    r"(課|室|事務所|事務局|センター|動物公園|博物館|図書館|学校|保健所|"
    r"消防署|区役所|市民会館|市場|農政センター)"
    r"(?:、.*(?:課|室|事務所|事務局|センター|動物公園|博物館|図書館|学校|"
    r"保健所|消防署|区役所|市民会館|市場|農政センター))*$"
)
FULLWIDTH_TRANSLATION = str.maketrans("１２３４５６７８９０－", "1234567890-")
FOOTNOTE_RE = re.compile(r"\s*P\d+\s*")
MARKER_RE = re.compile(r"【[^】]+】")

LAYOUT_OVERRIDE_SPECS = (
    {
        "field_number": 3,
        "printed_page": 73,
        "fragments": ("障害者ケアラー", "等への支援", "精神保健福祉課"),
        "source_heading_text": "障害者ケアラー P195 等への支援",
        "responsible_departments": (
            "障害者自立支援課",
            "精神保健福祉課",
            "こころの健康センター",
        ),
        "review_note": (
            "公式PDFの複数行・複数列レイアウトを目視照合し、"
            "分割された事業名と3担当組織を復元した。"
        ),
    },
    {
        "field_number": 4,
        "printed_page": 88,
        "fragments": ("新児童相談所の整備【新規】",),
        "source_heading_text": "新児童相談所の整備【新規】",
        "responsible_departments": ("こども家庭支援課", "東部児童相談所"),
        "review_note": (
            "公式PDFで事業名の上下に分割表示された2担当組織を目視照合した。"
        ),
    },
    {
        "field_number": 4,
        "printed_page": 92,
        "fragments": ("ＩＣＴ教育の推進", "教育改革推進課"),
        "source_heading_text": "ＩＣＴ教育の推進",
        "responsible_departments": ("教育指導課", "教育改革推進課", "教育センター"),
        "review_note": (
            "公式PDFで事業名の前後行に分割表示された3担当組織を目視照合した。"
        ),
    },
    {
        "field_number": 5,
        "printed_page": 108,
        "fragments": ("区役所を中心とした地域支援プラットフォームの構築【新規】",),
        "source_heading_text": (
            "区役所を中心とした地域支援プラットフォームの構築【新規】"
        ),
        "responsible_departments": ("市民自治推進課", "区政推進課"),
        "review_note": (
            "公式PDFで事業名の上下に分割表示された2担当組織を目視照合した。"
        ),
    },
    {
        "field_number": 6,
        "printed_page": 118,
        "fragments": ("千葉氏に関する企画展の実施及び調査研究の推進【再掲】",),
        "source_heading_text": "千葉氏に関する企画展の実施及び調査研究の推進【再掲】",
        "responsible_departments": (
            "文化財課",
            "郷土博物館",
            "埋蔵文化財調査センター",
        ),
        "review_note": (
            "公式PDFで再掲事業名の上下に分割表示された3担当組織を目視照合した。"
        ),
    },
    {
        "field_number": 7,
        "printed_page": 136,
        "fragments": ("千葉氏に関する企画展の実施及び調査研究の推進",),
        "source_heading_text": "千葉氏に関する企画展の実施及び調査研究の推進",
        "responsible_departments": (
            "文化財課",
            "郷土博物館",
            "埋蔵文化財調査センター",
        ),
        "review_note": (
            "公式PDFで事業名の上下に分割表示された3担当組織を目視照合した。"
        ),
    },
    {
        "field_number": 7,
        "printed_page": 160,
        "fragments": ("下水道ストックマネジメントの推進", "下水道施設建設課"),
        "source_heading_text": "下水道ストックマネジメントの推進",
        "responsible_departments": (
            "下水道整備課",
            "下水道施設建設課",
            "下水道維持課",
        ),
        "review_note": (
            "公式PDFで事業名の前後行に分割表示された3担当組織を目視照合した。"
        ),
    },
    {
        "field_number": 8,
        "printed_page": 178,
        "fragments": ("農政センターのリニューアル",),
        "source_heading_text": (
            "農政センターのリニューアル"
            "（コミュニケーションエリアの活用検討及び改修等）【新規】"
        ),
        "responsible_departments": ("農業経営支援課",),
        "review_note": (
            "公式PDFで2行に分割された事業名と中間行の担当組織を目視照合した。"
        ),
    },
)


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


def layout_override(
    field_number: int,
    printed_page: int,
    line: str,
) -> dict | None:
    stripped = line.strip()
    for spec in LAYOUT_OVERRIDE_SPECS:
        if spec["field_number"] != field_number:
            continue
        if spec["printed_page"] != printed_page:
            continue
        if all(fragment in stripped for fragment in spec["fragments"]):
            return spec
    return None


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

            override = layout_override(field_number, printed_page, line)
            if override is not None:
                if current_measure is None:
                    raise ValueError(
                        "Layout override encountered before a measure heading: "
                        f"field={field_number} page={printed_page}"
                    )
                source_heading_text = override["source_heading_text"]
                candidates.append(
                    {
                        "measure_code": current_measure,
                        "project_name": normalize_project_name(source_heading_text),
                        "source_heading_text": source_heading_text,
                        "responsible_departments": list(
                            override["responsible_departments"]
                        ),
                        "source_printed_page": printed_page,
                        "source_location": f"PDF p.{printed_page + 3}",
                        "source_physical_page": printed_page + 4,
                        "new_in_first_plan": "新規" in source_heading_text,
                        "is_repost": "【再掲" in source_heading_text,
                        "layout_review_note": override["review_note"],
                    }
                )
                continue

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
            "same_field_repost"
            if same_field_primary
            else "cross_field_repost_pending_primary_review"
        )
        repost["primary_review_id"] = same_field_primary
        repost["decision"] = (
            "do_not_duplicate_identity"
            if same_field_primary
            else (
                f"exclude_from_field{field_number:02d}_unique_"
                f"{meta['official_count']}_and_resolve_primary_in_later_field_review"
            )
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


def resolve_cross_field_reposts(payloads: dict[int, dict]) -> None:
    primary_by_name: dict[str, str] = {}
    for payload in payloads.values():
        for record in payload["records"]:
            name = record["project_name"]
            if name in primary_by_name:
                raise ValueError(
                    "Duplicate historical primary project name across fields: "
                    f"{name!r}"
                )
            primary_by_name[name] = record["review_id"]

    for payload in payloads.values():
        for repost in payload["displayed_reposts"]:
            if repost["repost_type"] != "cross_field_repost_pending_primary_review":
                continue
            primary_review_id = primary_by_name.get(repost["project_name"])
            if primary_review_id is None:
                continue
            repost["repost_type"] = "cross_field_repost_resolved"
            repost["primary_review_id"] = primary_review_id
            repost["decision"] = "do_not_duplicate_identity"




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
                "data/catalog/"
                f"chiba_historical_project_identities_field{field_number:02d}.json"
            )
            field_row["status"] = "reviewed_complete"
        if field_row.get("status") == "reviewed_complete":
            reviewed_total += field_row["reviewed_unique_projects"]
            reviewed_paths.append(field_row["identity_path"])

    universe = manifest["historical_project_universe"]
    remaining = universe - reviewed_total
    manifest["historical_identity_coverage"] = {
        "reviewed": reviewed_total,
        "remaining": remaining,
    }
    manifest["historical_identity_paths"] = reviewed_paths

    next_pending = next(
        (
            row
            for row in manifest["field_review_order"]
            if row["status"] != "reviewed_complete"
        ),
        None,
    )

    if next_pending is not None:
        manifest["status"] = "historical_identity_review_started"
        manifest["next_action"] = (
            f"Field {next_pending['field_code']}（{next_pending['field_name']}）の抽出候補を"
            "公式PDFレイアウトと照合し、公式分野別事業数に不足する見出しを"
            "特定したうえで、再掲を除いた一次identityだけをreviewedへ昇格する。"
        )
        manifest["quality_boundary"] = (
            f"旧第1次計画360事業のうち{reviewed_total}件をidentity review済み。"
            f"残り{remaining}件を完了するまで360→189のversioned linkageはblocked。"
            "候補抽出件数が公式分野別事業数と一致しない分野は不足見出しを"
            "解消するまで昇格しない。名称一致・類似だけで継続・改称・統合・"
            "分割・廃止を確定しない。"
        )
    else:
        total_reposts = 0
        resolved_reposts = 0
        unresolved_reposts = 0
        all_primary_ids: set[str] = set()
        all_primary_names: set[str] = set()

        for field_number in FIELD_META:
            payload = load_json(
                CATALOG
                / f"chiba_historical_project_identities_field{field_number:02d}.json"
            )
            for record in payload["records"]:
                review_id = record["review_id"]
                project_name = record["project_name"]
                if review_id in all_primary_ids:
                    raise ValueError(f"Duplicate historical review_id: {review_id}")
                if project_name in all_primary_names:
                    raise ValueError(
                        "Duplicate historical primary project name after full review: "
                        f"{project_name!r}"
                    )
                all_primary_ids.add(review_id)
                all_primary_names.add(project_name)

            for repost in payload["displayed_reposts"]:
                total_reposts += 1
                if repost.get("primary_review_id"):
                    resolved_reposts += 1
                else:
                    unresolved_reposts += 1

        if len(all_primary_ids) != universe:
            raise ValueError(
                f"Historical identity total {len(all_primary_ids)} != universe {universe}"
            )
        if unresolved_reposts:
            raise ValueError(
                "Historical repost reconciliation incomplete: "
                f"{unresolved_reposts} unresolved"
            )

        manifest["status"] = "historical_identity_review_complete"
        manifest["historical_repost_reconciliation"] = {
            "displayed_reposts": total_reposts,
            "resolved_to_primary_identity": resolved_reposts,
            "unresolved": unresolved_reposts,
        }
        manifest["versioned_linkage_gate"]["status"] = (
            "ready_for_versioned_linkage_review"
        )
        manifest["next_action"] = (
            "旧2023～2025年度360事業identityと現行2026～2028年度189事業identityを"
            "公式掲載位置、施策、担当課、取組内容、事業量等で照合し、continued、"
            "renamed_continuation、merged_into_current、split_into_current、"
            "retired_after_first_plan、new_in_second_plan、unresolvedのversioned "
            "linkageをEvidence付きでレビューする。名称一致・類似だけでは確定しない。"
        )
        manifest["quality_boundary"] = (
            "旧第1次計画360/360事業のhistorical identity reviewを完了し、"
            f"再掲{total_reposts}件はすべて一次identityへ解決済み。"
            "これは現行189事業との継続・改称・統合・分割・終了・新規関係が"
            "確定したことを意味しない。360→189のversioned linkageは次の独立レビュー"
            "でEvidenceを確認し、名称一致・類似だけでは確定しない。"
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

    reviewed_fields = sorted(set(args.fields))
    payloads: dict[int, dict] = {}
    for field_number in reviewed_fields:
        primary, reposts = parsed[field_number]
        payloads[field_number] = build_reviewed_identity_payload(
            field_number, primary, reposts, pdf_sha256
        )

    resolve_cross_field_reposts(payloads)

    for field_number, payload in payloads.items():
        write_json(
            CATALOG / f"chiba_historical_project_identities_field{field_number:02d}.json",
            payload,
        )
        write_json(
            EVIDENCE / f"chiba_historical_project_identities_field{field_number:02d}_evidence.json",
            build_evidence(payload),
        )

    update_manifest(parsed_counts, reviewed_fields)


if __name__ == "__main__":
    main()
