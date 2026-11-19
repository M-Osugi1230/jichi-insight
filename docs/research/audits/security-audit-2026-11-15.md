# Jichi Insight 依存・セキュリティ監査レポート（2026-11-15）

- 実施日: 2026-11-15（JST）
- 対象: `M-Osugi1230/jichi-insight`、基準 main = `da9b39a1`（545b5ac のマージ後に publication 記録コミットが続いた先端。監査対象ファイルは origin/main の内容と一致することを diff で確認済み）
- 方法: 読み取り専用。pip-audit 実測、npm registry での最新版照合、ワークフロー16件の静的棚卸し、現行ツリーへの秘密情報パターン grep。
- 対応する残課題: 監査レポート P0-15（dependency audit / secrets scan / Actions least-privilege 監査）
- GitHub の secret scanning（connector の run_secret_scanning）は書き込み系のため、指示により**実行していない**。

## サマリー

| 深刻度 | 件数 | 内訳 |
|---|---|---|
| 高 | **0** | — |
| 中 | **2** | F1: pull_request トリガーで contents: write のワークフロー2件 / F2: lockfile 不在による依存解決の浮動 |
| 低 | **3** | F3: Actions がタグ固定のみ（SHA固定なし） / F4: Actions・Node dev依存のメジャー遅延 / F5: ade-remote-pr-gate の広い権限（設計上の記録） |

実測でゼロだったもの: Python 既知脆弱性（pip-audit）、秘密情報パターンの混入、pull_request_target、permissions 未宣言ワークフロー。
未実施: Node の脆弱性監査（pnpm audit）— 理由は F2 と環境制約（下記）。**Node の脆弱性件数は「未確認」であり、ゼロではない。**

---

## 1. Python 依存（pip-audit 実測）

pyproject.toml の依存（範囲指定のみ、ロックファイルなし）:

| パッケージ | 指定 | 解決バージョン（監査時） |
|---|---|---|
| beautifulsoup4 | >=4.13,<5 | 4.15.0 |
| jsonschema | >=4.23,<5 | 4.26.0 |
| openpyxl | >=3.1,<4 | 3.1.5 |
| pdfplumber | >=0.11,<1 | 0.11.10 |
| python-docx | >=1.2,<2 | 1.2.0 |
| requests | >=2.32,<3 | 2.34.2 |
| pytest（dev） | >=8.3,<10 | 9.2.0 |
| ruff（dev） | >=0.9,<1 | 0.17.5 |

- 実測: 専用 venv に上記＋推移的依存（pillow, pdfminer.six, cryptography, urllib3 等を含む全パッケージ）をインストールし `pip-audit 2.10.1` を実行 → **"No known vulnerabilities found"（既知脆弱性ゼロ）**。
- 留意: ロックファイルがないため、この結果は「監査時点の最新解決」に対するもので、CI が毎回同じ解決になる保証はない（F2 と共通）。

## 2. Node 依存（監査未実施・直接依存の乖離のみ実測）

- **pnpm audit は実施できなかった。** 理由は2つ:
  1. リポジトリに `pnpm-lock.yaml` がコミットされていない（F2）。作業用に生成した lockfile を使って試行したが、
  2. npm registry の監査エンドポイントが実行環境のポリシーで **403（policy_denied）** を返し、再試行も接続リセットで失敗した。
  したがって Node 依存の既知脆弱性は**未確認**。ゼロと書くことはできない。
- 直接依存と最新版の乖離（npm registry 実測、解決バージョンは直近の pnpm install 実測）:

| パッケージ | 指定 | 解決 | 最新 | 判定 |
|---|---|---|---|---|
| next | ^16.0.0 | 16.4.6 | 16.4.6 | 最新 |
| react / react-dom | ^19.0.0 | 19.3.1 | 19.3.1 | 最新 |
| eslint-config-next | ^16.0.0 | 16.4.6 | 16.4.6 | 最新 |
| @types/react / @types/react-dom | ^19.0.0 | 19.3.0 | 19.3.0 | 最新 |
| @types/node | ^24.0.0 | 24.19.2 | 26.6.6 | **メジャー遅延**（dev のみ） |
| eslint | ^9.0.0 | 9.39.5 | 10.15.0 | **メジャー遅延**（dev のみ） |
| typescript | ^5.9.0 | 5.9.3 | 7.0.2 | **メジャー遅延**（dev のみ） |

- メジャー遅延の3件はいずれも devDependencies で、本番配信物（静的エクスポート）には含まれない。3件とも Dependabot PR #17 で更新が提示済み（棚卸し資料参照）。本番依存（next/react/react-dom）は最新に一致。

## 3. GitHub Actions（全16件の棚卸し）

### 良好な点（実測）
- **全16件がトップレベル `permissions:` を明示**している（未宣言 0件）。
- `pull_request_target` の使用 **0件**。`curl | sh` 形式の実行 **0件**。PR の head を checkout する危険パターン **0件**（verify-pages の head_sha 参照はデプロイ済み SHA の記録用で、コード実行ではない）。
- pages.yml は contents: read + pages: write + id-token: write で、デプロイ用途として妥当。

### ワークフロー別一覧

| ファイル | 主な uses | permissions | トリガー上の注意 |
|---|---|---|---|
| ade-remote-pr-gate.yml | checkout@v4, setup-python@v5 | actions: read, **contents: write, pull-requests: write** | workflow_run + schedule。自動マージゲート用途（F5） |
| build-phase10-core-linkage.yml | checkout@v4, upload-artifact@v4 | **contents: write** | **pull_request でも起動（F1）** |
| commit-phase10-accountability-artifact.yml | checkout@v4, download-artifact@v4 | actions: read, contents: write | push + dispatch（自動コミット用途） |
| discover-phase10-accountability-sources.yml | checkout@v4, upload-artifact@v4 | **contents: write** | **pull_request でも起動（F1）** |
| extract-fukuoka-progress.yml | checkout@v4, upload-artifact@v4 | contents: read | — |
| extract-fukuoka-project-linkage.yml | checkout@v4, upload-artifact@v4 | contents: read | — |
| extract-hokkaido-actual-candidates.yml | checkout@v4, upload-artifact@v4 | contents: read | — |
| extract-miyagi-money-linkage.yml | checkout@v4, upload-artifact@v4 | contents: read | — |
| extract-tokyo-children-review.yml | checkout@v4, upload-artifact@v4 | contents: read | — |
| finalize-phase10.yml | checkout@v4 | contents: write | push + dispatch（自動コミット用途） |
| nationwide-coverage-smoke.yml | checkout@v4, upload-artifact@v4 | contents: read | — |
| pages.yml | checkout@v4, setup-node@v4, configure-pages@v5, upload-pages-artifact@v4, deploy-pages@v4 | contents: read, pages: write, id-token: write | 本番デプロイ経路 |
| production-smoke.yml | checkout@v4, upload-artifact@v4 | contents: read | — |
| quality.yml | checkout@v4, setup-python@v5, setup-node@v4, upload-artifact@v4 | contents: read | CI 本体 |
| render-chiba-visual-review-pages.yml | checkout@v4, setup-python@v5, upload-artifact@v4 | contents: read | — |
| verify-pages.yml | checkout@v4 | contents: write | workflow_run + push（公開記録の自動コミット用途） |

### 所見
- **F1（中）**: build-phase10-core-linkage.yml と discover-phase10-accountability-sources.yml は `pull_request` トリガーを持ちながら `contents: write` を宣言している。upload-artifact は contents: write を必要としないため、最小権限の観点では read へ下げられる可能性が高い。フォークPRではトークンは自動で read-only になるが、同一リポジトリのブランチPRでは write トークンでコードが実行される。推奨: 両ワークフローの permissions を contents: read に変更し、書き込みが要る工程があるかを実行履歴で確認する（ワークフロー変更は GitHub App の workflows 権限が必要なため、実施はユーザー側操作とセット）。
- **F3（低）**: 使用アクションは全てメジャータグ固定（@v4/@v5）で、**SHA 固定は0件**。タグは可変のため、厳密なサプライチェーン固定には SHA 固定＋Dependabot 更新が望ましい。現行の Dependabot 運用と併せて段階導入を推奨。
- **F4（低）**: Actions のメジャー遅延 — checkout@v4（PR #13 で v7 提示）、setup-python@v5（PR #14 で v6）、deploy-pages@v4（PR #29 で v5）等。いずれも滞留 Dependabot PR の対象で、新規の所見ではない。pages.yml 系は本番経路のため、棚卸しの推奨どおり公開検証を挟んだ段階適用が前提。
- **F5（低・記録）**: ade-remote-pr-gate.yml は contents: write + pull-requests: write を持ち、workflow_run と schedule で自動実行される。ADE の自動マージゲートという設計目的と対応しているが、リポジトリ内で最も強い自動権限のため、ADE 再開判断の際に併せて見直し対象とする。

## 4. シークレット混入チェック（現行ツリー、全パターン実測ゼロ）

現行ツリー（node_modules / .git / out を除く）を対象に grep 走査:

- 厳密パターン: 秘密鍵ヘッダ（RSA/EC/OPENSSH/PGP/PRIVATE KEY）、AWS アクセスキー（AKIA…）、GitHub トークン（ghp_ / github_pat_）、OpenAI 型キー（sk-）、Slack トークン、Google API キー → **ヒット 0件**
- 汎用パターン: `api_key / access_token / client_secret / password` への20文字以上の値の直接代入、`Bearer <token>` → **ヒット 0件**
- `.env` 系ファイルの存在 → **0件**
- 参考: リポジトリには SECURITY.md（脆弱性報告は Private vulnerability reporting を使用、公開Issueへの機微情報投稿禁止）が整備されている。
- 未実施: GitHub secret scanning の実行（書き込み系のため指示により見送り）。git 履歴全体の走査も本監査の範囲外（現行ツリーのみ）。

## 5. 横断所見

- **F2（中）**: **lockfile が存在しない** — Node は `pnpm-lock.yaml` が未コミット、Python も pyproject の範囲指定のみ。このため (a) CI の依存解決が実行ごとに浮動し、再現性がない、(b) 依存監査の対象バージョンを固定できない、(c) 悪性バージョンが範囲内に入った場合に検知しにくい。推奨: pnpm-lock.yaml を生成してコミットし、CI を `--frozen-lockfile` に切り替える。Python は当面 pip-audit の定期実行（解決時監査）で代替し、必要なら constraints ファイルを導入する。

## 推奨アクション（優先順）

1. pnpm-lock.yaml のコミット＋CI の frozen-lockfile 化（F2 の解消。ワークフロー変更を伴う場合はユーザー側操作とセット）
2. F1 の2ワークフローの permissions を contents: read へ（要 workflows 権限）
3. Node 監査の定常化: lockfile 整備後に GitHub の Dependabot alerts / `pnpm audit` を CI または定期実行で回す（今回未確認のまま残った領域）
4. Actions の SHA 固定は Dependabot の段階適用（#13〜#15, #28, #29 の処理）と合わせて検討（F3/F4）
5. ade-remote-pr-gate の権限は ADE 再開判断と同時に再確認（F5）

## 未実施・未確認の一覧

- Node 依存の既知脆弱性（pnpm audit 未実施: lockfile 不在＋監査エンドポイントの環境ポリシー 403）
- GitHub secret scanning（指示により実行せず）
- git 履歴全体の秘密情報走査（範囲外）
- 各ワークフローの実行時挙動（本監査は静的棚卸しのみ。F1 の「書き込み工程の有無」は実行履歴での裏付けが未実施）
