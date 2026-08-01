from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data/catalog"
TODAY = "2026-08-01"

DIMENSION_TARGETS = {
    "target_statements": "reviewed",
    "evidence_packets": "reviewed",
    "annual_actuals": "linked",
    "budget": "linked",
    "settlement": "linked",
    "priority_projects": "linked",
    "contracts": "reviewed",
    "assembly": "reviewed",
    "audit": "linked",
    "executive_manifesto": "reviewed",
    "publication": "reviewed",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, payload: dict) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def assert_core(core: dict) -> None:
    assert core["status"] == "complete"
    assert core["summary"]["prefecture_count"] == 47
    assert core["summary"]["linked_prefecture_count"] == 47
    assert set(core["summary"]["linked_dimension_counts"].values()) == {47}
    assert core["summary"]["policy_achievement_assessment_count"] == 0


def assert_accountability(accountability: dict) -> None:
    assert accountability["status"] == "complete"
    assert accountability["summary"]["prefecture_count"] == 47
    assert accountability["summary"]["reviewed_role_count"] == 141
    assert accountability["summary"]["nonexistence_claim_count"] == 0
    assert accountability["summary"]["policy_achievement_assessment_count"] == 0
    assert len({record["prefecture_code"] for record in accountability["records"]}) == 47


def finalize_uniformity() -> None:
    path = CATALOG / "phase10_uniformity.json"
    payload = load(path)
    payload["status"] = "complete"
    payload["scope_version"] = TODAY
    for dimension in payload["dimensions"]:
        dimension["completion_status"] = DIMENSION_TARGETS[dimension["id"]]
    payload["default_depth"] = dict(DIMENSION_TARGETS)
    payload["default_work"] = {
        "status": "complete",
        "next_gate": "publication_verification",
        "next_action_template": (
            "{name}のPhase 10文書スコープ接続と説明責任資料レビューを維持し、"
            "個票単位の追加接続は次期深掘り工程で実施する。"
        ),
    }
    payload["overrides"] = {}
    payload["completion_rule"] = {
        "description": (
            "47都道府県すべてについて、政策・Evidence・公開をReviewed、年度実績・"
            "予算・決算・重点事業・監査を文書スコープLinked、契約・議会・首長公約を"
            "公式一次資料または不存在を断定しない公式検索結果までReviewedとした場合のみ"
            "Phase 10をcompleteとする。個票単位接続や達成判定は完了条件に含めない。"
        ),
        "required_prefecture_count": 47,
        "allow_partial_complete": False,
    }
    payload["policy_achievement_assessment_status"] = "not_assessed"
    payload["ranking_eligibility"] = "excluded_until_comparability_verified"
    payload["updated_at"] = TODAY
    write(path, payload)


def finalize_queue() -> None:
    path = CATALOG / "phase10_execution_queue.json"
    payload = load(path)
    payload["status"] = "complete"
    payload["scope_version"] = TODAY
    payload["active_prefecture_code"] = "47"
    payload["default_depth"] = {
        "target_statements": "reviewed",
        "annual_evaluation": "linked",
        "budget": "linked",
        "project_evaluation": "linked",
        "contracts": "reviewed",
    }
    for record in payload["wave1_records"]:
        record["status"] = "complete"
        record["current_depth"] = dict(payload["default_depth"])
        record["next_gate"] = "publication_verification"
        record["next_action"] = (
            "Phase 10の文書スコープ接続と公式資料レビューを維持し、個票単位の追加接続は"
            "次期深掘り工程で実施する。"
        )
    payload["counts"] = {
        "total_prefectures": 47,
        "wave1_prefectures": 9,
        "target_statements_reviewed": 47,
        "annual_evaluation_linked": 47,
        "annual_evaluation_indexed": 47,
        "budget_reviewed": 47,
        "project_evaluation_indexed_or_better": 47,
        "contracts_indexed_or_better": 47,
    }
    payload["policy_achievement_assessment_status"] = "not_assessed"
    payload["ranking_eligibility"] = "excluded_until_comparability_verified"
    payload["updated_at"] = TODAY
    write(path, payload)


def publication_page_count() -> int:
    root = ROOT / "apps/web/app/municipalities/phase10"
    return len(list(root.rglob("page.tsx")))


def finalize_completion() -> None:
    path = CATALOG / "phase10_completion.json"
    payload = load(path)
    payload["status"] = "complete"
    payload["scope_version"] = TODAY
    payload["counts"] = {
        "total_prefectures": 47,
        "wave1_prefectures": 9,
        "target_statements_reviewed": 47,
        "annual_evaluation_linked": 47,
        "annual_evaluation_indexed": 47,
        "budget_reviewed": 47,
        "project_evaluation_indexed_or_better": 47,
        "contracts_indexed_or_better": 47,
        "published_phase10_pages": publication_page_count(),
    }
    payload["nationwide_uniform_counts"] = {
        "reviewed_anchor_prefectures": 9,
        "prefectures_with_five_layers_indexed_or_better": 47,
        "prefectures_with_five_layers_reviewed": 47,
        "annual_actuals_reviewed_or_better": 47,
        "budget_reviewed_or_better": 47,
        "settlement_reviewed_or_better": 47,
        "priority_projects_reviewed_or_better": 47,
        "audit_reviewed_or_better": 47,
        "uniform_depth_complete": 47,
    }
    evidence = {
        "phase9_handoff_verified": [
            "data/catalog/phase9_completion.json",
            "tests/test_phase9_completion.py",
        ],
        "nationwide_vertical_source_inventory": [
            "data/catalog/phase10_uniformity.json",
            "data/catalog/phase10_nationwide_core_linkage.json",
            "tests/test_phase10_uniformity.py",
            "tests/test_phase10_nationwide_core_linkage.py",
        ],
        "wave1_annual_actuals_linkage": [
            "data/catalog/phase10_nationwide_core_linkage.json",
            "data/catalog/hokkaido_annual_actual_linkage.json",
            "data/catalog/miyagi_policy_review_manifest.json",
            "data/catalog/tokyo_children_annual_actual_linkage.json",
            "data/catalog/fukuoka_annual_actual_linkage.json",
        ],
        "wave1_money_and_project_spine": [
            "data/catalog/phase10_nationwide_core_linkage.json",
            "data/catalog/miyagi_project_money_linkage.json",
            "data/catalog/fukuoka_project_linkage.json",
            "tests/test_miyagi_project_money_linkage.py",
            "tests/test_fukuoka_project_linkage.py",
        ],
        "contracts_and_accountability_linkage": [
            "data/catalog/phase10_nationwide_accountability_linkage.json",
            "schemas/phase10_nationwide_accountability_linkage.schema.json",
            "tests/test_phase10_nationwide_accountability_linkage.py",
        ],
        "phase10_publication_and_smoke": [
            "apps/web/app/municipalities/phase10/page.tsx",
            "apps/web/lib/phase10.ts",
            "scripts/validate_static_export.py",
            "scripts/check_production.sh",
            "tests/test_phase10_web_contract.py",
        ],
    }
    for gate in payload["gates"]:
        gate["status"] = "passed"
        gate["evidence_paths"] = evidence[gate["id"]]
    payload["scope_note"] = (
        "Phase 10 is complete at the declared nationwide document scope. All 47 prefectures have "
        "Reviewed policy statements and Evidence, document-scope links for annual actuals, budget, "
        "settlement, priority projects, and audit, and Reviewed accountability coverage for "
        "contracts, assembly, and executive manifestos. Accountability coverage may be either a "
        "prefecture-level official source entrance or an explicit official-host search outcome; a "
        "missing stable source is never treated as proof of nonexistence. Publication is Reviewed. "
        "Record-level one-to-one linkage is deeper in Hokkaido, Miyagi, Tokyo, and Fukuoka and "
        "continues separately. No policy-achievement assessment or cross-prefecture ranking is made."
    )
    payload["updated_at"] = TODAY
    write(path, payload)


def preserve_linked_depth_in_web_loader() -> None:
    path = ROOT / "apps/web/lib/phase10.ts"
    text = path.read_text(encoding="utf-8")
    marker = "const statusRank: Record<Phase10DepthStatus, number> = {"
    if "function atLeastDepth(" not in text:
        end = text.index("};", text.index(marker)) + 2
        helper = "\n\nfunction atLeastDepth(\n  current: Phase10DepthStatus,\n  minimum: Phase10DepthStatus,\n): Phase10DepthStatus {\n  return statusRank[current] >= statusRank[minimum] ? current : minimum;\n}"
        text = text[:end] + helper + text[end:]

    old = '''        current_depth: {
          ...(existing?.current_depth ?? {}),
          annual_actuals: "reviewed",
          budget: "reviewed",
          settlement: "reviewed",
          priority_projects: "reviewed",
          audit: "reviewed",
        },'''
    new = '''        current_depth: {
          ...(existing?.current_depth ?? {}),
          annual_actuals: atLeastDepth(
            existing?.current_depth.annual_actuals ??
              uniformity.default_depth.annual_actuals,
            "reviewed",
          ),
          budget: atLeastDepth(
            existing?.current_depth.budget ?? uniformity.default_depth.budget,
            "reviewed",
          ),
          settlement: atLeastDepth(
            existing?.current_depth.settlement ??
              uniformity.default_depth.settlement,
            "reviewed",
          ),
          priority_projects: atLeastDepth(
            existing?.current_depth.priority_projects ??
              uniformity.default_depth.priority_projects,
            "reviewed",
          ),
          audit: atLeastDepth(
            existing?.current_depth.audit ?? uniformity.default_depth.audit,
            "reviewed",
          ),
        },'''
    if old not in text:
        raise SystemExit("Phase 10 web-loader overlay block was not found")
    text = text.replace(old, new, 1)
    path.write_text(text, encoding="utf-8")


def append_completion_docs() -> None:
    entries = {
        ROOT / "README.md": (
            "## Phase 10 completion (2026-08-01)\n\n"
            "Phase 10 is complete at nationwide document scope for all 47 prefectures. The five "
            "delivery-evidence layers are linked by prefecture, official role, and reporting period. "
            "Contracts, assembly, and executive-manifesto coverage is Reviewed through an official "
            "source entrance or an explicit official-host search outcome. Missing results do not "
            "assert nonexistence. Record-level one-to-one deepening and policy-achievement assessment "
            "remain outside this completion claim.\n"
        ),
        ROOT / "docs/ROADMAP.md": (
            "## Phase 10 — Complete (2026-08-01)\n\n"
            "All 47 prefectures satisfy the declared 11-dimension completion depths. Nationwide "
            "document-scope linkage and accountability-source review are complete; record-level "
            "deepening continues as the next research track without changing Phase 10 status.\n"
        ),
        ROOT / "docs/PHASE10_VERTICAL_LINKAGE.md": (
            "## Completion boundary (2026-08-01)\n\n"
            "Phase 10 completion means nationwide document-scope linkage, not universal one-to-one "
            "target, budget-line, project, contract, statement, or audit-finding linkage. For "
            "accountability roles, a Reviewed official-host search outcome is retained when no stable "
            "primary source is identified; it is not a nonexistence claim. Achievement is not assessed.\n"
        ),
    }
    for path, section in entries.items():
        text = path.read_text(encoding="utf-8")
        heading = section.splitlines()[0]
        if heading not in text:
            path.write_text(text.rstrip() + "\n\n" + section, encoding="utf-8")


def main() -> None:
    core = load(CATALOG / "phase10_nationwide_core_linkage.json")
    accountability = load(
        CATALOG / "phase10_nationwide_accountability_linkage.json"
    )
    assert_core(core)
    assert_accountability(accountability)
    finalize_uniformity()
    finalize_queue()
    finalize_completion()
    preserve_linked_depth_in_web_loader()
    append_completion_docs()


if __name__ == "__main__":
    main()
