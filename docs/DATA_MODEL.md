# Data model

## Entity map

```text
Municipality
 ├─ FiscalRecord
 ├─ MetricSeries
 ├─ Policy
 │   └─ Project
 │       ├─ BudgetRecord
 │       ├─ Contract
 │       ├─ KPI
 │       ├─ Outcome
 │       └─ Evidence
 ├─ ExecutiveTerm
 │   └─ Promise
 │       ├─ Milestone
 │       ├─ RelatedProject
 │       └─ Evidence
 └─ Assembly
     ├─ Session
     ├─ Proposal
     ├─ Vote
     ├─ Committee
     ├─ PoliticalActivityExpense
     └─ InspectionTrip
```

## Core identifiers

識別子は表示名から直接生成せず、安定した形式を使用します。

- Municipality: `jp-local-<official-code>`
- Executive term: `<municipality-id>-executive-<term-start>`
- Promise: `<executive-term-id>-promise-<sequence>`
- Project: `<municipality-id>-project-<fiscal-year>-<source-key>`
- Source: `source-<sha256-prefix>`

## Municipality

- official code
- name
- type
- prefecture
- official URL
- population reference
- fiscal years available
- data status
- sources

## Project

- municipality
- fiscal year
- official title
- plain-language title
- purpose
- target population
- policy area
- related plan and promise
- budget records
- contracts
- KPIs
- outcomes
- assembly and audit references
- review status
- sources

## Promise

- original text
- source election
- policy area
- baseline
- target
- deadline
- funding statement
- municipal controllability
- progress state
- related projects
- change explanation
- evidence

## State semantics

### Progress

- `achieved`
- `mostly_achieved`
- `partially_achieved`
- `in_progress`
- `not_started`
- `changed`
- `abandoned`
- `not_assessable`

### Review

- `verified`
- `reviewed`
- `extracted`
- `inferred`
- `missing`

### Availability

- `published`
- `not_published`
- `not_found`
- `not_applicable`
- `unknown`

これらを空文字やnullだけで表現しないことが重要です。

## Temporal model

年度、公開日、取得日、確認日を区別します。

- `fiscal_year`: 対象会計年度
- `period_start`, `period_end`: 指標対象期間
- `published_at`: 資料公開日
- `retrieved_at`: 取得日
- `last_verified_at`: 最終確認日
- `valid_from`, `valid_to`: 組織・役職などの有効期間

## Evidence model

すべての重要な主張はEvidenceへ接続します。

- URL
- 資料名
- 発行主体
- 資料種別
- ページ
- 根拠箇所
- 抽出方法
- レビュー状態
- 信頼度
- コンテンツハッシュ
