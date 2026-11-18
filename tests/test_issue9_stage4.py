from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

ASSEMBLIES = {
    "fukuoka-prefecture": {
        "assembly_id": "jp-local-400009-assembly-2023",
        "expenses": 12,
        "factions": 12,
        "members": 0,
        "reports_granularity": "faction",
    },
    "kitakyushu-city": {
        "assembly_id": "jp-local-401005-assembly-2025",
        "expenses": 10,
        "factions": 10,
        "members": 0,
        "reports_granularity": "faction",
    },
    "fukuoka-city": {
        "assembly_id": "jp-local-401307-assembly-2023",
        "expenses": 64,
        "factions": 7,
        "members": 57,
        "reports_granularity": "member",
    },
}


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def assert_valid(schema_path: str, instance: Any) -> None:
    validator = Draft202012Validator(
        load_json(ROOT / schema_path),
        format_checker=FormatChecker(),
    )
    errors = list(validator.iter_errors(instance))
    assert errors == [], "; ".join(error.message for error in errors)


def catalog_source_ids() -> set[str]:
    ids: set[str] = set()
    for path in (ROOT / "data" / "catalog").glob("*.json"):
        value = load_json(path)
        if isinstance(value, dict) and isinstance(value.get("records"), list):
            ids.update(
                record["id"]
                for record in value["records"]
                if isinstance(record, dict) and isinstance(record.get("id"), str)
            )
    return ids


def referenced_sources(value: Any) -> set[str]:
    result: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            if key in {"sources", "source_ids"} and isinstance(child, list):
                result.update(item for item in child if isinstance(item, str))
            result.update(referenced_sources(child))
    elif isinstance(value, list):
        for child in value:
            result.update(referenced_sources(child))
    return result


def load_assembly(slug: str) -> tuple[list[dict], list[dict]]:
    base = ROOT / "data" / "reviewed" / slug / "assembly"
    expenses = load_json(base / "political_activity_expenses.json")
    packets = load_json(base / "expense_evidence_packets.json")
    return expenses, packets


def test_stage4_records_match_contracts() -> None:
    for slug, spec in ASSEMBLIES.items():
        expenses, packets = load_assembly(slug)
        assert len(expenses) == spec["expenses"]
        assert len(packets) == spec["expenses"]

        expected_ids = {
            f"{spec['assembly_id']}-political-activity-expense-2025-{seq:03d}"
            for seq in range(1, spec["expenses"] + 1)
        }
        assert {record["id"] for record in expenses} == expected_ids

        factions = [r for r in expenses if r["recipient_type"] == "faction"]
        members = [r for r in expenses if r["recipient_type"] == "member"]
        assert len(factions) == spec["factions"]
        assert len(members) == spec["members"]

        for record in expenses:
            assert_valid("schemas/political_activity_expense.schema.json", record)
            assert record["assembly_id"] == spec["assembly_id"]
            # FY2025 (Reiwa 7) is the latest published fiscal year for
            # all three assemblies as of this registration.
            assert record["fiscal_year"] == 2025
            assert record["report_status"] == "published"
            # Receipts are never published online by these assemblies;
            # they are viewable in person only.
            assert record["receipt_access"] == "in_person_only"
            assert record["review_status"] == "reviewed"
            assert record["confidence"] == "high"
            # The breakdown lists only categories with a printed amount
            # (a printed zero is kept; a blank category is omitted), and
            # it always sums to the printed expenditure total.
            assert sum(item["amount_yen"] for item in record["breakdown"]) == (record["spent_yen"])
            assert record["granted_yen"] is not None
            assert record["spent_yen"] is not None

        for packet in packets:
            assert_valid("schemas/evidence_packet.schema.json", packet)
            assert packet["subject_type"] == "political_activity_expense"
        assert {packet["subject_id"] for packet in packets} == expected_ids
        for packet in packets:
            record = next(r for r in expenses if r["id"] == packet["subject_id"])
            assert packet["claims"][0]["source_ids"] == record["sources"]

        references = referenced_sources([expenses, packets])
        assert references <= catalog_source_ids()


def test_stage4_amounts_reconcile() -> None:
    # Prefecture and Kitakyushu reports carry grant-only income, so the
    # residual is exactly grant minus expenditure.
    for slug in ("fukuoka-prefecture", "kitakyushu-city"):
        expenses, _ = load_assembly(slug)
        for record in expenses:
            if record["returned_yen"] is None:
                assert record["granted_yen"] - record["spent_yen"] < 0
            else:
                assert record["granted_yen"] - record["spent_yen"] == record["returned_yen"]

    # Fukuoka City reports add deposit interest to the income side; the
    # registered grant excludes interest, so the residual is at least
    # grant minus expenditure and the difference is the printed interest.
    expenses, _ = load_assembly("fukuoka-city")
    for record in expenses:
        assert record["returned_yen"] is not None
        assert record["returned_yen"] >= record["granted_yen"] - record["spent_yen"]


def test_stage4_negative_residuals_are_kept_in_packets() -> None:
    # Two prefecture factions printed a negative residual (expenditure
    # above the grant). returned_yen cannot hold a negative value, so
    # those two records keep it null and the printed value is preserved
    # verbatim in the evidence packet statement instead.
    expenses, packets = load_assembly("fukuoka-prefecture")
    null_records = [r for r in expenses if r["returned_yen"] is None]
    assert {r["recipient_name"] for r in null_records} == {
        "自由と繁栄の会",
        "日本維新の会福岡",
    }
    statements = {packet["subject_id"]: packet["claims"][0]["statement"] for packet in packets}
    for record in null_records:
        printed = record["granted_yen"] - record["spent_yen"]
        assert printed < 0
        assert f"{printed:,}" in statements[record["id"]]


def test_stage4_disclosure_profiles_match_registration() -> None:
    # The stage-0 disclosure profiles already describe the granularity
    # registered here, so they stand unchanged (the Kitakyushu receipts
    # note was only reworded to stop implying the reports themselves are
    # offline; availability and granularity are untouched).
    for slug, spec in ASSEMBLIES.items():
        base = ROOT / "data" / "reviewed" / slug / "assembly"
        profiles = load_json(base / "disclosure_profiles.json")
        items = {item["item"]: item for profile in profiles for item in profile["items"]}
        reports = items["political_activity_expense_reports"]
        assert reports["availability"] == "published"
        assert reports["granularity"] == spec["reports_granularity"]
        receipts = items["political_activity_expense_receipts"]
        assert receipts["availability"] == "restricted"
