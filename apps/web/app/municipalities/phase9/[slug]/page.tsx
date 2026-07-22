import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { PageIntro } from "@/components/PageIntro";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { StatusBadge } from "@/components/StatusBadge";
import {
  loadPhase9Catalog,
  loadPhase9Summary,
  phase9SourceLocation,
} from "@/lib/phase9Targets";

import styles from "../phase9.module.css";

const GENERATION_PENDING_SLUG = "generation-pending";

export const dynamic = "force-static";
export const dynamicParams = false;

export function generateStaticParams() {
  const params = loadPhase9Summary().records.map((record) => ({ slug: record.slug }));
  return params.length > 0 ? params : [{ slug: GENERATION_PENDING_SLUG }];
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const catalog = loadPhase9Catalog(slug);
  if (!catalog) {
    return {
      title: slug === GENERATION_PENDING_SLUG ? "Phase 9｜Reviewedデータ生成中" : "Phase 9 Reviewed目標",
      robots: slug === GENERATION_PENDING_SLUG ? { index: false, follow: false } : undefined,
    };
  }
  return {
    title: `${catalog.name}｜主要数値目標Reviewed`,
    description: `${catalog.name}の主要数値目標${catalog.reviewed_target_statement_count}件を、公式資料の原文・資料位置・Evidenceとともに公開します。`,
  };
}

export default async function Phase9PrefecturePage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const catalog = loadPhase9Catalog(slug);

  if (!catalog) {
    if (slug !== GENERATION_PENDING_SLUG) {
      notFound();
    }
    return (
      <main id="main-content">
        <SiteHeader />
        <div className="pageShell">
          <PageIntro
            eyebrow="Phase 9 data generation"
            title="38県のReviewedデータを検証しています。"
          >
            <p>
              公式資料の原文、資料位置、文書ハッシュ、比較可能性境界を確認した後に公開します。
              入口索引だけをReviewedとして表示することはありません。
            </p>
            <div className={styles.introLinks}>
              <Link href="/municipalities/phase9">Phase 9の公開状況へ戻る</Link>
              <Link href="/methodology">抽出・評価方法を確認する</Link>
            </div>
          </PageIntro>
          <section className="contentSection">
            <div className={styles.emptyState}>
              <StatusBadge label="生成検証中" tone="neutral" />
              <p>
                38県すべてのEvidence整合性と静的ページ出力が完了すると、県別ページへ自動的に置き換わります。
              </p>
            </div>
          </section>
        </div>
        <SiteFooter />
      </main>
    );
  }

  return (
    <main id="main-content">
      <SiteHeader />
      <div className="pageShell">
        <PageIntro
          eyebrow={`Phase 9 / ${catalog.prefecture_code}`}
          title={`${catalog.name}の目標原文を、資料位置から確かめる。`}
        >
          <p>
            {catalog.plan_title}（{catalog.plan_period}）の公式数値目標資料から、
            明示的な数値目標行をReviewed化しました。原文の数値を独自の達成率や
            評価点へ変換せず、比較可能性が確認できるまでランキング対象外とします。
          </p>
          <div className={styles.introLinks}>
            <Link href="/municipalities/phase9">Phase 9の38県一覧へ戻る</Link>
            <a href={catalog.source_url} target="_blank" rel="noreferrer">
              公式の数値目標入口を開く ↗
            </a>
          </div>
        </PageIntro>

        <section className={styles.summaryGrid} aria-label={`${catalog.name}のReviewed状況`}>
          <article>
            <span>Reviewed目標原文</span>
            <strong>{catalog.reviewed_target_statement_count}</strong>
            <p>表と本文の明示的な数値目標行を保持します。</p>
          </article>
          <article>
            <span>Evidence Packet</span>
            <strong>{catalog.evidence_packet_count}</strong>
            <p>目標原文と資料位置を1対1で接続します。</p>
          </article>
          <article>
            <span>公式文書</span>
            <strong>{catalog.documents.length}</strong>
            <p>最終URLとSHA-256を記録した取得文書です。</p>
          </article>
          <article>
            <span>政策評価</span>
            <strong>0</strong>
            <p>Reviewedは政策達成判定を意味しません。</p>
          </article>
        </section>

        <section className={styles.catalogMeta}>
          <div>
            <p className="eyebrow">Plan and source boundary</p>
            <h2>現行計画と旧計画を、同じ時系列へ混ぜない。</h2>
            <p>{catalog.records[0]?.plan_history_boundary}</p>
          </div>
          <dl>
            <div>
              <dt>現行計画</dt>
              <dd>{catalog.plan_title}</dd>
            </div>
            <div>
              <dt>計画期間</dt>
              <dd>{catalog.plan_period}</dd>
            </div>
            <div>
              <dt>数値目標資料</dt>
              <dd>{catalog.source_title}</dd>
            </div>
            <div>
              <dt>比較状態</dt>
              <dd>定義照合前のため全件ランキング対象外</dd>
            </div>
          </dl>
        </section>

        <section className="contentSection" aria-labelledby="reviewed-target-statements">
          <div className={styles.sectionHeading}>
            <div>
              <p className="eyebrow">Evidence-backed statements</p>
              <h2 id="reviewed-target-statements">
                {catalog.reviewed_target_statement_count}件の目標原文とEvidence。
              </h2>
            </div>
            <p>
              単位・母集団・期間が行内に書かれていない場合は不明のまま表示します。
              複数の数値がある行を一つの系列へ推測統合しません。
            </p>
          </div>

          <div className={styles.recordList}>
            {catalog.records.map((record) => (
              <details className={styles.recordCard} key={record.id}>
                <summary>
                  <span>#{String(record.display_order).padStart(4, "0")}</span>
                  <strong>{record.indicator_name_original}</strong>
                  <em>Reviewed / Not comparable</em>
                </summary>
                <div className={styles.recordBody}>
                  <p className={styles.originalText}>{record.target_statement_original}</p>
                  <dl className={styles.recordFacts}>
                    <div>
                      <dt>数値表記</dt>
                      <dd>{record.numeric_tokens_original.join(" / ")}</dd>
                    </div>
                    <div>
                      <dt>期間表記</dt>
                      <dd>{record.period_tokens_original.join(" / ") || "行内記載なし"}</dd>
                    </div>
                    <div>
                      <dt>単位</dt>
                      <dd>{record.unit_original ?? "行内記載なし"}</dd>
                    </div>
                    <div>
                      <dt>母集団</dt>
                      <dd>{record.population_scope_original ?? "行内記載なし"}</dd>
                    </div>
                    <div>
                      <dt>資料位置</dt>
                      <dd>{phase9SourceLocation(record)}</dd>
                    </div>
                    <div>
                      <dt>Evidence ID</dt>
                      <dd>{record.evidence_id}</dd>
                    </div>
                    <div>
                      <dt>取得文書</dt>
                      <dd>
                        <a href={record.source_document_url} target="_blank" rel="noreferrer">
                          {record.source_document_title} ↗
                        </a>
                      </dd>
                    </div>
                    <div>
                      <dt>比較対象外の理由</dt>
                      <dd>{record.comparability.reasons.join(" / ")}</dd>
                    </div>
                  </dl>
                </div>
              </details>
            ))}
          </div>

          <p className={styles.notice}>
            このページは公式資料の目標原文と所在を確認するためのものです。
            年度実績との定義照合、予算・事業・契約との接続、政策達成の評価は別工程です。
          </p>
        </section>
      </div>
      <SiteFooter />
    </main>
  );
}
