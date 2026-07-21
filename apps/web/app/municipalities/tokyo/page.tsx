import type { Metadata } from "next";
import Link from "next/link";

import { PageIntro } from "@/components/PageIntro";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { StatusBadge } from "@/components/StatusBadge";
import {
  reviewedTokyoPolicyTargets,
  tokyoPolicySources,
  tokyoPolicyTargetStats,
  tokyoValueDisplay,
  tokyoValueRoleLabel,
} from "@/lib/tokyoPolicyTargets";

import styles from "./page.module.css";

export const metadata: Metadata = {
  title: "東京都｜2050東京戦略の政策目標",
  description:
    "2050東京戦略の政策目標一覧60ページを索引化し、子供分野の8目標・9系列をEvidence Packet付きで公開しています。",
};

export default function TokyoPage() {
  return (
    <main id="main-content">
      <SiteHeader />
      <div className="pageShell">
        <PageIntro eyebrow="Tokyo policy targets" title="東京都の政策目標を、値と条件を変えずに読む。">
          <p>
            「2050東京戦略 政策目標一覧」全{tokyoPolicyTargetStats.sourcePages}ページの位置を索引化し、
            最初の子供分野について{tokyoPolicyTargetStats.reviewedTargetGroups}目標・
            {tokyoPolicyTargetStats.reviewedSeries}系列を人が照合しました。
            これは政策成果の達成率ではなく、公式資料のReviewedカバレッジです。
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
            <span>Reviewed目標</span>
            <strong>{tokyoPolicyTargetStats.reviewedTargetGroups}</strong>
            <p>子供分野の目標グループ。複数系列は統合しません。</p>
          </article>
          <article>
            <span>Reviewed系列</span>
            <strong>{tokyoPolicyTargetStats.reviewedSeries}</strong>
            <p>割合、自治体数、定性的な実施状態を別系列で保持。</p>
          </article>
          <article>
            <span>Evidence Packet</span>
            <strong>{tokyoPolicyTargetStats.evidencePackets}</strong>
            <p>各目標に名称、値、期間、PDFページの根拠を付与。</p>
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
              {tokyoPolicyTargetStats.reviewedPages} / {tokyoPolicyTargetStats.sourcePages}ページをReviewed。
            </h2>
          </div>
          <div className={styles.progressDetail}>
            <div className={styles.progressTrack} aria-hidden="true">
              <span
                style={{
                  width: `${
                    (tokyoPolicyTargetStats.reviewedPages / tokyoPolicyTargetStats.sourcePages) * 100
                  }%`,
                }}
              />
            </div>
            <dl>
              <div><dt>位置索引</dt><dd>{tokyoPolicyTargetStats.sourcePages}ページ</dd></div>
              <div><dt>本文Reviewed</dt><dd>{tokyoPolicyTargetStats.reviewedPages}ページ</dd></div>
              <div><dt>残り</dt><dd>{tokyoPolicyTargetStats.remainingPages}ページ</dd></div>
              <div><dt>次工程</dt><dd>{tokyoPolicyTargetStats.nextReviewScope}</dd></div>
            </dl>
            <p>
              未Reviewedページは数値を公開せず、位置索引だけを保持します。
              政策目標、年度実績、政策評価、予算事業はそれぞれ別の資料役割として接続します。
            </p>
          </div>
        </section>

        <section className="contentSection">
          <div className={styles.sectionHeading}>
            <div>
              <p className="eyebrow">Reviewed area 01</p>
              <h2>子供（Children）</h2>
            </div>
            <p>
              PDFページ1〜2を照合済みです。下限型目標、維持目標、対象年齢、母集団の違いを残しています。
            </p>
          </div>

          <div className={styles.targetGrid}>
            {reviewedTokyoPolicyTargets.map((target) => (
              <article className={styles.targetCard} key={target.id}>
                <div className={styles.targetHeader}>
                  <span>{String(target.target_group_number).padStart(2, "0")}</span>
                  <StatusBadge label="Reviewed" tone="verified" />
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
              定義と期間が一致する系列だけを、今後の工程で年度実績へ接続します。
            </p>
          </div>
          <div className={styles.sourceList}>
            {tokyoPolicySources.map((source) => (
              <article key={source.id}>
                <div>
                  <span>{source.category}</span>
                  <StatusBadge
                    label={source.review_status === "partially_reviewed" ? "一部Reviewed" : "Indexed"}
                    tone={source.review_status === "partially_reviewed" ? "progress" : "neutral"}
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
