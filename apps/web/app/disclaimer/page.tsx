import type { Metadata } from "next";

import { PageIntro } from "@/components/PageIntro";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";

export const metadata: Metadata = {
  title: "免責事項",
  description: "Jichi Insightの情報品質、評価、外部リンク、専門的助言に関する免責事項。",
};

export default function DisclaimerPage() {
  return (
    <main>
      <SiteHeader />
      <div className="pageShell">
        <PageIntro eyebrow="Disclaimer" title="免責事項">
          <p>Jichi Insightは、自治体の公開資料を読み解くための調査・整理基盤です。公式な行政機関、報道機関、選挙運動、法律・会計・投資等の専門助言サービスではありません。</p>
          <p>最終更新：2026年7月29日</p>
        </PageIntro>

        <section className="contentSection">
          <h2>情報の正確性と更新</h2>
          <p>一次資料との照合、出典、確認日、品質状態の表示に努めますが、情報の正確性、完全性、最新性、特定目的への適合性を保証しません。自治体による資料の差し替え、URL変更、訂正、制度改正、集計定義の変更等により、掲載内容と最新の公式情報が一致しない場合があります。</p>
        </section>

        <section className="contentSection">
          <h2>評価と比較</h2>
          <p>掲載する比較や評価は、公開された方法論と確認できた根拠に基づきます。根拠不足、定義差、対象期間差、母集団差がある場合は評価不能または要確認として扱います。順位や数値だけで自治体、首長、議会、政策の優劣を断定するものではありません。</p>
        </section>

        <section className="contentSection">
          <h2>重要な判断</h2>
          <p>投票、行政手続、契約、税務、法務、会計、投資、寄付、報道その他の重要な判断では、本サイトだけに依存せず、最新の公式資料、原文、担当機関および必要に応じた専門家へ確認してください。</p>
        </section>

        <section className="contentSection">
          <h2>外部リンクと原資料</h2>
          <p>外部サイトの内容、可用性、安全性、継続性を保証しません。リンク先資料の著作権、利用条件、個人情報の取扱いは各公開元に帰属します。リンク切れや資料差し替えを確認した場合は訂正手続から報告できます。</p>
        </section>

        <section className="contentSection">
          <h2>損害への責任</h2>
          <p>法令上認められる範囲で、本サイトの利用または利用不能、情報の誤り・欠落・遅延、外部リンク、第三者による投稿等から生じた損害について、運営者は責任を負いません。ただし、運営者の故意または重過失による場合など、法令上免責が認められない範囲を除きます。</p>
        </section>

        <section className="contentSection">
          <h2>訂正</h2>
          <p>具体的な誤り、より強い一次資料、公式な反論を確認した場合は、訂正・反論ページから申請してください。検証結果と変更内容は、可能な範囲で追跡できる形で記録します。</p>
        </section>
      </div>
      <SiteFooter />
    </main>
  );
}
