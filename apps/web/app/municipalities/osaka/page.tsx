import type { Metadata } from "next";
import Link from "next/link";

import { OsakaIndicatorExplorer } from "@/components/OsakaIndicatorExplorer";
import { PageIntro } from "@/components/PageIntro";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { StatusBadge } from "@/components/StatusBadge";
import { osakaIndicatorStats, osakaPolicySources } from "@/lib/osakaIndicators";

import styles from "./page.module.css";

export const metadata: Metadata = {
  title: "大阪府｜Beyond EXPO 2025の政策指標",
  description:
    "Beyond EXPO 2025の経済目標、客観KPI、主観・Well-Being指標83件・91系列をEvidence付きで公開します。",
};

export default function OsakaPage() {
  return (
    <main id="main-content">
      <SiteHeader />
      <div className="pageShell">
        <PageIntro eyebrow="Osaka Beyond EXPO indicators" title="大阪府の戦略目標とWell-Beingを、同じ点数にしない。">
          <p>
            2026年3月策定の最終版「Beyond EXPO 2025」から、経済目標
            {osakaIndicatorStats.strategyTargets}件、客観KPI
            {osakaIndicatorStats.objectiveKpis}件、主観・Well-Being指標
            {osakaIndicatorStats.subjectiveIndicators}件を照合しました。
            Reviewedは公式資料の抽出と根拠確認であり、政策の達成判定ではありません。
          </p>
          <div className={styles.introLinks}>
            <Link href="/municipalities">全国47都道府県へ戻る</Link>
            <a href="https://www.pref.osaka.lg.jp/o020060/kikaku_keikaku/beyondexpo2025/index.html" target="_blank" rel="noreferrer">
              公式の最終戦略を開く ↗
            </a>
          </div>
        </PageIntro>

        <section className={styles.summaryGrid} aria-label="大阪府政策指標の公開状況">
          <article>
            <span>Reviewed指標</span>
            <strong>{osakaIndicatorStats.indicatorRows}</strong>
            <p>現行戦略の明示目標・客観KPI・主観指標。</p>
          </article>
          <article>
            <span>指標系列</span>
            <strong>{osakaIndicatorStats.indicatorSeries}</strong>
            <p>日本人・外国人、男女、複数ランキングを統合しません。</p>
          </article>
          <article>
            <span>Evidence Packet</span>
            <strong>{osakaIndicatorStats.evidencePackets}</strong>
            <p>指標名、値、期間、尺度、PDFページを1対1で記録。</p>
          </article>
          <article>
            <span>初回調査待ち</span>
            <strong>{osakaIndicatorStats.subjectivePendingSurvey}</strong>
            <p>大阪府独自の主観指標。未調査を0点に変換しません。</p>
          </article>
        </section>

        <section className={styles.boundarySection}>
          <div>
            <p className="eyebrow">Data boundaries</p>
            <h2>目標、最新状態、主観評価を分ける。</h2>
          </div>
          <div className={styles.boundaryGrid}>
            <article>
              <strong>明示的な数値目標</strong>
              <p>2040年代の名目GDP80兆円が戦略の経済目標です。27客観KPIの最新値を個別目標へ読み替えません。</p>
            </article>
            <article>
              <strong>異なる回答尺度</strong>
              <p>幸福度等の0〜10点と、地域幸福度指標の1〜5点を同じ尺度として平均しません。</p>
            </article>
            <article>
              <strong>旧戦略の実績</strong>
              <p>「将来ビジョン・大阪」の令和4〜6年実績は別の戦略系統として保持し、自動接続しません。</p>
            </article>
            <article>
              <strong>事業一覧</strong>
              <p>令和8年度事業一覧は実施レイヤーです。事業費を指標達成の因果関係として扱いません。</p>
            </article>
          </div>
        </section>

        <section className="contentSection" aria-labelledby="osaka-all-indicators">
          <div className={styles.sectionHeading}>
            <div>
              <p className="eyebrow">Reviewed indicators</p>
              <h2 id="osaka-all-indicators">83指標を、レイヤー・分野・値から探す。</h2>
            </div>
            <p>
              順位、累計、最新値、主観尺度、逆転項目、未調査を原文の意味のまま表示します。
            </p>
          </div>
          <OsakaIndicatorExplorer />
        </section>

        <section className={styles.sourceSection} aria-labelledby="osaka-sources">
          <div>
            <p className="eyebrow">Official sources</p>
            <h2 id="osaka-sources">最終戦略、事業、旧実績、予算、事業評価を分ける。</h2>
            <p>
              2026年3月31日に策定された最終版を正本としています。意見募集時の案は現行戦略として扱いません。
            </p>
          </div>
          <div className={styles.sourceList}>
            {osakaPolicySources.map((source) => (
              <article key={source.id}>
                <div>
                  <span>{source.category}</span>
                  <StatusBadge
                    label={source.review_status === "reviewed" ? "Reviewed" : "Indexed"}
                    tone={source.review_status === "reviewed" ? "verified" : "neutral"}
                  />
                </div>
                <h3>{source.title}</h3>
                <p>{source.role_note}</p>
                <a href={source.url} target="_blank" rel="noreferrer">公式資料を開く ↗</a>
              </article>
            ))}
          </div>
        </section>
      </div>
      <SiteFooter />
    </main>
  );
}
