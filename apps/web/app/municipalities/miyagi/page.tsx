import type { Metadata } from "next";
import Link from "next/link";

import { PageIntro } from "@/components/PageIntro";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { StatusBadge } from "@/components/StatusBadge";
import {
  miyagiPolicyHierarchyStats,
  miyagiPolicySourceInventory,
  reviewedMiyagiParallelDomains,
  reviewedMiyagiPolicyDirections,
  reviewedMiyagiPolicyHierarchy,
} from "@/lib/miyagiPolicies";

import styles from "./page.module.css";

export const metadata: Metadata = {
  title: "宮城県｜政策体系",
  description:
    "新・宮城の将来ビジョンの4基本方向、8政策、18施策と、復興完了に向けた4取組分野を、公式順序と根拠資料から確認できます。",
};

export default function MiyagiPage() {
  return (
    <main>
      <SiteHeader />
      <div className="pageShell">
        <PageIntro eyebrow="Miyagi policy hierarchy" title="宮城県の政策体系を、3階層のまま読む。">
          <p>
            「新・宮城の将来ビジョン」の4つの政策推進の基本方向、8政策、18施策を一次資料と照合しました。
            復興完了に向けた4取組分野は政策番号1〜8へ混ぜず、別枠で表示します。目標指標、年度実績、県の自己評価、行政評価委員会の意見はまだ接続していません。
          </p>
          <div className={styles.introLinks}>
            <Link href="/municipalities">全国47都道府県へ戻る</Link>
            <a
              href={miyagiPolicySourceInventory.sources.find((source) => source.id === "miyagi-source-vision-entry")?.url}
              target="_blank"
              rel="noreferrer"
            >
              公式ビジョンを開く ↗
            </a>
            <a
              href={miyagiPolicySourceInventory.sources.find((source) => source.id === miyagiPolicySourceInventory.current_implementation_plan_id)?.url}
              target="_blank"
              rel="noreferrer"
            >
              現行実施計画を開く ↗
            </a>
          </div>
        </PageIntro>

        <section className={styles.summaryGrid} aria-label="宮城県政策体系のReviewed状況">
          <article className={styles.summaryCard}>
            <span>基本方向</span>
            <strong>{miyagiPolicyHierarchyStats.directions}</strong>
            <p>公式掲載順と所属政策をReviewed済み。</p>
          </article>
          <article className={styles.summaryCard}>
            <span>政策</span>
            <strong>{miyagiPolicyHierarchyStats.policies}</strong>
            <p>政策番号1〜8を重複なく登録。</p>
          </article>
          <article className={styles.summaryCard}>
            <span>施策</span>
            <strong>{miyagiPolicyHierarchyStats.measures}</strong>
            <p>施策番号1〜18を政策へ接続。</p>
          </article>
          <article className={styles.summaryCard}>
            <span>Evidence Packet</span>
            <strong>{miyagiPolicyHierarchyStats.evidencePackets}</strong>
            <p>4基本方向と復興支援別枠の根拠を保存。</p>
          </article>
        </section>

        <section className="contentSection">
          <p className="eyebrow">Reviewed hierarchy</p>
          <h2>{reviewedMiyagiPolicyHierarchy.plan_title_original}</h2>
          <p className={styles.sectionLead}>
            {reviewedMiyagiPolicyHierarchy.plan_period_original}。政策推進の基本方向、政策、施策を別階層として保持し、番号と原文を公式資料の順序から変更していません。
          </p>

          <div className={styles.directionStack}>
            {reviewedMiyagiPolicyDirections.map((direction) => (
              <article className={styles.directionCard} key={direction.id}>
                <div className={styles.directionHeader}>
                  <div>
                    <span className={styles.directionNumber}>
                      {String(direction.display_order).padStart(2, "0")}
                    </span>
                    <h3>{direction.title_original}</h3>
                  </div>
                  <StatusBadge label="政策体系Reviewed" tone="verified" />
                </div>

                <div className={styles.policyGrid}>
                  {direction.policies.map((policy) => (
                    <section className={styles.policyCard} key={policy.id}>
                      <div className={styles.policyHeader}>
                        <h4>{policy.title_original}</h4>
                        <span className={styles.policyNumber}>{policy.policy_number}</span>
                      </div>
                      <ul className={styles.measureList}>
                        {policy.measures.map((measure) => (
                          <li key={measure.id}>
                            <strong>{measure.measure_number}</strong>
                            <span>{measure.title_original}</span>
                          </li>
                        ))}
                      </ul>
                    </section>
                  ))}
                </div>
              </article>
            ))}
          </div>
        </section>

        <section className="contentSection">
          <p className="eyebrow">Parallel reconstruction support</p>
          <h2>復興完了に向けた4取組分野は、政策9ではありません。</h2>
          <p className={styles.sectionLead}>
            被災地へのきめ細かなサポートは、4基本方向・8政策・18施策と並行する別枠です。政策番号を付与せず、公式の4取組分野として保持します。
          </p>
          <div className={styles.parallelGrid}>
            {reviewedMiyagiParallelDomains.map((domain) => (
              <article className={styles.parallelCard} key={domain.id}>
                <span>取組分野 {domain.display_order}</span>
                <h3>{domain.title_original}</h3>
                <p>{domain.relationship_note}</p>
              </article>
            ))}
          </div>
        </section>

        <section className={styles.boundary}>
          <div>
            <p className="eyebrow">Not linked yet</p>
            <h2>政策体系を確認したことと、成果を評価したことは別です。</h2>
            <p>
              現在は関連資料{miyagiPolicyHierarchyStats.inventorySources}件、資料関係{miyagiPolicyHierarchyStats.inventoryRelationships}件、政策体系の原文と順序までReviewed済みです。
            </p>
          </div>
          <ul>
            <li>中期実施計画の目標指標一覧と18施策の接続</li>
            <li>目標値・期間・単位・基準値のReviewed化</li>
            <li>年度実績と活動年度の対応</li>
            <li>県の自己評価と行政評価委員会意見の分離</li>
            <li>評価原案・審議過程・確定評価の履歴</li>
          </ul>
        </section>

        <nav className={styles.bottomNav} aria-label="関連ページ">
          <Link href="/municipalities/hokkaido">北海道の政策指標</Link>
          <Link href="/policies">福岡県の政策体系</Link>
          <Link href="/data-quality">データ品質</Link>
          <Link href="/municipalities">全国自治体一覧</Link>
        </nav>
      </div>
      <SiteFooter />
    </main>
  );
}
