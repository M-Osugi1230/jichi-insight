from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "apps/web/app/municipalities/miyagi/page.tsx"
STYLES = ROOT / "apps/web/app/municipalities/miyagi/page.module.css"
COVERAGE = ROOT / "apps/web/lib/nationwideCoverage.ts"
MUNICIPALITIES = ROOT / "apps/web/app/municipalities/page.tsx"
SITEMAP = ROOT / "apps/web/app/sitemap.ts"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_miyagi_page_exposes_reviewed_targets_without_assessment_inference():
    page = read(PAGE)
    assert STYLES.is_file()
    assert "宮城県の政策目標を、原文・期間・未設定までそのまま読む。" in page
    assert "成果の達成率ではなく" in page
    assert "目標1〜23を、政策上の所属と4つの時点から確認する。" in page
    assert "累計値。単年度値ではありません。" in page
    assert "目標値の確認と、政策成果の評価を分ける。" in page
    assert "評価原案と確定評価の版差分" in page


def test_miyagi_page_is_linked_from_coverage_queue_and_sitemap():
    coverage = read(COVERAGE)
    municipalities = read(MUNICIPALITIES)
    sitemap = read(SITEMAP)
    assert 'record.prefecture_code === "04"' in coverage
    assert '"/municipalities/miyagi"' in coverage
    assert 'href="/municipalities/miyagi"' in municipalities
    assert "宮城県の23目標を公開" in municipalities
    assert '"/municipalities/miyagi"' in sitemap
