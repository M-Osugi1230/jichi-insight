# Jichi Insight 初期ロードマップ Issue #5〜#11 実態再照合レポート（2026-11-15）

- 実施日: 2026-11-15（JST）
- 対象: Issue #5〜#11（初期ロードマップ、すべて 2026-07-14 作成・本文未更新・受け入れ条件は全て未チェックのまま）
- 方法: GitHub connector（issue_read）で本文と受け入れ条件を取得 → 作業クローン（最新 main = da9b39a）の実ファイルで条件ごとに実測 → 公開サイト（https://m-osugi1230.github.io/jichi-insight/）の URL 実在確認（対象14URLすべて HTTP 200）。
- 本タスクは読み取り専用。Issue の編集・コメント投稿は行っていない。各 Issue 末尾の「更新コメント案」は投稿用の下書きである。
- 分類の定義: **満たす**＝実装と根拠を確認／**部分的に満たす**＝土台はあるが条件の一部が未達／**満たさない**＝未実装または未実施／**確認不能**＝実物だけでは判定できず人間の確認が必要。
- 下地: 監査レポート `audit-2026-11-15.md` (4)・(5)。本レポートはその後の進捗（PR #456 マージ等）を含む最新 main で再照合した。

## 総括

| Issue | タイトル | 満たす | 部分的 | 満たさない | 確認不能 | 推奨 |
|---|---|---|---|---|---|---|
| #5 | 共通 Evidence/鮮度/品質 UI コンポーネント | 2 | 2 | 2 | 0 | **更新すべき** |
| #6 | 自治体プロフィール＋3年度財政ビュー | 3 | 1 | 0 | 1 | **更新すべき** |
| #7 | 重点事業ページと予算→成果ライフサイクル | 1 | 4 | 1 | 0 | **更新すべき** |
| #8 | 首長公約台帳と進捗モデル | 2 | 2 | 2 | 0 | **更新すべき** |
| #9 | 議会・採決・支出・視察モデル | 2 | 3 | 1 | 0 | **そのまま継続** |
| #10 | 訂正・反論・変更履歴 | 2 | 3 | 1 | 0 | **更新すべき** |
| #11 | preview / staging / production | 1 | 3 | 2 | 0 | **更新すべき** |

- **クローズ可能: 0件**。どの Issue も「画面はあるが受け入れ条件の核心が残る」状態であり、現時点で閉じられるものはない。
- **更新すべき: 6件**（#5, #6, #7, #8, #10, #11）。実装済み部分を実測根拠付きで記録し、残タスクだけを残す形に更新すべき。
- **そのまま継続: 1件**（#9）。残タスクがスコープの大半を占め、現状の「未着手に近い」記述と実態の乖離が最も小さい（ただし現状スライを明記するコメントは有用）。

### 最も重要な残タスク（上位3件）

1. **#11: PR プレビューと staging 環境が存在せず、デプロイが品質ゲートに連動していない。** pages.yml は main への push のみで発火し、Quality ワークフローの成功をデプロイの前提にしていない。Public beta の Engineering ゲート（監査 P0-14/P1-1）に直結する最大の構造的欠落。
2. **#10: 訂正フローの通し試験（架空訂正）が未実施で、変更履歴の公開表示がない。** 申請導線と手続文書は完成しているが、Trust ゲート（監査 P0-1〜P0-3）が要求する「実際に1件通して履歴が公開される」証跡がゼロ。
3. **#9: 議会の共通モデル（議員・議案・議員別採決）が未実装。** 実装済みは福岡県議会の海外活動スライ（視察3件）のみで、3議会共通モデルはスキーマ例（`data/examples/assembly.example.json`）と設計文書止まり。P1 で最大の未実装スコープ。

次点: #5 のキーボード/スクリーンリーダー・レビューと fixture デモ（監査 P0-10 と連動）、#7 の事業単位の予算接続（全30取組が progress_linkage=not_linked）。

---

## Issue #5: [P0] Build shared evidence, freshness and data-quality UI components

本文の6条件を実測した結果: **満たす 2 / 部分的 2 / 満たさない 2**。コンポーネント群（`apps/web/components/StatusBadge.tsx`、`SourceCard.tsx`、`EvidencePanel.tsx`）は実在し、全主要ページで使用されている（利用箇所は app 配下 25 ファイル以上）。不足は「fixture によるデモ」と「a11y レビューの実施記録」。

| 受け入れ条件 | 分類 | 実測根拠 |
|---|---|---|
| Components work on mobile and desktop | 部分的に満たす | 共通コンポーネントは全ページで使用され、サイト全体がレスポンシブ実装（`apps/web/app/globals.css` 系）。ただし実機確認の記録はなく、`docs/RELEASE_CHECKLIST.md` の実機監査は未チェックのまま（監査 P0-10）。 |
| Status is not communicated by color alone | **満たす** | `StatusBadge` は `label` 文字列を必須 props として描画し、tone は補助的な色分けにすぎない（例: `label="Reviewed"`）。 |
| Source title, organization, URL, page and date are accessible | 部分的に満たす | `SourceCard` は資料名・組織・公式URL・確認日（`indexed_at`）を表示。ページ番号は SourceCard 単体にはなく、Evidence claim 単位の `location_note` として `EvidencePanel` に表示される。年度と最終確認は EvidencePanel の「対象年度」「保存値」等で表示。 |
| Missing values cannot appear as zero | **満たす** | `apps/web/lib/finance.ts` の `formatExactYen` / `formatCompactYen` / `formatJapaneseYen` はいずれも null を「未確認」と表示。`SettlementTrend` は null を「評価不能」と表示。状態は型付き列挙（`availability: published / not_published / not_found / restricted / unknown` 等）で管理。 |
| Components are demonstrated with fictional fixtures | 満たさない | 架空 fixture は政策資料収集側には存在する（`tests/test_policy_sources.py` の「架空市」fixture）が、UI コンポーネント自体のデモ/fixture ページは存在しない。 |
| Keyboard and screen-reader semantics are reviewed | 満たさない | レビュー記録が存在しない（RELEASE_CHECKLIST 未チェック）。装飾要素への `aria-hidden` 等の配慮は散見されるが、レビュー実施の証跡はない。 |

**推奨: 残タスクを残して更新すべき。** 残タスク = (a) fixture デモページ、(b) キーボード/スクリーンリーダー・レビュー（P0-10 と一体）、(c) SourceCard へのページ位置情報の出し方の統一。

### 更新コメント案（#5）

```markdown
## 実態再照合（2026-11-15）

本文の受け入れ条件は未チェックのままですが、実装側は大きく進んでいます。実測結果を記録します。

**満たしている条件**
- 色だけに頼らない状態表示: `apps/web/components/StatusBadge.tsx` はラベル文字列を必須として描画し、色は補助です。
- 欠測を 0 と表示しない: `apps/web/lib/finance.ts` の金額整形は null を「未確認」と表示し、`SettlementTrend` は「評価不能」と表示します。状態は型付き列挙で管理されています。

**部分的に満たしている条件**
- モバイル/デスクトップ動作: 共通コンポーネント（StatusBadge / SourceCard / EvidencePanel）は全主要ページで使用されていますが、実機確認の記録はまだありません。
- 出典情報の表示: SourceCard は資料名・組織・URL・確認日を表示します。ページ位置は Evidence claim の location_note として EvidencePanel 側にあります。

**残タスク**
- [ ] UI コンポーネントの fictional fixture によるデモ
- [ ] キーボード / スクリーンリーダーのセマンティクス・レビュー（RELEASE_CHECKLIST の実機監査と一体）
- [ ] SourceCard と EvidencePanel のページ位置表示の統一

この Issue は上記が残るためオープン継続とします。
```

---

## Issue #6: [P1] Implement municipality profiles and three-year fiscal views

**満たす 3 / 部分的 1 / 確認不能 1**。福岡3自治体のページは本番稼働し（いずれも HTTP 200）、検証済みデータから描画されている。県は決算5年度トレンドを持つが、2市は「当初予算＋単年度決算」のスライ段階で、目的別・性質別支出、基金・債務指標、住民1人当たり値は未掲載（ページ上で「まだ評価していないこと」として明示されている）。

| 受け入れ条件 | 分類 | 実測根拠 |
|---|---|---|
| 福岡県, 福岡市 and 北九州市 render from validated data | **満たす** | `apps/web/app/municipalities/{fukuoka-prefecture,fukuoka-city,kitakyushu-city}/page.tsx` が `data/reviewed/<自治体>/fiscal_records.json` と `evidence_packets.json` を読み描画。本番 URL は3件とも 200。 |
| At least three fiscal years are available where official data permits | 部分的に満たす | 福岡県は決算 2020〜2024 の5年度トレンド（`settlementTrend()`、`SettlementTrend` コンポーネント）。一方、福岡市・北九州市の Reviewed 財政レコードは 2024 決算＋2026 当初予算の2年度分のみで、3年度トレンドは未整備。 |
| Initial, revised and settlement figures are not mixed | **満たす** | `FiscalRecord.stage` が `initial_budget / revised_budget / execution / settlement` の型付きフィールドで、`settlementRecord()` は stage=settlement のみを抽出。市ページは「予算案と決算を、別の事実として見る」と節を分離。 |
| Missing data is explicit | **満たす** | null は「未確認」表示。市ページには「まだ評価していないこと」節があり、目的別・性質別支出などが未評価であることを明示。 |
| Mobile core questions can be answered within three minutes | 確認不能 | 初見ユーザーによる実測記録が存在しない（監査 P0-13 の3分理解テストと同一の未実施事項）。実物だけでは判定できない。 |
| All key figures link to official evidence | **満たす** | 各レコードに EvidencePacket が対応し、`EvidencePanel` が一次資料リンク・該当箇所（location_note）を表示。福岡市ページは「4つの数値すべてに、戻れる根拠を付ける」とし、実際に全レコード分の packet が存在する。 |

スコープとの差分（条件外だが本文 Scope にあるもの）: 目的別・性質別支出、基金・債務・主要財政指標、総額/住民1人当たりの併記、比較グループ文脈は2市では未実装（ページ上で未評価と明示）。県ページも指標の網羅は部分的。

**推奨: 残タスクを残して更新すべき。** 残タスク = (a) 福岡市・北九州市の3年度以上の決算トレンド、(b) 目的別・性質別支出と基金・債務指標、(c) 住民1人当たり値、(d) 3分理解テスト（人間確認）。

### 更新コメント案（#6）

```markdown
## 実態再照合（2026-11-15）

福岡3自治体のページは本番稼働済みで、受け入れ条件の一部は満たしています。

**満たしている条件**
- 3自治体とも `data/reviewed/` の検証済み財政データから描画され、本番で表示されています。
- 当初予算・補正・決算の混同防止: `stage` を型付きフィールドとして保持し、決算トレンドは決算レコードのみから構成しています。福岡県は決算2020〜2024の5年度トレンドを表示しています。
- 欠測の明示: null は「未確認」と表示し、未評価範囲は各ページの「まだ評価していないこと」で明示しています。
- 主要数値と公式 Evidence の接続: 全レコードに Evidence Packet が対応し、一次資料リンクと該当箇所を表示しています。

**残タスク**
- [ ] 福岡市・北九州市の3年度以上の決算トレンド（現状は2024決算＋2026当初予算）
- [ ] 目的別・性質別支出、基金・債務などの財政指標
- [ ] 住民1人当たり値の併記
- [ ] モバイルで主要な問いに3分以内に答えられるかの実測（人間の確認が必要）

この Issue は上記が残るためオープン継続とします。
```

---

## Issue #7: [P1] Implement priority-project pages and the budget-to-outcome lifecycle

**満たす 1 / 部分的 4 / 満たさない 1**。福岡県の政策取組30件が Reviewed カタログとして存在し、各取組ページ（KPI 基準値・目標値）が本番稼働している。しかし全30件が `progress_linkage_status = not_linked`、`evaluation_status = not_assessed` であり、事業単位の予算（当初・補正・執行・決算）接続は未実装。Phase 10 の事業照合（266事業・108候補）は「候補は完成済みの接続ではない」と明示された候補段階にある。

| 受け入れ条件 | 分類 | 実測根拠 |
|---|---|---|
| At least 30 projects reach Reviewed status | 部分的に満たす | `data/entities/policy/fukuoka_prefecture_policy_initiatives.json` は取組30件・カタログ自体の review_status=reviewed。ただしこれは計画上の「取組・数値目標」の Reviewed であり、予算接続済みの事業 Reviewed ではない（全件 not_linked / not_assessed）。件数の字面は満たすが、Issue の Goal（予算→成果の接続）としては未達。 |
| Every project has an official source packet | 部分的に満たす | 政策方向（4件）には Evidence Packet が対応。取組単位では計画出典（source_document_url、該当ページ）への接続はあるが、取組ごとの source packet は未整備。 |
| Budget stages and fiscal years are explicit | 部分的に満たす | 自治体財政レベルでは stage と年度が明示される（#6 のとおり）。事業単位では予算段階そのものが未接続で、未接続であることはページ上で明示されている。 |
| KPI targets and actuals are not conflated | **満たす** | 取組ページ（`PolicyTargetDetail`）は基準値・目標値と実績を分離し、「実績未接続」状態を明示。説明文でも「基準値、目標値、期間、実績未接続状態とともに確認できます」としている。 |
| Causality limitations are displayed | 部分的に満たす | 方法論ページで事実/比較/解釈/評価の層を定義し、取組ページでも「基準値と目標値だけでは達成度を評価しません」と明示。ただし事業ページ単位での因果の限界表示は、事業接続自体が未実装のため限定的。 |
| Project pages are reusable across all three municipality types | 満たさない | 取組ページは福岡県のみ（`apps/web/app/policies/fukuoka-prefecture/initiatives/01〜25` 等）。福岡市・北九州市の事業ページは存在しない。 |

**推奨: 残タスクを残して更新すべき。** 残タスクの中心は「事業単位の予算ライフサイクル接続」（Phase 10 候補 108件の照合確定が前提）と「3自治体への展開」。

### 更新コメント案（#7）

```markdown
## 実態再照合（2026-11-15）

**進んでいる部分**
- 福岡県の政策取組30件が Reviewed カタログとして登録され、取組ごとの数値目標ページが本番稼働しています。
- KPI の目標値と実績は混同されておらず、実績が未接続であることはページ上で明示されています。

**未達の核心**
- 全30取組が `progress_linkage_status = not_linked`、`evaluation_status = not_assessed` です。事業単位の当初予算・補正・執行・決算の接続（この Issue の Goal である budget-to-outcome lifecycle）は未実装です。
- Phase 10 の事業照合（266事業・108候補）は候補段階であり、接続の確定ではありません。
- 事業ページは福岡県のみで、福岡市・北九州市への展開はありません。

**残タスク**
- [ ] 事業単位の予算段階（当初・補正・執行・決算）と KPI 実績の接続
- [ ] 取組ごとの公式 source packet の整備
- [ ] 福岡市・北九州市への事業ページ展開

この Issue はオープン継続とします。
```

---

## Issue #8: [P1] Build the executive manifesto registry and progress model

**満たす 2 / 部分的 2 / 満たさない 2**。台帳は「任期の固定」と「公約出典の探索・記録可能性の判定」までが完了した段階。公約レコードそのものは **0件**（作成された promise record はゼロ）で、進捗モデルは未稼働。一方、採点しない・総合点を出さないというガードレールは満たしている。

| 受け入れ条件 | 分類 | 実測根拠 |
|---|---|---|
| All identified promises are recorded or have an explicit non-recordable reason | 部分的に満たす | 福岡3首長全員の出典探索記録（`data/entities/executives/manifesto_source_searches.json`、3件）が存在し、結果は「source_registered 1件 / 安定した一次資料が未発見 2件」と理由付きで記録。ただし公約の同定・記録自体は未実施で、「記録できない理由」は出典レベルの判定にとどまる。 |
| Original wording is preserved with official evidence | 満たさない | 公約レコードが0件のため、原文保存の対象自体が存在しない。唯一の manifesto review（北九州市長）は `promise_records_created = 0`、`segmentation_status = manual_review_required`、理由コード（mixed_narrative 等）付きで記録されている。 |
| Project links include confidence and review status | 満たさない | 公約レコードが存在しないため、事業リンクも存在しない（型定義には confidence / review_status の設計がある）。 |
| Changed promises are not automatically treated as failure | 部分的に満たす | 失敗として扱う仕組み自体が存在せず、ページは「現職名と任期が分かっても、実績評価はできない」と評価境界を明示。ただし進捗モデル未稼働のため、検証可能な実装としての充足ではない。 |
| Policy ideology is not scored | **満たす** | サイト全体に思想・政策の採点は存在せず、/executives は評価を行わない旨を明示している。 |
| No aggregate executive score is published in alpha | **満たす** | 総合スコアはどこにも公開されていない。 |

**推奨: 残タスクを残して更新すべき。** 残タスク = (a) 出典が登録できた首長からの公約原文の切り分けとレコード化（手動レビュー必須の1件を含む）、(b) 公約と事業・予算の接続、(c) 進捗状態の運用開始。

### 更新コメント案（#8）

```markdown
## 実態再照合（2026-11-15）

**完了している土台**
- 福岡県知事・福岡市長・北九州市長の現任期（任期・選挙・出典）を Evidence 付きで固定しています。
- 3首長全員について公約出典の探索記録があり、「出典が登録できた1件」「安定した一次資料が未発見の2件」が理由付きで記録されています。未発見を不存在と扱わない方針も明記されています。
- 政策思想の採点と首長の総合スコアは存在しません（受け入れ条件のガードレールは充足）。

**未達の核心**
- 公約レコードは現在 0 件です。北九州市長の manifesto review は、手動切り分けが必要な理由コード付きで記録されていますが、レコード化には至っていません。
- そのため、公約原文の保存、事業・予算への接続、進捗モデルは未稼働です。

**残タスク**
- [ ] 出典が確認できた公約原文の切り分けとレコード化（手動レビューを含む）
- [ ] 公約と関連事業・予算の接続（confidence と review status 付き）
- [ ] 進捗状態（変更・遅延・撤回と公式説明を含む）の運用開始

この Issue はオープン継続とします。
```

---

## Issue #9: [P1] Model assembly accountability, votes, expenses and inspection trips

**満たす 2 / 部分的 3 / 満たさない 1**。実装済みは福岡県議会の海外活動スライ（視察3件、費用・報告の状態と Evidence 付き）のみ。3議会共通の議員・議案・採決モデルは、スキーマ例（`data/examples/assembly.example.json`）と設計文書（`docs/ASSEMBLY_ACCOUNTABILITY.md`）止まりで、データ実装がない。/assemblies ページ自体が「議会全体の評価は、まだ行いません」と範囲を明示している。

| 受け入れ条件 | 分類 | 実測根拠 |
|---|---|---|
| 福岡県議会, 福岡市議会 and 北九州市議会 share one extensible model | 満たさない | 共通モデルでのデータ実装は存在しない。福岡県議会の海外活動だけが専用型（`apps/web/lib/assemblyOverseas.ts`）で実装され、他2議会のデータはない。 |
| Executive outcomes are not directly assigned as assembly performance | **満たす** | そのような帰属表示は存在せず、/assemblies は議会全体の評価を行わない旨を明示。 |
| Expenses are linked to reports and policy follow-up where available | 部分的に満たす | 海外活動3件について費用・報告書の状態（`cost_status` / `report_status`、未公開を含む）と Evidence Packet が接続済み。ただし政策フォローアップへの接続は限定的で、対象も海外活動のみ。 |
| Missing member-level votes are explicit | 部分的に満たす | /assemblies の Next scope に「議員別採決の公開状況」が明記され、未整備であることは利用者に分かる。ただし議会ごとの採決公開状況のデータ自体は未整備。 |
| Official records and page-level evidence are accessible | 部分的に満たす | 海外活動スライについては一次資料と該当箇所の Evidence が公開されている。他の領域（議案・採決・政務活動費）にはデータがない。 |
| No question-count-only ranking is introduced | **満たす** | 質問回数等によるランキングは存在しない。 |

**推奨: そのまま継続。** 残タスクがスコープの大半（共通モデル設計の実装、3議会の議員・議案・採決データ）であり、Issue 本文の記述と実態の乖離が7件中で最も小さい。ただし現状スライを明記するステータスコメントの投稿は有用。

### 更新コメント案（#9）

```markdown
## 実態メモ（2026-11-15）

現時点で実装済みなのは、福岡県議会の海外活動スライのみです。

- 海外活動3件について、目的・費用・報告書の状態（未公開を含む）と Evidence Packet を接続し、本番の /assemblies/fukuoka-prefecture/overseas-activities で公開しています。
- 議会全体の評価や、執行部成果の議会への帰属は行っていません。質問回数のみのランキングも導入していません。

**未実装（この Issue の残スコープ）**
- [ ] 3議会共通の議員・会派・委員会・議案・採決モデル（現状はスキーマ例と設計文書のみ）
- [ ] 議員別採決の公開状況の議会別データ
- [ ] 政務活動費・議会予算と報告書・政策フォローアップの接続

引き続きオープンとして進めます。
```

---

## Issue #10: [P1] Implement corrections, right of reply and immutable change history

**満たす 2 / 部分的 3 / 満たさない 1**。申請の入口（構造化フォーム）と手続文書は完成度が高い。一方で、変更履歴の「公開表示」と「架空訂正による通し試験」が未実施で、これは監査の P0-1〜P0-3（Public beta の Trust ゲート）と同一の残件である。

| 受け入れ条件 | 分類 | 実測根拠 |
|---|---|---|
| A user can submit a structured correction with official evidence | **満たす** | 本番 /corrections から `.github/ISSUE_TEMPLATE/data-correction.yml` のフォームへ導線があり、対象ページ・現在の記載・訂正案・公式 Evidence（URL・資料名・年度・ページ）・重大度が必須項目として構造化されている。 |
| Material errors are not silently overwritten | 部分的に満たす | `docs/CORRECTIONS.md` が修正前後・理由・根拠を残す手続を規定し、修正は PR 経由で Git 履歴に残る設計。ただし実際に重大訂正が発生・処理された公開事例はまだなく、運用の実績としては未検証。 |
| Previous and corrected states can be audited | 部分的に満たす | Git 履歴と文書化された変更履歴モデル（前後・理由・根拠・レビュー担当・日時）で監査可能性の土台はあるが、利用者が画面上で前後を照合できる公開履歴は未整備（次項）。 |
| Personal information is excluded from public issues | **満たす** | /corrections ページが公開 Issue へ個人情報・認証情報を書かないよう明示し、受付手順でも個人情報の有無を確認する段取りが文書化されている。 |
| The process is documented and tested using a fictional correction | 部分的に満たす | 手続・重大度（P0: 24時間以内に確認開始 / P1: 3営業日 / P2: 10営業日）・反論の扱いは `docs/CORRECTIONS.md` に文書化済み。しかし架空訂正による通し試験（送信→受付→審査→修正→履歴公開）は未実施（監査 P0-1/P0-2）。 |
| Public pages show relevant correction history | 満たさない | 公開ページに訂正履歴を表示する仕組み・データが存在しない。/corrections は手続の説明のみで、履歴一覧や個別ページへの訂正表示はない（監査 P0-3）。 |

**推奨: 残タスクを残して更新すべき。** 残タスク = (a) 架空訂正の通し試験と証跡の保存、(b) 変更履歴の公開画面。どちらも Public beta の Trust ゲートに直結する。

### 更新コメント案（#10）

```markdown
## 実態再照合（2026-11-15）

**満たしている条件**
- 構造化された訂正申請: 本番 /corrections から Issue フォーム（対象・現在の記載・訂正案・公式 Evidence・重大度が必須）へ申請できます。
- 個人情報の排除: 公開 Issue に個人情報を書かない注意と、受付時の確認手順が公開・文書化されています。
- 手続の文書化: `docs/CORRECTIONS.md` に、事実訂正と意見・反論の区別、重大度ごとの応答目標（P0 は24時間以内に確認開始 等）、修正前後と根拠を残す方針が定められています。

**残タスク**
- [ ] 架空の訂正による通し試験（送信→受付→審査→修正→履歴公開）を行い、証跡を残す
- [ ] 変更履歴の公開表示（修正前後・理由・根拠・日時を公開ページで確認できること）

上記2点は Public beta の Trust ゲートにも直結するため、この Issue はオープン継続とします。
```

---

## Issue #11: [P1] Establish preview, staging and production deployment

**満たす 1 / 部分的 3 / 満たさない 2**。本番公開の検証基盤（公開検証レコード、Production Smoke、Verify Pages）は強固だが、PR プレビューと staging 環境は存在せず、デプロイが品質ゲートの成功に機械的に連動していない。7件の中で Engineering 面の構造的欠落が最も大きい。

| 受け入れ条件 | 分類 | 実測根拠 |
|---|---|---|
| Every UI PR receives a preview URL | 満たさない | プレビュー用ワークフローが存在しない。`.github/workflows/pages.yml` は main への push と手動実行でのみ発火する。 |
| Staging uses reviewed but not-yet-public data | 満たさない | staging 環境自体が存在しない。`docs/DEPLOYMENT.md` は「実評価の公開前に別途 staging を導入する」と先送りを明記している。 |
| Production uses published data only | **満たす** | Web は `data/reviewed/` と catalog のみを読み込む構成で、候補（candidates）は公開経路に含まれない。静的エクスポート検証（`scripts/validate_static_export.py`）と公開検証（`.github/publication-status.json`: verified、deployed_commit_sha と verified_at を記録）が運用されている。ただしこれは環境分離ではなくデータ境界による担保である。 |
| A failed quality gate cannot deploy to production | 部分的に満たす | Quality ワークフローは PR と main push で実行されるが、pages.yml のデプロイは Quality の成功を前提条件にしていない（needs 連携なし）。main ブランチ保護の有無は本再照合でも確認手段がなく未確認。失敗したゲートが機械的にデプロイを止める保証はない。 |
| Rollback is documented and tested | 部分的に満たす | `docs/OPERATIONS_RUNBOOK.md` にロールバック手順（直前の安全なコミットへ戻す等）が文書化されている。実地訓練の記録はない（監査 P0-16）。 |
| Monitoring and incident ownership are documented | 部分的に満たす | production-smoke / verify-pages / nationwide-coverage-smoke の各ワークフローで公開後の自動確認はある。ただし OPERATIONS_RUNBOOK の担当表は各 owner が「未設定」で、障害時の責任者が文書上決まっていない（監査 P0-18）。 |

**推奨: 残タスクを残して更新すべき。** 残タスク = (a) PR プレビューの仕組み、(b) staging の要否と境界の確定、(c) デプロイと品質ゲートの連動（ブランチ保護の確認を含む）、(d) ロールバック訓練、(e) 運用担当の明記。

### 更新コメント案（#11）

```markdown
## 実態再照合（2026-11-15）

**満たしている条件**
- 本番は公開データのみを使用: Web は reviewed データと catalog のみを読み、候補データは公開経路に含まれません。公開検証レコード（deployed_commit_sha / verified_at）による本番確認も運用されています。

**部分的に満たしている条件**
- ロールバック: 手順は OPERATIONS_RUNBOOK に文書化されていますが、実地訓練の記録はありません。
- 監視: 公開後の smoke / verify ワークフローはありますが、運用担当（owner）が未設定です。
- 品質ゲート: Quality ワークフローは存在しますが、Pages デプロイはその成功を前提にしておらず、失敗が機械的にデプロイを止める保証はありません。

**未達**
- [ ] PR プレビュー URL の仕組みがありません（pages.yml は main push のみ）
- [ ] staging 環境がありません（DEPLOYMENT.md で先送りが明記されています）

**残タスク**
- [ ] PR プレビューの導入
- [ ] staging の要否と境界の確定
- [ ] デプロイと品質ゲートの連動（ブランチ保護の確認を含む）
- [ ] ロールバックの実地訓練
- [ ] 監視・障害対応の担当明記

この Issue はオープン継続とします。
```

---

## 付記: 再照合の方法と制約

- Issue 本文は GitHub connector の `issue_read` で取得（`get_issue` は現在の MCP サーバで提供されておらず使用不可だった）。
- 実装の判定はすべて最新 main（da9b39a）の実ファイルと、本番サイトの HTTP 200 確認に基づく。画面の存在だけで「満たす」とはせず、データ接続・状態表示・未接続の明示まで確認した。
- 「確認不能」は #6 の3分理解テストのみ。これは初見ユーザーの実測が必要な性質のもので、監査レポートの P0-13 と同一事項。
- 本レポートの推奨は分類の提案であり、Issue の更新・クローズの実施はユーザーの判断を経てから行うこと（本タスクでは読み取りのみ）。
- 関連する並行作業: PR #456（エラー状態の受け皿）は本再照合の基準 main にマージ済み。Phase 15 キュー整合性テスト等、他の P0 パッケージ作業とは独立に判定している。

（作成: 2026-11-15、読み取り専用再照合。Issue への書き込みは行っていない。）
