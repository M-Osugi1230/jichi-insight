from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APPLICATOR = ROOT / "scripts/apply_phase13_chiba_field04_visual_review.py"


def main() -> None:
    text = APPLICATOR.read_text(encoding="utf-8")
    old = '    text = replace_once(text, "== 41\\n", "== 33\\n", "queue total pending count")'
    new = (
        "    text = replace_once(\n"
        "        text,\n"
        "        'assert len(queued_ids) == len(set(queued_ids)) == 41',\n"
        "        'assert len(queued_ids) == len(set(queued_ids)) == 33',\n"
        "        \"queue total pending count\",\n"
        "    )"
    )
    if old not in text:
        raise RuntimeError("Expected queue assertion patch target was not found")
    if text.count(old) != 1:
        raise RuntimeError("Queue assertion patch target is ambiguous")
    APPLICATOR.write_text(text.replace(old, new), encoding="utf-8")
    subprocess.run([sys.executable, str(APPLICATOR)], cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
