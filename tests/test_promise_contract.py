import copy
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def validate(value):
    validator = Draft202012Validator(
        load("schemas/promise.schema.json"),
        format_checker=FormatChecker(),
    )
    return list(validator.iter_errors(value))


def test_example_matches_updated_contract():
    example = load("data/examples/promise.example.json")
    assert validate(example) == []
    assert example["statement_type"] == "specific_commitment"
    assert example["assessability"] == "assessable"


def test_catalog_source_id_is_supported():
    example = copy.deepcopy(load("data/examples/promise.example.json"))
    example["sources"] = ["kitakyushu-mayor-election-2023-bulletin"]
    assert validate(example) == []


def test_vision_requires_not_assessable_state():
    example = copy.deepcopy(load("data/examples/promise.example.json"))
    example["statement_type"] = "vision"
    assert validate(example)
    example["assessability"] = "not_assessable"
    example["progress_state"] = "not_assessable"
    assert validate(example) == []


def test_not_assessable_cannot_be_not_started():
    example = copy.deepcopy(load("data/examples/promise.example.json"))
    example["statement_type"] = "directional_commitment"
    example["assessability"] = "not_assessable"
    example["progress_state"] = "not_started"
    assert validate(example)
