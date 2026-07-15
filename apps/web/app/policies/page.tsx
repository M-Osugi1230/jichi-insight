import type { Metadata } from "next";

import { PageIntro } from "@/components/PageIntro";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { StatusBadge } from "@/components/StatusBadge";
import {
  evidenceForPolicyDirection,
  fukuokaPolicyDirections,
  policyDirectionStats,
  sourcesForPolicyDirection,
} from "@/lib/policies";

import styles from "./page.module.css";

export const metadata: Metadata = {
  title: "政策体系",
  description:
    "福岡県総合計画の4つの基本方向を、原文・順序・計画期間・根拠資料・未接続範囲とともに確認できます。",
};

export default function PoliciesPage() {
  return (
    <main>
      <SiteHeader />
      <div className="pageShell">
        <PageIntro eyebrow="Policy registry" title="政策評価の前に、計画が何を目指すかを構造化する。">
          <p>
            福岡県総合計画の公式ページで確認できる4つの基本方向を、原文のまま登録しています。
            現在は計画体系の確認段階であり、年度実績、予算、事業、公約との接続や達成度評価は行っていません。
          </p>
        </PageIntro>

        <section className={styles.summaryGrid} aria-label="政策体系の整備状況">
          <article className={styles.summaryCard}>
            <span>Reviewed基本方向</span>
            <strong>{policyDirectionStats.reviewedDirections}</strong>
            <p>福岡県総合計画の公式掲載順で登録。</p>
          </article>
          <article className={styles.summaryCard}>
            <span>年度進捗へ接続済み</span>
            <strong>{policyDirectionStats.progressLinked}</strong>
            <p>30の取組事項と数値目標への対応付けは次工程。</p>
          </article>
          <article className={styles.summaryCard}>
            <span>政策評価済み</span>
            <strong>{policyDirectionStats.assessed}</strong>
            <p>計画文だけでは成果を評価しません。</p>
          </article>
        </section>

        <section className="contentSection">
          <p className="eyebrow">Fukuoka Prefecture 2022–2026</p>
          <h2>福岡県総合計画の4つの基本方向</h2>
          <div className={styles.directionGrid}>
            {fukuokaPolicyDirections.map((direction) => {
              const sources = sourcesForPolicyDirection(direction);
              const evidence = evidenceForPolicyDirection(direction);
              return (
                <article className={styles.directionCard} key={direction.id}>
                  <div className={styles.order} aria-label={`基本方向${direction.display_order}`}>
                    {String(direction.display_order).padStart(2, "0")}
                  </div>
                  <div className={styles.directionMain}>
                    <p>Strategic direction</p>
                    <h3>{direction.title_original}</h3>
                    <p>{direction.source_location}</p>
                    {sources.map((source) => (
                      <a href={source.url} target="_blank" rel="noreferrer" key={source.id}>
                        公式計画を開く ↗
                      </a>
                    ))}
                  </div>
                  <dl className={styles.directionFacts}>
                    <div><dt>計画期間</dt><dd>{direction.plan_period_start}–{direction.plan_period_end}年度</dd></div>
                    <div><dt>レビュー</dt><dd><StatusBadge label="Reviewed" tone="verified" /></dd></div>
                    <div><dt>年度進捗</dt><dd>未接続</dd></div>
                    <div><dt>評価</dt><dd>未評価</dd></div>
                  </dl>
                  <div className={styles.questions}>
                    <p>Open questions</p>
                    <ul>
                      {evidence?.open_questions.map((question) => (
                        <li key={question}>{question}</li>
                      ))}
                    </ul>
                  </div>
                </article>
              );
            })}
          </div>
        </section>

        <section className={`contentSection ${styles.boundary}`}>
          <div>
            <p className="eyebrow">What remains</p>
            <h2>計画の方向と、実際の成果はまだ別々です。</h2>
          </div>
          <ul>
            <li>4方向の配下にある30の取組事項</li>
            <li>取組事項ごとの数値目標</li>
            <li>2022–2024年度の実績推移</li>
            <li>関連する事業・予算・契約</li>
            <li>知事公約との根拠付き対応関係</li>
            <li>未達・変更・延期に関する公式説明</li>
          </ul>
        </section>

        <section className="callout callout--dark">
          <div>
            <p className="eyebrow">Next extraction</p>
            <h2>次は30の取組事項を、4方向の下へ接続する。</h2>
            <p>
              年度実施状況報告から取組名称、数値目標、実績、課題を原文位置付きで抽出します。
              接続が完了するまでは、基本方向ごとの進捗率や評価点を表示しません。
            </p>
          </div>
        </section>
      </div>
      <SiteFooter />
    </main>
  );
}
