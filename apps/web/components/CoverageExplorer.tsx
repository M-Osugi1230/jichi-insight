"use client";

import Link from "next/link";
import { useMemo, useState } from "react";

import { aichiPolicyIndicatorStats } from "@/lib/aichiIndicators";
import { hiroshimaIndicatorStats } from "@/lib/hiroshimaIndicators";
import { kagawaIndicatorStats } from "@/lib/kagawaIndicators";
import {
  nationwidePrefectureCoverage,
  nationwideSourceInventoryByCode,
  planCurrencyLabel,
  publicationStatusLabel,
  regionOrder,
  sourceInventoryCategoryLabel,
  sourceInventoryCategoryOrder,
  type SourceInventoryCategory,
  type SourceInventoryStatus,
} from "@/lib/nationwideCoverage";
import { okinawaIndicatorStats } from "@/lib/okinawaIndicators";
import { osakaIndicatorStats } from "@/lib/osakaIndicators";
import { tokyoPolicyTargetStats } from "@/lib/tokyoPolicyTargets";

import { StatusBadge } from "./StatusBadge";
import styles from "./CoverageExplorer.module.css";

type QuickFilter = "all" | "public" | "kpi" | "evaluation" | "budget";

const statusLabels: Record<SourceInventoryStatus, string> = {
  not_indexed: "未索引",
  indexed: "索引済",
  reviewed: "照合済",
  linked: "接続済",
};

const quickFilters: Array<{
  value: QuickFilter;
  label: string;
  category?: SourceInventoryCategory;
}> = [
  { value: "all", label: "すべて" },
  { value: "public", label: "自治体ページ公開中" },
  { value: "kpi", label: "KPI資料あり", category: "kpi_source" },
  { value: "evaluation", label: "年度評価あり", category: "annual_evaluation" },
  { value: "budget", label: "予算・決算あり", category: "budget" },
];

function displayedSourceStatus(
  prefectureCode: string,
  category: SourceInventoryCategory,
  status: SourceInventoryStatus,
): SourceInventoryStatus {
  const tokyoReviewed =
    prefectureCode === "13" && tokyoPolicyTargetStats.reviewedTargetGroups > 0;
  const aichiReviewed =
    prefectureCode === "23" && aichiPolicyIndicatorStats.indicatorRows > 0;
  const osakaReviewed =
    prefectureCode === "27" && osakaIndicatorStats.indicatorRows > 0;
  const hiroshimaReviewed =
    prefectureCode === "34" && hiroshimaIndicatorStats.reviewedIndicators > 0;
  const kagawaReviewed =
    prefectureCode === "37" && kagawaIndicatorStats.reviewedIndicators > 0;
  const okinawaReviewed =
    prefectureCode === "47" && okinawaIndicatorStats.reviewedIndicators > 0;
  if (
    category === "kpi_source" &&
    (
      tokyoReviewed ||
      aichiReviewed ||
      osakaReviewed ||
      hiroshimaReviewed ||
      kagawaReviewed ||
      okinawaReviewed
    ) &&
    status === "indexed"
  ) {
    return "reviewed";
  }
  return status;
}

function isIndexed(status: SourceInventoryStatus | undefined) {
  return status !== undefined && status !== "not_indexed";
}

function matchesQuickFilter(
  filter: QuickFilter,
  record: (typeof nationwidePrefectureCoverage)[number],
) {
  if (filter === "all") return true;
  if (filter === "public") return record.publicationStatus === "published";
  const definition = quickFilters.find((item) => item.value === filter);
  const inventory = nationwideSourceInventoryByCode.get(record.prefecture_code);
  return definition?.category
    ? isIndexed(inventory?.sources[definition.category])
    : false;
}

function countForFilter(filter: QuickFilter) {
  return nationwidePrefectureCoverage.filter((record) =>
    matchesQuickFilter(filter, record),
  ).length;
}

export function CoverageExplorer() {
  const [query, setQuery] = useState("");
  const [region, setRegion] = useState("all");
  const [quickFilter, setQuickFilter] = useState<QuickFilter>("all");

  const filteredGroups = useMemo(() => {
    const normalizedQuery = query.trim().toLocaleLowerCase("ja-JP");
    const records = nationwidePrefectureCoverage.filter((record) => {
      const inventory = nationwideSourceInventoryByCode.get(record.prefecture_code);
      const matchesQuery =
        normalizedQuery.length === 0 ||
        [
          record.name,
          record.region,
          record.planSource?.title ?? "",
          inventory?.next_action ?? "",
        ]
          .join(" ")
          .toLocaleLowerCase("ja-JP")
          .includes(normalizedQuery);
      const matchesRegion = region === "all" || record.region === region;

      return matchesQuery && matchesRegion && matchesQuickFilter(quickFilter, record);
    });

    return regionOrder
      .map((regionName) => ({
        region: regionName,
        records: records.filter((record) => record.region === regionName),
      }))
      .filter((group) => group.records.length > 0);
  }, [query, quickFilter, region]);

  const resultCount = filteredGroups.reduce(
    (total, group) => total + group.records.length,
    0,
  );
  const hasActiveFilter = query.length > 0 || region !== "all" || quickFilter !== "all";

  function resetFilters() {
    setQuery("");
    setRegion("all");
    setQuickFilter("all");
  }

  return (
    <div className={styles.explorer}>
      <div className={styles.filterPanel}>
        <div className={styles.searchGroup}>
          <label htmlFor="coverage-search">都道府県・計画名から探す</label>
          <input
            id="coverage-search"
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="例：宮城県、沖縄、長期ビジョン"
          />
        </div>
        <div className={styles.regionGroup}>
          <label htmlFor="coverage-region">地域</label>
          <select
            id="coverage-region"
            value={region}
            onChange={(event) => setRegion(event.target.value)}
          >
            <option value="all">全国</option>
            {regionOrder.map((regionName) => (
              <option value={regionName} key={regionName}>{regionName}</option>
            ))}
          </select>
        </div>
        <fieldset className={styles.stageGroup}>
          <legend>確認したい資料の深さ</legend>
          <div className={styles.filterChips}>
            {quickFilters.map((filter) => (
              <button
                type="button"
                className={quickFilter === filter.value ? styles.activeChip : undefined}
                aria-pressed={quickFilter === filter.value}
                onClick={() => setQuickFilter(filter.value)}
                key={filter.value}
              >
                <span>{filter.label}</span>
                <strong>{countForFilter(filter.value)}</strong>
              </button>
            ))}
          </div>
        </fieldset>
      </div>

      <div className={styles.legend} aria-label="資料状態の凡例">
        <span>資料状態</span>
        {(Object.keys(statusLabels) as SourceInventoryStatus[]).map((status) => (
          <span className={styles[`status_${status}`]} key={status}>{statusLabels[status]}</span>
        ))}
      </div>

      <div className={styles.resultBar}>
        <p aria-live="polite"><strong>{resultCount}</strong>都道府県を表示</p>
        {hasActiveFilter ? (
          <button type="button" onClick={resetFilters}>絞り込みを解除</button>
        ) : (
          <span>都道府県コード順</span>
        )}
      </div>

      {filteredGroups.length > 0 ? (
        <div className={styles.regionStack}>
          {filteredGroups.map((group) => (
            <section className={styles.regionSection} key={group.region}>
              <div className={styles.regionHeader}>
                <h3>{group.region}</h3>
                <span>{group.records.length}都道府県</span>
              </div>
              <div className={styles.prefectureGrid}>
                {group.records.map((record) => {
                  const inventory = nationwideSourceInventoryByCode.get(record.prefecture_code);
                  const nextAction =
                    record.prefecture_code === "13"
                      ? "政策目標一覧60ページ・25分野・304目標カードをReviewed済み。次に年度実績を定義照合する。"
                      : record.prefecture_code === "23"
                        ? `進捗管理指標${aichiPolicyIndicatorStats.indicatorRows}件・${aichiPolicyIndicatorStats.indicatorSeries}系列をReviewed済み。次に管理事業評価との対応を検証する。`
                        : record.prefecture_code === "27"
                          ? `現行戦略の${osakaIndicatorStats.indicatorRows}指標・${osakaIndicatorStats.indicatorSeries}系列をReviewed済み。次に事業一覧と年次更新を別レイヤーで接続する。`
                          : record.prefecture_code === "34"
                            ? `改定版ビジョンの${hiroshimaIndicatorStats.reviewedIndicators}指標をReviewed済み。次に新アクションプランと年度実績を定義照合する。`
                            : record.prefecture_code === "37"
                              ? `延長後計画の${kagawaIndicatorStats.reviewedIndicators}指標・Evidence ${kagawaIndicatorStats.evidencePackets}件をReviewed済み。次に行政評価と年度実績を接続する。`
                              : record.prefecture_code === "47"
                                ? `現行中期計画の${okinawaIndicatorStats.reviewedIndicators}指標（主要${okinawaIndicatorStats.majorIndicators}・成果${okinawaIndicatorStats.outcomeIndicators}）をReviewed済み。次に過年度PDCA実績を定義照合する。`
                                : inventory?.next_action ?? "資料インベントリを確認中";
                  return (
                    <article className={styles.prefectureCard} key={record.prefecture_code}>
                      <div className={styles.prefectureTop}>
                        <div>
                          <span className={styles.code}>{record.prefecture_code} / {record.region}</span>
                          <h4>{record.name}</h4>
                        </div>
                        <StatusBadge
                          label={record.publicationStatus === "published" ? "自治体ページ公開中" : "現行計画確認済み"}
                          tone={record.publicationStatus === "published" ? "verified" : "progress"}
                        />
                      </div>

                      <div className={styles.sourceDepth} aria-label={`${record.name}の資料カバレッジ`}>
                        {sourceInventoryCategoryOrder.map((category) => {
                          const baseStatus = inventory?.sources[category] ?? "not_indexed";
                          const status = displayedSourceStatus(
                            record.prefecture_code,
                            category,
                            baseStatus,
                          );
                          return (
                            <div className={styles[`status_${status}`]} key={category}>
                              <dt>{sourceInventoryCategoryLabel(category)}</dt>
                              <dd>{statusLabels[status]}</dd>
                            </div>
                          );
                        })}
                      </div>

                      <dl className={styles.prefectureFacts}>
                        <div>
                          <dt>現行の政策計画</dt>
                          <dd>{record.planSource?.title ?? "未索引"}</dd>
                        </div>
                        <div>
                          <dt>現行性</dt>
                          <dd>{planCurrencyLabel(record.planCurrencyStatus)}</dd>
                        </div>
                        <div>
                          <dt>公開状態</dt>
                          <dd>{publicationStatusLabel(record.publicationStatus)}</dd>
                        </div>
                        <div>
                          <dt>次に確認すること</dt>
                          <dd>{nextAction}</dd>
                        </div>
                      </dl>

                      <div className={styles.actions}>
                        {record.publicHref ? <Link href={record.publicHref}>詳細ページ</Link> : null}
                        {record.planSource ? (
                          <a href={record.planSource.url} target="_blank" rel="noreferrer">政策計画 ↗</a>
                        ) : null}
                        <a href={record.official_url} target="_blank" rel="noreferrer">公式サイト ↗</a>
                      </div>
                    </article>
                  );
                })}
              </div>
            </section>
          ))}
        </div>
      ) : (
        <div className={styles.emptyState}>
          <p>条件に一致する都道府県はありません。</p>
          <button type="button" onClick={resetFilters}>すべて表示する</button>
        </div>
      )}
    </div>
  );
}
