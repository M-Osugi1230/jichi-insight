import type { Metadata } from "next";
import Link from "next/link";

import { EvidencePanel } from "@/components/EvidencePanel";
import { FiscalReview } from "@/components/FiscalReview";
import { MunicipalityDiscoveryPanel } from "@/components/MunicipalityDiscoveryPanel";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { StatusBadge } from "@/components/StatusBadge";
import {
  aichiBudgetRecord,
  aichiEvidenceForRecord,
  aichiFinance,
  aichiFinanceSources,
  aichiPlanReview,
} from "@/lib/aichiFinance";
import {
  currentExecutiveTerms,
  evidenceForExecutive,
  formatDateJa,
  sourcesForExecutive,
  promisesForExecutive,
} from "@/lib/executives";
import { formatCompactYen, formatExactYen } from "@/lib/finance";
import { canonicalFor } from "@/lib/pageMetadata";

import styles from "../fukuoka-prefecture/page.module.css";

export const metadata: Metadata = {
  alternates: { canonical: canonicalFor("/municipalities/aichi-prefecture") },
  title: "愛知県｜あいちビジョン2030・2026年度当初予算・普通会計決算",
  description: "愛知県の計画レビュー、成立後の2026年度一般会計当初予算、2022〜2024年度普通会計決算と大村秀章知事の現任期を一次資料付きで掲載します。",
};

export default function AichiPrefecturePage() {
  const budget = aichiBudgetRecord("total_revenue");
  const tax = aichiBudgetRecord("local_tax");
  const expenditure = aichiBudgetRecord("total_expenditure");
  const budgetShare = budget?.amount_yen && tax?.amount_yen
    ? (tax.amount_yen / budget.amount_yen) * 100 : null;
  const governor = currentExecutiveTerms.find((term) =>
    term.municipality_id === aichiFinance.municipality.id &&
    term.office === "governor" &&
    term.status === "current" &&
    (term.review_status === "reviewed" || term.review_status === "verified"),
  );
  const governorSources = governor ? sourcesForExecutive(governor) : [];
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
              <h1>愛知県</h1>
              <p>
                「あいちビジョン2030」の計画レビュー、2026年度一般会計の
                <strong>成立後当初予算</strong>、2022〜2024年度の
                <strong>普通会計決算</strong>を区別して掲載します。
                政策成果や首長の公約達成度を独自に評価するものではありません。
              </p>
            </div>
            <dl className={styles.heroFacts}>
              <div><dt>Reviewed 財政レコード</dt><dd>{aichiFinance.records.length}件</dd></div>
              <div><dt>収録年度</dt><dd>2022〜2024・2026</dd></div>
              <div><dt>最終確認</dt><dd>{aichiFinance.municipality.last_verified_at}</dd></div>
            </dl>
          </section>

          <MunicipalityDiscoveryPanel
            officialCode={aichiFinance.municipality.official_code}
            planHref="#scope-title"
            budgetHref="#finance-headline-title"
            settlementHref="#fiscal-detail"
            fiscalDetailHref="#fiscal-detail"
          />

          <section className={styles.scope} aria-label="登録情報の範囲">
            <div><p className="eyebrow">Scope</p><h2 id="scope-title">計画・予算・決算・知事の任期を分けて確認する。</h2></div>
            <div>
              <p>確認できること：「あいちビジョン2030」の計画構造と実施計画、2026年度の成立後一般会計当初予算、2022〜2024年度普通会計決算、大村秀章知事の登録済み現任期と公式出典。</p>
              <p>まだ確認できないこと：本サイトには愛知県知事の Reviewed 公約、重点事業、県議会の個別レコードが未登録です。未登録は実際の公表・実施の不存在を意味しません。個別の公約達成度や政策成果を推定しません。</p>
              <p>一般会計と普通会計、予算と決算は範囲・段階が異なります。直接つないで増減率や達成率とは扱いません。</p>
            </div>
          </section>

          <section className={styles.scope} aria-labelledby="plan-title">
            <div>
              <p className="eyebrow">Plan review</p>
              <h2 id="plan-title">あいちビジョン2030の計画レビュー</h2>
              <p>Reviewed：{aichiPlanReview.reviewed_at}</p>
              <p><Link href="/municipalities/aichi">政策目標・進捗指標の専用ページを見る</Link></p>
            </div>
            <div>
              {aichiPlanReview.records.filter((record) => record.decision === "accepted").map((record) => (
                <article key={record.id}>
                  <h3>{record.title}</h3>
                  <p>{record.statement}</p>
                  <p>確認範囲：{record.evidence_location}</p>
                  <p>レビュー注記：{record.review_note}</p>
                  <p><a href={record.source_url} target="_blank" rel="noopener noreferrer">計画の公式出典を見る</a></p>
                </article>
              ))}
              <p>47の主要政策の個別列挙はこの計画レビューの対象外です。計画の記載と事業成果を同一視しません。</p>
            </div>
          </section>

          <section className={styles.headline} aria-labelledby="finance-headline-title">
            <div className="sectionIntro">
              <p className="eyebrow">FY2026 enacted initial budget</p>
              <h2 id="finance-headline-title">2026年度に成立した一般会計当初予算</h2>
              <p>令和8年2月定例県議会の第1号議案は2026年3月25日に可決され、提案額どおり成立しました。補正予算や複数月を合算した予算とは区別します。</p>
            </div>
            <div className={styles.metricGrid}>
              <article className={styles.metricCard}>
                <span>一般会計当初予算（歳入規模）</span>
                <strong>{formatCompactYen(budget?.amount_yen ?? null)}</strong>
                <small>{formatExactYen(budget?.amount_yen ?? null)}</small>
                <p>2026年度・一般会計・成立後当初予算。</p>
              </article>
              <article className={styles.metricCard}>
                <span>県税収入</span>
                <strong>{formatCompactYen(tax?.amount_yen ?? null)}</strong>
                <small>{formatExactYen(tax?.amount_yen ?? null)}</small>
                <p>2026年度当初予算の公式資料に記録された県税収入。</p>
              </article>
              <article className={styles.metricCard}>
                <span>一般会計当初予算（歳出規模）</span>
                <strong>{formatCompactYen(expenditure?.amount_yen ?? null)}</strong>
                <small>{formatExactYen(expenditure?.amount_yen ?? null)}</small>
                <p>予算に関する説明書に記載された歳出総額。</p>
              </article>
              <article className={`${styles.metricCard} ${styles.derived}`}>
                <span>一般会計当初予算に占める県税収入</span>
                <strong>{budgetShare === null ? "評価不能" : `${budgetShare.toFixed(1)}%`}</strong>
                <small>Jichi Insight による単純計算</small>
                <p>県税収入 ÷ 一般会計当初予算。政策成果や財政健全性の判定ではありません。</p>
              </article>
            </div>
          </section>

          <div id="fiscal-detail" style={{ scrollMarginTop: 90 }}>
            <FiscalReview municipality="愛知県" records={aichiFinance.records} sources={aichiFinanceSources} />
          </div>

          <section className={styles.evidence} aria-labelledby="evidence-title">
            <div className="sectionIntro">
              <p className="eyebrow">Evidence trail</p>
              <h2 id="evidence-title">予算の登録値と公式資料の根拠</h2>
              <p>一般会計当初予算の各数値と、資料の該当箇所・レビュー状態を確認できます。</p>
            </div>
            <div className={styles.evidenceGrid}>
              {[budget, tax, expenditure].filter((record) => record !== undefined).map((record) => (
                <EvidencePanel key={record.id} record={record} packet={aichiEvidenceForRecord(record.id)} />
              ))}
            </div>
          </section>

          <section className={styles.scope} aria-labelledby="governor-title">
            <div>
              <p className="eyebrow">Executive term</p>
              <h2 id="governor-title">知事の現任期</h2>
              <p><Link href="/executives">首長台帳を見る</Link></p>
            </div>
            <div>
              {governor ? (
                <>
                  <h3>{governor.person_name} 知事</h3>
                  <p>任期：{formatDateJa(governor.term_start)} 〜 {formatDateJa(governor.term_end)}</p>
                  <p>選挙日：{formatDateJa(governor.election_date)} ／ 登録状態：{governor.review_status}</p>
                  <p>{governorPromises.length > 0 ? `Reviewed 公約原文：${governorPromises.length}件` : "公約原文：未登録（公約の不存在や未公表を意味しません）"}</p>
                  {governorSources.map((source) => (
                    <p key={source.id}><a href={source.url} target="_blank" rel="noopener noreferrer">{source.title}</a></p>
                  ))}
                  {governorEvidence?.open_questions.length ? (
                    <p>未確認事項：{governorEvidence.open_questions.join("／")}</p>
                  ) : null}
                </>
              ) : (
                <p>知事の現任期は本サイトの Reviewed 台帳に未登録です。</p>
              )}
            </div>
          </section>

          <section className={styles.scope} aria-labelledby="sources-title">
            <div><p className="eyebrow">Official sources</p><h2 id="sources-title">公式出典一覧</h2></div>
            <div>
              <ul>
                {aichiFinanceSources.map((source) => (
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
              <li>知事の公約原文と達成度（本サイトへの公約登録は未実施）</li>
              <li>重点事業の個別予算・実施状況・KPI</li>
              <li>県議会の議案・表決・監視活動の個別記録</li>
              <li>2026年度予算の執行実績・決算</li>
            </ul>
          </section>

          <nav className={styles.bottomNav} aria-label="関連ページ">
            <Link href="/municipalities/aichi">愛知県の政策・進捗指標</Link>
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
