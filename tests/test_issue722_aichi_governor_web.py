"""Issue #722: Aichi governor's bulletin promises are rendered on both Web routes."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "apps/web"
DATA = ROOT / "data"
REGISTRY = (WEB / "app/promises/page.tsx").read_text(encoding="utf-8")
AICHI = (WEB / "app/municipalities/aichi-prefecture/page.tsx").read_text(
    encoding="utf-8"
)
EXPORT = (ROOT / "scripts/validate_static_export.py").read_text(
    encoding="utf-8"
)
EXE = (WEB / "lib/executives.ts").read_text(encoding="utf-8")


def test_bulletin_provenance_and_exact_ten_reviewed_promises():
    terms = json.loads(
        (DATA / "entities/executives/executive_terms.json").read_text(encoding="utf-8")
    )
    promises = json.loads(
        (DATA / "entities/executives/promises.json").read_text(encoding="utf-8")
    )
    source_id = "aichi-pref-governor-election-2023-bulletin"
    governor = next(
        term for term in terms if term["municipality_id"] == "jp-local-230006"
    )
    matches = [
        p for p in promises if p["executive_term_id"] == governor["id"]
    ]
    assert governor["manifesto_source_ids"] == [source_id]
    assert len(matches) == 10
    assert all(
        p["review_status"] == "reviewed"
        and p["confidence"] == "high"
        and p["sources"] == [source_id]
        for p in matches
    )
    assert all(
        p["progress_state"] in ("in_progress", "not_assessable") for p in matches
    )


def test_promises_index_keeps_fukuoka_rendering_and_shows_aichi_evidence():
    assert '["fukuoka-prefecture",fukuokaPrefectureProjectData.projects]' in REGISTRY
    assert '["fukuoka-city",fukuokaCityProjectData.projects]' in REGISTRY
    assert '["kitakyushu-city",kitakyushuProjectData.projects]' in REGISTRY
    assert '["aichi-prefecture",aichiProjects as ProjectRecord[]]' in REGISTRY
    assert 'promisesForExecutive(term).filter(p=>p.review_status==="reviewed")' in REGISTRY
    assert "evidenceForPromise(p)" in REGISTRY
    assert "p.original_text" in REGISTRY
    assert "promiseSourceDetails(p.sources)" in REGISTRY
    assert 'municipality.key==="aichi-prefecture"' in REGISTRY
    assert "low / inferred" in REGISTRY
    assert "関連事業の詳細ページは Web 登録後に公開" in REGISTRY


def test_aichi_detail_has_bulletin_source_and_original_text_cards():
    assert "manifestoSourcesForExecutive(governor)" in AICHI
    assert "governorPromises.map((promise)" in AICHI
    assert "promise.original_text" in AICHI
    assert "promise.plain_summary" in AICHI
    assert "evidenceForPromise(promise)" in AICHI
    assert "promiseSourceDetails(promise.sources)" in AICHI
    assert 'id="governor-promises"' in AICHI
    assert 'href="/promises#aichi-prefecture"' in AICHI
    assert "公約原文：選挙公報" in AICHI
    assert "県議会の個別レコードが未登録" in AICHI
    assert "Reviewed 公約、重点事業、県議会の個別レコードが未登録" not in AICHI
    assert "公約登録は未実施" not in AICHI
    assert "公約の達成判定に必要" not in AICHI or "公式評価材料" in AICHI


def test_static_export_keeps_strict_aichi_promise_requirements():
    assert '"promises/index.html": [' in EXPORT
    for required in (
        '"公約原文：選挙公報"',
        '"Reviewed 10件"',
        '"ジブリパークの魅力発信"',
        '"大村秀章知事の公約原文（選挙公報）"',
        '"公式選挙公報"',
    ):
        assert required in EXPORT
    assert '"公約原文：未登録"' not in EXPORT
    assert 'municipalities/aichi-prefecture/index.html' in EXPORT
    assert "export function promisesForExecutive(term:" in EXE
