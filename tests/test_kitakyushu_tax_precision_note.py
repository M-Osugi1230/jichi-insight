"""Kitakyushu FY2026 local-tax precision notes match the registered data.

PR #641 refined the FY2026 Kitakyushu local-tax record to the enacted
budget-book value at thousand-yen precision (192,462,010 thousand yen).
Notes that still described the record as oku-yen precision are stale and
must not return, and the comparison tax share must be computed from the
registered amount rather than the rounded budget-proposal figure.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

STALE_NOTES = [
    "公式資料の表示精度：億円",
    "北九州市は公式資料の億円単位の表示精度で収録",
    "市税は億円単位の公式表示を使用",
]

CHECKED_FILES = [
    "apps/web/app/municipalities/kitakyushu-city/page.tsx",
    "apps/web/app/compare/page.tsx",
    "apps/web/lib/financeComparison.ts",
]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_no_stale_oku_precision_note_remains() -> None:
    for relative in CHECKED_FILES:
        text = read(relative)
        for stale in STALE_NOTES:
            assert stale not in text, f"stale precision note in {relative}: {stale}"


def test_kitakyushu_tax_card_shows_exact_yen() -> None:
    page = read("apps/web/app/municipalities/kitakyushu-city/page.tsx")
    assert "{formatExactYen(budgetTax.amount_yen)}" in page


def test_comparison_notes_state_thousand_yen_precision() -> None:
    comparison = read("apps/web/lib/financeComparison.ts")
    compare_page = read("apps/web/app/compare/page.tsx")
    assert "北九州市は予算書の千円単位の表示精度で収録。" in comparison
    assert "市税は予算書の千円単位の公式表示を使用。" in compare_page


def test_tax_share_uses_registered_thousand_yen_amount() -> None:
    records = json.loads(
        (ROOT / "data/reviewed/kitakyushu-city/fiscal_records.json").read_text(encoding="utf-8")
    )
    tax = next(
        record
        for record in records
        if record["fiscal_year"] == 2026
        and record["stage"] == "initial_budget"
        and record["metric"] == "local_tax"
    )
    total = next(
        record
        for record in records
        if record["fiscal_year"] == 2026
        and record["stage"] == "initial_budget"
        and record["metric"] == "total_revenue"
    )
    # Enacted budget-book value at thousand-yen precision, not the rounded
    # 192,500,000,000 yen derived from the proposal-stage oku-yen display.
    assert tax["amount_yen"] == 192_462_010_000
    share = tax["amount_yen"] / total["amount_yen"] * 100
    assert round(share, 1) == 29.7

    comparison = read("apps/web/lib/financeComparison.ts")
    # The share is derived from the registered records, never a literal.
    assert 'kitakyushuBudgetRecord("local_tax").amount_yen' in comparison
    assert "192500000000" not in comparison
    assert "192_500_000_000" not in comparison
