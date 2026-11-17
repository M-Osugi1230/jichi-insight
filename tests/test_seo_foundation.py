"""SEO foundation contracts: canonical coverage and sitemap lastmod rule.

Every route published in the sitemap must declare a canonical URL (in its
page file or in the template that generates it), the shared metadata
defaults must live in lib/pageMetadata.ts and be wired into the root
layout, and sitemap lastmod dates must be derived from repository data
stamps rather than hardcoded literals.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps/web/app"
SITEMAP = APP / "sitemap.ts"
LAYOUT = APP / "layout.tsx"
PAGE_METADATA = ROOT / "apps/web/lib/pageMetadata.ts"

STATIC_ROUTES = [
    "",
    "/about",
    "/assemblies",
    "/assemblies/fukuoka-prefecture/overseas-activities",
    "/compare",
    "/corrections",
    "/corrections/history",
    "/data-quality",
    "/executives",
    "/executives/source-requests",
    "/methodology",
    "/municipalities",
    "/municipalities/phase9",
    "/municipalities/phase10",
    "/municipalities/phase10/hokkaido-actuals",
    "/municipalities/phase10/tokyo-children-actuals",
    "/municipalities/phase10/miyagi-money",
    "/municipalities/phase10/fukuoka-actuals",
    "/municipalities/phase10/fukuoka-projects",
    "/municipalities/phase10/tohoku",
    "/municipalities/phase10/kanto",
    "/municipalities/phase10/chubu",
    "/municipalities/phase10/kinki",
    "/municipalities/phase10/chugoku",
    "/municipalities/phase10/shikoku",
    "/municipalities/phase10/kyushu",
    "/municipalities/hokkaido",
    "/municipalities/miyagi",
    "/municipalities/tokyo",
    "/municipalities/aichi",
    "/municipalities/osaka",
    "/municipalities/hiroshima",
    "/municipalities/kagawa",
    "/municipalities/okinawa",
    "/municipalities/fukuoka-prefecture",
    "/municipalities/fukuoka-city",
    "/municipalities/kitakyushu-city",
    "/policies",
    "/policy-sources",
    "/review-progress",
    "/sources",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def page_file_for(route: str) -> Path:
    if route == "":
        return APP / "page.tsx"
    return APP / route.lstrip("/") / "page.tsx"


def test_shared_metadata_defaults_exist_and_layout_uses_them():
    helper = read(PAGE_METADATA)
    layout = read(LAYOUT)
    assert "export const siteUrl" in helper
    assert "export const defaultOgImages" in helper
    assert "export function canonicalFor" in helper
    assert 'from "@/lib/pageMetadata"' in layout
    assert "images: defaultOgImages" in layout


def test_every_static_sitemap_route_declares_a_canonical():
    for route in STATIC_ROUTES:
        page = page_file_for(route)
        assert page.exists(), f"missing page for route {route}"
        assert "canonical" in read(page), f"no canonical declared for route {route}"


def test_dynamic_templates_declare_canonicals():
    phase15_template = read(APP / "municipalities/[slug]/page.tsx")
    phase9_template = read(APP / "municipalities/phase9/[slug]/page.tsx")
    assert "canonical" in phase15_template
    assert "canonicalFor" in phase9_template
    for nn in range(1, 27):
        page = APP / f"policies/fukuoka-prefecture/initiatives/{nn:02d}/page.tsx"
        assert "canonical" in read(page), f"no canonical for initiative {nn:02d}"


def test_phase15_template_passes_the_default_og_image():
    template = read(APP / "municipalities/[slug]/page.tsx")
    assert "images: defaultOgImages" in template


def test_sitemap_lastmod_is_derived_from_data_stamps():
    sitemap = read(SITEMAP)
    # The unified rule reads stamps from the data each page renders.
    for needle in [
        "city.completedAt",
        "phase15Progress.updatedAt",
        "reviewedCoverageStats.updatedAt",
        "phase9Summary.updated_at",
        "catalog.updated_at",
        "page.catalog.reviewed_at",
        "correctionsHistory.updatedAt",
        "loadPhase10RegionalDepthBySlug",
        "updated_at",
    ]:
        assert needle in sitemap, f"sitemap lastmod derivation missing: {needle}"
    # No route keeps a hardcoded calendar literal as its lastmod source.
    assert '"2026-' not in sitemap
    assert "'2026-" not in sitemap
