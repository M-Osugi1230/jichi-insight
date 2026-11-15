# Public release checklist

最終更新: 2026-11-15

このチェックリストは、実装の有無ではなく、公開判断に必要な証跡がリポジトリ上で確認できるかを基準に管理します。

- `[x]` 証跡確認済み
- `[ ]` 未完了または最終確認未実施

## Current release position

- 公開状態: **正式公開（Public release）**（2026-11-15、公開責任者・大杉邑大が正式公開への移行を承認。同日に正式Public betaへの移行（公開責任者・大杉邑大が正式Public betaへの移行を承認）を経ており、本変更のマージとデプロイをもって表記を切り替える）。GitHub Pagesで公開済み
- 直近の公開検証: 2026-11-15 success（`.github/publication-status.json`、deployed_commit_sha `95f972fa`）
- Phase 11: 全国47都道府県・15,327個票を共通Schemaで正規化／公式一次資料上の最大到達深度まで完了
- Phase 13: 政令指定都市20/20のv1 record-review foundation完了（うち2市はReviewed reference）
- Phase 14: 中核市・県庁所在地67/67の公式Source Inventory完了
- Phase 15: 15/67自治体 reviewed_complete、52自治体 pending_record_review（正本キューの更新日は2026-11-15）
- 各Phaseの`complete`は全政策・予算・事業・契約・実績の完全な接続や全国比較可能性を保証しない
- Public beta移行時点で未実施の事項は、外部法務確認、外部の中立性・方法論レビュー、実機・キーボード・スクリーンリーダー監査、初見ユーザーの3分理解テスト、障害対応の実地試験。訂正申請フォームの本番送信テストは2026-11-15に実施済み（Issue #492）。障害対応は机上訓練を2026-11-15に実施済み（Issue #12に記録）だが、実地試験は未実施のままである。公開責任者は、これらが未実施であることを本チェックリストに明記したうえでPublic betaへ移行する判断をし（2026-11-15）、同日、外部法務確認と外部の中立性・方法論レビューを含む未実施事項が残ることを明記したうえで、正式公開へ移行する判断をした（2026-11-15）。訂正・反論の通し試験、ロールバック訓練、ライセンス確定、Lighthouse計測と是正、運用責任体制の確定は完了済み
- 正式な公開判断の親Issue: [#12 Public beta trust and launch gate](https://github.com/M-Osugi1230/jichi-insight/issues/12)
- **Phase 15の全67自治体レビュー完了はPublic betaの必須条件ではない**。未完了範囲を明示し、審査済みデータのみ公開する


## Data

- [x] 47都道府県の公式入口と現行政策計画
- [x] 47都道府県のEvidence-backed Reviewed政策目標
- [x] 年度実績、予算、決算、重点事業、監査の文書スコープ接続
- [x] 契約、議会、首長公約のReviewed coverage
- [x] 計画版、報告年度、測定年度、会計区分の分離
- [x] 予算、決算、事業費、契約額の分離
- [x] 比較可能性未確認のランキングを公開しない
- [x] 独自の政策達成・未達判定を公開しない
- [x] Wave 1の861個票を全件正規化・統合検証
- [x] 愛知県56行・62系列を全件正規化
- [x] 大阪府83行・91系列を全件正規化
- [x] 広島県62指標を全件正規化
- [x] 香川県135固有指標・141表示箇所を全件正規化
- [x] 沖縄県375指標をReviewed最大到達深度として全件正規化
- [x] 沖縄県の計画基準値を年度実績へ昇格しない
- [x] 沖縄県の全国値を沖縄県実績として扱わない
- [x] Wave 2の5拠点・711件を一つの統合ゲートで検証
- [x] Wave 3の38県・13,755個票をReviewed最大到達深度へ引き上げ（`data/catalog/phase11_completion.json`）
- [x] Phase 13の20政令指定都市のv1レビュー基盤を完了（`data/catalog/phase13_completion.json`）
- [x] Phase 14の67自治体の公式資料インベントリを完了（`data/catalog/phase14_completion.json`）
- [ ] Phase 15の残り52自治体の個票レビュー（Public betaの必須条件ではない）
- [ ] 議会発言、採決、監査指摘、首長公約を個票単位で接続
- [ ] 比較可能性確認済み指標だけを横断比較へ昇格

## Product

- [x] Home、全国カバレッジ、47都道府県ページ
- [x] Phase 9 Reviewed目標ページ
- [x] Phase 10完了・深度マトリクスページ
- [x] 方法論、データ品質、出典、欠損表示
- [x] 利用規約、プライバシー、免責ページ
- [x] `robots.txt`、`sitemap.xml`、静的出力、GitHub Pages配信
- [ ] Phase 11個票接続の公開進捗ページ
- [ ] 個別事業ページの全国共通テンプレート
- [ ] 首長・公約ページ
- [ ] 議会・議案・採決ページ
- [ ] 比較可能性確認済み指標の比較画面
- [x] 訂正申請フォームの本番送信テスト（2026-11-15: 公開フォームから実際に送信し、Issue #492として起票とラベル自動付与を確認、テストとして判定・クローズまで完了）
- [x] 変更履歴の公開画面（2026-11-15: PR #458で`/corrections/history`を公開し、PR #468で実在の訂正correction-2026-001を登録、本番表示を確認）
- [x] 404、空状態、エラー状態の本番確認（2026-11-15: 存在しないURLで専用404ページの表示を本番確認。変更履歴ページの表示も確認。エラー状態はPR #456で実装）

## Trust

- [x] 事実、比較、解釈、評価を分離
- [x] 一次資料優先、未確認を推測で補完しない
- [x] 政治思想、政党、人物の好悪を採点しない
- [x] 首長、行政、議会、監査を役割別に扱う
- [x] 根拠不足時に評価しない品質状態
- [x] PartialとNot linkedをスキップしない
- [x] Wave 1のPartial 58件とNot linked 383件を未昇格保持
- [x] 愛知県の欠損値・目標改定・再掲を別状態として保持
- [x] 大阪府の将来目標・未調査値・旧系列・事業因果を推測しない
- [x] 広島県の未測定値・複合値・定性条件を原文保持
- [x] 香川県の目標版・再掲・訂正値・累積期間を原文保持
- [x] 沖縄県375件をannual actual未接続のPartialとして保持
- [x] 沖縄県の公式資料内異常値を無断訂正しない
- [x] 訂正・反論フローの本番通し試験
- [ ] 中立性、方法論、重大表現の外部レビュー（未実施。依頼パッケージは作成済みだが依頼先は未定・未依頼。公開責任者の判断により、未実施であることを本記録に明記したうえでPublic betaへ移行する（2026-11-15））
- [x] 公開可否レビューの承認記録（2026-11-15、公開責任者・大杉邑大がPublic betaへの移行を承認。本チェックリストのCurrent release positionがその記録を兼ねる）

## Engineering

- [x] リポジトリ検証、全Pythonテスト、Lint、型検査、production build
- [x] Phase 10完了ゲート
- [x] Phase 11共通個票Schema
- [x] Wave 1全861件の統合ゲート
- [x] 愛知県・大阪府・広島県・香川県・沖縄県の決定的Normalizer
- [x] Wave 2全711件の統合Schema・参照整合性テスト
- [x] GitHub Pages、Publication Audit、本番HTTP verification、Production Smoke
- [x] Wave 3の地域バッチNormalizerと統合ゲート（Phase 11完了）
- [ ] mainブランチ保護設定の最終確認（2026-11-15に確認: ブランチ保護・ルールセットはいずれも未設定。強制プッシュや削除を防ぐ技術的統制はなく、PR運用はプロジェクトの規律による。設定の要否は公開責任者の判断事項）
- [x] dependency audit、secrets scan、Actions least-privilege監査（2026-11-15: secrets scanは追跡ファイル1,988件で検出なし（対象はmainツリー、履歴全体は対象外）。Python依存は既知の脆弱性0件。Web依存はロック済み275パッケージをOSVで照合し本番依存は0件、開発専用（eslint経由のminimatch）に低深刻度1件（GHSA-g3hv-75wg-m249、可用性のみで本番未混入、修正版11.0.1で解消可能）。Actions least-privilege化は2026-11-15に適用済み）
- [x] preview / staging / production境界の確定（2026-11-15に確定: 専用のpreview / staging環境は持たず、productionはGitHub Pages（mainのみ）、マージ前確認はブランチ／PR＋ローカルproduction build＋全テスト＋契約テスト、previewはローカルビルドのみ、という境界を docs/DEPLOYMENT.md の「Environment boundary (adopted 2026-11-15)」に明文化。ホスト型PRプレビューは将来の選択肢として明示的に繰り延べ）
- [ ] rollback、backup、monitoring、incident訓練（2026-11-15: ロールバック実地訓練（PR #471・#472）と障害対応の机上訓練（Issue #12に記録）は実施済み。バックアップは正式公開前にリポジトリのmirror cloneを別保管先へ作成し、復元cloneで手順を確認済み。monitoringの自動アラートは未導入で、検知は週次確認・マージ時の公開検証・利用者報告に依存する）

## UX and accessibility

- [x] スマートフォンを主要導線の前提として設計
- [x] 見出し構造と色だけに依存しない状態ラベル
- [x] 出典・品質・未確認範囲を主要ページに表示
- [ ] 実機スマートフォン、キーボード、スクリーンリーダー監査（未実施。2026-11-15に公開責任者から確認OKの表明があったが、実機・キーボード・VoiceOverによる実測は行っていないため未完了として記録する）
- [x] 画像・図表の代替テキスト、コントラスト監査（2026-11-15: コンテンツ画像が存在しないことを確認（`<img>`・next/image ともに使用なし、唯一の画像資産はファビコン用SVG）。コントラストはPR #461・#464・#483で是正し、Lighthouse Accessibility 100で確認）
- [x] Lighthouse accessibility測定（2026-11-15、本番7ページをLighthouse 13.6・モバイルで計測。是正（PR #483）後の再計測でAccessibility 100、Best Practices 100、SEO 100を全ページで確認。Performanceはサンドボックス経由の参考値）
- [ ] 初見ユーザーによる3分理解テスト（未実施。公開責任者の確認表明はあったが、初見ユーザーによる実測は行っていないため未完了として記録する）

## Legal and policy

- [x] 編集方針、データ品質、訂正・反論、データ方針
- [x] 利用規約、プライバシーポリシー、免責ページ
- [ ] 公開文書の外部法務確認（未実施。公開責任者の判断により、未実施であることを本記録に明記したうえでPublic betaへ移行する（2026-11-15）。「法務確認済み」とは記載しない）
- [x] コード、方法論、構造化データのライセンス確定（2026-11-15 決定・PR #462: コード MIT／方法論・構造化データ CC BY 4.0、適用範囲は docs/LICENSING.md。外部法務確認は上の項目で別途未完了）
- [ ] 原資料の転載・引用範囲確認
- [ ] 個人情報、政治資金情報、要配慮情報の取扱確認

## Operations

- [x] リリース、訂正、障害、ロールバック、バックアップ手順
- [x] Production Smokeと公開検証の自動化
- [x] 更新責任者とレビュー責任者を明記（2026-11-15確定: 全ロールを大杉邑大が兼務する単独運用体制。docs/OPERATIONS_RUNBOOK.md §2）
- [x] 定期更新頻度、計画改定検知、訂正回答期限を確定（頻度と検知方法はOPERATIONS_RUNBOOK §4、訂正の確認開始目標はdocs/CORRECTIONS.mdとOPERATIONS_RUNBOOK §5）
- [x] P0 / P1障害連絡経路を確定（GitHub Issuesを正規の受付経路とし、非公開事項の扱いを含めOPERATIONS_RUNBOOK §6に明記）
- [x] 公開後4週間の安定運用計測方法を確定（OPERATIONS_RUNBOOK §11に週次計測の項目と安定の目安を定義。計測の実施は正式公開後）

## Repository hygiene

- [x] 後続作業で置換済みの旧PRを閉じる
- [x] Wave 1のNormalizerと統合ゲート
- [x] Wave 2の5拠点Normalizerと統合ゲート
- [x] Phase 11実行キューと完了記録を全国47都道府県・15,327件へ更新
- [ ] 初期ロードマップIssueを現在の完了状態へ再分類
- [ ] README、Roadmap、Release Checklist、公開ページの状態同期を回帰テスト化

## Final go / no-go gates

正式なPublic betaへ進むには、最低限次をすべて満たします。

1. 本番CI、build、deployment、Publication Audit、Production Smokeが成功
2. 公開対象の主張に一次資料とEvidenceがある
3. 公開範囲と個票未接続範囲が主要画面で一致
4. 利用規約、プライバシー、免責、ライセンスの確認が完了
5. 訂正受付、変更履歴、障害対応、ロールバックを本番相当環境で試験
6. モバイル、キーボード、読み上げ、Lighthouse監査を完了
7. 外部レビューと重大表現の法務確認を完了
8. 公開責任者が公開境界と未収録範囲を承認

## Current recommendation（2026-11-14）

**正式Public betaを最優先の並走トラックとする。** Phase 15データの個票レビューは別トラックとして継続する。

1. Issue #12のTrust / Legal / Accessibility / Operationsについて、確認日・証跡URL・レビュアーを記録する。
2. 自動化可能なCI、定期Production Smoke、公開範囲の同期テスト、更新日表示を整備する。
3. 人による承認が必要な法務、重大表現・中立性、訂正フローの本番相当試験、読み上げ・実機テストを実施する。
4. P0/P1既知問題0件とGo / No-Go承認を確認して初めて「Public beta」と表記する。
5. Phase 15は正本キューとhuman reviewを維持し、未検証候補をReviewedとして公開しない。

進捗の正本は`data/catalog/phase15_core_capital_review_queue.json`および`data/catalog/phase11_completion.json`。このチェックリストは公開判断の証跡であり、実装やレビューの完了を推定してチェックしない。
