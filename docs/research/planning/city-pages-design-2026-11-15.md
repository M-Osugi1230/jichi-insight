# Phase 15 レビュー済み市ページ 設計書（2026-11-15）

対象: Jichi Insight（M-Osugi1230/jichi-insight、apps/web、Next.js 静的エクスポート → GitHub Pages）
状態: 設計のみ（未実装）。調査は promote-kawaguchi-work ワークツリー（main 相当・14/67 時点）で実施。

## 1. 目的

Phase 15 で reviewed_complete になった14市について、reviewed パッケージから読みやすい市別ページを生成し、/review-progress の行（現在は GitHub の生 JSON へのリンクのみ）からリンクする。表示するのは Promise（計画の枠組み）・Money（FY2026 成立予算＋FY2024 決算、出典と精度を明記）・接続判定（not_assessable を正直に表示）・出典リンクに限る。ランキング・スコア・他市比較はしない。

## 2. 調査結果

### 2.1 reviewed パッケージの構造（14市で均一）

各市は `data/reviewed/<slug>-city/` に4ファイルを持つ（slug = hakodate, asahikawa, aomori, hachinohe, morioka, akita, yamagata, fukushima, koriyama, utsunomiya, maebashi, takasaki, kawagoe, kawaguchi）。

| ファイル | 形式 | 主なフィールド |
|---|---|---|
| municipality.json | object | id（`jp-local-<code>`）, official_code, name_ja, municipality_type, prefecture_name_ja, official_url, data_status（`"reviewed"`）, fiscal_years（[2024, 2026]）, last_verified_at, sources（出典ID配列） |
| plan_review.json | object | review_status（`"reviewed"`）, reviewed_at, records[], quality_boundary（英語）, next_action |
| fiscal_records.json | array（全市ちょうど3件） | id, fiscal_year, account_type（general）, stage, metric, metric_label（日本語）, amount_yen, value_status, period_start/end, note（日本語の来歴・精度説明）, review_status, confidence, sources（出典ID配列） |
| evidence_packets.json | array（3件、財政レコードと1対1） | subject_id（財政レコードIDと一致）, claims[]（field, statement, source_ids, location_note, decision, review_note）, open_questions[] |

plan_review.records[] の各レコード: evidence_role, title, statement, value/unit（任意）, source_url（**全14市・全レコードに存在**）, evidence_location, decision（`accepted` / `not_assessable`）, review_note。レコード数は市により4〜6件で、evidence_role の構成も市により異なる（current_plan_identity と policy_structure は全市に存在。implementation_layer / progress_governance / plan_transition / annual_progress は市により有無が異なる）。

カタログ側（`data/catalog/`）:
- `<city>_phase15_completion.json` — status `"reviewed_complete"`, completed_at, review_package（source_catalog_path / plan_review_path / policy_structure_path / progress_review_path / fiscal_records_path / fiscal_evidence_path / counts）, quality_gate, deferred_depth[]（id, status, boundary）, completion_boundary（日本語）。
- `<city>_phase15_sources.json` — sources[]: id, title, official_url, format, evidence_role, evidence_location, use_boundary。財政レコードや municipality.json が参照する出典IDはここで URL に解決できる。**例外: `<city>-city-home` というIDは出典カタログに無く、municipality.official_url を指す**（実装で特別扱いが必要）。

### 2.2 財政レコードの均一性と精度

- 全14市とも財政は3件で固定: FY2026 initial_budget / total_expenditure、FY2024 settlement / total_revenue、FY2024 settlement / total_expenditure。全件 value_status = available、amount_yen は非 null、review_status = reviewed。
- **精度は機械可読フィールドに無い。** amount_yen は常に円換算の整数だが、宇都宮・高崎のように千円精度の出典では末尾が 000 になり、精度の説明は note の散文にのみ書かれている（例: 宇都宮「第1表（単位：千円）…円単位の総額は公式要約文書に印字されていない」）。→ 金額表示には必ず当該レコードの note を併記し、円単位の正確さが保証される見せ方（例: 億円への丸め換算を単独で大きく出す）をしない。
- 成立性の来歴（議案番号・議決日・認定日）も note と evidence claim の statement に含まれる。stage = initial_budget だが note が「成立予算として保持」と明記しているため、表示ラベルは note の記述に従い「当初予算（成立）」とする。

### 2.3 初期4市と後期10市の差異（重要）

- 後期10市（盛岡以降）: plan_review に annual_progress ロールのレコードがあり、decision = `not_assessable`（FY2024決算と個別実施計画事業の接続は未判定、という明示レコード）。
- 初期4市（函館・旭川・青森・八戸）: 全レコード decision = accepted。annual_progress 系レコードは「年次評価資料が公表されている」ことの確認であり、**決算と計画の接続判定レコードは存在しない**。
- → 「接続」セクションは decision フィールド駆動で描画し、not_assessable レコードが無い市では completion の deferred_depth / completion_boundary の文言で「v1 では接続を確立していない」ことを示す。初期4市について「接続は not_assessable と判定された」と書いてはいけない（判定自体が無い）。
- 函館には plan_transition レコード（次期基本構想は素案・パブコメ中）がある。現行計画と混同されないよう分離表示する。

### 2.4 政策構造 JSON は市ごとにスキーマが異なる

`data/catalog/<city>_current_policy_structure.json` は市ごとに形が違う（盛岡: current_plan.basic_goals[{name_ja, measures[]}]＋management_principles／川口: current_plan.components[]＋structure 散文。completion の counts のキー名も basic_goals と current_plan_basic_goals で揺れる）。
→ **v1 では政策構造 JSON の深部（目標・施策の一覧）は描画しない。** Promise セクションは plan_review の policy_structure レコード（statement＋出典リンク）で担い、構造の詳細は GitHub 上の正本へのリンクで案内する。全市共通スキーマへの正規化は将来課題。

### 2.5 Web 側の既存パターン

- データ読込は2方式が既存:
  1. JSON の静的 import（`lib/phase15Progress.ts`, `lib/catalog.ts`, `lib/reviewedCoverage.ts`）— `../../../data/...` への相対 import、resolveJsonModule 有効。
  2. fs 読込（`lib/phase9Targets.ts`）— `findDataRoot()` で repo ルートの data/ を解決し、slug 単位で遅延読込。動的ルートの唯一の前例。
- 動的ルートの前例は `app/municipalities/phase9/[slug]/page.tsx` のみ: `dynamic = "force-static"`、`dynamicParams = false`、`generateStaticParams()`、`generateMetadata()`、notFound() フォールバック。
- `lib/phase15Progress.ts` はモジュール読込時にキューの整合性を検証し、不一致なら throw してビルドを落とす（fail-closed）。市ページ側もこの流儀に合わせる。
- /review-progress は `phase15Progress.municipalities` を描画し、reviewed_complete の行には GitHub の completion JSON へのリンクのみがある。キュー項目には slug フィールドが無いが、completion_path のファイル名（`<city>_phase15_completion.json`）と reviewed ディレクトリ名（`<city>-city`）が全14市で規則的に対応する。
- sitemap（`app/sitemap.ts`）は静的ルート配列＋ phase9 のように lib から動的ルートを合成する方式。

### 2.6 ビルドへの可用性と .gitignore の注意

- `.gitignore` に `data/reviewed/` があるが、Phase 15 の56ファイル（14市×4）は force-add で追跡済み（git ls-files で確認）。CI のチェックアウトにも含まれるためビルドで読める。
- ただし `data/reviewed/` には他フェーズの政令市パッケージ（fukuoka-city 等、3ファイルのみで plan_review が無い別形状）も混在する。**ページ生成の対象はディレクトリスキャンではなく、必ず Phase 15 キューの reviewed_complete 項目＋completion レコードから駆動する。**
- 将来の新規 reviewed パッケージが force-add し忘れると CI でファイルが欠落する。ローダーは「キューで reviewed_complete なのにファイルが無い」場合に throw してビルドを落とすことで検出する（fail-closed）。

## 3. 提案

### 3.1 URL 方式

**推奨: `/municipalities/<slug>`**（slug は reviewed ディレクトリ名、例: `/municipalities/morioka-city`）

- 既存の /municipalities/fukuoka-city、/municipalities/kitakyushu-city と同じ名前空間・命名規則で、利用者が推測しやすい。
- 既存の静的セグメント（aichi, fukuoka-city, hiroshima, hokkaido, kagawa, kitakyushu-city, miyagi, okinawa, osaka, tokyo, phase9, phase10 等）と衝突しないことを確認済み。Next.js では静的セグメントが動的セグメントに優先するため共存可能。
- 代替案: `/municipalities/phase15/<slug>`（phase9/phase10 の前例に倣う）。内部工程名が URL に出る点と、将来その市に専用ページを作る際の移行コストを考えると第一推奨はしない。最終判断はオーナー確認事項。

### 3.2 ページ構成（セクションとデータ対応）

1. **ヘッダー / 概要**
   - name_ja、prefecture_name_ja（municipality.json）、公式サイトへのリンク（official_url）
   - 「一次資料レビュー完了」バッジ＋ reviewed_at（plan_review）／ last_verified_at（municipality）
   - completion へのリンク（GitHub の完了記録 JSON）と /review-progress への戻りリンク
   - completion_boundary の要旨（このレビューが主張する範囲）
2. **Promise — 計画の枠組み**（plan_review.records から role で振り分け）
   - current_plan_identity / policy_structure / implementation_layer / progress_governance のレコードを、title・statement・（あれば value）・出典リンク（source_url＋evidence_location）で表示。review_note は details で展開
   - plan_transition レコードは「計画の移行・次期計画の動向（現行計画ではない）」と明示した別ブロックに分離
3. **Money — 予算と決算**（fiscal_records 3件）
   - 各レコード: metric_label、年度＋段階ラベル（FY2026 当初予算（成立）／FY2024 決算 歳入・歳出）、amount_yen（桁区切り円表示）、対象期間、**note を全文併記**（精度・議案・議決の来歴を含む）、出典リンク（sources のIDを出典カタログで解決し title＋official_url を表示。`<city>-city-home` は official_url に解決）
   - 対応する evidence packet の claim（statement / location_note）を details で展開可能にする（phase9 の recordCard パターン踏襲）。open_questions があれば「未確認の残件」として明示
   - 金額の並び替え・他市との比較表示は一切しない
4. **接続の判定 — 計画と決算のつながり**
   - decision = not_assessable のレコードがあれば、それを主役に表示: バッジ「判定不能（not_assessable）」＋ statement ＋ review_note
   - 無い市（初期4市）では completion.deferred_depth のうち fiscal-detail-and-amendment-linkage 等の boundary と completion_boundary を表示し、「v1 レビューでは個別事業・実績への接続を確立していない」と明記（判定があったかのような表現はしない）
   - あわせて deferred_depth 全件を「このレビューに含まれないもの」として一覧表示
5. **出典一覧**（`<city>_phase15_sources.json` の sources 全件）
   - title、format、evidence_role、evidence_location、use_boundary、official_url へのリンク
6. **境界と訂正導線（フッター）**
   - plan_review.quality_boundary と completion.completion_boundary を全文表示
   - /methodology、/corrections へのリンク、GitHub 上の正本（パッケージ4ファイル＋completion）へのリンク

### 3.3 not_assessable と精度の描画ルール

- decision が accepted でないレコードは、accepted のレコードと視覚的に区別する（バッジ＋文面をそのまま出す）。decision の値を言い換えて表示しない。
- 金額は amount_yen をそのまま桁区切り表示し、必ず同じカード内に note を置く。千円精度の市では note がそれを説明する。億円換算などの二次加工値は出さない（出す場合も note 併記が前提だが、v1 では出さない）。
- value_status が available でない財政レコードが将来現れたら、金額の代わりに状態を表示し 0 や概数で埋めない（現14市では全件 available）。

### 3.4 リンク導線

- /review-progress: reviewed_complete の行に市ページへの内部リンク（「市のページを見る」）を主リンクとして追加し、GitHub リンク（公式資料の索引・レビュー完了記録）は従リンクとして残す。slug は phase15Progress のモデルに completion_path から導出して追加（ファイル名規則 `<city>_phase15_completion.json` → `<city>-city`）。導出規則は新しい lib 側で「対応する reviewed ディレクトリと completion が実在すること」を検証して担保する。
- /municipalities: 既存のキュレーション型インデックスに「Phase 15 詳細レビュー済みの市」セクションを追加し、同じ lib から14市へのリンクをデータ駆動で出す（手書きリストで二重管理しない）。
- sitemap: phase9Routes と同様に lib から市ページのルートを合成して追加。

### 3.5 実装ステップ（最小構成）

1. `apps/web/lib/phase15Cities.ts`（新規）— phase9Targets と同じ fs 方式で data ルートを解決。キュー（reviewed_complete のみ）→ completion → パッケージ4ファイル＋出典カタログを読み、ページ用モデルを返す。整合性チェック（queue の status、completion.status、municipality.data_status、plan_review.review_status がすべて reviewed 系であること／ファイル欠落）を満たさなければ throw。
2. `apps/web/app/municipalities/[slug]/page.tsx`（新規）＋ `page.module.css` — phase9/[slug] の作法（force-static / dynamicParams=false / generateStaticParams / generateMetadata）に倣う。共通部品は既存の PageIntro / SiteHeader / SiteFooter / StatusBadge を再利用。
3. `apps/web/lib/phase15Progress.ts`（変更）— municipalities の各項目に slug を追加（completion_path から導出）。
4. `apps/web/app/review-progress/page.tsx`（変更）— reviewed_complete 行に市ページへの Link を追加。
5. `apps/web/app/municipalities/page.tsx`（変更）— レビュー済み市セクションを追加。
6. `apps/web/app/sitemap.ts`（変更）— 市ページのルートを追加。
7. テスト（新規）`tests/test_phase15_city_pages_web_contract.py` — 既存の *_web_contract.py の流儀で、(a) キューの reviewed_complete 全市について slug とパッケージの実在、(b) ページ／lib のソースに必須の境界文言（not_assessable の扱い、ランキングをしない旨）が含まれること、(c) review-progress と sitemap が市ページを参照すること、を検証。あわせて `tests/test_phase15_public_progress.py` の期待を市ページリンク分だけ拡張。

### 3.6 検証観点（実装時に確認すべきこと）

- ビルド（next build）が14ページを静的生成し、生成 HTML に金額・note・出典 URL・not_assessable バッジが含まれること。
- pytest 全件（特に test_phase15_* 群と新規 web contract）が通ること。
- 本番反映は publication-status と実ページで確認（従来どおり配信キャッシュの遅延に注意）。

## 4. リスク

| リスク | 内容 | 対策 |
|---|---|---|
| 未レビュー情報の混入 | data/reviewed には他フェーズの別形状パッケージも存在。ディレクトリスキャンで生成すると未検証データを Reviewed と誤表示しかねない | 対象はキュー＋completion 駆動に限定し、状態不一致は throw |
| .gitignore の罠 | data/reviewed/ は gitignore 対象で、現14市は force-add 済み。将来分が未追加だと CI で欠落 | ローダーの fail-closed で検出。運用手順に force-add を明記 |
| 精度の誤読 | 千円精度の金額が円単位の確定値に見える | note 全文を金額と同一カードに併記。換算値・丸め表示をしない |
| 接続判定の誤表現 | 初期4市には not_assessable レコードが無いのに「判定不能」と断定すると虚偽表示になる | decision 駆動の描画＋deferred_depth の境界文言で代替し、判定の有無を区別 |
| スキーマの揺れ | 政策構造 JSON と counts のキーが市ごとに異なる | v1 では深部構造を描画せず、plan_review の statement と正本リンクで代替 |
| ビルドサイズ | 静的 import 方式だと全市の JSON がバンドルされる | fs 読込方式（phase9 前例）を採用。生成物は14ページの静的 HTML のみで増分は軽微 |
| URL の将来衝突 | 将来、特定市に専用ページを作る場合に [slug] と競合しうる | 静的セグメント優先のため技術的衝突はないが、移行時はリダイレクト方針を別途決める |

## 5. ブロッカー・未決事項

- ハードなブロッカーは無し。データ・読込方式・ルーティングすべてに既存の前例と材料が揃っている。
- オーナー判断が要る点は1件のみ: URL を `/municipalities/<slug>`（推奨）にするか `/municipalities/phase15/<slug>` にするか。
- 任意の将来課題: 政策構造 JSON の共通スキーマ化（目標・施策一覧の描画はその後）、progress_review サマリ（年次評価）の扱い。
