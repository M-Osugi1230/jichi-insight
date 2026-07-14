# Architecture

## Architecture goals

- 一次資料から公開表示までの追跡可能性
- 取得、抽出、レビュー、公開の分離
- 静的生成を優先し、低コストで安全に公開
- データ量増加後にPostgreSQLへ移行可能
- フロントエンドとデータ処理を同じスキーマで接続
- 人手レビューを自動化で補助し、置き換えない

## Repository architecture

```text
apps/web
  Next.js public application

pipelines
  collectors    資料一覧とメタデータ取得
  extractors    PDF/HTML/CSVから候補値抽出
  normalizers   年度、金額、団体、指標の標準化
  validators    スキーマ、整合性、重複、単位検証
  publishers    Reviewedデータから公開データ生成

data
  catalog       対象自治体、資料カタログ、収集計画
  examples      スキーマ検証用の架空データ
  raw           原資料・取得情報（原則Git外）
  extracted     自動抽出（原則Git外または大容量管理）
  reviewed      人手確認済み
  published     サイトが参照する生成物

schemas
  Web、pipeline、data reviewで共有する契約

apps/web
  published dataのみを参照
```

## Data flow

```text
Official source
    ↓ discover
Source catalog
    ↓ fetch / hash
Raw reference
    ↓ extract
Candidate records
    ↓ normalize
Normalized records
    ↓ validate
Schema + consistency checks
    ↓ human review
Reviewed records
    ↓ publish
Versioned public dataset
    ↓ build
Static pages / search index
```

## Initial technology

- Web: Next.js + TypeScript
- Package manager: pnpm workspace
- Data pipeline: Python
- Contract: JSON Schema 2020-12
- CI: GitHub Actions
- Hosting: static-first deployment
- Storage: Git-managed reviewed metadata + external raw document storage
- Future database: PostgreSQL

## Deployment environments

| Environment | Purpose |
|---|---|
| local | 開発とデータ確認 |
| preview | PR単位の表示確認 |
| staging | 公開前データ・回帰確認 |
| production | 公開条件を満たした内容のみ |

## Source of truth

- 原資料の所在: source catalog
- データ形式: schemas
- レビュー状態: reviewed records
- 公開画面: published recordsから生成
- 評価方法: docs/METHODOLOGY.md
- 変更判断: ADR

画面側で欠損値や評価を独自推定しません。

## Scaling path

### Stage 1

JSONと静的生成。対象3自治体、重点事業30件。

### Stage 2

データ更新ジョブ、検索インデックス、差分検知。都道府県・政令市へ拡大。

### Stage 3

PostgreSQL、API、履歴テーブル、権限付きレビューUI。

### Stage 4

全国自治体、議員・選挙、外部API、研究・報道向けデータ提供。
