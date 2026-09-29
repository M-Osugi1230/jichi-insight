from __future__ import annotations
import json
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker
ROOT=Path(__file__).resolve().parents[1]
def load(p): return json.loads((ROOT/p).read_text(encoding="utf-8"))
def test_okayama_completion_contract():
    c=load("data/catalog/okayama_phase13_completion.json"); s=load("schemas/okayama_phase13_completion.schema.json")
    assert list(Draft202012Validator(s,format_checker=FormatChecker()).iter_errors(c))==[]
    assert c["review_package"]["counts"]=={"perspectives":4,"basic_directions":8,"policies":30,"measures":99,"current_completed_annual_results":0,"fiscal_top_line_records":3}
    assert all(c["quality_gate"].values())
def test_okayama_source_precision_and_availability():
    f=load("data/reviewed/okayama-city/fiscal_records.json")
    notes=" ".join(r["note"] for r in f)
    assert "source" in notes or "余" in notes
    assert {r["amount_yen"] for r in f}=={429_863_380_000,406_500_000_000,387_700_000_000}
    assert load("data/catalog/okayama_current_progress_availability.json")["current_plan_lane"]["annual_result_status"]=="not_yet_available"
def test_okayama_is_complete_in_final_phase13_queue():
    q=load("data/catalog/phase13_designated_city_review_queue.json")
    by={r["official_code"]:r["status"] for r in q["execution_queue"]}
    assert by["331007"]=="reviewed_complete"
    assert q["status"]=="complete"
    assert q["summary"]["reviewed_complete_count"]==18
    assert q["summary"]["next_official_code"] is None
