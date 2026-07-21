import type { Metadata } from "next";
import Link from "next/link";

import { PageIntro } from "@/components/PageIntro";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { StatusBadge } from "@/components/StatusBadge";
import {
  hokkaidoIndicatorGroups,
  hokkaidoIndicatorReviewStats,
} from "@/lib/hokkaidoIndicators";
import { miyagiKpiActualStats } from "@/lib/miyagiActuals";
import { miyagiPolicyReviewStats } from "@/lib/miyagiPolicies";
import {
  evidenceForPolicyDirection,
  fukuokaPolicyDirections,
  fukuokaPolicyInitiativeCatalog,
  initiativesForPolicyDirection,
  policyDirectionStats,
  policyInitiativeStats,
  sourcesForPolicyDirection,
} from "@/lib/policies";
import { allPolicyTargetStats, policyTargetPages } from "@/lib/policyTargets";

import styles from "./page.module.css";

export const metadata: Metadata = {
  title: "政策と成果",
  description:
    "北海道・宮城県・福岡県の政策体系、数値目標、年度実績、未接続範囲を一次資料から確認できます。",
};

const targetDetails = Object.fromEntries(
  policyTargetPages.map((page) => [
    Number(page.slug),
    {
      href: `/policies/fukuoka-prefecture/initiatives/${page.slug}`,
      count: page.catalog.items.length,
    },
  ]),
) as Record<number, { href: string; count: number }>;

export default function PoliciesPage() {
  return (
    <main>
      <SiteHeader />
      <div className="pageShell">
        <PageIntro eyebrow="Policies and results" title="目標を読み、実績の有無を確かめる。">
          <p>
            北海道の全{hokkaidoIndicatorReviewStats.reviewedIndicators}指標、宮城県の全{miyagiPolicyReviewStats.reviewedTargetGroups}目標と{miyagiKpiActualStats.annualResultRows}件の年度実績、
            福岡県の4基本方向・30取組と{allPolicyTargetStats.reviewedTargets}数値目標を公開しています。実績がないものに達成率は付けません。
          </p>
        </PageIntro>

        <section className={styles.prefectureIndex} aria-labelledby="prefecture-policy-title">
          <div>
            <p className="eyebrow">Prefecture policy views</p>
            <h2 id="prefecture-policy-title">自治体ごとに、確認できた深さを分ける。</h2>
          </div>
          <div className={styles.prefectureCards}>
            <article>
              <div><span>北海道</span><StatusBadge label="KPI全件Reviewed" tone="verified" /></div>
              <strong>{hokkaidoIndicatorReviewStats.reviewedIndicators}指標</strong>
              <p>{hokkaidoIndicatorGroups.length}分野の全指標を照合済み。年度実績は未接続のため、計画の目標設計を読むページです。</p>
              <Link href="/municipalities/hokkaido">北海道の政策指標を見る</Link>
            </article>
            <article>
              <div><span>宮城県</span><StatusBadge label="年度実績あり" tone="verified" /></div>
              <strong>{miyagiPolicyReviewStats.reviewedTargetGroups}目標・{miyagiKpiActualStats.annualResultRows}実績</strong>
              <p>{miyagiKpiActualStats.linkedSeries}系列を直接接続し、{miyagiKpiActualStats.reviewNeededSeries}系列は定義差などの要確認として分けています。</p>
              <Link href="/municipalities/miyagi#results">宮城県の年度実績を見る</Link>
            </article>
            <article>
              <div><span>福岡県</span><StatusBadge label="Reviewed" tone="verified" /></div>
              <strong>{allPolicyTargetStats.reviewedTargets}数値目標</strong>
              <p>4方向・30取組を登録し、取組1〜26の数値目標を公開しています。</p>
              <a href="#fukuoka-policy">福岡県の政策体系を見る</a>
            </article>
          </div>
        </section>

        <section className={styles.summaryGrid} aria-label="福岡県政策体系の整備状況">
          <article className={styles.summaryCard}><span>Reviewed基本方向</span><strong>{policyDirectionStats.reviewedDirections}</strong><p>福岡県総合計画の公式掲載順で登録。</p></article>
          <article className={styles.summaryCard}><span>Reviewed取組事項</span><strong>{policyInitiativeStats.reviewedInitiatives}</strong><p>目次PDFの1番から30番までを原文で登録。</p></article>
          <article className={styles.summaryCard}><span>Reviewed数値目標</span><strong>{allPolicyTargetStats.reviewedTargets}</strong><p>取組1から26の指標1から118まで。</p></article>
          <article className={styles.summaryCard}><span>年度実績へ接続済み</span><strong>{allPolicyTargetStats.actualsLinked}</strong><p>年度報告の実績との個別対応は次工程。</p></article>
          <article className={styles.summaryCard}><span>政策評価済み</span><strong>{policyInitiativeStats.assessed}</strong><p>計画文と目標値だけでは成果を評価しません。</p></article>
        </section>

        <section className="contentSection" id="fukuoka-policy">
          <p className="eyebrow">Fukuoka Prefecture 2022–2026</p>
          <h2>4つの基本方向と30の取組事項</h2>
          <p className={styles.sectionLead}>
            取組事項の番号と開始ページは公式目次に基づきます。数値目標が確認できた取組には詳細ページを設けていますが、年度進捗が確認できるまでは「未接続・未評価」です。
          </p>
          <a className={styles.catalogLink} href={fukuokaPolicyInitiativeCatalog.source_document_url} target="_blank" rel="noreferrer">
            公式目次PDFを開く ↗
          </a>

          <div className={styles.directionGrid}>
            {fukuokaPolicyDirections.map((direction) => {
              const sources = sourcesForPolicyDirection(direction);
              const evidence = evidenceForPolicyDirection(direction);
              const initiatives = initiativesForPolicyDirection(direction);
              return (
                <article className={styles.directionCard} key={direction.id}>
                  <div className={styles.order} aria-label={`基本方向${direction.display_order}`}>
                    {String(direction.display_order).padStart(2, "0")}
                  </div>
                  <div className={styles.directionMain}>
                    <p>Strategic direction</p>
                    <h3>{direction.title_original}</h3>
                    <p>{direction.source_location}</p>
                    {sources.map((source) => (
                      <a href={source.url} target="_blank" rel="noreferrer" key={source.id}>公式計画を開く ↗</a>
                    ))}
                  </div>
                  <dl className={styles.directionFacts}>
                    <div><dt>計画期間</dt><dd>{direction.plan_period_start}–{direction.plan_period_end}年度</dd></div>
                    <div><dt>取組事項</dt><dd>{initiatives.length}件</dd></div>
                    <div><dt>レビュー</dt><dd><StatusBadge label="Reviewed" tone="verified" /></dd></div>
                    <div><dt>年度進捗</dt><dd>未接続</dd></div>
                    <div><dt>評価</dt><dd>未評価</dd></div>
                  </dl>

                  <div className={styles.initiativeList}>
                    <p>Policy initiatives</p>
                    <ol start={initiatives[0]?.sequence_number}>
                      {initiatives.map((initiative) => {
                        const detail = targetDetails[initiative.sequence_number];
                        return (
                          <li key={initiative.id} value={initiative.sequence_number}>
                            <div>
                              {detail ? (
                                <Link href={detail.href}><strong>{initiative.title_original}</strong></Link>
                              ) : (
                                <strong>{initiative.title_original}</strong>
                              )}
                              <span>計画本文 {initiative.plan_page_start}ページ</span>
                            </div>
                            <div className={styles.initiativeStatus}>
                              {detail ? <span>数値目標{detail.count}件</span> : null}
                              <span>進捗未接続</span>
                              <span>未評価</span>
                            </div>
                          </li>
                        );
                      })}
                    </ol>
                  </div>

                  <div className={styles.questions}>
                    <p>Open questions</p>
                    <ul>{evidence?.open_questions.map((question) => <li key={question}>{question}</li>)}</ul>
                  </div>
                </article>
              );
            })}
          </div>
        </section>

        <section className={`contentSection ${styles.boundary}`}>
          <div>
            <p className="eyebrow">What remains</p>
            <h2>取組と目標の一覧と、実際の成果はまだ別々です。</h2>
          </div>
          <ul>
            <li>取組27から30の数値目標</li>
            <li>2022–2024年度の実績推移</li>
            <li>関連する事業・予算・契約</li>
            <li>知事公約との根拠付き対応関係</li>
            <li>未達・変更・延期に関する公式説明</li>
          </ul>
        </section>

        <section className="callout callout--dark">
          <div>
            <p className="eyebrow">Evidence boundary</p>
            <h2>目標があっても、実績がなければ評価しない。</h2>
            <p>
              福岡県は年度実績との対応が未接続です。宮城県のように公式評価書と定義を照合できるまで、
              独自の進捗率や評価点を表示しません。
            </p>
          </div>
        </section>
      </div>
      <SiteFooter />
    </main>
  );
}
