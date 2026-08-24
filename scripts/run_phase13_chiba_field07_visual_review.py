from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APPLICATOR = ROOT / "scripts/apply_phase13_chiba_field07_visual_review.py"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Expected one {label} target, found {count}")
    return text.replace(old, new)


def main() -> None:
    text = APPLICATOR.read_text(encoding="utf-8")
    text = replace_once(
        text,
        '    assert (special_zone["current_text"], special_zone["plan_text"], special_zone["target_text"]) == (\n',
        '    assert (\n'
        '        special_zone["current_text"],\n'
        '        special_zone["plan_text"],\n'
        '        special_zone["target_text"],\n'
        '    ) == (\n',
        "special-zone assertion wrap",
    )
    text = replace_once(
        text,
        '    assert all(review_id.startswith("chiba-f08-") for review_id in structuring["pending_review_ids"])\n',
        '    assert all(\n'
        '        review_id.startswith("chiba-f08-")\n'
        '        for review_id in structuring["pending_review_ids"]\n'
        '    )\n',
        "remaining-field assertion wrap",
    )
    APPLICATOR.write_text(text, encoding="utf-8")
    subprocess.run([sys.executable, str(APPLICATOR)], cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
