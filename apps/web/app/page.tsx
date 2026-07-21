import Link from "next/link";

import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { StatusBadge } from "@/components/StatusBadge";
import { catalogStats } from "@/lib/catalog";
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

import styles from "./page.module.css";

const evidenceChain = [
  { number: "01", key: "Promise", title: "何を目指すか", text: "計画、公約、数値目標を原文と期間から読む。" },
  { number: "02", key: "Money", title: "いくら使うか", text: "予算、補正、執行、決算を同じ金額として混ぜない。" },
  { number: "03", key: "Action", title: "何をしたか", text: "事業、契約、支出先、実施内容を目標へつなぐ。" },
  { number: "04", key: "Result", title: "何が変わったか", text: "年度実績とKPIを比較可能な条件で確かめる。" },
  { number: "05", key: "Accountability", title: "どう説明したか", text: "首長、議会、監査、訂正履歴から説明責任を見る。" },
];

const depthCards = [
  {
    className: styles.miyagiCard,
    area: "宮城県",
    label: "年度実績まで読む",
    title: `${miyagiKpiActualStats.annualResultRows}件の実績推移を公開`,
    text: `${miyagiKpiActualStats.linkedSeries}系列を直接接続し、${miyagiKpiActualStats.reviewNeededSeries}系列は定義差などの要確認として分けています。`,
    facts: [`${miyagiPolicyReviewStats.reviewedTargetGroups}目標`, `${miyagiPolicyReviewStats.reviewedIndicatorSeries}系列`, "2021–2024年度"],
    href: "/municipalities/miyagi#results",
    action: "実績を確かめる",
  },
  {
    className: styles.hokkaidoCard,
    area: "北海道",
    label: "政策指標を読む",
    title: `${hokkaidoIndicatorReviewStats.reviewedIndicators}指標を全件照合`,
    text: "条件型目標、累計値、未公表値、比較上の注意を消さずに、公式計画の構造をそのまま確認できます。",
    facts: ["18政策分野", "108根拠記録", "実績は未接続"],
    href: "/municipalities/hokkaido",
    action: "政策指標を見る",
  },
  {
    className: styles.fukuokaCard,
    area: "福岡県",
    label: "政策と財政を読む",
    title: `${allPolicyTargetStats.reviewedTargets}件の数値目標`,
    text: "4基本方向・30取組と財政資料を公開。実績が未接続の目標には、達成率を付けていません。",
    facts: ["30取組", "政策目標118件", "県・2市の財政"],
    href: "/municipalities/fukuoka-prefecture",
    action: "福岡県を見る",
  },
];

export default function Home() {
  return (
    <main id="main-content">
      <SiteHeader />

      <section className={styles.hero}>
        <div className={styles.heroCopy}>
          <p className={styles.heroKicker}>PUBLIC EVIDENCE FOR LOCAL GOVERNMENT</p>
          <h1>自治体を、<br /><em>自分で確かめる。</em></h1>
          <p className={styles.heroLead}>
            計画、予算、事業、成果、議会。ばらばらに公開された一次資料を、
            住民が判断できる順序へつなぎ直します。
          </p>
          <div className={styles.heroActions}>
            <Link className="primaryAction" href="/municipalities">全国47都道府県から探す</Link>
            <Link className="secondaryAction" href="/about">このサイトの目的</Link>
          </div>
          <div className={styles.heroPrinciples} aria-label="表示原則">
            <span>一次資料を表示</span>
            <span>未確認を明記</span>
            <span>単純ランキングなし</span>
          </div>
        </div>

        <aside className={styles.currentFocus} aria-labelledby="current-focus-title">
          <div className={styles.focusHeader}>
            <span>いま最も深く読める自治体</span>
            <StatusBadge label="年度実績あり" tone="verified" />
          </div>
          <p className={styles.focusArea}>04 / MIYAGI</p>
          <h2 id="current-focus-title">宮城県の目標と、4年分の実績。</h2>
          <dl className={styles.focusMetrics}>
            <div><dt>直接接続</dt><dd>{miyagiKpiActualStats.linkedSeries}<small>系列</small></dd></div>
            <div><dt>対応要確認</dt><dd>{miyagiKpiActualStats.reviewNeededSeries}<small>系列</small></dd></div>
            <div><dt>年度実績</dt><dd>{miyagiKpiActualStats.annualResultRows}<small>行</small></dd></div>
          </dl>
          <p className={styles.focusNote}>
            公式評価書の令和6年度目標と、現行計画の令和9年度目標を分けて表示します。
          </p>
          <Link href="/municipalities/miyagi#results">実績の推移を見る <span aria-hidden="true">→</span></Link>
        </aside>
      </section>

      <section className={styles.snapshot} aria-label="現在のデータ公開状況">
        <div className={styles.snapshotLead}>
          <p>JICHI INSIGHT NOW</p>
          <strong>現在地を、数字で。</strong>
          <span>更新 {nationwideCoverageStats.updatedAt}</span>
        </div>
        <dl>
          <div><dt>現行計画を確認</dt><dd>{nationwideCoverageStats.currentPlanConfirmedPrefectures}<small>/47</small></dd></div>
          <div><dt>都道府県詳細</dt><dd>{nationwideCoverageStats.publishedPrefecturePages}<small>地域</small></dd></div>
          <div><dt>Reviewed目標・指標</dt><dd>{hokkaidoIndicatorReviewStats.reviewedIndicators + miyagiPolicyReviewStats.reviewedTargetGroups + allPolicyTargetStats.reviewedTargets}<small>件</small></dd></div>
          <div><dt>宮城・年度実績</dt><dd>{miyagiKpiActualStats.annualResultRows}<small>行</small></dd></div>
          <div><dt>Jichi Insight評価</dt><dd>{catalogStats.publishedEvaluations}<small>件</small></dd></div>
        </dl>
      </section>

      <section className={styles.section}>
        <div className={styles.sectionHeading}>
          <div>
            <p className="eyebrow">Start with a question</p>
            <h2>知りたい深さから、入口を選ぶ。</h2>
          </div>
          <p>掲載件数の多さではなく、何をどこまで確認できるかで選べます。</p>
        </div>
        <div className={styles.depthGrid}>
          {depthCards.map((card) => (
            <article className={`${styles.depthCard} ${card.className}`} key={card.area}>
              <div className={styles.depthTop}><span>{card.area}</span><small>{card.label}</small></div>
              <h3>{card.title}</h3>
              <p>{card.text}</p>
              <ul>{card.facts.map((fact) => <li key={fact}>{fact}</li>)}</ul>
              <Link href={card.href}>{card.action} <span aria-hidden="true">→</span></Link>
            </article>
          ))}
          <article className={`${styles.depthCard} ${styles.nationwideCard}`}>
            <div className={styles.depthTop}><span>全国</span><small>資料の深さを探す</small></div>
            <h3>47都道府県を、6種類の資料で比較。</h3>
            <p>政策計画、実施計画、KPI、年度評価、予算・決算、事業評価の索引状況を確認できます。</p>
            <ul><li>公式入口 47/47</li><li>現行計画 47/47</li><li>未索引も表示</li></ul>
            <Link href="/municipalities#prefectures">全国から探す <span aria-hidden="true">→</span></Link>
          </article>
        </div>
      </section>

      <section className={`${styles.section} ${styles.chainSection}`}>
        <div className={styles.sectionHeading}>
          <div>
            <p className="eyebrow">One chain, five questions</p>
            <h2>資料ではなく、判断の順番でつなぐ。</h2>
          </div>
          <p>目標だけ、金額だけ、結果だけを切り取らず、前後の根拠をたどれる状態を目指します。</p>
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
            <p className="eyebrow">Nationwide source depth</p>
            <h2>47の入口は揃った。<br />次は、資料の奥行き。</h2>
            <p className={styles.readinessLead}>
              現行の政策計画は全都道府県で確認済みです。一方、年度評価や事業評価はまだ多くが未索引です。
              「ない」と「まだ確認していない」を分けて公開します。
            </p>
            <Link className="secondaryAction" href="/municipalities">資料カバレッジを見る</Link>
          </div>
          <div className={styles.readinessBars}>
            {sourceInventoryCategoryOrder.map((category) => {
              const count = nationwideSourceInventoryStats[category].indexedOrHigher;
              return (
                <div key={category}>
                  <div><span>{sourceInventoryCategoryLabel(category)}</span><strong>{count}<small>/47</small></strong></div>
                  <div className={styles.bar} aria-label={`${sourceInventoryCategoryLabel(category)} ${count}/47`}>
                    <span style={{ width: `${(count / 47) * 100}%` }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      <section className={styles.trustSection}>
        <div>
          <p className="eyebrow">Facts before scores</p>
          <h2>評価より先に、<br />評価できる状態かを示す。</h2>
        </div>
        <div>
          <p>
            Jichi Insightの目的は、自治体や人物に早く点数を付けることではありません。
            事実、比較、解釈、評価を分け、足りない根拠は足りないまま表示します。
          </p>
          <ul>
            <li><strong>確認済み</strong><span>一次資料と人が照合</span></li>
            <li><strong>要確認</strong><span>定義差・系列差などを保留</span></li>
            <li><strong>未接続</strong><span>実績・予算・事業との対応なし</span></li>
            <li><strong>評価不能</strong><span>根拠不足を点数で埋めない</span></li>
          </ul>
          <div className={styles.trustActions}>
            <Link className="invertedAction" href="/methodology">読み方・評価方法</Link>
            <Link href="/data-quality">全データ品質を見る →</Link>
          </div>
        </div>
      </section>

      <SiteFooter />
    </main>
  );
}
