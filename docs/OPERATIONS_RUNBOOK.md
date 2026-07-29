# Jichi Insight publication operations runbook

最終更新: 2026-07-29

## 1. Purpose

公開後の更新、訂正、障害、ロールバックを、担当者の記憶ではなく再現可能な手順で実施するための運用基準です。

## 2. Roles

正式公開前にGitHubユーザー名または組織ロールを記入します。

| Role | Responsibility | Owner |
| --- | --- | --- |
| Publication owner | 公開境界、Go / No-Go、重大表現の最終承認 | 未設定 |
| Data reviewer | 一次資料、Evidence Packet、年度・単位・定義の照合 | 未設定 |
| Engineering owner | CI、build、deployment、monitoring、rollback | 未設定 |
| Correction owner | 訂正受付、一次回答、調査、履歴公開 | 未設定 |

一人が複数ロールを兼務する場合でも、各判断をPull RequestまたはIssueへ記録します。

## 3. Normal release procedure

1. 対象データと公開境界をPull Request本文へ明記する。
2. `pnpm check`を実行し、データ検証、Pythonテスト、Lint、型検査、production buildを完了する。
3. 出典URL、確認日、品質状態、未確認範囲をレビューする。
4. 法務・プライバシー・重大表現に影響する変更がないか確認する。
5. mainへマージし、GitHub Pages deploymentを確認する。
6. ホーム、代表自治体ページ、`robots.txt`、`sitemap.xml`のProduction Smokeを確認する。
7. `.github/publication-status.json`の検証結果を確認する。
8. 公開境界に影響する変更はCHANGELOGまたはPull Requestへ記録する。

## 4. Update cadence

- 公式計画入口・リンク切れ: 月1回以上
- 深掘り対象自治体の計画・KPI・年度実績: 四半期ごと、および公式改定検知時
- 予算・決算・行政評価: 各自治体の公表時期に合わせて確認
- 重大な訂正: 確認後、通常更新を待たず対応
- 依存関係・セキュリティ監査: 月1回以上

更新がない場合も、最終確認日を更新するためだけに根拠なくコミットしません。確認した資料と結果を記録します。

## 5. Correction service level

公開Issueで受け付けられる内容に限り、次を運用目標とします。

- 受付確認: 7日以内
- 重大性の一次判定: 7日以内
- 明白な事実誤認・リンク切れ: 原則14日以内に修正または状況回答
- 複雑な定義差・評価変更: 調査計画と次回更新予定をIssueへ記録

個人情報、認証情報、脆弱性、非公開資料が投稿された場合は、内容を引用せず、可能な範囲で非表示化・削除を優先します。

## 6. Incident levels

### P0 — Critical

- サイト全体が閲覧不能
- 公開データに認証情報、秘密情報、重大な個人情報が含まれる
- 大規模な誤データが評価・比較へ反映されている
- 改ざんまたは権限侵害が疑われる

対応:

1. 公開停止または直前の安全なコミットへロールバックする。
2. 新規マージを止める。
3. Issueまたは非公開の安全な連絡経路へ時系列を記録する。
4. 影響範囲を確認し、秘密情報は失効・再発行する。
5. 復旧後に原因、影響、再発防止を公開可能な範囲で記録する。

### P1 — High

- 主要ページの404、表示崩れ、誤誘導
- 重要数値、単位、年度、出典の誤り
- 訂正申請が利用不能
- deploymentまたは検証が継続的に失敗

対応:

1. 当日中にIssue化し、公開影響を明記する。
2. 修正または該当箇所を一時的に非公開・要確認へ変更する。
3. Production Smokeを再実行する。

### P2 — Normal

- 軽微な表示、表記揺れ、低影響のリンク切れ
- 深掘り未完了、追加資料候補

通常のPull Requestで対応します。

## 7. Rollback

1. 直近の正常なdeploymentとcommit SHAを特定する。
2. 問題コミットをrevertするPull Requestを作成する。緊急時は公開責任者とEngineering ownerの判断を記録して迅速にrevertする。
3. mainへの反映後、deploymentとProduction Smokeを確認する。
4. 原因修正はrollbackと分けたPull Requestで行う。
5. P0/P1の場合は、影響範囲と再発防止をIssueへ記録する。

正式公開前に、無害なテスト変更でrevertから再deploymentまでを一度実地確認します。

## 8. Backup and recovery

- コード、設定、構造化データ、ドキュメントはGitHubリポジトリを正本とする。
- GitHub外にしか存在しない手作業データを公開工程へ持ち込まない。
- 外部取得した一次資料は、公開条件を確認し、URL、資料名、発行主体、取得日、該当ページをEvidence Packetへ保持する。
- GitHub自体が利用不能な場合に備え、正式公開前にリポジトリのcloneまたはarchiveを別保管先へ保存し、復元手順を確認する。
- secretsはバックアップへ含めず、再発行可能な形で管理する。

## 9. Monitoring

最低限、次を定期的に確認します。

- GitHub ActionsのCI、deployment、Production Smoke失敗
- ホームと代表ページのHTTP応答
- `robots.txt`と`sitemap.xml`
- 公開対象URLの404・リダイレクト異常
- 公式一次資料リンクのリンク切れ
- 依存関係とsecret scan

監視を自動化する場合、失敗通知先、確認担当、再通知条件を明記します。

## 10. Public beta Go / No-Go record

公開判断IssueまたはPull Requestへ、次を記録します。

- 対象commit SHA
- 公開範囲と未収録範囲
- CI、build、deployment、Production Smoke結果
- 法務ページと訂正導線の確認結果
- モバイル、キーボード、読み上げ、Lighthouse結果
- 外部レビューと重大表現確認の結果
- 未解決P0/P1件数
- Publication ownerのGo / No-Go判断と日時
