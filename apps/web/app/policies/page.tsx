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
  title: "政策体系",
  description:
    "福岡県と北海道の総合計画・政策指標を、原文・掲載順・数値目標・未接続範囲とともに確認できます。",
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
        <PageIntro eyebrow="Policy registry" title="政策評価の前に、計画が何を目指すかを構造化する。">
          <p>
            福岡県総合計画の4つの基本方向・30の取組事項と、北海道総合計画の政策体系・Reviewed指標1〜{hokkaidoIndicatorReviewStats.reviewedIndicators}を公開しています。
            数値目標は構造化しましたが、年度実績、予算、事業、公約との接続や達成度評価は行っていません。
          </p>
        </PageIntro>

        <section className={styles.prefectureIndex} aria-labelledby="prefecture-policy-title">
          <div>
            <p className="eyebrow">Prefecture policy views</p>
            <h2 id="prefecture-policy-title">自治体ごとに、確認できた深さを分ける。</h2>
          </div>
          <div className={styles.prefectureCards}>
            <article>
              <div><span>北海道</span><StatusBadge label="部分公開" tone="progress" /></div>
              <strong>{hokkaidoIndicatorReviewStats.reviewedIndicators} / 108指標</strong>
              <p>{hokkaidoIndicatorGroups.length}分野・指標1〜{hokkaidoIndicatorReviewStats.reviewedIndicators}をReviewed。残り{hokkaidoIndicatorReviewStats.remainingIndicators}指標と年度実績は未接続です。</p>
              <Link href="/municipalities/hokkaido">北海道の政策指標を見る</Link>
            </article>
            <article>
              <div><span>福岡県</span><StatusBadge label="Reviewed" tone="verified" /></div>
              <strong>{allPolicyTargetStats.reviewedTargets}数値目標</strong>
              <p>4方向・30取組を登録し、取組1〜26の数値目標を公開しています。</p>
              <a href="#fukuoka-policy">福岡県の政策体系を見る</a>
            </article>
          </div>
        </section>

        <section className={styles.summaryGrid} aria-label="政策体系の整備状況">
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
            <p className="eyebrow">Next extraction</p>
            <h2>次は取組27以降の数値目標を順に接続する。</h2>
            <p>
              同じ公式数値目標PDFから、基準値、目標値、期間、単位を保存します。
              年度実績が確認できるまでは進捗率や評価点を表示しません。
            </p>
          </div>
        </section>
      </div>
      <SiteFooter />
    </main>
  );
}
