import type { Metadata } from "next";
import Link from "next/link";

import { PageIntro } from "@/components/PageIntro";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import {
  phase10StageSummary,
  reviewedCoverageStats,
} from "@/lib/reviewedCoverage";

import styles from "./page.module.css";

export const metadata: Metadata = {
  title: "データ品質と公開範囲",
  description:
    "全国47都道府県、15,124件のReviewed目標・指標のEvidence coverage、接続状況、欠損、評価可能性を公開します。",
};

const qualityLevels = [
  ["Coverage", "対象と資料の存在を把握", "収録候補。事実表示には未使用"],
  ["Indexed", "公式URL、年度、資料位置を特定", "一次資料へ戻るための索引"],
  ["Current", "後継計画、改定、有効期間を確認", "現行資料として扱える状態"],
  ["Extracted", "原文や候補値を機械抽出", "人手照合前。原則として非公開"],
  ["Reviewed", "本文、値、単位、期間を人が照合", "事実表示に利用"],
  ["Linked", "別資料との定義と期間を照合して接続", "目標と実績などを並べて確認"],
  ["Published", "公開基準、画面、リンクを検証", "本番サイトで閲覧可能"],
];

const boundaries = [
  {
    label: "粒度",
    title: "件数を自治体間で比べない",
    text: "目標原文、指標行、目標カードなど、計画が採用する公式な記載単位を保持しています。",
  },
  {
    label: "欠損",
    title: "抽出エラーを0にしない",
    text: `Phase 9の抽出エラー${reviewedCoverageStats.phase9ExtractionErrors}件は、推測で補完せず欠損と原資料への導線を残しています。`,
  },
  {
    label: "接続",
    title: "定義差を保留する",
    text: `宮城県では${reviewedCoverageStats.linkedAnnualSeries}系列を直接接続し、${reviewedCoverageStats.reviewNeededAnnualSeries}系列を要確認として分離しています。`,
  },
  {
    label: "評価",
    title: "目標の掲載を達成と呼ばない",
    text: "実績、予算、事業、説明責任の根拠が揃うまで、独自の政策達成率や自治体ランキングを出しません。",
  },
];

const knownLimits = [
  `年度実績を目標へ直接接続できているのは${reviewedCoverageStats.annualLinkedPrefectures}都道府県です。`,
  `予算・決算を人がReviewedした政策接続候補は${reviewedCoverageStats.budgetReviewedPrefectures}都道府県です。`,
  `事業評価と契約の公式入口を索引できているのは各${reviewedCoverageStats.projectIndexedOrBetterPrefectures}都道府県です。`,
  "Reporting yearとmeasurement year、旧計画と現行計画、公式達成率と独自計算を混ぜません。",
  "資料が未索引であることを、資料が存在しないこととは扱いません。",
];

function formatNumber(value: number) {
  return new Intl.NumberFormat("ja-JP").format(value);
}

export default function DataQualityPage() {
  return (
    <main id="main-content">
      <SiteHeader />
      <div className="pageShell">
        <PageIntro
          eyebrow="Data quality / current scope"
          title="件数ではなく、確認の深さを公開する。"
        >
          <p>
            資料を見つけた状態、値を人が確認した状態、別資料と接続できた状態、評価に使える状態は異なります。
            Jichi Insightは、公開量と品質段階、欠損、未接続範囲を同時に示します。
          </p>
        </PageIntro>

        <section className={styles.snapshot} aria-label="全国データ品質概要">
          <div>
            <span>Reviewed都道府県</span>
            <strong>{reviewedCoverageStats.reviewedPrefectures}<small>/47</small></strong>
            <p>現行計画の目標・指標を全47都道府県で人手照合。</p>
          </div>
          <div>
            <span>目標・指標レコード</span>
            <strong>{formatNumber(reviewedCoverageStats.reviewedRecords)}<small>件</small></strong>
            <p>公式な記載単位を保持。自治体間の件数比較には不使用。</p>
          </div>
          <div>
            <span>Evidence coverage</span>
            <strong>{reviewedCoverageStats.evidenceCoveragePercent}<small>%</small></strong>
            <p>{formatNumber(reviewedCoverageStats.evidencePackets)}件すべてにEvidence Packet。</p>
          </div>
          <div>
            <span>年度実績</span>
            <strong>{reviewedCoverageStats.annualResultRows}<small>行</small></strong>
            <p>宮城県の2021〜2024年度。目標値と測定年を分離。</p>
          </div>
          <div>
            <span>政策達成評価</span>
            <strong>{reviewedCoverageStats.policyAssessments}<small>件</small></strong>
            <p>根拠不足を点数や達成率で埋めていません。</p>
          </div>
        </section>

        <section className="contentSection">
          <div className={styles.sectionHeading}>
            <div>
              <p className="eyebrow">Coverage composition</p>
              <h2>15,124件の内訳。</h2>
            </div>
            <p>
              9地域の専用データと、Phase 9で追加した38県の目標原文を合算しています。どちらもEvidence Packet必須です。
            </p>
          </div>
          <div className={styles.composition}>
            <article>
              <span>専用分析 / 9都道府県</span>
              <strong>{formatNumber(reviewedCoverageStats.anchorReviewedRecords)}</strong>
              <p>北海道、宮城、東京、愛知、大阪、広島、香川、福岡、沖縄。計画構造に合わせた専用画面。</p>
              <Link href="/municipalities#prefectures">
                全国索引で見る →
              </Link>
            </article>
            <article>
              <span>Phase 9 / 38都道府県</span>
              <strong>{formatNumber(reviewedCoverageStats.phase9ReviewedRecords)}</strong>
              <p>{reviewedCoverageStats.phase9SourceDocuments}公式文書から目標原文を抽出・照合。比較不能情報も保持。</p>
              <Link href="/municipalities/phase9">
                Phase 9の検証情報 →
              </Link>
            </article>
          </div>
        </section>

        <section className="contentSection">
          <div className={styles.sectionHeading}>
            <div>
              <p className="eyebrow">Vertical linkage</p>
              <h2>目標から契約までの現在地。</h2>
            </div>
            <p>
              Phase 10は進行中です。47県の目標Reviewed完了と、縦接続の完成は別の進捗として扱います。
            </p>
          </div>
          <div className={styles.stageGrid}>
            {phase10StageSummary.map((stage, index) => (
              <article key={stage.key}>
                <span>0{index + 1}</span>
                <small>{stage.label}</small>
                <strong>{stage.count}<em>/47</em></strong>
                <div aria-label={`${stage.label} ${stage.count}/47`}>
                  <span style={{ width: `${(stage.count / 47) * 100}%` }} />
                </div>
                <p>{stage.note}</p>
              </article>
            ))}
          </div>
          <div className={styles.inlineAction}>
            <Link className="secondaryAction" href="/municipalities/phase10">
              Phase 10の出典とゲートを確認
            </Link>
          </div>
        </section>

        <section className="contentSection">
          <div className={styles.sectionHeading}>
            <div>
              <p className="eyebrow">Quality boundaries</p>
              <h2>壊さない4つの境界。</h2>
            </div>
            <p>
              データ量が増えても、原文、欠損、比較条件、評価可能性を平らにしません。
            </p>
          </div>
          <div className={styles.boundaryGrid}>
            {boundaries.map((boundary) => (
              <article key={boundary.label}>
                <span>{boundary.label}</span>
                <h3>{boundary.title}</h3>
                <p>{boundary.text}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="contentSection">
          <p className="eyebrow">Quality ladder</p>
          <h2>公開までの7段階。</h2>
          <div className={styles.qualityTableWrap}>
            <table className={styles.qualityTable}>
              <thead>
                <tr>
                  <th>段階</th>
                  <th>意味</th>
                  <th>利用方法</th>
                </tr>
              </thead>
              <tbody>
                {qualityLevels.map(([level, meaning, use]) => (
                  <tr key={level}>
                    <td>{level}</td>
                    <td>{meaning}</td>
                    <td>{use}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className="contentSection">
          <p className="eyebrow">Known limitations</p>
          <h2>いま、まだ評価できない理由。</h2>
          <ul className={styles.gapList}>
            {knownLimits.map((limit) => <li key={limit}>{limit}</li>)}
          </ul>
        </section>

        <section className="callout callout--dark">
          <div>
            <p className="eyebrow">Why zero evaluations</p>
            <h2>データ不足を、点数で埋めません。</h2>
            <p>
              15,124件の目標・指標は、政策成果の評価件数ではありません。目標、実績、予算、事業、契約、説明責任が比較可能な条件でつながるまで、政策達成評価0件を維持します。
            </p>
          </div>
          <Link className="primaryAction" href="/methodology">
            読み方・評価方法
          </Link>
        </section>
      </div>
      <SiteFooter />
    </main>
  );
}
