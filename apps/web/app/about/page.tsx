import Link from "next/link";

import { PageIntro } from "@/components/PageIntro";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { miyagiKpiActualStats } from "@/lib/miyagiActuals";
import { nationwideCoverageStats } from "@/lib/nationwideCoverage";

const problems = [
  ["資料が分断されている", "同じ事業でも、予算、契約、決算、KPI、監査、議会質疑が別々の場所にあります。"],
  ["金額と成果がつながらない", "何に使ったかは分かっても、何を実行し、住民生活がどう変わったかまで追いにくい状態です。"],
  ["公約と事業がつながらない", "選挙時の約束が、どの予算・事業・成果指標に対応するのかが明確ではありません。"],
  ["責任主体が分かりにくい", "首長の執行責任と、議会の審議・監視責任を分けて確認する必要があります。"],
];

export default function AboutPage() {
  return (
    <main>
      <SiteHeader />
      <div className="pageShell">
        <PageIntro eyebrow="Why Jichi Insight" title="公開資料を、住民が判断できる根拠へ。"><p>日本の自治体は多くの資料を公開しています。それでも住民が短時間で全体像を理解するのは簡単ではありません。問題は情報がないことだけではなく、情報が資料単位で分断され、目標・支出・実行・成果の関係を追いにくいことです。</p></PageIntro>
        <section className="contentSection"><p className="eyebrow">Problem</p><h2>私たちが解決する4つの分断</h2><div className="problemGrid">{problems.map(([title, text]) => <article key={title}><h3>{title}</h3><p>{text}</p></article>)}</div></section>
        <section className="contentSection narrativeSection"><div><p className="eyebrow">North star</p><h2>誰かを採点することが、目的ではありません。</h2></div><div><p>Jichi Insightが提供するのは、確認できた事実、条件をそろえた比較、ルールを明示した解釈、根拠を確認できる評価、そして分からないことです。</p><blockquote>住民が、自分自身で自治体、知事・市長、議会を評価できる情報環境をつくる。</blockquote><p>これが、機能や対象地域が増えても変えない最上位の目的です。</p></div></section>
        <section className="contentSection"><p className="eyebrow">What we will not do</p><h2>信頼を損なう近道は選びません。</h2><ul className="plainList"><li>投票先や候補者を推奨しない</li><li>政党や政治思想を採点しない</li><li>根拠のない疑惑を掲載しない</li><li>AI抽出結果を未確認のまま評価に使わない</li><li>全国を浅く並べるために品質を下げない</li></ul></section>
        <section className="callout"><div><p className="eyebrow">Current phase</p><h2>全国の入口から、目標と実績の接続へ。</h2><p>全{nationwideCoverageStats.currentPlanConfirmedPrefectures}都道府県で現行の政策計画を確認済みです。北海道・宮城県・福岡県を深掘りし、宮城県では{miyagiKpiActualStats.annualResultRows}件の年度実績まで接続しました。次は予算・事業・契約・議会へ根拠の鎖を伸ばします。</p></div><Link className="primaryAction" href="/municipalities">現在の公開状況を見る</Link></section>
      </div>
      <SiteFooter />
    </main>
  );
}
