import Link from "next/link";
import { SiteHeader } from "@/components/SiteHeader";
import { SiteFooter } from "@/components/SiteFooter";
import { StatusBadge } from "@/components/StatusBadge";
import { MunicipalityDiscoveryPanel } from "@/components/MunicipalityDiscoveryPanel";
import { FiscalReview } from "@/components/FiscalReview";
import { EvidencePanel } from "@/components/EvidencePanel";
import { ProjectReview } from "@/components/ProjectReview";
import { assemblies } from "@/lib/assemblyRegistry";
import {
  currentExecutiveTerms, evidenceForExecutive, formatDateJa,
  manifestoSourcesForExecutive, promisesForExecutive,
} from "@/lib/executives";
import { formatCompactYen, formatExactYen } from "@/lib/finance";
import { projectRegistry } from "@/lib/projectRegistry";
import { tohokuBudgetRecord, tohokuFinance, type TohokuSlug } from "@/lib/tohokuFinance";
import styles from "@/app/municipalities/fukuoka-prefecture/page.module.css";
import projectStyles from "@/components/ProjectReview.module.css";

const assemblyBoundaries: Partial<Record<TohokuSlug, string>> = {
  "iwate-prefecture":
    "令和7年度岩手県一般会計歳入歳出決算は継続審査中（pending）です。" +
    " 認定済みとして扱いません。",
  "aomori-prefecture":
    "令和7年度決算等7議案は継続審査中（pending）です。" +
    " 決算認定の結果を推測しません。",
  "aomori-city":
    "青森市議会の登録済み表決の採決方法は未確定（unknown）です。" +
    " 表決結果と採決方法を混同しません。",

  "fukushima-prefecture":
    "令和7年度決算4議案は継続審査中です。認定済みとは表示しません。",
  "yamagata-prefecture":
    "令和7年度決算は未認定です。議案の提出・審査と認定を区別します。",
  "akita-prefecture":
    "段階4は部分登録です。令和8年9月議会は決算関係2件のみ確認済みです。"
    + " 令和8年12月議会は未閉会のため対象外です。",
};

export function TohokuMunicipalityReview({ slug }: { slug: TohokuSlug }) {
  const { municipality, records, evidencePackets, sources, plan } = tohokuFinance[slug];
  const area = projectRegistry[slug];
  const assembly = assemblies[slug];
  const isPrefecture = slug.endsWith("-prefecture");
  const office = isPrefecture ? "governor" : "mayor";
  const chiefTitle = isPrefecture ? "知事" : "市長";
  const chief = currentExecutiveTerms.find((term) =>
    term.municipality_id === municipality.id &&
    term.office === office && term.status === "current" &&
    (term.review_status === "reviewed" || term.review_status === "verified"),
  );
  const promises = chief ? promisesForExecutive(chief).filter((item) =>
    item.review_status === "reviewed" || item.review_status === "verified",
  ) : [];
  const electionClaim = chief
    ? evidenceForExecutive(chief)?.claims.find((claim) =>
        claim.field === "election_date" && claim.decision === "accepted")
    : undefined;
  const projects = area.projects.filter((item) =>
    item.municipality_id === municipality.id && item.review_status === "reviewed",
  );
  const budget = tohokuBudgetRecord(slug, "total_revenue")
    ?? tohokuBudgetRecord(slug, "total_expenditure");
  const tax = tohokuBudgetRecord(slug, "local_tax");
  const settlements = records.filter((item) =>
    item.stage === "settlement" && item.account_type === "ordinary" &&
    item.review_status === "reviewed",
  );
  const currentPlan = plan.records.find((item) =>
    item.decision === "accepted" &&
    (item.title.includes("現行計画") || item.title.includes("計画期間")));
  const planTitle = currentPlan?.title ?? municipality.name_ja + "の現行計画";
  const evidenceForBudget = (id: string) => evidencePackets.find((item) =>
    item.subject_id === id &&
    (item.review_status === "reviewed" || item.review_status === "verified"),
  );

  return (
    <>
      <SiteHeader />
      <main>
        <div className="pageShell">
          <section className={styles.hero}>
            <div>
              <div className={styles.heroMeta}>
                <span>{isPrefecture ? "都道府県" : "市"}</span>
                <StatusBadge label="Reviewed" tone="verified" />
              </div>
              <h1>{municipality.name_ja}</h1>
              <p>{planTitle}を起点に2026年度当初予算とFY2022〜2024普通会計決算、
                重点事業、{chiefTitle}公約、議会の公式記録を別の資料・状態として確認します。</p>
            </div>
            <dl className={styles.heroFacts}>
              <div><dt>普通会計決算</dt><dd>{settlements.length}件（FY2022–2024）</dd></div>
              <div><dt>重点事業</dt><dd>{projects.length}系列</dd></div>
              <div><dt>{chiefTitle}公約</dt><dd>{promises.length}件</dd></div>
              <div><dt>最終確認</dt><dd>{municipality.last_verified_at}</dd></div>
            </dl>
          </section>
          <MunicipalityDiscoveryPanel
            officialCode={municipality.official_code}
            planHref="#plan-title" budgetHref="#finance-headline-title"
            settlementHref="#fiscal-detail" fiscalDetailHref="#fiscal-detail"
            projectHref="#priority-projects"
          />
          <section className={styles.scope} aria-labelledby="scope-title">
            <div><p className="eyebrow">Scope</p>
              <h2 id="scope-title">登録された計画と確認範囲</h2></div>
            <div>
              <p>{currentPlan?.statement ??
                plan.quality_boundary ?? "現行計画の登録済み範囲を表示します。"}</p>
              <p>当初予算と決算を混同せず、未公表の事業単位金額や指標実績は補完しません。</p>
              {assemblyBoundaries[slug] ? <p>{assemblyBoundaries[slug]}</p> : null}
            </div>
          </section>
          <section className={styles.scope} aria-labelledby="plan-title">
            <div><p className="eyebrow">Plan review</p>
              <h2 id="plan-title">{planTitle}</h2>
              {plan.reviewed_at ? <p>Reviewed：{plan.reviewed_at}</p> : null}</div>
            <div>
              {plan.records.filter((item) => item.decision === "accepted").map((item) => (
                <article key={item.id}>
                  <h3>{item.title}</h3><p>{item.statement}</p>
                  {item.source_url ? <p><a href={item.source_url} target="_blank"
                    rel="noopener noreferrer">公式出典を確認</a></p> : null}
                </article>
              ))}
            </div>
          </section>
          <section className={styles.headline} aria-labelledby="finance-headline-title">
            <div className="sectionIntro"><p className="eyebrow">FY2026 initial budget</p>
              <h2 id="finance-headline-title">2026年度一般会計当初予算</h2>
              <p>登録済みの当初予算額と地方税収です。未確定の項目を0円で補完しません。</p>
            </div>
            <div className={styles.metricGrid}>
              {[
                { label: "一般会計当初予算", record: budget },
                { label: isPrefecture ? "県税収入" : "市税収入", record: tax },
              ].map(({ label, record }) => (
                <article className={styles.metricCard} key={label}>
                  <span>{label}</span>
                  <strong>{record?.value_status === "available"
                    ? formatCompactYen(record.amount_yen) : "未確定・未収録"}</strong>
                  <small>{record?.value_status === "available"
                    ? formatExactYen(record.amount_yen) : "確定値未収録"}</small>
                  <p>原資料の千円単位：
                    {record?.value_status === "available" && record.amount_yen !== null
                      ? (record.amount_yen / 1000).toLocaleString("ja-JP") + "千円"
                      : "未収録"}</p>
                </article>
              ))}
            </div>
          </section>
          <div id="fiscal-detail" style={{ scrollMarginTop: 90 }}>
            <FiscalReview municipality={municipality.name_ja}
              records={records} sources={sources} />
          </div>
          <section className={styles.evidence} aria-labelledby="evidence-title">
            <div className="sectionIntro"><p className="eyebrow">Evidence</p>
              <h2 id="evidence-title">予算のReviewed証拠パケット</h2></div>
            <div className={styles.evidenceGrid}>
              {[budget, tax].filter((record) => record !== undefined).map((record) => (
                <EvidencePanel key={record.id} record={record}
                  packet={evidenceForBudget(record.id)} />
              ))}
            </div>
          </section>
          <section id="priority-projects" className={styles.headline}
            aria-labelledby="projects-title">
            <div className="sectionIntro"><p className="eyebrow">Priority projects</p>
              <h2 id="projects-title">重点事業と成果指標</h2>
              <p>Reviewed登録済み{projects.length}系列を表示します。
                <Link href={"/projects#" + slug}> 重点事業一覧を見る</Link></p>
            </div>
            <div className={projectStyles.cards}>
              {projects.map((record) => (
                <article className={projectStyles.card} key={record.series_id}>
                  <p className={projectStyles.meta}>{record.fiscal_year}年度・Reviewed</p>
                  <h3>{record.official_title}</h3><p>{record.plain_title}</p>
                  <details><summary>成果指標・公式評価と根拠</summary>
                    <ProjectReview area={slug} record={record}
                      kpis={area.kpis.filter((item) =>
                        item.project_id === record.id && item.review_status === "reviewed",
                      )} />
                  </details>
                  <p><Link href={"/projects/" + slug + "/" +
                    encodeURIComponent(record.series_id)}>詳細を見る</Link></p>
                </article>
              ))}
            </div>
          </section>
          <section className={styles.scope} aria-labelledby="executive-title">
            <div><p className="eyebrow">Executive</p>
              <h2 id="executive-title">{chiefTitle}の任期・得票・公約</h2></div>
            <div>
              {chief ? <>
                <h3>{chief.person_name} {chiefTitle}</h3>
                <p>任期：{formatDateJa(chief.term_start)}〜{formatDateJa(chief.term_end)}</p>
                <p>選挙日：{formatDateJa(chief.election_date)}</p>
                {electionClaim ? <p>選挙結果（公式資料）：{electionClaim.statement}</p> : null}
                <p>Reviewed公約：{promises.length}件</p>
                <p><Link href={"/promises#" + slug}>公約原文と根拠を見る</Link></p>
                {manifestoSourcesForExecutive(chief).map((source) => (
                  <p key={source.id}><a href={source.url} target="_blank"
                    rel="noopener noreferrer">{source.title}</a></p>
                ))}
              </> : <p>Reviewed現任期は未登録です。</p>}
            </div>
          </section>
          <section className={styles.scope} aria-labelledby="assembly-title">
            <div><p className="eyebrow">Assembly</p>
              <h2 id="assembly-title">{assembly.assembly.name}</h2></div>
            <div>
              <p>議案{assembly.proposals.length}件、会派別賛否
                {assembly.factionVotes.length}件、政務活動費{assembly.expenses.length}件、
                視察{assembly.trips.length}件。</p>
              {assemblyBoundaries[slug] ? <p>{assemblyBoundaries[slug]}</p> : null}
              <p>未公表の賛否・議決は補完せず、審査中と議決済みを区別します。</p>
              <p><Link href={"/assemblies/" + slug}>議会の公式記録を見る</Link></p>
            </div>
          </section>
          <section className={styles.scope} aria-labelledby="sources-title">
            <div><p className="eyebrow">Primary sources</p>
              <h2 id="sources-title">公式財政資料</h2></div>
            <div><ul>{sources.filter((source) => source.url).map((source) => (
              <li key={source.id}><a href={source.url} target="_blank"
                rel="noopener noreferrer">{source.title}</a></li>
            ))}</ul></div>
          </section>
          <nav className={styles.bottomNav} aria-label="関連ページ">
            <Link href="/municipalities">自治体一覧</Link>
            <Link href={"/projects#" + slug}>重点事業</Link>
            <Link href={"/promises#" + slug}>{chiefTitle}公約</Link>
            <Link href={"/assemblies/" + slug}>議会</Link>
          </nav>
        </div>
      </main>
      <SiteFooter />
    </>
  );
}
