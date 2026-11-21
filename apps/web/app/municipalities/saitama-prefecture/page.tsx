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
  saitamaBudgetRecord,
  saitamaEvidenceForRecord,
  saitamaFinance,
  saitamaFinanceSources,
  saitamaPlanReview,
} from "@/lib/saitamaFinance";
import { canonicalFor } from "@/lib/pageMetadata";
import { assemblies } from "@/lib/assemblyRegistry";
import { projectRegistry } from "@/lib/projectRegistry";

import styles from "../fukuoka-prefecture/page.module.css";
import projectStyles from "@/components/ProjectReview.module.css";

export const metadata: Metadata = {
  alternates: { canonical: canonicalFor("/municipalities/saitama-prefecture") },
  title: "埼玉県｜5か年計画・財政・重点事業・大野元裕知事公約・県議会",
  description: "埼玉県5か年計画（令和4〜8年度）の計画レビュー、FY2026成立後当初予算、FY2022〜2024普通会計決算、分野別施策10系列、大野元裕知事の公約と埼玉県議会の公開範囲を登録資料から確認します。",
};

export default function SaitamaPrefecturePage() {
  const assembly = assemblies["saitama-prefecture"];
  const projects = projectRegistry["saitama-prefecture"];
  const reviewedRecords = projects.projects.filter((project) => project.review_status === "reviewed");
  const reviewedProjects = Array.from(
    reviewedRecords.slice().sort((a, b) => a.fiscal_year - b.fiscal_year)
      .reduce((map, project) => map.set(project.series_id, project), new Map<string, typeof reviewedRecords[number]>()),
  ).map(([, project]) => project);
  const governor = currentExecutiveTerms.find((term) =>
    term.municipality_id === saitamaFinance.municipality.id &&
    term.office === "governor" && term.status === "current" &&
    (term.review_status === "reviewed" || term.review_status === "verified"),
  );
  const governorPromises = governor
    ? promisesForExecutive(governor).filter((promise) => promise.review_status === "reviewed" || promise.review_status === "verified")
    : [];
  const budget = saitamaBudgetRecord("total_revenue");
  const tax = saitamaBudgetRecord("local_tax");
  const spending = saitamaBudgetRecord("total_expenditure");
  const settlements = saitamaFinance.records.filter((record) =>
    record.stage === "settlement" && record.account_type === "ordinary" && record.review_status === "reviewed",
  );
  const taxShare = budget?.amount_yen && tax?.amount_yen ? 100 * tax.amount_yen / budget.amount_yen : null;
  const planName = "埼玉県5か年計画 ～日本一暮らしやすい埼玉へ～";

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
              <h1>埼玉県</h1>
              <p>
                「{planName}」の計画レビュー、2026年度に成立した一般会計当初予算、
                2022〜2024年度の普通会計決算、大野元裕知事の現任期・公約、
                重点事業10系列と埼玉県議会の登録情報を、公式資料の公表単位を保って掲載します。
                独自の政策達成判定や議員評価は行いません。
              </p>
            </div>
            <dl className={styles.heroFacts}>
              <div><dt>Reviewed 財政レコード</dt><dd>{saitamaFinance.records.length}件</dd></div>
              <div><dt>普通会計決算</dt><dd>{settlements.length}件（FY2022–2024）</dd></div>
              <div><dt>最終確認</dt><dd>{saitamaFinance.municipality.last_verified_at}</dd></div>
            </dl>
          </section>

          <MunicipalityDiscoveryPanel
            officialCode={saitamaFinance.municipality.official_code}
            planHref="#plan-title"
            budgetHref="#finance-headline-title"
            settlementHref="#fiscal-detail"
            fiscalDetailHref="#fiscal-detail"
            projectHref="#priority-projects"
          />

          <section className={styles.scope} aria-labelledby="scope-title">
            <div><p className="eyebrow">Scope</p><h2 id="scope-title">公表単位を混同せず、計画・財政・施策・公約・議会を読む。</h2></div>
            <div>
              <p>現行計画は令和4〜8年度（2022〜2026年度）で、3つの将来像、12の針路、54の分野別施策から構成されます。次期計画は策定中であり、混在させません。</p>
              <p>重点事業の登録単位は「施策」（10系列）です。県の施策評価で公表されているのは施策指標ごとの進捗・判定であり、施策単位の公式評価は公表されていません。</p>
              <p>施策単位の金額（予算額・決算額）は県の評価報告書にも掲載されていないため、0円とはせず未登録として扱います。一般会計当初予算と普通会計決算の金額は異なる会計区分のため直接連結しません。</p>
            </div>
          </section>

          <section className={styles.scope} aria-labelledby="plan-title">
            <div>
              <p className="eyebrow">Plan review</p>
              <h2 id="plan-title">{planName}の計画レビュー</h2>
              <p>Reviewed：{saitamaPlanReview.reviewed_at}</p>
            </div>
            <div>
              {saitamaPlanReview.records.filter((record) => record.decision === "accepted").map((record) => (
                <article key={record.id}>
                  <h3>{record.title}</h3>
                  <p>{record.statement}</p>
                  <p><a href={record.source_url} target="_blank" rel="noopener noreferrer">計画の公式出典を見る</a></p>
                </article>
              ))}
              <p>3つの将来像 → 12の針路 → 54の分野別施策。令和7年3月に中間年度の一部変更が行われました。施策評価と独自評価を区別します。</p>
            </div>
          </section>

          <section className={styles.headline} aria-labelledby="finance-headline-title">
            <div className="sectionIntro">
              <p className="eyebrow">FY2026 enacted initial budget</p>
              <h2 id="finance-headline-title">2026年度に成立した一般会計当初予算</h2>
              <p>埼玉県議会の令和8年2月定例会で第1号議案が2026年3月27日に原案可決されました。補正予算・決算とは区別します。</p>
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
            <FiscalReview municipality="埼玉県" records={saitamaFinance.records} sources={saitamaFinanceSources} />
          </div>

          <section className={styles.evidence} aria-labelledby="evidence-title">
            <div className="sectionIntro">
              <p className="eyebrow">Evidence trail</p>
              <h2 id="evidence-title">当初予算の根拠とReviewed証拠パケット</h2>
            </div>
            <div className={styles.evidenceGrid}>
              {[budget, tax, spending].filter((record) => record !== undefined).map((record) => (
                <EvidencePanel key={record.id} record={record} packet={saitamaEvidenceForRecord(record.id)} />
              ))}
            </div>
          </section>

          <section id="priority-projects" className={styles.headline} aria-labelledby="priority-projects-title">
            <div className="sectionIntro">
              <p className="eyebrow">Reviewed priority projects</p>
              <h2 id="priority-projects-title">埼玉県の重点事業：10系列の施策指標・KPI</h2>
              <p>
                公式母集団は「{planName}」の54の分野別施策です。
                12の針路を掲載順に巡回する選定規則で10系列を選びました。
                Reviewed登録は{reviewedRecords.length}件・{reviewedProjects.length}系列です。
                施策単位の金額と公式評価は公表されず、指標単位の判定のみ公表されています。
              </p>
              <p><Link href="/projects#saitama-prefecture">埼玉県の事業一覧を見る</Link></p>
            </div>
            <div className={projectStyles.cards}>
              {reviewedProjects.map((project) => (
                <article className={projectStyles.card} key={project.series_id}>
                  <p className={projectStyles.meta}>{project.fiscal_year}年度／{project.policy_area}／Reviewed</p>
                  <h3>{project.official_title}</h3>
                  <p>{project.plain_title}</p>
                  <p>施策単位の予算額・決算額と公式評価：未公表（指標単位の判定のみ公表）。</p>
                  <p className={projectStyles.meta}>Reviewed KPI：{projects.kpis.filter((kpi) => kpi.project_id === project.id && kpi.review_status === "reviewed").length}件</p>
                  <details>
                    <summary>KPI・施策指標・出典を確認</summary>
                    <ProjectReview area="saitama-prefecture" record={project} kpis={projects.kpis.filter((kpi) => kpi.project_id === project.id && kpi.review_status === "reviewed")} />
                  </details>
                  <p><Link href={`/projects/saitama-prefecture/${encodeURIComponent(project.series_id)}`}>年度別詳細を見る</Link></p>
                </article>
              ))}
            </div>
          </section>

          <section className={styles.scope} aria-labelledby="governor-title">
            <div>
              <p className="eyebrow">Executive term</p>
              <h2 id="governor-title">埼玉県知事の現任期と公約</h2>
              <p><Link href="/executives">首長台帳を見る</Link></p>
            </div>
            <div>
              {governor ? (
                <>
                  <h3>{governor.person_name} 知事</h3>
                  <p>任期：{formatDateJa(governor.term_start)} 〜 {formatDateJa(governor.term_end)}</p>
                  <p>選挙日：{formatDateJa(governor.election_date)} ／ 登録状態：{governor.review_status}</p>
                  <p>Reviewed 公約原文：{governorPromises.length}件</p>
                  <p><Link href="/promises#saitama-prefecture">大野元裕知事の公約原文と根拠を見る</Link></p>
                  {manifestoSourcesForExecutive(governor).map((source) => (
                    <p key={source.id}>公約原典：<a href={source.url} target="_blank" rel="noopener noreferrer">{source.title}</a></p>
                  ))}
                  {sourcesForExecutive(governor).map((source) => (
                    <p key={source.id}><a href={source.url} target="_blank" rel="noopener noreferrer">{source.title}</a></p>
                  ))}
                  {evidenceForExecutive(governor)?.open_questions.length
                    ? <p>任期に関する未確認事項：{evidenceForExecutive(governor)?.open_questions.join("／")}</p>
                    : null}
                </>
              ) : <p>知事の現任期はReviewed台帳に未登録です。</p>}
            </div>
          </section>

          <section id="assembly" className={styles.scope} aria-labelledby="assembly-title">
            <div>
              <p className="eyebrow">Reviewed assembly · Stage 4</p>
              <h2 id="assembly-title">埼玉県議会の議案・表決・情報公開</h2>
              <p><Link href="/assemblies/saitama-prefecture">埼玉県議会の議決・会派別賛否・政務活動費・視察の登録情報を見る</Link></p>
            </div>
            <div>
              <p>定数{assembly.assembly.seat_count}人。登録議案{assembly.proposals.length}件、表決{assembly.votes.length}件、政務活動費{assembly.expenses.length}単位を登録しています。</p>
              <p>会派別の賛否は本会議に先立つ議会運営委員会で確認した態度であり、本会議の投票記録そのものではありません。</p>
              <p>個人名による賛否は無所属議員の公表分に限定し、会派所属議員の個人票を再構成しません。未登録・未公表は活動の不存在を意味しません。</p>
            </div>
          </section>

          <section className={styles.scope} aria-labelledby="sources-title">
            <div><p className="eyebrow">Primary sources</p><h2 id="sources-title">計画・予算・決算の公式資料</h2></div>
            <div><ul>{saitamaFinanceSources.map((source) => (
              <li key={source.id}>
                <a href={source.url} target="_blank" rel="noopener noreferrer">{source.title}</a>
                <span>（{source.review_status}・索引更新 {source.indexed_at}）</span>
              </li>
            ))}</ul></div>
          </section>

          <section className={styles.notAssessed}>
            <div><p className="eyebrow">Not assessed yet</p><h2>まだ登録・評価していないこと</h2></div>
            <ul>
              <li>公約と行政実績との因果関係や達成度は未判定です。</li>
              <li>54の分野別施策のうち重点事業として選定していない44施策は、この10系列に含みません。</li>
              <li>施策単位の金額と総合的な公式評価は公表されていません。指標単位の判定を施策の評定に置き換えません。</li>
              <li>2026年度の予算執行実績・決算と施策ごとの成果との対応は未確認です。</li>
            </ul>
          </section>

          <nav className={styles.bottomNav} aria-label="関連ページ">
            <Link href="/municipalities">自治体一覧</Link>
            <Link href="/projects#saitama-prefecture">重点事業10系列</Link>
            <Link href="/promises#saitama-prefecture">知事公約{governorPromises.length}件</Link>
            <Link href="/assemblies/saitama-prefecture">埼玉県議会</Link>
            <Link href="/methodology">評価方法</Link>
          </nav>
        </div>
      </main>
      <SiteFooter />
    </>
  );
}
