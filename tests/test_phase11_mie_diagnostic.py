from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


def test_print_mie_phase9_summary() -> None:
    source = json.loads(
        Path("data/reviewed/phase9/24.json").read_text(encoding="utf-8")
    )
    records = source["records"]
    documents = source.get("documents") or []

    summary = {
        "top_level": {
            key: source.get(key)
            for key in (
                "prefecture_code",
                "name",
                "slug",
                "plan_title",
                "plan_period",
                "source_title",
                "source_url",
                "reviewed_target_statement_count",
                "evidence_packet_count",
                "updated_at",
            )
        },
        "record_count": len(records),
        "documents": documents,
        "document_count": len(documents),
        "display_order": [records[0]["display_order"], records[-1]["display_order"]],
        "unique_record_ids": len({record["id"] for record in records}),
        "unique_evidence_ids": len({record["evidence_id"] for record in records}),
        "source_title_counts": dict(
            Counter(record["source_document_title"] for record in records)
        ),
        "source_url_counts": dict(
            Counter(record["source_document_url"] for record in records)
        ),
        "source_hash_counts": dict(
            Counter(record["source_document_sha256"] for record in records)
        ),
        "location_counts": dict(
            Counter(
                record["source_location"]["location_kind"]
                for record in records
            )
        ),
        "page_types": dict(
            Counter(
                type(record["source_location"].get("page")).__name__
                for record in records
            )
        ),
        "unit_counts": dict(
            Counter(
                "missing" if record["unit_original"] is None else "reported"
                for record in records
            )
        ),
        "review_status_counts": dict(
            Counter(record["review_status"] for record in records)
        ),
        "assessment_counts": dict(
            Counter(
                record["policy_achievement_assessment_status"]
                for record in records
            )
        ),
        "comparability_counts": dict(
            Counter(record["comparability"]["status"] for record in records)
        ),
        "plan_history_counts": dict(
            Counter(record["plan_history_boundary"] for record in records)
        ),
        "first_record": records[0],
        "last_record": records[-1],
    }
    print(
        "\nPHASE11_MIE_DIAGNOSTIC="
        + json.dumps(summary, ensure_ascii=False, sort_keys=True)
    )
    raise AssertionError("intentional diagnostic failure; remove before merge")
