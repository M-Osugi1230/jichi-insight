import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def catalogs():
    records = [load(path) for path in POLICY.glob("miyagi_kpi_catalog_*.json")]
    return sorted(records, key=lambda record: record["target_group_start"])


def evidence_packets():
    paths = [
        *POLICY.glob("miyagi_kpi_measure*_evidence_packets.json"),
        *POLICY.glob("miyagi_kpi_pillar*_evidence_packets.json"),
    ]
    return [packet for path in paths for packet in load(path)]


def test_all_groups_series_and_evidence_are_contiguous():
    groups = [group for catalog in catalogs() for group in catalog["items"]]
    series = [item for group in groups for item in group["series"]]
    packets = evidence_packets()
    assert [group["target_group_number"] for group in groups] == list(range(1, 129))
    assert [item["series_number"] for item in series] == list(range(1, 150))
    assert len({group["id"] for group in groups}) == 128
    assert len({item["id"] for item in series}) == 149
    assert len(packets) == 128
    assert len({packet["id"] for packet in packets}) == 128
    assert {packet["subject_id"] for packet in packets} == {
        group["id"] for group in groups
    }
