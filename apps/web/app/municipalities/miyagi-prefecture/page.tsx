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
  miyagiFinance, miyagiPlanReview, miyagiFinanceSources,
  miyagiBudgetRecord, miyagiEvidenceForRecord,
} from "@/lib/miyagiFinance";
import { assemblies } from "@/lib/assemblyRegistry";
import { projectRegistry } from "@/lib/projectRegistry";
import styles from "../fukuoka-prefecture/page.module.css";
import projectStyles from "@/components/ProjectReview.module.css";

export const metadata: Metadata = {
  alternates: { canonical: canonicalFor("/municipalities/miyagi-prefecture") },
  title: "宮城県｜新・宮城の将来ビジョン・財政・重点施策・知事公約・県議会",
  description: "新・宮城の将来ビジョン、FY2026一般会計当初予算、FY2022〜2024普通会計決算、村井嘉浩知事の公約4件、登録施策10系列、第401回宮城県議会の議員別表決記録を確認します。",
};

export default function MiyagiPrefecturePage() {
  const prefectureId = miyagiFinance.municipality.id;
  const projects = projectRegistry["miyagi-prefecture"];
  const reviewedProjects = Array.from(
    projects.projects.filter((project) => project.review_status === "reviewed")
      .sort((a, b) => a.fiscal_year - b.fiscal_year)
      .reduce((map, project) => map.set(project.series_id, project),
        new Map<string, (typeof projects.projects)[number]>()),
  ).map(([, project]) => project);
  const governor = currentExecutiveTerms.find((term) =>
    term.municipality_id === prefectureId && term.office === "governor" &&
    term.status === "current" &&
    (term.review_status === "reviewed" || term.review_status === "verified"),
  );
  const governorPromises = governor ? promisesForExecutive(governor).filter(
    (promise) => promise.review_status === "reviewed" || promise.review_status === "verified",
  ) : [];
  const electionEvidence = governor ? evidenceForExecutive(governor) : undefined;
  const electionClaim = electionEvidence?.claims.find((claim) => claim.field === "election_date");

  const revenue = miyagiBudgetRecord("total_revenue");
  const tax = miyagiBudgetRecord("local_tax");
  const spending = miyagiBudgetRecord("total_expenditure");
  const settlements = miyagiFinance.records.filter((record) =>
    record.review_status === "reviewed" && record.stage === "settlement" &&
    record.account_type === "ordinary",
  );
  const taxShare = revenue?.amount_yen && tax?.amount_yen
    ? 100 * tax.amount_yen / revenue.amount_yen : null;

  const assembly = assemblies["miyagi-prefecture"];
  const memberVoteDisclosure = assembly.disclosure.items.find(
    (item) => item.item === "member_votes",
  );
  const factionDisclosure = assembly.disclosure.items.find(
    (item) => item.item === "faction_votes",
  );
  const structure = miyagiPlanReview.records.find(
    (record) => record.id === "miyagi-plan-policy-structure",
  );

  return (
    <>
      <SiteHeader />
      <main>
        <div className="pageShell">
          <section className={styles.hero}>
            <div>
              <div className={styles.heroMeta}>
                <span>都道府県</span><StatusBadge label="Reviewed" tone="verified" />
              </div>
              <h1>宮城県</h1>
              <p>「新・宮城の将来ビジョン」（2021〜2030年度）、2026年度成立後一般会計当初予算、
                2022〜2024年度普通会計決算、村井嘉浩知事の公約4件、
                施策単位の重点事業10系列と宮城県議会第401回定例会を、公式資料の公表範囲で確認します。</p>
            </div>
            <dl className={styles.heroFacts}>
              <div><dt>Reviewed 財政レコード</dt><dd>{miyagiFinance.records.length}件</dd></div>
              <div><dt>普通会計決算</dt><dd>{settlements.length}件（FY2022–2024）</dd></div>
              <div><dt>Reviewed 重点施策</dt><dd>{reviewedProjects.length}系列</dd></div>
              <div><dt>最終確認</dt><dd>{miyagiFinance.municipality.last_verified_at}</dd></div>
            </dl>
          </section>

          <MunicipalityDiscoveryPanel
            officialCode={miyagiFinance.municipality.official_code}
            planHref="#plan-title"
            budgetHref="#finance-headline-title"
            settlementHref="#fiscal-detail"
            fiscalDetailHref="#fiscal-detail"
            projectHref="#priority-projects"
          />

          <section className={styles.scope} aria-labelledby="scope-title">
            <div><p className="eyebrow">Scope</p><h2 id="scope-title">計画・財政・施策評価・選挙・議会の単位を混同しない。</h2></div>
            <div>
              <p>最上位計画は「新・宮城の将来ビジョン」（2021〜2030年度）。
                柱「1＋4」（復興サポートと政策推進の基本方向4つ）、
                政策8、施策18の体系です。現行は中期実施計画（2025〜2027年度、令和8年2月改定版）です。</p>
              <p>FY2026一般会計当初予算は2026年3月18日の第399回定例会で原案可決された値です。
                FY2022〜2024普通会計決算とは年度・会計区分を分けて表示します。</p>
              <p>重点事業の登録単位は「施策」（10系列）です。
                県の施策評価に基づく公式評定・目標指標と、
                令和6年度事業の施策決算額を区別します。
                令和7年度事業の施策全体の決算額は未公表で、主要事業の決算額の合計で補完しません。</p>
            </div>
          </section>

          <section className={styles.scope} aria-labelledby="plan-title">
            <div><p className="eyebrow">Plan review</p>
              <h2 id="plan-title">新・宮城の将来ビジョン</h2>
              <p>Reviewed：{miyagiPlanReview.reviewed_at}</p></div>
            <div>
              {miyagiPlanReview.records.filter((record) => record.decision === "accepted").map((record) => (
                <article key={record.id}>
                  <h3>{record.title}</h3>
                  <p>{record.statement}</p>
                  <p><a href={record.source_url} target="_blank" rel="noopener noreferrer">公式出典：{record.title}</a></p>
                </article>
              ))}
              <p>{structure?.value ?? "政策8・施策18"}</p>
            </div>
          </section>

          <section className={styles.headline} aria-labelledby="finance-headline-title">
            <div className="sectionIntro">
              <p className="eyebrow">FY2026 enacted initial budget</p>
              <h2 id="finance-headline-title">2026年度に成立した一般会計当初予算</h2>
              <p>2026年3月18日、第399回定例会で第1号議案
                「令和8年度宮城県一般会計予算」が原案可決。
                金額は公式登録データの円換算値です（千円単位の公表値に基づきます）。</p>
            </div>
            <div className={styles.metricGrid}>
              {[
                { label: "一般会計当初予算（歳入総額）", record: revenue },
                { label: "県税収入", record: tax },
                { label: "一般会計当初予算（歳出総額）", record: spending },
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
                <span>一般会計当初予算に占める県税収入</span>
                <strong>{taxShare === null ? "算出不可" : `${taxShare.toFixed(1)}%`}</strong>
                <small>Jichi Insight による単純計算</small>
              </article>
            </div>
          </section>

          <div id="fiscal-detail" style={{ scrollMarginTop: 90 }}>
            <FiscalReview municipality="宮城県" records={miyagiFinance.records} sources={miyagiFinanceSources} />
          </div>
          <section className={styles.evidence} aria-labelledby="evidence-title">
            <div className="sectionIntro">
              <p className="eyebrow">Evidence trail</p>
              <h2 id="evidence-title">予算額のReviewed証拠パケット</h2>
            </div>
            <div className={styles.evidenceGrid}>
              {[revenue, tax, spending].filter((record) => record !== undefined).map((record) => (
                <EvidencePanel key={record.id} record={record} packet={miyagiEvidenceForRecord(record.id)} />
              ))}
            </div>
          </section>

          <section id="priority-projects" className={styles.headline} aria-labelledby="projects-title">
            <div className="sectionIntro">
              <p className="eyebrow">Reviewed priority projects</p>
              <h2 id="projects-title">施策単位の重点事業10系列</h2>
              <p>新・宮城の将来ビジョンの政策8・施策18から施策10系列を選定。
                県の施策評価と施策決算額の対象年度を分け、未公表金額を推計しません。
                <Link href="/projects#miyagi-prefecture"> 宮城県の重点事業一覧を見る</Link></p>
            </div>
            <div className={projectStyles.cards}>
              {reviewedProjects.map((project) => (
                <article className={projectStyles.card} key={project.series_id}>
                  <p className={projectStyles.meta}>{project.fiscal_year}年度／{project.policy_area}／Reviewed</p>
                  <h3>{project.official_title}</h3>
                  <p>{project.plain_title}</p>
                  <p>公式施策評価：{project.official_evaluation?.rating ?? "未登録"}</p>
                  <details>
                    <summary>施策評価・決算・KPI・出典を確認</summary>
                    <ProjectReview area="miyagi-prefecture" record={project}
                      kpis={projects.kpis.filter((kpi) => kpi.project_id === project.id && kpi.review_status === "reviewed")} />
                  </details>
                  <p><Link href={`/projects/miyagi-prefecture/${encodeURIComponent(project.series_id)}`}>年度別詳細を見る</Link></p>
                </article>
              ))}
            </div>
          </section>

          <section className={styles.scope} aria-labelledby="governor-title">
            <div><p className="eyebrow">Executive term</p><h2 id="governor-title">村井嘉浩知事の現任期と公約</h2>
              <p><Link href="/executives">首長台帳を見る</Link></p></div>
            <div>{governor ? (
              <>
                <h3>{governor.person_name} 知事</h3>
                <p>任期：{formatDateJa(governor.term_start)} 〜 {formatDateJa(governor.term_end)}</p>
                <p>選挙日：{formatDateJa(governor.election_date)} ／ 登録状態：{governor.review_status}</p>
                <p>得票数：340,190票（2025年10月26日執行の宮城県知事選挙）</p>
                <p>Reviewed 公約原文：{governorPromises.length}件</p>
                <p><Link href="/promises#miyagi-prefecture">村井嘉浩知事の公約原文と根拠を見る</Link></p>
                {manifestoSourcesForExecutive(governor).map((source) => (
                  <p key={source.id}>公約原典：<a href={source.url} target="_blank" rel="noopener noreferrer">{source.title}</a></p>
                ))}
                {sourcesForExecutive(governor).map((source) => (
                  <p key={source.id}><a href={source.url} target="_blank" rel="noopener noreferrer">{source.title}</a></p>
                ))}
                {electionClaim ? <details><summary>2025年知事選挙・任期の根拠</summary>
                  <p>{electionClaim.statement}</p></details> : null}
                {electionEvidence?.open_questions.length ? <p>未確認事項：{electionEvidence.open_questions.join("／")}</p> : null}
              </>
            ) : <p>知事の現任期はReviewed台帳に未登録です。</p>}</div>
          </section>

          <section id="assembly" className={styles.scope} aria-labelledby="assembly-title">
            <div><p className="eyebrow">Reviewed assembly · Stage 4</p>
              <h2 id="assembly-title">宮城県議会・令和8年9月第401回定例会</h2>
              <p><Link href="/assemblies/miyagi-prefecture">宮城県議会の議案・議員別表決・視察を見る</Link></p></div>
            <div>
              <p>議員定数{assembly.assembly.seat_count}人、会期時点の現員56人。
                登録議案{assembly.proposals.length}件、表決{assembly.votes.length}件。
                政務活動費{assembly.expenses.length}単位、委員会調査{assembly.trips.length}件。</p>
              <p>宮城県議会の「各議員の表決状況」は、<strong>本会議の表決そのものの事後記録</strong>です。
                採決に先立って表明された会派態度の集約ではありません。
                賛否は議員個人別に公表され、会派別賛否は登録・再集計していません。</p>
              <p>{memberVoteDisclosure?.note ?? "個人別表決の公表範囲は未確認です。"}</p>
              <p>{factionDisclosure?.note ?? "会派別賛否の公表範囲は未確認です。"}</p>
            </div>
          </section>

          <section className={styles.scope} aria-labelledby="sendai-title">
            <div><p className="eyebrow">Related municipality · Sendai City</p>
              <h2 id="sendai-title">仙台市の政策・首長・市議会</h2></div>
            <div>
              <p>仙台市長は郡和子。市長公約4件、登録事業10系列（仙台市の公式自己評価つき）を別の自治体の実績として表示します。</p>
              <p><Link href="/municipalities/sendai-city">仙台市の専用ページを見る</Link></p>
              <p><Link href="/assemblies/sendai-city">仙台市議会の会派別賛否を見る</Link></p>
            </div>
          </section>

          <section className={styles.scope} aria-labelledby="sources-title">
            <div><p className="eyebrow">Primary sources</p><h2 id="sources-title">公式資料と根拠</h2></div>
            <div><ul>{miyagiFinanceSources.map((source) => (
              <li key={source.id}><a href={source.url} target="_blank" rel="noopener noreferrer">{source.title}</a>
                <span>（{source.review_status}・索引更新 {source.indexed_at}）</span></li>
            ))}</ul></div>
          </section>
          <section className={styles.notAssessed}>
            <div><p className="eyebrow">Not assessed yet</p><h2>まだ評価していないこと</h2></div>
            <ul>
              <li>知事公約4件の達成度や政策との因果関係は独自判定していません。</li>
              <li>主要事業の決算額を施策全体の決算額に見立てていません。</li>
              <li>議員別表決から会派別の態度を再構成していません。</li>
            </ul>
          </section>
          <nav className={styles.bottomNav} aria-label="関連ページ">
            <Link href="/municipalities">自治体一覧</Link>
            <Link href="/projects#miyagi-prefecture">宮城県の施策10系列</Link>
            <Link href="/promises#miyagi-prefecture">知事公約{governorPromises.length}件</Link>
            <Link href="/assemblies/miyagi-prefecture">宮城県議会</Link>
            <Link href="/municipalities/sendai-city">仙台市</Link>
            <Link href="/methodology">評価方法</Link>
          </nav>
        </div>
      </main>
      <SiteFooter />
    </>
  );
}
