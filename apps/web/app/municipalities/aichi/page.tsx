import type { Metadata } from "next";
import Link from "next/link";

import { AichiIndicatorExplorer } from "@/components/AichiIndicatorExplorer";
import { PageIntro } from "@/components/PageIntro";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { StatusBadge } from "@/components/StatusBadge";
import {
  aichiPolicyIndicatorStats,
  aichiPolicySources,
} from "@/lib/aichiIndicators";

import styles from "./page.module.css";

export const metadata: Metadata = {
  title: "愛知県｜あいちビジョン2030の進捗管理指標",
  description:
    "あいちビジョン2030の進捗管理指標56件・62系列を、策定時、現状、進捗目標、Evidenceとともに公開します。",
};

export default function AichiPage() {
  return (
    <main id="main-content">
      <SiteHeader />
      <div className="pageShell">
        <PageIntro eyebrow="Aichi progress indicators" title="愛知県の目標と年次現状値を、定義を変えずに読む。">
          <p>
            「あいちレポート2025」の進捗管理指標
            {aichiPolicyIndicatorStats.indicatorRows}件・
            {aichiPolicyIndicatorStats.indicatorSeries}系列を、
            2024-2026実施計画の進捗目標と照合しました。
            Reviewedは抽出と根拠確認の完了を示し、政策成果の独自評価ではありません。
          </p>
          <div className={styles.introLinks}>
            <Link href="/municipalities">全国47都道府県へ戻る</Link>
            <a
              href="https://www.pref.aichi.jp/soshiki/kikaku/2025vision-report.html"
              target="_blank"
              rel="noreferrer"
            >
              公式の年次レポートを開く ↗
            </a>
          </div>
        </PageIntro>

        <section className={styles.summaryGrid} aria-label="愛知県進捗指標の公開状況">
          <article>
            <span>Reviewed指標行</span>
            <strong>{aichiPolicyIndicatorStats.indicatorRows}</strong>
            <p>基本目標と10の政策方向。再掲2件を含みます。</p>
          </article>
          <article>
            <span>指標系列</span>
            <strong>{aichiPolicyIndicatorStats.indicatorSeries}</strong>
            <p>男女別・水質別などの複数系列を統合しません。</p>
          </article>
          <article>
            <span>現状値接続</span>
            <strong>{aichiPolicyIndicatorStats.currentLinkedSeries}</strong>
            <p>2025年次レポート掲載の現状値。欠損1系列も保持。</p>
          </article>
          <article>
            <span>Evidence Packet</span>
            <strong>{aichiPolicyIndicatorStats.evidencePackets}</strong>
            <p>指標名、策定時、現状、目標、資料位置を1対1で記録。</p>
          </article>
        </section>

        <section className={styles.boundarySection}>
          <div>
            <p className="eyebrow">Data boundaries</p>
            <h2>同じ表にあっても、同じ意味とは限らない。</h2>
          </div>
          <div className={styles.boundaryGrid}>
            <article>
              <strong>再掲</strong>
              <p>{aichiPolicyIndicatorStats.repostIndicators}件は別の政策方向にも掲載されますが、県全体の固有指標数では重複集計しません。</p>
            </article>
            <article>
              <strong>目標改定</strong>
              <p>ICT活用指導力の目標は、2025年度100％から2026年度100％程度へ更新された履歴を残します。</p>
            </article>
            <article>
              <strong>評価単位</strong>
              <p>管理事業評価{aichiPolicyIndicatorStats.managementProjects}事業は、ビジョン指標とは別の評価単位です。</p>
            </article>
            <article>
              <strong>独自判定</strong>
              <p>政策評価済みは{aichiPolicyIndicatorStats.policyAssessments}件です。達成率や優劣を独自計算しません。</p>
            </article>
          </div>
        </section>

        <section className="contentSection" aria-labelledby="aichi-all-indicators">
          <div className={styles.sectionHeading}>
            <div>
              <p className="eyebrow">Reviewed indicators</p>
              <h2 id="aichi-all-indicators">56指標を、政策方向・値・年度から探す。</h2>
            </div>
            <p>
              多年平均、累計、下限・上限、概数、定性値、欠損、定義変更を原文の意味のまま表示します。
            </p>
          </div>
          <AichiIndicatorExplorer />
        </section>

        <section className={styles.sourceSection} aria-labelledby="aichi-sources">
          <div>
            <p className="eyebrow">Official sources</p>
            <h2 id="aichi-sources">計画、年次進捗、事業評価、予算を分ける。</h2>
            <p>
              年次レポートの現状値は指標へ接続しましたが、296管理事業の評価結果や公共事業評価を
              指標の達成判定へ自動転用していません。
            </p>
          </div>
          <div className={styles.sourceList}>
            {aichiPolicySources.map((source) => (
              <article key={source.id}>
                <div>
                  <span>{source.category}</span>
                  <StatusBadge
                    label={source.review_status === "reviewed" ? "Reviewed" : "Indexed"}
                    tone={source.review_status === "reviewed" ? "verified" : "neutral"}
                  />
                </div>
                <h3>{source.title}</h3>
                <p>{source.role_note}</p>
                <a href={source.url} target="_blank" rel="noreferrer">公式資料を開く ↗</a>
              </article>
            ))}
          </div>
        </section>
      </div>
      <SiteFooter />
    </main>
  );
}
