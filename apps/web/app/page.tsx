import Link from "next/link";

import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { StatusBadge } from "@/components/StatusBadge";
import {
  phase10StageSummary,
  reviewedCoverageStats,
} from "@/lib/reviewedCoverage";

import styles from "./page.module.css";

const evidenceChain = [
  {
    number: "01",
    key: "Promise",
    title: "何を目指すか",
    text: "計画、公約、数値目標を原文と期間から読む。",
  },
  {
    number: "02",
    key: "Money",
    title: "いくら使うか",
    text: "予算、補正、執行、決算を同じ金額として混ぜない。",
  },
  {
    number: "03",
    key: "Action",
    title: "何をしたか",
    text: "事業、契約、支出先、実施内容を目標へつなぐ。",
  },
  {
    number: "04",
    key: "Result",
    title: "何が変わったか",
    text: "年度実績とKPIを比較可能な条件で確かめる。",
  },
  {
    number: "05",
    key: "Accountability",
    title: "どう説明したか",
    text: "首長、議会、監査、訂正履歴から説明責任を見る。",
  },
];

const depthCards = [
  {
    className: styles.nationwideCard,
    area: "全国47都道府県",
    label: "目標原文から探す",
    title: `${formatNumber(reviewedCoverageStats.reviewedRecords)}件をEvidence付きで公開`,
    text: "47都道府県すべてで目標・指標の原文をReviewed。計画ごとの粒度を保ち、件数ランキングには使いません。",
    facts: ["47/47 Reviewed", "Evidence 100%", "公開ページ47"],
    href: "/municipalities#prefectures",
    action: "全国の目標を探す",
  },
  {
    className: styles.miyagiCard,
    area: "宮城県",
    label: "年度実績まで読む",
    title: `${reviewedCoverageStats.annualResultRows}件の実績推移を公開`,
    text: `${reviewedCoverageStats.linkedAnnualSeries}系列を直接接続し、${reviewedCoverageStats.reviewNeededAnnualSeries}系列は定義差などの要確認として分けています。`,
    facts: ["128目標", "149系列", "2021–2024年度"],
    href: "/municipalities/miyagi#results",
    action: "実績を確かめる",
  },
  {
    className: styles.fukuokaCard,
    area: "福岡県",
    label: "政策と財政を読む",
    title: "118件の数値目標と、予算・決算。",
    text: "政策目標とReviewed財政値を別レイヤーで公開。実績が未接続の目標に、達成率は付けません。",
    facts: ["4基本方向", "30取組", "財政値Reviewed"],
    href: "/municipalities/fukuoka-prefecture",
    action: "福岡県を見る",
  },
  {
    className: styles.qualityCard,
    area: "Phase 10",
    label: "完了範囲を読む",
    title: "47都道府県で、文書スコープ接続完了。",
    text: "年度実績、予算・決算、重点事業、監査は全国で文書単位まで接続。個別目標・事業の一対一接続は次の深掘り工程です。",
    facts: ["47/47 同一粒度", "文書スコープ完了", "政策評価0件"],
    href: "/municipalities/phase10",
    action: "Phase 10の完了境界を見る",
  },
];

function formatNumber(value: number) {
  return new Intl.NumberFormat("ja-JP").format(value);
}

export default function Home() {
  return (
    <main id="main-content">
      <SiteHeader />

      <section className={styles.hero}>
        <div className={styles.heroCopy}>
          <p className={styles.heroKicker}>
            PUBLIC EVIDENCE FOR LOCAL GOVERNMENT
          </p>
          <h1>
            自治体を、
            <br />
            <em>根拠から読む。</em>
          </h1>
          <p className={styles.heroLead}>
            計画、予算、事業、成果、議会。ばらばらに公開された一次資料を、
            住民が自分で判断できる順序へつなぎ直します。
          </p>
          <div className={styles.heroActions}>
            <Link className="primaryAction" href="/municipalities">
              47都道府県から探す
            </Link>
            <Link className="secondaryAction" href="/about">
              このサイトの目的
            </Link>
          </div>
          <div className={styles.heroPrinciples} aria-label="表示原則">
            <span>一次資料を表示</span>
            <span>未確認を明記</span>
            <span>単純ランキングなし</span>
          </div>
        </div>

        <aside
          className={styles.currentFocus}
          aria-labelledby="current-focus-title"
        >
          <div className={styles.focusHeader}>
            <span>NATIONWIDE REVIEW</span>
            <StatusBadge label="47 / 47 公開" tone="verified" />
          </div>
          <p className={styles.focusArea}>ALL PREFECTURES / EVIDENCE 100%</p>
          <h2 id="current-focus-title">
            {formatNumber(reviewedCoverageStats.reviewedRecords)}件の目標・指標を、
            根拠付きで。
          </h2>
          <dl className={styles.focusMetrics}>
            <div>
              <dt>Reviewed</dt>
              <dd>{reviewedCoverageStats.reviewedPrefectures}<small>県</small></dd>
            </div>
            <div>
              <dt>Evidence</dt>
              <dd>{formatNumber(reviewedCoverageStats.evidencePackets)}<small>件</small></dd>
            </div>
            <div>
              <dt>根拠付与率</dt>
              <dd>{reviewedCoverageStats.evidenceCoveragePercent}<small>%</small></dd>
            </div>
          </dl>
          <p className={styles.focusNote}>
            計画ごとの記載単位を保持しているため、件数は自治体間の優劣を示しません。
            目標の掲載と、達成評価も分けています。
          </p>
          <Link href="/municipalities#prefectures">
            47都道府県の統合索引へ <span aria-hidden="true">→</span>
          </Link>
        </aside>
      </section>

      <section className={styles.snapshot} aria-label="現在のデータ公開状況">
        <div className={styles.snapshotLead}>
          <p>JICHI INSIGHT NOW</p>
          <strong>現在地を、数字で。</strong>
          <span>更新 {reviewedCoverageStats.updatedAt}</span>
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
            <dd>{reviewedCoverageStats.annualResultRows}<small>行</small></dd>
          </div>
          <div>
            <dt>政策達成評価</dt>
            <dd>{reviewedCoverageStats.policyAssessments}<small>件</small></dd>
          </div>
        </dl>
      </section>

      <section className={styles.section}>
        <div className={styles.sectionHeading}>
          <div>
            <p className="eyebrow">Start with a question</p>
            <h2>知りたい深さから、入口を選ぶ。</h2>
          </div>
          <p>
            掲載件数の多さではなく、何をどこまで確認できるかで選べます。
          </p>
        </div>
        <div className={styles.depthGrid}>
          {depthCards.map((card) => (
            <article
              className={`${styles.depthCard} ${card.className}`}
              key={card.area}
            >
              <div className={styles.depthTop}>
                <span>{card.area}</span>
                <small>{card.label}</small>
              </div>
              <h3>{card.title}</h3>
              <p>{card.text}</p>
              <ul>
                {card.facts.map((fact) => <li key={fact}>{fact}</li>)}
              </ul>
              <Link href={card.href}>
                {card.action} <span aria-hidden="true">→</span>
              </Link>
            </article>
          ))}
        </div>
      </section>

      <section className={`${styles.section} ${styles.chainSection}`}>
        <div className={styles.sectionHeading}>
          <div>
            <p className="eyebrow">One chain, five questions</p>
            <h2>資料ではなく、判断の順番でつなぐ。</h2>
          </div>
          <p>
            目標だけ、金額だけ、結果だけを切り取らず、前後の根拠をたどれる状態を目指します。
          </p>
        </div>
        <ol className={styles.chain}>
          {evidenceChain.map((item) => (
            <li key={item.key}>
              <span>{item.number}</span>
              <small>{item.key}</small>
              <h3>{item.title}</h3>
              <p>{item.text}</p>
            </li>
          ))}
        </ol>
      </section>

      <section className={styles.section}>
        <div className={styles.readinessLayout}>
          <div>
            <p className="eyebrow">Post-Phase 10 / record-level deepening</p>
            <h2>
              全国の文書基盤は完了。
              <br />
              次は、個票の一対一接続。
            </h2>
            <p className={styles.readinessLead}>
              年度実績、予算・決算、重点事業、監査は47都道府県で文書スコープまで接続済みです。
              次は、個別の目標、予算科目、事業、契約、議会発言、監査指摘を、定義・期間・主体を照合しながら一対一で深めます。
            </p>
            <Link className="secondaryAction" href="/municipalities/phase10">
              Phase 10の完了境界を見る
            </Link>
          </div>
          <div className={styles.readinessBars}>
            {phase10StageSummary.map((stage) => (
              <div key={stage.key}>
                <div>
                  <span>
                    {stage.label}
                    <small>
                      {stage.key === "project_evaluation"
                        ? "47都道府県で文書スコープ接続"
                        : stage.key === "contracts"
                          ? "47都道府県でReviewed coverage"
                          : stage.note}
                    </small>
                  </span>
                  <strong>{stage.count}<small>/47</small></strong>
                </div>
                <div
                  className={styles.bar}
                  aria-label={`${stage.label} ${stage.count}/47`}
                >
                  <span style={{ width: `${(stage.count / 47) * 100}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className={styles.trustSection}>
        <div>
          <p className="eyebrow">Facts before scores</p>
          <h2>
            評価より先に、
            <br />
            評価できる状態かを示す。
          </h2>
        </div>
        <div>
          <p>
            Jichi Insightの目的は、自治体や人物に早く点数を付けることではありません。
            事実、比較、解釈、評価を分け、足りない根拠は足りないまま表示します。
          </p>
          <ul>
            <li><strong>Reviewed</strong><span>一次資料と人が照合</span></li>
            <li><strong>要確認</strong><span>定義差・系列差などを保留</span></li>
            <li><strong>未接続</strong><span>実績・予算・事業との対応なし</span></li>
            <li><strong>評価不能</strong><span>根拠不足を点数で埋めない</span></li>
          </ul>
          <div className={styles.trustActions}>
            <Link className="invertedAction" href="/methodology">
              読み方・評価方法
            </Link>
            <Link href="/data-quality">全データ品質を見る →</Link>
          </div>
        </div>
      </section>

      <SiteFooter />
    </main>
  );
}
