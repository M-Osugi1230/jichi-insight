import Link from "next/link";

import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { StatusBadge } from "@/components/StatusBadge";
import { catalogStats, municipalityMeta } from "@/lib/catalog";

const pillars = [
  { label: "Promise", title: "何を約束したか", text: "選挙公報、マニフェスト、総合計画を、評価可能な単位へ整理します。" },
  { label: "Money", title: "いくら使ったか", text: "当初予算、補正、執行、決算を区別し、事業・契約へ接続します。" },
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
            <Link className="primaryAction" href="/sources">公式資料の整備状況を見る</Link>
            <Link className="secondaryAction" href="/about">なぜ作るのか</Link>
          </div>
        </div>
        <aside className="heroStatus" aria-label="開発状況">
          <div className="heroStatusHeader"><StatusBadge label="Pre-alpha" tone="progress" /><span>更新 {catalogStats.updatedAt}</span></div>
          <dl className="metricList">
            <div><dt>初期対象</dt><dd>{catalogStats.municipalities}自治体</dd></div>
            <div><dt>確認済み公式入口</dt><dd>{catalogStats.officialSources}件</dd></div>
            <div><dt>公開済み評価</dt><dd>{catalogStats.publishedEvaluations}件</dd></div>
          </dl>
          <p>現在は評価を公開する前に、公式資料の所在、出典、データ構造を整備しています。</p>
        </aside>
      </section>
      <section className="section">
        <div className="sectionIntro"><p className="eyebrow">From documents to decisions</p><h2>PDFの山を、判断できる情報へ。</h2><p>予算書、決算書、事業評価、契約、議事録、選挙公報は別々に公開されています。Jichi Insightは、一つの事業を起点に、それらを検証可能な形で接続します。</p></div>
        <div className="pillarGrid">{pillars.map((pillar) => <article className="pillarCard" key={pillar.label}><p>{pillar.label}</p><h3>{pillar.title}</h3><span>{pillar.text}</span></article>)}</div>
      </section>
      <section className="section">
        <div className="sectionIntro sectionIntro--row"><div><p className="eyebrow">Pilot municipalities</p><h2>まず、3自治体を深くつなぐ。</h2></div><p>全国を浅く並べるのではなく、財政、重点事業、公約、議会まで一本につないだモデルを完成させてから拡大します。</p></div>
        <div className="municipalityGrid">{Object.entries(municipalityMeta).map(([key, municipality]) => <article className="municipalityCard" key={key}><div className="municipalityCardTop"><span>{municipality.type}</span><StatusBadge label={municipality.status} tone="progress" /></div><h3>{municipality.name}</h3><p>{municipality.summary}</p><Link href={`/sources#${key}`}>公式資料を見る</Link></article>)}</div>
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
