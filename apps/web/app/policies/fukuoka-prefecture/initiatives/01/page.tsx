import type { Metadata } from "next";
import Link from "next/link";

import { PageIntro } from "@/components/PageIntro";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { StatusBadge } from "@/components/StatusBadge";
import {
  formatTargetValue,
  initiative01TargetCatalog,
  initiative01TargetEvidence,
  initiative01TargetStats,
  targetScopeLabel,
} from "@/lib/policyTargets";

import styles from "./page.module.css";

export const metadata: Metadata = {
  title: "次代を担う「人財」の育成｜数値目標",
  description:
    "福岡県総合計画の取組1に設定された10の数値目標を、基準値、目標値、期間、実績未接続状態とともに確認できます。",
};

export default function Initiative01Page() {
  const catalog = initiative01TargetCatalog;

  return (
    <main>
      <SiteHeader />
      <div className="pageShell">
        <PageIntro eyebrow="Policy initiative 01" title="次代を担う「人財」の育成">
          <p>
            福岡県総合計画の数値目標PDFに掲載された10指標を、原文のまま構造化しています。
            基準値と目標値は確認済みですが、2022〜2024年度の実績値とはまだ接続していません。
          </p>
          <Link href="/policies">4方向・30取組へ戻る</Link>
        </PageIntro>

        <section className={styles.summaryGrid} aria-label="数値目標の整備状況">
          <article className={styles.summaryCard}>
            <span>Reviewed数値目標</span>
            <strong>{initiative01TargetStats.reviewedTargets}</strong>
            <p>公式PDFの指標1から10まで。</p>
          </article>
          <article className={styles.summaryCard}>
            <span>年度実績へ接続済み</span>
            <strong>{initiative01TargetStats.actualsLinked}</strong>
            <p>実績値を確認するまで0件を維持。</p>
          </article>
          <article className={styles.summaryCard}>
            <span>評価済み</span>
            <strong>{initiative01TargetStats.assessed}</strong>
            <p>基準値と目標値だけでは達成度を評価しません。</p>
          </article>
        </section>

        <section className="contentSection">
          <p className="eyebrow">Baseline and target</p>
          <h2>基準値と目標値を、期間単位まで分けて見る。</h2>
          <a
            className={styles.sourceLink}
            href={catalog.source_document_url}
            target="_blank"
            rel="noreferrer"
          >
            公式数値目標PDF・印刷ページ{catalog.printed_page}を開く ↗
          </a>

          <div className={styles.targetGrid}>
            {catalog.items.map((target) => {
              const mixedScopes = target.components.some(
                (component) => component.baseline_scope !== component.target_scope,
              );
              return (
                <article className={styles.targetCard} key={target.id}>
                  <div className={styles.number}>{String(target.target_number).padStart(2, "0")}</div>
                  <div>
                    <div className={styles.targetHeader}>
                      <div>
                        <p>{target.submeasure_title_original}</p>
                        <h3>{target.indicator_name_original}</h3>
                      </div>
                      <StatusBadge label="Reviewed" tone="verified" />
                    </div>

                    <div className={styles.componentGrid}>
                      {target.components.map((component) => (
                        <div className={styles.component} key={component.label ?? "main"}>
                          <p>{component.label ?? "指標値"}</p>
                          <div className={styles.values}>
                            <div>
                              <span>基準値</span>
                              <strong>{formatTargetValue(component.baseline_value, component.baseline_unit)}</strong>
                              <small>{component.baseline_period}・{targetScopeLabel(component.baseline_scope)}</small>
                            </div>
                            <div>
                              <span>目標値</span>
                              <strong>{formatTargetValue(component.target_value, component.target_unit)}</strong>
                              <small>{component.target_period}・{targetScopeLabel(component.target_scope)}</small>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                  <p className={styles.warning}>
                    {mixedScopes
                      ? "基準値と目標値の集計期間が異なります。年次値と5年間累計をそのまま達成率へ変換しません。"
                      : "年度実績は未接続です。目標値との差や達成率はまだ算出していません。"}
                  </p>
                </article>
              );
            })}
          </div>
        </section>

        <section className={`contentSection ${styles.boundary}`}>
          <div>
            <p className="eyebrow">Evaluation boundary</p>
            <h2>目標を設定したことと、成果を上げたことは別です。</h2>
          </div>
          <ul>
            <li>2022年度から2024年度の各指標実績</li>
            <li>指標定義・集計方法の年度変更</li>
            <li>目標との差が生じた理由</li>
            <li>関連する事業・予算・契約</li>
            <li>目標達成と政策効果の因果関係</li>
          </ul>
        </section>

        <section className="callout callout--dark">
          <div>
            <p className="eyebrow">Next link</p>
            <h2>次は10指標へ、年度別実績と公式説明を接続する。</h2>
            <p>{initiative01TargetEvidence.open_questions.join(" ")}</p>
          </div>
        </section>
      </div>
      <SiteFooter />
    </main>
  );
}
