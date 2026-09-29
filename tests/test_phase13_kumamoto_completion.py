from __future__ import annotations
import json
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

ROOT=Path(__file__).resolve().parents[1]
def load(p): return json.loads((ROOT/p).read_text(encoding="utf-8"))

def test_kumamoto_completion_contract():
    c=load("data/catalog/kumamoto_phase13_completion.json")
    s=load("schemas/kumamoto_phase13_completion.schema.json")
    assert list(Draft202012Validator(s,format_checker=FormatChecker()).iter_errors(c))==[]
    assert c["review_package"]["counts"]=={
        "plan_layers":3,"visions":8,"fy2026_priority_items":4,
        "reviewed_current_evaluation_fiscal_years":1,"accountability_roles":2,
        "fiscal_top_line_records":3,
    }
    assert all(c["quality_gate"].values())

def test_kumamoto_current_progress_roles_are_separate():
    p=load("data/catalog/kumamoto_current_progress_review_summary.json")
    assert p["reporting_fiscal_year"]==2024
    assert p["administrative_evaluation"]["status"]=="published"
    assert p["deliberative_review"]["actor"]=="熊本市総合計画審議会"
    assert p["administrative_evaluation"]["evidence_role"]!="external_deliberative_review"
    assert "独自評価へ変換しない" in p["administrative_evaluation"]["boundary"]

def test_kumamoto_fiscal_top_lines_and_lineage():
    f={r["id"]:r for r in load("data/reviewed/kumamoto-city/fiscal_records.json")}
    assert f["jp-local-431001-fiscal-2026-total-revenue"]["amount_yen"]==437_840_000_000
    assert f["jp-local-431001-fiscal-2024-total-revenue"]["amount_yen"]==428_730_240_000
    assert f["jp-local-431001-fiscal-2024-total-expenditure"]["amount_yen"]==419_712_090_000
    assert "原案どおり可決" in f["jp-local-431001-fiscal-2026-total-revenue"]["metric_label"]

def test_kumamoto_queue_is_final_city_complete():
    q=load("data/catalog/phase13_designated_city_review_queue.json")
    by={r["official_code"]:r["status"] for r in q["execution_queue"]}
    assert by["431001"]=="reviewed_complete"
    assert all(r["status"]=="reviewed_complete" for r in q["execution_queue"])
    assert q["summary"]["reviewed_complete_count"]==18
    assert q["summary"]["review_in_progress_count"]==0
    assert q["summary"]["pending_record_review_count"]==0
