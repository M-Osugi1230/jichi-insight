# リリース準備監査レポート（2026-11-15）

`docs/RELEASE_CHECKLIST.md` の未完了項目（97行目「dependency audit、secrets scan、Actions least-privilege監査」等）に対応する監査のうち、以下の4件を実施した記録。Actions least-privilege 監査は今回の範囲外。

- 対象: `M-Osugi1230/jichi-insight` の `origin/main`
- 監査時点の HEAD: `8c4466ce132bd4518920a7f01b355c6cb3c9107d`（2026-11-15 08:39 UTC "Record Pages publication status"）
- 方法: origin/main の新規 detached worktree で実施。コミット・push は一切していない。追跡ファイル総数 1,988 件。

---

## 1. main ブランチ保護 — **未設定（保護なし）**

### コネクタ経由では読み取り不可
- Muse の GitHub コネクタ（`/opt/hatch/bin/github call-read-tool`）で使える読み取りツールは CONNECTOR.md 記載の固定セット（`get_file_contents`、`list_pull_requests` 等）のみで、ブランチ保護を読むツールは含まれていない。
- `list-tools` で取得した実ツール目録（全46件）にも、protection / ruleset / 管理系の読み取りツールは存在しないことを確認した。コネクタ単体では保護設定は確認できない。

### gh CLI（M-Osugi1230 で認証済み・repo スコープ）による REST API 確認 — 確定結果あり
- `GET /repos/M-Osugi1230/jichi-insight/branches/main` → `"protected": false`
- `GET /repos/M-Osugi1230/jichi-insight/branches/main/protection` → HTTP 404 "Branch not protected"
- `GET /repos/M-Osugi1230/jichi-insight/rulesets` → `[]`（リポジトリルールセットなし）

### 結論
**main にはブランチ保護もルールセットも設定されていない。** 必須レビュー、必須ステータスチェック、force push / 削除のブロックはいずれも存在しない。現在の「ブランチ + PR 経由のみ」という運用は GitHub の設定による強制ではなく、プロジェクトの規律によるものである。リリース準備上のギャップとして明示する（技術的には main への直接 push が可能な状態）。

---

## 2. Secrets スキャン — **実シークレットの混入なし（origin/main ツリー範囲）**

- `gitleaks` は未インストールのため、grep パターン検査 + エントロピー検査で代替した。
- 対象: origin/main の追跡ファイル全 1,988 件（作業ツリー）。**git 履歴全体のスキャンは未実施**（gitleaks が使えないため）。この範囲制限を明記する。

### 検査パターン（すべてヒット 0 件）
- 秘密鍵ブロック: `BEGIN … PRIVATE KEY`
- AWS アクセスキー ID: `AKIA…` / `ASIA…` 形式
- GitHub トークン: `ghp_` / `gho_` / `ghu_` / `ghs_` / `ghr_` / `github_pat_`
- Slack トークン: `xox[baprs]-…`
- Stripe ライブキー: `sk_live_` / `rk_live_`
- Google API キー: `AIza…`
- JWT: `eyJ….eyJ….…`
- 資格情報のリテラル代入（`api_key` / `secret` / `token` / `password` 等への文字列リテラル代入、コード・設定ファイル対象、data/ 除外）
- URL 埋め込み資格情報（`https://user:pass@…`）
- `Bearer` リテラル

### ファイル名検査
- 追跡ファイルに `.env`、`*.pem`、`*.key`、`*.p12` / `*.pfx`、`id_rsa`、認証情報を想起させる名前のファイルは存在しない。

### エントロピー検査
- コード・設定ファイル（data/ とロックファイルを除外）の引用符内文字列（24文字以上）を対象に Shannon エントロピーを計算。
- パス・URL 様の文字列 2,834 件を除外（import パス等）。H ≥ 4.3 の非パス候補は 31 件で、**すべてテスト内の宮城 KPI データファイル識別子**（例: `miyagi_kpi_actuals_measure1_2024.json` のパス構成要素）であり、目視確認のうえ無害と判定した。

### ワークフロー
- `.github/workflows/` 内の secret 参照は `secrets.GITHUB_TOKEN`（組み込みトークンへの参照）の2件のみ。値そのものの記載はない。

### 結論
**origin/main の現行ツリーに、コミットされた実シークレットは見つからなかった。** 未実施範囲: git 履歴の走査（gitleaks 等の導入時に別途実施が望ましい）。

---

## 3. 依存関係監査

### Python（pip-audit 2.10.1 で実施）
pip-audit は venv-lh にも PATH にも無かったため、使い捨て venv に pip-audit 2.10.1 を導入して実施した。

| 対象 | 内容 | 結果 |
|---|---|---|
| venv-lh の実環境 | `pip freeze` の11パッケージ（pytest 9.2.0、jsonschema 4.26.0、PyYAML 6.0.3 等のテスト系ツールチェーン） | **既知の脆弱性 0 件** |
| pyproject.toml の宣言依存（CI が `quality.yml` で `pip install -e ".[dev]"` する集合） | runtime（beautifulsoup4、jsonschema、openpyxl、pdfplumber、python-docx、requests）+ dev（pytest、ruff）を宣言レンジ内で新規解決し、推移的依存を含む29パッケージを監査 | **既知の脆弱性 0 件**（全深刻度） |

注記: リポジトリに Python のロックファイルはなく、CI も毎回レンジ内で新規解決する。今回の解決は 2026-11-15 時点の最新許容バージョンによる。

### Web（pnpm audit）— **本環境からは完了できず**
- pnpm は未インストール。ルート `package.json` の `packageManager: pnpm@10.0.0` に従い `npx pnpm@10.0.0` を使用（node v24.22.1 は engines `>=24 <27` を満たす）。
- ワークスペースルートで `pnpm audit --prod --json` を **2 回試行し、2 回とも失敗**： registry.npmjs.org の一括監査エンドポイント（`/-/npm/v1/security/audits`）への接続が `ECONNRESET` で切断された。429（レート制限）ではない。pnpm 本体の取得など他の registry 通信は成功しており、当該エンドポイントへの接続のみが本環境から確立できない。
- したがって **Web 側の脆弱性判定は未実施**であり、「脆弱性なし」とは言えない。参考情報としてロックファイル上の本番依存の確定バージョンを記録する（これは監査結果ではない）：
  - 直接依存（apps/web）: next **16.4.6**、react **19.3.1**、react-dom **19.3.1**（postcss 8.5.23 等を含む。ロックファイルの解決パッケージ総数は 392 件＝dev 含む）
- クローズ条件: registry の監査エンドポイントへ到達できる環境（利用者のマシンや CI 等）で `pnpm audit --prod` を実行し、結果を記録すること。

---

## 4. 画像 alt テキスト監査 — **対象画像なし（欠落 0 件）**

apps/web のソース（app/、components/、lib/ の ts/tsx/css/mdx）を検査した。

| 検査項目 | 結果 |
|---|---|
| `<img` 使用箇所 | **0 件** |
| `next/image` の import | **0 件** |
| `<Image` コンポーネント使用 | **0 件** |
| Markdown 画像（`![...](...)`） | **0 件** |
| コンポーネント内のインライン `<svg>` | **0 件** |
| apps/web 内の画像ファイル | `app/icon.svg` の **1 件のみ** |

- 唯一の画像アセット `app/icon.svg` はサイトアイコン（favicon 相当、「JI」の文字アイコン）であり、コンテンツ画像ではないため alt テキストの対象外。
- CSS の `background-image` 使用は3件あるが、いずれも `<select>` の矢印を描く `linear-gradient`（装飾用の CSS グラデーション）で、画像ファイルではない。
- 生成ページはこれらのコンポーネントから描画されるため、画像を出力する要素自体が存在しない。

### 結論
**Web アプリにはラスタ画像・コンテンツ画像が存在せず、alt テキストの欠落は構造的に発生しない。** チェック対象 0 件・欠落 0 件。サイトがテキスト中心であることと一致する。

---

## 総括

| # | 項目 | 結果 |
|---|---|---|
| 1 | main ブランチ保護 | **未設定**（API で確定。必須レビュー・必須チェック・force push ブロックなし、ルールセットなし）。コネクタでは読み取り不可、gh CLI で確認 |
| 2 | Secrets スキャン | **混入なし**（origin/main ツリー全 1,988 ファイル、パターン + エントロピー検査）。履歴スキャンは未実施 |
| 3 | 依存関係監査 | Python: **脆弱性 0 件**（venv 実環境 11 件 + 宣言依存の解決集合 29 件）。Web: **未完了**（pnpm audit のエンドポイントへ本環境から接続できず2回失敗。バージョン記録のみ） |
| 4 | 画像 alt | **対象画像なし**（`<img` / `next/image` ともに 0 件。唯一のアセットは favicon 用 SVG） |
