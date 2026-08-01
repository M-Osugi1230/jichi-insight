import type { Metadata } from "next";
import Link from "next/link";

import { PageIntro } from "@/components/PageIntro";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import {
  formatThousandYen,
  miyagiMoneyStatusLabel,
  miyagiProjectMoneyLinkage,
  miyagiProjectMoneyRecords,
} from "@/lib/miyagiProjectMoney";

import styles from "./page.module.css";

export const metadata: Metadata = {
  title: "宮城県 予算・決算・事業接続｜Phase 10",
  description:
    "宮城県の令和8年度予算事業627件を令和6年度決算・実績へ照合し、同一事業系列、追加確認、前年度同一事業なしを分けて公開します。",
};

export const dynamic = "force-static";

const statusOrder = { linked: 0, partial: 1, not_linked: 2 } as const;

export default function MiyagiProjectMoneyPage() {
  const rows = [...miyagiProjectMoneyRecords].sort((a, b) => {
    const statusDifference =
      statusOrder[a.linkage_status] - statusOrder[b.linkage_status];
    return (
      statusDifference ||
      a.measure_id.localeCompare(b.measure_id, "ja") ||
      a.project_name.localeCompare(b.project_name, "ja")
    );
  });
  const summary = miyagiProjectMoneyLinkage.summary;

  return (
    <main id="main-content">
      <SiteHeader />
      <div className="pageShell">
        <PageIntro
          eyebrow="Phase 10 / Miyagi money-to-action linkage"
          title="627事業の予算と決算を、施策単位で照合。"
        >
          <p>
            宮城県の令和8年度予算事業と、令和6年度の事業別決算・実績を照合しました。
            同一施策、同一事業名、同一部局、同一担当課が確認できたものだけを同一事業系列へ接続しています。
          </p>
          <div className={styles.introLinks}>
            <a
              href={miyagiProjectMoneyLinkage.sources.budget.url}
              target="_blank"
              rel="noreferrer"
            >
              公式予算反映資料 ↗
            </a>
            <a
              href={miyagiProjectMoneyLinkage.sources.settlement.url}
              target="_blank"
              rel="noreferrer"
            >
              公式成果・決算資料 ↗
            </a>
            <Link href="/municipalities/phase10">全国深度マトリクス</Link>
          </div>
        </PageIntro>

        <section className={styles.summaryGrid} aria-label="宮城県事業金額接続状況">
          <article>
            <span>令和8年度予算事業</span>
            <strong>{miyagiProjectMoneyLinkage.record_count}</strong>
            <p>8政策・18施策の公式事業一覧です。</p>
          </article>
          <article data-status="linked">
            <span>同一事業系列へ接続</span>
            <strong>{summary.linked_record_count}</strong>
            <p>施策、名称、部局、担当課が一致しています。</p>
          </article>
          <article data-status="partial">
            <span>追加確認が必要</span>
            <strong>{summary.partial_record_count}</strong>
            <p>組織変更、施策変更、複数掲載の可能性があります。</p>
          </article>
          <article data-status="not_linked">
            <span>前年度同一事業なし</span>
            <strong>{summary.not_linked_record_count}</strong>
            <p>新規事業・改称・統合を含むため推測接続しません。</p>
          </article>
        </section>

        <section className={styles.boundary}>
          <div>
            <p className="eyebrow">Evidence boundary</p>
            <h2>金額の接続と、成果の評価を分ける。</h2>
          </div>
          <div>
            <p>
              令和8年度予算額と令和6年度決算額は異なる年度の金額です。差額を執行率、増減率、政策成果へ自動変換しません。
            </p>
            <p>
              Partialと未接続は失敗ではなく、公式資料だけでは同一事業系列を確定できない状態です。
            </p>
          </div>
        </section>

        <section className="contentSection" aria-labelledby="miyagi-money-table">
          <div className={styles.sectionHeading}>
            <div>
              <p className="eyebrow">Project-level linkage</p>
              <h2 id="miyagi-money-table">627事業の照合結果。</h2>
            </div>
            <p>
              各行から予算資料・決算資料の該当ページを確認できます。金額単位は公式資料と同じ千円です。
            </p>
          </div>

          <div className={styles.tableWrap}>
            <table className={styles.moneyTable}>
              <thead>
                <tr>
                  <th scope="col">施策</th>
                  <th scope="col">事業・担当</th>
                  <th scope="col">状態</th>
                  <th scope="col">R8予算</th>
                  <th scope="col">R6決算</th>
                  <th scope="col">Evidence</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((record) => (
                  <tr key={record.id}>
                    <td>{record.measure_id.replace("policy-measure-miyagi-", "施策")}</td>
                    <th scope="row">
                      <strong>{record.project_name}</strong>
                      <small>
                        {record.department} / {record.office}
                      </small>
                    </th>
                    <td>
                      <span className={styles.status} data-status={record.linkage_status}>
                        {miyagiMoneyStatusLabel(record.linkage_status)}
                      </span>
                    </td>
                    <td>{formatThousandYen(record.budget_amount_thousand_yen)}</td>
                    <td>{formatThousandYen(record.settlement_amount_thousand_yen)}</td>
                    <td>
                      <a
                        href={`${miyagiProjectMoneyLinkage.sources.budget.url}#page=${record.budget_pdf_page}`}
                        target="_blank"
                        rel="noreferrer"
                      >
                        予算 {record.budget_pdf_page}頁 ↗
                      </a>
                      {record.settlement_pdf_page ? (
                        <a
                          href={`${miyagiProjectMoneyLinkage.sources.settlement.url}#page=${record.settlement_pdf_page}`}
                          target="_blank"
                          rel="noreferrer"
                        >
                          決算 {record.settlement_pdf_page}頁 ↗
                        </a>
                      ) : null}
                      {record.settlement_candidates.length ? (
                        <small>候補 {record.settlement_candidates.length}件を保留</small>
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
            <h2>事業からKPI・契約・監査へつなぐ。</h2>
            <p>
              同一事業系列へ接続した238件を起点に、既存の年度実績、契約案件、監査指摘、議会記録との照合を続けます。
            </p>
          </div>
          <Link className="primaryAction" href="/municipalities/miyagi">
            宮城県ページへ
          </Link>
        </section>
      </div>
      <SiteFooter />
    </main>
  );
}
