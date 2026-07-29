import type { Metadata } from "next";

import { PageIntro } from "@/components/PageIntro";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";

export const metadata: Metadata = {
  title: "利用規約",
  description: "Jichi Insightの利用条件、禁止事項、知的財産、免責、訂正手続を定めます。",
};

const updatedAt = "2026年7月29日";

export default function TermsPage() {
  return (
    <main>
      <SiteHeader />
      <div className="pageShell">
        <PageIntro eyebrow="Terms of use" title="利用規約">
          <p>本規約は、Jichi Insight（以下「本サイト」）の利用条件を定めるものです。本サイトを利用した時点で、本規約に同意したものとみなします。</p>
          <p>最終更新：{updatedAt}</p>
        </PageIntro>

        <section className="contentSection">
          <h2>1. 本サイトの目的</h2>
          <p>本サイトは、自治体が公表する計画、予算、事業、成果、議会その他の一次資料を整理し、住民が自ら確認・比較・判断できる情報環境を提供することを目的とします。特定の自治体、政党、候補者、議員、政策または投票行動を推奨するものではありません。</p>
        </section>

        <section className="contentSection">
          <h2>2. 情報の利用</h2>
          <ul className="plainList">
            <li>閲覧者は、法令および各原資料の利用条件に従い、本サイトを利用できます。</li>
            <li>本サイトの説明文、編集、構造、画面、方法論その他の独自コンテンツを転載・再配布する場合は、出典と参照日を明示してください。</li>
            <li>自治体等が公開する原資料の著作権・利用条件は、各権利者および公開元の条件に従います。</li>
            <li>構造化データの一括再配布、商用利用、機械取得については、公開ライセンスまたは個別の表示がある場合、その条件を優先します。</li>
          </ul>
        </section>

        <section className="contentSection">
          <h2>3. 禁止事項</h2>
          <ul className="plainList">
            <li>法令、公序良俗または第三者の権利を侵害する行為</li>
            <li>虚偽情報、個人情報、認証情報、未公開資料を公開フォームやIssueへ投稿する行為</li>
            <li>本サイトまたは関連システムの運用を妨害する行為</li>
            <li>誤解を招く形で、本サイトが特定の主張・候補者・商品を支持していると表示する行為</li>
            <li>出典表示を除去し、Jichi Insight独自の調査・編集成果を自己の成果として表示する行為</li>
          </ul>
        </section>

        <section className="contentSection">
          <h2>4. 訂正と反論</h2>
          <p>事実誤認、より強い一次資料、公式な反論または補足がある場合は、訂正・反論ページから申請できます。申請内容は一次資料と照合し、事実訂正、評価変更、反論掲載または対応なしを区別して判断します。</p>
        </section>

        <section className="contentSection">
          <h2>5. 免責</h2>
          <p>本サイトは正確性、完全性、最新性の向上に努めますが、これらを保証しません。本サイトの情報は、法務、税務、会計、投資、選挙または行政手続に関する専門的助言ではありません。重要な判断では、必ず最新の公式資料と専門家の助言を確認してください。</p>
        </section>

        <section className="contentSection">
          <h2>6. 変更・停止</h2>
          <p>本サイトは、保守、障害対応、資料更新、法令対応その他の必要に応じて、予告なく内容の変更、公開範囲の縮小または提供停止を行う場合があります。</p>
        </section>

        <section className="contentSection">
          <h2>7. 規約の変更</h2>
          <p>本規約を変更した場合は、本ページの最終更新日を更新します。重大な変更は、可能な範囲でサイト上またはリポジトリ上に変更理由を記録します。</p>
        </section>
      </div>
      <SiteFooter />
    </main>
  );
}
