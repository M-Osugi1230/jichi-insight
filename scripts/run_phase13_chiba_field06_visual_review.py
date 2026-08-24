from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APPLICATOR = ROOT / "scripts/apply_phase13_chiba_field06_visual_review.py"
FIELD06_TEST = ROOT / "tests/test_phase13_chiba_project_work_items_field06.py"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Expected unique {label} patch target, found {count}")
    return text.replace(old, new)


def main() -> None:
    text = APPLICATOR.read_text(encoding="utf-8")
    old = (
        "    text = replace_once(text, '== 29\\n', '== 20\\n', "
        '"queue total pending count")'
    )
    new = (
        "    text = replace_once(\n"
        "        text,\n"
        "        'assert len(queued_ids) == len(set(queued_ids)) == 29',\n"
        "        'assert len(queued_ids) == len(set(queued_ids)) == 20',\n"
        "        \"queue total pending count\",\n"
        "    )"
    )
    APPLICATOR.write_text(
        replace_once(text, old, new, "queue pending-count"),
        encoding="utf-8",
    )

    subprocess.run([sys.executable, str(APPLICATOR)], cwd=ROOT, check=True)

    test_text = FIELD06_TEST.read_text(encoding="utf-8")
    long_assert = (
        '    assert pools[1]["current_text"] == pools[1]["plan_text"] '
        '== pools[1]["target_text"] == "基礎調査"'
    )
    wrapped_assert = (
        "    assert (\n"
        '        pools[1]["current_text"]\n'
        '        == pools[1]["plan_text"]\n'
        '        == pools[1]["target_text"]\n'
        '        == "基礎調査"\n'
        "    )"
    )
    FIELD06_TEST.write_text(
        replace_once(test_text, long_assert, wrapped_assert, "Field 6 lint"),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
