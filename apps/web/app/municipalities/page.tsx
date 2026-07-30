import type { Metadata } from "next";
import Link from "next/link";

import { CoverageExplorer } from "@/components/CoverageExplorer";
import { PageIntro } from "@/components/PageIntro";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { StatusBadge } from "@/components/StatusBadge";
import {
  phase10StageSummary,
  reviewedCoverageStats,
} from "@/lib/reviewedCoverage";

import styles from "./page.module.css";

export const metadata: Metadata = {
  title: "47都道府県の政策目標を根拠から探す",
  description:
    "全国47都道府県、15,124件のReviewed目標・指標とEvidence Packetを検索し、実績・予算・事業・契約の接続状況を確認できます。",
};

const readingLevels = [
  {
    number: "01",
    label: "Reviewed",
    title: "目標原文を読む",
    text: "名称、値、単位、期間、条件を一次資料と照合したレコードです。",
  },
  {
    number: "02",
    label: "Evidence",
    title: "根拠へ戻る",
    text: "各レコードから公式資料、ページ、採否判断をたどれます。",
  },
  {
    number: "03",
    label: "Linked",
    title: "実績と条件を合わせる",
    text: "定義と対象期間が一致した系列だけを目標へ接続します。",
  },
  {
    number: "04",
    label: "Assessment",
    title: "評価可能性を判断する",
    text: "目標の掲載だけでは達成判定や自治体間ランキングを行いません。",
  },
];

const featuredPaths = [
  {
    code: "04",
    area: "宮城県",
    status: "年度実績を接続",
    tone: "verified" as const,
    title: `${reviewedCoverageStats.annualResultRows}行の年度実績まで読む。`,
    text: `${reviewedCoverageStats.linkedAnnualSeries}系列を直接接続し、${reviewedCoverageStats.reviewNeededAnnualSeries}系列は定義差などの要確認として分離しています。`,
    facts: ["128目標", "149系列", "2021–2024年度"],
    href: "/municipalities/miyagi#results",
    action: "宮城県の実績を見る",
  },
  {
    code: "40",
    area: "福岡県",
    status: "財政値をReviewed",
    tone: "progress" as const,
    title: "政策目標と予算・決算を分けて読む。",
    text: "118件の数値目標とReviewed財政値を公開。年度実績との接続前に、同じ成果だとは扱いません。",
    facts: ["118目標", "30取組", "予算・決算"],
    href: "/municipalities/fukuoka-prefecture",
    action: "福岡県の政策と財政を見る",
  },
  {
    code: "ALL",
    area: "全国",
    status: "Phase 9 完了",
    tone: "verified" as const,
    title: "38県・13,755件の目標原文。",
    text: `${reviewedCoverageStats.phase9SourceDocuments}公式文書から抽出し、全件にEvidence Packetを付与。抽出エラー${reviewedCoverageStats.phase9ExtractionErrors}件も欠損として残しています。`,
    facts: ["38県", "13,755レコード", "Evidence 100%"],
    href: "/municipalities/phase9",
    action: "全国レビューの検証情報を見る",
  },
];

function formatNumber(value: number) {
  return new Intl.NumberFormat("ja-JP").format(value);
}

export default function MunicipalitiesPage() {
  return (
    <main id="main-content">
      <SiteHeader />
      <div className="pageShell">
        <PageIntro
          eyebrow="47 prefectures / reviewed evidence"
          title="47都道府県の目標原文を、Evidenceから探す。"
        >
          <p>
            現行政策計画の入口だけでなく、全47都道府県の目標・指標を人が照合して公開しました。
            件数の大小を順位にせず、各レコードの公式根拠と、その先の実績・予算・事業・契約の接続状況を示します。
          </p>
        </PageIntro>

        <section className={styles.overview} aria-label="全国Reviewedデータ概要">
          <div className={styles.overviewLead}>
            <span>PHASE 9 COMPLETE</span>
            <strong>全国Reviewed公開</strong>
            <StatusBadge label="47 / 47" tone="verified" />
          </div>
          <dl>
            <div>
              <dt>Reviewed都道府県</dt>
              <dd>{reviewedCoverageStats.reviewedPrefectures}<small>/47</small></dd>
            </div>
            <div>
              <dt>目標・指標レコード</dt>
              <dd>{formatNumber(reviewedCoverageStats.reviewedRecords)}<small>件</small></dd>
            </div>
            <div>
              <dt>Evidence Packet</dt>
              <dd>{formatNumber(reviewedCoverageStats.evidencePackets)}<small>件</small></dd>
            </div>
            <div>
              <dt>年度実績</dt>
              <dd>{formatNumber(reviewedCoverageStats.annualResultRows)}<small>行</small></dd>
            </div>
            <div>
              <dt>政策達成評価</dt>
              <dd>{reviewedCoverageStats.policyAssessments}<small>件</small></dd>
            </div>
          </dl>
        </section>
        <p className={styles.countNote}>
          ※「目標・指標」は各計画の公式な記載単位を保持しており、目標原文・指標行・目標カードなど粒度が異なります。自治体間の件数比較には使いません。
        </p>

        <section className="contentSection">
          <div className={styles.sectionHeading}>
            <div>
              <p className="eyebrow">Choose the evidence depth</p>
              <h2>知りたい深さから読む。</h2>
            </div>
            <p>
              全国の目標原文、専用分析、実績接続、財政Reviewedを、同じ「公開済み」にまとめず分けています。
            </p>
          </div>
          <div className={styles.featuredGrid}>
            {featuredPaths.map((path) => (
              <article className={styles.featuredCard} key={path.code}>
                <div className={styles.featuredTop}>
                  <span>{path.code} / {path.area}</span>
                  <StatusBadge label={path.status} tone={path.tone} />
                </div>
                <h3>{path.title}</h3>
                <p>{path.text}</p>
                <ul>
                  {path.facts.map((fact) => <li key={fact}>{fact}</li>)}
                </ul>
                <Link href={path.href}>{path.action} →</Link>
              </article>
            ))}
          </div>
        </section>

        <section className={styles.levelSection}>
          <div>
            <p className="eyebrow">How to read</p>
            <h2>「目標がある」と「達成した」は違う。</h2>
            <p>
              目標、根拠、実績、評価可能性を順番に確認してください。
            </p>
          </div>
          <ol>
            {readingLevels.map((item) => (
              <li key={item.number}>
                <span>{item.number}</span>
                <small>{item.label}</small>
                <strong>{item.title}</strong>
                <p>{item.text}</p>
              </li>
            ))}
          </ol>
        </section>

        <section className="contentSection" id="prefectures">
          <div className={styles.sectionHeading}>
            <div>
              <p className="eyebrow">All 47 prefectures</p>
              <h2>47都道府県の統合索引。</h2>
            </div>
            <p>
              都道府県名・地域・計画名で検索できます。各カードの5段階表示で、目標から契約までの接続状況を確認できます。
            </p>
          </div>
          <CoverageExplorer />
        </section>

        <section className="contentSection">
          <div className={styles.sectionHeading}>
            <div>
              <p className="eyebrow">Phase 10 / vertical linkage</p>
              <h2>47の目標から、実績とお金へ。</h2>
            </div>
            <p>
              Phase 10は進行中です。索引済みは「資料入口を固定した状態」、接続済みは「定義を照合して目標と結んだ状態」です。
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
        </section>

        <section className="callout callout--dark">
          <div>
            <p className="eyebrow">Phase 10 in progress</p>
            <h2>評価を急がず、Evidence Chainを縦につなぐ。</h2>
            <p>
              15,124件は政策達成評価ではありません。次は年度実績、予算、事業、契約を同じ政策IDへ照合し、住民が自分で判断できる根拠の連鎖を広げます。
            </p>
          </div>
          <div className={styles.calloutActions}>
            <Link className="primaryAction" href="/municipalities/phase10">
              Phase 10の進捗
            </Link>
            <Link href="/data-quality">品質と限界を見る →</Link>
          </div>
        </section>
      </div>
      <SiteFooter />
    </main>
  );
}
