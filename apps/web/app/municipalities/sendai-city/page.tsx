import type { Metadata } from "next";
import Link from "next/link";
import { SiteHeader } from "@/components/SiteHeader";
import { SiteFooter } from "@/components/SiteFooter";
import { StatusBadge } from "@/components/StatusBadge";
import { MunicipalityDiscoveryPanel } from "@/components/MunicipalityDiscoveryPanel";
import { FiscalReview } from "@/components/FiscalReview";
import { EvidencePanel } from "@/components/EvidencePanel";
import { ProjectReview } from "@/components/ProjectReview";
import {
  currentExecutiveTerms, evidenceForExecutive, formatDateJa,
  manifestoSourcesForExecutive, promisesForExecutive, sourcesForExecutive,
} from "@/lib/executives";
import { formatCompactYen, formatExactYen } from "@/lib/finance";
import { canonicalFor } from "@/lib/pageMetadata";
import {
  sendaiFinance, sendaiPlanReview, sendaiFinanceSources,
  sendaiBudgetRecord, sendaiEvidenceForRecord,
} from "@/lib/sendaiFinance";
import { assemblies } from "@/lib/assemblyRegistry";
import { projectRegistry } from "@/lib/projectRegistry";
import styles from "../fukuoka-prefecture/page.module.css";
import projectStyles from "@/components/ProjectReview.module.css";

export const metadata: Metadata = {
  alternates: { canonical: canonicalFor("/municipalities/sendai-city") },
  title: "仙台市｜基本計画・財政・市の自己評価・郡和子市長公約・市議会",
  description: "仙台市基本計画2021-2030、FY2026一般会計当初予算、郡和子市長の公約4件、事業単位10系列と市の公式自己評価、令和8年第3回仙台市議会の会派別賛否を確認します。",
};

export default function SendaiCityPage() {
  const cityId = sendaiFinance.municipality.id;
  const projects = projectRegistry["sendai-city"];
  const reviewedProjects = Array.from(
    projects.projects.filter((project) => project.review_status === "reviewed")
      .sort((a, b) => a.fiscal_year - b.fiscal_year)
      .reduce((map, project) => map.set(project.series_id, project),
        new Map<string, (typeof projects.projects)[number]>()),
  ).map(([, project]) => project);
  const mayor = currentExecutiveTerms.find((term) =>
    term.municipality_id === cityId && term.office === "mayor" &&
    term.status === "current" &&
    (term.review_status === "reviewed" || term.review_status === "verified"),
  );
  const mayorPromises = mayor ? promisesForExecutive(mayor).filter(
    (promise) => promise.review_status === "reviewed" || promise.review_status === "verified",
  ) : [];
  const electionEvidence = mayor ? evidenceForExecutive(mayor) : undefined;
  const electionClaim = electionEvidence?.claims.find((claim) => claim.field === "election_date");
  const revenue = sendaiBudgetRecord("total_revenue");
  const tax = sendaiBudgetRecord("local_tax");
  const taxShare = revenue?.amount_yen && tax?.amount_yen
    ? 100 * tax.amount_yen / revenue.amount_yen : null;
  const assembly = assemblies["sendai-city"];
  const factionDisclosure = assembly.disclosure.items.find((item) => item.item === "faction_votes");
  const memberDisclosure = assembly.disclosure.items.find((item) => item.item === "member_votes");

  return (
    <>
      <SiteHeader />
      <main>
        <div className="pageShell">
          <section className={styles.hero}>
            <div>
              <div className={styles.heroMeta}>
                <span>政令指定都市</span><StatusBadge label="Reviewed" tone="verified" />
              </div>
              <h1>仙台市</h1>
              <p>仙台市基本計画2021-2030、実施計画2024-2026、2026年度成立後一般会計当初予算、
                郡和子市長の現任期と公約4件、事業単位の重点事業10系列、
                令和8年第3回仙台市議会の会派別賛否を、公表資料の単位で表示します。</p>
            </div>
            <dl className={styles.heroFacts}>
              <div><dt>Reviewed 財政レコード</dt><dd>{sendaiFinance.records.length}件</dd></div>
              <div><dt>Reviewed 重点事業</dt><dd>{reviewedProjects.length}系列</dd></div>
              <div><dt>市長公約</dt><dd>{mayorPromises.length}件</dd></div>
              <div><dt>登録データ最終確認</dt><dd>{sendaiFinance.municipality.last_verified_at}</dd></div>
            </dl>
          </section>

          <MunicipalityDiscoveryPanel
            officialCode={sendaiFinance.municipality.official_code}
            planHref="#plan-title"
            budgetHref="#finance-headline-title"
            settlementHref="#fiscal-detail"
            fiscalDetailHref="#fiscal-detail"
            projectHref="#priority-projects"
          />

          <section className={styles.scope} aria-labelledby="scope-title">
            <div><p className="eyebrow">Scope</p><h2 id="scope-title">事業単位の市の自己評価を、そのまま表示する。</h2></div>
            <div>
              <p>「仙台市基本計画2021-2030」の計画期間は2021〜2030年度、
                現行「仙台市実施計画2024-2026」は2024〜2026年度です。
                8つのチャレンジプロジェクトと市政運営を合わせた9グループ・108事業から、
                事業単位の重点事業10系列を選定しました。</p>
              <p>仙台市の公式自己評価（◎・○・△・×）を、事業単位で表示します。
                これは市の自己評価であり、Jichi Insight独自の評価ではありません。
                事業単位の当初予算額は公表資料に対応値がないため未登録で、0円ではありません。</p>
              <p>FY2026一般会計当初予算とFY2024の一般会計決算は
                年度と予算・決算を区別して表示します。</p>
            </div>
          </section>

          <section className={styles.scope} aria-labelledby="plan-title">
            <div><p className="eyebrow">Plan review</p><h2 id="plan-title">仙台市基本計画2021-2030・実施計画2024-2026</h2>
              <p>Reviewed：{sendaiPlanReview.reviewed_at}</p></div>
            <div>
              {sendaiPlanReview.records.filter((record) => record.decision === "accepted").map((record) => (
                <article key={record.id}>
                  <h3>{record.title}</h3>
                  <p>{record.statement}</p>
                  <p><a href={record.source_url} target="_blank" rel="noopener noreferrer">公式出典：{record.title}</a></p>
                </article>
              ))}
            </div>
          </section>

          <section className={styles.headline} aria-labelledby="finance-headline-title">
            <div className="sectionIntro">
              <p className="eyebrow">FY2026 enacted initial budget</p>
              <h2 id="finance-headline-title">2026年度に成立した一般会計当初予算</h2>
              <p>第14号議案「令和8年度仙台市一般会計予算」は2026年3月12日に原案可決。
                金額は議案本文の千円単位の公表数値を円に換算した登録値です。
                概数7,306億円に置き換えません。</p>
            </div>
            <div className={styles.metricGrid}>
              {[
                { label: "一般会計当初予算（歳入総額）", record: revenue },
                { label: "市税収入", record: tax },
              ].map(({ label, record }) => (
                <article className={styles.metricCard} key={label}>
                  <span>{label}</span>
                  <strong>{formatCompactYen(record?.amount_yen ?? null)}</strong>
                  <small>{formatExactYen(record?.amount_yen ?? null)}</small>
                  <p>公式資料の千円単位：{record?.amount_yen == null ? "未登録" : `${(record.amount_yen / 1000).toLocaleString("ja-JP")}千円`}</p>
                  <p>FY2026・一般会計・成立後当初予算</p>
                </article>
              ))}
              <article className={`${styles.metricCard} ${styles.derived}`}>
                <span>一般会計当初予算に占める市税収入</span>
                <strong>{taxShare === null ? "算出不可" : `${taxShare.toFixed(1)}%`}</strong>
                <small>Jichi Insightによる単純計算（公式評価ではありません）</small>
              </article>
            </div>
          </section>

          <div id="fiscal-detail" style={{ scrollMarginTop: 90 }}>
            <FiscalReview municipality="仙台市" records={sendaiFinance.records} sources={sendaiFinanceSources} />
          </div>
          <section className={styles.evidence} aria-labelledby="evidence-title">
            <div className="sectionIntro"><p className="eyebrow">Evidence trail</p>
              <h2 id="evidence-title">財政数値のReviewed証拠パケット</h2></div>
            <div className={styles.evidenceGrid}>
              {[revenue, tax].filter((record) => record !== undefined).map((record) => (
                <EvidencePanel key={record.id} record={record} packet={sendaiEvidenceForRecord(record.id)} />
              ))}
            </div>
          </section>

          <section id="priority-projects" className={styles.headline} aria-labelledby="projects-title">
            <div className="sectionIntro">
              <p className="eyebrow">Reviewed priority projects</p>
              <h2 id="projects-title">事業単位の重点事業10系列と市の自己評価</h2>
              <p>仙台市実施計画2024-2026の108事業から10系列を選定。
                市が公表した自己評価をそのまま表示し、未登録の事業別予算額は補完しません。
                <Link href="/projects#sendai-city"> 仙台市の重点事業一覧を見る</Link></p>
            </div>
            <div className={projectStyles.cards}>
              {reviewedProjects.map((project) => (
                <article className={projectStyles.card} key={project.series_id}>
                  <p className={projectStyles.meta}>{project.fiscal_year}年度／{project.policy_area}／Reviewed</p>
                  <h3>{project.official_title}</h3>
                  <p>{project.plain_title}</p>
                  <p>仙台市の公式自己評価：{project.official_evaluation?.rating ?? "未登録"}</p>
                  <p>事業単位の当初予算額：未登録（0円ではありません）</p>
                  <details><summary>自己評価・事業内容・公式出典</summary>
                    <ProjectReview area="sendai-city" record={project}
                      kpis={projects.kpis.filter((kpi) => kpi.project_id === project.id && kpi.review_status === "reviewed")} />
                  </details>
                  <p><Link href={`/projects/sendai-city/${encodeURIComponent(project.series_id)}`}>年度別詳細を見る</Link></p>
                </article>
              ))}
            </div>
          </section>

          <section className={styles.scope} aria-labelledby="mayor-title">
            <div><p className="eyebrow">Executive term</p><h2 id="mayor-title">郡和子市長の現任期と公約</h2>
              <p><Link href="/executives">首長台帳を見る</Link></p></div>
            <div>{mayor ? (
              <>
                <h3>{mayor.person_name} 市長</h3>
                <p>任期：{formatDateJa(mayor.term_start)} 〜 {formatDateJa(mayor.term_end)}</p>
                <p>選挙日：{formatDateJa(mayor.election_date)} ／ 登録状態：{mayor.review_status}</p>
                <p>得票数：204,844票（2025年8月3日執行の仙台市長選挙）</p>
                <p>Reviewed 公約原文：{mayorPromises.length}件</p>
                <p><Link href="/promises#sendai-city">郡和子市長の公約原文と根拠を見る</Link></p>
                {manifestoSourcesForExecutive(mayor).map((source) => (
                  <p key={source.id}>公約原典：<a href={source.url} target="_blank" rel="noopener noreferrer">{source.title}</a></p>
                ))}
                {sourcesForExecutive(mayor).map((source) => (
                  <p key={source.id}><a href={source.url} target="_blank" rel="noopener noreferrer">{source.title}</a></p>
                ))}
                {electionClaim ? <details><summary>2025年市長選挙・任期の根拠</summary>
                  <p>{electionClaim.statement}</p></details> : null}
                {electionEvidence?.open_questions.length ? <p>未確認事項：{electionEvidence.open_questions.join("／")}</p> : null}
              </>
            ) : <p>市長の現任期はReviewed台帳に未登録です。</p>}</div>
          </section>

          <section id="assembly" className={styles.scope} aria-labelledby="assembly-title">
            <div><p className="eyebrow">Reviewed assembly · Stage 4</p>
              <h2 id="assembly-title">仙台市議会・令和8年第3回定例会</h2>
              <p><Link href="/assemblies/sendai-city">仙台市議会の議案・会派別賛否を見る</Link></p></div>
            <div>
              <p>議員定数{assembly.assembly.seat_count}人。
                登録議案{assembly.proposals.length}件、
                表決{assembly.votes.length}件、
                会派別賛否{assembly.factionVotes.length}件。
                政務活動費{assembly.expenses.length}単位。</p>
              <p>仙台市議会が公式に公表しているのは会派別賛否です。
                会派内で賛否が分かれる議案では人数内訳が掲載されます。
                議員個人別の賛否は公表されておらず、個々の会派所属議員の投票を推測して再構成しません。</p>
              <p>{factionDisclosure?.note ?? "会派別賛否の公開範囲は未確認です。"}</p>
              <p>{memberDisclosure?.note ?? "議員別賛否の公開範囲は未確認です。"}</p>
            </div>
          </section>
          <section className={styles.scope} aria-labelledby="sources-title">
            <div><p className="eyebrow">Primary sources</p><h2 id="sources-title">公式資料と根拠</h2></div>
            <div><ul>{sendaiFinanceSources.map((source) => (
              <li key={source.id}><a href={source.url} target="_blank" rel="noopener noreferrer">{source.title}</a>
                <span>（{source.review_status}・索引更新 {source.indexed_at}）</span></li>
            ))}</ul></div>
          </section>
          <section className={styles.notAssessed}>
            <div><p className="eyebrow">Not assessed yet</p><h2>まだ評価していないこと</h2></div>
            <ul>
              <li>市長公約4件の達成度や実施施策との因果関係は独自判定していません。</li>
              <li>事業別予算額の未登録を0円とみなしていません。</li>
              <li>会派別賛否から議員個人別投票を推定していません。</li>
            </ul>
          </section>
          <nav className={styles.bottomNav} aria-label="関連ページ">
            <Link href="/municipalities">自治体一覧</Link>
            <Link href="/projects#sendai-city">仙台市の重点事業10系列</Link>
            <Link href="/promises#sendai-city">市長公約{mayorPromises.length}件</Link>
            <Link href="/assemblies/sendai-city">仙台市議会</Link>
            <Link href="/municipalities/miyagi-prefecture">宮城県</Link>
            <Link href="/methodology">評価方法</Link>
          </nav>
        </div>
      </main>
      <SiteFooter />
    </>
  );
}
