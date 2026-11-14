import type { Metadata } from "next";
import Link from "next/link";

import { PageIntro } from "@/components/PageIntro";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { phase15Progress, phase15StatusLabels } from "@/lib/phase15Progress";

import styles from "./page.module.css";

export const metadata: Metadata = {
  title: "自治体レビューの進捗・収録範囲",
  description:
    "Jichi InsightのPhase 15対象67自治体について、一次資料レビューの完了・進行中・未着手を、正本データから透明に公開します。",
};

const sourcePrefix = "https://github.com/M-Osugi1230/jichi-insight/blob/main/";

export default function ReviewProgressPage() {
  const progressPercent = (phase15Progress.reviewed / phase15Progress.total) * 100;

  return (
    <main id="main-content">
      <SiteHeader />
      <div className="pageShell">
        <PageIntro
          eyebrow="Coverage / Phase 15"
          title="どこまで確認できたかも、公開する。"
        >
          <p>
            47都道府県の公開済みデータと、中核市・県庁所在地67自治体の詳細レビューは別の取り組みです。
            このページではPhase 15の進捗を、審査待ちも含めて公開します。
            「資料を発見した」「候補を作った」だけでレビュー完了とは扱いません。
          </p>
        </PageIntro>

        <section className={styles.summary} aria-labelledby="review-progress-title">
          <div className={styles.summaryHeading}>
            <div>
              <p className="eyebrow">Current review coverage</p>
              <h2 id="review-progress-title">Phase 15の現在地</h2>
            </div>
            <p>正本更新日: <time>{phase15Progress.updatedAt}</time></p>
          </div>

          <dl className={styles.metrics}>
            <div>
              <dt>レビュー完了</dt>
              <dd>{phase15Progress.reviewed}<small> / {phase15Progress.total}</small></dd>
            </div>
            <div>
              <dt>進行中</dt>
              <dd>{phase15Progress.inProgress}<small> 自治体</small></dd>
            </div>
            <div>
              <dt>レビュー待ち</dt>
              <dd>{phase15Progress.pending}<small> 自治体</small></dd>
            </div>
            <div>
              <dt>資料確認に課題あり</dt>
              <dd>{phase15Progress.blocked}<small> 自治体</small></dd>
            </div>
          </dl>
          <div className={styles.progressLabel}>
            <strong>レビュー完了率</strong>
            <span>{progressPercent.toFixed(1)}%</span>
          </div>
          <progress
            className={styles.progress}
            value={phase15Progress.reviewed}
            max={phase15Progress.total}
            aria-label="Phase 15のレビュー完了自治体数"
          >
            {phase15Progress.reviewed} / {phase15Progress.total}
          </progress>
          {phase15Progress.nextMunicipality && (
            <p className={styles.next}>
              次の審査対象: <strong>{phase15Progress.nextMunicipality}</strong>
            </p>
          )}
        </section>

        <section className={styles.boundary} aria-labelledby="public-boundary-title">
          <h2 id="public-boundary-title">公開対象と、未確認の境界</h2>
          <p>
            「レビュー完了」は一次資料との人による照合を経た状態です。
            それ以外の自治体では資料の索引があっても、個別事業・指標・実績・金額が確認済みとは限りません。
            作業中の候補データは、Reviewedデータとして公開しません。
          </p>
          <p>
            この一覧は進捗の透明性を示すものであり、自治体の政策成果や優劣を示すランキングではありません。
            各自治体の正式なレビュー状況は、更新日付きの正本キューに従います。
          </p>
          <Link href="/data-quality">データ品質と表示上の限界を読む →</Link>
        </section>

        <section className={styles.directory} aria-labelledby="review-directory-title">
          <div className={styles.directoryHeading}>
            <div>
              <p className="eyebrow">All 67 municipalities</p>
              <h2 id="review-directory-title">自治体別のレビュー状況</h2>
            </div>
            <p>
              資料索引と完了記録はGitHub上の公開原本です。
              審査中・未着手の行には「完了記録」を表示しません。
            </p>
          </div>

          <ol className={styles.list}>
            {phase15Progress.municipalities.map((record) => (
              <li key={record.officialCode} className={styles.municipality}>
                <div className={styles.identity}>
                  <span className={styles.sequence}>{String(record.sequence).padStart(2, "0")}</span>
                  <div>
                    <small>{record.prefecture} / Wave {record.wave}</small>
                    <strong>{record.name}</strong>
                  </div>
                </div>
                <div className={styles.reviewDetails}>
                  <span
                    className={
                      record.status === "reviewed_complete"
                        ? styles.reviewed
                        : record.status === "review_in_progress"
                          ? styles.inProgress
                          : styles.waiting
                    }
                  >
                    {phase15StatusLabels[record.status]}
                  </span>
                  <div className={styles.evidenceLinks}>
                    <a
                      href={sourcePrefix + record.sourceInventoryPath}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      公式資料の索引
                    </a>
                    {record.status === "reviewed_complete" && record.completionPath && (
                      <a
                        href={sourcePrefix + record.completionPath}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        レビュー完了記録
                      </a>
                    )}
                  </div>
                </div>
              </li>
            ))}
          </ol>
        </section>

        <div className={styles.disclaimer}>
          <p>掲載状態は公式資料の有無や政策の達成度を意味しません。</p>
          <Link href="/methodology">判定方法を見る →</Link>
          <Link href="/corrections">誤りを報告する →</Link>
        </div>
      </div>
      <SiteFooter />
    </main>
  );
}
