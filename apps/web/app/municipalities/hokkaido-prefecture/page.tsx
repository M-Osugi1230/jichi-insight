import type { Metadata } from "next";
import Link from "next/link";

import { EvidencePanel } from "@/components/EvidencePanel";
import { FiscalReview } from "@/components/FiscalReview";
import { MunicipalityDiscoveryPanel } from "@/components/MunicipalityDiscoveryPanel";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { StatusBadge } from "@/components/StatusBadge";
import {
  currentExecutiveTerms,
  evidenceForExecutive,
  formatDateJa,
  promisesForExecutive,
  sourcesForExecutive,
} from "@/lib/executives";
import { formatCompactYen, formatExactYen } from "@/lib/finance";
import {
  hokkaidoBudgetRecord,
  hokkaidoEvidenceForRecord,
  hokkaidoFinance,
  hokkaidoFinanceSources,
  hokkaidoPlanReview,
} from "@/lib/hokkaidoFinance";
import { canonicalFor } from "@/lib/pageMetadata";

import styles from "../fukuoka-prefecture/page.module.css";

export const metadata: Metadata = {
  alternates: { canonical: canonicalFor("/municipalities/hokkaido-prefecture") },
  title: "北海道｜北海道総合計画・2026年度当初予算・普通会計決算",
  description:
    "北海道総合計画、2026年度に成立した一般会計当初予算、2022〜2024年度の普通会計決算、鈴木直道知事の現任期を一次資料とともに掲載します。",
};

export default function HokkaidoPrefecturePage() {
  const budget = hokkaidoBudgetRecord("total_revenue");
  const tax = hokkaidoBudgetRecord("local_tax");
  const expenditure = hokkaidoBudgetRecord("total_expenditure");
  const taxShare = budget?.amount_yen && tax?.amount_yen
    ? (tax.amount_yen / budget.amount_yen) * 100
    : null;
  const governor = currentExecutiveTerms.find((term) =>
    term.municipality_id === hokkaidoFinance.municipality.id &&
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
              <h1>北海道</h1>
              <p>
                北海道総合計画の計画レビュー、2026年度一般会計の
                <strong>成立後当初予算</strong>、2022〜2024年度の
                <strong>普通会計決算</strong>を会計区分と段階を保って掲載します。
                道政の成果や知事の公約達成率を独自に判定しません。
              </p>
            </div>
            <dl className={styles.heroFacts}>
              <div><dt>Reviewed 財政レコード</dt><dd>{hokkaidoFinance.records.length}件</dd></div>
              <div><dt>収録年度</dt><dd>2022〜2024・2026</dd></div>
              <div><dt>最終確認</dt><dd>{hokkaidoFinance.municipality.last_verified_at}</dd></div>
            </dl>
          </section>

          <MunicipalityDiscoveryPanel
            officialCode={hokkaidoFinance.municipality.official_code}
            planHref="#plan-title"
            budgetHref="#finance-headline-title"
            settlementHref="#fiscal-detail"
            fiscalDetailHref="#fiscal-detail"
          />

          <section className={styles.scope} aria-label="登録情報の範囲">
            <div>
              <p className="eyebrow">Scope</p>
              <h2 id="scope-title">計画・予算・決算・知事の任期を分けて確認する。</h2>
            </div>
            <div>
              <p>確認できること：北海道総合計画の Reviewed 計画レビュー、2026年度の成立後一般会計当初予算、2022〜2024年度の普通会計決算51件、鈴木直道知事の現任期と公式出典です。</p>
              <p>まだ登録・評価していないこと：知事公約の原文は未登録（段階3で登録予定）、北海道議会の個別レコードは未登録（段階4で登録予定）です。重点事業は段階2で登録中であり、このページに個別事業の成果を掲載していません。未登録は実際の公表・実施の不存在を意味しません。</p>
              <p>北海道総合計画は政策指標108件（重複を含め113件）が公表されていますが、このページの計画レビュー4項目を個別指標の達成度に置き換えません。一般会計と普通会計、予算と決算を直接連結した増減率・達成率は示しません。</p>
            </div>
          </section>

          <section className={styles.scope} aria-labelledby="plan-title">
            <div>
              <p className="eyebrow">Plan review</p>
              <h2 id="plan-title">北海道総合計画の計画レビュー</h2>
              <p>Reviewed：{hokkaidoPlanReview.reviewed_at}</p>
              <p><Link href="/municipalities/hokkaido">北海道の政策指標108件を見る</Link></p>
            </div>
            <div>
              {hokkaidoPlanReview.records.filter((record) => record.decision === "accepted").map((record) => (
                <article key={record.id}>
                  <h3>{record.title}</h3>
                  <p>{record.statement}</p>
                  <p>確認範囲：{record.evidence_location}</p>
                  <p>レビュー注記：{record.review_note}</p>
                  <p><a href={record.source_url} target="_blank" rel="noopener noreferrer">計画の公式出典を見る</a></p>
                </article>
              ))}
              <p>北海道総合計画（2024年7月策定、2024年度から概ね10年間）に独立した実施計画文書は確認されていません。実施の管理単位は、政策体系に沿った基本評価調書の施策です。計画に記載された目標を政策成果と同一視しません。</p>
            </div>
          </section>

          <section className={styles.headline} aria-labelledby="finance-headline-title">
            <div className="sectionIntro">
              <p className="eyebrow">FY2026 enacted initial budget</p>
              <h2 id="finance-headline-title">2026年度に成立した一般会計当初予算</h2>
              <p>令和8年第1回北海道議会定例会の議案第1号は2026年3月19日に原案可決され、提案額のまま成立しました。予算案の金額や補正予算と混同しません。</p>
            </div>
            <div className={styles.metricGrid}>
              <article className={styles.metricCard}>
                <span>一般会計当初予算（歳入規模）</span>
                <strong>{formatCompactYen(budget?.amount_yen ?? null)}</strong>
                <small>{formatExactYen(budget?.amount_yen ?? null)}</small>
                <p>2026年度・一般会計・成立後当初予算。</p>
              </article>
              <article className={styles.metricCard}>
                <span>道税収入</span>
                <strong>{formatCompactYen(tax?.amount_yen ?? null)}</strong>
                <small>{formatExactYen(tax?.amount_yen ?? null)}</small>
                <p>2026年度一般会計当初予算の公式議案に掲載された道税です。</p>
              </article>
              <article className={styles.metricCard}>
                <span>一般会計当初予算（歳出規模）</span>
                <strong>{formatCompactYen(expenditure?.amount_yen ?? null)}</strong>
                <small>{formatExactYen(expenditure?.amount_yen ?? null)}</small>
                <p>2026年度の成立後当初予算の歳出総額です。</p>
              </article>
              <article className={`${styles.metricCard} ${styles.derived}`}>
                <span>一般会計当初予算に占める道税収入</span>
                <strong>{taxShare === null ? "評価不能" : `${taxShare.toFixed(1)}%`}</strong>
                <small>Jichi Insight による単純計算</small>
                <p>道税収入 ÷ 一般会計当初予算。財政健全性や政策成果の評価ではありません。</p>
              </article>
            </div>
          </section>

          <div id="fiscal-detail" style={{ scrollMarginTop: 90 }}>
            <FiscalReview municipality="北海道" records={hokkaidoFinance.records} sources={hokkaidoFinanceSources} />
          </div>

          <section className={styles.evidence} aria-labelledby="evidence-title">
            <div className="sectionIntro">
              <p className="eyebrow">Evidence trail</p>
              <h2 id="evidence-title">当初予算の登録値と公式資料の根拠</h2>
              <p>3件の一般会計当初予算と、出典の該当箇所・Reviewed 証拠パケットを確認できます。</p>
            </div>
            <div className={styles.evidenceGrid}>
              {[budget, tax, expenditure].filter((record) => record !== undefined).map((record) => (
                <EvidencePanel key={record.id} record={record} packet={hokkaidoEvidenceForRecord(record.id)} />
              ))}
            </div>
          </section>

          <section className={styles.scope} aria-labelledby="governor-title">
            <div>
              <p className="eyebrow">Executive term</p>
              <h2 id="governor-title">北海道知事の現任期</h2>
              <p><Link href="/executives">首長台帳を見る</Link></p>
            </div>
            <div>
              {governor ? (
                <>
                  <h3>{governor.person_name} 知事</h3>
                  <p>任期：{formatDateJa(governor.term_start)} 〜 {formatDateJa(governor.term_end)}</p>
                  <p>選挙日：{formatDateJa(governor.election_date)} ／ 登録状態：{governor.review_status}</p>
                  <p>{governorPromises.length > 0
                    ? `Reviewed 公約原文：${governorPromises.length}件`
                    : "公約原文：未登録（段階3で登録予定。公約の不存在や未公表を意味しません）"}</p>
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

          <section className={styles.scope} aria-labelledby="sources-title">
            <div>
              <p className="eyebrow">Primary sources</p>
              <h2 id="sources-title">計画・予算・決算の公式資料</h2>
              <p>出典は省庁・道庁・道議会の一次資料です。</p>
            </div>
            <div>
              <ul>
                {hokkaidoFinanceSources.map((source) => (
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
              <li>知事公約の原文・進捗・達成度（段階3で登録予定）</li>
              <li>北海道議会の議案・表決・監視活動の個別記録（段階4で登録予定）</li>
              <li>重点事業の個別予算・KPI・実績（段階2で登録中）</li>
              <li>2026年度の執行実績と決算</li>
              <li>計画指標の年度実績と公表値に基づく政策成果判定</li>
            </ul>
          </section>

          <nav className={styles.bottomNav} aria-label="関連ページ">
            <Link href="/municipalities/hokkaido">北海道の政策指標</Link>
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
