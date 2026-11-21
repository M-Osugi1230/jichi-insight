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
  shizuokaFinance, shizuokaPlanReview, shizuokaFinanceSources,
  shizuokaBudgetRecord, shizuokaEvidenceForRecord,
} from "@/lib/shizuokaFinance";
import { assemblies } from "@/lib/assemblyRegistry";
import { projectRegistry } from "@/lib/projectRegistry";
import styles from "../fukuoka-prefecture/page.module.css";
import projectStyles from "@/components/ProjectReview.module.css";

export const metadata: Metadata = {
  alternates: { canonical: canonicalFor("/municipalities/shizuoka-prefecture") },
  title: "静岡県｜しずおか ウェルビーイングプラン・財政・知事公約・県議会",
  description: "静岡県総合計画～しずおか ウェルビーイングプラン～、FY2026一般会計当初予算、FY2022〜2024普通会計決算、政策の柱10系列、鈴木康友知事の公約9件、県議会の議決結果と継続審査を確認します。",
};

export default function ShizuokaPrefecturePage() {
  const municipalityId = shizuokaFinance.municipality.id;
  const area = projectRegistry["shizuoka-prefecture"];
  const projects = area.projects.filter((record) => record.review_status === "reviewed");
  const settlements = shizuokaFinance.records.filter((record) =>
    record.review_status === "reviewed" && record.stage === "settlement" &&
    record.account_type === "ordinary",
  );
  const revenue = shizuokaBudgetRecord("total_revenue");
  const tax = shizuokaBudgetRecord("local_tax");
  const expenditure = shizuokaBudgetRecord("total_expenditure");
  const governor = currentExecutiveTerms.find((term) =>
    term.municipality_id === municipalityId && term.office === "governor" &&
    term.status === "current" && (term.review_status === "reviewed" || term.review_status === "verified"),
  );
  const promises = governor ? promisesForExecutive(governor).filter(
    (promise) => promise.review_status === "reviewed" || promise.review_status === "verified",
  ) : [];
  const electionClaim = governor
    ? evidenceForExecutive(governor)?.claims.find((claim) => claim.field === "election_date")
    : undefined;
  const assembly = assemblies["shizuoka-prefecture"];
  const pending = assembly.proposals.filter((proposal) => proposal.outcome === "pending");
  const factionNote = assembly.disclosure.items.find((item) => item.item === "faction_votes");
  const memberNote = assembly.disclosure.items.find((item) => item.item === "member_votes");

  return (
    <>
      <SiteHeader />
      <main>
        <div className="pageShell">
          <section className={styles.hero}>
            <div>
              <div className={styles.heroMeta}><span>都道府県</span><StatusBadge label="Reviewed" tone="verified" /></div>
              <h1>静岡県</h1>
              <p>静岡県総合計画～しずおか ウェルビーイングプラン～、2026年度一般会計当初予算、
                FY2022〜2024普通会計決算、政策の柱10系列・KPI46件、
                鈴木康友知事の公約9件、静岡県議会の公式記録を確認します。</p>
            </div>
            <dl className={styles.heroFacts}>
              <div><dt>普通会計決算</dt><dd>{settlements.length}件（FY2022–2024）</dd></div>
              <div><dt>重点事業</dt><dd>{projects.length}系列</dd></div>
              <div><dt>知事公約</dt><dd>{promises.length}件</dd></div>
              <div><dt>最終確認</dt><dd>{shizuokaFinance.municipality.last_verified_at}</dd></div>
            </dl>
          </section>

          <MunicipalityDiscoveryPanel
            officialCode={shizuokaFinance.municipality.official_code}
            planHref="#plan-title" budgetHref="#finance-headline-title"
            settlementHref="#fiscal-detail" fiscalDetailHref="#fiscal-detail"
            projectHref="#priority-projects"
          />

          <section className={styles.scope} aria-labelledby="scope-title">
            <div><p className="eyebrow">Scope</p>
              <h2 id="scope-title">「政策の柱」を登録単位として成果指標を確認する。</h2></div>
            <div>
              <p>県の最上位計画は「静岡県総合計画～しずおか ウェルビーイングプラン～」
                （2025〜2028年度）。政策区分3つと行政経営の下に、政策8本・政策の柱24本・取組197・成果指標101を配置しています。</p>
              <p>重点事業は政策の柱24本から10系列を選定し、KPI46件を登録しています。
                県の年次評価書は成果指標のA〜D評価区分を公表しますが、
                政策の柱単位の公式総合評定や予算額は公表していません。
                指標の評価を柱全体の評価に転用せず、金額の欠損を0円とみなしません。</p>
              <p>FY2026一般会計当初予算とFY2022〜2024普通会計決算は、
                年度・会計区分を分けて表示します。</p>
            </div>
          </section>

          <section className={styles.scope} aria-labelledby="plan-title">
            <div><p className="eyebrow">Plan review</p><h2 id="plan-title">静岡県総合計画～しずおか ウェルビーイングプラン～</h2>
              <p>Reviewed：{shizuokaPlanReview.reviewed_at}</p></div>
            <div>{shizuokaPlanReview.records.filter((record) => record.decision === "accepted").map((record) => (
              <article key={record.id}>
                <h3>{record.title}</h3>
                <p>{record.statement}</p>
                <p><a href={record.source_url} target="_blank" rel="noopener noreferrer">公式出典：{record.title}</a></p>
              </article>
            ))}</div>
          </section>

          <section className={styles.headline} aria-labelledby="finance-headline-title">
            <div className="sectionIntro"><p className="eyebrow">FY2026 initial budget</p>
              <h2 id="finance-headline-title">2026年度一般会計当初予算</h2>
              <p>登録済みのFY2026一般会計当初予算と県税の公表値を表示します。
                2022〜2024年度の普通会計決算や事業別金額には付け替えません。</p>
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
                  <p>原資料の千円単位：{record?.amount_yen == null ? "未登録" : `${(record.amount_yen / 1000).toLocaleString("ja-JP")}千円`}</p>
                  <p>FY2026・一般会計・当初予算</p>
                </article>
              ))}
            </div>
          </section>

          <div id="fiscal-detail" style={{ scrollMarginTop: 90 }}>
            <FiscalReview municipality="静岡県" records={shizuokaFinance.records} sources={shizuokaFinanceSources} />
          </div>
          <section className={styles.evidence} aria-labelledby="evidence-title">
            <div className="sectionIntro"><p className="eyebrow">Evidence</p>
              <h2 id="evidence-title">財政数値のReviewed証拠パケット</h2></div>
            <div className={styles.evidenceGrid}>
              {[revenue, tax, expenditure].filter((record) => record !== undefined).map((record) => (
                <EvidencePanel key={record.id} record={record} packet={shizuokaEvidenceForRecord(record.id)} />
              ))}
            </div>
          </section>

          <section id="priority-projects" className={styles.headline} aria-labelledby="projects-title">
            <div className="sectionIntro"><p className="eyebrow">Priority projects</p>
              <h2 id="projects-title">政策の柱10系列・KPI46件</h2>
              <p>しずおか ウェルビーイングプランの政策の柱を登録単位とし、成果指標の判定を
                政策の柱そのものの評定として表示しません。
                <Link href="/projects#shizuoka-prefecture"> 重点事業一覧を見る</Link></p>
            </div>
            <div className={projectStyles.cards}>{projects.map((record) => (
              <article className={projectStyles.card} key={record.series_id}>
                <p className={projectStyles.meta}>{record.fiscal_year}年度・Reviewed</p>
                <h3>{record.official_title}</h3><p>{record.plain_title}</p>
                <p>登録単位：政策の柱／公式総合評定：未公表・未登録</p>
                <details><summary>成果指標と根拠</summary>
                  <ProjectReview area="shizuoka-prefecture" record={record}
                    kpis={area.kpis.filter((kpi) => kpi.project_id === record.id && kpi.review_status === "reviewed")} />
                </details>
                <p><Link href={`/projects/shizuoka-prefecture/${encodeURIComponent(record.series_id)}`}>詳細を見る</Link></p>
              </article>
            ))}</div>
          </section>

          <section className={styles.scope} aria-labelledby="governor-title">
            <div><p className="eyebrow">Executive</p>
              <h2 id="governor-title">鈴木康友知事の現任期と公約</h2></div>
            <div>{governor ? (
              <>
                <h3>{governor.person_name} 知事</h3>
                <p>任期：{formatDateJa(governor.term_start)} 〜 {formatDateJa(governor.term_end)}</p>
                <p>選挙日：{formatDateJa(governor.election_date)} ／ 得票数：728,500票</p>
                <p>Reviewed 公約原文：{promises.length}件</p>
                <p><Link href="/promises#shizuoka-prefecture">鈴木康友知事の公約原文と根拠</Link></p>
                {manifestoSourcesForExecutive(governor).map((source) => (
                  <p key={source.id}><a href={source.url} target="_blank" rel="noopener noreferrer">{source.title}</a></p>
                ))}
                {electionClaim ? <details><summary>選挙結果の出典</summary><p>{electionClaim.statement}</p></details> : null}
              </>
            ) : <p>知事の現任期はReviewed台帳に未登録です。</p>}</div>
          </section>

          <section className={styles.scope} aria-labelledby="assembly-title">
            <div><p className="eyebrow">Assembly</p>
              <h2 id="assembly-title">静岡県議会・令和8年9月定例会</h2>
              <p><Link href="/assemblies/shizuoka-prefecture">県議会の議案・議決・情報公開を見る</Link></p></div>
            <div>
              <p>議員定数{assembly.assembly.seat_count}人、現員67人。
                登録議案等{assembly.proposals.length}件、表決{assembly.votes.length}件、
                会派別賛否{assembly.factionVotes.length}件。
                令和7年度決算認定{pending.length}件は未議決（pending）です。</p>
              <p>静岡県議会の「議決結果一覧表」は<strong>本会議での表決そのものの事後記録</strong>です。
                採決前の会派態度表明の集約ではありません。
                会派別賛否と無所属議員の個人名列を区別し、会派所属議員の個人別投票は推測しません。</p>
              <p>{factionNote?.note}</p><p>{memberNote?.note}</p>
              <p><Link href="/assemblies/shizuoka-city">静岡市議会</Link>と
                <Link href="/assemblies/hamamatsu-city">浜松市議会</Link>も別議会として登録されています。</p>
            </div>
          </section>

          <section className={styles.scope} aria-labelledby="sources-title">
            <div><p className="eyebrow">Primary sources</p><h2 id="sources-title">公式資料と根拠</h2></div>
            <div><ul>{shizuokaFinanceSources.map((source) => (
              <li key={source.id}><a href={source.url} target="_blank" rel="noopener noreferrer">{source.title}</a></li>
            ))}</ul></div>
          </section>
          <nav className={styles.bottomNav} aria-label="関連ページ">
            <Link href="/municipalities">自治体一覧</Link>
            <Link href="/projects#shizuoka-prefecture">政策の柱10系列</Link>
            <Link href="/promises#shizuoka-prefecture">公約9件</Link>
            <Link href="/assemblies/shizuoka-prefecture">静岡県議会</Link>
            <Link href="/municipalities/shizuoka-city">静岡市</Link>
            <Link href="/municipalities/hamamatsu-city">浜松市</Link>
          </nav>
        </div>
      </main>
      <SiteFooter />
    </>
  );
}
