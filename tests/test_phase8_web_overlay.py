from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COVERAGE = ROOT / "apps/web/lib/nationwideCoverage.ts"
MUNICIPALITIES = ROOT / "apps/web/app/municipalities/page.tsx"
REVIEWED_COVERAGE = ROOT / "apps/web/lib/reviewedCoverage.ts"
EXPLORER = ROOT / "apps/web/components/CoverageExplorer.tsx"


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


def test_nationwide_page_exposes_reviewed_counts_and_vertical_depth():
    page = read(MUNICIPALITIES)
    reviewed_coverage = read(REVIEWED_COVERAGE)
    explorer = read(EXPLORER)

    assert "reviewedCoverageStats.reviewedRecords" in page
    assert "phase10StageSummary" in page
    assert "reviewedPrefectureCoverage" in reviewed_coverage
    assert "phase9Summary.reviewed_target_statement_count" in reviewed_coverage
    assert "evidenceDepthOrder.map" in explorer
    assert "索引済" in explorer
    assert "照合済" in explorer
    assert "接続済" in explorer
