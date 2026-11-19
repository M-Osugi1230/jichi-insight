# Lighthouse 再計測レポート（PR #483 デプロイ後、2026-11-15）

- 位置づけ: PR #483（Lighthouse a11y 修正、merge コミット `539a7e0a`）のデプロイ後に、前回計測（`lighthouse-check-2026-11-15.md`、対象コミット `a371736b`）で失敗した監査項目が本番で解消されたかを確認する再計測。
- **結論: 前回失敗した対象5項目は、全7ページで解消を確認した。** Accessibility は全ページ 100、Best Practices も全ページ 100（前回は全ページ 96）になった。
- GitHub への書き込みは行っていない（計測と本ファイルの保存のみ）。

## 1. 実施概要

| 項目 | 内容 |
|---|---|
| デプロイ確認 | `origin/main` の `.github/publication-status.json` を `git show` で確認: `deployed_commit_sha` = `539a7e0adcd56a6cd7a03944caa180163108b8af`（PR #483 の merge コミットそのもの）、`status` = `verified`、`verified_at` = 2026-11-15T06:13:45Z（15:13:45 JST）。**計測開始時点でデプロイ反映済み**だったため、待ち時間なしで計測に入った |
| 実施日時 | 2026-11-15 15:14〜15:17 JST（レポートの fetchTime: 06:14〜06:17 UTC）。トップのみ 15:18 JST に再実行（§2） |
| 対象 | 本番サイト https://m-osugi1230.github.io/jichi-insight/ の7ページ（前回と同一） |
| ツール・条件 | 前回と同一: Lighthouse 13.6.0（CLI）／ Chrome for Testing 157.0.8103.78（ヘッドレス）／ モバイル（Moto G 相当、throttlingMethod=simulate）。前回の計測基盤（`lh-work/` のローカル中継プロキシ＋手動起動 Chrome へ `--port` 接続、ページごとに Chrome 再起動）をそのまま再利用 |
| 成果物 | `lh-work/reports-recheck/<page>.report.json` / `.report.html`（7ページ分。前回分は `lh-work/reports/` に不変で残置） |

## 2. トップページの初回パスが古い内容だった件（再実行で解消）

- 再計測の初回パス（fetchTime 06:14:27Z、デプロイ検証の約40秒後）のトップページ結果は、前回と同一の失敗（color-contrast 6件・label-content-name-mismatch 2件・favicon 404）を返し、DOM に修正前の `aria-label="Jichi Insight ホーム"` 等が残っていた。
- 直後にライブ HTML を直接取得したところ、修正済みの内容（`aria-label` の mismatch 解消、`<link rel="icon" href="/jichi-insight/icon.svg?…">` の追加）が返った。初回パスは GitHub Pages の CDN キャッシュに残っていた旧 index.html を掴んだものと判断し、トップページのみ再実行した（fetchTime 06:18:07Z）。再実行結果が本レポートのトップページの値である。
- 初回パスの結果は `lh-work/reports-recheck/top-stale.report.json` として証跡を残した（比較には使用していない）。

## 3. スコア前後比較（モバイル、全カテゴリ）

| ページ | Performance 前回 → 今回 | Accessibility 前回 → 今回 | Best Practices 前回 → 今回 | SEO 前回 → 今回 |
|---|---|---|---|---|
| トップ | 73 → 73 | 96 → **100** | 96 → **100** | 100 → 100 |
| 自治体一覧 | 79 → 58 | 93 → **100** | 96 → **100** | 100 → 100 |
| データ品質 | 78 → 80 | 92 → **100** | 96 → **100** | 100 → 100 |
| 変更履歴 | 68 → 64 | 100 → 100 | 96 → **100** | 100 → 100 |
| 宮城県 | 68 → 58 | 93 → **100** | 96 → **100** | 100 → 100 |
| レビュー進捗 | 74 → 51 | 100 → 100 | 96 → **100** | 100 → 100 |
| 訂正・反論 | 76 → 76 | 100 → 100 | 96 → **100** | 100 → 100 |

参考指標（前回 → 今回）:

| ページ | FCP | LCP | TBT | CLS | リクエスト数 | 転送量 |
|---|---|---|---|---|---|---|
| トップ | 2.2s → 1.6s | 3.0s → 1.6s | 760ms → 1,514ms | 0 → 0 | 38 → 38 | 594 KiB → 589 KiB |
| 自治体一覧 | 2.7s → 2.5s | 2.9s → 4.2s | 430ms → 946ms | 0 → 0 | 29 → 29 | 575 KiB → 570 KiB |
| データ品質 | 2.4s → 2.3s | 2.4s → 2.4s | 660ms → 574ms | 0 → 0 | 28 → 28 | 554 KiB → 550 KiB |
| 変更履歴 | 2.1s → 2.5s | 2.1s → 2.5s | 2,020ms → 1,775ms | 0 → 0 | 27 → 27 | 548 KiB → 544 KiB |
| 宮城県 | 2.8s → 3.0s | 2.9s → 4.6s | 1,020ms → 758ms | 0 → 0 | 34 → 34 | 625 KiB → 620 KiB |
| レビュー進捗 | 1.9s → 2.8s | 1.9s → 4.8s | 1,250ms → 1,461ms | 0 → 0 | 28 → 28 | 558 KiB → 553 KiB |
| 訂正・反論 | 1.8s → 2.4s | 1.8s → 2.4s | 1,060ms → 672ms | 0 → 0 | 27 → 27 | 548 KiB → 544 KiB |

**Performance の留保（前回と同一）**: 本測定は「サンドボックス → 認証プロキシ → GitHub Pages」経由＋共有 1.5 コア相当 CPU での simulated throttling であり、**Performance スコアは参考値**で実機・通常回線の値とはみなせない。今回、自治体一覧・宮城県・レビュー進捗でスコアが下がったが、転送量は全ページで微減・リクエスト数は不変であり、悪化は LCP / TBT のタイミングばらつき（前回レポートでも同程度のページ間で TBT 430〜2,020ms のばらつきを確認済み）によるもので、コンテンツ増による悪化ではない。Accessibility / Best Practices / SEO は DOM ベースの監査であり、この留保の影響を受けない。

## 4. 対象項目の解消状況（ページごと）

### 4.1 color-contrast — 解消（全ページ pass）

| ページ | 前回 | 今回 |
|---|---|---|
| トップ | 失敗（6件） | **pass** |
| 自治体一覧 | 失敗（10件、最悪 1.67:1 のステータスバッジ） | **pass** |
| データ品質 | 失敗（5件） | **pass** |
| 宮城県 | 失敗（5件、濃紺地コーラル 2.19:1 等） | **pass** |
| 変更履歴 / レビュー進捗 / 訂正・反論 | pass | pass（維持） |

### 4.2 label-content-name-mismatch — 解消（全ページで監査対象が消滅）

- 前回: 全7ページで失敗（各2件: ブランドリンク `aria-label="Jichi Insight ホーム"`、ナビ `<summary aria-label="ナビゲーションを開く">`）。
- 今回: 全7ページで **notApplicable**（mismatch する要素が存在しない）。`aria-label` と可視テキストの不一致は本番から無くなった。
- なお本監査は Lighthouse 13.6 では Accessibility カテゴリ内の重み 0 のため、スコアの増減には現れない（解消の根拠は監査結果そのもの）。

### 4.3 aria-prohibited-attr — 解消

- 前回: 自治体一覧・データ品質で失敗（各5件、Phase 10 サマリの role なし div の `aria-label`）。
- 今回: 両ページとも **pass**。他5ページも pass を維持。
- 副次効果として、両ページと宮城県で前回失敗していた `agent-accessibility-tree` も pass になり、agentic-browsing カテゴリが 50 → 100 になった。

### 4.4 definition-list — 解消

- 前回: 宮城県で失敗（3件、dl 内の `div > small` 構造）。
- 今回: 宮城県 **pass**。全ページ pass（対象構造のないページは notApplicable）。

### 4.5 favicon 由来の Best Practices 減点 — 解消

- 前回: 全7ページで `errors-in-console` が失敗し、内容はドメインルート `https://m-osugi1230.github.io/favicon.ico` の 404（1件）。これが Best Practices 96 の唯一の減点要因だった。
- 今回: 全7ページで `errors-in-console` が **pass**（コンソールエラー 0 件）。HTML に `<link rel="icon" href="/jichi-insight/icon.svg?…">` が入り、ルート favicon.ico への 404 リクエストが発生しなくなった。Best Practices は全ページ **100**。

## 5. 新たに失敗した項目

- Accessibility / Best Practices / SEO の各カテゴリでは、**新たに失敗した項目はない**。
- Performance 系の診断項目で、ページにより以下のいずれかが今回新たに失敗として現れた: `server-response-time`（トップ・自治体一覧・変更履歴）、`bf-cache`（変更履歴）、`forced-reflow-insight`（データ品質・変更履歴）、`lcp-breakdown-insight`（トップ・自治体一覧・変更履歴）、`document-latency-insight`（トップ）。いずれも §3 の留保の対象（プロキシ経由の応答時間・タイミング計測に依存する診断）であり、#483 の変更対象（a11y 修正）とは無関係。実機・通常回線での再現性は**未確認**。
- 前回から継続して失敗している Performance 系の改善機会（`unused-javascript`、`valid-source-maps`、`cache-insight`、`modern-http-insight`、`render-blocking-insight` 等）は今回も同様に失敗している。これらは GitHub Pages のプラットフォーム制約を含む既知の項目で、#483 の対象外。

## 6. 残る指摘・未確認事項

- **#483 の対象5項目については、残る指摘はない**（全7ページで解消を実測確認）。
- Performance スコアの実機相当値は今回も**未確認**（サンドボックス経由の参考値のみ）。実機・通常回線での Lighthouse 測定は未実施のまま。
- 前回レポート §7 の人間側テスト（実機 iPhone 確認、キーボード操作、VoiceOver、3分理解テスト）は本再計測の対象外であり、未実施のまま変わらない。
- データ品質ページの品質テーブル（700px）のモバイル実機での使い勝手確認も、本再計測では対象外（未確認）。

## 7. 実施しなかったこと

- GitHub への書き込み（Issue / PR / コミット）は一切行っていない。
- 前回のレポートファイル（`lighthouse-check-2026-11-15.md`）と前回レポート一式（`lh-work/reports/`）は変更していない。
