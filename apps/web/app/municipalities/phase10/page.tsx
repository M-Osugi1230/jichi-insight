import type { Metadata } from "next";
import Link from "next/link";

import { PageIntro } from "@/components/PageIntro";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { StatusBadge } from "@/components/StatusBadge";
import {
  loadPhase10Queue,
  loadPhase10ReferenceReviews,
  loadPhase10SourceInventory,
  loadPhase10Uniformity,
  phase10DepthLabel,
  phase10ReferenceReviewsByPrefecture,
  phase10SourcesByPrefecture,
  phase10UniformRecords,
  phase10UniformSummary,
  phase10UniformRecordStatusLabel,
  type Phase10DepthStatus,
  type Phase10DimensionId,
  type Phase10UniformRecord,
} from "@/lib/phase10";

import styles from "./phase10.module.css";

export const metadata: Metadata = {
  title: "Phase 10｜全国47都道府県の情報深度をそろえる",
  description:
    "全国47都道府県を同じ品質ゲートで管理し、政策目標を年度実績、予算・決算、重点事業、契約、議会、監査、首長公約へ接続するPhase 10の進行状況を公開します。",
};

export const dynamic = "force-static";

const depthFields = [
  ["annual_evaluation", "年度実績"],
  ["budget", "予算・決算"],
  ["project_evaluation", "事業評価"],
  ["contracts", "契約"],
] as const;

const matrixDimensions: Array<{
  id: Phase10DimensionId;
  label: string;
}> = [
  { id: "annual_actuals", label: "年度実績" },
  { id: "budget", label: "予算" },
  { id: "settlement", label: "決算" },
  { id: "priority_projects", label: "重点事業" },
  { id: "contracts", label: "契約" },
  { id: "assembly", label: "議会" },
  { id: "audit", label: "監査" },
  { id: "executive_manifesto", label: "首長公約" },
];

const sourceCategoryLabels = {
  annual_evaluation: "年度実績",
  budget: "予算",
  project_evaluation: "事業評価",
  contracts: "契約",
};

const referenceDimensionLabels = {
  annual_actuals: "年度実績",
  budget: "予算",
  settlement: "決算",
  priority_projects: "重点事業",
  assembly: "議会",
  audit: "監査",
};

const wave1DepthMap = {
  annual_evaluation: "annual_actuals",
  budget: "budget",
  project_evaluation: "priority_projects",
  contracts: "contracts",
} as const;

function indexedOrBetter(counts: Record<Phase10DepthStatus, number>): number {
  return counts.indexed + counts.reviewed + counts.linked;
}

function statusTone(
  status: Phase10UniformRecord["status"],
): "neutral" | "progress" | "warning" | "verified" {
  if (status === "complete" || status === "review_ready") {
    return "verified";
  }
  if (status === "linkage_in_progress") {
    return "progress";
  }
  if (status === "source_indexing") {
    return "warning";
  }
  return "neutral";
}

export default function Phase10MunicipalitiesPage() {
  const queue = loadPhase10Queue();
  const uniformity = loadPhase10Uniformity();
  const uniformRecords = phase10UniformRecords(uniformity);
  const uniformSummary = phase10UniformSummary(uniformity, uniformRecords);
  const sourceInventory = loadPhase10SourceInventory();
  const sourcesByPrefecture = phase10SourcesByPrefecture(sourceInventory);
  const referenceReviews = loadPhase10ReferenceReviews();
  const referenceReviewsByPrefecture =
    phase10ReferenceReviewsByPrefecture(referenceReviews);
  const uniformByCode = new Map(
    uniformRecords.map((record) => [record.prefecture_code, record]),
  );
  const budgetIndexed = indexedOrBetter(uniformSummary.budget);
  const settlementIndexed = indexedOrBetter(uniformSummary.settlement);

  return (
    <main id="main-content">
      <SiteHeader />
      <div className="pageShell">
        <PageIntro
          eyebrow="Phase 10 nationwide uniform depth"
          title="47都道府県を、同じ深さまで掘る。"
        >
          <p>
            Phase 9で確認した全国47都道府県の目標原文を、年度実績、予算・決算、
            重点事業、契約、議会、監査、首長公約へつなぎます。掲載件数ではなく、
            全都道府県が同じ品質ゲートを通過したかでPhase 10の完了を判断します。
          </p>
          <div className={styles.introLinks}>
            <Link href="/municipalities/phase9">全国のReviewed目標を見る</Link>
            <Link href="/methodology">方法論を確認する</Link>
          </div>
        </PageIntro>

        <section className={styles.summaryGrid} aria-label="Phase 10進行状況">
          <article>
            <span>同一粒度 完了</span>
            <strong>{uniformSummary.uniform_depth_complete} / 47</strong>
            <p>11項目すべてが共通ゲートへ到達した都道府県数です。</p>
          </article>
          <article>
            <span>Reviewed目標・Evidence</span>
            <strong>47 / 47</strong>
            <p>全都道府県でPhase 10の接続元を確保済みです。</p>
          </article>
          <article>
            <span>年度実績 接続済み</span>
            <strong>{uniformSummary.annual_actuals.linked}</strong>
            <p>定義、期間、対象範囲を確認して目標へ接続した県数です。</p>
          </article>
          <article>
            <span>予算 / 決算 入口以上</span>
            <strong>{budgetIndexed} / {settlementIndexed}</strong>
            <p>入口確認以上の県数です。金額接続済みを意味しません。</p>
          </article>
          <article>
            <span>公式ソース</span>
            <strong>{sourceInventory.summary.source_count}</strong>
            <p>現在の参照実装で確認した年度実績、予算、事業、契約の入口です。</p>
          </article>
        </section>

        <section className={styles.boundary}>
          <div>
            <p className="eyebrow">One gate for all 47</p>
            <h2>深い県だけで、全国対応とは呼ばない。</h2>
          </div>
          <div className={styles.boundaryGrid}>
            <article>
              <strong>入口確認</strong>
              <p>公式資料の所在を確認した状態です。目標との対応はまだ確定しません。</p>
            </article>
            <article>
              <strong>Reviewed</strong>
              <p>値、年度、範囲、資料位置をEvidenceとともに確認した状態です。</p>
            </article>
            <article>
              <strong>目標へ接続</strong>
              <p>定義、期間、対象範囲を照合し、同じ政策系列として接続した状態です。</p>
            </article>
            <article>
              <strong>部分完了なし</strong>
              <p>47都道府県すべてが共通ゲートを通るまでPhase 10は完了にしません。</p>
            </article>
          </div>
        </section>

        <section className="contentSection" aria-labelledby="uniform-depth-matrix">
          <div className={styles.sectionHeading}>
            <div>
              <p className="eyebrow">Nationwide depth matrix</p>
              <h2 id="uniform-depth-matrix">全47都道府県の深度差を、そのまま表示。</h2>
            </div>
            <p>
              政策目標、Evidence、公開検証は47都道府県でReviewed済みです。
              下表は、その先の実績・金額・事業・説明責任の未完範囲を示します。
            </p>
          </div>

          <div className={styles.matrixWrap}>
            <table className={styles.depthMatrix}>
              <thead>
                <tr>
                  <th scope="col">都道府県</th>
                  <th scope="col">状態</th>
                  {matrixDimensions.map((dimension) => (
                    <th scope="col" key={dimension.id}>{dimension.label}</th>
                  ))}
                  <th scope="col">残り</th>
                </tr>
              </thead>
              <tbody>
                {uniformRecords.map((record) => (
                  <tr key={record.prefecture_code}>
                    <th scope="row">
                      <span>{record.prefecture_code}</span>
                      {record.name}
                      <small>{record.region}</small>
                    </th>
                    <td>
                      <StatusBadge
                        label={phase10UniformRecordStatusLabel(record.status)}
                        tone={statusTone(record.status)}
                      />
                    </td>
                    {matrixDimensions.map((dimension) => {
                      const depth = record.current_depth[dimension.id];
                      return (
                        <td key={dimension.id}>
                          <span className={styles.depthState} data-state={depth}>
                            {phase10DepthLabel(depth)}
                          </span>
                        </td>
                      );
                    })}
                    <td className={styles.gapCell}>{record.gap_count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className={styles.matrixNote}>
            「未索引」は不存在を意味しません。公式資料入口をまだ固定していない状態です。
          </p>
        </section>

        <section className="contentSection" aria-labelledby="reference-depth-reviews">
          <div className={styles.sectionHeading}>
            <div>
              <p className="eyebrow">Reviewed reference depth</p>
              <h2 id="reference-depth-reviews">宮城県と福岡県の次の層を、公式資料で確認。</h2>
            </div>
            <p>
              年度実績の先にある予算、決算、重点事業、議会、監査について、
              公式資料の内容と未接続範囲を分けてReviewed化しました。
            </p>
          </div>

          <div className={styles.reviewGrid}>
            {referenceReviews.prefecture_codes.map((code) => {
              const records = referenceReviewsByPrefecture.get(code) ?? [];
              const prefecture = uniformByCode.get(code);
              return (
                <article className={styles.reviewCard} key={code}>
                  <div className={styles.cardHeader}>
                    <span>{code} / {prefecture?.region}</span>
                    <StatusBadge label="深掘りReviewed" tone="verified" />
                  </div>
                  <h3>{prefecture?.name}</h3>
                  <div className={styles.reviewList}>
                    {records.map((record) => (
                      <div key={record.id}>
                        <div className={styles.reviewMeta}>
                          <strong>{referenceDimensionLabels[record.dimension]}</strong>
                          <span>{phase10DepthLabel(record.resulting_depth)}</span>
                        </div>
                        <a href={record.url} target="_blank" rel="noreferrer">
                          {record.title} ↗
                        </a>
                        <p>{record.claims[0]}</p>
                        <small>{record.boundary}</small>
                      </div>
                    ))}
                  </div>
                </article>
              );
            })}
          </div>
        </section>

        <section className="contentSection" aria-labelledby="phase10-wave1">
          <div className={styles.sectionHeading}>
            <div>
              <p className="eyebrow">Reference implementations</p>
              <h2 id="phase10-wave1">9地域拠点から、接続方法を確立する。</h2>
            </div>
            <p>
              宮城県を年度実績接続の基準、福岡県を予算・決算接続の基準として、
              残る7拠点へ同じ工程を適用します。
            </p>
          </div>

          <div className={styles.prefectureGrid}>
            {queue.wave1_records.map((record) => {
              const sources = sourcesByPrefecture.get(record.prefecture_code) ?? [];
              const uniformRecord = uniformByCode.get(record.prefecture_code);
              return (
                <article className={styles.prefectureCard} key={record.prefecture_code}>
                  <div className={styles.cardHeader}>
                    <span>{record.prefecture_code} / {record.region}</span>
                    <StatusBadge
                      label={
                        uniformRecord
                          ? phase10UniformRecordStatusLabel(uniformRecord.status)
                          : "資料索引待ち"
                      }
                      tone={uniformRecord ? statusTone(uniformRecord.status) : "neutral"}
                    />
                  </div>
                  <h3>{record.name}</h3>
                  <dl>
                    {depthFields.map(([field, label]) => (
                      <div key={field}>
                        <dt>{label}</dt>
                        <dd>
                          {phase10DepthLabel(
                            uniformRecord?.current_depth[wave1DepthMap[field]] ??
                              record.current_depth[field],
                          )}
                        </dd>
                      </div>
                    ))}
                  </dl>
                  <p>{uniformRecord?.next_action ?? record.next_action}</p>
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
            <h2>宮城県と福岡県で、実績・金額・事業の接続基準を固める。</h2>
            <p>
              宮城県の年度実績接続と福岡県のReviewed財政・決算を基準に、
              予算、重点事業、契約、議会、監査、公約を同じ政策系列へ接続します。
            </p>
          </div>
          <Link href="/municipalities/miyagi">宮城県の年度実績を見る →</Link>
        </section>
      </div>
      <SiteFooter />
    </main>
  );
}
