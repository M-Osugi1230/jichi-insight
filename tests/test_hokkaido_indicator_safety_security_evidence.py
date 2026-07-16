import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
EVIDENCE = POLICY / "hokkaido_indicator_safety_security_evidence_packets.json"
CATALOG = POLICY / "hokkaido_indicator_catalog_safety_security.json"
SCHEMA = ROOT / "schemas/evidence_packet.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_evidence_schema_coverage_and_pages():
    packets = load(EVIDENCE)
    items = {item["id"]: item for item in load(CATALOG)["items"]}
    validator = Draft202012Validator(load(SCHEMA))
    assert len(packets) == 6
    assert all(list(validator.iter_errors(packet)) == [] for packet in packets)
    assert {packet["subject_id"] for packet in packets} == set(items)
    for packet in packets:
        item = items[packet["subject_id"]]
        assert packet["open_questions"] == []
        assert packet["review_status"] == "reviewed"
        assert len(packet["claims"]) == 2
        for claim in packet["claims"]:
            assert claim["source_ids"] == [
                "policy-source-hokkaido-indicators-safety-security"
            ]
            assert f"PDFページ{item['source_page']}" in claim["location_note"]
            assert claim["decision"] == "accepted"


def test_evidence_preserves_quality_boundaries():
    packets = {packet["subject_id"]: packet for packet in load(EVIDENCE)}
    notes = {}
    for number in range(74, 80):
        packet = packets[f"policy-indicator-hokkaido-{number}"]
        series_claim = next(
            claim for claim in packet["claims"] if claim["field"] == "series"
        )
        notes[number] = series_claim["review_note"]
    assert "複合条件" in notes[74] and "固定数値へ変換しない" in notes[74]
    assert "複合条件" in notes[75] and "固定数値へ変換しない" in notes[75]
    assert "29歳以下・65歳以上" in notes[76]
    assert "算出要素" in notes[77]
    assert "指標68" in notes[78]
    assert "区域・指定医療機関別" in notes[79]
