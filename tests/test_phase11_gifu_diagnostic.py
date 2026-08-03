from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


def test_print_gifu_phase9_summary() -> None:
    source_path = Path("data/reviewed/phase9/21.json")
    source = json.loads(source_path.read_text(encoding="utf-8"))
    records = source["records"]

    title_counts = Counter(record["source_document_title"] for record in records)
    hash_counts = Counter(record["source_document_sha256"] for record in records)
    url_counts = Counter(record["source_document_url"] for record in records)
    location_counts = Counter(
        record["source_location"]["location_kind"] for record in records
    )
    page_types = Counter(
        type(record["source_location"].get("page")).__name__ for record in records
    )
    unit_counts = Counter(
        "missing" if record["unit_original"] is None else "reported"
        for record in records
    )
    review_status_counts = Counter(record["review_status"] for record in records)
    assessment_counts = Counter(
        record["policy_achievement_assessment_status"] for record in records
    )
    comparability_counts = Counter(
        record["comparability"]["status"] for record in records
    )

    document_metadata = source.get("documents") or []
    registered_urls = [str(item.get("source_url") or item.get("url")) for item in document_metadata]
    used_urls = set(url_counts)
    summary = {
        "top_level_keys": sorted(source),
        "prefecture_code": source.get("prefecture_code"),
        "prefecture_name": source.get("prefecture_name"),
        "source_title": source.get("source_title"),
        "source_url": source.get("source_url"),
        "plan_title": source.get("plan_title"),
        "plan_period": source.get("plan_period"),
        "record_count_declared": source.get("record_count"),
        "record_count_actual": len(records),
        "evidence_count_declared": source.get("evidence_count"),
        "extraction_error_count": source.get("extraction_error_count"),
        "document_metadata": document_metadata,
        "document_metadata_count": len(document_metadata),
        "display_order_unique": len({record["display_order"] for record in records}),
        "first_display_order": records[0]["display_order"],
        "last_display_order": records[-1]["display_order"],
        "record_id_unique": len({record["id"] for record in records}),
        "evidence_id_unique": len({record["evidence_id"] for record in records}),
        "source_title_counts": dict(title_counts),
        "source_hash_counts": dict(hash_counts),
        "source_url_counts": dict(url_counts),
        "source_location_counts": dict(location_counts),
        "source_page_types": dict(page_types),
        "unit_counts": dict(unit_counts),
        "review_status_counts": dict(review_status_counts),
        "assessment_counts": dict(assessment_counts),
        "comparability_counts": dict(comparability_counts),
        "registered_source_urls": registered_urls,
        "registered_sources_with_reviewed_records": [
            url for url in registered_urls if url in used_urls
        ],
        "registered_sources_without_reviewed_records": [
            url for url in registered_urls if url not in used_urls
        ],
        "used_urls_not_in_document_metadata": sorted(used_urls - set(registered_urls)),
    }
    print("\nPHASE11_GIFU_DIAGNOSTIC=" + json.dumps(summary, ensure_ascii=False, sort_keys=True))
    raise AssertionError("intentional diagnostic failure; remove before merge")
