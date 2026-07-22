#!/usr/bin/env python3
"""Materialize the final Phase 9 source-index batches into queue and completion state."""

from pathlib import Path

from apply_phase9_source_registry import apply, load, write

REGISTRIES = [
    Path("data/catalog/phase9_chugoku_source_registry.json"),
    Path("data/catalog/phase9_shikoku_source_registry.json"),
    Path("data/catalog/phase9_kyushu_okinawa_source_registry.json"),
]


def main() -> None:
    root = Path.cwd()
    for registry in REGISTRIES:
        apply(root, registry)

    queue_path = root / "data/catalog/phase9_execution_queue.json"
    completion_path = root / "data/catalog/phase9_completion.json"
    queue = load(queue_path)
    completion = load(completion_path)

    phase9_indexed = sum(
        item["numeric_target_status"] in {"indexed", "reviewed"}
        for item in queue["items"]
    )
    phase9_reviewed = sum(
        item["numeric_target_status"] == "reviewed" for item in queue["items"]
    )
    assert phase9_indexed == 38
    assert phase9_reviewed == 0

    normalized_test_path = "tests/test_phase9_kyushu_okinawa_source_registry.py"
    generated_test_path = "tests/test_phase9_kyushu-okinawa_source_registry.py"
    for gate in completion["gates"]:
        gate["evidence_paths"] = [
            normalized_test_path if path == generated_test_path else path
            for path in gate["evidence_paths"]
        ]
        if gate["id"] == "all_major_numeric_targets_indexed":
            gate["status"] = "passed"

    completion["scope_note"] = (
        "Phase 9 is in progress. All 47 major policy plans and major numeric-target "
        "entrances are indexed, all nine regional anchors have Evidence-backed "
        "Reviewed targets, and all 38 Phase 9 prefectures have official source "
        "boundaries fixed. Full indicator extraction, Evidence review, publication "
        "and smoke verification remain in progress."
    )
    write(completion_path, completion)


if __name__ == "__main__":
    main()
