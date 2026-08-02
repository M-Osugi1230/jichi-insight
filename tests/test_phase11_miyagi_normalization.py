from __future__ import annotations

import importlib.util
import json
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts/normalize_phase11_miyagi.py"
SCHEMA_PATH = ROOT / "schemas/phase11_record_linkage.schema.json"
MANIFEST_PATH = ROOT / "data/catalog/phase11_miyagi_normalization.json"
MANIFEST_SCHEMA_PATH = ROOT / "schemas/phase11_miyagi_normalization.schema.json"

spec = importlib.util.spec_from_file_location(
    "normalize_phase11_miyagi",
    SCRIPT_PATH,
)
assert spec is not None
assert spec.loader is not None
normalizer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(normalizer)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def source_records() -> list[tuple[str, dict]]:
    _, records = normalizer.load_source_records(ROOT)
    return records


def normalized_catalog() -> dict:
    return normalizer.build_catalog(ROOT)


def measurement_by_role(record: dict) -> dict[str, dict]:
    return {
        measurement["role"]: measurement
        for measurement in record["measurements"]
    }


def expected_candidates(source: dict) -> list[dict]:
    return [
        {
            "policy_ref": candidate["policy_id"],
            "measure_ref": candidate["measure_id"],
            "name": candidate["project_name"],
            "department": candidate["department"],
            "office": candidate["office"],
            "amount_thousand_yen": candidate[
                "settlement_amount_thousand_yen"
            ],
            "page": candidate["settlement_pdf_page"],
        }
        for candidate in source["settlement_candidates"]
    ]


def expected_locations(source: dict) -> list[dict]:
    candidates = [
        {
            "source_number": 1,
            "page": source["budget_pdf_page"],
            "is_reprint": False,
        }
    ]
    if source["settlement_pdf_page"] is not None:
        candidates.append(
            {
                "source_number": 2,
                "page": source["settlement_pdf_page"],
                "is_reprint": False,
            }
        )
    candidates.extend(
        {
            "source_number": 2,
            "page": candidate["settlement_pdf_page"],
            "is_reprint": False,
        }
        for candidate in source["settlement_candidates"]
    )

    output: list[dict] = []
    seen: set[tuple[int, int]] = set()
    for location in candidates:
        key = (location["source_number"], location["page"])
        if key not in seen:
            seen.add(key)
            output.append(location)
    return output


def test_miyagi_normalization_manifest_matches_schema():
    validator = Draft202012Validator(
        load(MANIFEST_SCHEMA_PATH),
        format_checker=FormatChecker(),
    )
    manifest = load(MANIFEST_PATH)

    assert list(validator.iter_errors(manifest)) == []
    for path_field in (
        "source_catalog",
        "normalizer",
        "record_schema",
        "regression_test",
    ):
        assert (ROOT / manifest[path_field]).exists()
    assert all((ROOT / path).exists() for path in manifest["source_files"])


def test_all_627_records_match_the_reusable_phase11_schema():
    validator = Draft202012Validator(load(SCHEMA_PATH))
    catalog = normalized_catalog()

    assert len(catalog["records"]) == 627
    for record in catalog["records"]:
        assert list(validator.iter_errors(record)) == []


def test_source_order_ids_and_statuses_are_preserved_without_skips():
    sources = source_records()
    catalog = normalized_catalog()
    normalized = catalog["records"]

    expected_sequences = list(range(1, 628))
    source_sequences = [
        int(record["id"].rsplit("-", maxsplit=1)[-1])
        for _, record in sources
    ]
    assert source_sequences == expected_sequences
    assert [record["subject"]["sequence"] for record in normalized] == (
        expected_sequences
    )
    assert [record["source_record_id"] for record in normalized] == [
        record["id"] for _, record in sources
    ]
    assert len({record["id"] for record in normalized}) == 627

    statuses = Counter(record["linkage_status"] for record in normalized)
    assert statuses == {
        "linked": 238,
        "partial": 26,
        "not_linked": 363,
    }
    manifest = load(MANIFEST_PATH)
    assert {
        "record_count": len(normalized),
        "linked_record_count": statuses["linked"],
        "partial_record_count": statuses["partial"],
        "not_linked_record_count": statuses["not_linked"],
        "policy_achievement_assessment_count": 0,
    } == manifest["summary"]


def test_every_source_identity_and_money_field_is_mapped_exactly():
    normalized_by_source_id = {
        record["source_record_id"]: record
        for record in normalized_catalog()["records"]
    }

    for source_registry, source in source_records():
        record = normalized_by_source_id[source["id"]]
        subject = record["subject"]
        context = record["context"]
        measurements = measurement_by_role(record)

        hierarchy_refs = [
            value
            for value in (source["policy_id"], source["measure_id"])
            if value is not None
        ]
        assert record["source_registry"] == source_registry
        assert record["linkage_status"] == source["linkage_status"]
        assert record["partial_reason"] == (
            None
            if source["linkage_status"] == "linked"
            else source["match_basis"]
        )
        assert record["boundary"] == source["boundary"]
        assert subject == {
            "record_ref": source["id"],
            "sequence": int(source["id"].rsplit("-", maxsplit=1)[-1]),
            "name": source["project_name"],
            "source_name": source["project_name"],
            "definition": "",
            "hierarchy_refs": hierarchy_refs,
        }
        assert context == {
            "policy_ref": source["policy_id"],
            "measure_ref": source["measure_id"],
            "normalized_name": source["project_name_normalized"],
            "department": source["department"],
            "office": source["office"],
            "implementation_period": source["implementation_period"],
            "match_basis": source["match_basis"],
            "settlement_project_number_text": source[
                "settlement_project_number_text"
            ],
            "settlement_candidates": expected_candidates(source),
        }

        assert measurements["budget"] == {
            "role": "budget",
            "status": "reported",
            "period_text": source["budget_period"],
            "value_text": source["budget_amount_text"],
            "components": [
                {
                    "label": None,
                    "unit": "千円",
                    "value_text": source["budget_amount_text"],
                    "value": source["budget_amount_thousand_yen"],
                    "value_status": "numeric",
                }
            ],
            "evidence": {
                "source_number": 1,
                "page": source["budget_pdf_page"],
            },
        }
        assert record["evidence"] == {
            "primary_source_number": 1,
            "primary_page": source["budget_pdf_page"],
            "locations": expected_locations(source),
        }


def test_linked_records_keep_budget_and_settlement_separate():
    source_by_id = {
        source["id"]: source
        for _, source in source_records()
    }
    linked = [
        record
        for record in normalized_catalog()["records"]
        if record["linkage_status"] == "linked"
    ]

    assert len(linked) == 238
    for record in linked:
        source = source_by_id[record["source_record_id"]]
        measurements = measurement_by_role(record)
        settlement = measurements["settlement"]

        assert record["partial_reason"] is None
        assert measurements["budget"]["period_text"] == "令和8年度"
        assert settlement == {
            "role": "settlement",
            "status": "available",
            "period_text": "令和6年度",
            "value_text": source["settlement_amount_text"],
            "components": [
                {
                    "label": None,
                    "unit": "千円",
                    "value_text": source["settlement_amount_text"],
                    "value": source["settlement_amount_thousand_yen"],
                    "value_status": "numeric",
                }
            ],
            "evidence": {
                "source_number": 2,
                "page": source["settlement_pdf_page"],
            },
        }
        assert record["context"]["settlement_candidates"] == []
        assert record["evaluation_status"] == "not_assessed"
        assert record["comparability_status"] == "excluded_until_verified"


def test_partial_records_keep_all_candidates_without_promotion():
    source_by_id = {
        source["id"]: source
        for _, source in source_records()
    }
    partial = [
        record
        for record in normalized_catalog()["records"]
        if record["linkage_status"] == "partial"
    ]

    assert len(partial) == 26
    reasons = Counter(record["partial_reason"] for record in partial)
    assert reasons == {
        "exact_name_measure_changed_or_relisted": 24,
        "same_measure_organization_changed": 2,
    }
    for record in partial:
        source = source_by_id[record["source_record_id"]]
        settlement = measurement_by_role(record)["settlement"]
        assert settlement == {
            "role": "settlement",
            "status": "not_promoted",
            "period_text": "",
            "value_text": "",
            "components": [],
            "evidence": {"source_number": None, "page": None},
        }
        assert record["context"]["settlement_candidates"] == (
            expected_candidates(source)
        )
        assert record["context"]["settlement_candidates"]
        assert source["settlement_period"] is None
        assert source["settlement_amount_thousand_yen"] is None
        assert source["settlement_pdf_page"] is None


def test_not_linked_records_remain_explicitly_unavailable():
    not_linked = [
        record
        for record in normalized_catalog()["records"]
        if record["linkage_status"] == "not_linked"
    ]

    assert len(not_linked) == 363
    assert {
        record["partial_reason"] for record in not_linked
    } == {"exact_name_not_found_in_fy2024_settlement"}
    for record in not_linked:
        settlement = measurement_by_role(record)["settlement"]
        assert settlement == {
            "role": "settlement",
            "status": "not_available",
            "period_text": "",
            "value_text": "",
            "components": [],
            "evidence": {"source_number": None, "page": None},
        }
        assert record["context"]["settlement_candidates"] == []
        assert len(record["evidence"]["locations"]) == 1


def test_match_basis_counts_reconcile_with_manifest_and_source_catalog():
    catalog = normalized_catalog()
    manifest = load(MANIFEST_PATH)
    source_catalog = load(ROOT / manifest["source_catalog"])
    actual = Counter(
        record["context"]["match_basis"]
        for record in catalog["records"]
    )

    assert dict(actual) == manifest["match_basis_counts"]
    assert dict(actual) == source_catalog["summary"]["match_basis_counts"]
    assert catalog["summary"]["match_basis_counts"] == dict(sorted(actual.items()))


def test_normalization_is_deterministic():
    assert normalizer.build_catalog(ROOT) == normalizer.build_catalog(ROOT)
