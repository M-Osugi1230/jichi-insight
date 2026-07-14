# Data policy

## Purpose

この文書は、Jichi Insightが収集・生成・公開する情報の権利、出典、品質、訂正、保存方針を定めます。

## Data layers

```text
source catalog  資料の所在・書誌情報
raw             取得した原資料または参照情報
extracted       自動抽出結果
reviewed        人手確認済み構造化データ
published       公開条件を満たしたデータ
```

`raw`、`extracted`、`reviewed`、`published` はGit管理の適否を個別に判断します。大容量PDF、利用条件が不明な原資料、個人情報を含む資料はGitへ格納せず、参照URLとハッシュを管理します。

## Required provenance

主要データは最低限、次を持ちます。

- `source_url`
- `source_title`
- `source_organization`
- `document_type`
- `published_at` または `last_verified_at`
- `fiscal_year`
- `page_number` または `location_note`
- `extraction_method`
- `review_status`
- `confidence`

## Copyright and reuse

- 公式資料を無条件に再配布可能とは扱いません。
- 原資料の全文転載より、URL、資料名、該当ページ、短い根拠箇所を優先します。
- 公的統計は提供元の利用規約に従います。
- 独自の構造化、評価、注釈は原資料と区別します。
- コード、方法論、公開データのライセンスは分離して決定します。
- ライセンス確定前は、明示的な許可なく再利用できません。

## Accuracy

- 不明値を0や空文字で代替しません。
- 「未公開」「未確認」「該当なし」「評価不能」を区別します。
- 当初予算、補正後予算、執行額、決算額を混同しません。
- 単位、会計年度、名目・実質、一般会計・特別会計を明示します。
- 比較では人口規模、行政区分、地域条件を考慮します。

## Corrections and right of reply

自治体、首長、議員、政党、住民、研究者は根拠資料付きで訂正を申請できます。修正時は次を記録します。

- 修正前
- 修正後
- 修正理由
- 根拠資料
- 修正日
- レビュー担当

反論は、事実訂正と意見表明を区別して掲載します。

## Retention

取得日、原資料URL、コンテンツハッシュ、抽出バージョンを保存し、資料差し替えやリンク切れを検知できるようにします。
