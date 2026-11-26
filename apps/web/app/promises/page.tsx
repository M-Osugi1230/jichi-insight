import type { Metadata } from "next";
import Link from "next/link";
import { SiteHeader } from "@/components/SiteHeader";
import { SiteFooter } from "@/components/SiteFooter";
import { currentExecutiveTerms, promiseRecords, executiveMunicipality, promisesForExecutive, evidenceForPromise, evidenceForExecutive, formatDateJa } from "@/lib/executives";
import { promiseSourceDetails } from "@/lib/promiseSources";
import { sourceConfidenceLabel } from "@/lib/statusLabels";
import { fukuokaCityProjectData } from "@/lib/fukuokaCityProjects";
import { fukuokaPrefectureProjectData } from "@/lib/fukuokaPrefectureProjects";
import { kitakyushuProjectData, type ProjectRecord } from "@/lib/kitakyushuProjects";
import aichiProjects from "../../../../data/reviewed/aichi-prefecture/projects.json";
import styles from "./page.module.css";

export const metadata: Metadata = {
  title:"首長公約レジストリ｜原文・出典・評価材料",
  description:"登録済みの知事・市長の公約原文と証拠を掲載。公約未登録の首長は区別し、達成率や首長の点数は公開しません。",
};
const projectGroups = [
  ["fukuoka-prefecture",fukuokaPrefectureProjectData.projects],
  ["fukuoka-city",fukuokaCityProjectData.projects],
  ["kitakyushu-city",kitakyushuProjectData.projects],
  ["aichi-prefecture",aichiProjects as ProjectRecord[]],
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
  const reviewedPromiseCount = promiseRecords.filter((item) =>
    item.review_status === "reviewed" || item.review_status === "verified"
  ).length;
  return <><SiteHeader/><main className="pageShell">
    <header className={styles.hero}><p className="eyebrow">Reviewed promise registry</p><h1>首長公約の原文と根拠</h1>
      <p>Reviewed公約 {reviewedPromiseCount.toLocaleString("ja-JP")}件／登録首長term {currentExecutiveTerms.length}件。</p>
      <p>公約を首長・選挙ごとに整理しています。事業との関連は確定的な成果や達成を意味しません。未接続は未着手・未達を意味しません。首長のスコア、達成率、ランキングは表示しません。</p>
      <p>確認できること：本サイトに Reviewed 公約が登録されている首長の公約原文と根拠。公約が未登録の首長については未登録と表示し、公約の不存在や未実施を意味しません。まだ確認できないこと：すべての公約の進捗評価は提供していません。評価材料がない公約は「評価材料なし（未接続）」と表示します。</p>
    </header>
    {currentExecutiveTerms.map(term=>{
      const municipality=executiveMunicipality(term);
      const promises=promisesForExecutive(term).filter(p=>p.review_status==="reviewed");
      const evidence=evidenceForExecutive(term);
      const termStartClaim=evidence?.claims.find(claim=>claim.field==="term_start");
      const vacancyElectionStart=municipality.key==="yokohama-city" &&
        Boolean(termStartClaim?.statement.includes("欠員選挙") &&
          termStartClaim?.review_note?.includes("欠員選挙"));
      const areas=[...new Set(promises.map(p=>p.policy_area))];
      return <section className={styles.area} key={term.id} id={municipality.key}>
        <h2>{municipality.name}・{term.person_name}</h2>
        <p className={styles.meta}>{term.office==="governor"?"知事":"市長"} / 選挙日：{formatDateJa(term.election_date)} / 任期開始：{formatDateJa(term.term_start)} / 任期満了：{formatDateJa(term.term_end)} / {promises.length > 0 ? `Reviewed 公約原文 ${promises.length}件` : "公約原文：未登録"}</p>
        {vacancyElectionStart ? <p className={styles.meta}>任期起算：欠員選挙による選挙日起算</p> : null}
        {promises.length === 0 ? <p className={styles.meta}>本サイトにはこの首長の Reviewed 公約が登録されていません。公約が存在しない、または公表されていないことを示すものではありません。</p> : null}
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
                  return <li key={projectId}>{match ? (match.area === "aichi-prefecture"
                    ? <span>{match.project.official_title}（愛知県・関連事業の詳細ページは Web 登録後に公開）</span>
                    : <Link href={`/projects/${match.area}/${encodeURIComponent(match.project.series_id)}`}>{match.project.official_title}</Link>)
                    : "事業レコード参照ID："+projectId}
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
                {municipality.key==="aichi-prefecture" ? <p>原典来歴：2023年愛知県知事選挙の公式選挙公報を使用しています。資料上の★印項目を基に10件登録。事業との関連は low / inferred・要レビューであり、進捗記録は事業の成果・達成の確定判定ではありません。</p> : null}
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
