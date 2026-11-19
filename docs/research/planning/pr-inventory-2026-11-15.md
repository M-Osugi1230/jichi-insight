# Jichi Insight 滞留PR棚卸しレポート（2026-11-15）

- 実施日: 2026-11-15（JST）
- 対象: `M-Osugi1230/jichi-insight` の Open PR 全件
- 基準 main: **`20cd7d8`**（"Record Pages publication status"。PR #456 マージコミット 370c3aa の後に公開記録コミット2件が先行したもの）
- 方法: GitHub connector（読み取り）で Open PR を実測し、監査時のローカルクローンを unshallow 化したうえで `refs/pull/*/head` を取得し、各PRについて (a) 最新 main からの遅れ/先行コミット数、(b) main との3点差分（変更ファイル・実質）、(c) `git merge-tree` による競合シミュレーション、(d) マージ後のツリーに対する対象テストのローカル実行、を行った。**書き込み（クローズ・マージ・コメント等）は一切行っていない。**
- テスト環境の注記: ローカル実行は pytest **9.2.0**（venv）＋ jsonschema。リポジトリの現行制約は pytest>=8.3,<9 のため、バージョン差のある参考値である（PR #16 がその制約を <10 に広げる提案である点に注意）。
- 未確認事項: 各PRの **GitHub Actions CI の現行状態**と **GitHub API 上の mergeable_state** は、監査時と同様に connector の読み取りツール範囲では取得できなかった。本レポートの「競合なし」はローカル `merge-tree` シミュレーション（現行 main × PR head）の結果であり、CI 成功を意味しない。

---

## サマリー

| 区分 | 件数 | PR |
|---|---|---|
| Open PR 実測総数 | **12** | #452, #454, #437, #439, #440, #13, #14, #15, #16, #17, #28, #29（監査時点から増減なし） |
| クローズ推奨 | **2** | #439, #440（実質空PR） |
| マージ候補 | **3** | #437, #14, #16（いずれも前提条件あり） |
| 保持 | **5** | #452, #454, #15, #28, #29 |
| 要ユーザー判断 | **2** | #13, #17 |

---

## Phase 15 関連PR（5件）

### PR #452 — いわき市 非公開レビュー候補 scaffold と安全性テスト

| 項目 | 実測 |
|---|---|
| 作成者 / 作成日 | M-Osugi1230 / 2026-11-14 |
| Draft | **Yes** |
| head / base | `feat/phase15-iwaki-safe-scaffold-20261114`（eb89be7） / main |
| 遅れ / 先行 | main より **10 behind / 5 ahead** |
| 変更ファイル | 2件・新規追加のみ: `data/candidates/iwaki-city/review_candidate.json`（166行）、`tests/test_phase15_iwaki_review_candidate_staging.py`（88行） |
| 競合 | merge-tree: **CLEAN** |
| 候補の状態（PR内JSON実測） | package_state=**scaffold**、human_review required=true / status=pending、publication.eligible=false |
| マージ後テスト（ローカル） | iwaki テスト＋既存 staging テスト = **8 passed** |
| 正本・既存候補との関係 | main の `data/candidates/` に iwaki-city は**存在しない**（既存は5市のみ）。正本キュー上のいわき市（072044）は pending_record_review のままで、このPRはキューを変更しない |

- **推奨: 保持**（Draft のまま維持）。
- 理由: scaffold は ADE の PlanningGoal request-102 が目指す prepared（evidence-backed）候補の**前段階**であり、ファイルパス（`data/candidates/iwaki-city/review_candidate.json`）は ADE が prepared 候補を作成する場合と同一になる。ADE 再開時に scaffold を土台にするか作り直すかが未決定のため、今マージすると二重作業・内容競合の起点になり得る。テストはマージ後ツリーで通過しており、scaffold 自体の品質に問題は見つかっていない。
- 次アクション: ADE 再開判断（監査レポート (7)-7）とセットで「scaffold を取り込んで土台にするか」を決める。それまで Draft 維持が安全。

### PR #454 — 水戸市 非公開レビュー候補 scaffold と安全性テスト

| 項目 | 実測 |
|---|---|
| 作成者 / 作成日 | M-Osugi1230 / 2026-11-14 |
| Draft | **Yes** |
| head / base | `feat/phase15-mito-safe-scaffold-20261114`（6fb3818） / main |
| 遅れ / 先行 | main より **7 behind / 4 ahead** |
| 変更ファイル | 2件・新規追加のみ: `data/candidates/mito-city/review_candidate.json`（169行）、`tests/test_phase15_mito_review_candidate_staging.py`（84行） |
| 競合 | merge-tree: **CLEAN** |
| 候補の状態（PR内JSON実測） | package_state=**scaffold**、human_review required=true / status=pending、publication.eligible=false |
| マージ後テスト（ローカル） | mito テスト＋既存 staging テスト = **8 passed** |
| 正本・既存候補との関係 | main に mito-city 候補は**存在しない**。正本キューの水戸市（082015）は pending_record_review のまま |

- **推奨: 保持**（Draft のまま維持）。理由・次アクションは #452 と同構造（ADE request-102 は「いわき→水戸」の順序を計画しており、水戸も同一パスの競合対象になる）。

### PR #437 — test(phase15): Morioka candidate の package state・構造 assert 追加

| 項目 | 実測 |
|---|---|
| 作成者 / 作成日 | M-Osugi1230（Jules 自動作成） / 2026-10-17 |
| Draft | No |
| head / base | `morioka-phase15-staging-test-update-69784360747900956`（abf16c0） / main |
| 遅れ / 先行 | main より **31 behind / 1 ahead** |
| 変更ファイル | 1件: `tests/test_phase15_review_candidate_staging.py` に **+12行** |
| 競合 | merge-tree: **CLEAN**。現行 main に対しても差分は同じ +12行（3つの assert 追加）として適用できることを確認 |
| 差分の実質 | 監査時点の所見（「内容は main 未取込」）を再検証し、**現行 main にも未取込であることを確認**: (1) `source_inventory_path` の実在 assert、(2) plan_review 全レコードの source_url が盛岡市公式ドメインで始まる assert、(3) management_principles の完全一致 assert（現行 main は件数 `==5` のみ）。いずれも既存テストの強化であり、重複ではない |
| マージ後テスト（ローカル） | staging テスト **4 passed**（現行 main のベースラインも 4 passed。同テスト内の assert 追加のため件数は不変） |

- **推奨: マージ候補**。
- 前提条件: (a) GitHub CI（Quality）がグリーンであることの確認（本レポートでは未確認）、(b) マージ前にブランチを現行 main へ更新（update branch）して再検証すること。内容は小規模・テストのみ・本番コードとデータ正本に触れないため、12件の中で最もリスクが低い。

### PR #439 — Verify Akita City review candidate package（Jules）

| 項目 | 実測 |
|---|---|
| 作成者 / 作成日 | M-Osugi1230（Jules 自動作成） / 2026-10-18 |
| Draft | No |
| head | `jules-7868541196065694380-86cfa7bb`（fea3d1b） |
| 遅れ / 先行 | main より 30 behind / 1 ahead |
| 変更ファイル | **なし**。head コミット自体が自らの親に対しても**ファイル変更ゼロの空コミット**であることを `git show` で確認。現行 main との差分もゼロ |
| 競合 | なし（差分がないため merge-tree は main と同一ツリー） |

- **推奨: クローズ推奨**。
- 理由: 変更が一切存在せず、マージしても何も起きない。検証目的だった内容（秋田候補の staging テスト）は main に既存（`tests/test_phase15_akita_review_candidate_staging.py` が main に入り、監査・本棚卸しのテスト実行でも対象になっている）。残しておく価値はなく、棚卸しノイズになるだけである。

### PR #440 — Verify Akita City review candidate schema and non-inference rules（Jules）

| 項目 | 実測 |
|---|---|
| 作成者 / 作成日 | M-Osugi1230（Jules 自動作成） / 2026-10-18 |
| Draft | No |
| head | `verify-akita-review-candidate-staging-8059598169694436631`（06e4302） |
| 遅れ / 先行 | main より 30 behind / 1 ahead |
| 変更ファイル | **なし**（#439 と同様、空コミットであることを実測） |
| 競合 | なし |

- **推奨: クローズ推奨**。理由は #439 と同一。

---

## Dependabot PR（7件）

前提となる実測: **現行 main は全対象について PR の "from" バージョンのまま**である（checkout@v4、setup-python@v5、setup-node@v4、configure-pages@v5、deploy-pages@v4、pytest>=8.3,<9、web 依存は @types/node ^24 / eslint ^9 / typescript ^5.9）。つまり **7件すべて「main に追い越されて陳腐化」はしていない**。一方で各ブランチの base は古く（44〜1,258 behind）、ファイル単位の重なりは以下:

- `quality.yml` を共有: **#13（checkout）・#14（setup-python）・#15（setup-node）**
- `pages.yml` を共有: **#13（checkout）・#15（setup-node）・#28（configure-pages）・#29（deploy-pages）**

いずれも変更行は互いに異なる行であり、現行 main との merge-tree は全件 CLEAN。ただし同一ファイルを触るPR同士は、1件マージするごとに他PRの behind が増え、順次 branch 更新が必要になる。

### PR #13 — Bump actions/checkout 4→7

| 項目 | 実測 |
|---|---|
| 作成 | dependabot[bot] / 2026-07-14（head コミット 2026-07-25） |
| 遅れ / 先行 | **973 behind** / 1 ahead |
| 変更 | 5ファイル・6箇所の checkout@v4→v7（nationwide-coverage-smoke, pages, production-smoke, quality×2, verify-pages） |
| 競合 | merge-tree: CLEAN |
| 陳腐化 | なし（main は v4 のまま） |

- **推奨: 要ユーザー判断**。
- 論点: このPRが対象にするのは5ファイルのみだが、**現行 main には checkout@v4 の使用が16ファイル・17箇所**ある（Phase 10 系ワークフロー等はこのPRの作成後に増えた）。このPRだけをマージしても checkout のバージョンがリポジトリ内で混在する。選択肢は (a) このPRをマージし残りは Dependabot の再提案/追加PRで段階適用、(b) このPRを閉じて全ワークフロー一括更新の新規PRを作る、のいずれか。CI 基幹（quality.yml）を含むメジャーバージョン jump（v4→v7）でもあるため、適用順序と合わせて判断が要る。

### PR #14 — Bump actions/setup-python 5→6

| 項目 | 実測 |
|---|---|
| 作成 | dependabot[bot] / 2026-07-14 |
| 遅れ / 先行 | 1,258 behind / 1 ahead |
| 変更 | `quality.yml` の setup-python@v5→v6 の **1行のみ** |
| 競合 | merge-tree: CLEAN |
| 陳腐化 | なし |

- **推奨: マージ候補**。
- 前提条件: branch を現行 main へ更新し、Quality ワークフローがグリーンになること。変更が1行・対象が CI 用アクションのみで、Dependabot 7件の中で最も影響範囲が小さい。

### PR #15 — Bump actions/setup-node 4→7

| 項目 | 実測 |
|---|---|
| 作成 | dependabot[bot] / 2026-07-14 |
| 遅れ / 先行 | 1,255 behind / 1 ahead |
| 変更 | `pages.yml`・`quality.yml` の setup-node@v4→v7（2行） |
| 競合 | merge-tree: CLEAN |
| 陳腐化 | なし |

- **推奨: 保持**。
- 理由: setup-node は v7 で要求ランタイムが変わるメジャー jump であり、対象に**本番デプロイ経路の pages.yml** を含む。マージ自体は可能だが、pages 系（#28・#29）と合わせて「デプロイ経路の Actions をどの順序で上げるか」を決めてから1件ずつ公開検証（publication-status）で確認する進め方が安全。次アクション: #28・#29 とセットで適用順序を決める（要判断論点参照）。

### PR #16 — pytest requirement >=8.3,<9 → >=8.3,<10

| 項目 | 実測 |
|---|---|
| 作成 | dependabot[bot] / 2026-07-14（head 2026-10-06 に更新） |
| 遅れ / 先行 | 44 behind / 1 ahead |
| 変更 | `pyproject.toml` の pytest 制約 1行のみ |
| 競合 | merge-tree: CLEAN |
| 陳腐化 | なし |

- **推奨: マージ候補**。
- 根拠: 本棚卸しで pytest **9.2.0** を使い、Phase 15 staging 系テスト（現行 main のベースライン＋#437・#452・#454 のマージ後ツリー）を実行し**すべて passed** だった。pytest 9 系で少なくとも対象テスト群が動く実測がある。前提条件: マージ前に CI（test:py 全体）がグリーンであることの確認（本レポートのローカル実行は staging 系テストに限定され、全テストではない）。

### PR #17 — web-dependencies グループ 3件更新

| 項目 | 実測 |
|---|---|
| 作成 | dependabot[bot] / 2026-07-14（head 2026-10-06 に更新） |
| 遅れ / 先行 | 44 behind / 1 ahead |
| 変更 | `apps/web/package.json` の3件: **@types/node ^24.0.0→^26.6.4、eslint ^9.0.0→^10.12.0、typescript ^5.9.0→^7.0.2** |
| 競合 | merge-tree: CLEAN |
| 陳腐化 | なし（main は旧バージョンのまま） |

- **推奨: 要ユーザー判断**。
- 論点: 3件ともメジャー更新で、特に **TypeScript 7 と ESLint 10** は lint / typecheck / build の破壊的変更リスクが高い。リポジトリには pnpm-lock.yaml が無く（PR #456 作業時に実測）、解決バージョンの再現性も弱い。選択肢は (a) このPRを branch 更新のうえ CI（lint・typecheck・build）で検証してから判断、(b) 閉じて Dependabot に再提案させる/個別PRに分ける、のいずれか。棚卸し時点では未検証のため「マージ候補」にはしない。

### PR #28 — Bump actions/configure-pages 5→6

| 項目 | 実測 |
|---|---|
| 作成 | dependabot[bot] / 2026-07-14 |
| 遅れ / 先行 | 1,249 behind / 1 ahead |
| 変更 | `pages.yml` の configure-pages@v5→v6（1行） |
| 競合 | merge-tree: CLEAN |
| 陳腐化 | なし |

- **推奨: 保持**。理由: 本番デプロイ経路（pages.yml）専用のアクションであり、#29（deploy-pages）と対で、デプロイ→公開検証のサイクルに載せて1件ずつ確認すべきもの。次アクション: #15・#29 と合わせて適用順序を決め、適用後は publication-status.json の verified 更新で本番確認する。

### PR #29 — Bump actions/deploy-pages 4→5

| 項目 | 実測 |
|---|---|
| 作成 | dependabot[bot] / 2026-07-14 |
| 遅れ / 先行 | 1,249 behind / 1 ahead |
| 変更 | `pages.yml` の deploy-pages@v4→v5（1行） |
| 競合 | merge-tree: CLEAN |
| 陳腐化 | なし |

- **推奨: 保持**。理由・次アクションは #28 と同じ（デプロイ経路のため公開検証とセットで段階適用）。

---

## 要ユーザー判断の論点（集約）

1. **#439・#440 のクローズ実行**: 実質空であることは実測済み。クローズ操作自体はユーザーの処分判断（監査レポート (7)-8）。
2. **ADE 再開と #452・#454 の扱い**: scaffold を土台に prepared 化するか、ADE に作り直させるか。再開前に決めないと同一パスへの二重作成が起き得る。
3. **checkout v7 の適用範囲（#13）**: 5ファイルの部分適用か、全16ファイル一括か。
4. **デプロイ経路 Actions の適用順序（#15・#28・#29）**: pages.yml を触る3件をどの順で、公開検証を挟みながら適用するか。
5. **#17 のメジャー3件（TS 7 / ESLint 10 / @types/node 26）**: 検証付きで取り込むか、閉じて再提案させるか。

## 本棚卸しの制約

- 各PRの GitHub Actions CI 現行状態: **未確認**（connector の読み取り範囲外）。マージ候補3件はいずれも「CI グリーン確認」が前提条件。
- GitHub API の mergeable_state: **未確認**。競合判定はローカル merge-tree シミュレーションによる。
- ローカルテストは Phase 15 staging 系に限定し、全テストスイートは実行していない。pytest のバージョンも現行制約（<9）と異なる 9.2.0 で実施した参考値。
- 本レポートは棚卸しと推奨のみで、PR への書き込みは一切行っていない。

（作成: 2026-11-15、読み取り＋ローカル検証のみ）
