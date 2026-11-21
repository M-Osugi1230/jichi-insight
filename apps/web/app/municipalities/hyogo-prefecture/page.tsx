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
  hyogoBudgetRecord,
  hyogoEvidenceForRecord,
  hyogoFinance,
  hyogoFinanceSources,
  hyogoPlanReview,
} from "@/lib/hyogoFinance";
import { canonicalFor } from "@/lib/pageMetadata";
import { assemblies } from "@/lib/assemblyRegistry";
import { projectRegistry } from "@/lib/projectRegistry";

import styles from "../fukuoka-prefecture/page.module.css";
import projectStyles from "@/components/ProjectReview.module.css";

export const metadata: Metadata = {
  alternates: { canonical: canonicalFor("/municipalities/hyogo-prefecture") },
  title: "兵庫県｜ひょうごビジョン2050・地域創生戦略・財政・知事公約・県議会",
  description:
    "ひょうごビジョン2050と第三期兵庫県地域創生戦略、2026年度一般会計当初予算、2022〜2024年度普通会計決算、斎藤元彦知事の公約18件、重点事業10系列、兵庫県議会の公開情報を確認します。",
};

export default function HyogoPrefecturePage() {
  const prefectureId = hyogoFinance.municipality.id;
  const cityId = "jp-local-281000";

  const projects = projectRegistry["hyogo-prefecture"];
  const reviewedProjects = Array.from(
    projects.projects
      .filter((project) => project.review_status === "reviewed")
      .sort((a, b) => a.fiscal_year - b.fiscal_year)
      .reduce(
        (map, project) => map.set(project.series_id, project),
        new Map<string, (typeof projects.projects)[number]>(),
      ),
  ).map(([, project]) => project);

  const governor = currentExecutiveTerms.find(
    (term) =>
      term.municipality_id === prefectureId &&
      term.office === "governor" &&
      term.status === "current" &&
      (term.review_status === "reviewed" || term.review_status === "verified"),
  );
  const mayor = currentExecutiveTerms.find(
    (term) =>
      term.municipality_id === cityId &&
      term.office === "mayor" &&
      term.status === "current" &&
      (term.review_status === "reviewed" || term.review_status === "verified"),
  );
  const reviewedPromises = (term: typeof governor) =>
    term
      ? promisesForExecutive(term).filter(
          (promise) =>
            promise.review_status === "reviewed" ||
            promise.review_status === "verified",
        )
      : [];
  const governorPromises = reviewedPromises(governor);
  const mayorPromises = reviewedPromises(mayor);
  const governorEvidence = governor ? evidenceForExecutive(governor) : undefined;
  const mayorEvidence = mayor ? evidenceForExecutive(mayor) : undefined;
  const governorElection = governorEvidence?.claims.find(
    (claim) => claim.field === "election_date",
  );
  const mayorElection = mayorEvidence?.claims.find(
    (claim) => claim.field === "election_date",
  );

  const revenue = hyogoBudgetRecord("total_revenue");
  const tax = hyogoBudgetRecord("local_tax");
  const spending = hyogoBudgetRecord("total_expenditure");
  const settlements = hyogoFinance.records.filter(
    (record) =>
      record.review_status === "reviewed" &&
      record.stage === "settlement" &&
      record.account_type === "ordinary",
  );
  const taxShare =
    revenue?.amount_yen && tax?.amount_yen
      ? (tax.amount_yen / revenue.amount_yen) * 100
      : null;

  const prefecturalAssembly = assemblies["hyogo-prefecture"];
  const cityAssembly = assemblies["kobe-city"];
  const voteDisclosure = prefecturalAssembly.disclosure.items.find(
    (item) => item.item === "faction_votes",
  );
  const memberDisclosure = prefecturalAssembly.disclosure.items.find(
    (item) => item.item === "member_votes",
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
              <h1>兵庫県</h1>
              <p>
                長期ビジョン「ひょうごビジョン2050」と実行プログラム
                「第三期兵庫県地域創生戦略」を区別し、一般会計当初予算、
                普通会計決算、知事の現任期・公約18件、重点事業10系列、
                兵庫県議会の情報公開を公式資料に沿って確認します。
              </p>
            </div>
            <dl className={styles.heroFacts}>
              <div><dt>Reviewed 財政レコード</dt><dd>{hyogoFinance.records.length}件</dd></div>
              <div><dt>普通会計決算</dt><dd>{settlements.length}件（FY2022–2024）</dd></div>
              <div><dt>Reviewed 重点事業</dt><dd>{reviewedProjects.length}系列</dd></div>
              <div><dt>最終確認</dt><dd>{hyogoFinance.municipality.last_verified_at}</dd></div>
            </dl>
          </section>

          <MunicipalityDiscoveryPanel
            officialCode={hyogoFinance.municipality.official_code}
            planHref="#plan-title"
            budgetHref="#finance-headline-title"
            settlementHref="#fiscal-detail"
            fiscalDetailHref="#fiscal-detail"
            projectHref="#priority-projects"
          />

          <section className={styles.scope} aria-labelledby="scope-title">
            <div>
              <p className="eyebrow">Scope</p>
              <h2 id="scope-title">長期ビジョン、地域創生戦略、年度別財政を区別する。</h2>
            </div>
            <div>
              <p>
                県政の基本指針は2022年3月策定の「ひょうごビジョン2050」
                （テーマ「躍動する兵庫」）です。
                その実行プログラムは2025年3月策定の第三期「兵庫県地域創生戦略」
                （2025〜2029年）であり、兵庫県地域創生条例第6条と
                まち・ひと・しごと創生法第9条に基づく戦略です。
              </p>
              <p>
                第三期戦略は3つの柱・8つの方向性の体系です。
                2026年度一般会計成立後当初予算と、2022〜2024年度の普通会計決算は、
                会計区分・年度が異なるため同一系列として比較しません。
              </p>
              <p>
                重点事業の登録単位は第三期戦略の「取組方針項目」です。
                全66項目（再掲2項目、固有64項目）のうち10系列を選定しています。
                取組方針項目単位の予算額・決算額・公式評定・KPIは未公表・未登録です。
                方向性単位の187指標を取組方針項目の評価として扱いません。
              </p>
            </div>
          </section>

          <section className={styles.scope} aria-labelledby="plan-title">
            <div><p className="eyebrow">Plan review</p><h2 id="plan-title">ひょうごビジョン2050／第三期兵庫県地域創生戦略</h2>
              <p>Reviewed：{hyogoPlanReview.reviewed_at}</p></div>
            <div>
              {hyogoPlanReview.records
                .filter((record) => record.decision === "accepted")
                .map((record) => (
                  <article key={record.id}>
                    <h3>{record.title}</h3>
                    <p>{record.statement}</p>
                    <p><a href={record.source_url} target="_blank" rel="noopener noreferrer">公式出典：{record.title}</a></p>
                  </article>
                ))}
            </div>
          </section>

          <section className={styles.headline} aria-labelledby="finance-headline-title">
            <div className="sectionIntro">
              <p className="eyebrow">FY2026 enacted initial budget</p>
              <h2 id="finance-headline-title">2026年度に成立した一般会計当初予算</h2>
              <p>
                令和8年度の一般会計当初予算は成立後の数値を表示します。
                補正予算、普通会計決算、事業単位の金額に置き換えません。
              </p>
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
                  <p>FY2026・一般会計・成立後当初予算</p>
                </article>
              ))}
              <article className={`${styles.metricCard} ${styles.derived}`}>
                <span>一般会計当初予算に占める県税収入</span>
                <strong>{taxShare === null ? "算出不可" : `${taxShare.toFixed(1)}%`}</strong>
                <small>Jichi Insight による単純計算</small>
                <p>県税収入 ÷ 当初予算の歳入総額。公式評価ではありません。</p>
              </article>
            </div>
          </section>

          <div id="fiscal-detail" style={{ scrollMarginTop: 90 }}>
            <FiscalReview municipality="兵庫県" records={hyogoFinance.records} sources={hyogoFinanceSources} />
          </div>

          <section className={styles.evidence} aria-labelledby="evidence-title">
            <div className="sectionIntro">
              <p className="eyebrow">Evidence trail</p>
              <h2 id="evidence-title">財政数値のReviewed証拠パケット</h2>
            </div>
            <div className={styles.evidenceGrid}>
              {[revenue, tax, spending]
                .filter((record) => record !== undefined)
                .map((record) => (
                  <EvidencePanel
                    key={record.id}
                    record={record}
                    packet={hyogoEvidenceForRecord(record.id)}
                  />
                ))}
            </div>
          </section>

          <section id="priority-projects" className={styles.headline} aria-labelledby="projects-title">
            <div className="sectionIntro">
              <p className="eyebrow">Reviewed priority projects</p>
              <h2 id="projects-title">取組方針項目の重点事業10系列</h2>
              <p>
                第三期兵庫県地域創生戦略の掲載順に選定した取組方針項目です。
                方向性単位の達成度ランクや187指標を個々の取組方針の
                評価・KPIとして付け替えず、未公表の金額を0円として補完しません。
                <Link href="/projects#hyogo-prefecture"> 兵庫県の重点事業一覧を見る</Link>
              </p>
            </div>
            <div className={projectStyles.cards}>
              {reviewedProjects.map((project) => (
                <article className={projectStyles.card} key={project.series_id}>
                  <p className={projectStyles.meta}>{project.fiscal_year}年度／{project.policy_area}／Reviewed</p>
                  <h3>{project.official_title}</h3>
                  <p>{project.plain_title}</p>
                  <p>取組方針項目単位の金額・公式評定・KPI：未登録</p>
                  <details>
                    <summary>登録内容・未公表理由・公式出典</summary>
                    <ProjectReview
                      area="hyogo-prefecture"
                      record={project}
                      kpis={projects.kpis.filter(
                        (kpi) => kpi.project_id === project.id && kpi.review_status === "reviewed",
                      )}
                    />
                  </details>
                  <p><Link href={`/projects/hyogo-prefecture/${encodeURIComponent(project.series_id)}`}>年度別詳細を見る</Link></p>
                </article>
              ))}
            </div>
          </section>

          <section className={styles.scope} aria-labelledby="governor-title">
            <div>
              <p className="eyebrow">Executive term</p>
              <h2 id="governor-title">斎藤元彦知事の現任期と公約</h2>
              <p><Link href="/executives">首長台帳を見る</Link></p>
            </div>
            <div>
              {governor ? (
                <>
                  <h3>{governor.person_name} 知事</h3>
                  <p>任期：{formatDateJa(governor.term_start)} 〜 {formatDateJa(governor.term_end)}</p>
                  <p>選挙日：{formatDateJa(governor.election_date)} ／ 登録状態：{governor.review_status}</p>
                  <p>得票数：1,113,911票（2024年11月17日執行の知事選挙）</p>
                  <p>Reviewed 公約原文：{governorPromises.length}件</p>
                  <p><Link href="/promises#hyogo-prefecture">知事公約の原文と根拠を見る</Link></p>
                  {manifestoSourcesForExecutive(governor).map((source) => (
                    <p key={source.id}>公約原典：<a href={source.url} target="_blank" rel="noopener noreferrer">{source.title}</a></p>
                  ))}
                  {sourcesForExecutive(governor).map((source) => (
                    <p key={source.id}><a href={source.url} target="_blank" rel="noopener noreferrer">{source.title}</a></p>
                  ))}
                  {governorElection ? (
                    <details>
                      <summary>2024年知事選挙・任期の根拠</summary>
                      <p>{governorElection.statement}</p>
                    </details>
                  ) : null}
                  {governorEvidence?.open_questions.length ? (
                    <p>任期・選挙に関する未確認事項：{governorEvidence.open_questions.join("／")}</p>
                  ) : null}
                </>
              ) : <p>知事の現任期はReviewed台帳に未登録です。</p>}
            </div>
          </section>

          <section className={styles.scope} aria-labelledby="kobe-mayor-title">
            <div>
              <p className="eyebrow">Related municipality · Kobe City</p>
              <h2 id="kobe-mayor-title">神戸市長の現任期と公約</h2>
              <p><Link href="/promises#kobe-city">神戸市長の公約原文と根拠を見る</Link></p>
            </div>
            <div>
              {mayor ? (
                <>
                  <h3>{mayor.person_name} 市長</h3>
                  <p>任期：{formatDateJa(mayor.term_start)} 〜 {formatDateJa(mayor.term_end)}</p>
                  <p>選挙日：{formatDateJa(mayor.election_date)} ／ 登録状態：{mayor.review_status}</p>
                  <p>得票数：275,273票（2025年10月26日執行の神戸市長選挙）</p>
                  <p>Reviewed 公約原文：{mayorPromises.length}件</p>
                  {manifestoSourcesForExecutive(mayor).map((source) => (
                    <p key={source.id}>公約原典：<a href={source.url} target="_blank" rel="noopener noreferrer">{source.title}</a></p>
                  ))}
                  {mayorElection ? (
                    <details><summary>2025年市長選挙・得票数の根拠</summary><p>{mayorElection.statement}</p></details>
                  ) : null}
                  {mayorEvidence?.open_questions.length ? (
                    <p>任期・選挙に関する未確認事項：{mayorEvidence.open_questions.join("／")}</p>
                  ) : null}
                  <p><Link href="/projects#kobe-city">神戸市の重点事業10系列を見る</Link></p>
                  <p><Link href="/assemblies/kobe-city">神戸市会の登録議案・会派別賛否を見る</Link></p>
                </>
              ) : <p>神戸市長の現任期はReviewed台帳に未登録です。</p>}
            </div>
          </section>

          <section id="assembly" className={styles.scope} aria-labelledby="assembly-title">
            <div>
              <p className="eyebrow">Reviewed assembly · Stage 4</p>
              <h2 id="assembly-title">兵庫県議会の議案・会派態度・情報公開</h2>
              <p><Link href="/assemblies/hyogo-prefecture">兵庫県議会の詳細を見る</Link></p>
            </div>
            <div>
              <p>
                定数{prefecturalAssembly.assembly.seat_count}人。
                登録議案{prefecturalAssembly.proposals.length}件、
                議決結果等の記録{prefecturalAssembly.votes.length}件、
                会派態度{prefecturalAssembly.factionVotes.length}件、
                政務活動費{prefecturalAssembly.expenses.length}単位、
                委員会調査{prefecturalAssembly.trips.length}件を登録しています。
              </p>
              <p>
                「議案等に対する会派態度」は、表決そのものの記録ではなく、
                採決に先立って各会派・議員が表明した態度を議会事務局が集約した資料です。
                本会議の投票記録と同一視しません。
              </p>
              <p>{voteDisclosure?.note ?? "会派態度の公開範囲は未確認です。"}</p>
              <p>{memberDisclosure?.note ?? "議員個人別の公開範囲は未確認です。"}</p>
              <p>
                <Link href="/assemblies/kobe-city">{cityAssembly.assembly.name}</Link>も
                別の議会として登録しています。登録議案{cityAssembly.proposals.length}件、
                表決{cityAssembly.votes.length}件です。
              </p>
            </div>
          </section>

          <section className={styles.scope} aria-labelledby="sources-title">
            <div><p className="eyebrow">Primary sources</p><h2 id="sources-title">公式資料と出典</h2></div>
            <div>
              <ul>{hyogoFinanceSources.map((source) => (
                <li key={source.id}>
                  <a href={source.url} target="_blank" rel="noopener noreferrer">{source.title}</a>
                  <span>（{source.review_status}・索引更新 {source.indexed_at}）</span>
                </li>
              ))}</ul>
            </div>
          </section>

          <section className={styles.notAssessed}>
            <div><p className="eyebrow">Not assessed yet</p><h2>まだ評価していないこと</h2></div>
            <ul>
              <li>知事公約18件・市長公約28件の行政実績との因果関係や達成度は未判定です。</li>
              <li>兵庫県の取組方針項目単位の金額・公式評定・KPIは未登録です。</li>
              <li>方向性単位の指標から、個々の取組方針項目の成績を推測しません。</li>
              <li>県議会の会派態度を本会議での議員別投票結果として再構成しません。</li>
            </ul>
          </section>

          <nav className={styles.bottomNav} aria-label="関連ページ">
            <Link href="/municipalities">自治体一覧</Link>
            <Link href="/projects#hyogo-prefecture">兵庫県重点事業</Link>
            <Link href="/projects#kobe-city">神戸市重点事業</Link>
            <Link href="/promises#hyogo-prefecture">知事公約{governorPromises.length}件</Link>
            <Link href="/promises#kobe-city">市長公約{mayorPromises.length}件</Link>
            <Link href="/assemblies/hyogo-prefecture">兵庫県議会</Link>
            <Link href="/assemblies/kobe-city">神戸市会</Link>
            <Link href="/methodology">評価方法</Link>
          </nav>
        </div>
      </main>
      <SiteFooter />
    </>
  );
}
