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
  manifestoSourcesForExecutive, promisesForExecutive,
} from "@/lib/executives";
import { formatCompactYen, formatExactYen } from "@/lib/finance";
import { canonicalFor } from "@/lib/pageMetadata";
import {
  hiroshimaFinance, hiroshimaPlanReview, hiroshimaFinanceSources,
  hiroshimaBudgetRecord, hiroshimaEvidenceForRecord,
} from "@/lib/hiroshimaFinance";
import { assemblies } from "@/lib/assemblyRegistry";
import { projectRegistry } from "@/lib/projectRegistry";
import styles from "../fukuoka-prefecture/page.module.css";
import projectStyles from "@/components/ProjectReview.module.css";

export const metadata: Metadata = {
  alternates: { canonical: canonicalFor("/municipalities/hiroshima-prefecture") },
  title: "広島県｜ひろしまビジョン・財政・知事公約・県議会",
  description: "広島県の「安心▷誇り▷挑戦 ひろしまビジョン」、2026年度一般会計当初予算、普通会計決算、重点事業、横田美香知事の公約、県議会の公式記録を一次資料で確認します。",
};

export default function HiroshimaPrefecturePage() {
  const municipalityId = hiroshimaFinance.municipality.id;
  const area = projectRegistry["hiroshima-prefecture"];
  const projects = area.projects.filter((record) =>
    record.municipality_id === municipalityId && record.review_status === "reviewed",
  );
  const settlements = hiroshimaFinance.records.filter((record) =>
    record.municipality_id === municipalityId && record.review_status === "reviewed" &&
    record.stage === "settlement" && record.account_type === "ordinary",
  );
  const revenue = hiroshimaBudgetRecord("total_revenue");
  const tax = hiroshimaBudgetRecord("local_tax");
  const expenditure = hiroshimaBudgetRecord("total_expenditure");
  const governor = currentExecutiveTerms.find((term) =>
    term.municipality_id === municipalityId && term.office === "governor" &&
    term.status === "current" &&
    (term.review_status === "reviewed" || term.review_status === "verified"),
  );
  const promises = governor
    ? promisesForExecutive(governor).filter((promise) =>
      promise.review_status === "reviewed" || promise.review_status === "verified",
    ) : [];
  const electionClaim = governor
    ? evidenceForExecutive(governor)?.claims.find((claim) => claim.field === "election_date")
    : undefined;
  const assembly = assemblies["hiroshima-prefecture"];
  const budgetProposal = assembly.proposals.find((proposal) =>
    proposal.title?.includes("令和8年度広島県一般会計予算"),
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
              <h1>広島県</h1>
              <p>「安心▷誇り▷挑戦 ひろしまビジョン」の政策、2026年度一般会計当初予算、
                2022〜2024年度普通会計決算、重点事業、横田美香知事の公約、
                広島県議会の公式記録を一次資料で確認します。</p>
            </div>
            <dl className={styles.heroFacts}>
              <div><dt>普通会計決算</dt><dd>{settlements.length}件（FY2022–2024）</dd></div>
              <div><dt>重点事業</dt><dd>{projects.length}系列</dd></div>
              <div><dt>知事公約</dt><dd>{promises.length}件</dd></div>
              <div><dt>最終確認</dt><dd>{hiroshimaFinance.municipality.last_verified_at}</dd></div>
            </dl>
          </section>

          <MunicipalityDiscoveryPanel
            officialCode={hiroshimaFinance.municipality.official_code}
            planHref="#plan-title" budgetHref="#finance-headline-title"
            settlementHref="#fiscal-detail" fiscalDetailHref="#fiscal-detail"
            projectHref="#priority-projects"
          />

          <section className={styles.scope} aria-labelledby="scope-title">
            <div><p className="eyebrow">Scope</p>
              <h2 id="scope-title">政策計画・予算・実績を、登録単位と時点を分けて確認する。</h2></div>
            <div>
              <p>広島県の最上位計画は「安心▷誇り▷挑戦 ひろしまビジョン」です。
                2020年10月策定、2026年6月改定。改定版アクションプランは
                2026〜2030年度を対象とし、5つの施策の柱の下に17の施策領域を置きます。</p>
              <p>登録済みの重点事業と成果指標は、登録資料の年度・施策領域に沿って表示します。
                施策領域単位の予算額が公表資料から接続できない場合は、
                金額を0円で補完せず、指標の達成状況を領域全体の公式評価とみなしません。</p>
              <p>2026年度一般会計当初予算と2022〜2024年度普通会計決算を混同せず表示します。
                県第1号議案「令和8年度広島県一般会計予算」は2026年3月17日に「可決」です。</p>
            </div>
          </section>

          <section className={styles.scope} aria-labelledby="plan-title">
            <div><p className="eyebrow">Plan review</p>
              <h2 id="plan-title">安心▷誇り▷挑戦 ひろしまビジョン</h2>
              <p>Reviewed：{hiroshimaPlanReview.reviewed_at}</p></div>
            <div>
              {hiroshimaPlanReview.records.filter((record) => record.decision === "accepted").map((record) => (
                <article key={record.id}>
                  <h3>{record.title}</h3>
                  <p>{record.statement}</p>
                  <p><a href={record.source_url} target="_blank" rel="noopener noreferrer">公式出典：{record.title}</a></p>
                </article>
              ))}
            </div>
          </section>

          <section className={styles.headline} aria-labelledby="finance-headline-title">
            <div className="sectionIntro"><p className="eyebrow">FY2026 initial budget</p>
              <h2 id="finance-headline-title">2026年度一般会計当初予算</h2>
              <p>県第1号議案で可決された予算の原資料記載値を使用します。
                一般会計の歳入・歳出総額は1,151,390,000千円です。
                2022〜2024年度普通会計決算とは会計・年度を分けます。</p>
            </div>
            <div className={styles.metricGrid}>
              {[
                { label: "一般会計当初予算（歳入総額）", record: revenue },
                { label: "県税収入", record: tax },
                { label: "一般会計当初予算（歳出総額）", record: expenditure },
              ].map(({ label, record }) => (
                <article className={styles.metricCard} key={label}>
                  <span>{label}</span>
                  <strong>{formatCompactYen(record?.amount_yen ?? null)}</strong>
                  <small>{formatExactYen(record?.amount_yen ?? null)}</small>
                  <p>原資料の千円単位：{record?.amount_yen == null ? "未登録" :
                    `${(record.amount_yen / 1000).toLocaleString("ja-JP")}千円`}</p>
                  <p>FY2026・一般会計・当初予算</p>
                </article>
              ))}
            </div>
          </section>

          <div id="fiscal-detail" style={{ scrollMarginTop: 90 }}>
            <FiscalReview municipality="広島県" records={hiroshimaFinance.records} sources={hiroshimaFinanceSources} />
          </div>
          <section className={styles.evidence} aria-labelledby="evidence-title">
            <div className="sectionIntro"><p className="eyebrow">Evidence</p>
              <h2 id="evidence-title">財政数値のReviewed証拠パケット</h2></div>
            <div className={styles.evidenceGrid}>
              {[revenue, tax, expenditure].filter((record) => record !== undefined).map((record) => (
                <EvidencePanel key={record.id} record={record} packet={hiroshimaEvidenceForRecord(record.id)} />
              ))}
            </div>
          </section>

          <section id="priority-projects" className={styles.headline} aria-labelledby="projects-title">
            <div className="sectionIntro"><p className="eyebrow">Priority projects</p>
              <h2 id="projects-title">重点事業と成果指標</h2>
              <p>施策領域の公式総合評価と事業別金額を推測せず、
                登録済みの指標・予算接続状況を表示します。
                <Link href="/projects#hiroshima-prefecture"> 重点事業一覧を見る</Link></p>
            </div>
            <div className={projectStyles.cards}>
              {projects.map((record) => (
                <article className={projectStyles.card} key={record.series_id}>
                  <p className={projectStyles.meta}>{record.fiscal_year}年度・Reviewed</p>
                  <h3>{record.official_title}</h3><p>{record.plain_title}</p>
                  <details><summary>成果指標と根拠</summary>
                    <ProjectReview area="hiroshima-prefecture" record={record}
                      kpis={area.kpis.filter((kpi) =>
                        kpi.project_id === record.id && kpi.review_status === "reviewed",
                      )} />
                  </details>
                  <p><Link href={`/projects/hiroshima-prefecture/${encodeURIComponent(record.series_id)}`}>詳細を見る</Link></p>
                </article>
              ))}
            </div>
          </section>

          <section className={styles.scope} aria-labelledby="governor-title">
            <div><p className="eyebrow">Executive</p>
              <h2 id="governor-title">横田美香知事の現任期と公約</h2></div>
            <div>{governor ? (
              <>
                <h3>{governor.person_name} 知事</h3>
                <p>任期：{formatDateJa(governor.term_start)} 〜 {formatDateJa(governor.term_end)}</p>
                <p>選挙日：{formatDateJa(governor.election_date)}</p>
                <p>Reviewed 公約原文：{promises.length}件</p>
                <p><Link href="/promises#hiroshima-prefecture">知事の公約原文と根拠</Link></p>
                {manifestoSourcesForExecutive(governor).map((source) => (
                  <p key={source.id}><a href={source.url} target="_blank" rel="noopener noreferrer">{source.title}</a></p>
                ))}
                {electionClaim ? <details><summary>選挙結果の出典</summary>
                  <p>{electionClaim.statement}</p></details> : null}
              </>
            ) : <p>知事の現任期はReviewed台帳に未登録です。</p>}</div>
          </section>

          <section className={styles.scope} aria-labelledby="assembly-title">
            <div><p className="eyebrow">Assembly</p>
              <h2 id="assembly-title">広島県議会</h2>
              <p><Link href="/assemblies/hiroshima-prefecture">県議会の議案・議決・情報公開を見る</Link></p></div>
            <div>
              <p>議員定数{assembly.assembly.seat_count}人。
                登録議案等{assembly.proposals.length}件、表決{assembly.votes.length}件、
                会派別賛否{assembly.factionVotes.length}件。</p>
              <p>県第1号議案（令和8年度広島県一般会計予算）は「可決」です。
                可決された当初予算と、その後の補正予算・執行・決算を同一の状態として扱いません。</p>
              {budgetProposal ? <p>関連登録議案：{budgetProposal.title}</p> : null}
              <p><Link href="/assemblies/hiroshima-city">広島市議会</Link>も別議会として確認できます。
                賛否の公開粒度はそれぞれの公式資料の範囲で表示します。</p>
            </div>
          </section>

          <section className={styles.scope} aria-labelledby="sources-title">
            <div><p className="eyebrow">Primary sources</p>
              <h2 id="sources-title">公式資料と根拠</h2></div>
            <div><ul>{hiroshimaFinanceSources.map((source) => (
              <li key={source.id}><a href={source.url} target="_blank" rel="noopener noreferrer">{source.title}</a></li>
            ))}</ul></div>
          </section>
          <nav className={styles.bottomNav} aria-label="関連ページ">
            <Link href="/municipalities">自治体一覧</Link>
            <Link href="/projects#hiroshima-prefecture">重点事業</Link>
            <Link href="/promises#hiroshima-prefecture">知事公約</Link>
            <Link href="/assemblies/hiroshima-prefecture">広島県議会</Link>
            <Link href="/municipalities/hiroshima-city">広島市</Link>
          </nav>
        </div>
      </main>
      <SiteFooter />
    </>
  );
}
