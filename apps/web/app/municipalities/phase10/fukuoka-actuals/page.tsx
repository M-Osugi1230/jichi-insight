import type { Metadata } from "next";
import Link from "next/link";

import { PageIntro } from "@/components/PageIntro";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import {
  fukuokaAnnualActualForTarget,
  fukuokaAnnualActualLinkage,
  fukuokaAnnualActualStatusLabel,
} from "@/lib/fukuokaAnnualActuals";
import { policyTargetPages } from "@/lib/policyTargets";

import styles from "./page.module.css";

export const metadata: Metadata = {
  title: "福岡県 年度実績接続｜Phase 10",
  description:
    "福岡県総合計画の118目標を令和6年度実施状況へ照合し、接続済み、目標版再確認、別資料探索を分けて公開します。",
};

export const dynamic = "force-static";

const statusOrder = { linked: 0, partial: 1, not_linked: 2 } as const;

export default function FukuokaAnnualActualsPage() {
  const rows = policyTargetPages
    .flatMap((page) =>
      page.catalog.items.map((target) => ({
        initiative: page.title,
        target,
        actual: fukuokaAnnualActualForTarget(target.id),
      })),
    )
    .sort((a, b) => {
      const statusDifference =
        statusOrder[a.actual?.linkage_status ?? "not_linked"] -
        statusOrder[b.actual?.linkage_status ?? "not_linked"];
      return statusDifference || a.target.target_number - b.target.target_number;
    });

  return (
    <main id="main-content">
      <SiteHeader />
      <div className="pageShell">
        <PageIntro
          eyebrow="Phase 10 / Fukuoka annual actual linkage"
          title="118目標を、年度実績へ一件ずつ照合。"
        >
          <p>
            福岡県総合計画のReviewed目標と、公式の「令和6年度 福岡県総合計画の実施状況」を照合しました。
            指標定義と計画目標が一致したもの、同一指標でも目標値が改定されたもの、当該報告書に掲載されないものを分けています。
          </p>
          <div className={styles.introLinks}>
            <a
              href={fukuokaAnnualActualLinkage.source.url}
              target="_blank"
              rel="noreferrer"
            >
              公式実施状況PDF ↗
            </a>
            <Link href="/municipalities/phase10">全国深度マトリクス</Link>
          </div>
        </PageIntro>

        <section className={styles.summaryGrid} aria-label="福岡県年度実績接続状況">
          <article>
            <span>Reviewed目標</span>
            <strong>{fukuokaAnnualActualLinkage.target_count}</strong>
            <p>Phase 9で原文・当初値・目標値を確認した目標です。</p>
          </article>
          <article data-status="linked">
            <span>年度実績へ接続</span>
            <strong>{fukuokaAnnualActualLinkage.summary.linked_target_count}</strong>
            <p>指標、当初値、目標値、期間を照合しました。</p>
          </article>
          <article data-status="partial">
            <span>目標版の再確認</span>
            <strong>{fukuokaAnnualActualLinkage.summary.partial_target_count}</strong>
            <p>同一指標ですが、公式報告書で目標値の改定を検出しました。</p>
          </article>
          <article data-status="not_linked">
            <span>別資料を探索</span>
            <strong>{fukuokaAnnualActualLinkage.summary.not_linked_target_count}</strong>
            <p>当該実施状況報告の数値目標表に同一指標がありません。</p>
          </article>
        </section>

        <section className={styles.boundary}>
          <div>
            <p className="eyebrow">Evidence boundary</p>
            <h2>接続と評価を分ける。</h2>
          </div>
          <div>
            <p>{fukuokaAnnualActualLinkage.boundaries.linked}</p>
            <p>{fukuokaAnnualActualLinkage.boundaries.partial}</p>
            <p>{fukuokaAnnualActualLinkage.boundaries.not_linked}</p>
          </div>
        </section>

        <section className="contentSection" aria-labelledby="fukuoka-actual-table">
          <div className={styles.sectionHeading}>
            <div>
              <p className="eyebrow">Target-level linkage</p>
              <h2 id="fukuoka-actual-table">118目標の照合結果。</h2>
            </div>
            <p>
              「目標版の再確認」は当初計画値を上書きしません。「別資料を探索」は不存在ではなく、今回の報告書では確認できない状態です。
            </p>
          </div>

          <div className={styles.tableWrap}>
            <table className={styles.actualTable}>
              <thead>
                <tr>
                  <th scope="col">No.</th>
                  <th scope="col">政策・指標</th>
                  <th scope="col">状態</th>
                  <th scope="col">実績値</th>
                  <th scope="col">実績時点</th>
                  <th scope="col">Evidence</th>
                </tr>
              </thead>
              <tbody>
                {rows.map(({ initiative, target, actual }) => {
                  const status = actual?.linkage_status ?? "not_linked";
                  return (
                    <tr key={target.id}>
                      <td>{target.target_number}</td>
                      <th scope="row">
                        <small>{initiative}</small>
                        <strong>{target.indicator_name_original}</strong>
                      </th>
                      <td>
                        <span className={styles.status} data-status={status}>
                          {fukuokaAnnualActualStatusLabel(status)}
                        </span>
                      </td>
                      <td>{actual?.actual_value_text ?? "—"}</td>
                      <td>{actual?.actual_period_text ?? "—"}</td>
                      <td>
                        {actual?.source_pdf_page ? (
                          <a
                            href={`${fukuokaAnnualActualLinkage.source.url}#page=${actual.source_pdf_page}`}
                            target="_blank"
                            rel="noreferrer"
                          >
                            PDF {actual.source_pdf_page}頁 ↗
                          </a>
                        ) : (
                          <span>別資料を探索</span>
                        )}
                        {actual?.target_version_status ===
                        "revised_target_detected" ? (
                          <small>報告書の目標値を別版として保持</small>
                        ) : null}
                        {actual?.alias_review_note ? (
                          <small>{actual.alias_review_note}</small>
                        ) : null}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </section>

        <section className="callout callout--dark">
          <div>
            <p className="eyebrow">Next linkage</p>
            <h2>20目標の別資料探索と、12目標の版確認を続ける。</h2>
            <p>
              実績接続後も政策達成評価は行いません。次に、指標ごとの予算・決算・重点事業を同じ政策系列へ接続します。
            </p>
          </div>
          <Link className="primaryAction" href="/municipalities/fukuoka-prefecture">
            福岡県ページへ
          </Link>
        </section>
      </div>
      <SiteFooter />
    </main>
  );
}
