import Link from "next/link";
import { SiteHeader } from "@/components/SiteHeader";
import { SiteFooter } from "@/components/SiteFooter";
import { StatusBadge } from "@/components/StatusBadge";
import { MunicipalityDiscoveryPanel } from "@/components/MunicipalityDiscoveryPanel";
import { FiscalReview } from "@/components/FiscalReview";
import { EvidencePanel } from "@/components/EvidencePanel";
import { ProjectReview } from "@/components/ProjectReview";
import { currentExecutiveTerms, formatDateJa, manifestoSourcesForExecutive, promisesForExecutive } from "@/lib/executives";
import { formatCompactYen, formatExactYen } from "@/lib/finance";
import {
  kyotoCityFinance, kyotoCityPlanReview, kyotoCityFinanceSources,
  kyotoCityBudgetRecord, kyotoCityEvidenceForRecord,
} from "@/lib/kyotoFinance";
import { assemblies } from "@/lib/assemblyRegistry";
import { projectRegistry } from "@/lib/projectRegistry";
import styles from "@/app/municipalities/fukuoka-prefecture/page.module.css";
import projectStyles from "@/components/ProjectReview.module.css";

export function KyotoCityReview() {
  const municipalityId = kyotoCityFinance.municipality.id;
  const area = projectRegistry["kyoto-city"];
  const projects = area.projects.filter((record) =>
    record.review_status === "reviewed" && record.municipality_id === municipalityId,
  );
  const revenue = kyotoCityBudgetRecord("total_revenue");
  const tax = kyotoCityBudgetRecord("local_tax");
  const mayor = currentExecutiveTerms.find((term) =>
    term.municipality_id === municipalityId && term.office === "mayor" &&
    term.status === "current" &&
    (term.review_status === "reviewed" || term.review_status === "verified"),
  );
  const promises = mayor ? promisesForExecutive(mayor).filter((promise) =>
    promise.review_status === "reviewed" || promise.review_status === "verified",
  ) : [];
  const assembly = assemblies["kyoto-city"];
  return (
    <>
      <SiteHeader />
      <main><div className="pageShell">
        <section className={styles.hero}>
          <div><div className={styles.heroMeta}><span>政令指定都市</span>
            <StatusBadge label="Reviewed" tone="verified" /></div>
            <h1>京都市</h1>
            <p>京都基本構想（2026〜2050年）と新京都戦略（2024〜2027年度）を現行計画として、
              旧「京プラン2025」の政策評価・KPIは履歴として区別し、
              当初予算・決算・市長公約・市会記録を一次資料で確認します。</p>
          </div>
          <dl className={styles.heroFacts}>
            <div><dt>重点事業</dt><dd>{projects.length}系列</dd></div>
            <div><dt>市長公約</dt><dd>{promises.length}件</dd></div>
            <div><dt>最終確認</dt><dd>{kyotoCityFinance.municipality.last_verified_at}</dd></div>
          </dl>
        </section>
        <MunicipalityDiscoveryPanel
          officialCode={kyotoCityFinance.municipality.official_code}
          planHref="#plan-title" budgetHref="#finance-headline-title"
          settlementHref="#fiscal-detail" fiscalDetailHref="#fiscal-detail"
          projectHref="#priority-projects"
        />
        <section className={styles.scope} aria-labelledby="plan-title">
          <div><p className="eyebrow">Plan review</p>
            <h2 id="plan-title">京都基本構想・新京都戦略と旧「京プラン2025」の政策評価</h2>
            <p>確認日：{kyotoCityPlanReview.reviewed_at}</p></div>
          <div>
            <p>現行の京都基本構想・新京都戦略と、旧「京プラン2025」の政策評価を同一視しません。
              令和8年度政策評価結果は旧計画の27政策を評価した公式記録です。
              今回の重点事業10系列・KPI21件はその旧計画の政策単位で登録しています。</p>
            {kyotoCityPlanReview.records.map((record) => (
              <article key={record.id}>
                <h3>{record.title}</h3><p>{record.statement}</p>
                <p>根拠資料：{record.evidence_location}</p>
              </article>
            ))}
          </div>
        </section>
        <section className={styles.headline} aria-labelledby="finance-headline-title">
          <div className="sectionIntro"><p className="eyebrow">FY2026 initial budget</p>
            <h2 id="finance-headline-title">2026年度一般会計当初予算</h2>
            <p>2026年3月24日に原案可決された一般会計当初予算1,007,967,000千円と市税356,307,000千円を表示します。FY2022〜2024普通会計決算と区別します。</p>
          </div>
          <div className={styles.metricGrid}>
            {[
              { label: "一般会計当初予算", record: revenue },
              { label: "市税", record: tax },
            ].map(({label, record}) => (
              <article className={styles.metricCard} key={label}>
                <span>{label}</span>
                <strong>{formatCompactYen(record?.amount_yen ?? null)}</strong>
                <small>{formatExactYen(record?.amount_yen ?? null)}</small>
                <p>原資料の千円単位：{record?.amount_yen == null ? "未登録" :
                  `${(record.amount_yen / 1000).toLocaleString("ja-JP")}千円`}</p>
              </article>
            ))}
          </div>
        </section>
        <div id="fiscal-detail" style={{ scrollMarginTop: 90 }}>
          <FiscalReview municipality="京都市" records={kyotoCityFinance.records} sources={kyotoCityFinanceSources} />
        </div>
        <section className={styles.evidence} aria-labelledby="evidence-title">
          <div className="sectionIntro"><p className="eyebrow">Evidence</p>
            <h2 id="evidence-title">財政の一次資料照合</h2></div>
          <div className={styles.evidenceGrid}>
            {[revenue, tax].filter((record) => record !== undefined).map((record) => (
              <EvidencePanel key={record.id} record={record} packet={kyotoCityEvidenceForRecord(record.id)} />
            ))}
          </div>
        </section>
        <section id="priority-projects" className={styles.headline} aria-labelledby="projects-title">
          <div className="sectionIntro"><p className="eyebrow">Priority projects</p>
            <h2 id="projects-title">旧「京プラン2025」政策10系列・KPI21件</h2>
            <p>旧「京プラン2025」の政策10系列・KPI21件と令和8年度政策評価結果を表示します。
              政策単位の予算額は公表されていないため補完しません。
              <Link href="/projects#kyoto-city"> 重点事業一覧を見る</Link></p></div>
          <div className={projectStyles.cards}>
            {projects.map((record) => (
              <article className={projectStyles.card} key={record.series_id}>
                <p className={projectStyles.meta}>{record.fiscal_year}年度・Reviewed</p>
                <h3>{record.official_title}</h3><p>{record.plain_title}</p>
                <details><summary>成果指標と根拠</summary>
                  <ProjectReview area="kyoto-city" record={record}
                    kpis={area.kpis.filter((kpi) =>
                      kpi.project_id === record.id && kpi.review_status === "reviewed",
                    )}/>
                </details>
                <p><Link href={`/projects/kyoto-city/${encodeURIComponent(record.series_id)}`}>詳細を見る</Link></p>
              </article>
            ))}
          </div>
        </section>
        <section className={styles.scope} aria-labelledby="mayor-title">
          <div><p className="eyebrow">Executive</p><h2 id="mayor-title">松井孝治市長の任期と公約38件</h2></div>
          <div>{mayor ? (
            <>
              <h3>{mayor.person_name} 市長</h3>
              <p>任期：{formatDateJa(mayor.term_start)} 〜 {formatDateJa(mayor.term_end)}</p>
              <p>2024年市長選 得票数：177,454票 ／ Reviewed 公約：{promises.length}件</p>
              <p><Link href="/promises#kyoto-city">市長公約と出典を見る</Link></p>
              {manifestoSourcesForExecutive(mayor).map((source) => (
                <p key={source.id}><a href={source.url} target="_blank" rel="noopener noreferrer">{source.title}</a></p>
              ))}
            </>
          ) : <p>市長の現任期はReviewed台帳に未登録です。</p>}</div>
        </section>
        <section className={styles.scope} aria-labelledby="assembly-title">
          <div><p className="eyebrow">Assembly</p>
            <h2 id="assembly-title">京都市会</h2></div>
          <div><p>議員定数{assembly.assembly.seat_count}人。
            登録議案{assembly.proposals.length}件・会派別賛否{assembly.factionVotes.length}件、
            政務活動費{assembly.expenses.length}件・視察{assembly.trips.length}件。</p>
            <p>令和8年9月市会の議員別賛否385件は無所属7人分のみです。
              他の会派所属議員の個人別賛否は市会だより公表後に追加予定であり、
              登録済みの会派別賛否から推測しません。令和7年度決算は認定済みです。</p>
            <p><Link href="/assemblies/kyoto-city">議案・議決と公開資料を見る</Link></p></div>
        </section>
        <section className={styles.scope} aria-labelledby="sources-title">
          <div><p className="eyebrow">Primary sources</p><h2 id="sources-title">財政資料の公式出典</h2></div>
          <div><ul>{kyotoCityFinanceSources.map((source) => (
            <li key={source.id}><a href={source.url} target="_blank" rel="noopener noreferrer">{source.title}</a></li>
          ))}</ul></div>
        </section>
        <nav className={styles.bottomNav} aria-label="関連ページ">
          <Link href="/municipalities">自治体一覧</Link>
          <Link href="/municipalities/kyoto-prefecture">京都府</Link>
          <Link href="/projects#kyoto-city">重点事業</Link>
          <Link href="/promises#kyoto-city">市長公約</Link>
          <Link href="/assemblies/kyoto-city">京都市会</Link>
        </nav>
      </div></main>
      <SiteFooter />
    </>
  );
}
