#!/usr/bin/env python3
"""Run Tokyo children linkage with reviewed aliases for multi-column PDF text."""

from __future__ import annotations

import extract_tokyo_children_actual_linkage as base

base.LINKAGE_RULES[2]["alias"] = "自分の行動で社会を変えられる"
base.LINKAGE_RULES[3]["alias"] = "子供が権利の主体であることを知って"
base.LINKAGE_RULES[8]["alias"] = "母子保健部門と児童福祉部門が連携した"


if __name__ == "__main__":
    base.main()
