# ADR 0004: Schema registry and reference-integrity validation

- Status: Accepted
- Date: 2026-07-15

## Context

財政、契約、公約、議会、採決、視察を別々に実装すると、年度、欠損、出典、レビュー状態の意味がずれ、画面側で独自解釈が発生します。

## Decision

すべての主要エンティティをJSON Schemaで定義し、`schemas/registry.json`でスキーマと代表fixtureを登録します。

CIは次を検証します。

- JSON Schema適合
- fixtureが架空例として明確であること
- IDの一意性
- エンティティ間参照
- Source参照
- North Star文書の存在

## Consequences

- データ追加時の初期作業は増える
- pipeline、レビュー、Webが同じ意味を共有できる
- 破壊的変更を検出しやすい
- 実データ投入前にモデル不足を発見できる
