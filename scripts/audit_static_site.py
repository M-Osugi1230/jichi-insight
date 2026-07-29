#!/usr/bin/env python3
"""Audit the generated static site for publication-critical defects."""

from __future__ import annotations

import argparse
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EXPORT_ROOT = ROOT / "apps" / "web" / "out"

REQUIRED_ROUTES = {
    "/",
    "/404.html",
    "/about/",
    "/corrections/",
    "/data-quality/",
    "/disclaimer/",
    "/methodology/",
    "/municipalities/",
    "/privacy/",
    "/sources/",
    "/terms/",
}

SKIPPED_SCHEMES = {"mailto", "tel", "javascript", "data"}


class DocumentParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[str] = []
        self.canonicals: list[str] = []
        self.html_lang: str | None = None
        self.title_depth = 0
        self.title_text: list[str] = []
        self.h1_count = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {key.lower(): value for key, value in attrs}
        if tag == "html":
            self.html_lang = attributes.get("lang")
        elif tag == "a" and attributes.get("href"):
            self.links.append(attributes["href"] or "")
        elif tag == "link" and attributes.get("rel") and attributes.get("href"):
            rel_tokens = {token.lower() for token in (attributes["rel"] or "").split()}
            if "canonical" in rel_tokens:
                self.canonicals.append(attributes["href"] or "")
        elif tag == "title":
            self.title_depth += 1
        elif tag == "h1":
            self.h1_count += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "title" and self.title_depth:
            self.title_depth -= 1

    def handle_data(self, data: str) -> None:
        if self.title_depth:
            self.title_text.append(data)

    @property
    def title(self) -> str:
        return "".join(self.title_text).strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--export-root", type=Path, default=DEFAULT_EXPORT_ROOT)
    parser.add_argument(
        "--base-path",
        default="",
        help="Deployment base path, for example /jichi-insight.",
    )
    return parser.parse_args()


def route_for_html(export_root: Path, path: Path) -> str:
    relative = path.relative_to(export_root).as_posix()
    if relative == "index.html":
        return "/"
    if relative.endswith("/index.html"):
        return "/" + relative[: -len("index.html")]
    return "/" + relative


def target_file(export_root: Path, route: str) -> Path:
    clean = unquote(route).split("?", 1)[0].split("#", 1)[0]
    if not clean or clean == "/":
        return export_root / "index.html"
    relative = clean.lstrip("/")
    candidate = export_root / relative
    if clean.endswith("/"):
        return candidate / "index.html"
    if candidate.suffix:
        return candidate
    if candidate.is_file():
        return candidate
    return candidate / "index.html"


def strip_base_path(path: str, base_path: str) -> str | None:
    normalized = "/" + base_path.strip("/") if base_path else ""
    if not normalized:
        return path
    if path == normalized:
        return "/"
    if path.startswith(normalized + "/"):
        return path[len(normalized) :]
    return None


def audit_html(export_root: Path, base_path: str) -> list[str]:
    failures: list[str] = []
    html_files = sorted(export_root.rglob("*.html"))
    if not html_files:
        return [f"No HTML files found under {export_root}"]

    routes = {route_for_html(export_root, path) for path in html_files}
    for required in sorted(REQUIRED_ROUTES):
        if required not in routes:
            failures.append(f"Missing required route: {required}")

    for path in html_files:
        route = route_for_html(export_root, path)
        parser = DocumentParser()
        try:
            parser.feed(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError) as exc:
            failures.append(f"{route}: cannot read HTML: {exc}")
            continue

        if parser.html_lang != "ja":
            failures.append(f"{route}: html lang must be 'ja' (found {parser.html_lang!r})")
        if not parser.title:
            failures.append(f"{route}: missing non-empty title")
        if route != "/404.html" and parser.h1_count != 1:
            failures.append(f"{route}: expected exactly one h1, found {parser.h1_count}")
        if len(parser.canonicals) > 1:
            failures.append(f"{route}: multiple canonical links")

        for href in parser.links:
            parts = urlsplit(href)
            if parts.scheme.lower() in SKIPPED_SCHEMES or parts.netloc:
                continue
            if not parts.path or parts.path.startswith("#"):
                continue
            internal_path = strip_base_path(parts.path, base_path)
            if internal_path is None:
                continue
            if internal_path.startswith("/_next/"):
                continue
            destination = target_file(export_root, internal_path)
            if not destination.is_file():
                failures.append(f"{route}: broken internal link {href!r}")

    return failures


def audit_robots(export_root: Path, base_path: str) -> list[str]:
    path = export_root / "robots.txt"
    if not path.is_file():
        return ["Missing robots.txt"]
    content = path.read_text(encoding="utf-8")
    normalized_content = content.lower()
    failures: list[str] = []
    if "user-agent:" not in normalized_content:
        failures.append("robots.txt: missing User-agent directive")
    if "sitemap:" not in normalized_content:
        failures.append("robots.txt: missing Sitemap directive")
    normalized = "/" + base_path.strip("/") if base_path else ""
    if normalized and normalized not in content:
        failures.append(f"robots.txt: sitemap URL does not contain base path {normalized}")
    return failures


def audit_sitemap(export_root: Path, base_path: str) -> list[str]:
    path = export_root / "sitemap.xml"
    if not path.is_file():
        return ["Missing sitemap.xml"]
    failures: list[str] = []
    try:
        root = ElementTree.fromstring(path.read_text(encoding="utf-8"))
    except (ElementTree.ParseError, OSError, UnicodeError) as exc:
        return [f"sitemap.xml: invalid XML: {exc}"]

    locations = [
        element.text.strip()
        for element in root.iter()
        if element.tag.endswith("loc") and element.text
    ]
    if not locations:
        failures.append("sitemap.xml: no loc entries")
        return failures

    normalized = "/" + base_path.strip("/") if base_path else ""
    for location in locations:
        parts = urlsplit(location)
        if parts.scheme not in {"http", "https"} or not parts.netloc:
            failures.append(f"sitemap.xml: loc must be absolute: {location}")
            continue
        route = strip_base_path(parts.path, base_path)
        if route is None:
            failures.append(f"sitemap.xml: loc is outside base path: {location}")
            continue
        if normalized and normalized not in parts.path:
            failures.append(f"sitemap.xml: loc missing base path: {location}")
        if not target_file(export_root, route).is_file():
            failures.append(f"sitemap.xml: loc has no exported page: {location}")
    return failures


def main() -> int:
    args = parse_args()
    export_root = args.export_root.resolve()
    failures = [
        *audit_html(export_root, args.base_path),
        *audit_robots(export_root, args.base_path),
        *audit_sitemap(export_root, args.base_path),
    ]

    if failures:
        print("Static site audit failed:")
        for failure in sorted(set(failures)):
            print(f"- {failure}")
        return 1

    html_count = len(list(export_root.rglob("*.html")))
    print(f"Static site audit passed ({html_count} HTML files).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
