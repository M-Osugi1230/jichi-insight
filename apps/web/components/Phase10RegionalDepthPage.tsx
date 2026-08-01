import Link from "next/link";

import { PageIntro } from "@/components/PageIntro";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { StatusBadge } from "@/components/StatusBadge";
import {
  regionalDepthLabels,
  type RegionalDepthReviews,
} from "@/lib/phase10RegionalDepth";

import styles from "../app/municipalities/phase10/tohoku/page.module.css";

type Props = {
  reviews: RegionalDepthReviews;
  title: string;
  description: string;
  subjectLabel: string;
  boundaryTitle: string;
  boundaries: string[];
  nextTitle: string;
  nextDescription: string;
};

export function Phase10RegionalDepthPage({
  reviews,
  title,
  description,
  subjectLabel,
  boundaryTitle,
  boundaries,
  nextTitle,
  nextDescription,
}: Props) {
  return (
    <main id="main-content">
      <SiteHeader />
      <div className="pageShell">
        <PageIntro
          eyebrow={`Phase 10 regional depth / ${reviews.batch_id}`}
          title={title}
        >
          <p>{description}</p>
          <div className={styles.introLinks}>
            <Link href="/municipalities/phase10">全国47都道府県の深度を見る</Link>
            <Link href="/municipalities/phase9">全国のReviewed目標を見る</Link>
          </div>
        </PageIntro>

        <section className={styles.summaryGrid} aria-label={`${reviews.region}バッチのレビュー状況`}>
          <article>
            <span>対象自治体</span>
            <strong>{reviews.summary.prefecture_count}</strong>
            <p>{subjectLabel}</p>
          </article>
          <article>
            <span>共通レビュー層</span>
            <strong>{reviews.summary.dimension_count}</strong>
            <p>年度実績、予算、決算、重点事業、監査。</p>
          </article>
          <article>
            <span>Reviewed公式資料</span>
            <strong>{reviews.summary.reviewed_source_count}</strong>
            <p>各自治体5件の公式資料記録です。</p>
          </article>
          <article>
            <span>政策達成判定</span>
            <strong>0</strong>
            <p>資料確認だけで達成・未達を判定しません。</p>
          </article>
        </section>

        <section className={styles.boundary}>
          <div>
            <p className="eyebrow">Review boundary</p>
            <h2>{boundaryTitle}</h2>
          </div>
          <ul>
            {boundaries.map((boundary) => (
              <li key={boundary}>{boundary}</li>
            ))}
          </ul>
        </section>

        <section className="contentSection" aria-labelledby={`${reviews.batch_id}-reviewed-evidence`}>
          <div className={styles.sectionHeading}>
            <div>
              <p className="eyebrow">Official evidence by prefecture</p>
              <h2 id={`${reviews.batch_id}-reviewed-evidence`}>
                {reviews.summary.prefecture_count}自治体×5層の公式資料と、残る接続作業。
              </h2>
            </div>
            <p>
              各資料について、確認できた役割と、まだ確認できていない接続範囲を分けて表示します。
            </p>
          </div>

          <div className={styles.prefectureGrid}>
            {reviews.records.map((record) => (
              <article className={styles.prefectureCard} key={record.prefecture_code}>
                <div className={styles.cardHeader}>
                  <span>{record.prefecture_code} / {record.region}</span>
                  <StatusBadge label="5層Reviewed" tone="verified" />
                </div>
                <h3>{record.name}</h3>
                <div className={styles.sourceList}>
                  {reviews.dimensions.map((dimension) => {
                    const source = record.sources[dimension];
                    return (
                      <div key={dimension}>
                        <strong>{regionalDepthLabels[dimension]}</strong>
                        <a href={source.url} target="_blank" rel="noreferrer">
                          {source.title} ↗
                        </a>
                        <span>{source.reporting_period}</span>
                        <p>{source.claim}</p>
                        <small>{source.boundary}</small>
                      </div>
                    );
                  })}
                </div>
                <div className={styles.nextAction}>
                  <strong>次の接続</strong>
                  <p>{record.next_linkage}</p>
                </div>
              </article>
            ))}
          </div>
        </section>

        <section className="callout callout--dark">
          <div>
            <p className="eyebrow">Next Phase 10 work</p>
            <h2>{nextTitle}</h2>
            <p>{nextDescription}</p>
          </div>
          <Link className="primaryAction" href="/municipalities/phase10">
            全国マトリクスへ戻る
          </Link>
        </section>
      </div>
      <SiteFooter />
    </main>
  );
}
