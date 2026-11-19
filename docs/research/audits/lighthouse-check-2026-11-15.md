# Lighthouse 監査・モバイルレイアウト実測レポート（2026-11-15 再試行）

- 位置づけ: 2026-11-15 朝の a11y 監査で「環境の Chromium 制約により未実施」となった Lighthouse 測定の再試行結果。実施キット（`human-testing-kit-2026-11-15.md` §4）の対象ページを中心に、本番 URL に対して実測した。
- **結論: Lighthouse は実行できた。** 全7ページで完全なレポート（JSON / HTML）を取得した。朝の「未実施」は本試行で解消された。ただし測定経路はサンドボックス環境経由であり、Performance 値には環境由来の留保が付く（§2）。
- GitHub への書き込みは行っていない（計測と本ファイルの保存のみ）。

## 1. 実施概要

| 項目 | 内容 |
|---|---|
| 実施日時 | 2026-11-15 14:56〜15:00 JST（レポートの fetchTime: 05:56〜06:00 UTC） |
| 対象 | 本番サイト https://m-osugi1230.github.io/jichi-insight/ の7ページ（下表） |
| 対象コミット | `a371736b077df5ba605e648688ac5ff1bec6af1a`（`.github/publication-status.json`、status=verified、verified_at 2026-11-15T05:54:06Z） |
| ツール | Lighthouse 13.6.0（CLI、npx 経由）／ Chrome for Testing 157.0.8103.78（ヘッドレス） |
| 条件 | モバイル（formFactor=mobile、Moto G 相当のエミュレーション）、throttlingMethod=simulate、全カテゴリ（Performance / Accessibility / Best Practices / SEO） |
| 成果物 | `lh-work/reports/<page>.report.json` / `.report.html`（7ページ分） |

### 朝の未実施から実行に至るまでの障害と対処（事実の記録）

1. **Chrome 本体が環境になかった** → `@puppeteer/browsers` で Chrome for Testing 157 をダウンロードして使用した。
2. **`/tmp` が 100% 枯渇**（512MB の tmpfs が他作業で満杯）し、Chrome のプロファイル作成に失敗して無言で終了した → プロファイルと作業ディレクトリをホーム側ファイルシステムへ移した。
3. **Chrome がプロキシ認証を使えない**: この環境の外向き通信は認証付き egress プロキシ経由だが、Linux 版 Chrome は環境変数のプロキシ認証情報を無視する（Chromium の既知の制約、ログに `Proxy authentication parameters ignored`）。当初は `ERR_TUNNEL_CONNECTION_FAILED` で全ページ読み込み失敗 → ローカルに認証を肩代わりする中継プロキシ（`lh-work/proxy-shim.js`）を立て、Chrome はそれ経由で接続した。
4. **プロキシの TLS 証明書**: egress プロキシが独自 CA で TLS を中継するため、Chrome では `ERR_CERT_AUTHORITY_INVALID` となった → 測定用 Chrome に限り `--ignore-certificate-errors` を指定した（サイト自体の証明書の問題ではない。検証を無効化したのはサンドボックス内ブラウザのみ）。
5. **chrome-launcher が起動できなかった**（`waiting for dynamic debugging port` でタイムアウト） → Chrome を手動起動し、Lighthouse を `--port` で接続する方式に切り替えた。
6. **共有 Chrome インスタンスの劣化**: 連続実行の後半3ページが `READ_FAILED: An internal Chrome error occurred` で部分結果となった → ページごとに Chrome を再起動して再試行し、全ページ完全な結果を得た。本レポートの数値はすべて成功した実行のものである。

## 2. 測定値の留保（Performance について）

- 本測定の通信経路は「サンドボックス → 認証プロキシ → GitHub Pages」であり、実機のモバイル回線とは異なる。加えて実行 CPU は共有 1.5 コア相当で、Lighthouse の simulated throttling と相まって **TBT / TTI は実機より悪く出やすい**。実際、ページ重量が同程度でも TBT は 430〜2,020ms と実行間ばらつきが大きい。
- したがって **Performance スコア（68〜79）は参考値**であり、実機・通常回線での値とはみなせない。Accessibility / Best Practices / SEO は DOM ベースの監査であり、この留保の影響をほぼ受けない。
- CLS は全ページ 0、LCP は 1.8〜3.0 秒（同上の留保つき）。

## 3. スコア結果（モバイル、全カテゴリ）

| ページ | URL | Performance | Accessibility | Best Practices | SEO | FCP | LCP | TBT | CLS | リクエスト数 | 転送量 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| トップ | / | 73 | 96 | 96 | 100 | 2.2s | 3.0s | 760ms | 0 | 38 | 580 KiB |
| 自治体一覧 | /municipalities | 79 | 93 | 96 | 100 | 2.7s | 2.9s | 430ms | 0 | 29 | 561 KiB |
| データ品質 | /data-quality | 78 | 92 | 96 | 100 | 2.4s | 2.4s | 660ms | 0 | 28 | 541 KiB |
| 変更履歴 | /corrections/history | 68 | 100 | 96 | 100 | 2.1s | 2.1s | 2,020ms | 0 | 27 | 535 KiB |
| 宮城県 | /municipalities/miyagi | 68 | 93 | 96 | 100 | 2.8s | 2.9s | 1,020ms | 0 | 34 | 610 KiB |
| レビュー進捗 | /review-progress | 74 | 100 | 96 | 100 | 1.9s | 1.9s | 1,250ms | 0 | 28 | 545 KiB |
| 訂正・反論 | /corrections | 76 | 100 | 96 | 100 | 1.8s | 1.8s | 1,060ms | 0 | 27 | 536 KiB |

注記:
- 「redirects（複数リダイレクトの回避）」監査はトップ以外の6ページで失敗しているが、これは測定時に末尾スラッシュなし URL を指定し、GitHub Pages が `/municipalities/` 等へリダイレクトしたためであり、サイト側の欠陥ではない。
- 転送量は全ページ 535〜610 KiB（朝の静的監査の推定「圧縮約530 KiB」と概ね整合）。

## 4. Accessibility の失敗項目（重大な順）

### 4.1 color-contrast（4ページで失敗。静的監査の残所見を実測で裏付け）

| ページ | 件数 | 代表例（前景 / 背景 = 比率、サイズ） |
|---|---|---|
| 自治体一覧 | 10件 | ステータスバッジ `.statusBadge--verified`: `#ff9a80` / `#dcebe5` = **1.67:1**、9.76px・bold（最も深刻）。注記系 `#9b978d` / `#ece8dd` = 2.38:1、9.92px ほか |
| トップ | 6件 | 注記 `<span>`: `#b1aca0` / `#f5f3ed` = 2.03:1、10.4px。.eyebrow: `#a83a24` / `#0a2236`（濃紺地）= 2.54:1、10.72px・bold |
| データ品質 | 5件 | 注記 `<span>`: `#9b978d` / `#f5f3ed` = 2.62:1、9.28px |
| 宮城県 | 5件 | .eyebrow: `#a83a24` / `#102e46`（濃紺地）= 2.19:1、10.72px・bold。`<strong>`: `#986b16` / `#ece8dd` = 3.85:1、11.52px・bold |

- 合格だったページ: 訂正・反論、変更履歴、レビュー進捗（color-contrast は pass）。
- 読み取り: PR #461・#464 で修正したコーラル（`#a83a24`）は**明色地では AA を満たすが、濃紺地（ヒーロー等）の上では 2.19〜2.54:1 と未達**であることが新たに判明した。また静的監査で「推定計算」で残っていたバッジ色・注記色の未達が、実測でも確認された。対象はいずれも 9.3〜11.5px の小さい文字である。

### 4.2 label-content-name-mismatch（全7ページ、各2件）

- 対象は全ページ共通の2要素: ヘッダーのブランドリンク `<a class="brand" aria-label="Jichi Insight ホーム">` と、ナビゲーションの `<summary aria-label="ナビゲーションを開く">`。可視テキストが accessible name に含まれていない（WCAG 2.5.3 Label in Name の観点。音声操作ユーザーが表示ラベルで呼んでも一致しない）。
- Lighthouse 13.6 では本監査の Accessibility カテゴリ内の重みが 0 のため、**スコアは下がっていない**（訂正系3ページの A11y 100 はこの理由による）。スコアに出ないが実在する指摘として記録する。

### 4.3 aria-prohibited-attr（自治体一覧・データ品質、各5件）

- Phase 10 サマリのバ
...[truncated 4992 chars]