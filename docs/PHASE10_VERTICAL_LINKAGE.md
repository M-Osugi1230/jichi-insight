# Phase 10 — Nationwide uniform depth

Status: `complete`（2026-08-01）

Phase 10は、Phase 9で整備した全47都道府県のEvidence-backed Reviewed政策目標を、実行・財政・説明責任の公式資料へ同じ最低粒度で接続する工程です。

```text
Reviewed target statement
→ annual actual
→ budget
→ settlement
→ priority project
→ contract / procurement review
→ assembly review
→ audit
→ executive manifesto review
→ publication verification
```

Phase 10は独自の政策スコアを作りません。値の増加、予算の存在、事業の実施だけでは、政策が成功した証拠にはなりません。

## Completion statement

2026年8月1日、47都道府県すべてが宣言した11項目の共通ゲートへ到達しました。

- 政策・KPI Reviewed: 47 / 47
- Evidence Packet Reviewed: 47 / 47
- 年度実績 文書スコープLinked: 47 / 47
- 予算 文書スコープLinked: 47 / 47
- 決算 文書スコープLinked: 47 / 47
- 重点事業 文書スコープLinked: 47 / 47
- 監査 文書スコープLinked: 47 / 47
- 契約 Reviewed coverage: 47 / 47
- 議会 Reviewed coverage: 47 / 47
- 首長公約 Reviewed coverage: 47 / 47
- 公開検証 Reviewed: 47 / 47
- 共通ゲート完了: 47 / 47
- 政策達成評価: 0件
- 比較可能性未確認の全国ランキング: 0件

## Completion boundary

Phase 10の完了は**全国の文書スコープ**です。

文書スコープLinkedは、公式資料について次を確認した状態です。

- 対象都道府県
- 資料の役割
- 計画版または会計年度
- 報告・測定期間
- 公開主体
- 支持できる主張
- 未解決の個票接続範囲

次の普遍的な一対一接続を完了したとは主張しません。

- 全政策目標と全実績系列
- 全予算科目と全決算科目
- 全事業と全契約
- 全議会発言・議案・採決
- 全監査指摘・是正措置
- 全首長公約と行政計画

個票接続は北海道、宮城県、東京都、福岡県でより深く進んでおり、他県への展開はPhase 10後の深掘り工程です。

## Accountability coverage

契約、議会、首長公約は、47都道府県×3役割＝141件をレビューしました。

- 安定した都道府県公式一次資料入口: 3件
- 現任期の確認待ち: 1件
- 安定した一次資料を特定できなかった公式ホスト検索結果: 137件
- 不存在の断定: 0件
- 公約達成評価: 0件

`no_stable_primary_source_found`は「存在しない」という意味ではありません。確認した都道府県公式ホスト、検索条件、検索日、HTTP・役割チェック、再確認条件を記録したレビュー結果です。

首長選挙資料は、選挙日、候補者、現職知事、現任期が一致するまで公約レコードへ昇格しません。

## Canonical machine-readable state

- `data/catalog/phase10_uniformity.json`
- `data/catalog/phase10_execution_queue.json`
- `data/catalog/phase10_completion.json`
- `data/catalog/phase10_nationwide_core_linkage.json`
- `data/catalog/phase10_nationwide_accountability_linkage.json`
- `data/catalog/phase10_regional_depth_index.json`
- `data/catalog/phase10_reference_depth_reviews.json`
- `data/catalog/phase10_anchor_depth_reviews.json`
- `data/catalog/phase10_tohoku_depth_reviews.json`
- `data/catalog/phase10_kanto_depth_reviews.json`
- `data/catalog/phase10_chubu_depth_reviews.json`
- `data/catalog/phase10_kinki_depth_reviews.json`
- `data/catalog/phase10_chugoku_depth_reviews.json`
- `data/catalog/phase10_shikoku_depth_reviews.json`
- `data/catalog/phase10_kyushu_depth_reviews.json`
- `schemas/phase10_uniformity.schema.json`
- `schemas/phase10_nationwide_core_linkage.schema.json`
- `schemas/phase10_nationwide_accountability_linkage.schema.json`

## Uniform dimensions

| Dimension | Phase 10 completion requirement |
| --- | --- |
| Policy targets and KPI | `reviewed` or better |
| Evidence Packet | `reviewed` or better |
| Annual actuals | `linked` at document scope |
| Budget | `linked` at document scope |
| Settlement | `linked` at document scope |
| Priority projects | `linked` at document scope |
| Contracts and procurement | `reviewed` official source or reviewed official-host search outcome |
| Assembly explanation | `reviewed` official source or reviewed official-host search outcome |
| Audit | `linked` at document scope |
| Executive manifesto | `reviewed`; current-term verification required before promise records |
| Publication verification | `reviewed` or better |

## Status vocabulary

- `not_indexed`: 公式入口を台帳へ固定していない
- `indexed`: 公式資料入口を確認した
- `reviewed`: 内容、期間、範囲、Evidence位置を確認した
- `linked`: 宣言したスコープで定義、役割、期間を照合して接続した
- `source_reviewed`: 安定した都道府県公式資料入口をレビューした
- `search_reviewed`: 公式ホストの検索結果と未特定境界をレビューした

資料の状態と個票の接続状態は分離します。文書がLinkedでも、文書内の全行が一対一接続済みとは限りません。

## Core five-layer linkage

年度実績、予算、決算、重点事業、監査は、既存のReviewed地域台帳を正本として47都道府県へ展開しました。

各リンクは、元台帳の都道府県コードと資料役割を参照し、同じ内容を複製しません。これにより、公式資料の差し替えや期間更新が一つの正本へ集約されます。

より深い個票接続のEvidence:

- 北海道: 108指標の年度実績接続
- 宮城県: KPI年度実績、627予算事業、政策・施策接続
- 東京都: 子供分野8目標の年度実績照合
- 福岡県: 118目標の年度実績照合、266重点事業候補

定義、単位、期間、計画版が異なるものはPartialまたは未接続として維持します。

## Data rules

1. 報告年度と測定年度を分ける。
2. 現行計画と旧計画を分ける。
3. 予算、補正予算、支出、決算、事業費、契約額を同一視しない。
4. 事業名一致だけで接続せず、担当組織、期間、範囲、識別子を確認する。
5. 議会質問と監査指摘は説明・監督のEvidenceであり、成功・失敗の自動証明ではない。
6. 首長公約は自治体、候補者、任期、原文、政策範囲を確認できる場合だけ個票化する。
7. 公開する値と関係にEvidenceを要求する。
8. 未確認の関係は推測で接続しない。
9. 比較可能性が確認されるまで全国ランキングを作らない。
10. `not_indexed`や検索未特定を「存在しない」に読み替えない。

## Verified exit gates

Phase 10は次を検証して完了しました。

- 全47都道府県が11項目の宣言深度へ到達
- 全47都道府県の文書スコープ接続元を公式資料台帳で確認
- 計画版、報告年度、測定年度、会計区分を分離
- 予算、決算、事業費、契約額を分離
- 議会、監査、公約の主体・任期・役割を未確認のまま昇格しない
- 未確認関係と検索未特定を明示
- 公開Phase 10マトリクスと機械可読台帳を一致
- JSON Schema検証
- 全回帰テスト
- Python・Web lint
- TypeScript型検査
- Next.js本番ビルド
- 静的出力検証
- Publication Audit
- Production Smoke
- `data/catalog/phase10_completion.json`が`complete`
- 6完了ゲートがすべて`passed`

## Post-Phase 10 record-level deepening

1. 文書スコープから個票スコープへの一対一接続を全国へ展開する。
2. 政策・施策・事業・予算科目・契約・議会・監査の安定IDを拡張する。
3. 現任期の首長公約を候補者・任期・原文単位で確認する。
4. 公式サイト移転、新年度資料、計画改定を継続再探索する。
5. 比較可能性が確認された指標だけを比較機能へ接続する。

この深掘りはPhase 10の完了状態を覆すものではなく、完了した全国文書スコープの上に個票精度を積み上げる工程です。
