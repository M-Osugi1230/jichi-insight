import type { Metadata } from "next";
import Link from "next/link";

import { PageIntro } from "@/components/PageIntro";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { StatusBadge } from "@/components/StatusBadge";
import {
  loadPhase10KantoDepth,
  regionalDepthLabels,
} from "@/lib/phase10RegionalDepth";

import styles from "../tohoku/page.module.css";

export const metadata: Metadata = {
  title: "Phase 10 関東｜6県の年度実績・予算・決算・事業・監査",
  description:
    "茨城県、栃木県、群馬県、埼玉県、千葉県、神奈川県について、年度実績、予算、決算、重点事業、監査の公式資料と未接続範囲を公開します。",
};

export const dynamic = "force-static";

export default function Phase10KantoPage() {
  const reviews = loadPhase10KantoDepth();

  return (
    <main id="main-content">
      <SiteHeader />
      <div className="pageShell">
        <PageIntro
          eyebrow="Phase 10 regional depth / Kanto"
          title="関東6県も、同じ5層をReviewed化。"
        >
          <p>
            茨城県、栃木県、群馬県、埼玉県、千葉県、神奈川県について、年度実績、
            予算、決算、重点事業、監査の公式資料を確認しました。Reviewedは資料の
            内容、期間、範囲を確認した状態であり、政策目標との直接接続ではありません。
          </p>
          <div className={styles.introLinks}>
            <Link href="/municipalities/phase10">全国47都道府県の深度を見る</Link>
            <Link href="/municipalities/phase9">全国のReviewed目標を見る</Link>
          </div>
        </PageIntro>

        <section className={styles.summaryGrid} aria-label="関東バッチのレビュー状況">
          <article>
            <span>対象県</span>
            <strong>{reviews.summary.prefecture_count}</strong>
            <p>Phase 8拠点の東京都を除く関東6県です。</p>
          </article>
          <article>
            <span>共通レビュー層</span>
            <strong>{reviews.summary.dimension_count}</strong>
            <p>年度実績、予算、決算、重点事業、監査。</p>
          </article>
          <article>
            <span>Reviewed公式資料</span>
            <strong>{reviews.summary.reviewed_source_count}</strong>
            <p>各県5件、合計30件の公式資料記録です。</p>
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
            <h2>新旧計画、政策評価、公共事業評価を混同しない。</h2>
          </div>
          <ul>
            <li>千葉県の旧計画実績を現行計画目標へ自動接続しません。</li>
            <li>公共事業評価を全重点事業の代理として扱いません。</li>
            <li>予算額、決算額、事業費、契約額を別レコードで扱います。</li>
            <li>名称一致だけで同じ政策・事業とは判定しません。</li>
          </ul>
        </section>

        <section className="contentSection" aria-labelledby="kanto-reviewed-evidence">
          <div className={styles.sectionHeading}>
            <div>
              <p className="eyebrow">Official evidence by prefecture</p>
              <h2 id="kanto-reviewed-evidence">6県×5層の公式資料と、残る接続作業。</h2>
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
            <h2>関東の次は、中部8県を同じ工程で確認する。</h2>
            <p>
              新潟県、富山県、石川県、福井県、山梨県、長野県、岐阜県、静岡県について、
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
