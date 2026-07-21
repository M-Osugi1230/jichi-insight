import type { Metadata } from "next";
import Link from "next/link";

import { PageIntro } from "@/components/PageIntro";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { StatusBadge } from "@/components/StatusBadge";
import { TokyoPolicyTargetExplorer } from "@/components/TokyoPolicyTargetExplorer";
import {
  reviewedTokyoPolicyTargets,
  tokyoPolicySources,
  tokyoPolicyTargetStats,
  tokyoValueDisplay,
  tokyoValueRoleLabel,
} from "@/lib/tokyoPolicyTargets";

import styles from "./page.module.css";

export const metadata: Metadata = {
  title: "東京都｜2050東京戦略の政策目標304件",
  description:
    "2050東京戦略の政策目標一覧60ページ、25政策分野、304目標カードをEvidence Packet付きで公開しています。年度実績と政策評価は未接続です。",
};

export default function TokyoPage() {
  return (
    <main id="main-content">
      <SiteHeader />
      <div className="pageShell">
        <PageIntro eyebrow="Tokyo policy targets" title="東京都の政策目標を、値と条件を変えずに読む。">
          <p>
            「2050東京戦略 政策目標一覧」全{tokyoPolicyTargetStats.sourcePages}ページ、
            {tokyoPolicyTargetStats.policyAreas}政策分野、{tokyoPolicyTargetStats.reviewedTargetCards}目標カードを
            Evidence Packet付きでReviewed化しました。これは政策成果の達成率ではなく、
            公式資料を原文・ページ・目標型から確認したデータカバレッジです。
          </p>
          <div className={styles.introLinks}>
            <Link href="/municipalities">全国47都道府県へ戻る</Link>
            <a
              href="https://www.seisakukikaku.metro.tokyo.lg.jp/documents/d/seisakukikaku/2050tokyo-seisakumokuhyo2026"
              target="_blank"
              rel="noreferrer"
            >
              公式の政策目標一覧を開く ↗
            </a>
          </div>
        </PageIntro>

        <section className={styles.summaryGrid} aria-label="東京都政策目標の公開状況">
          <article>
            <span>Reviewed目標カード</span>
            <strong>{tokyoPolicyTargetStats.reviewedTargetCards}</strong>
            <p>公式PDFの全目標カード。見出し、強調目標、ページ、全文を保存。</p>
          </article>
          <article>
            <span>政策分野</span>
            <strong>{tokyoPolicyTargetStats.policyAreas}</strong>
            <p>子供から多摩・島しょまで、公式掲載順を維持。</p>
          </article>
          <article>
            <span>Evidence Packet</span>
            <strong>{tokyoPolicyTargetStats.evidencePackets}</strong>
            <p>304件すべてに公式ページとカード位置の根拠を付与。</p>
          </article>
          <article>
            <span>年度実績へ接続済み</span>
            <strong>{tokyoPolicyTargetStats.actualLinkedSeries}</strong>
            <p>政策レビューとの定義照合前のため、達成率は表示しません。</p>
          </article>
        </section>

        <section className={styles.progressSection} aria-labelledby="tokyo-review-progress">
          <div>
            <p className="eyebrow">Review coverage</p>
            <h2 id="tokyo-review-progress">
              60 / 60ページの政策目標カードReviewedを完了。
            </h2>
          </div>
          <div className={styles.progressDetail}>
            <div className={styles.progressTrack} aria-hidden="true">
              <span style={{ width: "100%" }} />
            </div>
            <dl>
              <div><dt>目標カード</dt><dd>{tokyoPolicyTargetStats.reviewedTargetCards}件</dd></div>
              <div><dt>政策分野</dt><dd>{tokyoPolicyTargetStats.policyAreas}分野</dd></div>
              <div><dt>未Reviewedページ</dt><dd>{tokyoPolicyTargetStats.remainingPages}ページ</dd></div>
              <div><dt>次工程</dt><dd>{tokyoPolicyTargetStats.nextReviewScope}</dd></div>
            </dl>
            <p>
              目標カードの見出し・強調された目標・全文は全件Reviewed済みです。
              一方、子供分野以外のグラフ点列は未正規化であり、年度実績・政策評価とも未接続です。
            </p>
          </div>
        </section>

        <section className="contentSection" aria-labelledby="tokyo-all-targets">
          <div className={styles.sectionHeading}>
            <div>
              <p className="eyebrow">All target cards</p>
              <h2 id="tokyo-all-targets">25政策分野・304目標カードを横断検索。</h2>
            </div>
            <p>
              下限、上限、累計、維持、順位、定性目標を同じ数値へ変換しません。
              公式カード全文を開き、原文とページをその場で確認できます。
            </p>
          </div>
          <TokyoPolicyTargetExplorer />
        </section>

        <section className="contentSection">
          <div className={styles.sectionHeading}>
            <div>
              <p className="eyebrow">Detailed review layer</p>
              <h2>子供分野は、グラフ点列まで詳細Reviewed。</h2>
            </div>
            <p>
              PDFページ1〜2の{tokyoPolicyTargetStats.detailedTargetGroups}目標・
              {tokyoPolicyTargetStats.reviewedSeries}系列は、基準値・現状値・途中目標・最終目標を
              別々の値として照合しています。
            </p>
          </div>

          <div className={styles.targetGrid}>
            {reviewedTokyoPolicyTargets.map((target) => (
              <article className={styles.targetCard} key={target.id}>
                <div className={styles.targetHeader}>
                  <span>{String(target.target_group_number).padStart(2, "0")}</span>
                  <StatusBadge label="点列までReviewed" tone="verified" />
                </div>
                <p className={styles.measure}>{target.policy_measure_original}</p>
                <h3>{target.target_name_original}</h3>
                {target.population_scope_original ? (
                  <p className={styles.scope}>対象：{target.population_scope_original}</p>
                ) : null}

                <div className={styles.seriesList}>
                  {target.series.map((series) => (
                    <section key={series.id} aria-label={series.label ?? target.target_name_original}>
                      {series.label ? <h4>{series.label}</h4> : null}
                      <div className={styles.valueGrid}>
                        {series.values.map((value) => (
                          <div key={`${series.id}-${value.role}-${value.period}`}>
                            <span>{tokyoValueRoleLabel(value.role)}</span>
                            <strong>{tokyoValueDisplay(value, series.unit_original)}</strong>
                            <small>{value.period}</small>
                          </div>
                        ))}
                      </div>
                    </section>
                  ))}
                </div>

                <div className={styles.boundaryNote}>
                  <strong>比較上の境界</strong>
                  <p>{target.comparability_note_original}</p>
                </div>
                <footer>
                  <span>公式PDF p.{target.source_page}</span>
                  <span>年度実績 未接続</span>
                  <span>政策評価 未判定</span>
                </footer>
              </article>
            ))}
          </div>
        </section>

        <section className={styles.sourceSection} aria-labelledby="tokyo-sources">
          <div>
            <p className="eyebrow">Official sources</p>
            <h2 id="tokyo-sources">目標・実績・評価を、同じ資料として扱わない。</h2>
            <p>
              2026年の政策目標一覧と、2025年の政策レビュー・取組状況は版と役割が異なります。
              定義と期間が一致する系列だけを、次工程で年度実績へ接続します。
            </p>
          </div>
          <div className={styles.sourceList}>
            {tokyoPolicySources.map((source) => (
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
