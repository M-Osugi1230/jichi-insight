"""Issue #780: CSS-only motion tokens, restrained effects and reduced-motion hard stop."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / "apps/web/app/globals.css").read_text(encoding="utf-8")
DOC = (ROOT / "docs/MOTION.md").read_text(encoding="utf-8")


def test_motion_tokens_encode_easing_timing_and_staging():
    for token in (
        "--motion-ease-standard",
        "--motion-ease-enter",
        "--motion-ease-feedback",
        "--motion-duration-quick: 120ms",
        "--motion-duration-standard: 200ms",
        "--motion-duration-enter: 320ms",
        "--motion-duration-emphasis: 480ms",
        "--motion-stagger-step: 48ms",
    ):
        assert token in CSS
    assert "Slow In and Slow Out" in DOC
    assert "Timing" in DOC
    assert "Staging" in DOC


def test_motion_uses_only_transform_and_opacity_for_entrance():
    assert "@keyframes reading-enter" in CSS
    keyframes = CSS.split("@keyframes reading-enter", 1)[1].split("}", 3)
    assert "opacity" in keyframes[0]
    assert "transform" in keyframes[0]
    assert "prefers-reduced-motion: no-preference" in CSS
    assert "opacity: .94" in CSS
    assert "translateY(5px)" not in CSS  # distance is tokenized


def test_reduced_motion_is_global_hard_off_switch_and_print_is_static():
    reduced = CSS.split("@media (prefers-reduced-motion: reduce)")[-1]
    assert "animation: none !important" in reduced
    assert "transition: none !important" in reduced
    assert "transform: none !important" in reduced
    assert "--motion-duration-enter: 0ms" in reduced
    assert "scroll-behavior: auto !important" in reduced
    assert "@media print" in CSS
    assert "opacity: 1 !important" in CSS


def test_motion_document_records_prohibitions_and_no_runtime_dependency():
    for phrase in (
        "No parallax",
        "No JavaScript animation",
        "No width, height, margin, padding",
        "new runtime dependency",
        "prefers-reduced-motion",
    ):
        assert phrase in DOC
