"""Issue #728: reviewed Aichi cluster councils and careful vote disclosure."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "apps/web"
DATA = ROOT / "data"
REGISTRY = (WEB / "lib/assemblyRegistry.ts").read_text(encoding="utf-8")
INDEX = (WEB / "app/assemblies/page.tsx").read_text(encoding="utf-8")
DETAIL = (WEB / "app/assemblies/[slug]/page.tsx").read_text(encoding="utf-8")
DISCOVERY = (WEB / "lib/municipalityDiscovery.ts").read_text(encoding="utf-8")
AICHI = (WEB / "app/municipalities/aichi-prefecture/page.tsx").read_text(
    encoding="utf-8"
)
EXPORT = (ROOT / "scripts/validate_static_export.py").read_text(
    encoding="utf-8"
)


def load(relative):
    return json.loads((DATA / relative).read_text(encoding="utf-8"))


def test_all_six_assemblies_have_registered_sources_and_static_routes():
    for city in (
        "fukuoka-prefecture", "fukuoka-city", "kitakyushu-city",
        "aichi-prefecture", "nagoya-city", "toyota-city",
    ):
        assert f'"{city}"' in REGISTRY
        assert f"/assemblies/{city}" not in INDEX or "assemblySlugs" in INDEX
    for city, source_catalog in (
        ("aichi-prefecture", "aichi_assembly_sources.json"),
        ("nagoya-city", "nagoya_assembly_sources.json"),
        ("toyota-city", "toyota_city_assembly_sources.json"),
    ):
        root = f"reviewed/{city}/assembly"
        assert len(load(f"{root}/assembly_records.json")) == 1
        assert len(load(f"{root}/disclosure_profiles.json")) == 1
        assert len(load(f"{root}/sessions.json")) == 1
        assert load(f"catalog/{source_catalog}")["records"]
        assert f'"assemblies/{city}/index.html"' in EXPORT
    assert "assemblySlugs.map" in INDEX
    assert "assemblySlugs.map" in DETAIL
    assert "20議会" in INDEX


def test_aichi_faction_attitudes_are_not_mistaken_for_plenary_ballots():
    assert len(load("reviewed/aichi-prefecture/assembly/proposals.json")) == 58
    assert len(load("reviewed/aichi-prefecture/assembly/faction_votes.json")) == 290
    assert len(load("reviewed/aichi-prefecture/assembly/political_activity_expenses.json")) == 103
    assert "採決に先立って議会運営委員会で確認" in DETAIL
    assert "本会議の投票記録そのものではありません" in DETAIL
    assert "f.for_count" in DETAIL and "f.against_count" in DETAIL
    assert 'id="aichi-assembly"' in AICHI
    assert "県議会の個別レコードが未登録" not in AICHI
    assert "assembly.proposals.length" in AICHI


def test_nagoya_only_no_134_has_individual_votes_and_speaker_is_not_absent():
    proposals = load("reviewed/nagoya-city/assembly/proposals.json")
    votes = load("reviewed/nagoya-city/assembly/votes.json")
    with_members = [vote for vote in votes if vote.get("member_votes")]
    assert len(proposals) == 22
    assert len(with_members) == 1
    assert len(with_members[0]["member_votes"]) == 68
    assert next(p for p in proposals if p["id"] == with_members[0]["proposal_id"])[
        "proposal_number"
    ] == "第134号"
    assert all(
        vote["method"] == "unanimous"
        for vote in votes if vote["id"] != with_members[0]["id"]
    )
    assert "議決に参加できない" in DETAIL
    assert "欠席ではありません" in DETAIL
    assert 'hideOpenQuestions={slug==="nagoya-city"' in DETAIL
    assert 'proposal.proposal_number==="第134号"' in DETAIL


def test_toyota_count_and_in_person_expense_disclosure():
    root = "reviewed/toyota-city/assembly"
    assert len(load(f"{root}/proposals.json")) == 63
    assert len(load(f"{root}/votes.json")) == 59
    assert len(load(f"{root}/faction_votes.json")) == 295
    assert len(load(f"{root}/political_activity_expenses.json")) == 5
    assert len(load(f"{root}/inspection_trips.json")) == 26
    assert "自民クラブは議長を除く・欠席1名" in DETAIL
    assert "会派別集計のみが Web 公表" in DETAIL


def test_discovery_respects_registered_assembly_and_mayor_promises():
    assert 'isAssemblySlug(city.slug)' in DISCOVERY
    assert 'promise.executive_term_id === term.id' in DISCOVERY
    assert "assembly: hasAssembly" in DISCOVERY
    assert 'key: hasAssembly ? "aichi-prefecture" : null' in DISCOVERY
    assert "promises: hasPromises" in DISCOVERY
    assert "projects: false, key: null" in DISCOVERY
    # The registry still drives the original Fukouka three councils.
    assert '"fukuoka-prefecture": registry(' in REGISTRY
    assert '"fukuoka-city": registry(' in REGISTRY
    assert '"kitakyushu-city": registry(' in REGISTRY
