import type { Metadata } from "next";
import Link from "next/link";

import { PageIntro } from "@/components/PageIntro";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { StatusBadge } from "@/components/StatusBadge";
import {
  loadPhase10Queue,
  loadPhase10SourceInventory,
  phase10DepthLabel,
  phase10SourcesByPrefecture,
} from "@/lib/phase10";

import styles from "./phase10.module.css";

export const metadata: Metadata = {
  title: "Phase 10｜目標・実績・予算・事業の接続",
  description:
    "全国47都道府県のReviewed目標を、年度実績、予算、重点事業、契約、説明責任へ接続するPhase 10の進行状況を公開します。",
};

export const dynamic = "force-static";

const depthFields = [
  ["annual_evaluation", "年度実績"],
  ["budget", "予算・決算"],
  ["project_evaluation", "事業評価"],
  ["contracts", "契約"],
] as const;

const sourceCategoryLabels = {
  annual_evaluation: "年度実績",
  budget: "予算",
  project_evaluation: "事業評価",
  contracts: "契約",
};

export default function Phase10MunicipalitiesPage() {
  const queue = loadPhase10Queue();
  const sourceInventory = loadPhase10SourceInventory();
  const sourcesByPrefecture = phase10SourcesByPrefecture(sourceInventory);

  return (
    <main id="main-content">
      <SiteHeader />
      <div className="pageShell">
        <PageIntro
          eyebrow="Phase 10 vertical linkage"
          title="目標から、実績・予算・事業へつなぐ。"
        >
          <p>
            Phase 9で確認した全国47都道府県の目標原文を、年度実績、予算・決算、
            重点事業、契約、評価・監査・議会説明へ順番につなぎます。資料入口を
            見つけた状態と、定義を照合して目標へ接続した状態は分けて表示します。
          </p>
          <div className={styles.introLinks}>
            <Link href="/municipalities/phase9">全国のReviewed目標を見る</Link>
            <Link href="/methodology">方法論を確認する</Link>
          </div>
        </PageIntro>

        <section className={styles.summaryGrid} aria-label="Phase 10進行状況">
          <article>
            <span>Reviewed目標</span>
            <strong>{queue.counts.target_statements_reviewed} / 47</strong>
            <p>Phase 10の接続元となる全国の政策目標です。</p>
          </article>
          <article>
            <span>年度実績 接続済み</span>
            <strong>{queue.counts.annual_evaluation_linked}</strong>
            <p>目標と年度実績の定義・期間を照合した県です。</p>
          </article>
          <article>
            <span>事業・契約 入口確認</span>
            <strong>
              {queue.counts.project_evaluation_indexed_or_better} / {queue.counts.contracts_indexed_or_better}
            </strong>
            <p>事業評価と契約の公式入口を確認した県数です。</p>
          </article>
          <article>
            <span>公式ソース</span>
            <strong>{sourceInventory.summary.source_count}</strong>
            <p>宮城県・福岡県で確認した年度実績、予算、事業、契約の入口です。</p>
          </article>
        </section>

        <section className={styles.boundary}>
          <div>
            <p className="eyebrow">Linkage boundaries</p>
            <h2>「資料がある」と「同じ政策へつながる」を混同しない。</h2>
          </div>
          <div className={styles.boundaryGrid}>
            <article>
              <strong>入口確認</strong>
              <p>公式資料の所在を確認した状態です。目標との対応はまだ確定しません。</p>
            </article>
            <article>
              <strong>Reviewed</strong>
              <p>値、年度、会計区分、資料位置をEvidenceとともに確認した状態です。</p>
            </article>
            <article>
              <strong>目標へ接続</strong>
              <p>指標定義、期間、対象範囲を照合し、同じ政策系列として接続した状態です。</p>
            </article>
            <article>
              <strong>政策評価は未判定</strong>
              <p>支出や事業実施だけを理由に、達成・未達や自治体の優劣を判定しません。</p>
            </article>
          </div>
        </section>

        <section className="contentSection" aria-labelledby="phase10-wave1">
          <div className={styles.sectionHeading}>
            <div>
              <p className="eyebrow">Wave 1 regional anchors</p>
              <h2 id="phase10-wave1">9地域拠点の接続状態。</h2>
            </div>
            <p>
              宮城県を年度実績接続の基準、福岡県を予算・財政接続の基準として、
              残る7拠点の資料入口を順に固定します。
            </p>
          </div>

          <div className={styles.prefectureGrid}>
            {queue.wave1_records.map((record) => {
              const sources = sourcesByPrefecture.get(record.prefecture_code) ?? [];
              return (
                <article className={styles.prefectureCard} key={record.prefecture_code}>
                  <div className={styles.cardHeader}>
                    <span>{record.prefecture_code} / {record.region}</span>
                    <StatusBadge
                      label={
                        record.status === "linked_baseline"
                          ? "接続基準"
                          : record.status === "review_ready"
                            ? "接続準備"
                            : "資料索引待ち"
                      }
                      tone={record.status === "queued" ? "neutral" : "verified"}
                    />
                  </div>
                  <h3>{record.name}</h3>
                  <dl>
                    {depthFields.map(([field, label]) => (
                      <div key={field}>
                        <dt>{label}</dt>
                        <dd>{phase10DepthLabel(record.current_depth[field])}</dd>
                      </div>
                    ))}
                  </dl>
                  <p>{record.next_action}</p>
                  {sources.length > 0 ? (
                    <div className={styles.sourceList}>
                      <strong>公式資料入口</strong>
                      {sources.map((source) => (
                        <a href={source.url} key={source.id} target="_blank" rel="noreferrer">
                          <span>{sourceCategoryLabels[source.category]}</span>
                          {source.title} ↗
                        </a>
                      ))}
                    </div>
                  ) : null}
                </article>
              );
            })}
          </div>
        </section>

        <section className={styles.nextSection}>
          <div>
            <p className="eyebrow">Current active reference</p>
            <h2>宮城県：年度実績の次に、予算・事業・契約をつなぐ。</h2>
            <p>
              公式入口の索引化は完了しました。次は予算資料と事業評価を政策・施策・事業IDへ照合し、
              契約結果を同じ事業へ接続できるか確認します。
            </p>
          </div>
          <Link href="/municipalities/miyagi">宮城県の年度実績を見る →</Link>
        </section>
      </div>
      <SiteFooter />
    </main>
  );
}
