from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_status_labels_cover_review_confidence_and_availability_states():
    labels = read("apps/web/lib/statusLabels.ts")

    for required in (
        "sourceReviewStatusPresentation",
        "sourceConfidenceLabel",
        "sourceAvailabilityPresentation",
        'verified: { label: "検証済み"',
        'reviewed: { label: "レビュー済み"',
        'extracted: { label: "抽出済み（未レビュー）"',
        'inferred: { label: "推定"',
        'missing: { label: "未確認"',
        'not_assessable: "信頼度：評価不能"',
        'not_published: { label: "未公表"',
        'not_found: { label: "資料未発見"',
        'restricted: { label: "公開制限あり"',
        'unknown: { label: "公開状況不明"',
        "statementKindLabels",
        "fiscalStageLabel",
        'settlement: "決算"',
    ):
        assert required in labels


def test_source_card_renders_status_badges_from_record_fields():
    card = read("apps/web/components/SourceCard.tsx")

    for required in (
        "sourceReviewStatusPresentation(source.review_status)",
        "sourceAvailabilityPresentation(source.availability)",
        "sourceConfidenceLabel(source.confidence)",
        "<StatusBadge",
    ):
        assert required in card


def test_source_location_is_the_shared_presentation():
    location = read("apps/web/components/SourceLocation.tsx")
    assert "資料位置" in location

    panel = read("apps/web/components/EvidencePanel.tsx")
    assert "SourceLocation" in panel
    assert "<span>{claim.location_note}</span>" not in panel

    city_page = read("apps/web/app/municipalities/[slug]/page.tsx")
    assert "SourceLocation" in city_page
    assert "資料位置: {source.evidenceLocation}" not in city_page


def test_evidence_panel_stage_comes_from_the_record():
    panel = read("apps/web/components/EvidencePanel.tsx")

    assert "fiscalStageLabel(record.stage)" in panel
    assert "<dd>当初予算</dd>" not in panel


def test_correction_history_entry_is_a_shared_component():
    component = read("apps/web/components/CorrectionHistoryEntry.tsx")
    assert "CorrectionHistoryEntry" in component
    assert "修正前" in component
    assert "修正後" in component

    page = read("apps/web/app/corrections/history/page.tsx")
    assert "<CorrectionHistoryEntry entry={entry}" in page


def test_component_demo_uses_fictional_fixtures_and_stays_unindexed():
    fixtures = read("apps/web/lib/componentFixtures.ts")
    assert "fictional" in fixtures
    assert "example.com" in fixtures
    assert "架空" in fixtures

    page = read("apps/web/app/component-demo/page.tsx")
    for required in (
        "componentFixtures",
        "robots: { index: false, follow: false }",
        "SourceCard",
        "EvidencePanel",
        "CorrectionHistoryEntry",
        "StatusBadge",
    ):
        assert required in page

    sitemap = read("apps/web/app/sitemap.ts")
    assert "component-demo" not in sitemap
