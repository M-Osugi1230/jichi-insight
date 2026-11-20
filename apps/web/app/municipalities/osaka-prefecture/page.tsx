import type { Metadata } from "next";
import Link from "next/link";

import { EvidencePanel } from "@/components/EvidencePanel";
import { FiscalReview } from "@/components/FiscalReview";
import { ProjectReview } from "@/components/ProjectReview";
import { MunicipalityDiscoveryPanel } from "@/components/MunicipalityDiscoveryPanel";
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
  osakaBudgetRecord,
  osakaEvidenceForRecord,
  osakaFinance,
  osakaFinanceSources,
  osakaPlanReview,
} from "@/lib/osakaPrefectureFinance";
import { canonicalFor } from "@/lib/pageMetadata";
import { assemblies } from "@/lib/assemblyRegistry";
import { projectRegistry } from "@/lib/projectRegistry";

import styles from "../fukuoka-prefecture/page.module.css";
import projectStyles from "@/components/ProjectReview.module.css";

export const metadata: Metadata = {
  alternates: { canonical: canonicalFor("/municipalities/osaka-prefecture") },
  title: "大阪府｜大阪府総合計画・2026年度当初予算・普通会計決算",
  description:
    "大阪府総合計画、2026年度に成立した一般会計当初予算、2022〜2024年度の普通会計決算、吉村洋文知事の現任期を一次資料とともに掲載します。",
};

export default function OsakaPrefecturePage() {
  const assembly = assemblies["osaka-prefecture"];
  const projects = projectRegistry["osaka-prefecture"];
  const reviewedProjects = projects.projects.filter((project) => project.review_status === "reviewed");
  const seriesCount = new Set(reviewedProjects.map((project) => project.series_id)).size;
  const budget = osakaBudgetRecord("total_revenue");
  const tax = osakaBudgetRecord("local_tax");
  const expenditure = osakaBudgetRecord("total_expenditure");
  const taxShare = budget?.amount_yen && tax?.amount_yen
    ? (tax.amount_yen / budget.amount_yen) * 100
    : null;
  const governor = currentExecutiveTerms.find((term) =>
    term.municipality_id === osakaFinance.municipality.id &&
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
              <h1>大阪府</h1>
              <p>
                大阪府総合計画の計画レビュー、2026年度一般会計の
                <strong>成立後当初予算</strong>、2022〜2024年度の
                <strong>普通会計決算</strong>を会計区分と段階を保って掲載します。
                道政の成果や知事の公約達成率を独自に判定しません。
              </p>
            </div>
            <dl className={styles.heroFacts}>
              <div><dt>Reviewed 財政レコード</dt><dd>{osakaFinance.records.length}件</dd></div>
              <div><dt>収録年度</dt><dd>2022〜2024・2026</dd></div>
              <div><dt>最終確認</dt><dd>{osakaFinance.municipality.last_verified_at}</dd></div>
            </dl>
          </section>

          <MunicipalityDiscoveryPanel
            officialCode={osakaFinance.municipality.official_code}
            planHref="#plan-title"
            budgetHref="#finance-headline-title"
            settlementHref="#fiscal-detail"
            fiscalDetailHref="#fiscal-detail"
            projectHref="#priority-projects"
          />

          <section className={styles.scope} aria-label="登録情報の範囲">
            <div>
              <p className="eyebrow">Scope</p>
              <h2 id="scope-title">計画・予算・決算・知事の任期を分けて確認する。</h2>
            </div>
            <div>
              <p>確認できること：大阪府総合計画の Reviewed 計画レビュー、2026年度の成立後一般会計当初予算、2022〜2024年度の普通会計決算51件、重点事業の Reviewed 10系列と道による一次政策評価（総合判定）、吉村洋文知事の現任期と公式出典です。</p>
              <p>確認できること：吉村洋文知事の公式選挙公報から Reviewed 公約原文15件が段階3で登録済みです。大阪府議会の議案・表決・政務活動費・情報公開状況は段階4で登録済みです。重点事業は段階2で10系列の Reviewed レコードを登録済みですが、全121施策の網羅や事業成果の独自判定ではありません。基本評価調書の「予算額」は当初予算ベースの施策単位合計額であり、決算額ではありません。未登録は実際の公表・実施の不存在を意味しません。</p>
              <p>大阪府総合計画は政策指標108件（重複を含め113件）が公表されていますが、このページの計画レビュー4項目を個別指標の達成度に置き換えません。一般会計と普通会計、予算と決算を直接連結した増減率・達成率は示しません。</p>
            </div>
          </section>

          <section className={styles.scope} aria-labelledby="plan-title">
            <div>
              <p className="eyebrow">Plan review</p>
              <h2 id="plan-title">大阪府総合計画の計画レビュー</h2>
              <p>Reviewed：{osakaPlanReview.reviewed_at}</p>
              <p><Link href="/municipalities/hokkaido">大阪府の政策指標108件を見る</Link></p>
            </div>
            <div>
              {osakaPlanReview.records.filter((record) => record.decision === "accepted").map((record) => (
                <article key={record.id}>
                  <h3>{record.title}</h3>
                  <p>{record.statement}</p>
                  <p>確認範囲：{record.evidence_location}</p>
                  <p>レビュー注記：{record.review_note}</p>
                  <p><a href={record.source_url} target="_blank" rel="noopener noreferrer">計画の公式出典を見る</a></p>
                </article>
              ))}
              <p>大阪府総合計画（2024年7月策定、2024年度から概ね10年間）に独立した実施計画文書は確認されていません。実施の管理単位は、政策体系に沿った基本評価調書の施策です。計画に記載された目標を政策成果と同一視しません。</p>
            </div>
          </section>

          <section className={styles.headline} aria-labelledby="finance-headline-title">
            <div className="sectionIntro">
              <p className="eyebrow">FY2026 enacted initial budget</p>
              <h2 id="finance-headline-title">2026年度に成立した一般会計当初予算</h2>
              <p>令和8年第1回大阪府議会定例会の議案第1号は2026年3月19日に原案可決され、提案額のまま成立しました。予算案の金額や補正予算と混同しません。</p>
            </div>
            <div className={styles.metricGrid}>
              <article className={styles.metricCard}>
                <span>一般会計当初予算（歳入規模）</span>
                <strong>{formatCompactYen(budget?.amount_yen ?? null)}</strong>
                <small>{formatExactYen(budget?.amount_yen ?? null)}</small>
                <p>2026年度・一般会計・成立後当初予算。</p>
              </article>
              <article className={styles.metricCard}>
                <span>府税収入</span>
                <strong>{formatCompactYen(tax?.amount_yen ?? null)}</strong>
                <small>{formatExactYen(tax?.amount_yen ?? null)}</small>
                <p>2026年度一般会計当初予算の公式議案に掲載された府税です。</p>
              </article>
              <article className={styles.metricCard}>
                <span>一般会計当初予算（歳出規模）</span>
                <strong>{formatCompactYen(expenditure?.amount_yen ?? null)}</strong>
                <small>{formatExactYen(expenditure?.amount_yen ?? null)}</small>
                <p>2026年度の成立後当初予算の歳出総額です。</p>
              </article>
              <article className={`${styles.metricCard} ${styles.derived}`}>
                <span>一般会計当初予算に占める府税収入</span>
                <strong>{taxShare === null ? "評価不能" : `${taxShare.toFixed(1)}%`}</strong>
                <small>Jichi Insight による単純計算</small>
                <p>府税収入 ÷ 一般会計当初予算。財政健全性や政策成果の評価ではありません。</p>
              </article>
            </div>
          </section>

          <div id="fiscal-detail" style={{ scrollMarginTop: 90 }}>
            <FiscalReview municipality="大阪府" records={osakaFinance.records} sources={osakaFinanceSources} />
          </div>

          <section className={styles.evidence} aria-labelledby="evidence-title">
            <div className="sectionIntro">
              <p className="eyebrow">Evidence trail</p>
              <h2 id="evidence-title">当初予算の登録値と公式資料の根拠</h2>
              <p>3件の一般会計当初予算と、出典の該当箇所・Reviewed 証拠パケットを確認できます。</p>
            </div>
            <div className={styles.evidenceGrid}>
              {[budget, tax, expenditure].filter((record) => record !== undefined).map((record) => (
                <EvidencePanel key={record.id} record={record} packet={osakaEvidenceForRecord(record.id)} />
              ))}
            </div>
          </section>

          <section id="priority-projects" className={styles.headline} aria-labelledby="priority-projects-title">
            <div className="sectionIntro">
              <p className="eyebrow">Reviewed priority projects</p>
              <h2 id="priority-projects-title">大阪府の重点施策の予算・KPI・道の公式評価</h2>
              <p>大阪府総合計画の3つの基本方向・政策の柱をたどり、令和7年度基本評価調書の公式掲載順から選定した {seriesCount} 系列・{reviewedProjects.length} 件の Reviewed 施策を掲載しています。全121施策の網羅ではなく、金額の大小による順位付けではありません。</p>
              <p><strong>基本評価調書の「予算額」は当初予算ベースの施策単位の合計額です。決算額、執行額、個別事務事業の額ではありません。</strong> 記録済みの総合判定は大阪府による<strong>一次政策評価の公式評価</strong>であり、Jichi Insight の独自評価ではありません。</p>
              <p>予算・KPI の目標値・実績値、一次評価の根拠を分けて表示します。<Link href="/projects#osaka-prefecture">大阪府の事業一覧を見る</Link></p>
            </div>
            <div className={projectStyles.cards}>
              {reviewedProjects.map((project) => (
                <article className={projectStyles.card} key={project.id}>
                  <p className={projectStyles.meta}>{project.fiscal_year}年度／{project.policy_area}／Reviewed</p>
                  <h3>{project.official_title}</h3>
                  <p>{project.plain_title}</p>
                  <p><strong>大阪府の一次政策評価・総合判定：{project.official_evaluation?.rating ?? "未収録"}</strong></p>
                  <p>{project.official_evaluation?.note ?? "公式評価の注記は未収録"}</p>
                  <ul>
                    {project.budget_records.map((record, index) => (
                      <li key={`${record.fiscal_year}-${record.kind}-${index}`}>
                        {record.fiscal_year}年度／基本評価調書の「予算額」（当初予算ベース・決算額ではありません）：
                        {record.amount_yen === null ? "未収録" : formatCompactYen(record.amount_yen)}
                        {record.note ? <p className={projectStyles.meta}>{record.note}</p> : null}
                      </li>
                    ))}
                  </ul>
                  <p className={projectStyles.meta}>Reviewed KPI：{projects.kpis.filter((kpi) =>
                    kpi.project_id === project.id && kpi.review_status === "reviewed",
                  ).length}件</p>
                  <details>
                    <summary>大阪府の一次政策評価・KPI・公式出典を詳しく見る</summary>
                    <ProjectReview area="osaka-prefecture" record={project} kpis={projects.kpis.filter(
                      (kpi) => kpi.project_id === project.id && kpi.review_status === "reviewed",
                    )} />
                  </details>
                  <p><Link href={`/projects/osaka-prefecture/${encodeURIComponent(project.series_id)}`}>この施策の年度別詳細を見る</Link></p>
                </article>
              ))}
            </div>
          </section>

          <section className={styles.scope} aria-labelledby="governor-title">
            <div>
              <p className="eyebrow">Executive term</p>
              <h2 id="governor-title">大阪府知事の現任期</h2>
              <p><Link href="/executives">首長台帳を見る</Link></p>
            </div>
            <div>
              {governor ? (
                <>
                  <h3>{governor.person_name} 知事</h3>
                  <p>任期：{formatDateJa(governor.term_start)} 〜 {formatDateJa(governor.term_end)}</p>
                  <p>選挙日：{formatDateJa(governor.election_date)} ／ 登録状態：{governor.review_status}</p>
                  <p>{governorPromises.length > 0
                    ? `Reviewed 公約原文：${governorPromises.length}件（段階3で登録済み）`
                    : "公約原文はこの知事の Reviewed 台帳に未登録です（不存在を意味しません）"}</p>
                  {governorPromises.length > 0 ? (
                    <p><Link href="/promises#osaka-prefecture">吉村洋文知事の公約原文15件と根拠を見る</Link></p>
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
                <p>知事の現任期は本サイトの Reviewed 台帳に未登録です。</p>
              )}
            </div>
          </section>

          <section id="assembly" className={styles.scope} aria-labelledby="assembly-title">
            <div>
              <p className="eyebrow">Reviewed assembly</p>
              <h2 id="assembly-title">大阪府議会の議案・表決と情報公開</h2>
              <p><Link href="/assemblies/osaka-prefecture">大阪府議会の議案・表決・政務活動費・情報公開の詳細を見る</Link></p>
            </div>
            <div>
              <p>大阪府議会の登録議案 {assembly.proposals.length}件、表決 {assembly.votes.length}件、政務活動費の集計 {assembly.expenses.length}レコードを公式資料に基づき掲載しています。</p>
              <p>議員個人別・会派別の賛否は公表されていません。政務活動費は集計値と閲覧制度のみが登録され、領収書の詳細を掲載していません。</p>
              <p>委員会視察・議員派遣は公表されていないため、実績を推測せず未登録とします。未公表は活動の不存在を意味しません。</p>
            </div>
          </section>

          <section className={styles.scope} aria-labelledby="sources-title">
            <div>
              <p className="eyebrow">Primary sources</p>
              <h2 id="sources-title">計画・予算・決算の公式資料</h2>
              <p>出典は省庁・道庁・道議会の一次資料です。</p>
            </div>
            <div>
              <ul>
                {osakaFinanceSources.map((source) => (
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
              <li>知事公約原文は Reviewed 15件登録済みですが、達成度や実績との因果関係は未判定です。</li>
              <li>大阪府議会の非公表の議員個人別・会派別賛否、委員会視察・議員派遣の個別記録</li>
              <li>登録済み10系列以外の事業全体の網羅、施策単位の決算・執行額、契約・監査との公式対応</li>
              <li>2026年度の執行実績と決算</li>
              <li>計画指標の年度実績と公表値に基づく政策成果判定</li>
            </ul>
          </section>

          <nav className={styles.bottomNav} aria-label="関連ページ">
            <Link href="/municipalities/hokkaido">大阪府の政策指標</Link>
            <Link href="/executives">首長台帳</Link>
            <Link href="/methodology">評価方法</Link>
            <Link href="/municipalities">自治体一覧</Link>
          </nav>
        </div>
      </main>
      <SiteFooter />
    </>
  );
}
