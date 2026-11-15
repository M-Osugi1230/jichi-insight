"""Web contract checks for the UI readiness round-2 changes.

Covers: the GitHub-account notice on /corrections (shown before the
click-through to the Issue form), the web app manifest icons, and the
homepage link into the reviewed Phase 15 city pages.
"""

import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "apps" / "web"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_corrections_page_warns_about_github_account_before_the_form_link():
    page = _read(WEB / "app" / "corrections" / "page.tsx")

    assert "issues/new?template=data-correction.yml" in page
    assert "GitHubアカウントが必要です" in page
    # The notice must appear before the submission link in the page source,
    # so a reader sees it before clicking through to the GitHub form.
    assert page.index("GitHubアカウントが必要です") < page.index("訂正申請を開く")


def test_manifest_declares_icons_and_png_files_match_declared_sizes():
    manifest = _read(WEB / "app" / "manifest.ts")

    assert "icons" in manifest
    for size in (192, 512):
        assert f"icon-{size}.png" in manifest
        assert f"{size}x{size}" in manifest
        png = WEB / "public" / "icons" / f"icon-{size}.png"
        data = png.read_bytes()
        assert data[:8] == b"\x89PNG\r\n\x1a\n"
        width, height = struct.unpack(">II", data[16:24])
        assert (width, height) == (size, size)


def test_homepage_links_into_reviewed_city_pages_via_municipalities_anchor():
    home = _read(WEB / "app" / "page.tsx")
    municipalities = _read(WEB / "app" / "municipalities" / "page.tsx")

    # The homepage Phase 15 section links readers to the reviewed cities,
    # and the anchor target exists on /municipalities.
    assert "/municipalities#reviewed-cities" in home
    assert 'id="reviewed-cities"' in municipalities
    # The homepage counts stay derived from the canonical Phase 15 queue.
    assert "phase15Progress.reviewed" in home
    assert "phase15Progress.total" in home
