import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def validate(schema_path, value):
    validator = Draft202012Validator(
        load(schema_path),
        format_checker=FormatChecker(),
    )
    return list(validator.iter_errors(value))


def test_manifesto_review_matches_contract_and_preserves_zero_records():
    reviews = load("data/entities/executives/manifesto_reviews.json")
    assert len(reviews) == 3
    bulletin = next(
        review
        for review in reviews
        if review["source_id"] == "kitakyushu-mayor-election-2023-bulletin"
    )
    assert validate("schemas/manifesto_review.schema.json", bulletin) == []
    assert bulletin["segmentation_status"] == "manual_review_required"
    assert bulletin["statement_boundary"] == "mixed"
    assert bulletin["promise_records_created"] == 0


def test_candidate_manifesto_review_is_segmented_into_34_records():
    reviews = load("data/entities/executives/manifesto_reviews.json")
    review = next(
        review
        for review in reviews
        if review["id"] == "manifesto-review-jp-local-401005-2023-v13"
    )
    assert validate("schemas/manifesto_review.schema.json", review) == []
    assert review["source_id"] == (
        "kitakyushu-mayor-candidate-2023-manifesto-v13-archive"
    )
    assert review["review_scope"] == "document"
    assert review["statement_boundary"] == "clear"
    assert review["segmentation_status"] == "segmented"
    assert review["promise_records_created"] == 34
    # The version caveat travels with the review: v13 is not the final
    # version by assertion, and the V15 diff is unverified.
    assert "V15" in review["review_note"]
    assert "最終版とは扱わない" in review["review_note"]


def test_manifesto_review_has_evidence_and_known_references():
    reviews = load("data/entities/executives/manifesto_reviews.json")
    packets = load(
        "data/entities/executives/manifesto_review_evidence_packets.json"
    )
    terms = load("data/entities/executives/executive_terms.json")
    sources = load("data/catalog/executive_sources.json")["records"]

    assert {packet["subject_id"] for packet in packets} == {
        review["id"] for review in reviews
    }
    assert {review["executive_term_id"] for review in reviews} <= {
        term["id"] for term in terms
    }
    assert {review["source_id"] for review in reviews} <= {
        source["id"] for source in sources
    }
    for packet in packets:
        assert validate("schemas/evidence_packet.schema.json", packet) == []
        assert packet["open_questions"]
