# Security policy

## Reporting

公開Issueに認証情報、個人情報、未公開資料、脆弱性の再現手順を投稿しないでください。リポジトリ所有者へGitHubのPrivate vulnerability reportingを使用してください。

## Protected information

Jichi Insightは公的活動の検証を目的とします。次の情報は収集・公開しません。

- 公務と無関係な自宅住所
- 家族や私人の情報
- 認証情報、非公開APIキー
- 情報公開請求で非開示とされた個人情報
- 根拠のない疑惑や匿名情報

## Supply chain

- 依存関係はDependabotで監視します。
- GitHub ActionsでPRタイトル、Issue本文、ブランチ名など未信頼入力をshellへ直接展開しません。
- Actionsは必要最小限のpermissionsで実行します。
- シークレットはfork由来PRに渡しません。
- データ取得処理と公開処理を分離します。

## Supported versions

正式公開前は `main` のみをサポート対象とします。
