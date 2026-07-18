import type { Metadata } from "next";
import Link from "next/link";

import { PageIntro } from "@/components/PageIntro";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { StatusBadge } from "@/components/StatusBadge";
import {
  miyagiKpiScopes,
  miyagiPolicyReviewStats,
  reviewedMiyagiPolicyDirections,
  reviewedMiyagiPolicyHierarchy,
  type MiyagiKpiValue,
} from "@/lib/miyagiPolicies";

import styles from "./page.module.css";

export const metadata: Metadata = {
  title: `宮城県｜政策目標${miyagiPolicyReviewStats.reviewedTargetGroups}件`,
  description:
    `新・宮城の将来ビジョン中期実施計画の政策体系と、Reviewed済み目標グループ1〜${miyagiPolicyReviewStats.reviewedTargetGroups}を、初期値・現況値・中期末目標・後期末目標・根拠資料とともに確認できます。`,
};

const implementationPlanUrl =
  "https://www.pref.miyagi.jp/documents/22609/jisshikeikaku2r8.pdf";

const roleLabels: Record<MiyagiKpiValue["role"], string> = {
  initial: "初期値",
  current: "現況値",
  midterm_target: "中期末目標",
  late_target: "後期末目標",
};

function valueLabel(value: MiyagiKpiValue, unit: string) {
  if (value.status === "not_set") return "未設定";
  if (value.status === "not_available") return "未公表";
  const displayUnit = unit === "単位記載なし" ? "" : unit;
  return `${value.value_text_original}${displayUnit}`;
}

export default function MiyagiPage() {
  const reviewRate =
    (miyagiPolicyReviewStats.reviewedTargetGroups /
      miyagiPolicyReviewStats.targetGroups) *
    100;

  return (
    <main>
      <SiteHeader />
      <div className="pageShell">
        <PageIntro
          eyebrow="Miyagi policy targets"
          title="宮城県の政策目標を、原文・期間・未設定までそのまま読む。"
        >
          <p>
            新・宮城の将来ビジョンの4基本方向・8政策・18取組をReviewed化し、
            現行中期実施計画にある128目標グループのうち、柱1と取組1〜5の
            {miyagiPolicyReviewStats.reviewedTargetGroups}件を公開しています。
            これは成果の達成率ではなく、一次資料を人が照合した作業カバレッジです。
          </p>
          <div className={styles.introLinks}>
            <Link href="/municipalities">全国47都道府県へ戻る</Link>
            <a href={implementationPlanUrl} target="_blank" rel="noreferrer">
              公式中期実施計画を開く ↗
            </a>
          </div>
        </PageIntro>

        <section className={styles.summaryGrid} aria-label="宮城県政策目標の公開状況">
          <article className={styles.summaryCard}>
            <span>Reviewed目標グループ</span>
            <strong>{miyagiPolicyReviewStats.reviewedTargetGroups}</strong>
            <p>
              公式の目標値No.1〜{miyagiPolicyReviewStats.reviewedTargetGroups}を本文・数値・単位・期間まで照合済み。
            </p>
          </article>
          <article className={styles.summaryCard}>
            <span>全目標グループ</span>
            <strong>{miyagiPolicyReviewStats.targetGroups}</strong>
            <p>149個別系列とは別概念。複数系列を独立KPIへ水増ししません。</p>
          </article>
          <article className={styles.summaryCard}>
            <span>KPI Evidence Packet</span>
            <strong>{miyagiPolicyReviewStats.kpiEvidencePackets}</strong>
            <p>各目標に名称・値・掲載ページの根拠を1件ずつ保存。</p>
          </article>
          <article className={styles.summaryCard}>
            <span>年度実績へ接続済み</span>
            <strong>0</strong>
            <p>評価書との接続前に、達成率や政策評価を生成しません。</p>
          </article>
        </section>

        <section className={styles.progressSection} aria-labelledby="miyagi-review-progress">
          <div>
            <p className="eyebrow">Review coverage</p>
            <h2 id="miyagi-review-progress">
              {miyagiPolicyReviewStats.reviewedTargetGroups} / {miyagiPolicyReviewStats.targetGroups}
              をReviewed。次は目標39〜52。
            </h2>
          </div>
          <div className={styles.progressDetail}>
            <div className={styles.progressTrack} aria-hidden="true">
              <span style={{ width: `${reviewRate}%` }} />
            </div>
            <dl>
              <div>
                <dt>Reviewed</dt>
                <dd>{miyagiPolicyReviewStats.reviewedTargetGroups}目標</dd>
              </div>
              <div>
                <dt>残り</dt>
                <dd>{miyagiPolicyReviewStats.remainingTargetGroups}目標</dd>
              </div>
              <div>
                <dt>今回の範囲</dt>
                <dd>柱1・取組1〜5</dd>
              </div>
            </dl>
            <p>
              後期末目標が「－」の{miyagiPolicyReviewStats.lateTargetsNotSet}系列は、
              0ではなく未設定として保持しています。累計指標
              {miyagiPolicyReviewStats.cumulativeGroups}件は単年度値へ変換していません。
            </p>
          </div>
        </section>

        <section className="contentSection">
          <p className="eyebrow">Policy hierarchy</p>
          <h2>{reviewedMiyagiPolicyHierarchy.plan_title_original}</h2>
          <p className={styles.sectionLead}>
            {reviewedMiyagiPolicyHierarchy.plan_period_original}。
            政策体系は4基本方向・8政策・18取組を公式掲載順で保持し、
            復興完了に向けた4分野は通常の政策体系へ混入させていません。
          </p>

          <div className={styles.directionGrid}>
            {reviewedMiyagiPolicyDirections.map((direction) => (
              <article className={styles.directionCard} key={direction.id}>
                <div className={styles.directionHeader}>
                  <span>{String(direction.display_order).padStart(2, "0")}</span>
                  <StatusBadge
                    label={direction.display_order === 1 ? "KPI一部公開" : "体系Reviewed"}
                    tone="progress"
                  />
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
          <p className="eyebrow">Reviewed targets</p>
          <h2>
            目標1〜{miyagiPolicyReviewStats.reviewedTargetGroups}を、政策上の所属と4つの時点から確認する。
          </h2>
          <p className={styles.sectionLead}>
            初期値、現況値、令和9年度の中期末目標、令和12年度の後期末目標を原文どおり表示します。
            増減だけを見て良否を判定せず、実績年度・単位・累計範囲を保ちます。
          </p>

          <div className={styles.scopeStack}>
            {miyagiKpiScopes.map((scope) => (
              <section className={styles.scopeSection} key={scope.id}>
                <div className={styles.scopeHeader}>
                  <div>
                    <span>{scope.label}</span>
                    <h3>{scope.title}</h3>
                  </div>
                  <strong>{scope.groups.length}目標</strong>
                </div>

                <div className={styles.indicatorGrid}>
                  {scope.groups.map((group) => (
                    <article className={styles.indicatorCard} key={group.id}>
                      <div className={styles.indicatorTop}>
                        <span>目標値No.{group.target_group_number}</span>
                        <StatusBadge
                          label={
                            group.target_setting_status === "set"
                              ? "後期目標あり"
                              : "後期目標未設定"
                          }
                          tone={
                            group.target_setting_status === "set"
                              ? "verified"
                              : "neutral"
                          }
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
                                <small>{value.period_original}（{value.period_year}年度）</small>
                              </div>
                            ))}
                          </dl>
                          {series.unit_original === "単位記載なし" ? (
                            <p className={styles.dataNote}>公式表に単位の記載がありません。</p>
                          ) : null}
                          {series.aggregation_scope === "cumulative_to_date" ? (
                            <p className={styles.dataNote}>累計値。単年度値ではありません。</p>
                          ) : null}
                        </div>
                      ))}

                      {group.comparability_note_original ? (
                        <p className={styles.comparabilityNote}>
                          {group.comparability_note_original}
                        </p>
                      ) : null}

                      <footer>
                        <span>
                          指標No.{group.series.map((series) => series.series_number).join("・")}
                        </span>
                        <a
                          href={`${implementationPlanUrl}#page=${group.source_page}`}
                          target="_blank"
                          rel="noreferrer"
                        >
                          PDF {group.source_page}ページ ↗
                        </a>
                      </footer>
                    </article>
                  ))}
                </div>
              </section>
            ))}
          </div>
        </section>

        <section className={`contentSection ${styles.boundary}`}>
          <div>
            <p className="eyebrow">Not assessed yet</p>
            <h2>目標値の確認と、政策成果の評価を分ける。</h2>
          </div>
          <ul>
            <li>年度別実績と評価書の対象年度</li>
            <li>評価原案と確定評価の版差分</li>
            <li>指標定義・基準年・集計範囲の変更履歴</li>
            <li>関連する重点事業・予算・決算・契約</li>
            <li>指標変化と政策効果の因果関係</li>
          </ul>
        </section>

        <nav className={styles.bottomNav} aria-label="関連ページ">
          <Link href="/municipalities/hokkaido">北海道の108指標</Link>
          <Link href="/data-quality">データ品質</Link>
          <Link href="/methodology">評価方法</Link>
          <Link href="/municipalities">全国自治体一覧</Link>
        </nav>
      </div>
      <SiteFooter />
    </main>
  );
}
