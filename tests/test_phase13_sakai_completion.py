from __future__ import annotations
import json
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

ROOT=Path(__file__).resolve().parents[1]
def load(p): return json.loads((ROOT/p).read_text(encoding="utf-8"))

def test_sakai_completion_contract():
    c=load("data/catalog/sakai_phase13_completion.json")
    s=load("schemas/sakai_phase13_completion.schema.json")
    assert list(Draft202012Validator(s,format_checker=FormatChecker()).iter_errors(c))==[]
    assert c["review_package"]["counts"]=={"kgi":3,"priority_strategies":5,"measures":27,"current_completed_annual_results":0,"fiscal_top_line_records":3}
    assert all(c["quality_gate"].values())

def test_sakai_fiscal_and_availability():
    fiscal=load("data/reviewed/sakai-city/fiscal_records.json")
    amounts={r["metric"]:[] for r in fiscal}
    for r in fiscal: amounts[r["metric"]].append(r["amount_yen"])
    assert 521_700_000_000 in amounts["total_revenue"]
    assert 477_935_503_067 in amounts["total_revenue"]
    assert 470_108_227_969 in amounts["total_expenditure"]
    p=load("data/catalog/sakai_current_progress_availability.json")
    assert p["current_plan_lane"]["annual_progress_status"]=="not_yet_available"
    assert "流用しない" in p["historical_lane"]["boundary"]

def test_sakai_queue_advances_to_kobe():
    q=load("data/catalog/phase13_designated_city_review_queue.json")
    by={r["official_code"]:r["status"] for r in q["execution_queue"]}
    assert by["271403"]=="reviewed_complete"
    assert by["281000"]=="review_in_progress"
