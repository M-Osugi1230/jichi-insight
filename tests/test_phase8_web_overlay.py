from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COVERAGE = ROOT / "apps/web/lib/nationwideCoverage.ts"
MUNICIPALITIES = ROOT / "apps/web/app/municipalities/page.tsx"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_nationwide_web_uses_regional_anchor_source_registry_as_an_overlay():
    coverage = read(COVERAGE)

    assert "regional_anchor_source_registry.json" in coverage
    assert "deeperSourceStatus" in coverage
    assert "anchorSourceStatusesByCode" in coverage
    assert "overlay[category] ?? \"not_indexed\"" in coverage
    assert "countSourceStatuses" in coverage


def test_overlay_cannot_downgrade_reviewed_or_linked_source_depth():
    coverage = read(COVERAGE)

    assert '"not_indexed",\n  "indexed",\n  "reviewed",\n  "linked"' in coverage
    assert "sourceInventoryStatusOrder.indexOf(candidate)" in coverage
    assert "sourceInventoryStatusOrder.indexOf(current)" in coverage


def test_nationwide_page_exposes_effective_source_depth():
    page = read(MUNICIPALITIES)

    assert "nationwideSourceInventoryStats" in page
    assert "stats.indexedOrHigher" in page
    assert "stats.reviewedOrHigher" in page
    assert "索引以上" in page
    assert "人手照合以上" in page
