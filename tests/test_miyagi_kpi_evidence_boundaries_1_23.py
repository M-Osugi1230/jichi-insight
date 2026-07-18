import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
EVIDENCE = [
    POLICY / "miyagi_kpi_pillar1_evidence_packets.json",
    POLICY / "miyagi_kpi_measure1_evidence_packets.json",
    POLICY / "miyagi_kpi_measure2_evidence_packets.json",
    POLICY / "miyagi_kpi_measure3a_evidence_packets.json",
    POLICY / "miyagi_kpi_measure3b_evidence_packets.json",
]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def series_note(packet):
    return next(
        claim["review_note"]
        for claim in packet["claims"]
        if claim["field"] == "series"
    )


def test_evidence_preserves_special_value_boundaries():
    packets = {
        packet["subject_id"]: packet
        for path in EVIDENCE
        for packet in load(path)
    }
    assert "負値" in series_note(packets["policy-target-miyagi-1"])

    for number in range(4, 24):
        assert "0へ変換しない" in series_note(
            packets[f"policy-target-miyagi-{number}"]
        )

    for number in [4, 5, 7, 9, 23]:
        assert "累計値" in series_note(
            packets[f"policy-target-miyagi-{number}"]
        )

    for number in [17, 18, 20, 21]:
        assert "現況値より低い" in series_note(
            packets[f"policy-target-miyagi-{number}"]
        )
