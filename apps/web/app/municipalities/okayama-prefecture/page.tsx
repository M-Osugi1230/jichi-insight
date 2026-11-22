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
  okayamaFinance, okayamaPlanReview, okayamaFinanceSources,
  okayamaBudgetRecord, okayamaEvidenceForRecord,
} from "@/lib/okayamaFinance";
import { assemblies } from "@/lib/assemblyRegistry";
import { projectRegistry } from "@/lib/projectRegistry";
import styles from "../fukuoka-prefecture/page.module.css";
import projectStyles from "@/components/ProjectReview.module.css";

export const metadata: Metadata = {
  alternates: { canonical: canonicalFor("/municipalities/okayama-prefecture") },
  title: "岡山県｜岡山県総合計画・財政・知事公約・県議会",
  description: "岡山県総合計画の重点施策、2026年度一般会計当初予算、2022〜2024年度普通会計決算、伊原木隆太知事の登録済み公約、岡山県議会の公開記録を確認します。",
};

export default function OkayamaPrefecturePage() {
  const municipalityId = okayamaFinance.municipality.id;
  const area = projectRegistry["okayama-prefecture"];
  const projects = area.projects.filter((record) =>
    record.municipality_id === municipalityId && record.review_status === "reviewed",
  );
  const settlements = okayamaFinance.records.filter((record) =>
    record.municipality_id === municipalityId && record.review_status === "reviewed" &&
    record.stage === "settlement" && record.account_type === "ordinary",
  );
  const revenue = okayamaBudgetRecord("total_revenue");
  const tax = okayamaBudgetRecord("local_tax");
  const expenditure = okayamaBudgetRecord("total_expenditure");
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
  const assembly = assemblies["okayama-prefecture"];
  const budgetProposal = assembly.proposals.find((proposal) =>
    proposal.title?.includes("令和8年度岡山県一般会計予算"),
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
              <h1>岡山県</h1>
              <p>第4次晴れの国おかやま生き活きプランの戦略プログラム10系列・KPI85件、
                2026年度一般会計骨格予算と2022〜2024年度普通会計決算、
                伊原木隆太知事の公約29件、岡山県議会の公式記録を確認します。</p>
            </div>
            <dl className={styles.heroFacts}>
              <div><dt>普通会計決算</dt><dd>{settlements.length}件（FY2022–2024）</dd></div>
              <div><dt>重点事業</dt><dd>{projects.length}系列</dd></div>
              <div><dt>知事公約</dt><dd>{promises.length}件</dd></div>
              <div><dt>最終確認</dt><dd>{okayamaFinance.municipality.last_verified_at}</dd></div>
            </dl>
          </section>

          <MunicipalityDiscoveryPanel
            officialCode={okayamaFinance.municipality.official_code}
            planHref="#plan-title" budgetHref="#finance-headline-title"
            settlementHref="#fiscal-detail" fiscalDetailHref="#fiscal-detail"
            projectHref="#priority-projects"
          />

          <section className={styles.scope} aria-labelledby="scope-title">
            <div><p className="eyebrow">Scope</p>
              <h2 id="scope-title">政策計画・予算・実績を、登録単位と時点を分けて確認する。</h2></div>
            <div>
              <p>岡山県の最上位計画は「第4次晴れの国おかやま生き活きプラン」です。2025年3月策定で、長期構想とFY2025〜2028の4年間の行動計画から構成されます。</p>
              <p>戦略プログラム単位で重点事業10系列を登録しています。
                分野単位の予算・決算金額は公表資料で確認できないため、
                金額を0円で補完せず、個別指標を施策全体の総合評定に転用しません。</p>
              <p>2026年度一般会計当初予算は知事選前の骨格予算です。
                第1号議案は2026年3月12日に「原案可決」されました。
                当初予算と補正予算、2022〜2024年度普通会計決算を分けて表示します。</p>
            </div>
          </section>

          <section className={styles.scope} aria-labelledby="plan-title">
            <div><p className="eyebrow">Plan review</p>
              <h2 id="plan-title">岡山県総合計画</h2>
              <p>Reviewed：{okayamaPlanReview.reviewed_at}</p></div>
            <div>
              {okayamaPlanReview.records.filter((record) => record.decision === "accepted").map((record) => (
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
              <p>知事選挙を控えて編成された骨格予算です。
                第1号議案「令和8年度岡山県一般会計予算」は2026年3月19日に原案可決され、
                一般会計総額819,698,359千円です。
                補正前の当初予算額であり、普通会計決算とは区別します。</p>
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
            <FiscalReview municipality="岡山県" records={okayamaFinance.records} sources={okayamaFinanceSources} />
          </div>
          <section className={styles.evidence} aria-labelledby="evidence-title">
            <div className="sectionIntro"><p className="eyebrow">Evidence</p>
              <h2 id="evidence-title">財政数値のReviewed証拠パケット</h2></div>
            <div className={styles.evidenceGrid}>
              {[revenue, tax, expenditure].filter((record) => record !== undefined).map((record) => (
                <EvidencePanel key={record.id} record={record} packet={okayamaEvidenceForRecord(record.id)} />
              ))}
            </div>
          </section>

          <section id="priority-projects" className={styles.headline} aria-labelledby="projects-title">
            <div className="sectionIntro"><p className="eyebrow">Priority projects</p>
              <h2 id="projects-title">分野別基本施策10系列・KPI51件</h2>
              <p>分野別基本施策10系列・KPI51件を登録しています。分野単位の予算額や総合評定を推測せず、
                登録済みの指標・予算接続状況を表示します。
                <Link href="/projects#okayama-prefecture"> 重点事業一覧を見る</Link></p>
            </div>
            <div className={projectStyles.cards}>
              {projects.map((record) => (
                <article className={projectStyles.card} key={record.series_id}>
                  <p className={projectStyles.meta}>{record.fiscal_year}年度・Reviewed</p>
                  <h3>{record.official_title}</h3><p>{record.plain_title}</p>
                  <details><summary>成果指標と根拠</summary>
                    <ProjectReview area="okayama-prefecture" record={record}
                      kpis={area.kpis.filter((kpi) =>
                        kpi.project_id === record.id && kpi.review_status === "reviewed",
                      )} />
                  </details>
                  <p><Link href={`/projects/okayama-prefecture/${encodeURIComponent(record.series_id)}`}>詳細を見る</Link></p>
                </article>
              ))}
            </div>
          </section>

          <section className={styles.scope} aria-labelledby="governor-title">
            <div><p className="eyebrow">Executive</p>
              <h2 id="governor-title">伊原木隆太知事の任期と公約29件</h2></div>
            <div>{governor ? (
              <>
                <h3>{governor.person_name} 知事</h3>
                <p>任期：{formatDateJa(governor.term_start)} 〜 {formatDateJa(governor.term_end)}</p>
                <p>選挙日：{formatDateJa(governor.election_date)} ／ 得票数：412,583票</p>
                <p>Reviewed 公約原文：{promises.length}件</p>
                <p><Link href="/promises#okayama-prefecture">知事の公約原文と根拠</Link></p>
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
              <h2 id="assembly-title">岡山県議会</h2>
              <p><Link href="/assemblies/okayama-prefecture">府議会の議案・議決・情報公開を見る</Link></p></div>
            <div>
              <p>議員定数{assembly.assembly.seat_count}人。
                登録議案等{assembly.proposals.length}件、表決{assembly.votes.length}件、
                会派別賛否{assembly.factionVotes.length}件、政務活動費{assembly.expenses.length}件、視察{assembly.trips.length}件。</p>
              <p>2026年度当初予算（骨格予算）は2026年3月12日「原案可決」です。
                岡山県議会は賛否の公表自体がなく、会派別・議員別の賛否は未公表として扱います。
                未公表の賛否を推測していません。</p>
              {budgetProposal ? <p>関連登録議案：{budgetProposal.title}</p> : null}
              <p><Link href="/assemblies/okayama-city">岡山市会</Link>も別議会として確認できます。
                賛否の公開粒度はそれぞれの公式資料の範囲で表示します。</p>
            </div>
          </section>

          <section className={styles.scope} aria-labelledby="sources-title">
            <div><p className="eyebrow">Primary sources</p>
              <h2 id="sources-title">公式資料と根拠</h2></div>
            <div><ul>{okayamaFinanceSources.map((source) => (
              <li key={source.id}><a href={source.url} target="_blank" rel="noopener noreferrer">{source.title}</a></li>
            ))}</ul></div>
          </section>
          <nav className={styles.bottomNav} aria-label="関連ページ">
            <Link href="/municipalities">自治体一覧</Link>
            <Link href="/projects#okayama-prefecture">重点事業</Link>
            <Link href="/promises#okayama-prefecture">知事公約</Link>
            <Link href="/assemblies/okayama-prefecture">岡山県議会</Link>
            <Link href="/municipalities/okayama-city">岡山市</Link>
          </nav>
        </div>
      </main>
      <SiteFooter />
    </>
  );
}
