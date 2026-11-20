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
  kanagawaBudgetRecord,
  kanagawaEvidenceForRecord,
  kanagawaFinance,
  kanagawaFinanceSources,
  kanagawaPlanReview,
} from "@/lib/kanagawaFinance";
import { canonicalFor } from "@/lib/pageMetadata";
import { assemblies } from "@/lib/assemblyRegistry";
import { projectRegistry } from "@/lib/projectRegistry";
import type { ProjectBudgetRecord } from "@/lib/kitakyushuProjects";

import styles from "../fukuoka-prefecture/page.module.css";
import projectStyles from "@/components/ProjectReview.module.css";

export const metadata: Metadata = {
  alternates: { canonical: canonicalFor("/municipalities/kanagawa-prefecture") },
  title: "神奈川県｜新かながわグランドデザイン・財政・重点事業・知事公約・県議会",
  description:
    "新かながわグランドデザイン、2026年度成立後当初予算、2022〜2024年度の普通会計決算、知事重点事業10系列、黒岩祐治知事の公約33件、神奈川県議会の登録情報を公式資料とともに確認できます。",
};

const yenHundredMillion = (amount: number | null) =>
  amount === null ? "未収録" : `${Math.floor(amount / 100_000_000).toLocaleString("ja-JP")}億円`;

export default function KanagawaPrefecturePage() {
  const assembly = assemblies["kanagawa-prefecture"];
  const projects = projectRegistry["kanagawa-prefecture"];
  const reviewedProjectRecords = projects.projects.filter(
    (project) => project.review_status === "reviewed",
  );
  const reviewedProjects = Array.from(
    reviewedProjectRecords
      .slice()
      .sort((a, b) => a.fiscal_year - b.fiscal_year)
      .reduce((map, project) => map.set(project.series_id, project), new Map()),
  ).map(([, project]) => project);
  const budget = kanagawaBudgetRecord("total_revenue");
  const tax = kanagawaBudgetRecord("local_tax");
  const expenditure = kanagawaBudgetRecord("total_expenditure");
  const taxShare = budget?.amount_yen && tax?.amount_yen
    ? (tax.amount_yen / budget.amount_yen) * 100
    : null;
  const governor = currentExecutiveTerms.find((term) =>
    term.municipality_id === kanagawaFinance.municipality.id &&
    term.office === "governor" &&
    term.status === "current" &&
    (term.review_status === "reviewed" || term.review_status === "verified"),
  );
  const governorSources = governor ? sourcesForExecutive(governor) : [];
  const governorManifestoSources = governor ? manifestoSourcesForExecutive(governor) : [];
  const governorEvidence = governor ? evidenceForExecutive(governor) : undefined;
  const governorPromises = governor ? promisesForExecutive(governor).filter(
    (promise) => promise.review_status === "reviewed" || promise.review_status === "verified",
  ) : [];
  const settlementRecords = kanagawaFinance.records.filter(
    (record) => record.stage === "settlement" &&
      record.account_type === "ordinary" &&
      record.review_status === "reviewed",
  );

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
              <h1>神奈川県</h1>
              <p>
                「新かながわグランドデザイン」の計画レビュー、2026年度に成立した一般会計当初予算、
                2022〜2024年度の普通会計決算、知事重点事業10系列、黒岩祐治知事の現任期・公約、
                神奈川県議会の登録情報を、会計区分・評価主体・公表範囲を保って掲載します。
                Jichi Insight 独自の政策達成判定や議員評価は行いません。
              </p>
            </div>
            <dl className={styles.heroFacts}>
              <div><dt>Reviewed 財政レコード</dt><dd>{kanagawaFinance.records.length}件</dd></div>
              <div><dt>収録年度</dt><dd>2022〜2024・2026</dd></div>
              <div><dt>最終確認</dt><dd>{kanagawaFinance.municipality.last_verified_at}</dd></div>
            </dl>
          </section>

          <MunicipalityDiscoveryPanel
            officialCode={kanagawaFinance.municipality.official_code}
            planHref="#plan-title"
            budgetHref="#finance-headline-title"
            settlementHref="#fiscal-detail"
            fiscalDetailHref="#fiscal-detail"
            projectHref="#priority-projects"
          />

          <section className={styles.scope} aria-label="登録情報の範囲">
            <div>
              <p className="eyebrow">Scope</p>
              <h2 id="scope-title">計画・財政・重点事業・知事公約・県議会を分けて確認する。</h2>
            </div>
            <div>
              <p>
                確認できること：2024年3月策定の「新かながわグランドデザイン」（基本構想と2024〜2027年度実施計画）、
                2026年度成立後一般会計当初予算3件、2022〜2024年度普通会計決算51件、
                実施計画13プロジェクトのうち選定規則に基づく重点事業10系列、
                黒岩祐治知事の現任期とReviewed公約{governorPromises.length}件、
                県議会の議案・会派別賛否・政務活動費・視察・情報公開状況です。
              </p>
              <p>
                普通会計決算は一般会計決算とは異なる統計上の会計です。一般会計当初予算と普通会計決算を直接連結した増減率・達成率は示しません。
                重点事業の金額は評価報告書に億円単位で掲載されたプロジェクト事業費で、1億円未満は切り捨てられています。
                公式評価は神奈川県総合計画審議会による二次評価であり、Jichi Insight独自の評価ではありません。
              </p>
              <p>
                県議会の賛否は会派別のみ公表され、議員個人別の賛否は公表されていません。
                公表されていない情報を推測・再構成せず、未登録・未公表を活動や成果の不存在と扱いません。
              </p>
            </div>
          </section>

          <section className={styles.scope} aria-labelledby="plan-title">
            <div>
              <p className="eyebrow">Plan review</p>
              <h2 id="plan-title">新かながわグランドデザインの計画レビュー</h2>
              <p>Reviewed：{kanagawaPlanReview.reviewed_at}</p>
            </div>
            <div>
              {kanagawaPlanReview.records.filter((record) => record.decision === "accepted").map((record) => (
                <article key={record.title}>
                  <h3>{record.title}</h3>
                  <p>{record.statement}</p>
                  <p><a href={record.source_url} target="_blank" rel="noopener noreferrer">計画の公式出典を見る</a></p>
                </article>
              ))}
              <p>
                新かながわグランドデザインは、2040年を展望する基本構想と、2024〜2027年度を計画期間とする実施計画で構成されます。
                実施計画は5つのテーマ・13のプロジェクトで整理され、各プロジェクトにロジックモデル、プロジェクト指標、KPIが設定されています。
              </p>
              <p>
                進行管理は毎年度の評価報告書で行われ、事業部局の一次評価を踏まえて総合計画審議会が二次評価を実施します。
                評価報告書2025では13プロジェクト中、順調6・概ね順調6・やや遅れ1・遅れ0の4段階評価です。
              </p>
            </div>
          </section>

          <section className={styles.headline} aria-labelledby="finance-headline-title">
            <div className="sectionIntro">
              <p className="eyebrow">FY2026 enacted initial budget</p>
              <h2 id="finance-headline-title">2026年度に成立した一般会計当初予算</h2>
              <p>
                令和8年第1回定例会で定県第1号議案が2026年3月25日に原案可決され、提案額のまま成立しました。
                予算案・補正予算とは区別して掲載します。
              </p>
            </div>
            <div className={styles.metricGrid}>
              <article className={styles.metricCard}>
                <span>一般会計当初予算（歳入歳出規模）</span>
                <strong>{formatCompactYen(budget?.amount_yen ?? null)}</strong>
                <small>{formatExactYen(budget?.amount_yen ?? null)}</small>
                <p>2026年度・一般会計・成立後当初予算。</p>
              </article>
              <article className={styles.metricCard}>
                <span>県税収入</span>
                <strong>{formatCompactYen(tax?.amount_yen ?? null)}</strong>
                <small>{formatExactYen(tax?.amount_yen ?? null)}</small>
                <p>定県第1号議案「第1表 歳入歳出予算」の款「県税」の印字値です。</p>
              </article>
              <article className={styles.metricCard}>
                <span>一般会計当初予算（歳出総額）</span>
                <strong>{formatCompactYen(expenditure?.amount_yen ?? null)}</strong>
                <small>{formatExactYen(expenditure?.amount_yen ?? null)}</small>
                <p>成立後当初予算の歳出総額です。</p>
              </article>
              <article className={`${styles.metricCard} ${styles.derived}`}>
                <span>当初予算に占める県税収入</span>
                <strong>{taxShare === null ? "評価不能" : `${taxShare.toFixed(1)}%`}</strong>
                <small>Jichi Insight による単純計算</small>
                <p>県税収入 ÷ 一般会計当初予算。財政健全性や政策成果の評価ではありません。</p>
              </article>
            </div>
          </section>

          <div id="fiscal-detail" style={{ scrollMarginTop: 90 }}>
            <FiscalReview municipality="神奈川県" records={kanagawaFinance.records} sources={kanagawaFinanceSources} />
          </div>

          <section className={styles.evidence} aria-labelledby="evidence-title">
            <div className="sectionIntro">
              <p className="eyebrow">Evidence trail</p>
              <h2 id="evidence-title">当初予算の登録値と公式資料の根拠</h2>
              <p>一般会計当初予算3件について、出典の該当箇所とReviewed証拠パケットを確認できます。</p>
            </div>
            <div className={styles.evidenceGrid}>
              {[budget, tax, expenditure].filter((record) => record !== undefined).map((record) => (
                <EvidencePanel key={record.id} record={record} packet={kanagawaEvidenceForRecord(record.id)} />
              ))}
            </div>
          </section>

          <section id="priority-projects" className={styles.headline} aria-labelledby="priority-projects-title">
            <div className="sectionIntro">
              <p className="eyebrow">Reviewed priority projects</p>
              <h2 id="priority-projects-title">神奈川県の重点事業：10系列の予算・KPI・公式評価</h2>
              <p>
                母集団は「新かながわグランドデザイン」実施計画の13プロジェクトです。
                5テーマを公式掲載順に巡回する選定規則で10系列を選定し、登録済みの{reviewedProjects.length}系列・
                {reviewedProjectRecords.length}件のReviewedレコードを掲載します。金額の大小による選定ではありません。
              </p>
              <p>
                <strong>
                  各金額は神奈川県の評価報告書「4 プロジェクト事業費」に億円単位で公表されたプロジェクト事業費です。
                  プロジェクト単位では1億円未満が切り捨てられているため、円換算・表示の精度は億円単位です。
                  プロジェクト単位の決算額ではありません。
                </strong>
              </p>
              <p>
                公式評価は神奈川県総合計画審議会による二次評価です。事業部局による一次評価と審議会の二次評価を区別し、
                Jichi Insight独自の評価・順位付けは行いません。
                <Link href="/projects#kanagawa-prefecture">神奈川県の事業一覧を見る</Link>
              </p>
            </div>
            <div className={projectStyles.cards}>
              {reviewedProjects.map((project) => (
                <article className={projectStyles.card} key={project.series_id}>
                  <p className={projectStyles.meta}>{project.fiscal_year}年度／{project.policy_area}／Reviewed</p>
                  <h3>{project.official_title}</h3>
                  <p>{project.plain_title}</p>
                  <p>{project.official_evaluation?.note ?? "公式評価の詳細は登録資料を確認してください。"}</p>
                  <ul>
                    {project.budget_records.map((record: ProjectBudgetRecord, index: number) => (
                      <li key={`${record.fiscal_year}-${record.kind}-${index}`}>
                        {record.fiscal_year}年度／評価報告書掲載プロジェクト事業費：
                        {yenHundredMillion(record.amount_yen)}
                        <p className={projectStyles.meta}>
                          億円単位で公表（1億円未満切捨て）。プロジェクト単位の決算額ではありません。
                        </p>
                      </li>
                    ))}
                  </ul>
                  <p className={projectStyles.meta}>
                    Reviewed KPI：{projects.kpis.filter((kpi) =>
                      kpi.project_id === project.id && kpi.review_status === "reviewed",
                    ).length}件
                  </p>
                  <details>
                    <summary>予算・KPI・公式出典を詳しく見る</summary>
                    <ProjectReview area="kanagawa-prefecture" record={project} kpis={projects.kpis.filter(
                      (kpi) => kpi.project_id === project.id && kpi.review_status === "reviewed",
                    )} />
                  </details>
                  <p><Link href={`/projects/kanagawa-prefecture/${encodeURIComponent(project.series_id)}`}>このプロジェクトの年度別詳細を見る</Link></p>
                </article>
              ))}
            </div>
          </section>

          <section className={styles.scope} aria-labelledby="governor-title">
            <div>
              <p className="eyebrow">Executive term</p>
              <h2 id="governor-title">神奈川県知事の現任期と公約</h2>
              <p><Link href="/executives">首長台帳を見る</Link></p>
            </div>
            <div>
              {governor ? (
                <>
                  <h3>{governor.person_name} 知事</h3>
                  <p>任期：{formatDateJa(governor.term_start)} 〜 {formatDateJa(governor.term_end)}</p>
                  <p>選挙日：{formatDateJa(governor.election_date)} ／ 登録状態：{governor.review_status}</p>
                  <p>
                    {governorPromises.length > 0
                      ? `Reviewed 公約原文：${governorPromises.length}件（段階3で登録済み）`
                      : "公約原文はこの知事のReviewed台帳に未登録です（不存在を意味しません）"}
                  </p>
                  {governorPromises.length > 0 ? (
                    <p><Link href="/promises#kanagawa-prefecture">黒岩祐治知事の公約原文33件と根拠を見る</Link></p>
                  ) : null}
                  {governorManifestoSources.map((source) => (
                    <p key={source.id}>公約原典：<a href={source.url} target="_blank" rel="noopener noreferrer">{source.title}</a></p>
                  ))}
                  {governorSources.map((source) => (
                    <p key={source.id}><a href={source.url} target="_blank" rel="noopener noreferrer">{source.title}</a></p>
                  ))}
                  {governorEvidence?.open_questions.length ? (
                    <p>任期に関する未確認事項：{governorEvidence.open_questions.join("／")}</p>
                  ) : null}
                </>
              ) : (
                <p>知事の現任期は本サイトのReviewed台帳に未登録です。</p>
              )}
            </div>
          </section>

          <section id="assembly" className={styles.scope} aria-labelledby="assembly-title">
            <div>
              <p className="eyebrow">Reviewed assembly · Stage 4</p>
              <h2 id="assembly-title">神奈川県議会の議案・会派別賛否と情報公開</h2>
              <p><Link href="/assemblies/kanagawa-prefecture">神奈川県議会の議案・表決・政務活動費・視察・情報公開の詳細を見る</Link></p>
            </div>
            <div>
              <p>
                定数{assembly.assembly.seat_count}人・登録名簿の現員{assembly.assembly.factions.reduce((sum, faction) => sum + faction.member_count, 0)}人。
                登録議案{assembly.proposals.length}件、表決{assembly.votes.length}件、会派別賛否{assembly.factionVotes.length}件、
                政務活動費{assembly.expenses.length}単位、現任期の視察報告書{assembly.trips.length}件を登録しています。
              </p>
              <p>
                賛否は会派別のみ公表され、議員個人別の賛否は公表されていません。
                欠席者等を示す▲は凡例にありますが、本会期の表には使われていません。
              </p>
              <p>政務活動費の収支報告書は令和7年度分の会派交付6単位・議員交付13単位を公開。会計帳簿・証拠書類等は確認時点で未公開です。</p>
              <p>未公表・未登録は活動の不存在を意味しません。議会の公表範囲と個別記録の登録範囲を分けて確認します。</p>
            </div>
          </section>

          <section className={styles.scope} aria-labelledby="sources-title">
            <div>
              <p className="eyebrow">Primary sources</p>
              <h2 id="sources-title">計画・予算・決算の公式資料</h2>
              <p>出典は神奈川県・総務省・神奈川県議会等の一次資料です。</p>
            </div>
            <div>
              <ul>
                {kanagawaFinanceSources.map((source) => (
                  <li key={source.id}>
                    <a href={source.url} target="_blank" rel="noopener noreferrer">{source.title}</a>
                    <span>（{source.review_status}・索引更新 {source.indexed_at}）</span>
                  </li>
                ))}
              </ul>
            </div>
          </section>

          <section className={styles.notAssessed}>
            <div><p className="eyebrow">Not assessed yet</p><h2>まだ登録・評価していないこと</h2></div>
            <ul>
              <li>登録済み33件の知事公約について、達成度や実績との因果関係は未判定です。</li>
              <li>実施計画13プロジェクトのうち、選定対象外の3プロジェクトはこの重点事業ページの10系列には含めていません。</li>
              <li>重点事業単位の決算額は登録・公表されていません。表示するプロジェクト事業費は評価報告書掲載の億円単位の予算値です。</li>
              <li>2026年度の執行実績と決算、事業単位の契約・監査との公式対応</li>
              <li>県議会で公表されていない議員個人別の賛否</li>
            </ul>
          </section>

          <nav className={styles.bottomNav} aria-label="関連ページ">
            <Link href="/municipalities">自治体一覧</Link>
            <Link href="/executives">首長台帳</Link>
            <Link href="/promises#kanagawa-prefecture">知事公約33件</Link>
            <Link href="/assemblies/kanagawa-prefecture">神奈川県議会</Link>
            <Link href="/methodology">評価方法</Link>
          </nav>
        </div>
      </main>
      <SiteFooter />
    </>
  );
}
