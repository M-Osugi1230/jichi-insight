from __future__ import annotations
import json
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker
ROOT=Path(__file__).resolve().parents[1]
def load(p): return json.loads((ROOT/p).read_text(encoding="utf-8"))
def test_kobe_completion_contract():
    c=load("data/catalog/kobe_phase13_completion.json"); s=load("schemas/kobe_phase13_completion.schema.json")
    assert list(Draft202012Validator(s,format_checker=FormatChecker()).iter_errors(c))==[]
    assert c["review_package"]["counts"]=={"basic_plan_directions":3,"implementation_plan_directions":3,"current_completed_annual_results":0,"fiscal_top_line_records":3}
    assert all(c["quality_gate"].values())
def test_kobe_fiscal_and_availability():
    f=load("data/reviewed/kobe-city/fiscal_records.json")
    assert {r["amount_yen"] for r in f}=={977_781_231_000,945_588_848_718,930_659_433_328}
    p=load("data/catalog/kobe_current_progress_availability.json")
    assert p["current_plan_lane"]["annual_result_status"]=="not_yet_available"
    assert p["governance"]["model"]=="annual_external_expert_progress_management"
def test_kobe_is_complete_in_final_phase13_queue():
    q=load("data/catalog/phase13_designated_city_review_queue.json")
    by={r["official_code"]:r["status"] for r in q["execution_queue"]}
    assert by["281000"]=="reviewed_complete"
    assert q["status"]=="complete"
    assert q["summary"]["reviewed_complete_count"]==18
    assert q["summary"]["next_official_code"] is None
