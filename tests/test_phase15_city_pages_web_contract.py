"""Guard the public Phase 15 city detail pages.

City pages must be generated only for reviewed_complete municipalities,
driven by the canonical queue plus each city's completion record and reviewed
package. Amounts must render together with their provenance notes, linkage
judgments must follow the recorded decisions (a city without a linkage
record must not be presented as judged not_assessable), and no page may
present the data as a ranking.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUEUE_PATH = ROOT / "data/catalog/phase15_core_capital_review_queue.json"
WEB_ROOT = ROOT / "apps/web"
LOADER = WEB_ROOT / "lib/phase15Cities.ts"
MODEL = WEB_ROOT / "lib/phase15Progress.ts"
PAGE = WEB_ROOT / "app/municipalities/[slug]/page.tsx"
REVIEW_PROGRESS_PAGE = WEB_ROOT / "app/review-progress/page.tsx"
MUNICIPALITIES_PAGE = WEB_ROOT / "app/municipalities/page.tsx"
SITEMAP = WEB_ROOT / "app/sitemap.ts"


def _reviewed_items():
    queue = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
    return [
        item for item in queue["execution_queue"] if item["status"] == "reviewed_complete"
    ]


def _slug_for(item) -> str:
    file_name = Path(item["completion_path"]).name
    suffix = "_phase15_completion.json"
    assert file_name.endswith(suffix)
    return f"{file_name[: -len(suffix)]}-city"


def test_every_reviewed_city_has_a_complete_package_for_its_page():
    items = _reviewed_items()
    assert items, "expected at least one reviewed_complete city"

    for item in items:
        slug = _slug_for(item)
        completion = json.loads((ROOT / item["completion_path"]).read_text(encoding="utf-8"))
        assert completion["status"] == "reviewed_complete"
        assert completion["official_code"] == item["official_code"]
        assert completion["completion_boundary"]
        assert completion["deferred_depth"]

        package = ROOT / "data/reviewed" / slug
        municipality = json.loads((package / "municipality.json").read_text(encoding="utf-8"))
        plan_review = json.loads((package / "plan_review.json").read_text(encoding="utf-8"))
        fiscal = json.loads((package / "fiscal_records.json").read_text(encoding="utf-8"))
        packets = json.loads((package / "evidence_packets.json").read_text(encoding="utf-8"))
        sources = json.loads(
            (ROOT / completion["review_package"]["source_catalog_path"]).read_text(encoding="utf-8")
        )

        assert municipality["data_status"] == "reviewed"
        assert plan_review["review_status"] == "reviewed"
        assert all(record["source_url"] for record in plan_review["records"])
        assert fiscal and all(record["review_status"] == "reviewed" for record in fiscal)
        assert all(record["note"] for record in fiscal)
        assert {packet["subject_id"] for packet in packets} == {record["id"] for record in fiscal}
        assert sources["sources"]


def test_city_page_loader_is_fail_closed_and_never_reads_candidates():
    loader = LOADER.read_text(encoding="utf-8")

    assert "phase15_core_capital_review_queue.json" in loader
    assert 'status === "reviewed_complete"' in loader
    assert "throw new Error" in loader
    assert "data/candidates" not in loader
    # Source ids resolve through the Phase 15 catalog, with the documented
    # finance-catalog fallback and the "<city>-city-home" exception.
    assert "_phase15_sources.json" in loader
    assert "_city_finance_sources.json" in loader
    assert "-city-home" in loader


def test_city_page_renders_amounts_with_notes_and_decisions_verbatim():
    page = PAGE.read_text(encoding="utf-8")

    # Amounts are rendered from the record itself, always with its note.
    assert "record.amountYen" in page
    assert "record.note" in page
    # No derived conversions of the amounts are produced.
    assert "100000000" not in page
    # Linkage judgments follow the recorded decision value.
    assert 'record.decision === "not_assessable"' in page
    assert "判定不能（not_assessable）" in page
    # Cities without a linkage record are disclosed as not judged.
    assert "判定レコードを作成していません" in page
    assert "接続を確立していない" in page
    # Plan transition records are separated from the current plan.
    assert "現行計画ではありません" in page
    # Boundaries are published in full and rankings are disclaimed.
    assert "city.completionBoundary" in page
    assert "city.qualityBoundary" in page
    assert "ランキングではありません" in page
    assert "city.deferredDepth" in page
    # Unavailable amounts are never filled with a number.
    assert "record.valueStatus" in page


def test_progress_model_and_pages_link_to_city_pages():
    model = MODEL.read_text(encoding="utf-8")
    review_progress = REVIEW_PROGRESS_PAGE.read_text(encoding="utf-8")
    municipalities = MUNICIPALITIES_PAGE.read_text(encoding="utf-8")
    sitemap = SITEMAP.read_text(encoding="utf-8")

    assert "slugFromCompletionPath" in model
    assert "{record.name}のページを見る" in review_progress
    assert "/municipalities/${record.slug}" in review_progress
    assert "loadPhase15CitySummaries" in municipalities
    assert "/municipalities/${city.slug}" in municipalities
    assert "loadPhase15CitySummaries" in sitemap
    assert "phase15CityRoutes" in sitemap
