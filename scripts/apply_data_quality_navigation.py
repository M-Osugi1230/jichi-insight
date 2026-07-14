#!/usr/bin/env python3
"""Apply discoverability and release checks for the data-quality page."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: str, old: str, new: str) -> None:
    target = ROOT / path
    content = target.read_text(encoding="utf-8")
    if new in content:
        return
    if content.count(old) != 1:
        raise RuntimeError(f"Expected exactly one match in {path}: {old!r}")
    target.write_text(content.replace(old, new), encoding="utf-8")


replace_once(
    "apps/web/components/SiteHeader.tsx",
    '  { href: "/sources", label: "公式資料" },\n',
    '  { href: "/sources", label: "公式資料" },\n'
    '  { href: "/data-quality", label: "データ品質" },\n',
)
replace_once(
    "apps/web/components/SiteFooter.tsx",
    '        <Link href="/methodology">方法論</Link>\n',
    '        <Link href="/methodology">方法論</Link>\n'
    '        <Link href="/data-quality">データ品質</Link>\n',
)
replace_once(
    "apps/web/app/sitemap.ts",
    '  "/corrections",\n',
    '  "/corrections",\n  "/data-quality",\n',
)
replace_once(
    "scripts/validate_static_export.py",
    '    "corrections/index.html",\n',
    '    "corrections/index.html",\n    "data-quality/index.html",\n',
)
replace_once(
    "scripts/validate_static_export.py",
    '    if failures:\n',
    '    quality_path = EXPORT_ROOT / "data-quality" / "index.html"\n'
    '    if quality_path.is_file():\n'
    '        quality = quality_path.read_text(encoding="utf-8")\n'
    '        for copy in [\n'
    '            "件数ではなく、確認の深さを公開する。",\n'
    '            "Evidence coverage",\n'
    '            "100%",\n'
    '            "データ不足を、点数で埋めません。",\n'
    '        ]:\n'
    '            if copy not in quality:\n'
    '                failures.append(\n'
    '                    f"Data quality page is missing required copy: {copy}"\n'
    '                )\n\n'
    '    if failures:\n',
)
replace_once(
    "README.md",
    '- [Editorial policy](docs/EDITORIAL_POLICY.md)\n',
    '- [Editorial policy](docs/EDITORIAL_POLICY.md)\n'
    '- [Data quality and publication readiness](docs/DATA_QUALITY.md)\n',
)
