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
    assert "柱1と取組1〜5" in page
    assert "目標1〜{miyagiPolicyReviewStats.reviewedTargetGroups}" in page
    assert "をReviewed。次は目標39〜52。" in page
    assert "累計値。単年度値ではありません。" in page
    assert "公式表に単位の記載がありません。" in page
    assert "目標値の確認と、政策成果の評価を分ける。" in page
    assert "評価原案と確定評価の版差分" in page


def test_miyagi_page_is_linked_from_coverage_queue_and_sitemap():
    coverage = read(COVERAGE)
    municipalities = read(MUNICIPALITIES)
    sitemap = read(SITEMAP)
    assert 'record.prefecture_code === "04"' in coverage
    assert '"/municipalities/miyagi"' in coverage
    assert 'href="/municipalities/miyagi"' in municipalities
    assert "次は目標39〜52" in municipalities
    assert "reviewedIndicatorSeries" in municipalities
    assert "remainingTargetGroups" in municipalities
    assert '"/municipalities/miyagi"' in sitemap
