import type { Metadata } from "next";
import Link from "next/link";

import { PageIntro } from "@/components/PageIntro";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import {
  seriesActualDisplay,
  tokyoChildrenAnnualActualLinkage,
  tokyoChildrenAnnualActualRecords,
  tokyoChildrenStatusLabel,
  tokyoConflictLabel,
} from "@/lib/tokyoChildrenActuals";

import styles from "./page.module.css";

export const metadata: Metadata = {
  title: "東京都 子供分野8目標の年度実績接続｜Phase 10",
  description:
    "2050東京戦略の子供分野8目標を政策レビューへ照合し、年度実績へ接続した目標と文書間の値・期間差を分けて公開します。",
};

export const dynamic = "force-static";

export default function TokyoChildrenAnnualActualsPage() {
  const summary = tokyoChildrenAnnualActualLinkage.summary;
  const records = [...tokyoChildrenAnnualActualRecords].sort(
    (a, b) =>
      Number(a.linkage_status === "partial") -
        Number(b.linkage_status === "partial") ||
      a.target_group_number - b.target_group_number,
  );

  return (
    <main id="main-content">
      <SiteHeader />
      <div className="pageShell">
        <PageIntro
          eyebrow="Phase 10 / Tokyo children annual actuals"
          title="子供分野8目標を、同じ戦略内の政策レビューへ接続。"
        >
          <p>
            2050東京戦略の令和8年1月政策目標一覧と、2025年8月政策レビューを照合しました。旧「未来の東京」戦略の実績は混ぜず、目標系列、値、測定期間が一致したものだけを接続しています。
          </p>
          <div className={styles.introLinks}>
            <a
              href={tokyoChildrenAnnualActualLinkage.target_source_url}
              target="_blank"
              rel="noreferrer"
            >
              政策目標一覧 ↗
            </a>
            <a
              href={tokyoChildrenAnnualActualLinkage.review_source_url}
              target="_blank"
              rel="noreferrer"
            >
              政策レビュー ↗
            </a>
            <Link href="/municipalities/tokyo">東京都ページ</Link>
          </div>
        </PageIntro>

        <section className={styles.summaryGrid} aria-label="東京都子供分野の年度実績接続状況">
          <article>
            <span>Reviewed目標</span>
            <strong>{tokyoChildrenAnnualActualLinkage.target_group_count}</strong>
            <p>子供分野8目標・9系列を対象。</p>
          </article>
          <article data-status="linked">
            <span>年度実績へ接続</span>
            <strong>{summary.linked_target_group_count}</strong>
            <p>{summary.linked_series_count}系列で値と測定期間を確認。</p>
          </article>
          <article data-status="partial">
            <span>接続保留</span>
            <strong>{summary.partial_target_group_count}</strong>
            <p>文書間で実績値または期間が一致しません。</p>
          </article>
          <article>
            <span>政策達成判定</span>
            <strong>0</strong>
            <p>実績の接続と、達成・未達の判断を分離。</p>
          </article>
        </section>

        <section className={styles.boundary}>
          <div>
            <p className="eyebrow">Evidence boundary</p>
            <h2>同じ戦略でも、文書の時点差を上書きしない。</h2>
          </div>
          <div>
            <p>
              「ライフプラン教育」は政策レビューが2023年度実績、目標一覧が2024年度です。「障害児・医療的ケア児受入」は44自治体・2023年と47自治体・2024年で異なります。
            </p>
            <p>
              2目標はどちらかの値を正解として上書きせず、Partialとして文書版と測定時点を保持しています。
            </p>
          </div>
        </section>

        <section className="contentSection" aria-labelledby="tokyo-children-table">
          <div className={styles.sectionHeading}>
            <div>
              <p className="eyebrow">Target-level evidence</p>
              <h2 id="tokyo-children-table">8目標の照合結果。</h2>
            </div>
            <p>
              2025年政策レビューに掲載された2022〜2025年の測定値を、そのままの期間で保持しています。
            </p>
          </div>

          <div className={styles.tableWrap}>
            <table className={styles.actualTable}>
              <thead>
                <tr>
                  <th scope="col">No.</th>
                  <th scope="col">政策目標</th>
                  <th scope="col">状態</th>
                  <th scope="col">接続した実績</th>
                  <th scope="col">文書差・Evidence</th>
                </tr>
              </thead>
              <tbody>
                {records.map((record) => (
                  <tr key={record.id}>
                    <td>{record.target_group_number}</td>
                    <th scope="row">
                      <strong>{record.target_name}</strong>
                      {record.partial_reason ? (
                        <small>{tokyoConflictLabel(record.partial_reason)}</small>
                      ) : null}
                    </th>
                    <td>
                      <span className={styles.status} data-status={record.linkage_status}>
                        {tokyoChildrenStatusLabel(record.linkage_status)}
                      </span>
                    </td>
                    <td>
                      {record.linked_series.length ? (
                        record.linked_series.map((series) => (
                          <small key={series.series_id}>{seriesActualDisplay(series)}</small>
                        ))
                      ) : (
                        <span>接続保留</span>
                      )}
                    </td>
                    <td>
                      {record.conflict
                        ? Object.entries(record.conflict).map(([key, value]) => (
                            <small key={key}>{key}: {value}</small>
                          ))
                        : null}
                      <a
                        href={`${tokyoChildrenAnnualActualLinkage.review_source_url}#page=${record.source_pdf_page}`}
                        target="_blank"
                        rel="noreferrer"
                      >
                        政策レビュー {record.source_pdf_page}頁 ↗
                      </a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className="callout callout--dark">
          <div>
            <p className="eyebrow">Next linkage</p>
            <h2>残る政策分野を、同じ版管理で接続する。</h2>
            <p>
              子供分野で確立した文書版・値・測定期間のゲートを、2050東京戦略の残る政策目標へ展開します。
            </p>
          </div>
          <Link className="primaryAction" href="/municipalities/phase10">
            全国深度マトリクスへ
          </Link>
        </section>
      </div>
      <SiteFooter />
    </main>
  );
}
