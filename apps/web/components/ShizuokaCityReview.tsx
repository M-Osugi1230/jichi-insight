import Link from "next/link";

import { SiteHeader } from "@/components/SiteHeader";
import { SiteFooter } from "@/components/SiteFooter";
import { StatusBadge } from "@/components/StatusBadge";
import { FiscalReview } from "@/components/FiscalReview";
import { MunicipalityDiscoveryPanel } from "@/components/MunicipalityDiscoveryPanel";
import { ProjectReview } from "@/components/ProjectReview";
import { EvidencePanel } from "@/components/EvidencePanel";
import { currentExecutiveTerms, evidenceForExecutive, formatDateJa, promisesForExecutive, manifestoSourcesForExecutive } from "@/lib/executives";
import { formatCompactYen, formatExactYen } from "@/lib/finance";
import { assemblies } from "@/lib/assemblyRegistry";
import { projectRegistry } from "@/lib/projectRegistry";
import { shizuokaCityFinance, shizuokaCityPlanReview, shizuokaCityFinanceSources, shizuokaCityBudgetRecord, shizuokaCityEvidenceForRecord } from "@/lib/shizuokaCityFinance";
import { hamamatsuFinance, hamamatsuPlanReview, hamamatsuFinanceSources, hamamatsuBudgetRecord, hamamatsuEvidenceForRecord } from "@/lib/hamamatsuFinance";
import shizuokaPhase13Sources from "../../../data/catalog/shizuoka_phase13_sources.json";
import hamamatsuPhase13Sources from "../../../data/catalog/hamamatsu_phase13_sources.json";
import styles from "../app/municipalities/fukuoka-prefecture/page.module.css";
import projectStyles from "@/components/ProjectReview.module.css";

type ShizuokaCitySlug = "shizuoka-city" | "hamamatsu-city";

export function ShizuokaCityReview({ slug }: { slug: ShizuokaCitySlug }) {
  const shizuoka = slug === "shizuoka-city";
  const cityName = shizuoka ? "静岡市" : "浜松市";
  const finance = shizuoka ? shizuokaCityFinance : hamamatsuFinance;
  const plan = shizuoka ? shizuokaCityPlanReview : hamamatsuPlanReview;
  const sources = shizuoka ? shizuokaCityFinanceSources : hamamatsuFinanceSources;
  const budget = shizuoka ? shizuokaCityBudgetRecord : hamamatsuBudgetRecord;
  const evidence = shizuoka ? shizuokaCityEvidenceForRecord : hamamatsuEvidenceForRecord;
  const planSources = shizuoka ? shizuokaPhase13Sources.records : hamamatsuPhase13Sources.records;
  const area = projectRegistry[slug];
  const projects = area.projects.filter((record) => record.review_status === "reviewed");
  const settlements = finance.records.filter((record) =>
    record.review_status === "reviewed" && record.stage === "settlement" &&
    record.account_type === "ordinary",
  );
  const revenue = budget("total_revenue");
  const tax = budget("local_tax");
  const mayor = currentExecutiveTerms.find((term) =>
    term.municipality_id === finance.municipality.id &&
    term.office === "mayor" && term.status === "current" &&
    (term.review_status === "reviewed" || term.review_status === "verified"),
  );
  const promises = mayor ? promisesForExecutive(mayor).filter(
    (promise) => promise.review_status === "reviewed" || promise.review_status === "verified",
  ) : [];
  const electionClaim = mayor ? evidenceForExecutive(mayor)?.claims.find((claim) => claim.field === "election_date") : undefined;
  const assembly = assemblies[slug];
  const memberDisclosure = assembly.disclosure.items.find((item) => item.item === "member_votes");
  const factionDisclosure = assembly.disclosure.items.find((item) => item.item === "faction_votes");

  return (
    <>
      <SiteHeader />
      <main>
        <div className="pageShell">
          <section className={styles.hero}>
            <div>
              <div className={styles.heroMeta}><span>政令指定都市</span><StatusBadge label="Reviewed" tone="verified" /></div>
              <h1>{cityName}</h1>
              <p>{shizuoka
                ? "第5次静岡市総合計画の施策10系列、難波喬司市長の公約3件、2026年度一般会計当初予算、FY2022〜2024普通会計決算、令和8年9月定例会の会派別賛否を登録データに沿って表示します。"
                : "浜松市総合計画第2期基本計画の基本政策10系列、中野祐介市長の公約10件、2026年度一般会計当初予算、FY2022〜2024普通会計決算、令和8年第3回定例会の議員別賛否を登録データに沿って表示します。"}</p>
            </div>
            <dl className={styles.heroFacts}>
              <div><dt>Reviewed 普通会計決算</dt><dd>{settlements.length}件（FY2022–2024）</dd></div>
              <div><dt>重点事業</dt><dd>{projects.length}系列</dd></div>
              <div><dt>市長公約</dt><dd>{promises.length}件</dd></div>
              <div><dt>最終確認</dt><dd>{finance.municipality.last_verified_at}</dd></div>
            </dl>
          </section>

          <MunicipalityDiscoveryPanel
            officialCode={finance.municipality.official_code}
            planHref="#plan-title" budgetHref="#finance-headline-title"
            settlementHref="#fiscal-detail" fiscalDetailHref="#fiscal-detail"
            projectHref="#priority-projects"
          />

          <section className={styles.scope} aria-labelledby="scope-title">
            <div><p className="eyebrow">Registration scope</p><h2 id="scope-title">計画の登録単位と公表された評価を区別する。</h2></div>
            <div>
              {shizuoka ? (
                <>
                  <p>第5次静岡市総合計画（基本構想2026〜2035年度）と実施計画（2026〜2030年度）は9分野・45政策・101施策から構成されます。登録単位は「施策」で、10系列・KPI23件を収録しています。</p>
                  <p>施策単位の予算額・公式評価は未公表・未登録です。取組単位で公表された5年間の投資的経費を合算して施策の当初予算額にはしません。計画初年度のため達成判定は未登録です。</p>
                </>
              ) : (
                <>
                  <p>浜松市総合計画第2期基本計画（2025〜2034年度）は7分野・25基本政策・125政策から構成されます。登録単位は「基本政策」で、10系列・KPI18件を収録しています。</p>
                  <p>基本政策単位の予算額と段階別の公式評定は未公表・未登録です。公式の基本政策シートの文章評価を独自の評点に換算せず、KPIの基準値・目標値を表示します。</p>
                </>
              )}
            </div>
          </section>

          <section className={styles.scope} aria-labelledby="plan-title">
            <div><p className="eyebrow">Plan review</p><h2 id="plan-title">{shizuoka ? "第5次静岡市総合計画" : "浜松市総合計画第2期基本計画"}</h2><p>Reviewed：{plan.reviewed_at}</p></div>
            <div>{plan.records.filter((record) => record.decision === "accepted").map((record) => {
              const source = planSources.find((item) => item.id === record.source_id);
              return (
                <article key={record.id}>
                  <h3>{record.title}</h3><p>{record.statement}</p>
                  {source ? (
                    <p><a href={source.url} target="_blank" rel="noopener noreferrer">公式出典：{record.title}</a></p>
                  ) : null}
                </article>
              );
            })}</div>
          </section>

          <section className={styles.headline} aria-labelledby="finance-headline-title">
            <div className="sectionIntro"><p className="eyebrow">FY2026 enacted budget</p>
              <h2 id="finance-headline-title">2026年度一般会計当初予算</h2>
              <p>一般会計の歳入総額・市税をFY2026成立値として表示します。普通会計のFY2022〜2024決算51件とは会計と年度を分けています。</p>
            </div>
            <div className={styles.metricGrid}>
              {[
                { label: "一般会計当初予算（歳入総額）", record: revenue },
                { label: "市税収入", record: tax },
              ].map(({ label, record }) => (
                <article className={styles.metricCard} key={label}>
                  <span>{label}</span><strong>{formatCompactYen(record?.amount_yen ?? null)}</strong>
                  <small>{formatExactYen(record?.amount_yen ?? null)}</small>
                  <p>原資料の千円単位：{record?.amount_yen == null ? "未登録" : `${(record.amount_yen / 1000).toLocaleString("ja-JP")}千円`}</p>
                </article>
              ))}
            </div>
          </section>

          <div id="fiscal-detail" style={{ scrollMarginTop: 90 }}>
            <FiscalReview municipality={cityName} records={finance.records} sources={sources} />
          </div>
          <section className={styles.evidence} aria-labelledby="evidence-title">
            <div className="sectionIntro"><p className="eyebrow">Evidence</p><h2 id="evidence-title">予算額のReviewed証拠パケット</h2></div>
            <div className={styles.evidenceGrid}>
              {[revenue, tax].filter((record) => record !== undefined).map((record) => (
                <EvidencePanel key={record.id} record={record} packet={evidence(record.id)} />
              ))}
            </div>
          </section>

          <section id="priority-projects" className={styles.headline} aria-labelledby="projects-title">
            <div className="sectionIntro"><p className="eyebrow">Priority projects</p>
              <h2 id="projects-title">{shizuoka ? "施策10系列・KPI23件" : "基本政策10系列・KPI18件"}</h2>
              <p>登録単位の違いを保ち、公式評価が未公表の場合に独自の評点を作りません。<Link href={`/projects#${slug}`}> 重点事業の比較一覧を見る</Link></p>
            </div>
            <div className={projectStyles.cards}>
              {projects.map((record) => (
                <article key={record.series_id} className={projectStyles.card}>
                  <p className={projectStyles.meta}>{record.fiscal_year}年度・Reviewed</p>
                  <h3>{record.official_title}</h3><p>{record.plain_title}</p>
                  <p>登録単位：{shizuoka ? "施策" : "基本政策"}。公式評定：{record.official_evaluation?.rating ?? "未公表・未登録"}</p>
                  <details><summary>指標・事業内容・根拠を見る</summary>
                    <ProjectReview area={slug} record={record} kpis={area.kpis.filter(
                      (kpi) => kpi.project_id === record.id && kpi.review_status === "reviewed",
                    )} />
                  </details>
                  <p><Link href={`/projects/${slug}/${encodeURIComponent(record.series_id)}`}>詳細を見る</Link></p>
                </article>
              ))}
            </div>
          </section>

          <section className={styles.scope} aria-labelledby="mayor-title">
            <div><p className="eyebrow">Executive</p><h2 id="mayor-title">{shizuoka ? "難波喬司" : "中野祐介"}市長の現任期と公約</h2></div>
            <div>{mayor ? (
              <>
                <h3>{mayor.person_name} 市長</h3>
                <p>任期：{formatDateJa(mayor.term_start)} 〜 {formatDateJa(mayor.term_end)}</p>
                <p>選挙日：{formatDateJa(mayor.election_date)} ／ 得票数：{shizuoka ? "149,117票" : "246,745票"}</p>
                <p>Reviewed 公約原文：{promises.length}件</p>
                <p><Link href={`/promises#${slug}`}>公約原文と根拠を確認する</Link></p>
                {manifestoSourcesForExecutive(mayor).map((source) => (
                  <p key={source.id}><a href={source.url} target="_blank" rel="noopener noreferrer">{source.title}</a></p>
                ))}
                {electionClaim ? <details><summary>選挙結果の一次情報</summary><p>{electionClaim.statement}</p></details> : null}
              </>
            ) : <p>現任期のReviewed登録はありません。</p>}</div>
          </section>

          <section className={styles.scope} aria-labelledby="assembly-title">
            <div><p className="eyebrow">Assembly</p>
              <h2 id="assembly-title">{cityName}議会・{shizuoka ? "令和8年9月定例会" : "令和8年第3回定例会"}</h2>
              <p><Link href={`/assemblies/${slug}`}>議会の詳細へ</Link></p></div>
            <div>
              <p>登録議案等{assembly.proposals.length}件、表決{assembly.votes.length}件、
                {shizuoka ? `会派別賛否${assembly.factionVotes.length}件` : `議員別賛否${assembly.votes.reduce((sum, vote) => sum + (vote.member_votes?.length ?? 0), 0).toLocaleString("ja-JP")}件`}。</p>
              {shizuoka ? (
                <p>会派別の賛否は公式の議案結果PDFによるもので、議員個人別の賛否は公表されていません。会派から個人票を復元しません。</p>
              ) : (
                <p>議員賛否一覧に記載された議員個人別の事後表決記録を表示します。会派別賛否は公表されていないため独自集計しません。</p>
              )}
              <p>{factionDisclosure?.note}</p><p>{memberDisclosure?.note}</p>
            </div>
          </section>

          <section className={styles.scope} aria-labelledby="sources-title">
            <div><p className="eyebrow">Sources</p><h2 id="sources-title">公式出典</h2></div>
            <div><ul>{sources.map((source) => (
              <li key={source.id}><a href={source.url} target="_blank" rel="noopener noreferrer">{source.title}</a></li>
            ))}</ul></div>
          </section>
          <nav className={styles.bottomNav} aria-label="関連ページ">
            <Link href="/municipalities">自治体一覧</Link>
            <Link href={`/projects#${slug}`}>重点事業</Link>
            <Link href={`/promises#${slug}`}>市長公約</Link>
            <Link href={`/assemblies/${slug}`}>議会</Link>
            <Link href="/methodology">評価方法</Link>
          </nav>
        </div>
      </main>
      <SiteFooter />
    </>
  );
}
