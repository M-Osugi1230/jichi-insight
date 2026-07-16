# Wave 1 policy review queue

## Purpose

第1波9都道府県の現行計画入口は確認済みですが、公式資料を見つけた状態と、政策体系・KPIを一次資料と照合したReviewed状態は異なります。

このキューは、次の作業対象、必要な品質ゲート、作業順の理由を記録し、件数拡大による誤昇格を防ぐための運用台帳です。機械可読な正本は [`data/catalog/wave1_policy_review_queue.json`](../data/catalog/wave1_policy_review_queue.json) です。

## Current queue

| 順序 | 都道府県 | 状態 | 次の品質ゲート | 主な次作業 |
|---:|---|---|---|---|
| 基準 | 福岡県 | Reviewed基準実装 | 年度実績との接続 | 118指標への年度実績接続、取組27以降の追加 |
| 1 | 北海道 | KPI本文Reviewed 18/108 | KPIカタログ化 | 指標19〜29（ゼロカーボン）を個票から抽出し、Evidence Packetを付与 |
| 2 | 宮城県 | 作業待ち | 関連資料の固定 | 実施計画、数値目標、行政評価を資料単位で固定 |
| 3 | 愛知県 | 作業待ち | 関連資料の固定 | 実施計画、年次フォローアップを資料単位で固定 |
| 4 | 香川県 | 作業待ち | 関連資料の固定 | 延長・改定後の数値目標、行政評価を固定 |
| 5 | 広島県 | 作業待ち | 関連資料の固定 | 政策体系、KPI、進捗管理資料を固定 |
| 6 | 沖縄県 | 作業待ち | 関連資料の固定 | 基本計画、実施計画、KPI、進捗資料を固定 |
| 7 | 東京都 | 作業待ち | 関連資料の固定 | 戦略、政策目標、KPI、実行・進捗資料の関係を整理 |
| 8 | 大阪府 | 作業待ち | 関連資料の固定 | 新戦略の政策階層、KPI、実行・進捗資料を固定 |

順序は自治体や政策の優劣を表すものではありません。資料構造、抽出方法の再利用性、作業依存関係に基づく運用順です。

## Reviewed promotion gate

都道府県を`reviewed_data`へ昇格するには、現行性、政策階層、全表示KPI、欠損・条件・再掲、Evidence Packet、参照整合性、Webビルド、公開後Smokeをすべて確認します。

## Source status boundaries

- `indexed / verified`：公式資料の存在、URL、現行性を確認済み。本文データは未Reviewed。
- `policy_hierarchy_reviewed`：政策体系の原文・順序・計画期間をReviewed済み。
- `indicator_positions_reviewed`：一意指標の番号、資料、PDFページ位置をReviewed済み。
- `indicator_relationships_reviewed`：複数政策分野への追加掲載を重複KPIではなく参照としてReviewed済み。KPI本文は段階的に追加。
- `reviewed`：本文、数値、期間、単位、条件を人が一次資料と照合済み。
- `actuals_linked`：目標と年度実績、公式説明、定義変更を接続済み。
- `published`：公開ゲートと本番確認を通過済み。

## Active work: Hokkaido

### Completed

- 計画期間：「2024（令和6）年度から概ね10年間」
- 3基本方向、18政策分野、政策体系Evidence Packet 3件
- 指標PDF18資料・108ページ、指標番号1〜108、欠落0・重複0
- 複数分野への追加掲載5件を参照として整合
- 指標1〜12（食）と指標13〜18（観光）をReviewed
- KPI Evidence Packet：18件
- 指標13・14・16の複数系列を個別に保持
- 指標13〜16の「以上」を`at_least`として保持
- 指標14・15の現状値なしをnullで保持
- 指標16・17は観光と社会経済の基盤整備への一意指標参照として保持
- 進捗・評価：未接続・未評価を維持

### Active

1. 指標19〜29（ゼロカーボン）の本文・値・単位・期間をReviewed化
2. 残る90指標を政策分野順に抽出
3. 条件、上下限、複数系列、目標未設定、比較注意を構造化
4. 各Reviewed指標と同時にEvidence Packetを付与

### Remaining

1. 残る90指標のReviewed化とEvidence Packet
2. 年度実績・進捗資料との接続
3. 自動テストと公開ゲート
4. 北海道公開ページ

資料本文を確認できない項目は推測で補完せず、`needs_review`または未登録のまま残します。
