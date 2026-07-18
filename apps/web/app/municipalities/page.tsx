import type { Metadata } from "next";
import Link from "next/link";

import { CoverageExplorer } from "@/components/CoverageExplorer";
import { PageIntro } from "@/components/PageIntro";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { StatusBadge } from "@/components/StatusBadge";
import { municipalityMeta, sourcesForMunicipality, type MunicipalityKey } from "@/lib/catalog";
import { miyagiPolicyReviewStats } from "@/lib/miyagiPolicies";
import {
  nationwideCoverageStats,
  nationwidePrefectureCoverage,
} from "@/lib/nationwideCoverage";
import {
  policyReviewNextGateLabel,
  policyReviewStatusLabel,
  policyReviewStatusTone,
  sourceInventoryStatusLabel,
  waveOnePolicyReviewQueue,
  waveOnePolicyReviewStats,
} from "@/lib/policyReviewQueue";

import styles from "./page.module.css";

export const metadata: Metadata = {
  title: "全国自治体カバレッジ",
  description:
    "全国47都道府県の登録状況、公式入口、総合計画の索引・現行性、Reviewedデータと公開ページの整備状況を確認できます。",
};

const cityKeys = (Object.keys(municipalityMeta) as MunicipalityKey[]).filter(
  (key) => municipalityMeta[key].type === "政令指定都市",
);

const indexedPlanNames = nationwidePrefectureCoverage
  .filter((record) => record.planSource !== null)
  .map((record) => record.name)
  .join("、");

export default function MunicipalitiesPage() {
  return (
    <main>
      <SiteHeader />
      <div className="pageShell">
        <PageIntro eyebrow="Nationwide coverage" title="全国47都道府県を、同じ品質段階で追う。">
          <p>
            全国を登録対象にしました。ただし、名前を登録した状態、公式サイトを確認した状態、計画入口を索引化した状態、現行計画であることを確認した状態、数値を人が照合した状態は同じではありません。
            Jichi Insightは、未着手や旧計画を公開済みのように見せず、段階ごとの進捗をそのまま表示します。
          </p>
        </PageIntro>

        <section className={styles.summaryGrid} aria-label="全国展開の概要">
          <article className={styles.summaryCard}>
            <span>全国登録</span>
            <strong>{nationwideCoverageStats.totalPrefectures}</strong>
            <p>47都道府県を共通コード・地域区分・公式URL候補付きで登録。</p>
          </article>
          <article className={styles.summaryCard}>
            <span>公式入口確認済み</span>
            <strong>{nationwideCoverageStats.verifiedOfficialEntries}</strong>
            <p>各地域の先行拠点を中心に、公式ホームページを手動確認。</p>
          </article>
          <article className={styles.summaryCard}>
            <span>総合計画索引済み</span>
            <strong>{nationwideCoverageStats.sourceCatalogedPrefectures}</strong>
            <p>{indexedPlanNames}で計画資料の入口を確認。</p>
          </article>
          <article className={styles.summaryCard}>
            <span>現行計画確認済み</span>
            <strong>{nationwideCoverageStats.currentPlanConfirmedPrefectures}</strong>
            <p>後継計画や改定状況まで確認した都道府県だけを計上。</p>
          </article>
          <article className={styles.summaryCard}>
            <span>Reviewedデータ公開</span>
            <strong>{nationwideCoverageStats.reviewedPrefectures}</strong>
            <p>一次資料と人の照合を通過した都道府県だけを計上。</p>
          </article>
        </section>

        <section className={styles.ladderSection}>
          <div>
            <p className="eyebrow">Coverage ladder</p>
            <h2>量を増やしても、品質段階は混ぜない。</h2>
          </div>
          <ol className={styles.ladder}>
            <li><strong>1</strong><span>全国登録済み</span><p>コード・名称・地域・公式URL候補を登録。</p></li>
            <li><strong>2</strong><span>公式入口確認済み</span><p>自治体の公式入口を確認済み。</p></li>
            <li><strong>3</strong><span>計画資料索引済み</span><p>総合計画・実施計画の公式入口を固定。</p></li>
            <li><strong>4</strong><span>現行計画確認済み</span><p>後継計画、改定、計画期間を確認。</p></li>
            <li><strong>5</strong><span>Reviewedデータ公開</span><p>本文・数値・期間・単位を一次資料と照合。</p></li>
          </ol>
        </section>

        <section className="contentSection">
          <p className="eyebrow">47 prefectures</p>
          <h2>地域ごとの全国カバレッジ</h2>
          <p className={styles.sectionLead}>
            第1波は各地域の拠点9都道府県です。候補URL、計画入口、現行性、Reviewed状態を分け、確認が終わった段階だけを昇格します。
          </p>

          <CoverageExplorer />
        </section>

        <section className="contentSection">
          <p className="eyebrow">Wave 1 review queue</p>
          <h2>宮城県{miyagiPolicyReviewStats.reviewedTargetGroups}目標を公開。次は取組6の目標41〜45。</h2>
          <p className={styles.sectionLead}>
            福岡県を基準実装とし、北海道では18政策分野・108指標・Evidence Packet 108件のReviewed工程を完了しました。宮城県では128目標グループ・149系列の位置を確認し、先頭40グループ・43系列をReviewed化しました。年度実績との接続は別工程として残し、順位は評価点ではなく資料構造と作業依存関係に基づく運用順です。
          </p>

          <div className={styles.queueSummary} aria-label="第1波Reviewed化の進捗">
            <article><span>Reviewed基準実装</span><strong>{waveOnePolicyReviewStats.reviewedReferences}</strong></article>
            <article><span>Reviewed化作業中</span><strong>{waveOnePolicyReviewStats.activeReviews}</strong></article>
            <article><span>作業待ち</span><strong>{waveOnePolicyReviewStats.queued}</strong></article>
          </div>

          <div className={styles.reviewQueue}>
            {waveOnePolicyReviewQueue.map((item) => (
              <article
                className={`${styles.reviewCard} ${item.status === "active_review" ? styles.reviewCardActive : ""}`.trim()}
                key={item.prefecture_code}
              >
                <div className={styles.reviewCardHeader}>
                  <div>
                    <span className={styles.queueOrder}>
                      {item.order === 0 ? "基準" : `優先 ${item.order}`}
                    </span>
                    <h3>{item.name}</h3>
                  </div>
                  <StatusBadge
                    label={policyReviewStatusLabel(item.status)}
                    tone={policyReviewStatusTone(item.status)}
                  />
                </div>
                <p className={styles.planTitle}>{item.current_plan_title}</p>
                <dl className={styles.reviewFacts}>
                  <div>
                    <dt>資料状態</dt>
                    <dd>{sourceInventoryStatusLabel(item.source_inventory_status)}</dd>
                  </div>
                  <div>
                    <dt>次の品質ゲート</dt>
                    <dd>{policyReviewNextGateLabel(item.next_gate)}</dd>
                  </div>
                </dl>
                <div className={styles.nextAction}>
                  <span>次の作業</span>
                  <p>{item.next_action}</p>
                </div>
                <details className={styles.priorityBasis}>
                  <summary>この順番の理由</summary>
                  <p>{item.priority_basis}</p>
                </details>
                <div className={styles.actions}>
                  {item.prefecture_code === "04" ? (
                    <Link href="/municipalities/miyagi">Reviewed目標を見る</Link>
                  ) : null}
                  {item.sources.map((source) => (
                    <a href={source.url} target="_blank" rel="noreferrer" key={source.id}>
                      {source.title} ↗
                    </a>
                  ))}
                </div>
              </article>
            ))}
          </div>
        </section>

        <section className="contentSection">
          <p className="eyebrow">Designated-city pilots</p>
          <h2>政令指定都市の既存パイロット</h2>
          <div className={styles.cityGrid}>
            {cityKeys.map((key) => {
              const municipality = municipalityMeta[key];
              return (
                <article className={styles.cityCard} key={key}>
                  <div>
                    <p>{municipality.type}</p>
                    <h3>{municipality.name}</h3>
                  </div>
                  <StatusBadge label={municipality.status} tone="verified" />
                  <p>{municipality.summary}</p>
                  <dl>
                    <div><dt>公式資料入口</dt><dd>{sourcesForMunicipality(key).length}件</dd></div>
                    <div><dt>財政データ</dt><dd>{municipality.fiscalSummary}</dd></div>
                  </dl>
                  {municipality.href ? <Link href={municipality.href}>自治体ページを見る</Link> : null}
                </article>
              );
            })}
          </div>
        </section>

        <section className="callout callout--dark">
          <div>
            <p className="eyebrow">Active review</p>
            <h2>宮城県の40目標を公開。未Reviewedの88目標も明示する。</h2>
            <p>
              初期値・現況値・中期末目標・後期末目標を原文のまま確認できます。後期末目標の「－」は0にせず未設定、複数系列や累計値は単一値や単年度値に変換せず表示しています。
            </p>
          </div>
          <Link className="primaryAction" href="/municipalities/miyagi">
            宮城県の{miyagiPolicyReviewStats.reviewedTargetGroups}目標を見る
          </Link>
        </section>
      </div>
      <SiteFooter />
    </main>
  );
}
