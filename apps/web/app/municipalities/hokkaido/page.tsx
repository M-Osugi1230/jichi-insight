import type { Metadata } from "next";
import Link from "next/link";

import { HokkaidoIndicatorExplorer } from "@/components/HokkaidoIndicatorExplorer";
import { PageIntro } from "@/components/PageIntro";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { StatusBadge } from "@/components/StatusBadge";
import {
  hokkaidoIndicatorGroups,
  hokkaidoIndicatorReviewStats,
} from "@/lib/hokkaidoIndicators";
import {
  hokkaidoPolicyHierarchyStats,
  reviewedHokkaidoPolicyDirections,
  reviewedHokkaidoPolicyHierarchy,
} from "@/lib/hokkaidoPolicies";
import { nationwidePrefectureCoverage } from "@/lib/nationwideCoverage";

import styles from "./page.module.css";

export const metadata: Metadata = {
  title: `北海道｜政策指標1〜${hokkaidoIndicatorReviewStats.reviewedIndicators}`,
  description:
    `北海道総合計画の政策体系とReviewed指標1〜${hokkaidoIndicatorReviewStats.reviewedIndicators}を、分野、現状値、中間目標、最終目標、比較上の注意、根拠資料とともに確認できます。`,
};

const hokkaidoCoverage = nationwidePrefectureCoverage.find(
  (record) => record.prefecture_code === "01",
);

const reviewedFieldIds = new Set(
  hokkaidoIndicatorGroups.map((group) => group.fieldId),
);

export default function HokkaidoPage() {
  return (
    <main>
      <SiteHeader />
      <div className="pageShell">
        <PageIntro eyebrow="Hokkaido policy indicators" title="北海道の政策指標を、原文と期間から読む。">
          <p>
            北海道総合計画の政策体系18分野と、公式の指標個票108件をすべてReviewed化して公開しています。
            現状値・中間目標・最終目標は確認済みですが、年度別実績とはまだ接続していないため、達成率や政策評価は表示しません。
          </p>
          <div className={styles.introLinks}>
            <Link href="/municipalities">全国47都道府県へ戻る</Link>
            {hokkaidoCoverage?.planSource ? (
              <a href={hokkaidoCoverage.planSource.url} target="_blank" rel="noreferrer">
                公式総合計画を開く ↗
              </a>
            ) : null}
          </div>
        </PageIntro>

        <section className={styles.summaryGrid} aria-label="北海道政策指標の公開状況">
          <article className={styles.summaryCard}>
            <span>Reviewed指標</span>
            <strong>{hokkaidoIndicatorReviewStats.reviewedIndicators}</strong>
            <p>公式番号1〜108を全件Reviewed済み。年度実績との接続は別工程です。</p>
          </article>
          <article className={styles.summaryCard}>
            <span>Reviewed分野</span>
            <strong>{hokkaidoIndicatorGroups.length}</strong>
            <p>食から歴史・文化・スポーツまで。政策体系18分野すべてです。</p>
          </article>
          <article className={styles.summaryCard}>
            <span>Evidence Packet</span>
            <strong>{hokkaidoIndicatorReviewStats.evidencePackets}</strong>
            <p>指標ごとに名称・数値・PDFページの根拠を保存。</p>
          </article>
          <article className={styles.summaryCard}>
            <span>年度実績へ接続済み</span>
            <strong>0</strong>
            <p>実績値を確認するまで達成率を算出しません。</p>
          </article>
        </section>

        <section className={styles.progressSection} aria-labelledby="review-progress-title">
          <div>
            <p className="eyebrow">Review coverage</p>
            <h2 id="review-progress-title">
              108 / 108のKPI本文Reviewedを完了。次は年度実績との接続。
            </h2>
          </div>
          <div className={styles.progressDetail}>
            <div className={styles.progressTrack} aria-hidden="true">
              <span
                style={{
                  width: `${(hokkaidoIndicatorReviewStats.reviewedIndicators / 108) * 100}%`,
                }}
              />
            </div>
            <dl>
              <div><dt>Reviewed</dt><dd>{hokkaidoIndicatorReviewStats.reviewedIndicators}指標</dd></div>
              <div><dt>次工程</dt><dd>年度実績接続</dd></div>
              <div><dt>更新日</dt><dd>2026年7月17日</dd></div>
            </dl>
            <p>
              この比率は政策成果の達成率ではなく、公式指標を人が照合した作業カバレッジです。
              目標を確認しただけで成果を評価したとは扱いません。
            </p>
          </div>
        </section>

        <section className="contentSection">
          <p className="eyebrow">Policy hierarchy</p>
          <h2>{reviewedHokkaidoPolicyHierarchy.plan_title_original}</h2>
          <p className={styles.sectionLead}>
            {reviewedHokkaidoPolicyHierarchy.plan_period_original}。3つの政策の方向と18分野を公式掲載順で登録し、{hokkaidoIndicatorGroups.length}分野すべての指標個票をReviewed化しています。
          </p>

          <div className={styles.directionGrid}>
            {reviewedHokkaidoPolicyDirections.map((direction) => {
              const reviewedFields = direction.fields.filter((field) =>
                reviewedFieldIds.has(field.id),
              );
              const allFieldsReviewed = reviewedFields.length === direction.fields.length;
              return (
                <article className={styles.directionCard} key={direction.id}>
                  <div className={styles.directionHeader}>
                    <span>{String(direction.display_order).padStart(2, "0")}</span>
                    <StatusBadge
                      label={allFieldsReviewed ? "全分野指標公開" : "一部指標公開"}
                      tone="progress"
                    />
                  </div>
                  <h3>{direction.title_original}</h3>
                  <p>{reviewedFields.length} / {direction.fields.length}分野で指標を公開</p>
                  <ul>
                    {direction.fields.map((field) => (
                      <li className={reviewedFieldIds.has(field.id) ? styles.reviewedField : undefined} key={field.id}>
                        <span>{field.title_original}</span>
                        <small>{reviewedFieldIds.has(field.id) ? "指標公開中" : "次工程"}</small>
                      </li>
                    ))}
                  </ul>
                </article>
              );
            })}
          </div>
          <p className={styles.hierarchyNote}>
            政策体系は{hokkaidoPolicyHierarchyStats.reviewedDirections}方向・{hokkaidoPolicyHierarchyStats.reviewedFields}分野をReviewed済みです。
            KPI本文のReviewed完了と、年度実績・政策評価の接続は別の品質段階として扱います。
          </p>
        </section>

        <section className="contentSection" id="indicators">
          <p className="eyebrow">Reviewed indicators</p>
          <h2>{hokkaidoIndicatorReviewStats.reviewedIndicators}指標を、分野と確認状態から探す。</h2>
          <p className={styles.sectionLead}>
            指標名や政策分野で検索し、目標設定の状態、現状値の有無、比較上の注意から絞り込めます。
            数字は公式個票の原文を保ち、単年度・累計・時点値を混ぜません。
          </p>
          <HokkaidoIndicatorExplorer />
        </section>

        <section className={`contentSection ${styles.boundary}`}>
          <div>
            <p className="eyebrow">Not assessed yet</p>
            <h2>目標を確認したことと、成果を確認したことは別です。</h2>
          </div>
          <ul>
            <li>年度別の実績値と集計条件</li>
            <li>定義変更・基準年変更・遡及改定の履歴</li>
            <li>目標との差が生じた理由</li>
            <li>関連する事業・予算・契約</li>
            <li>政策効果と指標変化の因果関係</li>
          </ul>
        </section>

        <nav className={styles.bottomNav} aria-label="関連ページ">
          <Link href="/policies">福岡県の政策体系</Link>
          <Link href="/data-quality">データ品質</Link>
          <Link href="/methodology">評価方法</Link>
          <Link href="/municipalities">全国自治体一覧</Link>
        </nav>
      </div>
      <SiteFooter />
    </main>
  );
}
