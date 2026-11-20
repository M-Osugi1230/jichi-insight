"""Issue #810: Kanagawa prefecture detail page and three-assembly Stage 4 Web coverage."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
WEB = ROOT / "apps/web"


def load(relative: str):
    return json.loads((DATA / relative).read_text(encoding="utf-8"))


def test_kanagawa_prefecture_page_facts_match_reviewed_plan_finance_projects_and_promises():
    municipality = load("reviewed/kanagawa-prefecture/municipality.json")
    plan = load("reviewed/kanagawa-prefecture/plan_review.json")
    budget = load("reviewed/kanagawa-prefecture/fiscal_records.json")
    settlements = load("reviewed/kanagawa-prefecture/settlement_records.json")
    projects = load("reviewed/kanagawa-prefecture/projects.json")
    selection = load("catalog/kanagawa_priority_project_selection.json")
    terms = load("entities/executives/executive_terms.json")
    promises = load("entities/executives/promises.json")
    page = (WEB / "app/municipalities/kanagawa-prefecture/page.tsx").read_text(encoding="utf-8")
    catalog = (WEB / "lib/catalog.ts").read_text(encoding="utf-8")

    assert municipality["official_code"] == "140007"
    assert municipality["name_ja"] == "神奈川県"
    assert municipality["data_status"] == "reviewed"
    assert plan["review_status"] == "reviewed"
    assert len(plan["records"]) == 4
    assert any("新かながわグランドデザイン" in record["title"] for record in plan["records"])
    assert any("13のプロジェクト" in record["title"] for record in plan["records"])

    assert len(budget) == 3
    budget_by_metric = {record["metric"]: record for record in budget}
    assert budget_by_metric["total_revenue"]["amount_yen"] == 2_375_969_000_000
    assert budget_by_metric["local_tax"]["amount_yen"] == 1_525_483_133_000
    assert budget_by_metric["total_expenditure"]["amount_yen"] == 2_375_969_000_000
    assert all(record["fiscal_year"] == 2026 for record in budget)
    assert all(record["stage"] == "initial_budget" for record in budget)
    assert all(record["account_type"] == "general" for record in budget)

    assert len(settlements) == 51
    assert {record["fiscal_year"] for record in settlements} == {2022, 2023, 2024}
    assert all(record["stage"] == "settlement" for record in settlements)
    assert all(record["account_type"] == "ordinary" for record in settlements)
    assert all(record["review_status"] == "reviewed" for record in settlements)

    assert len(projects) == 20
    assert len({record["series_id"] for record in projects}) == 10
    selected_titles = {item["official_title"] for item in selection["selections"]}
    assert len(selected_titles) == 10
    assert {record["official_title"] for record in projects} == selected_titles
    assert all(record["municipality_id"] == "jp-local-140007" for record in projects)
    for record in projects:
        assert record["review_status"] == "reviewed"
        assert record["budget_records"]
        for budget_record in record["budget_records"]:
            if budget_record["amount_yen"] is not None:
                # The official report publishes each project amount in units of 100 million yen.
                assert budget_record["amount_yen"] % 100_000_000 == 0
                assert "1億円未満" in budget_record["note"]
                assert "億円単位" in budget_record["note"]

    governor_terms = [
        term for term in terms
        if term["municipality_id"] == "jp-local-140007" and term["office"] == "governor"
        and term["status"] == "current" and term["review_status"] == "reviewed"
    ]
    assert len(governor_terms) == 1
    governor = governor_terms[0]
    assert governor["person_name"] == "黒岩 祐治"
    assert governor["term_start"] == "2023-04-23"
    assert governor["term_end"] == "2027-04-22"
    governor_promises = [
        promise for promise in promises
        if promise["municipality_id"] == "jp-local-140007"
        and promise["executive_term_id"] == governor["id"]
        and promise["review_status"] == "reviewed"
    ]
    assert len(governor_promises) == 33

    assert "新かながわグランドデザイン" in page
    assert "2022〜2024年度" in page
    assert "2026年度" in page
    assert "13プロジェクト" in page
    assert "Reviewed KPI" in page
    assert "1億円未満切捨て" in page
    assert "総合計画審議会による二次評価" in page
    assert "governorPromises.length" in page
    assert "reviewedProjects.length" in page
    assert "reviewedProjectRecords.length" in page
    assert "kanagawaFinance.records.length" in page
    assert "kanagawa-prefecture" in catalog
    assert 'href: "/municipalities/kanagawa-prefecture"' in catalog

    # Regression guard for the known cross-prefecture copy/paste failure mode.
    for foreign_copy in ("副首都ビジョン", "府政運営の基本方針", "吉村洋文", "北海道総合計画", "鈴木直道"):
        assert foreign_copy not in page


def test_kanagawa_assembly_display_facts_match_reviewed_registry():
    assembly = load("reviewed/kanagawa-prefecture/assembly/assembly_records.json")[0]
    disclosure = load("reviewed/kanagawa-prefecture/assembly/disclosure_profiles.json")[0]
    proposals = load("reviewed/kanagawa-prefecture/assembly/proposals.json")
    votes = load("reviewed/kanagawa-prefecture/assembly/votes.json")
    faction_votes = load("reviewed/kanagawa-prefecture/assembly/faction_votes.json")
    expenses = load("reviewed/kanagawa-prefecture/assembly/political_activity_expenses.json")
    trips = load("reviewed/kanagawa-prefecture/assembly/inspection_trips.json")
    detail = (WEB / "app/assemblies/[slug]/page.tsx").read_text(encoding="utf-8")
    page = (WEB / "app/municipalities/kanagawa-prefecture/page.tsx").read_text(encoding="utf-8")

    assert assembly["name"] == "神奈川県議会"
    assert assembly["seat_count"] == 105
    assert assembly["term_start"] == "2023-04-30"
    assert assembly["term_end"] == "2027-04-29"
    assert sum(faction["member_count"] for faction in assembly["factions"]) == 99
    assert len(proposals) == 45
    assert len(votes) == 45
    assert len(faction_votes) == 468
    assert len(expenses) == 19
    assert len(trips) == 79

    items = {item["item"]: item for item in disclosure["items"]}
    assert items["faction_votes"]["availability"] == "published"
    assert items["member_votes"]["availability"] == "not_published"
    assert "会派単位のみ" in items["member_votes"]["note"] or "議員個人別" in items["member_votes"]["note"]
    assert "▲" in items["faction_votes"]["note"]
    assert "本会期では▲は使われておらず" in items["faction_votes"]["note"]
    assert all(vote["member_vote_availability"] == "not_published" for vote in votes)
    assert all(vote["member_votes"] == [] for vote in votes)
    assert "神奈川県議会の賛否は会派別のみ公表" in detail
    assert "▲は使われていません" in detail
    assert "議員個人別の賛否は公表されていません" in page


def test_yokohama_assembly_display_facts_match_reviewed_records_and_caveats():
    base = "reviewed/yokohama-city/assembly"
    assembly = load(f"{base}/assembly_records.json")[0]
    disclosure = load(f"{base}/disclosure_profiles.json")[0]
    proposals = load(f"{base}/proposals.json")
    votes = load(f"{base}/votes.json")
    packets = load(f"{base}/proposal_vote_evidence_packets.json")
    detail = (WEB / "app/assemblies/[slug]/page.tsx").read_text(encoding="utf-8")

    assert assembly["name"] == "横浜市会"
    assert assembly["seat_count"] == 86
    assert len(proposals) == 72
    assert len(votes) == 63
    assert sum(vote["member_vote_availability"] == "published" for vote in votes) == 36
    assert sum(vote["member_vote_availability"] == "not_published" for vote in votes) == 27

    # 24 settlement records plus 3 profit-disposition decisions = 27 pending FY2025 closing items.
    pending_closing_items = [
        proposal for proposal in proposals
        if proposal["outcome"] == "pending" and
        ("決算" in proposal["title"] or "利益の処分" in proposal["title"])
    ]
    assert len(pending_closing_items) == 27
    assert all(proposal["decided_at"] is None for proposal in pending_closing_items)

    items = {item["item"]: item for item in disclosure["items"]}
    assert items["member_votes"]["availability"] == "published"
    assert "委員会報告への賛否" in items["member_votes"]["note"]
    assert items["political_activity_expense_receipts"]["availability"] == "restricted"
    assert "市会図書室での閲覧のみ" in items["political_activity_expense_receipts"]["note"]

    evidence_text = json.dumps(packets, ensure_ascii=False)
    assert "委員会報告への賛否" in evidence_text
    assert "採択への賛否" in evidence_text
    assert "第4回定例会" in evidence_text
    assert "表決はまだ行われていない" in evidence_text
    assert "継続審査中" in detail
    assert "横浜市会の議員個人別賛否" in detail
    assert "請願の賛否" in detail
    assert "決算関係27件" in detail
    assert "市会図書室での閲覧のみ" in detail


def test_kawasaki_assembly_display_facts_match_reviewed_records_and_caveats():
    base = "reviewed/kawasaki-city/assembly"
    assembly = load(f"{base}/assembly_records.json")[0]
    disclosure = load(f"{base}/disclosure_profiles.json")[0]
    proposals = load(f"{base}/proposals.json")
    votes = load(f"{base}/votes.json")
    expenses = load(f"{base}/political_activity_expenses.json")
    detail = (WEB / "app/assemblies/[slug]/page.tsx").read_text(encoding="utf-8")

    assert assembly["name"] == "川崎市議会"
    assert assembly["seat_count"] == 60
    assert len(proposals) == 69
    assert len(votes) == 64
    assert len(expenses) == 0

    individual_names = {
        member["member_name"]
        for vote in votes
        for member in vote["member_votes"]
    }
    assert len(individual_names) == 5
    assert all(len(vote["member_votes"]) == 5 for vote in votes)
    assert all(vote["member_vote_availability"] == "published" for vote in votes)

    items = {item["item"]: item for item in disclosure["items"]}
    assert items["member_votes"]["availability"] == "published"
    assert "無所属議員5名" in items["member_votes"]["note"]
    assert items["political_activity_expense_reports"]["availability"] == "not_published"
    assert items["political_activity_expense_receipts"]["availability"] == "not_published"
    assert "Web公表はない" in items["political_activity_expense_reports"]["note"]
    assert items["petition_results"]["availability"] == "published"
    assert "本会議での表決は行われない" in items["petition_results"]["note"]
    assert "無所属議員5名" in detail
    assert "議会局での閲覧制度のみ" in detail
    assert "陳情は委員会で審査され、本会議での表決対象ではありません" in detail


def test_three_new_assemblies_are_registered_and_discovery_gates_are_reviewed():
    registry = (WEB / "lib/assemblyRegistry.ts").read_text(encoding="utf-8")
    discovery = (WEB / "lib/municipalityDiscovery.ts").read_text(encoding="utf-8")
    overview = (WEB / "app/assemblies/page.tsx").read_text(encoding="utf-8")
    detail = (WEB / "app/assemblies/[slug]/page.tsx").read_text(encoding="utf-8")

    assert 'export type AssemblySlug =' in registry
    for slug in ("kanagawa-prefecture", "yokohama-city", "kawasaki-city"):
        assert f'"{slug}": registry(' in registry
        assert f'"{slug}"' in registry[registry.index("export const assemblySlugs"):]

    assert registry.count('import kanagawa') >= 13
    assert registry.count('import yokohama') >= 13
    assert registry.count('import kawasaki') >= 13
    assert '"kanagawa-prefecture", "yokohama-city", "kawasaki-city"' in registry
    assert "15議会" in overview
    assert 'assemblies["kanagawa-prefecture"]' in discovery
    assert 'assemblies["yokohama-city"]' in discovery
    assert 'assemblies["kawasaki-city"]' in discovery
    assert "hasAssembly" in discovery
    assert "kanagawaFinance.records" in discovery
    assert "hasReviewedExecutivePromises(kanagawaMunicipality.id)" in discovery
    for slug in ("kanagawa-prefecture", "yokohama-city", "kawasaki-city"):
        assert f'slug==="{slug}"' in detail


def test_kanagawa_page_and_registry_are_not_using_foreign_prefecture_copy():
    page = (WEB / "app/municipalities/kanagawa-prefecture/page.tsx").read_text(encoding="utf-8")
    finance = (WEB / "lib/kanagawaFinance.ts").read_text(encoding="utf-8")
    overview = (WEB / "app/assemblies/page.tsx").read_text(encoding="utf-8")

    assert "新かながわグランドデザイン" in page
    assert "神奈川県" in page
    assert "kanagawa-prefecture" in page
    assert "kanagawa-prefecture" in finance
    assert "神奈川3議会" in overview
    for wrong_prefecture in ("副首都ビジョン", "府政運営の基本方針", "吉村洋文", "北海道総合計画", "鈴木直道"):
        assert wrong_prefecture not in page
