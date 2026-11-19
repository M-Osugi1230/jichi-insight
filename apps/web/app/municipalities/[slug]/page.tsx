import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { BreadcrumbTrail } from "@/components/BreadcrumbTrail";
import { PageIntro } from "@/components/PageIntro";
import { CityOverview } from "@/components/CityOverview";
import { FiscalReview } from "@/components/FiscalReview";
import { MunicipalityDiscoveryPanel } from "@/components/MunicipalityDiscoveryPanel";
import { DeduplicateCitySourceTabStops } from "@/components/DeduplicateCitySourceTabStops";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { SourceLocation } from "@/components/SourceLocation";
import { StatusBadge } from "@/components/StatusBadge";
import {
  loadPhase15Cities,
  loadPhase15City,
  type Phase15FiscalRecord,
  type Phase15PlanRecord,
  type Phase15ResolvedSource,
} from "@/lib/phase15Cities";
import { defaultOgImages } from "@/lib/pageMetadata";
import { loadGenericCityFinance } from "@/lib/genericCityFinance";

import styles from "./page.module.css";

const siteUrl = "https://jimieru.com";
const sourcePrefix = "https://github.com/M-Osugi1230/jichi-insight/blob/main/";

export const dynamic = "force-static";
export const dynamicParams = false;

export function generateStaticParams() {
  return loadPhase15Cities().map((city) => ({ slug: city.slug }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const city = loadPhase15City(slug);
  if (!city) {
    return { title: "自治体ページ" };
  }
  const title = `${city.name}｜計画・予算・決算の一次資料レビュー`;
  const description = `${city.prefecture}${city.name}の現行計画・予算・決算を一次資料から確認。レビュー済みの情報と未接続の範囲を区別して公開します。`;
  return {
    title,
    description,
    alternates: {
      canonical: `${siteUrl}/municipalities/${city.slug}/`,
    },
    openGraph: {
      title,
      description,
      url: `${siteUrl}/municipalities/${city.slug}/`,
      // A returned openGraph object replaces the inherited one, including
      // the layout's default image, so the shared default is passed here.
      images: defaultOgImages,
    },
  };
}

const roleLabels: Record<string, string> = {
  current_plan_identity: "現行計画の特定",
  policy_structure: "政策体系",
  implementation_layer: "実施計画",
  progress_governance: "進行管理",
  annual_progress: "年次評価・実績資料",
  latest_completed_annual_progress: "年次評価・実績資料",
  plan_transition: "計画の移行",
};

function formatYen(amount: number) {
  return `${new Intl.NumberFormat("ja-JP").format(amount)}円`;
}

function fiscalStageLabel(record: Phase15FiscalRecord) {
  if (record.stage === "initial_budget") {
    return `${record.fiscalYear}年度 ${record.metricLabel}`;
  }
  if (record.stage === "settlement" && record.metric === "total_revenue") {
    return `${record.fiscalYear}年度 決算（歳入）`;
  }
  if (record.stage === "settlement" && record.metric === "total_expenditure") {
    return `${record.fiscalYear}年度 決算（歳出）`;
  }
  return `${record.fiscalYear}年度 ${record.metricLabel}`;
}

function SourceLink({ source }: { source: Phase15ResolvedSource }) {
  return (
    <a href={source.officialUrl} target="_blank" rel="noreferrer">
      {source.title} ↗
    </a>
  );
}

function PlanRecordCard({ record }: { record: Phase15PlanRecord }) {
  return (
    <article className={styles.recordCard}>
      <div className={styles.recordHead}>
        <span>{roleLabels[record.evidenceRole] ?? record.evidenceRole}</span>
        <StatusBadge
          label={record.decision === "accepted" ? "確認済み（accepted）" : record.decision}
          tone={record.decision === "accepted" ? "verified" : "warning"}
        />
      </div>
      <h3>{record.title}</h3>
      <p className={styles.statement}>{record.statement}</p>
      {record.value !== null && (
        <p className={styles.recordValue}>
          {record.value}
          {record.unit ? ` ${record.unit}` : ""}
        </p>
      )}
      <dl className={styles.recordFacts}>
        <div>
          <dt>出典</dt>
          <dd>
            <a href={record.sourceUrl} target="_blank" rel="noreferrer">
              公式資料を開く ↗
            </a>
          </dd>
        </div>
        <div>
          <dt>資料位置</dt>
          <dd>{record.evidenceLocation}</dd>
        </div>
      </dl>
      <details className={styles.detailBox}>
        <summary>レビュー注記</summary>
        <p>{record.reviewNote}</p>
      </details>
    </article>
  );
}

function FiscalRecordCard({ record }: { record: Phase15FiscalRecord }) {
  return (
    <article className={styles.recordCard}>
      <div className={styles.recordHead}>
        <span>{fiscalStageLabel(record)}</span>
        <StatusBadge label="Reviewed" tone="verified" />
      </div>
      <h3>{record.metricLabel}</h3>
      {record.valueStatus === "available" && record.amountYen !== null ? (
        <p className={styles.amount}>{formatYen(record.amountYen)}</p>
      ) : (
        <p className={styles.amountUnavailable}>
          金額は未確認です（状態: {record.valueStatus}）。推測値や概数では表示しません。
        </p>
      )}
      <dl className={styles.recordFacts}>
        <div>
          <dt>対象期間</dt>
          <dd>
            {record.periodStart} 〜 {record.periodEnd}
          </dd>
        </div>
        <div>
          <dt>出典</dt>
          <dd>
            <ul className={styles.sourceList}>
              {record.sources.map((source) => (
                <li key={source.id}>
                  <SourceLink source={source} />
                </li>
              ))}
            </ul>
          </dd>
        </div>
      </dl>
      <p className={styles.note}>{record.note}</p>
      {record.claims.length > 0 && (
        <details className={styles.detailBox}>
          <summary>Evidence（照合の記録）</summary>
          {record.claims.map((claim) => (
            <div className={styles.claim} key={`${claim.field}-${claim.statement}`}>
              <p className={styles.statement}>{claim.statement}</p>
              <dl className={styles.recordFacts}>
                <div>
                  <dt>資料位置</dt>
                  <dd>{claim.locationNote}</dd>
                </div>
                <div>
                  <dt>判定</dt>
                  <dd>{claim.decision}</dd>
                </div>
                <div>
                  <dt>出典</dt>
                  <dd>
                    <ul className={styles.sourceList}>
                      {claim.sources.map((source) => (
                        <li key={source.id}>
                          <SourceLink source={source} />
                        </li>
                      ))}
                    </ul>
                  </dd>
                </div>
              </dl>
              <p>{claim.reviewNote}</p>
            </div>
          ))}
        </details>
      )}
      {record.openQuestions.length > 0 && (
        <div className={styles.openQuestions}>
          <strong>未確認の残件</strong>
          <ul>
            {record.openQuestions.map((question) => (
              <li key={question}>{question}</li>
            ))}
          </ul>
        </div>
      )}
    </article>
  );
}

export default async function Phase15CityPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const city = loadPhase15City(slug);
  if (!city) {
    notFound();
  }

  const fiscalDetail = loadGenericCityFinance(slug);

  const promiseRecords = city.planRecords.filter(
    (record) => record.decision === "accepted" && record.evidenceRole !== "plan_transition",
  );
  const transitionRecords = city.planRecords.filter(
    (record) => record.evidenceRole === "plan_transition" && record.decision === "accepted",
  );
  const linkageRecords = city.planRecords.filter((record) => record.decision === "not_assessable");
  const fiscalLinkageDeferred = city.deferredDepth.filter(
    (item) => item.id === "fiscal-detail-and-amendment-linkage",
  );

  return (
    <>
      <SiteHeader />
      <main id="main-content">
      <div className={`pageShell ${styles.cityShell}`} data-city-source-tab-scope>
        <DeduplicateCitySourceTabStops />
        <BreadcrumbTrail items={[{name:"ホーム",href:"/"},{name:"自治体一覧",href:"/municipalities"},{name:city.name,href:`/municipalities/${city.slug}`}]} />
        <PageIntro
          eyebrow={`${city.prefecture} / ${city.officialCode} / 公式資料レビュー`}
          title={`${city.name}の政策・予算・決算`}
        >
          <p>
            {city.prefecture}
            {city.name}の政策計画と一般会計の予算・決算を、公式資料に基づいて整理しています。
            確認できた内容と、実績・事業との接続がまだできない内容を区別して掲載します。
          </p>
          <p>確認できること：この市のレビュー済み計画・予算・決算と公式出典。まだ確認できないこと：市債残高や財政健全性の指標は全67市に同条件では揃っていません。未収録の指標は、自治体が公表していないことを意味しません。</p>
          <div className={styles.introMeta}>
            <StatusBadge label="一次資料レビュー完了" tone="verified" />
            <dl>
              <div>
                <dt>レビュー完了日</dt>
                <dd>{city.completedAt}</dd>
              </div>
              <div>
                <dt>最終確認日</dt>
                <dd>{city.lastVerifiedAt}</dd>
              </div>
              <div>
                <dt>公式サイト</dt>
                <dd>
                  <a href={city.officialUrl} target="_blank" rel="noreferrer">
                    {city.name}公式サイト ↗
                  </a>
                </dd>
              </div>
            </dl>
          </div>
          <div className={styles.introLinks}>
            <Link href="/review-progress">自治体レビューの進捗へ戻る</Link>
            <a href={sourcePrefix + city.completionPath} target="_blank" rel="noreferrer">
              レビュー完了記録（GitHub） ↗
            </a>
          </div>
        </PageIntro>

        <MunicipalityDiscoveryPanel
          officialCode={city.officialCode}
          planHref="#promise-title"
          budgetHref="#money-title"
          fiscalDetailHref={fiscalDetail ? "#fiscal-detail" : undefined}
        />

        <nav className={styles.cityJumpNav} aria-label="この自治体ページの目次">
          <a href="#city-summary-title">概要</a>
          <a href="#promise-title">政策計画</a>
          <a href="#money-title">予算・決算</a>
          <a href="#linkage-title">実績との接続</a>
          <a href="#sources-title">公式資料</a>
          <a href="#boundary-title">確認の範囲</a>
        </nav>
        <CityOverview city={city} />

        <section className="contentSection" aria-labelledby="promise-title">
          <div className={styles.sectionHeading}>
            <div>
              <p className="eyebrow">Promise</p>
              <h2 id="promise-title">計画の枠組み</h2>
            </div>
            <p>
              現行計画が何であり、どの期間・構造で進むかを、計画資料の原文確認から示します。
              政策構造の詳細な正本はGitHub上の公開データへのリンクで案内します。
            </p>
          </div>
          <div className={styles.recordList}>
            {promiseRecords.map((record) => (
              <PlanRecordCard key={record.id} record={record} />
            ))}
          </div>

          {transitionRecords.length > 0 && (
            <div className={styles.transitionBlock}>
              <h3>計画の移行・次期計画の動向（現行計画ではありません）</h3>
              <div className={styles.recordList}>
                {transitionRecords.map((record) => (
                  <PlanRecordCard key={record.id} record={record} />
                ))}
              </div>
            </div>
          )}
        </section>

        <section className="contentSection" aria-labelledby="money-title">
          <div className={styles.sectionHeading}>
            <div>
              <p className="eyebrow">Money</p>
              <h2 id="money-title">予算と決算</h2>
            </div>
            <p>
              この一覧は原資料の数値を円換算で表示します。資料の公表単位や端数処理は各注記を確認してください。
              概要に表示した億円単位の値は読みやすさのための概数で、正式な金額は各レコードで確認できます。
            </p>
          </div>
          <div className={styles.recordList}>
            {city.fiscalRecords.map((record) => (
              <FiscalRecordCard key={record.id} record={record} />
            ))}
          </div>
        </section>

        {fiscalDetail ? (
          <div id="fiscal-detail" style={{ scrollMarginTop: 90 }}>
            <FiscalReview municipality={city.name} records={fiscalDetail.records} sources={fiscalDetail.sources} />
          </div>
        ) : null}

        <section className="contentSection" aria-labelledby="linkage-title">
          <div className={styles.sectionHeading}>
            <div>
              <p className="eyebrow">Linkage</p>
              <h2 id="linkage-title">計画と決算の接続の判定</h2>
            </div>
            <p>
              決算の金額が確認できても、個別事業や指標との接続が確認できたことにはなりません。
              接続の判定状態を、そのまま表示します。
            </p>
          </div>

          {linkageRecords.length > 0 ? (
            <div className={styles.recordList}>
              {linkageRecords.map((record) => (
                <article className={`${styles.recordCard} ${styles.linkageCard}`} key={record.id}>
                  <div className={styles.recordHead}>
                    <span>{record.title}</span>
                    <StatusBadge label="判定不能（not_assessable）" tone="warning" />
                  </div>
                  <p className={styles.statement}>{record.statement}</p>
                  <p>{record.reviewNote}</p>
                  <dl className={styles.recordFacts}>
                    <div>
                      <dt>出典</dt>
                      <dd>
                        <a href={record.sourceUrl} target="_blank" rel="noreferrer">
                          公式資料を開く ↗
                        </a>
                      </dd>
                    </div>
                    <div>
                      <dt>資料位置</dt>
                      <dd>{record.evidenceLocation}</dd>
                    </div>
                  </dl>
                </article>
              ))}
            </div>
          ) : (
            <div className={styles.notice}>
              <p>
                この市のv1レビューでは、決算と個別事業・実績への接続について判定レコードを作成していません。
                接続が確認できたとも、判定不能（not_assessable）と判定したとも扱わず、
                v1レビューでは個別事業・実績への接続を確立していないものとして表示します。
              </p>
              {fiscalLinkageDeferred.map((item) => (
                <p key={item.id}>{item.boundary}</p>
              ))}
            </div>
          )}

          <h3 className={styles.subHeading}>このレビューに含まれないもの</h3>
          <ul className={styles.deferredList}>
            {city.deferredDepth.map((item) => (
              <li key={item.id}>
                <strong>{item.id}</strong>
                <p>{item.boundary}</p>
              </li>
            ))}
          </ul>
        </section>

        <section className="contentSection" aria-labelledby="sources-title">
          <div className={styles.sectionHeading}>
            <div>
              <p className="eyebrow">Sources</p>
              <h2 id="sources-title">出典一覧</h2>
            </div>
            <p>このレビューが依拠した公式資料の正本目録です。各資料の利用境界も併せて示します。</p>
          </div>
          <ol className={styles.sourceCatalog}>
            {city.sources.map((source) => (
              <li key={source.id}>
                <div>
                  <strong>
                    <SourceLink source={source} />
                  </strong>
                  <span>
                    {source.format} / {source.evidenceRole}
                  </span>
                </div>
                {source.evidenceLocation && (
                  <SourceLocation note={source.evidenceLocation} />
                )}
                {source.useBoundary && <p>{source.useBoundary}</p>}
              </li>
            ))}
          </ol>
        </section>

        <section className={styles.boundary} aria-labelledby="boundary-title">
          <h2 id="boundary-title">このレビューの境界</h2>
          <h3>完了境界（completion_boundary）</h3>
          <p>{city.completionBoundary}</p>
          <h3>品質境界（quality_boundary）</h3>
          <p>{city.qualityBoundary}</p>
          <h3>次の工程</h3>
          <p>{city.nextAction}</p>
          <p className={styles.boundaryNote}>
            このページは進捗と根拠の透明性を示すものであり、自治体の政策成果や優劣を示すランキングではありません。
          </p>
          <div className={styles.introLinks}>
            <Link href="/methodology">判定方法を見る →</Link>
            <Link href="/corrections">誤りを報告する →</Link>
            <a href={sourcePrefix + city.packagePaths.planReview} target="_blank" rel="noreferrer">
              計画レビューの正本（GitHub） ↗
            </a>
            <a href={sourcePrefix + city.packagePaths.fiscalRecords} target="_blank" rel="noreferrer">
              財政レコードの正本（GitHub） ↗
            </a>
            <a href={sourcePrefix + city.packagePaths.evidencePackets} target="_blank" rel="noreferrer">
              Evidenceの正本（GitHub） ↗
            </a>
            <a href={sourcePrefix + city.packagePaths.sourceCatalog} target="_blank" rel="noreferrer">
              出典目録の正本（GitHub） ↗
            </a>
          </div>
        </section>
      </div>
      </main>
      <SiteFooter />
    </>
  );
}
