# ADR 0003: Protect the project North Star

- Status: Accepted
- Date: 2026-07-15

## Context

開発が長期化し、機能、対象自治体、評価項目が増えると、当初の課題意識が短期的な要望やランキング機能に埋もれる危険があります。

## Decision

`docs/NORTH_STAR.md`を最上位の判断基準、`docs/PROJECT_MEMORY.md`を着想と重要判断の記録として管理します。

通常の機能PRではNorth Starを変更しません。変更には専用PR、ADR、影響分析、変更理由の公開を必要とします。

## Consequences

- プロジェクトの一貫性を維持しやすい
- 目的に反する機能追加を検知できる
- 方針転換には追加手続が必要になる
