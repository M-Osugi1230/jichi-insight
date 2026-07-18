from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "apps/web/app/municipalities/miyagi/page.tsx"
STYLES = ROOT / "apps/web/app/municipalities/miyagi/page.module.css"
COVERAGE = ROOT / "apps/web/lib/nationwideCoverage.ts"
MUNICIPALITIES = ROOT / "apps/web/app/municipalities/page.tsx"
SITEMAP = ROOT / "apps/web/app/sitemap.ts"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_miyagi_page_copy_and_boundaries():
    page = read(PAGE)
    assert STYLES.is_file()
    for text in [
        "宮城県の政策目標を、原文・期間・未設定までそのまま読む。",
        "成果の達成率ではなく",
        "柱1〜2と取組1〜7",
        "次は目標53〜68",
        "累計値。単年度値ではありません。",
        "目標値の確認と、政策成果の評価を分ける。",
        "評価原案と確定評価の版差分",
    ]:
        assert text in page
    assert "direction.display_order <= 2" in page


def test_miyagi_page_links_and_dynamic_counts():
    coverage = read(COVERAGE)
    municipalities = read(MUNICIPALITIES)
    sitemap = read(SITEMAP)
    assert 'record.prefecture_code === "04"' in coverage
    assert '"/municipalities/miyagi"' in coverage
    assert 'href="/municipalities/miyagi"' in municipalities
    assert "miyagiPolicyReviewStats.reviewedTargetGroups" in municipalities
    assert "miyagiPolicyReviewStats.remainingTargetGroups" in municipalities
    assert "miyagiPolicyReviewStats.reviewedIndicatorSeries" in municipalities
    assert '"/municipalities/miyagi"' in sitemap
