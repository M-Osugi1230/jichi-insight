"use client";

import Link from "next/link";
import { useMemo, useState } from "react";

import {
  coverageStageLabel,
  coverageStageTone,
  nationwidePrefectureCoverage,
  planCurrencyLabel,
  regionOrder,
  type CoverageStage,
} from "@/lib/nationwideCoverage";

import { StatusBadge } from "./StatusBadge";
import styles from "./CoverageExplorer.module.css";

type QuickFilter = "all" | "official" | "current" | "reviewed";

const quickFilters: Array<{ value: QuickFilter; label: string }> = [
  { value: "all", label: "すべて" },
  { value: "official", label: "公式入口確認済み" },
  { value: "current", label: "現行計画確認済み" },
  { value: "reviewed", label: "Reviewed公開" },
];

const planReviewLabels = {
  not_started: "未着手",
  indexed: "計画入口確認済み",
  reviewed: "Reviewed",
  verified: "Verified",
} as const;

const stageDescriptions: Record<CoverageStage, string> = {
  registered: "全国一覧への登録のみ。公式入口はまだ確認していません。",
  official_entry_verified: "自治体の公式入口を確認済み。計画資料は未索引です。",
  source_cataloged: "計画資料の入口を索引済み。現行性と本文の確認段階は項目ごとに表示します。",
  reviewed_data: "一次資料と人の照合を通過したデータを公開しています。",
};

function countForFilter(filter: QuickFilter) {
  if (filter === "official") {
    return nationwidePrefectureCoverage.filter(
      (record) => record.officialEntryStatus === "verified",
    ).length;
  }
  if (filter === "current") {
    return nationwidePrefectureCoverage.filter(
      (record) => record.planCurrencyStatus === "current_confirmed",
    ).length;
  }
  if (filter === "reviewed") {
    return nationwidePrefectureCoverage.filter(
      (record) => record.coverageStage === "reviewed_data",
    ).length;
  }
  return nationwidePrefectureCoverage.length;
}

export function CoverageExplorer() {
  const [query, setQuery] = useState("");
  const [region, setRegion] = useState("all");
  const [quickFilter, setQuickFilter] = useState<QuickFilter>("all");

  const filteredGroups = useMemo(() => {
    const normalizedQuery = query.trim().toLocaleLowerCase("ja-JP");
    const records = nationwidePrefectureCoverage.filter((record) => {
      const matchesQuery =
        normalizedQuery.length === 0 ||
        [record.name, record.region, record.planSource?.title ?? ""]
          .join(" ")
          .toLocaleLowerCase("ja-JP")
          .includes(normalizedQuery);
      const matchesRegion = region === "all" || record.region === region;
      const matchesQuickFilter =
        quickFilter === "all" ||
        (quickFilter === "official" && record.officialEntryStatus === "verified") ||
        (quickFilter === "current" &&
          record.planCurrencyStatus === "current_confirmed") ||
        (quickFilter === "reviewed" && record.coverageStage === "reviewed_data");

      return matchesQuery && matchesRegion && matchesQuickFilter;
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
            placeholder="例：東京都、沖縄、総合計画"
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
          <legend>確認できた段階</legend>
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
                {group.records.map((record) => (
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

                    <p className={styles.stageDescription}>
                      {stageDescriptions[record.coverageStage]}
                    </p>

                    <dl className={styles.prefectureFacts}>
                      <div>
                        <dt>計画資料</dt>
                        <dd>{record.planSource?.title ?? "未索引"}</dd>
                      </div>
                      <div>
                        <dt>資料確認</dt>
                        <dd>{planReviewLabels[record.planReviewStatus]}</dd>
                      </div>
                      <div>
                        <dt>現行性</dt>
                        <dd>{planCurrencyLabel(record.planCurrencyStatus)}</dd>
                      </div>
                      <div>
                        <dt>自治体ページ</dt>
                        <dd>{record.publicHref ? "公開中" : "未公開"}</dd>
                      </div>
                    </dl>

                    <div className={styles.actions}>
                      {record.publicHref ? (
                        <Link href={record.publicHref}>自治体ページ</Link>
                      ) : null}
                      {record.planSource ? (
                        <a href={record.planSource.url} target="_blank" rel="noreferrer">
                          計画資料 ↗
                        </a>
                      ) : null}
                      <a href={record.official_url} target="_blank" rel="noreferrer">
                        {record.officialEntryStatus === "verified"
                          ? "公式サイト ↗"
                          : "公式URL候補 ↗"}
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
          <button type="button" onClick={resetFilters}>すべて表示する</button>
        </div>
      )}
    </div>
  );
}
