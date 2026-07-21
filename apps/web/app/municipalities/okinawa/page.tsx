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
  title: "沖縄県｜中期実施計画の375指標",
  description:
    "新・沖縄21世紀ビジョン実施計画（中期）の主要指標36件と成果指標339件を、基準値、R9年度目標、全国値、Evidenceとともに公開します。",
};

export default function OkinawaPage() {
  return (
    <main id="main-content">
      <SiteHeader />
      <div className="pageShell">
        <PageIntro
          eyebrow="Okinawa mid-term implementation indicators"
          title="沖縄県の375指標を、主要指標と成果指標に分けて読む。"
        >
          <p>
            現行の「新・沖縄21世紀ビジョン実施計画（中期：令和7年度～令和9年度）」附属資料を全件Reviewed化しました。
            基本施策を示す主要指標36件と、施策の成果を示す成果指標339件を分離し、活動指標や前期PDCA実績を混ぜません。
          </p>
          <div className={styles.introLinks}>
            <Link href="/municipalities">全国47都道府県へ戻る</Link>
            <a href={okinawaReviewManifest.source_url} target="_blank" rel="noreferrer">
              公式の附属資料を開く ↗
            </a>
          </div>
        </PageIntro>

        <section className={styles.summaryGrid} aria-label="沖縄県指標の公開状況">
          <article>
            <span>Reviewed指標</span>
            <strong>{okinawaIndicatorStats.reviewedIndicators}</strong>
            <p>全件を資料ページ・表行・Evidenceへ接続。</p>
          </article>
          <article>
            <span>主要指標</span>
            <strong>{okinawaIndicatorStats.majorIndicators}</strong>
            <p>36の基本施策の成果を示す上位指標。</p>
          </article>
          <article>
            <span>成果指標</span>
            <strong>{okinawaIndicatorStats.outcomeIndicators}</strong>
            <p>各施策の成果を検証する339指標。</p>
          </article>
          <article>
            <span>Evidence</span>
            <strong>{okinawaIndicatorStats.evidencePackets}</strong>
            <p>基準値、R9目標、全国値、根拠、属性を記録。</p>
          </article>
        </section>

        <section className={styles.boundary}>
          <div>
            <p className="eyebrow">Data boundaries</p>
            <h2>計画の階層と期間を、同じ数字にしない。</h2>
          </div>
          <div className={styles.boundaryGrid}>
            <article>
              <strong>主要指標と成果指標</strong>
              <p>基本施策36件と施策成果339件を別階層で保持し、合算した達成率を作りません。</p>
            </article>
            <article>
              <strong>離島・SDGs属性</strong>
              <p>離島指標{okinawaIndicatorStats.islandIndicators}件、SDGs優先課題{okinawaIndicatorStats.sdgsPriorityIndicators}件を原文属性として保持します。</p>
            </article>
            <article>
              <strong>定性目標</strong>
              <p>{okinawaIndicatorStats.qualitativeTargets}件は文章目標です。数値や達成率へ変換しません。</p>
            </article>
            <article>
              <strong>前期PDCA</strong>
              <p>令和4～6年度の実績は過年度評価です。現行R9年度目標へ自動接続しません。</p>
            </article>
          </div>
        </section>

        <section className={styles.sourceWarning}>
          <p className="eyebrow">Source-preserving review</p>
          <h2>原資料の単位差を、推測で直さない。</h2>
          <p>
            成果指標「再生可能エネルギー電源比率」のR9年度目標欄は、指標名・基準値と異なる単位で記載されています。
            Jichi Insightでは公式附属資料の値をそのまま保持し、原資料注記として明示します。
          </p>
        </section>

        <section className="contentSection" aria-labelledby="okinawa-indicators">
          <div className={styles.sectionHeading}>
            <div>
              <p className="eyebrow">Reviewed indicators</p>
              <h2 id="okinawa-indicators">375指標を、階層・政策・値・属性から探す。</h2>
            </div>
            <p>
              基準値、R9年度目標、全国の現状値、設定の考え方・出典、離島指標、SDGs優先課題を確認できます。
            </p>
          </div>
          <OkinawaIndicatorExplorer />
        </section>

        <section className={styles.sourceCallout}>
          <p className="eyebrow">Next linkage</p>
          <h2>過年度PDCAは、現行中期計画と定義を照合してから接続する。</h2>
          <p>{okinawaReviewManifest.next_review_scope}</p>
          <a
            href="https://www.pref.okinawa.jp/kensei/shisaku/1014211/1014252/index.html"
            target="_blank"
            rel="noreferrer"
          >
            沖縄県の施策評価ページを開く ↗
          </a>
        </section>
      </div>
      <SiteFooter />
    </main>
  );
}
