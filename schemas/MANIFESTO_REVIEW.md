# Manifesto review contract

`manifesto_review.schema.json` は、選挙公報や候補者マニフェストから個別公約を作る前の、人手レビュー判断を記録します。

## Why this entity exists

資料が存在しても、候補者欄が政策方向、経歴、理念、決意を連続した文章で記載している場合、句読点だけで複数公約へ分割すると原文にない境界を作る危険があります。

このエンティティは、個別公約を作った件数だけでなく、作らなかった理由も監査可能にします。

## Required relationships

```text
ExecutiveTerm
  └─ ManifestoReview
       ├─ Source
       └─ EvidencePacket
```

- `executive_term_id`: 対象の首長任期
- `source_id`: レビュー対象の公式公約資料
- `source_location`: ページ、候補者欄、見出し等の確認位置
- `statement_boundary`: 原文上の境界が明確か
- `segmentation_status`: 分割済み、手動レビュー待ち、未分割
- `promise_records_created`: 実際に作成した公約レコード数
- `reason_codes`: 分割判断の理由

## Safety invariant

`manual_review_required` または `not_segmented` の場合、`promise_records_created` は必ず0です。

公約資料が登録されただけで、個別公約や進捗評価が作成されたとは扱いません。

## Registry fixture

`data/examples/manifesto_review.example.json` は架空自治体・架空候補者を使い、標準Registryで自動検証されます。
