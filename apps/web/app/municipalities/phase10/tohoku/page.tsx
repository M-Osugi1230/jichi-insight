import type { Metadata } from "next";
import Link from "next/link";

import { PageIntro } from "@/components/PageIntro";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { StatusBadge } from "@/components/StatusBadge";
import {
  loadPhase10TohokuDepth,
  regionalDepthLabels,
} from "@/lib/phase10RegionalDepth";

import styles from "./page.module.css";

export const metadata: Metadata = {
  title: "Phase 10 東北｜5県の年度実績・予算・決算・事業・監査",
  description:
    "青森県、岩手県、秋田県、山形県、福島県について、年度実績、予算、決算、重点事業、監査の公式資料と未接続範囲を公開します。",
};

export const dynamic = "force-static";

export default function Phase10TohokuPage() {
  const reviews = loadPhase10TohokuDepth();

  return (
    <main id="main-content">
      <SiteHeader />
      <div className="pageShell">
        <PageIntro
          eyebrow="Phase 10 regional depth / Tohoku"
          title="東北5県も、同じ5層をReviewed化。"
        >
          <p>
            青森県、岩手県、秋田県、山形県、福島県について、年度実績、予算、
            決算、重点事業、監査の公式資料を確認しました。Reviewedは資料の内容、
            期間、範囲を確認した状態であり、政策目標との直接接続ではありません。
          </p>
          <div className={styles.introLinks}>
            <Link href="/municipalities/phase10">全国47都道府県の深度を見る</Link>
            <Link href="/municipalities/phase9">全国のReviewed目標を見る</Link>
          </div>
        </PageIntro>

        <section className={styles.summaryGrid} aria-label="東北バッチのレビュー状況">
          <article>
            <span>対象県</span>
            <strong>{reviews.summary.prefecture_count}</strong>
            <p>Phase 8拠点の宮城県を除く東北5県です。</p>
          </article>
          <article>
            <span>共通レビュー層</span>
            <strong>{reviews.summary.dimension_count}</strong>
            <p>年度実績、予算、決算、重点事業、監査。</p>
          </article>
          <article>
            <span>Reviewed公式資料</span>
            <strong>{reviews.summary.reviewed_source_count}</strong>
            <p>各県5件、合計25件の公式資料記録です。</p>
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
            <h2>旧計画と現行計画、予算と決算を混ぜない。</h2>
          </div>
          <ul>
            <li>報告年度と測定年度を分離します。</li>
            <li>旧計画の実績を新計画の目標へ自動接続しません。</li>
            <li>予算額、決算額、事業費、契約額を別レコードで扱います。</li>
            <li>名称一致だけで同じ政策・事業とは判定しません。</li>
          </ul>
        </section>

        <section className="contentSection" aria-labelledby="tohoku-reviewed-evidence">
          <div className={styles.sectionHeading}>
            <div>
              <p className="eyebrow">Official evidence by prefecture</p>
              <h2 id="tohoku-reviewed-evidence">5県×5層の公式資料と、残る接続作業。</h2>
            </div>
            <p>
              各資料について、確認できた役割と、まだ確認できていない接続範囲を
              分けて表示します。
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
            <p className="eyebrow">Next regional batch</p>
            <h2>東北の次は、関東6県を同じ工程で確認する。</h2>
            <p>
              茨城県、栃木県、群馬県、埼玉県、千葉県、神奈川県について、
              同じ5層の公式資料確認と境界記録を行います。
            </p>
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
