import type { Metadata } from "next";
import Link from "next/link";

import { HiroshimaIndicatorExplorer } from "@/components/HiroshimaIndicatorExplorer";
import { PageIntro } from "@/components/PageIntro";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import {
  hiroshimaIndicatorStats,
  hiroshimaReviewManifest,
} from "@/lib/hiroshimaIndicators";

import styles from "./page.module.css";

export const metadata: Metadata = {
  title: "広島県｜改定版ひろしまビジョンの成果指標",
  description:
    "改定版「安心▷誇り▷挑戦 ひろしまビジョン」の現行62指標を、基準値、最新値、目標、資料位置とともに公開します。",
};

export default function HiroshimaPage() {
  return (
    <main id="main-content">
      <SiteHeader />
      <div className="pageShell">
        <PageIntro
          eyebrow="Hiroshima revised vision indicators"
          title="広島県の62指標を、改定後の定義と目標から読む。"
        >
          <p>
            2026年7月公表の改定版「安心▷誇り▷挑戦 ひろしまビジョン」に掲載された
            現行指標を全件Reviewed化しました。削除された旧指標を含めず、基準値、最新値、
            令和10年度・令和12年度目標、出典、資料ページを一対一で保持しています。
          </p>
          <div className={styles.introLinks}>
            <Link href="/municipalities">全国47都道府県へ戻る</Link>
            <a
              href={hiroshimaReviewManifest.source_url}
              target="_blank"
              rel="noreferrer"
            >
              改定版ビジョンを開く ↗
            </a>
          </div>
        </PageIntro>

        <section className={styles.summaryGrid} aria-label="広島県指標の公開状況">
          <article>
            <span>Reviewed指標</span>
            <strong>{hiroshimaIndicatorStats.reviewedIndicators}</strong>
            <p>参考資料7ページに掲載された現行指標の全件です。</p>
          </article>
          <article>
            <span>政策分野</span>
            <strong>{hiroshimaIndicatorStats.policyAreas}</strong>
            <p>子供、教育、医療、防災、産業、中山間地域などを保持。</p>
          </article>
          <article>
            <span>現状値あり</span>
            <strong>{hiroshimaIndicatorStats.currentValues}</strong>
            <p>未測定3件をゼロへ置換せず、そのまま分離します。</p>
          </article>
          <article>
            <span>Evidence ID</span>
            <strong>{hiroshimaIndicatorStats.evidencePackets}</strong>
            <p>指標、資料ページ、値、出典を一対一で記録。</p>
          </article>
        </section>

        <section className={styles.boundary}>
          <div>
            <p className="eyebrow">Data boundaries</p>
            <h2>改定、未測定、定性目標を同じ数値にしない。</h2>
          </div>
          <div className={styles.boundaryGrid}>
            <article><strong>削除指標</strong><p>改定資料で削除扱いとなった旧指標は、現行62指標へ含めません。</p></article>
            <article><strong>測定待ち</strong><p>{hiroshimaIndicatorStats.pendingMeasurements}件は未測定のまま保持し、0件・0％へ変換しません。</p></article>
            <article><strong>目標年度</strong><p>令和10年度目標と令和12年度目標を分離し、同一時点として比較しません。</p></article>
            <article><strong>独自評価</strong><p>政策達成判定は{hiroshimaIndicatorStats.assessedIndicators}件です。達成率や順位を独自計算しません。</p></article>
          </div>
        </section>

        <section className="contentSection" aria-labelledby="hiroshima-indicators">
          <div className={styles.sectionHeading}>
            <div>
              <p className="eyebrow">Reviewed indicators</p>
              <h2 id="hiroshima-indicators">62指標を、分野・値・年度・出典から探す。</h2>
            </div>
            <p>全国平均との比較、複数系列、概数、減少目標、複数年平均、定性目標を原文のまま表示します。</p>
          </div>
          <HiroshimaIndicatorExplorer />
        </section>

        <section className={styles.sourceCallout}>
          <p className="eyebrow">Next linkage</p>
          <h2>新アクションプランと年度実績は、別工程で接続する。</h2>
          <p>{hiroshimaReviewManifest.next_review_scope}</p>
          <a
            href="https://www.pref.hiroshima.lg.jp/site/hiroshimavision/"
            target="_blank"
            rel="noreferrer"
          >広島県のビジョン公式ページを開く ↗</a>
        </section>
      </div>
      <SiteFooter />
    </main>
  );
}
