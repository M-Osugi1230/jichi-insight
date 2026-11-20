"""Issue #805: Kanagawa stage-three mayor promises and term Web integration."""

import json
import runpy
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
WEB = ROOT / "apps/web"
EXECUTIVES = (WEB / "lib/executives.ts").read_text(encoding="utf-8")
CATALOG = (WEB / "lib/catalog.ts").read_text(encoding="utf-8")
QUALITY = (WEB / "lib/dataQuality.ts").read_text(encoding="utf-8")
DISCOVERY = (WEB / "lib/municipalityDiscovery.ts").read_text(encoding="utf-8")
PROMISES_PAGE = (WEB / "app/promises/page.tsx").read_text(encoding="utf-8")
EXECUTIVES_PAGE = (WEB / "app/executives/page.tsx").read_text(encoding="utf-8")
EXPORT = (ROOT / "scripts/validate_static_export.py").read_text(encoding="utf-8")


def load(relative):
    return json.loads((DATA / relative).read_text(encoding="utf-8"))


def test_yokohama_and_kawasaki_current_mayor_terms_and_promises_are_registered():
    terms = load("entities/executives/executive_terms.json")
    promises = load("entities/executives/promises.json")
    expected = (
        ("141003", "yokohama-city", "原澤 敦美", "2026-10-18", "2030-10-17", 12),
        ("141305", "kawasaki-city", "福田 紀彦", "2025-11-19", "2029-11-18", 13),
    )
    for code, _slug, name, start, end, count in expected:
        municipality_id = f"jp-local-{code}"
        matching_terms = [term for term in terms if term["municipality_id"] == municipality_id]
        assert len(matching_terms) == 1
        term = matching_terms[0]
        assert term["person_name"] == name
        assert term["status"] == "current"
        assert term["review_status"] == "reviewed"
        assert term["term_start"] == start
        assert term["term_end"] == end
        assert term["election_date"] is not None
        reviewed = [
            promise for promise in promises
            if promise["municipality_id"] == municipality_id
            and promise["executive_term_id"] == term["id"]
            and promise["review_status"] == "reviewed"
        ]
        assert len(reviewed) == count
        assert all(promise["original_text"] for promise in reviewed)


def test_yokohama_vacancy_election_start_basis_is_data_backed_and_succinct():
    terms = load("entities/executives/executive_terms.json")
    packets = load("entities/executives/evidence_packets.json")
    term = next(item for item in terms if item["municipality_id"] == "jp-local-141003")
    packet = next(item for item in packets if item["subject_id"] == term["id"])
    claim = next(item for item in packet["claims"] if item["field"] == "term_start")
    assert "欠員選挙" in claim["statement"]
    assert "欠員選挙" in claim["review_note"]
    assert "欠員選挙による選挙日起算" in EXECUTIVES_PAGE
    assert "欠員選挙による選挙日起算" in PROMISES_PAGE
    # The detailed claim contains predecessor history; the UI must not render it.
    assert "山中竹春" not in EXECUTIVES_PAGE
    assert "山中竹春" not in PROMISES_PAGE
    assert "辞職" not in EXECUTIVES_PAGE
    assert "辞職" not in PROMISES_PAGE


def test_executives_and_promises_pages_show_term_end_and_both_city_promises():
    assert "formatDateJa(term.term_end)" in EXECUTIVES_PAGE
    assert "任期満了" in EXECUTIVES_PAGE
    assert "formatDateJa(term.term_end)" in PROMISES_PAGE
    assert "任期満了" in PROMISES_PAGE
    assert "evidenceForExecutive(term)" in EXECUTIVES_PAGE
    assert "evidenceForExecutive(term)" in PROMISES_PAGE
    assert "promisesForExecutive(term)" in PROMISES_PAGE
    assert "promisesForExecutive(term)" in EXECUTIVES_PAGE
    assert "Reviewed 公約原文 12件" not in PROMISES_PAGE
    assert "Reviewed 公約原文 13件" not in PROMISES_PAGE


def test_existing_web_registry_and_quality_metadata_cover_both_municipalities():
    assert '"jp-local-141003": "yokohama-city"' in EXECUTIVES
    assert '"jp-local-141305": "kawasaki-city"' in EXECUTIVES
    assert '"yokohama-city": {' in CATALOG
    assert '"kawasaki-city": {' in CATALOG
    assert '"yokohama-city":' in QUALITY
    assert '"kawasaki-city":' in QUALITY


def test_yokohama_and_kawasaki_promise_discovery_gates_are_reviewed_record_scoped():
    # After the stage-two merge (PR #800), the gates use the Reviewed
    # municipality records instead of literal codes, and the promises gate
    # is combined with the projects gate for both cities.
    assert "officialCode === yokohamaMunicipality.official_code" in DISCOVERY
    assert "hasReviewedExecutivePromises(yokohamaMunicipality.id)" in DISCOVERY
    assert 'key: "yokohama-city", finance: false, promises: hasPromises' in DISCOVERY
    assert "officialCode === kawasakiMunicipality.official_code" in DISCOVERY
    assert "hasReviewedExecutivePromises(kawasakiMunicipality.id)" in DISCOVERY
    assert 'key: "kawasaki-city", finance: false, promises: hasPromises' in DISCOVERY
    assert 'term.municipality_id === municipalityId' in DISCOVERY
    assert 'promise.municipality_id === municipalityId' in DISCOVERY
    assert 'promise.executive_term_id === term.id' in DISCOVERY


def test_municipality_specific_promise_validators_are_registered():
    assert "def validate_yokohama_promise_scope()" in EXPORT
    assert "def validate_kawasaki_promise_scope()" in EXPORT
    assert "failures.extend(validate_yokohama_promise_scope())" in EXPORT
    assert "failures.extend(validate_kawasaki_promise_scope())" in EXPORT
    assert '"Reviewed 公約原文 12件"' in EXPORT
    assert '"Reviewed 公約原文 13件"' in EXPORT
    unregistered_copy = "公約原文：" + "未登録"
    assert unregistered_copy not in EXPORT


def test_unregistered_copy_validation_is_scoped_to_its_own_municipality(tmp_path):
    validator = runpy.run_path(str(ROOT / "scripts/validate_static_export.py"))
    check_yokohama = validator["validate_yokohama_promise_scope"]
    check_kawasaki = validator["validate_kawasaki_promise_scope"]
    check_asahikawa = validator["validate_asahikawa_promise_scope"]
    output = tmp_path / "promises" / "index.html"
    output.parent.mkdir(parents=True)

    unregistered_copy = "公約原文：" + "未登録"
    sections = (
        '<section id="yokohama-city"><h2>横浜市・原澤 敦美</h2>'
        '<p>Reviewed 公約原文 12件</p></section>',
        '<section id="kawasaki-city"><h2>川崎市・福田 紀彦</h2>'
        '<p>Reviewed 公約原文 13件</p></section>',
        f'<section id="asahikawa-city"><h2>旭川市・今津 寛介</h2>'
        f'<p>{unregistered_copy}</p></section>',
    )
    with patch.dict(check_yokohama.__globals__, {"EXPORT_ROOT": tmp_path}):
        output.write_text("".join(sections), encoding="utf-8")
        assert check_yokohama() == []
        assert check_kawasaki() == []
        assert check_asahikawa() == []

        # Moving the unregistered copy to a different municipality must not
        # satisfy or invalidate either mayor's reviewed-promise section.
        wrong_scope = (
            sections[0].replace("Reviewed 公約原文 12件", unregistered_copy),
            sections[1],
            sections[2].replace(unregistered_copy, "Reviewed 公約原文 1件"),
        )
        output.write_text("".join(wrong_scope), encoding="utf-8")
        assert check_yokohama()
        assert check_kawasaki() == []
        assert check_asahikawa()
