import type { Metadata } from "next";
import Link from "next/link";

import { CoverageExplorer } from "@/components/CoverageExplorer";
import { PageIntro } from "@/components/PageIntro";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { StatusBadge } from "@/components/StatusBadge";
import { municipalityMeta, sourcesForMunicipality, type MunicipalityKey } from "@/lib/catalog";
import { hokkaidoIndicatorReviewStats } from "@/lib/hokkaidoIndicators";
import { miyagiKpiActualStats } from "@/lib/miyagiActuals";
import { miyagiPolicyReviewStats } from "@/lib/miyagiPolicies";
import {
  nationwideCoverageStats,
  nationwideSourceInventoryStats,
  sourceInventoryCategoryLabel,
  sourceInventoryCategoryOrder,
} from "@/lib/nationwideCoverage";
import { allPolicyTargetStats } from "@/lib/policyTargets";
import { waveOnePolicyReviewQueue } from "@/lib/policyReviewQueue";
import { tokyoPolicyTargetStats } from "@/lib/tokyoPolicyTargets";

import styles from "./page.module.css";

export const metadata: Metadata = {
  title: "全国47都道府県から探す",
  description:
    "全国47都道府県の現行政策計画と、実施計画・KPI・年度評価・予算・事業評価の資料カバレッジを確認できます。",
};

const cityKeys = (Object.keys(municipalityMeta) as MunicipalityKey[]).filter(
  (key) => municipalityMeta[key].type === "政令指定都市",
);

const readingLevels = [
  ["01", "入口", "現行の政策計画", "何を目指す自治体かを公式計画から確認。"],
  ["02", "構造", "政策・KPI", "目標の名称、値、単位、期間を人が照合。"],
  ["03", "推移", "年度実績", "同じ定義で比較できる年度値を目標へ接続。"],
  ["04", "判断", "評価・説明", "前提と限界を示したうえで、説明責任を確認。"],
];

const roadmapStatus = {
  reviewed_reference: { label: "深掘り公開", tone: "verified" as const },
  active_review: { label: "実績接続中", tone: "progress" as const },
  queued: { label: "資料深掘り待ち", tone: "neutral" as const },
};

export default function MunicipalitiesPage() {
  return (
    <main id="main-content">
      <SiteHeader />
      <div className="pageShell">
        <PageIntro eyebrow="Find a municipality" title="47都道府県を、資料の深さから探す。">
          <p>
            公式サイトと現行の政策計画は、全47都道府県で確認済みです。
            その先にあるKPI、年度評価、予算・決算、事業評価は、確認できた深さを個別に表示します。
          </p>
        </PageIntro>

        <section className={styles.overview} aria-label="全国カバレッジ概要">
          <div className={styles.overviewLead}>
            <span>PHASE 7 DATA GATE</span>
            <strong>全国の入口整備</strong>
            <StatusBadge label="完了" tone="verified" />
          </div>
          <dl>
            <div><dt>全国登録</dt><dd>{nationwideCoverageStats.totalPrefectures}<small>/47</small></dd></div>
            <div><dt>公式入口</dt><dd>{nationwideCoverageStats.verifiedOfficialEntries}<small>/47</small></dd></div>
            <div><dt>政策計画入口</dt><dd>{nationwideCoverageStats.indexedPolicyPlanEntries}<small>/47</small></dd></div>
            <div><dt>現行計画</dt><dd>{nationwideCoverageStats.currentPlanConfirmedPrefectures}<small>/47</small></dd></div>
            <div><dt>公開ページ</dt><dd>{nationwideCoverageStats.publishedPrefecturePages}<small>都道府県</small></dd></div>
          </dl>
        </section>

        <section className="contentSection">
          <div className={styles.sectionHeading}>
            <div>
              <p className="eyebrow">Deep dives</p>
              <h2>いま、深く読める4都道府県。</h2>
            </div>
            <p>自治体ごとに公開できる深さが違うため、同じ「公開済み」として扱いません。</p>
          </div>
          <div className={styles.deepDiveGrid}>
            <article className={`${styles.deepDiveCard} ${styles.miyagi}`}>
              <div><span>04 / 宮城県</span><StatusBadge label="年度実績あり" tone="verified" /></div>
              <h3>目標から、4年分の実績まで。</h3>
              <dl>
                <div><dt>Reviewed目標</dt><dd>{miyagiPolicyReviewStats.reviewedTargetGroups}</dd></div>
                <div><dt>直接接続</dt><dd>{miyagiKpiActualStats.linkedSeries}系列</dd></div>
                <div><dt>対応要確認</dt><dd>{miyagiKpiActualStats.reviewNeededSeries}系列</dd></div>
                <div><dt>年度実績</dt><dd>{miyagiKpiActualStats.annualResultRows}行</dd></div>
              </dl>
              <p>全{miyagiPolicyReviewStats.reviewedTargetGroups}目標を公開。旧評価書と現行計画の目標を混ぜず、定義差がある系列は要確認のまま表示します。</p>
              <Link href="/municipalities/miyagi">宮城県の実績を見る →</Link>
            </article>
            <article className={`${styles.deepDiveCard} ${styles.hokkaido}`}>
              <div><span>01 / 北海道</span><StatusBadge label="KPI全件Reviewed" tone="verified" /></div>
              <h3>108指標の目標設計を読む。</h3>
              <dl>
                <div><dt>政策分野</dt><dd>18</dd></div>
                <div><dt>Reviewed指標</dt><dd>{hokkaidoIndicatorReviewStats.reviewedIndicators}</dd></div>
                <div><dt>根拠記録</dt><dd>{hokkaidoIndicatorReviewStats.evidencePackets}</dd></div>
                <div><dt>年度実績</dt><dd>未接続</dd></div>
              </dl>
              <p>条件型、累計、未公表、比較注意など、単純な数値にできない情報も残します。</p>
              <Link href="/municipalities/hokkaido">北海道の指標を見る →</Link>
            </article>
            <article className={`${styles.deepDiveCard} ${styles.tokyo}`}>
              <div><span>13 / 東京都</span><StatusBadge label="目標カード全件Reviewed" tone="verified" /></div>
              <h3>60ページ・304目標カードを読む。</h3>
              <dl>
                <div><dt>政策分野</dt><dd>{tokyoPolicyTargetStats.policyAreas}</dd></div>
                <div><dt>Reviewed目標</dt><dd>{tokyoPolicyTargetStats.reviewedTargetGroups}</dd></div>
                <div><dt>Evidence</dt><dd>{tokyoPolicyTargetStats.evidencePackets}</dd></div>
                <div><dt>年度実績</dt><dd>未接続</dd></div>
              </dl>
              <p>25政策分野・304目標カードをEvidence付きで公開。子供分野以外のグラフ点列と年度実績は別工程です。</p>
              <Link href="/municipalities/tokyo">東京都の政策目標を見る →</Link>
            </article>
            <article className={`${styles.deepDiveCard} ${styles.fukuoka}`}>
              <div><span>40 / 福岡県</span><StatusBadge label="政策＋財政" tone="progress" /></div>
              <h3>政策目標と財政の入口を読む。</h3>
              <dl>
                <div><dt>基本方向</dt><dd>4</dd></div>
                <div><dt>取組事項</dt><dd>30</dd></div>
                <div><dt>数値目標</dt><dd>{allPolicyTargetStats.reviewedTargets}</dd></div>
                <div><dt>年度実績</dt><dd>未接続</dd></div>
              </dl>
              <p>県・福岡市・北九州市の財政資料と、福岡県の政策体系を別々の前提で確認できます。</p>
              <Link href="/municipalities/fukuoka-prefecture">福岡県を見る →</Link>
            </article>
          </div>
        </section>

        <section className={styles.levelSection}>
          <div>
            <p className="eyebrow">How to read</p>
            <h2>「見つけた」と「評価できる」は違う。</h2>
            <p>Jichi Insightでは、資料の存在から住民の判断までを4段階に分けています。</p>
          </div>
          <ol>
            {readingLevels.map(([number, label, title, text]) => (
              <li key={number}>
                <span>{number}</span><small>{label}</small><strong>{title}</strong><p>{text}</p>
              </li>
            ))}
          </ol>
        </section>

        <section className="contentSection" id="prefectures">
          <div className={styles.sectionHeading}>
            <div>
              <p className="eyebrow">All 47 prefectures</p>
              <h2>都道府県と、確認できる資料。</h2>
            </div>
            <p>政策計画が47/47でも、年度評価や予算・決算の索引はまだ少数です。各カードで6カテゴリを確認できます。</p>
          </div>
          <CoverageExplorer />
        </section>

        <section className="contentSection">
          <div className={styles.sectionHeading}>
            <div>
              <p className="eyebrow">Source depth</p>
              <h2>全国資料の現在地。</h2>
            </div>
            <p>「索引以上」は公式資料の入口を固定できた状態です。本文・数値の人手照合とは区別します。</p>
          </div>
          <div className={styles.sourceSummary}>
            {sourceInventoryCategoryOrder.map((category) => {
              const stats = nationwideSourceInventoryStats[category];
              const reviewedOrHigher =
                stats.reviewedOrHigher +
                (category === "kpi_source" && tokyoPolicyTargetStats.reviewedTargetGroups > 0 ? 1 : 0);
              return (
                <article key={category}>
                  <span>{sourceInventoryCategoryLabel(category)}</span>
                  <strong>{stats.indexedOrHigher}<small>/47</small></strong>
                  <div><span style={{ width: `${(stats.indexedOrHigher / 47) * 100}%` }} /></div>
                  <p>人手照合以上 {reviewedOrHigher}都道府県</p>
                </article>
              );
            })}
          </div>
        </section>

        <section className="contentSection">
          <p className="eyebrow">Designated-city pilots</p>
          <h2>政令指定都市のパイロット。</h2>
          <div className={styles.cityGrid}>
            {cityKeys.map((key) => {
              const municipality = municipalityMeta[key];
              return (
                <article className={styles.cityCard} key={key}>
                  <div><span>{municipality.type}</span><StatusBadge label={municipality.status} tone="verified" /></div>
                  <h3>{municipality.name}</h3>
                  <p>{municipality.summary}</p>
                  <dl>
                    <div><dt>公式資料入口</dt><dd>{sourcesForMunicipality(key).length}件</dd></div>
                    <div><dt>財政データ</dt><dd>{municipality.fiscalSummary}</dd></div>
                  </dl>
                  {municipality.href ? <Link href={municipality.href}>自治体ページを見る →</Link> : null}
                </article>
              );
            })}
          </div>
        </section>

        <section className="contentSection">
          <div className={styles.sectionHeading}>
            <div>
              <p className="eyebrow">Regional anchors</p>
              <h2>次に深くつなぐ、9つの地域拠点。</h2>
            </div>
            <p>順位付けではなく、地域バランスと資料構造に基づく整備順です。公開済み4地域と、次に資料を深掘りする5地域を示します。</p>
          </div>
          <div className={styles.roadmapGrid}>
            {waveOnePolicyReviewQueue.map((item) => {
              const status = roadmapStatus[item.status];
              const publicHref =
                item.prefecture_code === "01"
                  ? "/municipalities/hokkaido"
                  : item.prefecture_code === "04"
                    ? "/municipalities/miyagi"
                    : item.prefecture_code === "13"
                      ? "/municipalities/tokyo"
                      : item.prefecture_code === "40"
                        ? "/municipalities/fukuoka-prefecture"
                        : null;
              return (
                <article key={item.prefecture_code}>
                  <div>
                    <span>{item.prefecture_code}</span>
                    <StatusBadge label={status.label} tone={status.tone} />
                  </div>
                  <h3>{item.name}</h3>
                  <p>{item.next_action}</p>
                  {publicHref ? (
                    <Link href={publicHref}>詳細ページ →</Link>
                  ) : item.sources[0] ? (
                    <a href={item.sources[0].url} target="_blank" rel="noreferrer">公式計画 ↗</a>
                  ) : null}
                </article>
              );
            })}
          </div>
        </section>

        <section className="callout callout--dark">
          <div>
            <p className="eyebrow">Phase 8</p>
            <h2>全国の入口から、目標・実績・予算の接続へ。</h2>
            <p>次の重点は、各地域の拠点自治体でKPI、年度評価、予算・決算、事業評価を同じ品質基準でつなぐことです。</p>
          </div>
          <Link className="primaryAction" href="/data-quality">品質の内訳を見る</Link>
        </section>
      </div>
      <SiteFooter />
    </main>
  );
}
