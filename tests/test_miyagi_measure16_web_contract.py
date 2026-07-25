"""Keep Miyagi measures 16 through 18 on the public-data path."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOADER = ROOT / "apps/web/lib/miyagiActuals.ts"
MANIFEST = ROOT / "data/catalog/miyagi_policy_review_manifest.json"


def test_measure16_through_measure18_actuals_remain_loaded_for_publication():
    loader = LOADER.read_text(encoding="utf-8")
    for measure in (16, 17, 18):
        assert f"miyagi_kpi_actuals_measure{measure}_2024.json" in loader
        assert f"miyagi_kpi_actuals_measure{measure}_2024_evidence_packets.json" in loader
        assert f"...measure{measure}Actuals.records" in loader
        assert f"...measure{measure}Evidence" in loader

    assert "subjectFiscalYear: measure18Actuals.subject_fiscal_year" in loader
    assert "evaluationFiscalYear: measure18Actuals.evaluation_fiscal_year" in loader


def test_public_miyagi_totals_include_measure18():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["actual_linked_target_group_count"] == 94
    assert manifest["actual_linked_indicator_series_count"] == 108
    assert manifest["actual_linkage_review_needed_series_count"] == 19
    assert manifest["actual_result_row_count"] == 508
    assert manifest["actual_evidence_packet_count"] == 127
