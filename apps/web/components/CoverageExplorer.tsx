"use client";

import Link from "next/link";
import { useMemo, useState } from "react";

import { regionOrder } from "@/lib/nationwideCoverage";
import {
  evidenceDepthLabels,
  evidenceDepthOrder,
  evidenceDepthStatusLabels,
  reviewedPrefectureCoverage,
  reviewProfileLabels,
  type ReviewProfile,
} from "@/lib/reviewedCoverage";

import styles from "./CoverageExplorer.module.css";

type QuickFilter =
  | "all"
  | "dedicated"
  | "actuals_linked"
  | "finance_reviewed"
  | "target_statements";

const quickFilters: Array<{
  value: QuickFilter;
  label: string;
}> = [
  { value: "all", label: "47都道府県" },
  { value: "dedicated", label: "専用分析" },
  { value: "actuals_linked", label: "実績接続" },
  { value: "finance_reviewed", label: "財政Reviewed" },
  { value: "target_statements", label: "目標原文" },
];

function matchesQuickFilter(
  filter: QuickFilter,
  record: (typeof reviewedPrefectureCoverage)[number],
) {
  if (filter === "all") return true;
  if (filter === "dedicated") return record.dedicatedPage;
  return record.reviewProfile === filter;
}

function countForFilter(filter: QuickFilter) {
  return reviewedPrefectureCoverage.filter((record) =>
    matchesQuickFilter(filter, record),
  ).length;
}

function formatNumber(value: number) {
  return new Intl.NumberFormat("ja-JP").format(value);
}

export function CoverageExplorer() {
  const [query, setQuery] = useState("");
  const [region, setRegion] = useState("all");
  const [quickFilter, setQuickFilter] = useState<QuickFilter>("all");

  const filteredGroups = useMemo(() => {
    const normalizedQuery = query.trim().toLocaleLowerCase("ja-JP");
    const records = reviewedPrefectureCoverage.filter((record) => {
      const matchesQuery =
        normalizedQuery.length === 0 ||
        [
          record.name,
          record.region,
          record.planTitle,
          record.planPeriod ?? "",
          record.recordLabel,
        ]
          .join(" ")
          .toLocaleLowerCase("ja-JP")
          .includes(normalizedQuery);
      const matchesRegion = region === "all" || record.region === region;

      return (
        matchesQuery &&
        matchesRegion &&
        matchesQuickFilter(quickFilter, record)
      );
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
  const hasActiveFilter =
    query.length > 0 || region !== "all" || quickFilter !== "all";

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
            placeholder="例：宮城県、沖縄、総合計画"
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
              <option value={regionName} key={regionName}>
                {regionName}
              </option>
            ))}
          </select>
        </div>
        <fieldset className={styles.stageGroup}>
          <legend>読みたいデータの深さ</legend>
          <div className={styles.filterChips}>
            {quickFilters.map((filter) => (
              <button
                type="button"
                className={
                  quickFilter === filter.value ? styles.activeChip : undefined
                }
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

      <div className={styles.legend} aria-label="接続状態の凡例">
        <span>5段階の根拠</span>
        <span className={styles.status_reviewed}>照合済</span>
        <span className={styles.status_linked}>接続済</span>
        <span className={styles.status_indexed}>索引済</span>
        <span className={styles.status_not_indexed}>未索引</span>
      </div>

      <div className={styles.resultBar}>
        <p aria-live="polite">
          <strong>{resultCount}</strong>都道府県を表示
        </p>
        {hasActiveFilter ? (
          <button type="button" onClick={resetFilters}>
            絞り込みを解除
          </button>
        ) : (
          <span>地域・都道府県コード順</span>
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
                {group.records.map((record) => (
                  <article
                    className={styles.prefectureCard}
                    key={record.code}
                  >
                    <div className={styles.prefectureTop}>
                      <div>
                        <span className={styles.code}>
                          {record.code} / {record.region}
                        </span>
                        <h4>{record.name}</h4>
                      </div>
                      <span
                        className={`${styles.profileBadge} ${styles[`profile_${record.reviewProfile as ReviewProfile}`]}`}
                      >
                        {reviewProfileLabels[record.reviewProfile]}
                      </span>
                    </div>

                    <div className={styles.reviewCounts}>
                      <div>
                        <span>Reviewed {record.recordLabel}</span>
                        <strong>{formatNumber(record.reviewedRecords)}</strong>
                      </div>
                      <div>
                        <span>Evidence Packet</span>
                        <strong>{formatNumber(record.evidencePackets)}</strong>
                      </div>
                    </div>

                    <dl
                      className={styles.depthRail}
                      aria-label={`${record.name}の根拠接続状況`}
                    >
                      {evidenceDepthOrder.map((key) => {
                        const status = record.depth[key];
                        return (
                          <div className={styles[`status_${status}`]} key={key}>
                            <dt>{evidenceDepthLabels[key]}</dt>
                            <dd>{evidenceDepthStatusLabels[status]}</dd>
                          </div>
                        );
                      })}
                    </dl>

                    <div className={styles.plan}>
                      <span>確認した政策計画</span>
                      <p>{record.planTitle}</p>
                      {record.planPeriod ? <small>{record.planPeriod}</small> : null}
                    </div>

                    {record.extractionErrors > 0 ? (
                      <p className={styles.caution}>
                        抽出エラー {record.extractionErrors}件を欠損として保持
                      </p>
                    ) : null}

                    <div className={styles.actions}>
                      <Link href={record.route}>根拠を読む</Link>
                      <a
                        href={record.planUrl}
                        target="_blank"
                        rel="noreferrer"
                      >
                        公式計画 ↗
                      </a>
                    </div>
                  </article>
                ))}
              </div>
            </section>
          ))}
        </div>
      ) : (
        <div className={styles.emptyState}>
          <p>条件に一致する都道府県はありません。</p>
          <button type="button" onClick={resetFilters}>
            すべて表示する
          </button>
        </div>
      )}
    </div>
  );
}
