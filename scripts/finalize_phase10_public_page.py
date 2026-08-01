from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "apps/web/app/municipalities/phase10/page.tsx"
COMPLETION_MARKER = "Completed on 2026-08-01"


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise SystemExit(f"Expected Phase 10 page fragment not found: {old[:80]}")
    return text.replace(old, new, 1)


def main() -> None:
    text = PAGE.read_text(encoding="utf-8")
    if COMPLETION_MARKER in text:
        return

    old_description = (
        '    "全国47都道府県を同じ品質ゲートで管理し、政策目標を年度実績、'
        '予算・決算、重点事業、契約、議会、監査、首長公約へ接続する'
        'Phase 10の進行状況を公開します。",'
    )
    new_description = (
        '    "全国47都道府県がPhase 10の共通品質ゲートへ到達した完了状態と、'
        '文書スコープ・個票スコープの境界を公開します。",'
    )
    text = replace_once(text, old_description, new_description)

    text = replace_once(
        text,
        '''          <p>
            Phase 9で確認した全国47都道府県の目標原文を、年度実績、予算・決算、
            重点事業、契約、議会、監査、首長公約へつなぎます。掲載件数ではなく、
            全都道府県が同じ品質ゲートを通過したかでPhase 10の完了を判断します。
          </p>''',
        '''          <p>
            Phase 9で確認した全国47都道府県の目標原文を、年度実績、予算・決算、
            重点事業、契約、議会、監査、首長公約へ接続する共通ゲートを、
            2026年8月1日に全都道府県で完了しました。
          </p>
          <p>
            完了は全国の文書スコープを対象とします。個別の目標、予算科目、事業、
            契約、発言、監査指摘をすべて一対一接続したという意味ではありません。
          </p>''',
    )

    marker = "        </PageIntro>\n\n        <section className={styles.summaryGrid}"
    banner = '''        </PageIntro>

        <section className={styles.boundary} aria-label="Phase 10完了宣言">
          <div>
            <p className="eyebrow">Completed on 2026-08-01</p>
            <h2>Phase 10 完了</h2>
          </div>
          <div>
            <p>
              47都道府県すべてで、政策・Evidence・公開をReviewed、年度実績・予算・
              決算・重点事業・監査を文書スコープLinked、契約・議会・首長公約を
              公式一次資料または不存在を断定しない公式検索結果までReviewedとしました。
            </p>
            <p>
              政策の達成・未達は判定せず、比較可能性が確認されるまでランキングにも
              使用しません。個票単位の深掘りは次の研究工程として継続します。
            </p>
          </div>
        </section>

        <section className={styles.summaryGrid}'''
    text = replace_once(text, marker, banner)
    text = text.replace(
        'aria-label="Phase 10進行状況"',
        'aria-label="Phase 10完了状況"',
    )
    text = replace_once(
        text,
        "            <span>年度実績 Reviewed以上</span>",
        "            <span>年度実績 文書接続</span>",
    )

    old_actuals = (
        "            <p>うち目標へ直接接続済みは"
        "{uniformSummary.annual_actuals.linked}県です。</p>"
    )
    new_actuals = (
        "            <p>全47都道府県で公式年度実績を"
        "正しい資料役割・期間へ接続しています。</p>"
    )
    text = replace_once(text, old_actuals, new_actuals)

    text = replace_once(
        text,
        "            <p>入口確認以上の県数です。金額接続済みを意味しません。</p>",
        (
            "            <p>文書スコープの接続数です。"
            "全科目・全事業の個票接続を意味しません。</p>"
        ),
    )

    old_completion = (
        "              <p>47都道府県すべてが共通ゲートを通るまで"
        "Phase 10は完了にしません。</p>"
    )
    new_completion = (
        "              <p>47都道府県すべてが共通ゲートへ到達したため、"
        "Phase 10を完了としました。</p>"
    )
    text = replace_once(text, old_completion, new_completion)

    text = replace_once(
        text,
        '''              政策目標、Evidence、公開検証は47都道府県でReviewed済みです。
              下表は、その先の実績・金額・事業・説明責任の未完範囲を示します。''',
        '''              下表は、全47都道府県が到達した共通深度を示します。説明責任3層は
              一次資料または公式検索結果までReviewedし、未特定を不存在とは扱いません。''',
    )
    PAGE.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
