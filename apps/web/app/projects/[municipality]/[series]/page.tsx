import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { SiteHeader } from "@/components/SiteHeader";
import { SiteFooter } from "@/components/SiteFooter";
import { ProjectReview } from "@/components/ProjectReview";
import { projectRegistry, isProjectArea } from "@/lib/projectRegistry";
import styles from "@/components/ProjectReview.module.css";

type Props = {params:Promise<{municipality:string;series:string}>};
export function generateStaticParams() {
  return Object.entries(projectRegistry).flatMap(([municipality, area])=>
    [...new Set(area.projects.map(p=>p.series_id))].map(series=>({municipality,series})));
}
export async function generateMetadata({params}:Props):Promise<Metadata>{
  const {municipality,series}=await params;
  if(!isProjectArea(municipality)) return {};
  const project=projectRegistry[municipality].projects.find(p=>p.series_id===series);
  return {title:project ? `${project.official_title}｜${projectRegistry[municipality].name}` : "事業未登録"};
}
export default async function ProjectDetailPage({params}:Props){
  const {municipality,series}=await params;
  if(!isProjectArea(municipality)) notFound();
  const area=projectRegistry[municipality];
  const annual=area.projects.filter(p=>p.series_id===series && p.review_status==="reviewed").sort((a,b)=>a.fiscal_year-b.fiscal_year);
  if(!annual.length) notFound();
  return <><SiteHeader/><main className="pageShell"><h1>{annual[0].official_title}</h1>
    <p>{area.name}の公式資料による事業記録。資料段階ごとに予算と決算を分離し、評価は自治体の公式判断だけを表示します。</p>
    {annual.map(record=><div key={record.id}>
      <h2>{record.fiscal_year}年度の記録</h2>
      <ProjectReview area={municipality} record={record} kpis={area.kpis.filter(k=>k.project_id===record.id && k.review_status==="reviewed")} />
      <section className={styles.detail}><h2>証拠パケット</h2>
        {area.evidencePackets.filter(p=>p.subject_id===record.id).map(packet=><div key={packet.id}><p>レビュー状態：{packet.review_status}</p>
          <p>未解決の確認事項：{packet.open_questions?.length ? packet.open_questions.join("／") : "記載なし"}</p></div>)}
      </section>
    </div>)}
  </main><SiteFooter/></>;
}
