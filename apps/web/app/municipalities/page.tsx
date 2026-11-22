import type { Metadata } from "next";
import Link from "next/link";

import { CoverageExplorer } from "@/components/CoverageExplorer";
import { PageIntro } from "@/components/PageIntro";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { StatusBadge } from "@/components/StatusBadge";
import { loadPhase15CitySummaries } from "@/lib/phase15Cities";
import {
  phase10StageSummary,
  reviewedCoverageStats,
} from "@/lib/reviewedCoverage";

import styles from "./page.module.css";

export const metadata: Metadata = {
  title: "47都道府県の政策目標を根拠から探す",
  description:
    `全国47都道府県、${reviewedCoverageStats.reviewedRecords.toLocaleString("ja-JP")}件の確認済み目標・指標を検索し、実績・予算・事業の接続状況を確認できます。`,
  alternates: {
    canonical: "https://jimieru.com/municipalities/",
  },
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
  { code: "33", area: "岡山県・岡山市", status: "段階1〜4 Reviewed", tone: "verified" as const, title: "晴れの国の政策・予算・議会を確認。", text: "第4次晴れの国おかやま生き活きプランと岡山市第七次総合計画、財政・議会の公開記録を確認できます。", facts: ["岡山県", "岡山市", "決算・政策・議会"], href: "/municipalities/okayama-prefecture", action: "岡山クラスターの詳細を見る" },
  { code: "15", area: "新潟県・新潟市", status: "段階1〜4 Reviewed", tone: "verified" as const, title: "新潟県総合計画と市の重点戦略を読む。", text: "新潟県の総合計画・財政・成果指標と、新潟市総合計画2030の重点戦略、議会記録を確認できます。", facts: ["新潟県", "新潟市", "決算・政策・議会"], href: "/municipalities/niigata-prefecture", action: "新潟クラスターの詳細を見る" },
  {
    code: "26",
    area: "京都府・京都市",
    status: "段階1〜4 Reviewed",
    tone: "verified" as const,
    title: "京都府総合計画から予算・政策評価・議会へ。",
    text: "府の骨格予算と分野別基本施策、京都市の新京都戦略と旧京プラン2025の政策評価を区別し、首長公約・議会資料まで確認できます。",
    facts: ["京都府", "京都市", "決算・公約・議会"],
    href: "/municipalities/kyoto-prefecture",
    action: "京都クラスターの詳細を見る",
  },
  {
    code: "34",
    area: "広島県・広島市",
    status: "段階1〜4 Reviewed",
    tone: "verified" as const,
    title: "ひろしまビジョンから予算・成果・公約・議会へ。",
    text: "広島県の2026年度一般会計当初予算と普通会計決算、重点事業、知事公約、県議会記録を同じ入口から確認。広島市の専用ページにも接続します。",
    facts: ["広島県", "広島市", "予算・公約・議会"],
    href: "/municipalities/hiroshima-prefecture",
    action: "広島クラスターの詳細を見る",
  },
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

const phase15Cities = loadPhase15CitySummaries();

export default function MunicipalitiesPage() {
  return (
    <>
      <SiteHeader />
      <main id="main-content">
      <div className="pageShell">
        <PageIntro
          eyebrow="FIND YOUR MUNICIPALITY"
          title="あなたのまちの情報を探す。"
        >
          <p>
            現行政策計画の入口だけでなく、全47都道府県の目標・指標を人が照合して公開しました。
            件数の大小を順位にせず、各レコードの公式根拠と、その先の実績・予算・事業・契約の接続状況を示します。
          </p>
          <p>確認できること：詳細レビュー済み69市の基本情報と予算・決算、47都道府県の政策目標・指標。まだ確認できないこと：市債残高・財政健全性の指標は全69市に同条件では揃っていません。財政の詳細・重点事業・公約・議会の深掘りは広島県・広島市、京都府・京都市、新潟県・新潟市、岡山県・岡山市を含む複数の地域クラスターで公開しています。掲載の粒度は自治体ごとに異なります。</p>
        </PageIntro>

        <nav className={styles.topShortcuts} aria-label="自治体一覧のページ内案内">
          <a href="#prefectures">47都道府県を検索</a>
          <a href="#reviewed-cities">詳細レビュー済みの市</a>
          <Link href="/review-progress">その他の市の収録進捗</Link>
        </nav>
        <p className={styles.searchBoundary}>
          掲載対象は、47都道府県の政策計画と、詳細レビュー完了済みの市です。すべての市区町村が同じ深さで閲覧できるわけではありません。
        </p>
        <section className={styles.searchSection} id="prefectures">
          <div className={styles.sectionHeading}>
            <div>
              <p className="eyebrow">All 47 prefectures</p>
              <h2>都道府県名・地域から探す。</h2>
            </div>
            <p>
              都道府県名、地方、計画名で絞り込めます。検索結果から公式計画と確認済みの情報へ進めます。
            </p>
          </div>
          <CoverageExplorer />
        </section>


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

        <section className="contentSection" id="reviewed-cities">
          <div className={styles.sectionHeading}>
            <div>
              <p className="eyebrow">Phase 15 / core cities &amp; capitals</p>
              <h2>詳細レビュー済みの市を読む。</h2>
            </div>
            <p>
              中核市・県庁所在地のうち、一次資料レビューが完了した{phase15Cities.length}市について、
              計画の枠組みと予算・決算を市ページで公開しています。接続できない範囲は判定不能のまま明示します。
            </p>
          </div>
          <p><Link href="/municipalities/okayama-city">岡山市の政策・財政・市長公約・議会の詳細を見る</Link></p>
          <p><Link href="/municipalities/niigata-city">新潟市の政策・財政・市長公約・議会の詳細を見る</Link></p>
          <p><Link href="/municipalities/kyoto-city">京都市の政策・財政・市長公約・議会の詳細を見る</Link></p>
          <p><Link href="/municipalities/hiroshima-city">広島市の政策・財政・市長公約・議会の詳細を見る</Link></p>
          <ul className={styles.cityGrid}>
            {phase15Cities.map((city) => (
              <li key={city.slug} className={styles.cityCard}>
                <small>{city.prefecture} / {city.officialCode}</small>
                <strong>{city.name}</strong>
                <span>レビュー完了日 {city.completedAt}</span>
                <Link href={`/municipalities/${city.slug}`}>{city.name}のページを見る →</Link>
              </li>
            ))}
          </ul>
          <p className={styles.countNote}>
            ※ 市の一覧はレビューの進捗を示すもので、自治体の政策成果や優劣のランキングではありません。
            残りの自治体の状況は<Link href="/review-progress">レビュー進捗</Link>で公開しています。
          </p>
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

        <section className="contentSection">
          <div className={styles.sectionHeading}>
            <div>
              <p className="eyebrow">Phase 10 / vertical linkage</p>
              <h2>47の目標から、実績とお金へ。</h2>
            </div>
            <p>
              Phase 10の文書スコープ接続は47都道府県で完了しています。索引済みは「資料入口を固定した状態」、接続済みは「定義を照合して目標と結んだ状態」です。
            </p>
          </div>
          <div className={styles.stageGrid}>
            {phase10StageSummary.map((stage, index) => (
              <article key={stage.key}>
                <span>0{index + 1}</span>
                <small>{stage.label}</small>
                <strong>{stage.count}<em>/47</em></strong>
                <div role="img" aria-label={`${stage.label} ${stage.count}/47`}>
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
              {formatNumber(reviewedCoverageStats.reviewedRecords)}件は政策達成評価ではありません。次は年度実績、予算、事業、契約を同じ政策IDへ照合し、住民が自分で判断できる根拠の連鎖を広げます。
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
      </main>
      <SiteFooter />
    </>
  );
}
