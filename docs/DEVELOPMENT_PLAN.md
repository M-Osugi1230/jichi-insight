# Development plan

## Operating model

開発を6つのワークストリームに分け、依存関係の少ない作業を並列化します。

| Stream | Scope |
|---|---|
| A Product/UX | 情報設計、画面、用語、モバイル |
| B Data foundation | スキーマ、ID、出典、品質 |
| C Collection | 公式資料マップ、差分検知、取得 |
| D Policy research | 重点事業、公約、議会 |
| E Trust | 方法論、編集、法務、訂正 |
| F Platform | CI、テスト、公開、監視 |

## Critical path

```text
Entity definitions
  → source catalog
  → reviewed example records
  → UI components
  → finance/project data
  → manifesto linkage
  → assembly linkage
  → trust review
  → closed beta
  → public beta
```

大量収集は、Entity definitionsとreviewed example recordsが完成してから開始します。

## First 10 implementation epics

1. Foundation and repository controls
2. Source catalog for three pilot municipalities
3. Shared evidence and quality components
4. Municipality profile and fiscal summary
5. Project detail and budget lifecycle
6. KPI and outcome timeline
7. Manifesto registry and project linkage
8. Assembly, proposals, votes, expenses
9. Correction, right of reply, change history
10. Release hardening and public beta

## Sprint structure

1スプリントを「設計→実装→検証→証跡」の単位にします。日数ではなく、完了条件を満たすまで次へ進みません。

### Planning

- 目的
- 利用者価値
- 対象データ
- 非対象
- 受入条件
- リスク
- 必要な一次資料

### Delivery

- 小さなPR
- プレビュー
- 自動テスト
- データレビュー
- モバイル確認
- 方法論影響確認

### Review

- 画面から一次資料へ戻れるか
- 不明値を誤解させないか
- 誰かを不当に有利・不利にしないか
- 同じ処理を次自治体へ再利用できるか

## Efficiency methods

### Schema-first

実データを大量投入する前に3〜5件の代表データでスキーマを固定します。

### Vertical slice

財政だけを全国分集めるのではなく、1自治体について財政→事業→公約→議会まで一本つなぎ、モデルの欠陥を早期発見します。

### Evidence packet

1事業ごとに、資料一覧、抽出値、ページ、判断、未確認点を一つのレビュー単位にします。

### Quality tiers

- Coverage: 団体と資料の存在のみ
- Indexed: 資料とページを特定
- Extracted: 候補値を抽出
- Reviewed: 人が確認
- Published: 公開基準を通過

社数・自治体数とデータ深度を混同しません。

### Automation boundaries

自動化する:
- URL監視
- PDF/HTMLメタデータ
- テキスト抽出
- 金額・年度候補
- スキーマ検証
- 重複・リンク切れ
- 差分検知

人が確認する:
- 公約と事業の対応
- 目的と成果の解釈
- 因果関係
- 評価
- 中立的表現
- 訂正判断

## Initial issue plan

### P0

- Repository protections and CI
- Entity and status definitions
- Source schema and catalog
- Pilot source inventory
- Evidence component
- Data quality badge
- Fiscal record schema
- Project budget lifecycle schema

### P1

- Municipality page
- Project page
- Fiscal charts
- Promise registry
- Assembly registry
- Correction workflow
- Methodology page

### P2

- Comparison
- Search
- Change notifications
- Download
- Analytics
- API design

## Metrics

- Source coverage rate
- Reviewed data rate
- Published data rate
- Link health
- Data freshness
- Correction count and resolution time
- Build success
- Page performance
- Accessibility
- User completion of core questions

## Release cadence

- Code: small PRs continuously
- Reviewed data: batch PRs by municipality and topic
- Methodology: versioned releases only
- Production: scheduled release with checklist and rollback point
