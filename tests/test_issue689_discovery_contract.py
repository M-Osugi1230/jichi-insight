"""Issue #689: search is optional enhancement over Reviewed-only server markup."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "apps/web"
PROJECTS = WEB / "app/projects/page.tsx"
ASSEMBLIES = WEB / "app/assemblies/[slug]/page.tsx"
FILTER = WEB / "components/ProgressiveRecordFilter.tsx"

PROJECT_DATA = [
    ROOT / "data/reviewed/fukuoka-prefecture/projects.json",
    ROOT / "data/reviewed/fukuoka-city/projects.json",
    ROOT / "data/reviewed/kitakyushu-city/projects.json",
]


def test_registered_reviewed_projects_remain_complete_and_searchable():
    records = [
        record
        for path in PROJECT_DATA
        for record in json.loads(path.read_text(encoding="utf-8"))
        if record["review_status"] == "reviewed"
    ]
    assert len(records) == 30
    assert any(
        "子育て" in record["official_title"]
        or "子育て" in record["plain_title"]
        or record["policy_area"] == "childcare"
        for record in records
    )
    page = PROJECTS.read_text(encoding="utf-8")
    assert 'project.review_status === "reviewed"' in page
    assert "project.official_title" in page
    assert "project.plain_title" in page
    assert "project.policy_area" in page
    assert 'childcare: "子育て"' in page
    assert "data-filter-entry" in page
    assert "data-filter-group={project.policy_area}" in page
    assert "projectSourceCatalog.find" in page
    assert "stageLabels[record.kind]" in page


def test_assembly_search_does_not_change_vote_disclosure_logic():
    page = ASSEMBLIES.read_text(encoding="utf-8")
    assert "data-filter-group={session.id}" in page
    assert "${proposal.proposal_number} ${proposal.title}" in page
    assert "data-filter-section" in page
    assert "議員ごとの賛否は公表されていません" in page
    assert 'votingInfo?.availability==="not_published"' in page
    assert 'vote.totals===null' in page
    assert "data.disclosure.as_of" in page
    assert "<Sources ids={proposal.sources}" in page


def test_filter_works_without_hiding_initial_server_rendered_records():
    widget = FILTER.read_text(encoding="utf-8")
    assert '"use client"' in widget
    assert "onChange" in widget
    assert 'entry.hidden = !match' in widget
    assert 'apply("", "")' in widget
    assert 'setQuery("");' in widget
    assert 'setSelected("");' in widget
    assert "該当する収録事業がありません" in widget
    assert "該当する収録議案がありません" in widget
    assert "role=\"status\"" in widget
    assert "{children}" in widget
