import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOADER = ROOT / "apps/web/lib/miyagiActuals.ts"
MANIFEST = ROOT / "data/catalog/miyagi_policy_review_manifest.json"


def test_measure16_actuals_and_evidence_are_loaded_for_publication():
    loader = LOADER.read_text(encoding="utf-8")
    assert "miyagi_kpi_actuals_measure16_2024.json" in loader
    assert "miyagi_kpi_actuals_measure16_2024_evidence_packets.json" in loader
    assert "...measure16Actuals.records" in loader
    assert "...measure16Evidence" in loader
    assert "subjectFiscalYear: measure16Actuals.subject_fiscal_year" in loader


def test_public_miyagi_totals_include_measure16():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["actual_linked_target_group_count"] == 87
    assert manifest["actual_linked_indicator_series_count"] == 100
    assert manifest["actual_linkage_review_needed_series_count"] == 17
    assert manifest["actual_result_row_count"] == 468
    assert manifest["actual_evidence_packet_count"] == 117
