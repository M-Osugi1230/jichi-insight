from __future__ import annotations
import json
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker
ROOT=Path(__file__).resolve().parents[1]
def load(p): return json.loads((ROOT/p).read_text(encoding="utf-8"))
def test_hiroshima_completion_contract():
    c=load("data/catalog/hiroshima_phase13_completion.json"); s=load("schemas/hiroshima_phase13_completion.schema.json")
    assert list(Draft202012Validator(s,format_checker=FormatChecker()).iter_errors(c))==[]
    assert c["review_package"]["counts"]=={"plan_layers":3,"current_implementation_plan_period_years":6,"separately_identified_current_annual_result_packages":0,"fiscal_top_line_records":3}
    assert all(c["quality_gate"].values())
def test_hiroshima_fiscal_and_result_boundary():
    f=load("data/reviewed/hiroshima-city/fiscal_records.json")
    assert {r["amount_yen"] for r in f}=={794_011_359_000,720_118_240_000,716_676_720_000}
    p=load("data/catalog/hiroshima_current_progress_availability.json")
    assert p["current_separate_annual_result"]["status"]=="not_separately_identified_in_declared_v1_sources"
    assert "同一視しない" in p["current_separate_annual_result"]["boundary"]
def test_hiroshima_is_complete_in_final_phase13_queue():
    q=load("data/catalog/phase13_designated_city_review_queue.json")
    by={r["official_code"]:r["status"] for r in q["execution_queue"]}
    assert by["341002"]=="reviewed_complete"
    assert q["status"]=="complete"
    assert q["summary"]["reviewed_complete_count"]==18
    assert q["summary"]["next_official_code"] is None
