import type { Metadata } from "next";
import Link from "next/link";

import { PageIntro } from "@/components/PageIntro";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import {
  actualDisplay,
  hokkaidoAnnualActualLinkage,
  hokkaidoAnnualActualRecords,
  hokkaidoStatusLabel,
  partialReasonLabel,
} from "@/lib/hokkaidoAnnualActuals";

import styles from "./page.module.css";

export const metadata: Metadata = {
  title: "北海道 108指標の年度実績接続｜Phase 10",
  description:
    "北海道総合計画の108指標を令和6年度推進状況へ照合し、年度実績へ接続した指標と版・定義変更を分けて公開します。",
};

export const dynamic = "force-static";

export default function HokkaidoAnnualActualsPage() {
  const summary = hokkaidoAnnualActualLinkage.summary;
  const records = [...hokkaidoAnnualActualRecords].sort(
    (a, b) =>
      Number(a.linkage_status === "partial") -
        Number(b.linkage_status === "partial") ||
      a.indicator_number - b.indicator_number,
  );

  return (
    <main id="main-content">
      <SiteHeader />
      <div className="pageShell">
        <PageIntro
          eyebrow="Phase 10 / Hokkaido annual actuals"
          title="108指標を、公式番号で年度実績へ接続。"
        >
          <p>
            北海道総合計画のReviewed指標と、令和6年度推進状況に掲載された公式指標番号1〜108を照合しました。番号だけでは接続せず、指標名、単位、構成系列、目標版の整合を確認しています。
          </p>
          <div className={styles.introLinks}>
            {hokkaidoAnnualActualLinkage.source_urls.map((url, index) => (
              <a key={url} href={url} target="_blank" rel="noreferrer">
                基本方向{index + 1}の公式資料 ↗
              </a>
            ))}
            <Link href="/municipalities/hokkaido">北海道ページ</Link>
          </div>
        </PageIntro>

        <section className={styles.summaryGrid} aria-label="北海道年度実績接続の集計">
          <article>
            <span>Reviewed指標</span>
            <strong>{hokkaidoAnnualActualLinkage.indicator_count}</strong>
            <p>公式番号1〜108を欠落・重複なく管理。</p>
          </article>
          <article data-status="linked">
            <span>年度実績へ接続</span>
            <strong>{summary.linked_record_count}</strong>
            <p>指標名、単位、構成系列、目標版が整合。</p>
          </article>
          <article data-status="partial">
            <span>接続保留</span>
            <strong>{summary.partial_record_count}</strong>
            <p>指標改定・目標版変更・系列構成変更を確認。</p>
          </article>
          <article>
            <span>政策達成判定</span>
            <strong>0</strong>
            <p>実績値の接続と、達成・未達の判断を分離。</p>
          </article>
        </section>

        <section className={styles.boundary}>
          <div>
            <p className="eyebrow">Evidence boundary</p>
            <h2>同じ番号でも、定義が違えばつながない。</h2>
          </div>
          <div>
            <p>
              15件は、現行カタログとの目標版、指標定義、番号体系、構成系列の違いを確認したためPartialに留めています。
            </p>
            <p>
              実績が掲載されていても、目標値との単純比較から政策の成功・失敗や都道府県ランキングを生成しません。
            </p>
          </div>
        </section>

        <section className="contentSection" aria-labelledby="hokkaido-actual-table">
          <div className={styles.sectionHeading}>
            <div>
              <p className="eyebrow">Indicator-level evidence</p>
              <h2 id="hokkaido-actual-table">108指標の照合結果。</h2>
            </div>
            <p>
              実績時点は資料に記載された測定年・年度を保持しています。令和6年度資料に古い測定年の値が掲載される場合も、令和6年度値へ置き換えません。
            </p>
          </div>

          <div className={styles.tableWrap}>
            <table className={styles.actualTable}>
              <thead>
                <tr>
                  <th scope="col">No.</th>
                  <th scope="col">指標</th>
                  <th scope="col">状態</th>
                  <th scope="col">最新実績</th>
                  <th scope="col">測定時点</th>
                  <th scope="col">Evidence</th>
                </tr>
              </thead>
              <tbody>
                {records.map((record) => (
                  <tr key={record.id}>
                    <td>{record.indicator_number}</td>
                    <th scope="row">
                      <strong>{record.indicator_name}</strong>
                      {record.linkage_status === "partial" ? (
                        <small>{partialReasonLabel(record.partial_reason)}</small>
                      ) : null}
                    </th>
                    <td>
                      <span className={styles.status} data-status={record.linkage_status}>
                        {hokkaidoStatusLabel(record.linkage_status)}
                      </span>
                    </td>
                    <td>{actualDisplay(record)}</td>
                    <td>{record.actual_period_text || "—"}</td>
                    <td>
                      <a
                        href={`${hokkaidoAnnualActualLinkage.source_urls[record.source_number - 1]}#page=${record.pdf_page}`}
                        target="_blank"
                        rel="noreferrer"
                      >
                        公式資料 {record.pdf_page}頁 ↗
                      </a>
                      {record.related_source_locations.length > 1 ? (
                        <small>再掲を含む掲載箇所 {record.related_source_locations.length}件</small>
                      ) : null}
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
            <h2>基本評価調書の事務事業を、予算・決算へ接続する。</h2>
            <p>
              年度実績へ接続した93指標を起点に、施策を構成する事務事業、令和8年度予算、令和6年度決算、監査記録の共通ID化へ進みます。
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
