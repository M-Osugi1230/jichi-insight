"""Issue #708: analytics tag and privacy disclosure are committed together."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAYOUT = (ROOT / "apps/web/app/layout.tsx").read_text(encoding="utf-8")
PRIVACY = (ROOT / "apps/web/app/privacy/page.tsx").read_text(encoding="utf-8")
MEASUREMENT = (ROOT / "docs/MEASUREMENT.md").read_text(encoding="utf-8")


def test_official_clarity_snippet_is_shared_by_static_pages():
    assert 'import Script from "next/script";' in LAYOUT
    assert 'strategy="afterInteractive"' in LAYOUT
    assert 'id="microsoft-clarity"' in LAYOUT
    assert 't.src="https://www.clarity.ms/tag/"+i;' in LAYOUT
    assert '})(window, document, "clarity", "script", "zfzl22syr5");' in LAYOUT
    assert LAYOUT.count('"zfzl22syr5"') == 1


def test_privacy_disclosure_covers_clarity_and_official_sources():
    assert 'const updatedAt = "2026年11月19日";' in PRIVACY
    assert "<h2>4. 第三者サービス</h2>" in PRIVACY
    assert "<h2>6. アクセス解析（Microsoft Clarity）</h2>" in PRIVACY
    for text in (
        "Microsoft Clarity",
        "クリック",
        "スクロール",
        "Cookie",
        "個人を特定するため",
        "ブラウザの設定",
        "https://www.microsoft.com/en-US/privacy/privacystatement",
        "https://learn.microsoft.com/en-us/clarity/setup-and-installation/clarity-data",
    ):
        assert text in PRIVACY


def test_measurement_keeps_no_individual_tracking_and_legal_review_rule():
    assert "2026-11-19 所有者決定" in MEASUREMENT
    assert "個人を追跡する計測（フィンガープリント等）は導入しません" in MEASUREMENT
    assert "プライバシーポリシーの改定と法務確認を先に行います" in MEASUREMENT
    assert "決定済み（2026-11-19）" in MEASUREMENT
