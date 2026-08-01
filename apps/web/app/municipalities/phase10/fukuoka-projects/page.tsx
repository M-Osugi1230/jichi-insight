import type { Metadata } from "next";
import Link from "next/link";

import { PageIntro } from "@/components/PageIntro";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import {
  formatProjectCost,
  fukuokaProjectLinkage,
  fukuokaProjectLinkageRecords,
  projectStatusLabel,
} from "@/lib/fukuokaProjectLinkage";

import styles from "./page.module.css";

export const metadata: Metadata = {
  title: "福岡県 重点事業・予算・決算候補接続｜Phase 10",
  description:
    "福岡県の既存重点事業266件を、令和8年度予算、令和6年度決算、総合計画118目標へ保守的に照合した候補台帳です。",
};

export const dynamic = "force-static";

const order = { linked: 0, partial: 1, not_linked: 2 } as const;

export default function FukuokaProjectLinkagePage() {
  const rows = [...fukuokaProjectLinkageRecords].sort(
    (a, b) =>
      order[a.linkage_status] - order[b.linkage_status] ||
      a.evaluation_number - b.evaluation_number,
  );
  const summary = fukuokaProjectLinkage.summary;

  return (
    <main id="main-content">
      <SiteHeader />
      <div className="pageShell">
        <PageIntro
          eyebrow="Phase 10 / Fukuoka project linkage candidates"
          title="266重点事業を、予算・決算・118目標へ照合。"
        >
          <p>
            令和7年度行政評価に掲載された既存重点事業266件を正本に、令和8年度予算、令和6年度決算、総合計画のReviewed目標を照合しました。名称一致だけでは同一事業と確定せず、候補と未接続を分けて公開します。
          </p>
          <div className={styles.introLinks}>
            <a href={fukuokaProjectLinkage.sources.evaluation} target="_blank" rel="noreferrer">
              行政評価概要 ↗
            </a>
            <a href={fukuokaProjectLinkage.sources.budget} target="_blank" rel="noreferrer">
              令和8年度予算 ↗
            </a>
            <a href={fukuokaProjectLinkage.sources.settlement} target="_blank" rel="noreferrer">
              令和6年度決算 ↗
            </a>
            <Link href="/municipalities/phase10/fukuoka-actuals">118目標の実績接続</Link>
          </div>
        </PageIntro>

        <section className={styles.summaryGrid} aria-label="福岡県事業接続候補の集計">
          <article>
            <span>行政評価対象事業</span>
            <strong>{fukuokaProjectLinkage.record_count}</strong>
            <p>担当組織、事業費、指標、見直し方向を収録。</p>
          </article>
          <article data-status="linked">
            <span>完全名称一致候補</span>
            <strong>{summary.linked_record_count}</strong>
            <p>予算・決算の双方で完全事業名が一意に存在。</p>
          </article>
          <article data-status="partial">
            <span>追加確認が必要</span>
            <strong>{summary.partial_record_count}</strong>
            <p>予算、決算、目標のいずれかに候補があります。</p>
          </article>
          <article data-status="not_linked">
            <span>金額資料への接続なし</span>
            <strong>{summary.not_linked_record_count}</strong>
            <p>改称、新規、統合の可能性を推測接続しません。</p>
          </article>
        </section>

        <section className={styles.boundary}>
          <div>
            <p className="eyebrow">Evidence boundary</p>
            <h2>候補は、完成済みの接続ではない。</h2>
          </div>
          <div>
            <p>
              完全名称一致候補も、担当課、総合計画上の取組、対象年度が一致するまで県全体のLinked件数に加算しません。
            </p>
            <p>
              令和7年度の行政評価事業費、令和8年度予算、令和6年度決算は別年度・別役割の金額です。差額を執行率や政策成果へ変換しません。
            </p>
          </div>
        </section>

        <section className="contentSection" aria-labelledby="fukuoka-project-table">
          <div className={styles.sectionHeading}>
            <div>
              <p className="eyebrow">Project-level candidates</p>
              <h2 id="fukuoka-project-table">266事業の照合結果。</h2>
            </div>
            <p>
              17目標で行政評価の成果指標と総合計画の指標名が完全一致しましたが、事業と目標の因果関係は評価していません。
            </p>
          </div>

          <div className={styles.tableWrap}>
            <table className={styles.projectTable}>
              <thead>
                <tr>
                  <th scope="col">No.</th>
                  <th scope="col">事業・担当</th>
                  <th scope="col">R7事業費</th>
                  <th scope="col">状態</th>
                  <th scope="col">目標候補</th>
                  <th scope="col">Evidence</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((record) => (
                  <tr key={record.id}>
                    <td>{record.evaluation_number}</td>
                    <th scope="row">
                      <strong>{record.project_name}</strong>
                      <small>{record.department_office}</small>
                      <small>{record.direction}</small>
                    </th>
                    <td>{formatProjectCost(record.fy2025_project_cost_thousand_yen)}</td>
                    <td>
                      <span className={styles.status} data-status={record.linkage_status}>
                        {projectStatusLabel(record.linkage_status)}
                      </span>
                    </td>
                    <td>
                      {record.target_matches.length ? (
                        record.target_matches.map((match) => (
                          <small key={match.target_id}>{match.indicator_name}</small>
                        ))
                      ) : (
                        <span>—</span>
                      )}
                    </td>
                    <td>
                      <a
                        href={`${fukuokaProjectLinkage.sources.evaluation}#page=${record.evaluation_summary_pdf_page}`}
                        target="_blank"
                        rel="noreferrer"
                      >
                        評価 {record.evaluation_summary_pdf_page}頁 ↗
                      </a>
                      {record.budget_matches.map((match) => (
                        <a
                          key={`budget-${match.pdf_page}`}
                          href={`${fukuokaProjectLinkage.sources.budget}#page=${match.pdf_page}`}
                          target="_blank"
                          rel="noreferrer"
                        >
                          予算 {match.pdf_page}頁 ↗
                        </a>
                      ))}
                      {record.settlement_matches.map((match) => (
                        <a
                          key={`settlement-${match.pdf_page}`}
                          href={`${fukuokaProjectLinkage.sources.settlement}#page=${match.pdf_page}`}
                          target="_blank"
                          rel="noreferrer"
                        >
                          決算 {match.pdf_page}頁 ↗
                        </a>
                      ))}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className="callout callout--dark">
          <div>
            <p className="eyebrow">Next review</p>
            <h2>108候補を、担当課・取組・年度で確認する。</h2>
            <p>
              完全一致候補とPartial候補を優先し、118目標、重点事業、予算・決算を同一IDへ昇格できるものだけを順次確定します。
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
