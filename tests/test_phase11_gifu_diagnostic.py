from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from scripts.normalize_phase11_gifu import SOURCE_DOCUMENTS


def test_print_gifu_phase9_summary() -> None:
    source_path = Path("data/reviewed/phase9/21.json")
    source = json.loads(source_path.read_text(encoding="utf-8"))
    records = source["records"]

    title_counts: Counter[str] = Counter()
    hash_counts: Counter[str] = Counter()
    url_counts: Counter[str] = Counter()
    evidence_lengths: Counter[int] = Counter()
    page_types: Counter[str] = Counter()
    status_counts: Counter[str] = Counter()

    for record in records:
        evidence = record.get("Evidence") or []
        evidence_lengths[len(evidence)] += 1
        status_counts[str(record.get("Status"))] += 1
        for item in evidence:
            lineage = item.get("lineage") or {}
            title_counts[str(lineage.get("source_title"))] += 1
            hash_counts[str(lineage.get("source_hash"))] += 1
            url = lineage.get("source_url") or item.get("Reference URL")
            url_counts[str(url)] += 1
            page = (item.get("Location") or {}).get("page")
            page_types[type(page).__name__] += 1

    registered_urls = [item["url"] for item in SOURCE_DOCUMENTS]
    used_urls = {url for url in url_counts if url != "None"}
    summary = {
        "prefecture_code": source.get("prefecture_code"),
        "prefecture_name": source.get("prefecture_name"),
        "record_count": source.get("record_count"),
        "actual_records": len(records),
        "evidence_count": source.get("evidence_count"),
        "actual_evidence": sum(evidence_lengths[length] * length for length in evidence_lengths),
        "extraction_error_count": source.get("extraction_error_count"),
        "indicator_id_unique": len({record.get("Indicator ID") for record in records}),
        "first_indicator_id": records[0].get("Indicator ID"),
        "last_indicator_id": records[-1].get("Indicator ID"),
        "status_counts": dict(status_counts),
        "evidence_lengths": dict(evidence_lengths),
        "source_title_counts": dict(title_counts),
        "source_hash_counts": dict(hash_counts),
        "source_url_counts": dict(url_counts),
        "source_page_types": dict(page_types),
        "registered_source_urls": registered_urls,
        "registered_source_documents": len(registered_urls),
        "registered_sources_with_reviewed_records": [url for url in registered_urls if url in used_urls],
        "registered_sources_without_reviewed_records": [url for url in registered_urls if url not in used_urls],
        "unregistered_used_urls": sorted(used_urls - set(registered_urls)),
        "first_record": records[0],
        "last_record": records[-1],
    }
    print("\nPHASE11_GIFU_DIAGNOSTIC=" + json.dumps(summary, ensure_ascii=False, sort_keys=True))
    raise AssertionError("intentional diagnostic failure; remove before merge")
