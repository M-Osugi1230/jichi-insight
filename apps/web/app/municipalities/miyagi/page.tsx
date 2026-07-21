import type { Metadata } from "next";
import Link from "next/link";

import { MiyagiResultExplorer } from "@/components/MiyagiResultExplorer";
import { PageIntro } from "@/components/PageIntro";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { StatusBadge } from "@/components/StatusBadge";
import {
  miyagiKpiActualBySeriesId,
  miyagiKpiActualStats,
} from "@/lib/miyagiActuals";
import {
  miyagiKpiScopes,
  miyagiPolicyReviewStats,
  reviewedMiyagiPolicyDirections,
  reviewedMiyagiPolicyHierarchy,
  type MiyagiKpiValue,
} from "@/lib/miyagiPolicies";

import styles from "./page.module.css";

export const metadata: Metadata = {
  title: `宮城県｜政策目標${miyagiPolicyReviewStats.reviewedTargetGroups}件・年度実績${miyagiKpiActualStats.annualResultRows}件`,
  description:
    `宮城県の政策目標${miyagiPolicyReviewStats.reviewedTargetGroups}件と、${miyagiKpiActualStats.reviewedLinks}系列・${miyagiKpiActualStats.annualResultRows}件の年度実績を、公式評価書と現行計画の目標を分けて確認できます。`,
};

const implementationPlanUrl =
  "https://www.pref.miyagi.jp/documents/22609/jisshikeikaku2r8.pdf";
const evaluationDocumentUrl =
  "https://www.pref.miyagi.jp/documents/59769/r7-seikatohyouka_1.pdf";

const roleLabels: Record<MiyagiKpiValue["role"], string> = {
  initial: "初期値",
  current: "現況値",
  midterm_target: "中期末目標",
  late_target: "後期末目標",
};

function valueLabel(value: MiyagiKpiValue, unit: string) {
  if (value.status === "not_set") return "未設定";
  if (value.status === "not_available") return "未公表";
  return `${value.value_text_original}${unit}`;
}

export default function MiyagiPage() {
  return (
    <main id="main-content">
      <SiteHeader />
      <div className="pageShell">
        <PageIntro eyebrow="Miyagi / Plans and results" title="目標と実績を、同じものにしない。">
          <p>
            宮城県の現行中期実施計画にある全{miyagiPolicyReviewStats.reviewedTargetGroups}目標と、
            令和3〜6年度の公式評価書にある{miyagiKpiActualStats.annualResultRows}件の実績を公開します。
            評価書の目標と現行計画の目標は別の基準として表示します。
          </p>
          <div className={styles.introLinks}>
            <Link href="/municipalities">全国47都道府県へ戻る</Link>
            <a href={implementationPlanUrl} target="_blank" rel="noreferrer">現行中期実施計画 ↗</a>
            <a href={evaluationDocumentUrl} target="_blank" rel="noreferrer">令和7年度評価書 ↗</a>
          </div>
        </PageIntro>

        <section className={styles.summaryGrid} aria-label="宮城県政策データの公開状況">
          <article><span>Reviewed目標</span><strong>{miyagiPolicyReviewStats.reviewedTargetGroups}</strong><p>名称・値・単位・期間を照合。未Reviewedは{miyagiPolicyReviewStats.remainingTargetGroups}件。</p></article>
          <article><span>指標系列</span><strong>{miyagiPolicyReviewStats.reviewedIndicatorSeries}</strong><p>複数系列を1つの目標へまとめた構造を保持。</p></article>
          <article className={styles.emphasis}><span>年度実績へ直接接続</span><strong>{miyagiKpiActualStats.linkedSeries}</strong><p>名称・単位・定義を確認して目標へ接続。</p></article>
          <article className={styles.warning}><span>対応要確認</span><strong>{miyagiKpiActualStats.reviewNeededSeries}</strong><p>定義や対象範囲の差を残して追加確認中。</p></article>
          <article><span>年度実績</span><strong>{miyagiKpiActualStats.annualResultRows}</strong><p>2021〜2024年度、{miyagiKpiActualStats.reviewedLinks}系列分。</p></article>
        </section>

        <section className={styles.distinction} aria-labelledby="miyagi-distinction-title">
          <div>
            <p className="eyebrow">Important distinction</p>
            <h2 id="miyagi-distinction-title">2つの目標を、混ぜない。</h2>
          </div>
          <div className={styles.distinctionCards}>
            <article>
              <span>公式評価書</span>
              <h3>令和6年度までの評価目標</h3>
              <p>年度実績と公式進捗率は、この評価書に記載された旧目標を基準にしています。</p>
            </article>
            <article>
              <span>現行中期実施計画</span>
              <h3>令和9年度の中期末目標</h3>
              <p>現在の政策目標です。旧評価書の進捗率を、この目標の達成率として流用しません。</p>
            </article>
          </div>
        </section>

        <section className="contentSection" id="results">
          <div className={styles.sectionHeading}>
            <div>
              <p className="eyebrow">Annual results</p>
              <h2>年度実績を、指標ごとに確かめる。</h2>
            </div>
            <p>
              公式評価書の値と進捗率を原文のまま表示します。Jichi Insight独自の達成率や評価点ではありません。
            </p>
          </div>
          <MiyagiResultExplorer />
        </section>

        <section className="contentSection">
          <div className={styles.sectionHeading}>
            <div>
              <p className="eyebrow">Policy hierarchy</p>
              <h2>{reviewedMiyagiPolicyHierarchy.plan_title_original}</h2>
            </div>
            <p>
              {reviewedMiyagiPolicyHierarchy.plan_period_original}。4基本方向・8政策・18取組を公式掲載順で保持しています。
            </p>
          </div>
          <div className={styles.directionGrid}>
            {reviewedMiyagiPolicyDirections.map((direction) => (
              <article className={styles.directionCard} key={direction.id}>
                <div className={styles.directionHeader}>
                  <span>{String(direction.display_order).padStart(2, "0")}</span>
                  <StatusBadge label="KPI本文Reviewed" tone="verified" />
                </div>
                <h3>{direction.title_original}</h3>
                <ul>
                  {direction.policies.map((policy) => (
                    <li key={policy.id}>
                      <strong>政策{policy.policy_number}</strong>
                      <span>{policy.title_original}</span>
                      <small>{policy.measures.length}取組</small>
                    </li>
                  ))}
                </ul>
              </article>
            ))}
          </div>
        </section>

        <section className="contentSection" id="indicators">
          <div className={styles.sectionHeading}>
            <div>
              <p className="eyebrow">Current plan targets</p>
              <h2>現行計画の全{miyagiPolicyReviewStats.reviewedTargetGroups}目標。</h2>
            </div>
            <p>
              初期値、現況値、令和9年度の中期末目標、令和12年度の後期末目標を、未設定や累計表記も含めて確認できます。
            </p>
          </div>

          <div className={styles.scopeStack}>
            {miyagiKpiScopes.map((scope, index) => (
              <details className={styles.scopeSection} key={scope.id} open={index === 0}>
                <summary className={styles.scopeHeader}>
                  <div><span>{scope.label}</span><h3>{scope.title}</h3></div>
                  <strong>{scope.groups.length}目標 <em>＋</em></strong>
                </summary>
                <div className={styles.indicatorGrid}>
                  {scope.groups.map((group) => {
                    const actualRecords = group.series
                      .map((series) => miyagiKpiActualBySeriesId.get(series.id))
                      .filter((record) => record !== undefined);
                    const hasDirectLink = actualRecords.some((record) => record.linkage_status === "linked");
                    const needsReview = actualRecords.some((record) => record.linkage_status === "needs_review");
                    return (
                      <article className={styles.indicatorCard} key={group.id}>
                        <div className={styles.indicatorTop}>
                          <span>目標値No.{group.target_group_number}</span>
                          <StatusBadge
                            label={hasDirectLink ? "年度実績あり" : needsReview ? "実績対応要確認" : "実績未接続"}
                            tone={hasDirectLink ? "verified" : needsReview ? "warning" : "neutral"}
                          />
                        </div>
                        {group.series.map((series) => (
                          <div className={styles.seriesBlock} key={series.id}>
                            <h4>{series.indicator_name_original}</h4>
                            <dl className={styles.valueGrid}>
                              {series.values.map((value) => (
                                <div key={value.role}>
                                  <dt>{roleLabels[value.role]}</dt>
                                  <dd>{valueLabel(value, series.unit_original)}</dd>
                                  <small>{value.period_original}（{value.period_year}年）</small>
                                </div>
                              ))}
                            </dl>
                            {series.aggregation_scope === "cumulative_to_date" ? (
                              <p className={styles.dataNote}>累計値。単年度値には変換していません。</p>
                            ) : null}
                          </div>
                        ))}
                        {group.comparability_note_original ? (
                          <p className={styles.comparabilityNote}>{group.comparability_note_original}</p>
                        ) : null}
                        <footer>
                          <span>指標No.{group.series.map((series) => series.series_number).join("・")}</span>
                          <a href={`${implementationPlanUrl}#page=${group.source_page}`} target="_blank" rel="noreferrer">
                            PDF {group.source_page}ページ ↗
                          </a>
                        </footer>
                      </article>
                    );
                  })}
                </div>
              </details>
            ))}
          </div>
        </section>

        <section className={styles.boundary}>
          <div>
            <p className="eyebrow">Still unknown</p>
            <h2>ここから先は、まだ評価しない。</h2>
          </div>
          <ul>
            <li><strong>対応要確認 15系列</strong><span>定義・対象範囲・名称変更の追加照合</span></li>
            <li><strong>取組16〜18の年度実績</strong><span>確定評価資料との接続</span></li>
            <li><strong>予算・事業・契約</strong><span>指標変化へ寄与した実行内容との接続</span></li>
            <li><strong>政策効果</strong><span>外部要因を含む因果関係の検討</span></li>
          </ul>
        </section>

        <nav className={styles.bottomNav} aria-label="関連ページ">
          <Link href="/municipalities/hokkaido">北海道の108指標</Link>
          <Link href="/policies">政策と成果</Link>
          <Link href="/data-quality">データ品質</Link>
          <Link href="/methodology">読み方・評価方法</Link>
        </nav>
      </div>
      <SiteFooter />
    </main>
  );
}
