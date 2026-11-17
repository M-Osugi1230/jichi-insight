import type { Metadata } from "next";
import Link from "next/link";

import { CorrectionHistoryEntry } from "@/components/CorrectionHistoryEntry";
import { PageIntro } from "@/components/PageIntro";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { correctionsHistory } from "@/lib/correctionsHistory";
import { canonicalFor } from "@/lib/pageMetadata";

export const metadata: Metadata = {
  alternates: {
    canonical: canonicalFor("/corrections/history"),
  },
  title: "変更履歴",
  description:
    "Jichi Insightが公開データへ適用した訂正の履歴。修正前後、理由、根拠、日時、レビュー担当を公開します。",
};

export default function CorrectionsHistoryPage() {
  const { entries, total, updatedAt } = correctionsHistory;

  return (
    <>
      <SiteHeader />
      <main>
      <div className="pageShell">
        <PageIntro eyebrow="Change history" title="修正の前後を、そのまま残します。">
          <p>
            重大な訂正では、修正前、修正後、修正理由、根拠資料、修正日時、影響した評価・画面とレビュー担当をここに記録します。誤りを静かに差し替えることはしません。
          </p>
          <p>
            正本更新日: <time>{updatedAt}</time> / 記録件数: {total}件
          </p>
        </PageIntro>

        <section className="contentSection">
          <p className="eyebrow">Recorded fields</p>
          <h2>1件ごとに、確認できる形で残します。</h2>
          <div className="roleGrid">
            <article>
              <h3>修正前と修正後</h3>
              <p>変更した記載の前後の内容を、そのまま並べて示します。</p>
            </article>
            <article>
              <h3>理由と根拠</h3>
              <p>なぜ直したのかと、照合した一次資料へのリンクを残します。</p>
            </article>
            <article>
              <h3>日時とレビュー担当</h3>
              <p>公開した日付と、確認・判定を担当したレビュー担当を記録します。</p>
            </article>
          </div>
        </section>

        <section className="contentSection">
          <p className="eyebrow">History</p>
          <h2>公開中の変更履歴</h2>
          {total === 0 ? (
            <div>
              <p>
                現在、公開中の変更履歴はありません。訂正申請を受け付け、一次資料で検証し、実際に公開データを修正したものだけを、確定した順にここへ掲載します。
              </p>
              <p>
                架空の訂正やテスト用の履歴を載せることはありません。掲載がないことは、履歴が未整備なのではなく、公開を伴う訂正がまだ発生していないことを意味します。
              </p>
              <p>
                訂正の申請方法は <Link href="/corrections">訂正・反論のページ</Link> を確認してください。
              </p>
            </div>
          ) : (
            <div className="roleGrid">
              {entries.map((entry) => (
                <CorrectionHistoryEntry entry={entry} key={entry.id} />
              ))}
            </div>
          )}
        </section>
      </div>
      </main>
      <SiteFooter />
    </>
  );
}
