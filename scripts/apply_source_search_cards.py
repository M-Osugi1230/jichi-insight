from pathlib import Path

path = Path("apps/web/app/data-quality/page.tsx")
text = path.read_text(encoding="utf-8")
old_heading = "首長分野は、任期・公約資料・分割レビュー・評価を分ける。"
new_heading = "首長分野は、任期・探索・公約資料・分割レビュー・評価を分ける。"
if text.count(old_heading) != 1:
    raise SystemExit("unexpected heading")
text = text.replace(old_heading, new_heading)
old_card = """            <article className={styles.summaryCard}>
              <span>登録済み公約原文資料</span>
"""
new_cards = """            <article className={styles.summaryCard}>
              <span>公約資料の探索記録</span>
              <strong>{snapshot.manifestoSourceSearches}</strong>
              <p>確認範囲、未発見、次の確認方法を保存。</p>
            </article>
            <article className={styles.summaryCard}>
              <span>安定した一次資料を未発見</span>
              <strong>{snapshot.manifestoSourcesNotFound}</strong>
              <p>不存在ではなく、現時点の探索結果として表示。</p>
            </article>
            <article className={styles.summaryCard}>
              <span>登録済み公約原文資料</span>
"""
if text.count(old_card) != 1:
    raise SystemExit("unexpected card anchor")
path.write_text(text.replace(old_card, new_cards), encoding="utf-8")
