import type { Metadata } from "next";
import Link from "next/link";
import { SiteHeader } from "@/components/SiteHeader";
import { SiteFooter } from "@/components/SiteFooter";
import { projectRegistry, type ProjectArea } from "@/lib/projectRegistry";
import { canonicalFor } from "@/lib/pageMetadata";
import styles from "@/components/ProjectReview.module.css";

export const metadata: Metadata = { title:"重点事業｜公式評価と予算から成果への記録", alternates:{canonical:canonicalFor("/projects")} };
export default function ProjectsPage(){
  const areas = Object.entries(projectRegistry) as [ProjectArea,(typeof projectRegistry)[ProjectArea]][];
  return <><SiteHeader/><main className="pageShell"><h1>重点事業</h1>
    <p>3自治体の Reviewed 事業レコードを掲載しています。公式母集団から各政策の柱ごとに掲載順で選定したものであり、金額順・優先度順・独自ランキングではありません。</p>
    <p>確認できること：福岡県・福岡市・北九州市の登録済み重点事業の予算・KPI・公式評価。まだ確認できないこと：3自治体のすべての事業を網羅した一覧ではありません。未収録の項目を推測で補いません。</p>
    {areas.map(([key,area])=><section className={styles.section} key={key}>
      <h2>{area.name}｜登録事業</h2>
      <p className={styles.meta}>母集団：{area.selection.population?.description ?? "詳細未収録"}</p>
      <p className={styles.meta}>選定方法：{area.selection.selection_rule?.description ?? "選定規則未収録"}</p>
      <p className={styles.meta}>選定カタログ更新：{area.selection.updated_at ?? "未収録"}。選定・除外理由は Reviewed 選定カタログで管理しています。</p>
      <div className={styles.cards}>{area.projects.filter(p=>p.review_status==="reviewed").map(p=><article className={styles.card} key={p.id}>
        <p className={styles.meta}>{p.fiscal_year}年度 / {p.policy_area}</p><h3>{p.official_title}</h3><p>{p.plain_title}</p>
        <Link href={`/projects/${key}/${encodeURIComponent(p.series_id)}`}>予算・KPI・公式評価を見る</Link></article>)}</div>
    </section>)}
  </main><SiteFooter/></>;
}
