"use client";

import { useMemo, useState } from "react";

import {
  hokkaidoIndicatorGroups,
  hokkaidoIndicatorReviewStats,
  hokkaidoReviewedIndicators,
  type HokkaidoIndicator,
  type HokkaidoIndicatorValue,
} from "@/lib/hokkaidoIndicators";

import { StatusBadge } from "./StatusBadge";
import styles from "./HokkaidoIndicatorExplorer.module.css";

type IndicatorFilter = "all" | "set" | "partial" | "missing_current" | "warning";

const filters: Array<{ value: IndicatorFilter; label: string }> = [
  { value: "all", label: "すべて" },
  { value: "set", label: "目標設定済み" },
  { value: "partial", label: "一部のみ設定" },
  { value: "missing_current", label: "現状値なし" },
  { value: "warning", label: "比較上の注意あり" },
];

const roleLabels: Record<HokkaidoIndicatorValue["role"], string> = {
  current: "現状値",
  intermediate_target: "中間目標",
  final_target: "最終目標",
};

const fieldByIndicatorId = new Map(
  hokkaidoIndicatorGroups.flatMap((group) =>
    group.indicators.map((indicator) => [
      indicator.id,
      {
        fieldId: group.fieldId,
        label: group.label,
        sourceDocumentUrl: group.sourceDocumentUrl,
      },
    ] as const),
  ),
);

function hasMissingCurrent(indicator: HokkaidoIndicator) {
  return indicator.series.some((series) => {
    const current = series.values.find((value) => value.role === "current");
    return !current || current.status === "not_available";
  });
}

function matchesFilter(indicator: HokkaidoIndicator, filter: IndicatorFilter) {
  if (filter === "set") return indicator.target_setting_status === "set";
  if (filter === "partial") return indicator.target_setting_status === "partially_set";
  if (filter === "missing_current") return hasMissingCurrent(indicator);
  if (filter === "warning") return indicator.comparability_note_original !== null;
  return true;
}

function countForFilter(filter: IndicatorFilter) {
  return hokkaidoReviewedIndicators.filter((indicator) =>
    matchesFilter(indicator, filter),
  ).length;
}

function valueLabel(value: HokkaidoIndicatorValue, unit: string) {
  if (value.status === "not_set") return "未設定";
  if (value.status === "not_available") return "値なし";
  if (value.status === "conditional") return value.value_text_original;
  const prefix = value.operator === "at_least" ? "以上" : value.operator === "at_most" ? "以下" : "";
  const visibleUnit = unit === "（単位なし）" ? "" : unit;
  return `${value.value_text_original}${visibleUnit}${prefix}`;
}

function targetStatusLabel(indicator: HokkaidoIndicator) {
  if (indicator.target_setting_status === "set") return "目標設定済み";
  if (indicator.target_setting_status === "partially_set") return "一部のみ設定";
  return "目標未設定";
}

export function HokkaidoIndicatorExplorer() {
  const [query, setQuery] = useState("");
  const [field, setField] = useState("all");
  const [filter, setFilter] = useState<IndicatorFilter>("all");

  const filteredIndicators = useMemo(() => {
    const normalizedQuery = query.trim().toLocaleLowerCase("ja-JP");
    return hokkaidoReviewedIndicators.filter((indicator) => {
      const group = fieldByIndicatorId.get(indicator.id);
      const matchesQuery =
        normalizedQuery.length === 0 ||
        [
          indicator.indicator_number,
          indicator.indicator_name_original,
          indicator.policy_orientation_original,
          indicator.indicator_explanation_original,
          group?.label ?? "",
        ]
          .join(" ")
          .toLocaleLowerCase("ja-JP")
          .includes(normalizedQuery);
      const matchesField = field === "all" || group?.fieldId === field;
      return matchesQuery && matchesField && matchesFilter(indicator, filter);
    });
  }, [field, filter, query]);

  const hasActiveFilter = query.length > 0 || field !== "all" || filter !== "all";

  function resetFilters() {
    setQuery("");
    setField("all");
    setFilter("all");
  }

  return (
    <div className={styles.explorer}>
      <div className={styles.filterPanel}>
        <div className={styles.searchGroup}>
          <label htmlFor="hokkaido-indicator-search">指標名・政策分野から探す</label>
          <input
            id="hokkaido-indicator-search"
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="例：観光、出生率、再生可能エネルギー"
          />
        </div>
        <div className={styles.fieldGroup}>
          <label htmlFor="hokkaido-indicator-field">Reviewed分野</label>
          <select
            id="hokkaido-indicator-field"
            value={field}
            onChange={(event) => setField(event.target.value)}
          >
            <option value="all">{hokkaidoIndicatorGroups.length}分野すべて</option>
            {hokkaidoIndicatorGroups.map((group) => (
              <option value={group.fieldId} key={group.id}>
                {group.label}（{group.indicators.length}）
              </option>
            ))}
          </select>
        </div>
        <fieldset className={styles.filterGroup}>
          <legend>確認したい状態</legend>
          <div className={styles.filterChips}>
            {filters.map((item) => (
              <button
                type="button"
                className={filter === item.value ? styles.activeChip : undefined}
                aria-pressed={filter === item.value}
                onClick={() => setFilter(item.value)}
                key={item.value}
              >
                <span>{item.label}</span>
                <strong>{countForFilter(item.value)}</strong>
              </button>
            ))}
          </div>
        </fieldset>
      </div>

      <div className={styles.resultBar}>
        <p aria-live="polite">
          <strong>{filteredIndicators.length}</strong>指標を表示
        </p>
        {hasActiveFilter ? (
          <button type="button" onClick={resetFilters}>絞り込みを解除</button>
        ) : (
          <span>公式番号順・指標1〜{hokkaidoIndicatorReviewStats.reviewedIndicators}</span>
        )}
      </div>

      {filteredIndicators.length > 0 ? (
        <div className={styles.indicatorList}>
          {filteredIndicators.map((indicator) => {
            const group = fieldByIndicatorId.get(indicator.id);
            return (
              <article className={styles.indicatorCard} key={indicator.id}>
                <div className={styles.cardNumber} aria-label={`指標${indicator.indicator_number}`}>
                  {String(indicator.indicator_number).padStart(3, "0")}
                </div>
                <div className={styles.cardBody}>
                  <div className={styles.cardHeader}>
                    <div>
                      <p>{group?.label} · {indicator.policy_orientation_original}</p>
                      <h3>{indicator.indicator_name_original}</h3>
                    </div>
                    <StatusBadge label="Reviewed" tone="verified" />
                  </div>

                  <div className={styles.seriesStack}>
                    {indicator.series.map((series, seriesIndex) => (
                      <section className={styles.series} key={`${indicator.id}-${series.label ?? seriesIndex}`}>
                        {series.label ? <h4>{series.label}</h4> : null}
                        <div className={styles.valueGrid}>
                          {series.values.map((value) => (
                            <div className={styles.valueCell} key={`${value.role}-${value.period ?? "none"}`}>
                              <span>{roleLabels[value.role]}</span>
                              <strong>{valueLabel(value, series.unit_original)}</strong>
                              <small>{value.period ?? "期間記載なし"}</small>
                            </div>
                          ))}
                        </div>
                      </section>
                    ))}
                  </div>

                  <div className={styles.cardStatus}>
                    <span>{targetStatusLabel(indicator)}</span>
                    <span>実績未接続</span>
                    <span>未評価</span>
                  </div>

                  {indicator.comparability_note_original ? (
                    <p className={styles.warning}>
                      <strong>比較上の注意</strong>
                      {indicator.comparability_note_original}
                    </p>
                  ) : (
                    <p className={styles.boundaryNote}>
                      年度別実績は未接続です。目標との差や達成率は算出していません。
                    </p>
                  )}

                  <details className={styles.details}>
                    <summary>指標の説明と根拠を見る</summary>
                    <dl>
                      <div><dt>指標の説明</dt><dd>{indicator.indicator_explanation_original}</dd></div>
                      <div><dt>目標設定の考え方</dt><dd>{indicator.target_setting_rationale_original}</dd></div>
                      <div><dt>根拠資料</dt><dd>公式指標PDF・PDFページ{indicator.source_page}</dd></div>
                    </dl>
                    {group ? (
                      <a href={group.sourceDocumentUrl} target="_blank" rel="noreferrer">
                        公式指標PDFを開く ↗
                      </a>
                    ) : null}
                  </details>
                </div>
              </article>
            );
          })}
        </div>
      ) : (
        <div className={styles.emptyState}>
          <p>条件に一致するReviewed指標はありません。</p>
          <button type="button" onClick={resetFilters}>
            {hokkaidoIndicatorReviewStats.reviewedIndicators}指標をすべて表示する
          </button>
        </div>
      )}
    </div>
  );
}
