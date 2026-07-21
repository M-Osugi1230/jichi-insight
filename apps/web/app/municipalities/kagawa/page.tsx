import type { Metadata } from "next";
import Link from "next/link";

import { KagawaIndicatorExplorer } from "@/components/KagawaIndicatorExplorer";
import { PageIntro } from "@/components/PageIntro";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import {
  kagawaIndicatorStats,
  kagawaReviewManifest,
} from "@/lib/kagawaIndicators";

import styles from "./page.module.css";

export const metadata: Metadata = {
  title: "香川県｜延長後計画の135指標",
  description:
    "「人生100年時代のフロンティア県・香川」実現計画の135指標を、現状値、延長前目標、延長後目標、Evidenceとともに公開します。",
};

export default function KagawaPage() {
  return (
    <main id="main-content">
      <SiteHeader />
      <div className="pageShell">
        <PageIntro
          eyebrow="Kagawa extended-plan indicators"
          title="香川県の135指標を、延長前と延長後の目標から読む。"
        >
          <p>
            計画期間が令和8年度まで延長されたことに伴う公式の指標見直し表を全件Reviewed化しました。
            令和7年度目標と令和8年度目標を分離し、再掲6指標は掲載位置を保持しながら固有指標数へ重複計上しません。
          </p>
          <div className={styles.introLinks}>
            <Link href="/municipalities">全国47都道府県へ戻る</Link>
            <a href={kagawaReviewManifest.source_url} target="_blank" rel="noreferrer">
              公式の指標見直し資料を開く ↗
            </a>
          </div>
        </PageIntro>

        <section className={styles.summaryGrid} aria-label="香川県指標の公開状況">
          <article>
            <span>Reviewed指標</span>
            <strong>{kagawaIndicatorStats.reviewedIndicators}</strong>
            <p>番号1から135まで欠番なくEvidenceへ接続。</p>
          </article>
          <article>
            <span>掲載位置</span>
            <strong>{kagawaIndicatorStats.displayOccurrences}</strong>
            <p>再掲位置を含む表上の掲載回数です。</p>
          </article>
          <article>
            <span>目標更新</span>
            <strong>{kagawaIndicatorStats.targetRevisions}</strong>
            <p>延長前と延長後で原文が変わった指標。</p>
          </article>
          <article>
            <span>Evidence</span>
            <strong>{kagawaIndicatorStats.evidencePackets}</strong>
            <p>名称、現状値、旧目標、新目標、資料位置を記録。</p>
          </article>
        </section>

        <section className={styles.boundary}>
          <div>
            <p className="eyebrow">Data boundaries</p>
            <h2>計画延長を、単なる年度の置換にしない。</h2>
          </div>
          <div className={styles.boundaryGrid}>
            <article><strong>旧目標と新目標</strong><p>令和7年度目標と令和8年度目標を両方残し、改定履歴として確認できます。</p></article>
            <article><strong>再掲</strong><p>{kagawaIndicatorStats.repostedIndicators}指標は複数の政策位置に掲載されますが、固有指標数では一度だけ数えます。</p></article>
            <article><strong>参考指標135</strong><p>県人口は令和8年度ではなく令和12年目標です。年度を自動変換しません。</p></article>
            <article><strong>独自評価</strong><p>政策達成判定は{kagawaIndicatorStats.assessedIndicators}件です。Reviewedは出典照合の完了を示します。</p></article>
          </div>
        </section>

        <section className="contentSection" aria-labelledby="kagawa-indicators">
          <div className={styles.sectionHeading}>
            <div>
              <p className="eyebrow">Reviewed indicators</p>
              <h2 id="kagawa-indicators">135指標を、名称・値・変更状態から探す。</h2>
            </div>
            <p>複数系列、累計、下限・上限、年度途中値、訂正前後の値を原文の意味のまま表示します。</p>
          </div>
          <KagawaIndicatorExplorer />
        </section>

        <section className={styles.sourceCallout}>
          <p className="eyebrow">Next linkage</p>
          <h2>行政評価と年度実績は、延長後目標へ定義照合する。</h2>
          <p>{kagawaReviewManifest.next_review_scope}</p>
          <a href="https://www.pref.kagawa.lg.jp/seisaku/sogo/sogokeikakuminaoshi/keikakuminaoshi.html" target="_blank" rel="noreferrer">
            香川県の現行計画ページを開く ↗
          </a>
        </section>
      </div>
      <SiteFooter />
    </main>
  );
}
