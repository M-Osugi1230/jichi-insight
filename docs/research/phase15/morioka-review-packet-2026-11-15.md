# 盛岡市（032018）人間レビュー支援パケット — Phase 15

作成日: 2026-11-15
対象: 盛岡市（自治体コード 032018、岩手県、中核市・県庁所在地）
キューの状態: `phase15_core_capital_review_queue.json` で sequence 5 / wave 1 / **唯一の `review_in_progress`**、`completion_path` は null、`next_official_code` も盛岡市。Phase 14 では `source_inventory_complete`。
位置づけ: 本パケットは人間レビューの準備資料であり、レビューそのものではない。候補データは prepared（機械準備済み）であり Reviewed ではない。

凡例: 「事実」はリポジトリ内ファイルまたは本パケット作成時の自動確認で確認できたこと。「未確認」は一次資料での照合がまだ済んでいないこと。数値の正しさの最終判断はレビュー担当（人間）が一次資料で行う。

---

## 1. 候補の概要

### 1.1 候補パッケージの構成（事実）

候補は `data/candidates/morioka-city/review_candidate.json`（status: `review_candidate`、package_state: `prepared`、human_review: required / **pending**、publication: **not eligible**）に格納され、次の要素を含む。

- 候補内蔵の source catalog（5件、全て HTML、後述の正本目録とは別物）
- plan_review（レコード4件、全て `needs_review` または `not_assessable`）
- policy_structure（総合計画基本構想の体系）
- progress_review（実施計画の枠組みのみ）
- fiscal_records（3件、全て `needs_review`、confidence: medium）
- evidence_packets（3件、全て `needs_review`、うち1件に open question あり）

正本資料目録 `data/catalog/morioka_phase15_sources.json` は別途存在する（6件、うち PDF 2件。ファイル内には `reviewed_at: 2026-10-01` と記録されているが、キューは `review_in_progress` のままであり、候補の human_review も pending である。この `reviewed_at` の記録が何を意味するかは**未確認**）。

### 1.2 候補が主張する内容（一次資料未照合の候補値）

| 項目 | 候補の主張 | 段階・状態 |
|---|---|---|
| 現行計画 | 盛岡市総合計画基本構想、計画期間 2025年度〜2034年度（令和7〜16年度）の10年計画 | current plan identity（needs_review） |
| 将来像 | 「輝きが増し 活力に満ち 夢をかなえるまち盛岡」 | needs_review |
| 政策体系 | 4つの基本目標と25の施策（候補内の内訳は 6＋6＋6＋7＝25施策）、自治体経営の理念5つ | needs_review |
| 実施計画 | 3年間の実施計画を毎年度ローリング。現行版は令和8〜10年度（2026〜2028年度） | 進行管理構造として needs_review |
| FY2026 当初予算 | 一般会計 **110,000,000,000円**（候補内蔵目録の概要ページ由来） | **当初予算「案」段階**として記録、needs_review |
| FY2024 決算・歳入 | 一般会計収入済額 **120,000,000,000円** | needs_review |
| FY2024 決算・歳出 | 一般会計支出済額 **117,000,000,000円** | needs_review |
| FY2024 決算と個別実施計画事業の接続 | 完全細粒度接続は未判定 | **not_assessable**（候補の判断として明示済み） |

根拠資料として候補・目録が挙げるのは、盛岡市公式サイトの総合計画ページ、実施計画ページ、令和8年度予算の概要ページ、同当初予算案の概要 PDF、令和8年第1回市議会定例会の議決結果ページ、令和6年度決算ページ、令和6年度歳入歳出決算審査意見書 PDF（詳細は第5節）。

### 1.3 候補と正本目録の間の不一致（最重要・事実として確認済み）

候補の財政数値3件すべてが、正本目録 `morioka_phase15_sources.json` に locator 付きで記録された値と**一致しない**。どちらが正しいかは未確認であり、一次資料での突合がレビューの最優先事項になる。

| 項目 | 候補の値 | 正本目録が一次資料の値として記録する値 | 目録側の locator |
|---|---|---|---|
| FY2026 一般会計当初予算 | 110,000,000,000円 | **118,500,000千円（＝118,500,000,000円）** | 『令和8年度 当初予算案の概要』PDF p.3 / printed p.1『1 予算規模』 |
| FY2024 一般会計歳入 | 120,000,000,000円 | **124,850,210千円（＝124,850,210,000円）** | 『令和6年度 盛岡市歳入歳出決算審査意見書』PDF p.10 / printed p.4 |
| FY2024 一般会計歳出 | 117,000,000,000円 | **121,320,150千円（＝121,320,150,000円）** | 同上 |

- 候補の決算2値は 1,200億・1,170億という切りのよい概数であり、完了4市が守った「監査資料の exact source precision を保持する」基準（例: 函館市は円単位 144,921,264,078円まで保持）を満たしていない。
- 段階の扱いも食い違う。候補は FY2026 予算を「当初予算（案）」段階として記録するが、正本目録には議決結果（令和8年第1回定例会・議案第1号『令和8年度盛岡市一般会計予算』原案可決）が証拠として含まれ、Phase 14 の source inventory も同予算を「成立済みFY2026当初予算」と記述している。完了市のうち青森市・八戸市は `budget_enactment_state_preserved` を quality gate に含めており、盛岡でも議決済みであることの記録方法を決める必要がある（函館市は証拠パッケージに議決資料を含めず「予算案」のまま完了しているため、必須かどうかは盛岡のパッケージ宣言次第。ただし盛岡は議決資料が既に目録にある以上、「案」のまま記録すると状態の記録として不正確になる）。
- 候補の fiscal_records が参照する source ID は候補内蔵目録の ID（`morioka-budget-2026`、`morioka-settlement-2024`）であり、正本目録の ID（金額の根拠は `morioka-budget-2026-pdf`、決算は `morioka-settlement-2024-audit-pdf`）とは対応していない。完了市では reviewed な fiscal_records は正本目録の ID を参照している（例: 函館 `hakodate-budget-2026-pdf`）。

---

## 2. レビューで確認すべき項目のチェックリスト

完了4市（函館・旭川・青森・八戸）の completion ファイルの quality_gate と、`docs/PHASE15_CORE_CAPITAL_REVIEW.md` の Required review layers（10層）・Completion contract を盛岡に当てはめたもの。各項目は一次資料（公式ページ・PDF）を開いて確認する。

### A. 現行計画（Promise の土台）

- [ ] 総合計画基本構想が現行計画であり、計画期間が 2025年度〜2034年度であることを公式ページ本文で確認する
- [ ] 将来像「輝きが増し 活力に満ち 夢をかなえるまち盛岡」の原文表記を確認する
- [ ] 4つの基本目標と25施策の名称・数が公式資料と一致することを確認する（名称の転記ミス、施策の欠落・重複がないか）
- [ ] 自治体経営の理念5つの名称を確認する
- [ ] 前計画との境界（現行計画が初年度であること、前計画の実績を現行計画の実績として扱っていないこと）を記録できるか確認する ※候補には transition のレコードが無い（第3節参照）

### B. 実施計画・進行管理（Action / Result の土台）

- [ ] 実施計画の現行版が「令和8年度〜令和10年度」版であることを公式ページで確認する（改訂版が出ていないかを含む）
- [ ] 3年ローリングの進行管理構造が公式資料の記述どおりか確認する
- [ ] 実施計画の進行管理・評価の仕組み（評価の主体、公表方法、行政評価との関係）を示す公式資料を特定する ※候補・目録のどちらにも該当 source が無い（第3節参照）。完了4市は全て評価制度・進行レビューの証拠をパッケージに含めている

### C. 予算（Money）

- [ ] FY2026 一般会計当初予算の金額を一次資料で確定する（候補 110,000,000,000円 と目録 118,500,000千円の不一致を解消する）
- [ ] 金額の source precision（千円単位）を保持した形で記録する
- [ ] 段階を確定する: 議案第1号の原案可決（議決結果ページ）を確認し、「案」ではなく議決済み当初予算として記録する方法を決める
- [ ] 当初予算と補正予算を別 state として扱う境界を維持する
- [ ] 候補の evidence packet に残る open question「正式な議決予算書および審査意見書との最終数値突合」を解消する

### D. 決算（Result / Accountability）

- [ ] FY2024 一般会計歳入・歳出を決算審査意見書の exact 値で確定する（目録記録: 歳入 124,850,210千円・歳出 121,320,150千円。候補の概数 1,200億・1,170億は採用しない）
- [ ] 監査資料（決算審査意見書）が証拠であることを記録し、決算概要ページの概数表示と混同しない
- [ ] FY2024 決算と個別実施計画事業の接続は `not_assessable` のまま維持することを確認する（完了4市でも個別事業接続は deferred であり、v1 完了の障害にはならない）

### E. 証拠・運用面

- [ ] 第5節の公式URLの生存を実ブラウザで再確認する（特に財政・議会系。自動確認で 404 だったものは現行URLを再特定し、目録を更新する）
- [ ] 全レコードに record-level の evidence locator（ページ名・PDFページ番号・見出し）があることを確認する
- [ ] fiscal_records の source 参照を正本目録の ID に付け替える
- [ ] 政策達成度の独自スコア化、因果認定、他都市比較・ランキングへの変換が含まれていないことを確認する（候補の quality_boundaries はこの点は明示済み）

---

## 3. 不足・未確認の項目と、そのままでは昇格できない理由

### 3.1 ファイル・パッケージの不足（事実）

完了4市の completion が参照する reviewed パッケージ一式のうち、盛岡には次が**存在しない**。

| 完了4市の必須パッケージ | 盛岡の状態 |
|---|---|
| official source catalog（`data/catalog/*_phase15_sources.json`） | **あり**（6件） |
| plan review（`data/reviewed/*-city/plan_review.json`、review_status: reviewed、各レコード decision: accepted 等） | **なし**。候補内 staging のみ（全レコード needs_review / not_assessable） |
| policy structure（`data/catalog/*_current_policy_structure.json`） | **なし**。候補内 staging のみ |
| progress review summary（`data/catalog/*_current_progress_review_summary.json`） | **なし**。候補内は実施計画の枠組みのみ |
| fiscal records（`data/reviewed/*-city/fiscal_records.json`、review_status: reviewed、confidence: high） | **なし**。候補内 staging のみ（needs_review / medium） |
| fiscal evidence packets（`data/reviewed/*-city/evidence_packets.json`） | **なし**。候補内 staging のみ（open question 未解消） |
| municipality（`data/reviewed/*-city/municipality.json`） | **なし**（`data/reviewed/morioka-city/` ディレクトリ自体が無い） |
| completion（`data/catalog/*_phase15_completion.json`、quality_gate・counts・deferred_depth・completion_boundary） | **なし** |

`docs/PHASE15_CORE_CAPITAL_REVIEW.md` の Completion contract は上記パッケージを必須としており、現状のままでは契約を満たさない。キューのテスト（`tests/test_morioka_phase15_review.py`）も現状は「候補が staging のまま昇格していないこと」を検証する内容であり、昇格時には reviewed 側の検証への更新が必要になる。

### 3.2 内容面の不足・未確認

1. **財政数値の不一致（未解消）**: 第1.3節のとおり、候補の3値が正本目録の値と食い違う。どちらが正しいか未確認。この状態で昇格すると、誤った可能性のある数値を Reviewed として公開することになる。
2. **公式URLの到達性（要再確認）**: 本パケット作成時の自動確認（2026-11-15、curl とページ取得の2手法）では、財政・議会系のURLが 404 だった（第5節）。計画系ページは到達できたため、サイト側の一律な bot 制限とは考えにくいが、自動確認の 404 が「資料の消滅」を断定するものではない。レビュー時に実ブラウザでの再確認と、必要に応じた現行URLの再特定が必須。到達できないURLは stable evidence locator として使えない。
3. **進行管理・評価の証拠が無い**: 正本目録の6件には、実施計画の評価・進行レビューや行政評価にあたる source が無い（完了4市は全て `implementation_and_evaluation_design`、`annual_progress`、`latest_completed_annual_progress` 等の role を持つ source を含む）。Required review layers の第4層「available progress / KPI / evaluation evidence」に相当する確認が未了。
4. **計画 transition の記録が無い**: 候補の plan_review 4レコードは「期間」「政策体系」「ローリング構造」「決算接続 not_assessable」のみで、前計画との境界や現行計画の位置づけ（初年度）のレコードが無い。完了4市は次期計画 draft や移行を明示的にレコード化している。盛岡の現行計画は 2025年度開始のため次期計画 draft は存在しないはずだが、前計画との境界の扱いは**未確認**であり、記録の要否をレビューで判断する必要がある。
5. **候補内蔵目録と正本目録の二重管理**: 候補は独自の source catalog（5件・全HTML・PDF なし・議決資料なし）を内蔵し、正本目録（6件）と ID 体系も異なる。昇格時は正本目録を唯一の catalog とし、候補内蔵目録は reviewed パッケージに持ち込まない整理が必要。
6. **human_review が pending**: 候補の `human_review.status` は pending、`reviewed_at`・`reviewer_note` は null。当然ながら、この記録が人間による一次資料確認の後に埋まらない限り昇格できない。

### 3.3 昇格の障害にならないもの（完了4市の方式で確認済み）

次は未完了でも v1 の `reviewed_complete` を妨げない。完了4市はいずれもこれらを `deferred_depth` として明示したうえで完了している。

- 実施計画の個別事業・指標の全件 identity と実績の接続
- FY2024 決算と個別事業費の細粒度接続（盛岡候補は not_assessable として既に適切に保持）
- 補正予算・執行・契約・補助金への接続
- 施策と事業・KPI の細粒度 linkage（名称類似だけで接続しない）
- 政策効果の因果認定、他都市比較可能性、ランキング化（そもそも行わない）

---

## 4. 昇格の判断手順

盛岡を `reviewed_complete` と記録できるのは、次の手順をすべて終えた時点である（`docs/PHASE15_CORE_CAPITAL_REVIEW.md` の Completion contract と完了4市の実績に基づく）。

1. **証拠の到達性を回復する**: 第5節のURLを実ブラウザで再確認する。404 のものは盛岡市公式サイト内で現行の公式URLを再特定し、正本目録 `morioka_phase15_sources.json` の URL と locator を更新する。到達できない資料に基づくレコードは、その時点で昇格対象から外すか、到達可能な一次資料に差し替える。
2. **財政数値を一次資料で確定する**: 当初予算案の概要 PDF（または現行の予算資料）で FY2026 一般会計当初予算額を確認し、議決結果で原案可決を確認する。決算審査意見書で FY2024 歳入・歳出の exact 値を確認する。第1.3節の不一致はここで解消し、候補の概数は破棄する。
3. **計画・体系・実施計画を一次資料で照合する**: 第2節 A・B のチェックを終え、plan_review の各レコードの decision を人間が accepted（または根拠付きで not_assessable）に更新できる状態にする。評価・進行管理の証拠（3.2-3）もこの段階で特定する。
4. **reviewed パッケージを作成する**: `data/reviewed/morioka-city/` に municipality.json、plan_review.json、fiscal_records.json、evidence_packets.json を、`data/catalog/` に morioka_current_policy_structure.json、morioka_current_progress_review_summary.json を作成する。fiscal_records は review_status: reviewed、source は正本目録の ID を参照し、金額は source precision を保持する。
5. **completion を作成する**: `data/catalog/morioka_phase15_completion.json` に、完了4市と同形式で quality_gate（全項目 true）、counts、deferred_depth（第3.3節の項目）、completion_boundary（何をレビュー済みとし、何を deferred とするかの文章）を記録する。スキーマは `schemas/phase15_municipality_completion.schema.json`。
6. **検証を通す**: スキーマ検証と回帰テスト（`tests/test_morioka_phase15_review.py` の昇格版、`tests/test_phase15_core_capital_review_queue.py`、`tests/test_phase15_queue_consistency.py` 等）を通過させる。quality gate には `regression_suite_required_before_merge` が含まれる。
7. **キューを更新し、人間が承認する**: キューの盛岡エントリを status: `reviewed_complete` にし、`completion_path` に completion ファイルを設定する。候補の human_review に reviewed_at と reviewer_note を記録する。変更はブランチ＋PR で行い、公開対象に含める判断は人間（所有者）が行う。

判断基準の一文: **「宣言した v1 パッケージの範囲内で、主張する全レコードが、到達可能な公式一次資料と record-level locator を持ち、人間が照合済みであること」**。この基準を満たさないレコードが残る場合は、その部分を deferred または not_assessable として明示すれば全体の昇格は可能だが、数値の不一致や証拠URLの不達を抱えたままの昇格はできない。

---

## 5. 参照したファイルと公式URLの一覧

### 5.1 リポジトリ内ファイル（origin/main 時点で確認）

候補・正本（盛岡）:

- `data/candidates/morioka-city/review_candidate.json`
- `data/catalog/morioka_phase15_sources.json`
- `data/catalog/phase15_core_capital_review_queue.json`（盛岡エントリ: sequence 5、review_in_progress、completion_path: null）
- `data/indexed/morioka-city/source_inventory.json`（Phase 14、source_inventory_complete）

完了4市の基準:

- `data/catalog/hakodate_phase15_completion.json` / `hakodate_phase15_sources.json` / `data/reviewed/hakodate-city/fiscal_records.json` / `plan_review.json`
- `data/catalog/asahikawa_phase15_completion.json` / `asahikawa_phase15_sources.json`
- `data/catalog/aomori_phase15_completion.json` / `aomori_phase15_sources.json`
- `data/catalog/hachinohe_phase15_completion.json` / `hachinohe_phase15_sources.json`

手続き・スキーマ・テスト:

- `docs/PHASE15_CORE_CAPITAL_REVIEW.md`（Required review layers、Non-inference gates、Completion contract）
- `schemas/phase15_municipality_completion.schema.json`
- `tests/test_morioka_phase15_review.py`（現行は staging 契約の検証）

### 5.2 公式URLと生存確認結果（2026-11-15、本パケット作成時の自動確認）

確認方法: curl による HTTP ステータス確認と、ページ取得ツールによる取得の2手法。自動確認の結果であり、特に 404 は「現時点でこのURLでは到達できなかった」ことを示すに留まる（実ブラウザでの最終確認はレビュー時に必要）。

| URL | 用途 | 結果 |
|---|---|---|
| https://www.city.morioka.iwate.jp/shisei/keikaku/sogotekiplan/1009760/index.html | 総合計画の入口（正本目録・Phase 14 inventory） | 到達可（200） |
| https://www.city.morioka.iwate.jp/shisei/keikaku/sogotekiplan/1009760/1045034/1051240.html | 基本構想（候補・目録） | 到達可（200） |
| https://www.city.morioka.iwate.jp/shisei/keikaku/sogotekiplan/1009760/1045034/1051241.html | 実施計画（候補・目録） | 判定保留: curl では 404、ページ取得では 2026-08-08 時点のキャッシュ内容が返り、現行版「実施計画（令和8年度から令和10年度）」の掲載がその時点では確認できた。現在の生存は**未確認** |
| https://www.city.morioka.iwate.jp/shisei/zaisei/suii/1054620/1056173.html | 令和8年度予算の概要（候補・目録・inventory） | **404（2手法とも）** |
| https://www.city.morioka.iwate.jp/_res/projects/default_project/_page_/001/056/173/r8_tousho_gaiyou.pdf | 令和8年度 当初予算案の概要 PDF（目録。金額 118,500,000千円の根拠） | **404（curl）** ※ページ取得は未実施 |
| https://www.city.morioka.iwate.jp/gikai/giko/1008123/1056301.html | 令和8年第1回定例会 議決結果（目録。原案可決の根拠） | **404（2手法とも）** |
| https://www.city.morioka.iwate.jp/shisei/zaisei/1010723/1054397/index.html | 令和6年度決算（候補） | **404（2手法とも）** |
| https://www.city.morioka.iwate.jp/_res/projects/default_project/_page_/001/054/397/r6_kessan_shinsa.pdf | 令和6年度 決算審査意見書 PDF（目録。決算 exact 値の根拠） | **404（curl）** ※ページ取得は未実施 |

所見（推測を含む）: 計画系（shisei/keikaku）のページは到達でき、財政系（shisei/zaisei）・議会系（gikai）のページと PDF が軒並み到達できない。市のサイト再編やページ移転の可能性が高いが、原因は**未確認**。いずれにせよ、財政系の証拠 locator は現状のままでは使えない可能性が高く、第4節の手順1（現行URLの再特定）がレビュー着手の前提になる。
