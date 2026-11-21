import type { Metadata } from "next";
import Link from "next/link";

import { EvidencePanel } from "@/components/EvidencePanel";
import { FiscalReview } from "@/components/FiscalReview";
import { MunicipalityDiscoveryPanel } from "@/components/MunicipalityDiscoveryPanel";
import { ProjectReview } from "@/components/ProjectReview";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { StatusBadge } from "@/components/StatusBadge";
import {
  currentExecutiveTerms,
  evidenceForExecutive,
  formatDateJa,
  manifestoSourcesForExecutive,
  promisesForExecutive,
  sourcesForExecutive,
} from "@/lib/executives";
import { formatCompactYen, formatExactYen } from "@/lib/finance";
import {
  chibaBudgetRecord,
  chibaEvidenceForRecord,
  chibaFinance,
  chibaFinanceSources,
  chibaPlanReview,
} from "@/lib/chibaFinance";
import { canonicalFor } from "@/lib/pageMetadata";
import { assemblies } from "@/lib/assemblyRegistry";
import { projectRegistry } from "@/lib/projectRegistry";

import styles from "../fukuoka-prefecture/page.module.css";
import projectStyles from "@/components/ProjectReview.module.css";

export const metadata: Metadata = {
  alternates: { canonical: canonicalFor("/municipalities/chiba-prefecture") },
  title: "千葉県｜総合計画・財政・重点事業・熊谷俊人知事公約・県議会",
  description: "千葉県総合計画、FY2026成立後一般会計当初予算、FY2022〜2024普通会計決算、熊谷俊人知事の公約25件、重点事業10系列、千葉県議会の議案・表決と情報公開を登録データから確認します。",
};

export default function ChibaPrefecturePage() {
  const assembly = assemblies["chiba-prefecture"];
  const projects = projectRegistry["chiba-prefecture"];
  const reviewedRecords = projects.projects.filter((project) => project.review_status === "reviewed");
  const reviewedProjects = Array.from(
    reviewedRecords.slice().sort((a, b) => a.fiscal_year - b.fiscal_year)
      .reduce((map, project) => map.set(project.series_id, project), new Map<string, typeof reviewedRecords[number]>()),
  ).map(([, project]) => project);
  const governor = currentExecutiveTerms.find((term) =>
    term.municipality_id === chibaFinance.municipality.id &&
    term.office === "governor" && term.status === "current" &&
    (term.review_status === "reviewed" || term.review_status === "verified"),
  );
  const governorPromises = governor
    ? promisesForExecutive(governor).filter((promise) => promise.review_status === "reviewed" || promise.review_status === "verified")
    : [];
  const electionEvidence = governor ? evidenceForExecutive(governor) : undefined;
  const electionResult = electionEvidence?.claims.find((claim) => claim.field === "election_date");
  const budget = chibaBudgetRecord("total_revenue");
  const tax = chibaBudgetRecord("local_tax");
  const spending = chibaBudgetRecord("total_expenditure");
  const settlements = chibaFinance.records.filter((record) =>
    record.stage === "settlement" && record.account_type === "ordinary" && record.review_status === "reviewed",
  );
  const taxShare = budget?.amount_yen && tax?.amount_yen ? 100 * tax.amount_yen / budget.amount_yen : null;
  const pendingProposals = assembly.proposals.filter((proposal) => proposal.outcome === "pending");
  const policyStructure = chibaPlanReview.records.find((record) => record.id === "chiba-plan-policy-structure");

  return (
    <>
      <SiteHeader />
      <main>
        <div className="pageShell">
          <section className={styles.hero}>
            <div>
              <div className={styles.heroMeta}>
                <span>都道府県</span>
                <StatusBadge label="Reviewed" tone="verified" />
              </div>
              <h1>千葉県</h1>
              <p>
                「千葉県総合計画 ～千葉の未来をともに創る～」の計画レビュー、2026年度に成立した一般会計当初予算、
                2022〜2024年度の普通会計決算、熊谷俊人知事の現任期・公約25件、
                重点事業10系列と千葉県議会の登録情報を、公式資料の公表単位を保って掲載します。
                独自の政策達成判定や議員評価は行いません。
              </p>
            </div>
            <dl className={styles.heroFacts}>
              <div><dt>Reviewed 財政レコード</dt><dd>{chibaFinance.records.length}件</dd></div>
              <div><dt>普通会計決算</dt><dd>{settlements.length}件（FY2022–2024）</dd></div>
              <div><dt>Reviewed 重点事業</dt><dd>{reviewedProjects.length}系列</dd></div>
              <div><dt>最終確認</dt><dd>{chibaFinance.municipality.last_verified_at}</dd></div>
            </dl>
          </section>

          <MunicipalityDiscoveryPanel
            officialCode={chibaFinance.municipality.official_code}
            planHref="#plan-title"
            budgetHref="#finance-headline-title"
            settlementHref="#fiscal-detail"
            fiscalDetailHref="#fiscal-detail"
            projectHref="#priority-projects"
          />

          <section className={styles.scope} aria-labelledby="scope-title">
            <div><p className="eyebrow">Scope</p><h2 id="scope-title">計画・財政・施策・公約・議会を、公表単位を混同せずに読む。</h2></div>
            <div>
              <p>現行計画は「千葉県総合計画 ～千葉の未来をともに創る～」（2025年10月10日決定）。基本目標6、政策15、施策41、主な取組200で構成され、実施計画編は令和7〜10年度です。</p>
              <p>2026年度一般会計当初予算は成立後の値です。2022〜2024年度の普通会計決算とは会計区分と年度が異なるため、同一系列として連結しません。</p>
              <p>重点事業の登録単位は施策（10系列）です。令和7年度施策評価シートの施策計予算額・決算額を表示し、県が公表していない施策単位の公式評定は表示しません。指標単位の進捗判定を施策評定へ読み替えません。</p>
            </div>
          </section>

          <section className={styles.scope} aria-labelledby="plan-title">
            <div>
              <p className="eyebrow">Plan review</p>
              <h2 id="plan-title">千葉県総合計画 ～千葉の未来をともに創る～</h2>
              <p>Reviewed：{chibaPlanReview.reviewed_at}</p>
            </div>
            <div>
              {chibaPlanReview.records.filter((record) => record.decision === "accepted").map((record) => (
                <article key={record.id}>
                  <h3>{record.title}</h3>
                  <p>{record.statement}</p>
                  <p><a href={record.source_url} target="_blank" rel="noopener noreferrer">公式出典：{record.title}</a></p>
                </article>
              ))}
              <p>{policyStructure?.value ?? "基本目標6・政策15・施策41・主な取組200"}</p>
            </div>
          </section>

          <section className={styles.headline} aria-labelledby="finance-headline-title">
            <div className="sectionIntro">
              <p className="eyebrow">FY2026 enacted initial budget</p>
              <h2 id="finance-headline-title">2026年度に成立した一般会計当初予算</h2>
              <p>令和8年2月定例県議会で議案第1号が2026年3月13日に原案可決され、提案額のまま成立しました。補正予算・決算とは区別します。</p>
            </div>
            <div className={styles.metricGrid}>
              {[
                { label: "一般会計当初予算（歳入規模）", record: budget },
                { label: "県税収入", record: tax },
                { label: "一般会計当初予算（歳出総額）", record: spending },
              ].map(({ label, record }) => (
                <article className={styles.metricCard} key={label}>
                  <span>{label}</span>
                  <strong>{formatCompactYen(record?.amount_yen ?? null)}</strong>
                  <small>{formatExactYen(record?.amount_yen ?? null)}</small>
                  <p>FY2026・一般会計・成立後当初予算。公式資料の数値です。</p>
                </article>
              ))}
              <article className={`${styles.metricCard} ${styles.derived}`}>
                <span>当初予算に占める県税収入</span>
                <strong>{taxShare === null ? "評価不能" : `${taxShare.toFixed(1)}%`}</strong>
                <small>Jichi Insight による単純計算</small>
                <p>県税収入 ÷ 一般会計当初予算。政策成果の評価ではありません。</p>
              </article>
            </div>
          </section>

          <div id="fiscal-detail" style={{ scrollMarginTop: 90 }}>
            <FiscalReview municipality="千葉県" records={chibaFinance.records} sources={chibaFinanceSources} />
          </div>

          <section className={styles.evidence} aria-labelledby="evidence-title">
            <div className="sectionIntro">
              <p className="eyebrow">Evidence trail</p>
              <h2 id="evidence-title">当初予算の根拠とReviewed証拠パケット</h2>
            </div>
            <div className={styles.evidenceGrid}>
              {[budget, tax, spending].filter((record) => record !== undefined).map((record) => (
                <EvidencePanel key={record.id} record={record} packet={chibaEvidenceForRecord(record.id)} />
              ))}
            </div>
          </section>

          <section id="priority-projects" className={styles.headline} aria-labelledby="priority-projects-title">
            <div className="sectionIntro">
              <p className="eyebrow">Reviewed priority projects</p>
              <h2 id="priority-projects-title">千葉県の重点事業：10系列の施策・予算・決算</h2>
              <p>
                公式母集団は現行「千葉県総合計画」の41施策です。登録は10系列で、令和7年度施策評価シートに掲載された施策計の予算額（9月補正後）と決算額を掲載します。
                施策単位の公式評定は未公表であり、指標単位の進捗判定を施策の評定として扱いません。
                <Link href="/projects#chiba-prefecture"> 千葉県の重点事業一覧を見る</Link>
              </p>
            </div>
            <div className={projectStyles.cards}>
              {reviewedProjects.map((project) => (
                <article className={projectStyles.card} key={project.series_id}>
                  <p className={projectStyles.meta}>{project.fiscal_year}年度／{project.policy_area}／Reviewed</p>
                  <h3>{project.official_title}</h3>
                  <p>{project.plain_title}</p>
                  <p>施策計の予算額・決算額を掲載。施策単位の公式評定は未公表です。</p>
                  <p className={projectStyles.meta}>Reviewed KPI：{projects.kpis.filter((kpi) => kpi.project_id === project.id && kpi.review_status === "reviewed").length}件</p>
                  <details>
                    <summary>施策指標・KPI・出典を確認</summary>
                    <ProjectReview area="chiba-prefecture" record={project} kpis={projects.kpis.filter((kpi) => kpi.project_id === project.id && kpi.review_status === "reviewed")} />
                  </details>
                  <p><Link href={`/projects/chiba-prefecture/${encodeURIComponent(project.series_id)}`}>年度別詳細を見る</Link></p>
                </article>
              ))}
            </div>
          </section>

          <section className={styles.scope} aria-labelledby="governor-title">
            <div>
              <p className="eyebrow">Executive term</p>
              <h2 id="governor-title">熊谷俊人知事の現任期と公約</h2>
              <p><Link href="/executives">首長台帳を見る</Link></p>
            </div>
            <div>
              {governor ? (
                <>
                  <h3>{governor.person_name} 知事</h3>
                  <p>任期：{formatDateJa(governor.term_start)} 〜 {formatDateJa(governor.term_end)}</p>
                  <p>選挙日：{formatDateJa(governor.election_date)} ／ 登録状態：{governor.review_status}</p>
                  <p>得票数：1,404,905票（2025年3月16日執行・公式選挙結果）</p>
                  <p>Reviewed 公約原文：{governorPromises.length}件</p>
                  <p><Link href="/promises#chiba-prefecture">熊谷俊人知事の公約原文と根拠を見る</Link></p>
                  {manifestoSourcesForExecutive(governor).map((source) => (
                    <p key={source.id}>公約原典：<a href={source.url} target="_blank" rel="noopener noreferrer">{source.title}</a></p>
                  ))}
                  {sourcesForExecutive(governor).map((source) => (
                    <p key={source.id}><a href={source.url} target="_blank" rel="noopener noreferrer">{source.title}</a></p>
                  ))}
                  {electionEvidence?.claims.map((claim) => (
                    <details key={claim.field}>
                      <summary>{claim.field} の根拠</summary>
                      <p>{claim.statement}</p>
                      {claim.location_note ? <p>{claim.location_note}</p> : null}
                    </details>
                  ))}
                  {electionEvidence?.open_questions.length
                    ? <p>任期・選挙に関する未確認事項：{electionEvidence.open_questions.join("／")}</p>
                    : null}
                </>
              ) : <p>知事の現任期はReviewed台帳に未登録です。</p>}
            </div>
          </section>

          <section id="assembly" className={styles.scope} aria-labelledby="assembly-title">
            <div>
              <p className="eyebrow">Reviewed assembly · Stage 4</p>
              <h2 id="assembly-title">千葉県議会の議案・表決・情報公開</h2>
              <p><Link href="/assemblies/chiba-prefecture">千葉県議会の議決・会派別賛否・政務活動費・視察の詳細を見る</Link></p>
            </div>
            <div>
              <p>定数{assembly.assembly.seat_count}人。登録議案{assembly.proposals.length}件、表決{assembly.votes.length}件、会派別賛否{assembly.factionVotes.length}件、政務活動費{assembly.expenses.length}単位、視察{assembly.trips.length}件を登録しています。</p>
              <p>賛否一覧表は3種類あり、○の意味が異なります。議案表は原案に反対する会派等、発議案表は賛成会派等の内訳、請願表は採択に賛成する会派等を○で示します。表の種類をまたいで○を同じ意味として解釈しません。</p>
              <p>令和7年度決算認定は継続審査中（pending）です。現在の登録状態は「{pendingProposals.map((proposal) => proposal.title).join("、") || "未登録"}」。認定・不認定を先取りしません。</p>
              <p>議員個人別の賛否は無所属議員2名の個人名列に限られます。会派所属議員の個人票を再構成しません。領収書等の証拠書類はWeb公開ではなく議会事務局での閲覧です。</p>
            </div>
          </section>

          <section className={styles.scope} aria-labelledby="sources-title">
            <div><p className="eyebrow">Primary sources</p><h2 id="sources-title">計画・予算・決算の公式資料</h2></div>
            <div><ul>{chibaFinanceSources.map((source) => (
              <li key={source.id}>
                <a href={source.url} target="_blank" rel="noopener noreferrer">{source.title}</a>
                <span>（{source.review_status}・索引更新 {source.indexed_at}）</span>
              </li>
            ))}</ul></div>
          </section>

          <section className={styles.notAssessed}>
            <div><p className="eyebrow">Not assessed yet</p><h2>まだ登録・評価していないこと</h2></div>
            <ul>
              <li>登録済み25件の知事公約について、行政実績との因果関係や達成度は未判定です。</li>
              <li>現行計画の41施策のうち重点事業として選定していない31施策は、この10系列に含みません。</li>
              <li>施策単位の公式評定は公表されていません。指標単位の進捗判定を施策の評定に置き換えません。</li>
              <li>2026年度の予算執行実績・決算と施策ごとの成果との対応は未確認です。</li>
            </ul>
          </section>

          <nav className={styles.bottomNav} aria-label="関連ページ">
            <Link href="/municipalities">自治体一覧</Link>
            <Link href="/projects#chiba-prefecture">重点事業10系列</Link>
            <Link href="/promises#chiba-prefecture">知事公約{governorPromises.length}件</Link>
            <Link href="/assemblies/chiba-prefecture">千葉県議会</Link>
            <Link href="/assemblies/chiba-city">千葉市議会</Link>
            <Link href="/promises#chiba-city">千葉市長公約</Link>
            <Link href="/methodology">評価方法</Link>
          </nav>
        </div>
      </main>
      <SiteFooter />
    </>
  );
}
