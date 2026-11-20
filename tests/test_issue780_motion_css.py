"""Issue #780: CSS-only motion tokens, staging and reduced-motion safeguards."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSS_PATH = ROOT / "apps/web/app/globals.css"
DOC_PATH = ROOT / "docs/MOTION.md"


def test_motion_tokens_and_principles_are_documented():
    css = CSS_PATH.read_text(encoding="utf-8")
    doc = DOC_PATH.read_text(encoding="utf-8")

    for token in (
        "--motion-ease-standard",
        "--motion-ease-enter",
        "--motion-ease-feedback",
        "--motion-duration-quick",
        "--motion-duration-standard",
        "--motion-duration-enter",
        "--motion-duration-emphasis",
        "--motion-distance-subtle",
    ):
        assert token in css
        assert token in doc

    for principle in ("Slow In and Slow Out", "Timing", "Staging"):
        assert principle in doc

    assert "120ms" in doc
    assert "200ms" in doc
    assert "320ms" in doc
    assert "480ms" in doc
    assert "40ms" in doc


def test_entrance_keyframes_only_animate_compositor_properties():
    css = CSS_PATH.read_text(encoding="utf-8")
    match = re.search(
        r"@keyframes motion-rise-in\s*\{(.*?)\n\}",
        css,
        flags=re.DOTALL,
    )
    assert match is not None
    keyframes = match.group(1)
    properties = re.findall(r"(?m)^\s*([a-z-]+)\s*:", keyframes)
    assert set(properties) == {"opacity", "transform"}

    forbidden = (
        "height",
        "width",
        "margin",
        "padding",
        "top",
        "left",
        "grid-template",
        "gap",
    )
    assert not any(
        re.search(rf"(?m)^\s*{name}\s*:", keyframes)
        for name in forbidden
    )


def test_reduced_motion_and_print_disable_motion_without_hiding_content():
    css = CSS_PATH.read_text(encoding="utf-8")
    reduced_start = css.rfind("@media (prefers-reduced-motion: reduce)")
    assert reduced_start >= 0
    reduced = css[reduced_start:]

    assert "animation: none !important" in reduced
    assert "transition: none !important" in reduced
    assert "scroll-behavior: auto !important" in reduced
    assert "opacity: 1 !important" in reduced
    assert "transform: none !important" in reduced
    assert "@media print" in reduced
    assert "animation: none !important" in reduced.split("@media print", 1)[1]
    assert "transition: none !important" in reduced.split("@media print", 1)[1]


def test_disclosure_motion_keeps_native_details_semantics_and_no_js_gating():
    css = CSS_PATH.read_text(encoding="utf-8")
    doc = DOC_PATH.read_text(encoding="utf-8")

    assert "details > :not(summary)" in css
    assert "details[open] > :not(summary)" in css
    assert "allow-discrete" in css
    assert "@starting-style" in css
    assert "JavaScript" in doc
    assert "CSS のみ" in doc
    assert "GSAP" in doc
    assert "Lottie" in doc
