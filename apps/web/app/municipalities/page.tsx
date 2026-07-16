import type { Metadata } from "next";
import Link from "next/link";

import { PageIntro } from "@/components/PageIntro";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { StatusBadge } from "@/components/StatusBadge";
import { municipalityMeta, sourcesForMunicipality, type MunicipalityKey } from "@/lib/catalog";
import {
  coverageStageLabel,
  coverageStageTone,
  nationwideCoverageByRegion,
  nationwideCoverageStats,
  nationwidePrefectureCoverage,
  planCurrencyLabel,
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

const planStatusLabels = {
  not_started: "未着手",
  indexed: "計画入口確認済み",
  reviewed: "Reviewed",
  verified: "Verified",
} as const;

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
            <li><strong>2</strong><span>公式入口確認済み</span><p>自治体公式サイトであることを手動確認。</p></li>
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

          <div className={styles.regionStack}>
            {nationwideCoverageByRegion.map(({ region, records }) => (
              <section className={styles.regionSection} key={region}>
                <div className={styles.regionHeader}>
                  <h3>{region}</h3>
                  <span>{records.length}都道府県</span>
                </div>
                <div className={styles.prefectureGrid}>
                  {records.map((record) => (
                    <article className={styles.prefectureCard} key={record.prefecture_code}>
                      <div className={styles.prefectureTop}>
                        <div>
                          <span className={styles.code}>{record.prefecture_code}</span>
                          <h4>{record.name}</h4>
                        </div>
                        <StatusBadge
                          label={coverageStageLabel(record.coverageStage)}
                          tone={coverageStageTone(record.coverageStage)}
                        />
                      </div>

                      <dl className={styles.prefectureFacts}>
                        <div>
                          <dt>公式入口</dt>
                          <dd>{record.officialEntryStatus === "verified" ? "確認済み" : "候補・未確認"}</dd>
                        </div>
                        <div>
                          <dt>総合計画</dt>
                          <dd>{planStatusLabels[record.planReviewStatus]}</dd>
                        </div>
                        <div>
                          <dt>計画資料</dt>
                          <dd>{record.planSource?.title ?? "未索引"}</dd>
                        </div>
                        <div>
                          <dt>現行性</dt>
                          <dd>{planCurrencyLabel(record.planCurrencyStatus)}</dd>
                        </div>
                        <div>
                          <dt>公開ページ</dt>
                          <dd>{record.publicHref ? "公開中" : "未公開"}</dd>
                        </div>
                      </dl>

                      <div className={styles.actions}>
                        {record.publicHref ? <Link href={record.publicHref}>自治体ページ</Link> : null}
                        {record.planSource ? (
                          <a href={record.planSource.url} target="_blank" rel="noreferrer">総合計画 ↗</a>
                        ) : null}
                        <a href={record.official_url} target="_blank" rel="noreferrer">
                          {record.officialEntryStatus === "verified" ? "公式サイト ↗" : "公式URL候補 ↗"}
                        </a>
                      </div>
                    </article>
                  ))}
                </div>
              </section>
            ))}
          </div>
        </section>

        <section className="contentSection">
          <p className="eyebrow">Wave 1 review queue</p>
          <h2>Reviewed化は、北海道から始める。</h2>
          <p className={styles.sectionLead}>
            福岡県を基準実装とし、次は公式入口に108指標の個票がまとまる北海道で、政策体系・KPI・Evidence Packetの全国展開モデルを検証します。順位は評価点ではなく、資料構造と作業依存関係に基づく運用順です。
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
            <p className="eyebrow">Next nationwide wave</p>
            <h2>北海道の108指標から、全国Reviewed化を開始する。</h2>
            <p>
              第1波9拠点すべてで、公式ホームページ、計画入口、現行計画を確認しました。北海道で非福岡型の抽出・Evidence Packetを確立し、その方法を宮城県、愛知県、香川県へ展開します。
            </p>
          </div>
        </section>
      </div>
      <SiteFooter />
    </main>
  );
}
