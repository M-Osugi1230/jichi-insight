# UI Motion System

Jichi Insight は自治体情報を扱う静的サイトであるため、モーションは情報の理解を助ける補助表現に限定する。演出より可読性・操作の予測可能性・軽量性を優先する。

## 採用原則とトークン

| 原則 | CSSトークン | 値 | 用途 |
|---|---|---:|---|
| Slow In and Slow Out | `--motion-ease-standard` | `cubic-bezier(0.22, 1, 0.36, 1)` | カード・パネルの標準的な減速 |
| Slow In and Slow Out | `--motion-ease-enter` | `cubic-bezier(0.16, 1, 0.3, 1)` | コンテンツの穏やかな入場 |
| Timing | `--motion-ease-feedback` | `cubic-bezier(0.2, 0.75, 0.25, 1)` | hover・押下など短い操作応答 |
| Timing | `--motion-duration-quick` | `120ms` | 押下・色変化 |
| Timing | `--motion-duration-standard` | `200ms` | hover・開閉 |
| Timing | `--motion-duration-enter` | `320ms` | カード・一覧項目の入場 |
| Timing / Staging | `--motion-duration-emphasis` | `480ms` | ページ主要セクションの入場 |
| Staging | `--motion-distance-subtle` | `6px` | 入場時の小さな上昇距離 |

時間差は隣接要素ごとに40ms刻み、最大200msまでとする。長い待ち時間を作らず、一覧に視線の順番を与える。

## 適用範囲

- ページ主要セクションとカード・記事：opacity と transform のみで、6px上昇する短いフェードイン。
- カード・主要アクション・ボタン・ナビゲーションリンク：色、背景色、境界線、影、transform による控えめな hover / active 応答。
- ネイティブ `details / summary`：開閉パネルの opacity と transform を遷移。ネイティブの開閉・キーボード操作・フォーカス管理を維持する。
- 既存の `:focus-visible` のアウトライン仕様は変更しない。

## アクセシビリティと表示保証

- `prefers-reduced-motion: reduce` では追加した animation と transition をすべて無効化し、スクロールも即時にする。入場対象は opacity: 1 / transform: none に戻す。
- 印刷時も animation / transition を無効化し、内容を常に表示する。
- 表示内容・開閉状態を JavaScript に依存させない。CSS が無効、または animation が再生されない場合も、通常の文書フローで内容を読める。
- 点滅、大きな移動、視差スクロール、自動再生する反復アニメーションは使わない。

## 禁止事項・運用ルール

- GSAP、Lottie、Anime.js、Three.js 等のモーション／描画ライブラリを導入しない。実装は CSS のみとする。
- 入場アニメーションで height / width / margin / padding / top / left / grid 等のレイアウトプロパティをアニメーションしない。レイアウト再計算を伴う演出は避ける。
- 本文コピー、データ、DOM構造をモーション導入のために変更しない。
- モーションは意味や状態を伝える唯一の手段にしない。色・動きだけで状態を示さず、既存の文字情報とフォーカス表示を維持する。
