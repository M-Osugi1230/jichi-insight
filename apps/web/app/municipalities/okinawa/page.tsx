import type { Metadata } from "next";
import Link from "next/link";

import { OkinawaIndicatorExplorer } from "@/components/OkinawaIndicatorExplorer";
import { PageIntro } from "@/components/PageIntro";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import {
  okinawaIndicatorStats,
  okinawaReviewManifest,
} from "@/lib/okinawaIndicators";

import styles from "./page.module.css";

export const metadata: Metadata = {
  title: "沖縄県｜中期実施計画の376指標",
  description:
    "新・沖縄21世紀ビジョン実施計画（中期）の主要指標37件・成果指標339件を、基準値、令和9年度目標、全国値、離島・SDGs属性とともに公開します。",
};

export default function OkinawaPage() {
  return (
    <main id="main-content">
      <SiteHeader />
      <div className="pageShell">
        <PageIntro
          eyebrow="Okinawa midterm indicators"
          title="沖縄県の376指標を、主要と成果を分けて読む。"
        >
          <p>
            新・沖縄21世紀ビジョン実施計画（中期：令和7年度～令和9年度）の附属資料から、
            主要指標{okinawaIndicatorStats.majorIndicators}件と成果指標
            {okinawaIndicatorStats.outcomeIndicators}件を全件Reviewed化しました。
            活動指標は年度の事業量であり、政策成果とは別レイヤーに残します。
          </p>
          <div className={styles.introLinks}>
            <Link href="/municipalities">全国47都道府県へ戻る</Link>
            <a href={okinawaReviewManifest.source_url} target="_blank" rel="noreferrer">
              公式附属資料を開く ↗
            </a>
          </div>
        </PageIntro>

        <section className={styles.summaryGrid} aria-label="沖縄県指標の公開状況">
          <article>
            <span>Reviewed指標</span>
            <strong>{okinawaIndicatorStats.reviewedIndicators}</strong>
            <p>主要37件と成果339件を同じ順序でEvidenceへ接続。</p>
          </article>
          <article>
            <span>全国比較あり</span>
            <strong>{okinawaIndicatorStats.nationalComparators}</strong>
            <p>全国値が「－」の指標をゼロへ変換しません。</p>
          </article>
          <article>
            <span>離島指標</span>
            <strong>{okinawaIndicatorStats.remoteIslandIndicators}</strong>
            <p>離島属性を比較対象や母集団と混同しません。</p>
          </article>
          <article>
            <span>Evidence</span>
            <strong>{okinawaIndicatorStats.evidencePackets}</strong>
            <p>政策、名称、基準値、令和9年度目標、全国値を記録。</p>
          </article>
        </section>

        <section className={styles.boundary}>
          <div>
            <p className="eyebrow">Data boundaries</p>
            <h2>成果、活動、地域属性を同じ点数にしない。</h2>
          </div>
          <div className={styles.boundaryGrid}>
            <article><strong>主要と成果</strong><p>基本施策の主要指標と個別施策の成果指標を別レイヤーで保持します。</p></article>
            <article><strong>活動指標</strong><p>今回の成果カタログへの収録は{okinawaIndicatorStats.activityIndicators}件です。事業量として別管理します。</p></article>
            <article><strong>全国値・離島・SDGs</strong><p>比較値と属性を達成率の加点要素へ変換しません。SDGs連携は{okinawaIndicatorStats.sdgsLinkedIndicators}件です。</p></article>
            <article><strong>独自評価</strong><p>政策達成判定は{okinawaIndicatorStats.assessedIndicators}件です。Reviewedは一次資料との照合完了を示します。</p></article>
          </div>
        </section>

        <section className="contentSection" aria-labelledby="okinawa-indicators">
          <div className={styles.sectionHeading}>
            <div>
              <p className="eyebrow">Reviewed indicators</p>
              <h2 id="okinawa-indicators">376指標を、政策・属性・比較状態から探す。</h2>
            </div>
            <p>
              男女別、離島と本島過疎、全国比較なし、定性目標
              {okinawaIndicatorStats.qualitativeTargets}件などを原文の意味のまま表示します。
            </p>
          </div>
          <OkinawaIndicatorExplorer />
        </section>

        <section className={styles.sourceCallout}>
          <p className="eyebrow">Next linkage</p>
          <h2>PDCA評価を、同じ定義の指標へ接続する。</h2>
          <p>{okinawaReviewManifest.next_review_scope}</p>
          <a href="https://www.pref.okinawa.jp/kensei/shisaku/1014166/1034436.html" target="_blank" rel="noreferrer">
            沖縄県の中期実施計画ページを開く ↗
          </a>
        </section>
      </div>
      <SiteFooter />
    </main>
  );
}
