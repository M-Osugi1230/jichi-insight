import Link from "next/link";

import { PageIntro } from "@/components/PageIntro";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { StatusBadge } from "@/components/StatusBadge";
import {
  formatTargetValue,
  policyTargetStats,
  targetScopeLabel,
  type PolicyTargetPageDefinition,
} from "@/lib/policyTargets";

import styles from "./PolicyTargetDetail.module.css";

export function PolicyTargetDetail({ definition }: { definition: PolicyTargetPageDefinition }) {
  const { catalog, evidence, slug, title } = definition;
  const stats = policyTargetStats(catalog);

  return (
    <main>
      <SiteHeader />
      <div className="pageShell">
        <PageIntro eyebrow={`Policy initiative ${slug}`} title={title}>
          <p>
            福岡県総合計画の数値目標PDFに掲載された指標を、原文のまま構造化しています。
            基準値と目標値は確認済みですが、年度別の実績値とはまだ接続していません。
          </p>
          <Link href="/policies">4方向・30取組へ戻る</Link>
        </PageIntro>

        <section className={styles.summaryGrid} aria-label="数値目標の整備状況">
          <article className={styles.summaryCard}>
            <span>Reviewed数値目標</span>
            <strong>{stats.reviewedTargets}</strong>
            <p>公式PDFに掲載された指標を原文で登録。</p>
          </article>
          <article className={styles.summaryCard}>
            <span>年度実績へ接続済み</span>
            <strong>{stats.actualsLinked}</strong>
            <p>実績値を確認するまで0件を維持。</p>
          </article>
          <article className={styles.summaryCard}>
            <span>評価済み</span>
            <strong>{stats.assessed}</strong>
            <p>基準値と目標値だけでは達成度を評価しません。</p>
          </article>
        </section>

        <section className="contentSection">
          <p className="eyebrow">Baseline and target</p>
          <h2>基準値と目標値を、期間単位まで分けて見る。</h2>
          <a className={styles.sourceLink} href={catalog.source_document_url} target="_blank" rel="noreferrer">
            公式数値目標PDF・印刷ページ{catalog.printed_page}を開く ↗
          </a>

          <div className={styles.targetGrid}>
            {catalog.items.map((target) => {
              const missingBaseline = target.components.some(
                (component) => component.baseline_scope === "not_available",
              );
              const mixedScopes = target.components.some(
                (component) =>
                  component.baseline_scope !== "not_available" &&
                  component.baseline_scope !== component.target_scope,
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
                              <small>
                                {component.baseline_period ?? "期間記載なし"}・
                                {targetScopeLabel(component.baseline_scope)}
                              </small>
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
                    {missingBaseline
                      ? "当初値は公式資料でダッシュ表記です。0とは扱わず、年度実績を確認するまで達成率を算出しません。"
                      : mixedScopes
                        ? "基準値と目標値の集計期間が異なります。年次値と累計値をそのまま達成率へ変換しません。"
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
            <li>年度別の各指標実績</li>
            <li>指標定義・集計方法の年度変更</li>
            <li>目標との差が生じた理由</li>
            <li>関連する事業・予算・契約</li>
            <li>目標達成と政策効果の因果関係</li>
          </ul>
        </section>

        <section className="callout callout--dark">
          <div>
            <p className="eyebrow">Next link</p>
            <h2>次は指標へ、年度別実績と公式説明を接続する。</h2>
            <p>{evidence.open_questions.join(" ")}</p>
          </div>
        </section>
      </div>
      <SiteFooter />
    </main>
  );
}
