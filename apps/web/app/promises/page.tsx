import type { Metadata } from "next";
import Link from "next/link";
import { SiteHeader } from "@/components/SiteHeader";
import { SiteFooter } from "@/components/SiteFooter";
import { currentExecutiveTerms, executiveMunicipality, promisesForExecutive, evidenceForPromise, formatDateJa } from "@/lib/executives";
import { promiseSourceDetails } from "@/lib/promiseSources";
import { sourceConfidenceLabel } from "@/lib/statusLabels";
import { fukuokaCityProjectData } from "@/lib/fukuokaCityProjects";
import { fukuokaPrefectureProjectData } from "@/lib/fukuokaPrefectureProjects";
import { kitakyushuProjectData } from "@/lib/kitakyushuProjects";
import styles from "./page.module.css";

export const metadata: Metadata = {
  title:"首長公約レジストリ｜原文・出典・評価材料",
  description:"福岡県知事・福岡市長・北九州市長の登録済み公約を原文と証拠に基づき掲載。達成率や首長の点数は公開しません。",
};
const projectGroups = [
  ["fukuoka-prefecture",fukuokaPrefectureProjectData.projects],
  ["fukuoka-city",fukuokaCityProjectData.projects],
  ["kitakyushu-city",kitakyushuProjectData.projects],
] as const;
function relatedProject(id:string) {
  for(const [area,projects] of projectGroups) {
    const project=projects.find(p=>p.id===id);
    if(project) return {area,project};
  }
  return null;
}
const progressLabel:Record<string,string> = {
  not_assessable:"評価材料なし（未接続）",
  in_progress:"進行中（関連事業に基づく記録）",
  achieved:"達成（記録された判定）",
  mostly_achieved:"概ね達成（記録された判定）",
  partially_achieved:"一部達成（記録された判定）",
  not_started:"未着手（確認記録）",
  changed:"変更（公式説明を要確認）",
  abandoned:"撤回（公式説明を要確認）",
};
export default function PromisesPage() {
  return <><SiteHeader/><main className="pageShell">
    <header className={styles.hero}><p className="eyebrow">Reviewed promise registry</p><h1>首長公約の原文と根拠</h1>
      <p>公約を首長・選挙ごとに整理しています。事業との関連は確定的な成果や達成を意味しません。未接続は未着手・未達を意味しません。首長のスコア、達成率、ランキングは表示しません。</p>
    </header>
    {currentExecutiveTerms.map(term=>{
      const municipality=executiveMunicipality(term);
      const promises=promisesForExecutive(term).filter(p=>p.review_status==="reviewed");
      const areas=[...new Set(promises.map(p=>p.policy_area))];
      return <section className={styles.area} key={term.id} id={municipality.key}>
        <h2>{municipality.name}・{term.person_name}</h2>
        <p className={styles.meta}>{term.office==="governor"?"知事":"市長"} / 選挙日：{formatDateJa(term.election_date)} / 任期開始：{formatDateJa(term.term_start)} / Reviewed 公約原文</p>
        {areas.map(policyArea=><section key={policyArea} className={styles.policy}><h3>政策の柱：{policyArea}</h3>
          <div className={styles.grid}>{promises.filter(p=>p.policy_area===policyArea).map(p=>{
            const evidence=evidenceForPromise(p);
            return <article key={p.id} id={p.id} className={styles.card}>
              <p className={styles.meta}>公約原文（改変なし）・{p.statement_type}</p>
              <blockquote>{p.original_text}</blockquote>
              {p.plain_summary ? <p className={styles.summary}><strong>平易な要約（原文ではありません）</strong>：{p.plain_summary}</p> : null}
              <p className={styles.status}>進捗記録：{progressLabel[p.progress_state] ?? p.progress_state}</p>
              {p.progress_state==="not_assessable" ? <p className={styles.meta}>評価につながる資料が現時点で接続されていません。実施の有無を判定したものではありません。</p> : null}
              {p.target !== null ? <div className={styles.target}><strong>公約の目標（target）</strong><p>{String(p.target)}</p><small>実績：未登録（目標値を実績値として使用しません）</small></div> : null}
              <div className={styles.links}><h4>関連事業（自動推定を含む・要確認）</h4>
                {p.related_project_ids.length ? <ul>{p.related_project_ids.map(projectId=>{
                  const match=relatedProject(projectId);
                  return <li key={projectId}>{match ? <Link href={`/projects/${match.area}/${encodeURIComponent(match.project.series_id)}`}>{match.project.official_title}</Link> : "事業レコード参照ID："+projectId}
                    <span> / 確信度：低（inferred） / Evidence: needs_review</span></li>;
                })}</ul> : <p>接続事業なし（未着手・未達の意味ではありません）</p>}
              </div>
              <div className={styles.links}><h4>公約の出典・格付け</h4>
                {promiseSourceDetails(p.sources).map(source=><p key={source.id}>
                  {source.url ? <a href={source.url} target="_blank" rel="noreferrer">{source.title}</a> : source.id}
                  <span> / {source.review} / {source.confidence}</span>
                </p>)}
                <p>原文箇所：{p.source_location}</p>
                {municipality.key==="fukuoka-city" ? <p>原典来歴：候補者サイトを直接保存したものではなく、同時期記事の原文引用と選挙公報の見出し照合により登録しています。</p> : null}
                {municipality.key==="fukuoka-prefecture" ? <p>原典来歴：公式選挙公報を使用しています。</p> : null}
                <p>記録の確認：{p.review_status} / {sourceConfidenceLabel(p.confidence)}</p>
                <p>証拠パケット：{evidence?.review_status ?? "未収録"}。未解決事項：{evidence?.open_questions.length ? evidence.open_questions.join("／") : "記載なし"}</p>
              </div>
            </article>;
          })}</div>
        </section>)}
      </section>;
    })}
    <p><Link href="/executives">首長台帳に戻る</Link></p>
  </main><SiteFooter/></>;
}
