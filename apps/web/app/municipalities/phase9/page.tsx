import type { Metadata } from "next";
import Link from "next/link";

import { PageIntro } from "@/components/PageIntro";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { StatusBadge } from "@/components/StatusBadge";
import { loadPhase9Summary } from "@/lib/phase9Targets";

import styles from "./phase9.module.css";

export const metadata: Metadata = {
  title: "Phase 9｜38県の主要数値目標Reviewed",
  description:
    "Phase 9対象38県の主要数値目標を、公式資料の原文・資料位置・Evidence・比較可能性境界とともに公開します。",
};

export const dynamic = "force-static";

export default function Phase9MunicipalitiesPage() {
  const summary = loadPhase9Summary();
  const isComplete = summary.status === "reviewed_complete";

  return (
    <main id="main-content">
      <SiteHeader />
      <div className="pageShell">
        <PageIntro
          eyebrow="Phase 9 nationwide review"
          title="38県の数値目標を、原文とEvidenceから読む。"
        >
          <p>
            Phase 8の9地域拠点を除く38県について、現行計画の主要数値目標を
            公式資料の原文行・表位置・文書ハッシュへ接続します。Reviewedは
            抽出と根拠確認の完了であり、政策の達成度や自治体の優劣を示しません。
          </p>
          <div className={styles.introLinks}>
            <Link href="/municipalities">全国47都道府県へ戻る</Link>
            <Link href="/methodology">抽出・評価方法を確認する</Link>
          </div>
        </PageIntro>

        <section className={styles.summaryGrid} aria-label="Phase 9公開状況">
          <article>
            <span>Reviewed都道府県</span>
            <strong>{summary.prefecture_count}</strong>
            <p>Phase 9対象38県。地域拠点9県とは別の全国展開です。</p>
          </article>
          <article>
            <span>Reviewed目標原文</span>
            <strong>{summary.reviewed_target_statement_count}</strong>
            <p>数値を推測で正規化せず、原資料の行・表を保持します。</p>
          </article>
          <article>
            <span>Evidence Packet</span>
            <strong>{summary.evidence_packet_count}</strong>
            <p>公開する目標原文と1対1で資料位置を記録します。</p>
          </article>
          <article>
            <span>Evidence coverage</span>
            <strong>{summary.evidence_coverage_percent}%</strong>
            <p>比較可能性未確認の指標はランキング対象外です。</p>
          </article>
        </section>

        <section className={styles.boundary}>
          <div>
            <p className="eyebrow">Review boundaries</p>
            <h2>確認できたことと、まだ判断しないことを分ける。</h2>
          </div>
          <div className={styles.boundaryGrid}>
            <article>
              <strong>原文優先</strong>
              <p>目標値、基準値、年度実績が同じ行にあっても、独自に達成率へ変換しません。</p>
            </article>
            <article>
              <strong>Evidence 1対1</strong>
              <p>文書URL、SHA-256、PDF頁・表・行またはシート位置を各レコードへ保持します。</p>
            </article>
            <article>
              <strong>比較不能を保持</strong>
              <p>単位、母集団、期間、定義が一致しない指標は、全国順位や平均へ含めません。</p>
            </article>
            <article>
              <strong>政策評価は未判定</strong>
              <p>独自の政策達成判定は{summary.policy_achievement_assessed_count}件です。</p>
            </article>
          </div>
        </section>

        <section className="contentSection" aria-labelledby="phase9-prefectures">
          <div className={styles.sectionHeading}>
            <div>
              <p className="eyebrow">Reviewed prefectures</p>
              <h2 id="phase9-prefectures">地域・計画・Evidence件数から県を選ぶ。</h2>
            </div>
            <p>
              各ページでは、抽出した目標原文、数値表記、期間、単位、母集団、
              資料位置、比較対象外の理由を確認できます。
            </p>
          </div>

          {isComplete ? (
            <div className={styles.prefectureGrid}>
              {summary.records.map((record) => (
                <article className={styles.prefectureCard} key={record.prefecture_code}>
                  <div>
                    <span>{record.prefecture_code} / {record.batch_id}</span>
                    <StatusBadge label="Reviewed" tone="verified" />
                  </div>
                  <h3>{record.name}</h3>
                  <p>{record.plan_title}（{record.plan_period}）</p>
                  <dl>
                    <div>
                      <dt>目標原文</dt>
                      <dd>{record.reviewed_target_statement_count}</dd>
                    </div>
                    <div>
                      <dt>Evidence</dt>
                      <dd>{record.evidence_packet_count}</dd>
                    </div>
                  </dl>
                  <Link href={record.route}>{record.name}の目標原文を見る →</Link>
                </article>
              ))}
            </div>
          ) : (
            <div className={styles.emptyState}>
              <StatusBadge label="生成検証中" tone="neutral" />
              <p>
                Reviewedデータ生成後に38県の一覧を表示します。入口索引だけを
                Reviewedとして表示することはありません。
              </p>
            </div>
          )}
        </section>
      </div>
      <SiteFooter />
    </main>
  );
}
