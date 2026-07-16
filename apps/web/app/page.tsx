import Link from "next/link";

import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { StatusBadge } from "@/components/StatusBadge";
import { catalogStats, municipalityMeta } from "@/lib/catalog";
import { nationwideCoverageStats } from "@/lib/nationwideCoverage";
import { allPolicyTargetStats } from "@/lib/policyTargets";

const pillars = [
  { label: "Promise", title: "何を約束したか", text: "選挙公報、マニフェスト、総合計画を、評価可能な単位へ整理します。" },
  { label: "Money", title: "いくら使ったか", text: "当初予算、補正、執行、決算を区別し、事業・契約へ接続します。" },
  { label: "Action", title: "何を実行したか", text: "事業、契約、支出先、実施内容を整理し、計画と実行の間をつなぎます。" },
  { label: "Result", title: "何が変わったか", text: "KPIの目標と実績を示し、因果関係を断定できない場合も明記します。" },
  { label: "Accountability", title: "誰がどう説明したか", text: "首長の説明、議会の審議、監査、訂正履歴を確認できるようにします。" },
];

export default function Home() {
  return (
    <main>
      <SiteHeader />
      <section className="hero">
        <div className="heroCopy">
          <p className="eyebrow">自治体IR・行政アカウンタビリティ基盤</p>
          <h1>約束・予算・実行・成果を、<br />ひとつにつなぐ。</h1>
          <p className="lead">公開されているのに、理解しにくい自治体情報を整理します。住民が自治体、知事・市長、議会を自分で評価するための根拠を届けます。</p>
          <div className="heroActions">
            <Link className="primaryAction" href="/municipalities">全国47都道府県を探す</Link>
            <Link className="secondaryAction" href="/policies">福岡県の政策を見る</Link>
          </div>
        </div>
        <aside className="heroStatus" aria-label="開発状況">
          <div className="heroStatusHeader"><StatusBadge label="全国版を構築中" tone="progress" /><span>更新 {nationwideCoverageStats.updatedAt}</span></div>
          <dl className="metricList">
            <div><dt>全国登録</dt><dd>{nationwideCoverageStats.totalPrefectures}/47</dd></div>
            <div><dt>現行計画を確認</dt><dd>{nationwideCoverageStats.currentPlanConfirmedPrefectures}都道府県</dd></div>
            <div><dt>Reviewed数値目標</dt><dd>{allPolicyTargetStats.reviewedTargets}件</dd></div>
            <div><dt>公開済み評価</dt><dd>{catalogStats.publishedEvaluations}件</dd></div>
          </dl>
          <p>全国登録と公開済みデータは別です。現在は{nationwideCoverageStats.currentPlanConfirmedPrefectures}都道府県の現行計画を確認し、福岡県の政策データを人が照合して公開しています。</p>
        </aside>
      </section>
      <section className="section">
        <div className="sectionIntro"><p className="eyebrow">From documents to decisions</p><h2>PDFの山を、判断できる情報へ。</h2><p>予算書、決算書、事業評価、契約、議事録、選挙公報は別々に公開されています。Jichi Insightは、一つの事業を起点に、それらを検証可能な形で接続します。</p></div>
        <div className="pillarGrid">{pillars.map((pillar) => <article className="pillarCard" key={pillar.label}><p>{pillar.label}</p><h3>{pillar.title}</h3><span>{pillar.text}</span></article>)}</div>
      </section>
      <section className="section">
        <div className="sectionIntro sectionIntro--row"><div><p className="eyebrow">Nationwide &amp; deep dive</p><h2>全国の入口を整え、福岡で深くつなぐ。</h2></div><p>47都道府県の整備状況を同じ基準で見える化しながら、福岡県・福岡市・北九州市では財政、政策、首長、議会を縦につなぐモデルを作っています。</p></div>
        <div className="coveragePathGrid">
          <article className="coveragePathCard coveragePathCard--nationwide">
            <div><p>全国カバレッジ</p><StatusBadge label={`${nationwideCoverageStats.currentPlanConfirmedPrefectures}都道府県で現行計画確認`} tone="progress" /></div>
            <h3>47都道府県の「どこまで確認できたか」を探す。</h3>
            <p>登録、公式入口、計画索引、現行性、Reviewed公開を分けて表示します。</p>
            <Link href="/municipalities">全国カバレッジを見る</Link>
          </article>
          <article className="coveragePathCard">
            <div><p>福岡県の深掘り</p><StatusBadge label={`数値目標 ${allPolicyTargetStats.reviewedTargets}件`} tone="verified" /></div>
            <h3>計画の原文から、目標と未接続範囲を確認する。</h3>
            <p>実績がない目標に達成率を付けず、分かっていることと未確認を分けます。</p>
            <Link href="/policies">福岡県の政策体系を見る</Link>
          </article>
        </div>
        <div className="municipalityGrid">{Object.entries(municipalityMeta).map(([key, municipality]) => <article className="municipalityCard" key={key}><div className="municipalityCardTop"><span>{municipality.type}</span><StatusBadge label={municipality.status} tone="progress" /></div><h3>{municipality.name}</h3><p>{municipality.summary}</p><Link href={municipality.href ?? `/sources#${key}`}>{municipality.href ? "自治体ページを見る" : "公式資料を見る"}</Link></article>)}</div>
      </section>
      <section className="section principlesSection">
        <div><p className="eyebrow">Trust before scale</p><h2>評価より先に、根拠を見せる。</h2></div>
        <div className="principleGrid"><p>一次資料を優先し、未確認情報を推測で埋めません。</p><p>事実、比較、解釈、評価を同じ文章に混ぜません。</p><p>政策思想や政党ではなく、具体性、実行、成果、説明責任を見ます。</p><p>データ不足なら、無理に点数を出さず「評価不能」と示します。</p></div>
        <Link className="invertedAction" href="/methodology">評価方法を確認する</Link>
      </section>
      <SiteFooter />
    </main>
  );
}
