# Pipelines

パイプラインは `collect → extract → normalize → validate → review → publish` を明確に分離します。

初期実装では、まず資料カタログと検証を優先します。PDFから候補値を抽出できても、自動的に公開評価へ昇格させません。

予定モジュール:

- `collectors`: 自治体公式サイト、議会、選管、統計の資料発見
- `extractors`: HTML、CSV、PDFテキストから候補値抽出
- `normalizers`: 年度、金額、行政区分、政策分野を統一
- `validators`: JSON Schema、重複、整合性、リンク、単位
- `publishers`: Reviewedデータから公開JSON生成
