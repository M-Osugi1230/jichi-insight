"use client";

import { useDeferredValue, useMemo, useState } from "react";

import {
  aichiValueRoleLabels,
  reviewedAichiPolicyDirections,
  reviewedAichiPolicyIndicators,
} from "@/lib/aichiIndicators";

import { StatusBadge } from "./StatusBadge";
import styles from "./AichiIndicatorExplorer.module.css";

export function AichiIndicatorExplorer() {
  const [query, setQuery] = useState("");
  const [directionCode, setDirectionCode] = useState("all");
  const deferredQuery = useDeferredValue(query.trim().toLocaleLowerCase("ja-JP"));

  const filteredIndicators = useMemo(
    () =>
      reviewedAichiPolicyIndicators.filter((indicator) => {
        const matchesDirection =
          directionCode === "all" || indicator.policy_direction_code === directionCode;
        const searchable = [
          indicator.policy_direction_name_original,
          indicator.indicator_name_original,
          indicator.quality_note,
          ...indicator.series.flatMap((series) => [
            series.label ?? "",
            series.unit_original,
            series.comparability_note_original,
            ...series.values.flatMap((value) => [
              value.period,
              value.value_text_original,
              value.aggregation_scope,
            ]),
          ]),
        ]
          .join(" ")
          .toLocaleLowerCase("ja-JP");
        return matchesDirection &&
          (deferredQuery.length === 0 || searchable.includes(deferredQuery));
      }),
    [deferredQuery, directionCode],
  );

  function reset() {
    setQuery("");
    setDirectionCode("all");
  }

  return (
    <div className={styles.explorer}>
      <div className={styles.controls}>
        <div className={styles.searchField}>
          <label htmlFor="aichi-indicator-search">指標名・値・年度から探す</label>
          <input
            id="aichi-indicator-search"
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="例：健康寿命、2026年度、46％削減"
          />
        </div>
        <div className={styles.directionField}>
          <label htmlFor="aichi-indicator-direction">政策の方向性</label>
          <select
            id="aichi-indicator-direction"
            value={directionCode}
            onChange={(event) => setDirectionCode(event.target.value)}
          >
            <option value="all">基本目標＋10方向すべて</option>
            {reviewedAichiPolicyDirections.map((direction) => (
              <option key={direction.code} value={direction.code}>
                {direction.code} {direction.name_original}（{direction.indicator_row_count}件）
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className={styles.resultBar}>
        <p aria-live="polite"><strong>{filteredIndicators.length}</strong>件を表示</p>
        {query || directionCode !== "all" ? (
          <button type="button" onClick={reset}>絞り込みを解除</button>
        ) : (
          <span>公式資料掲載順</span>
        )}
      </div>

      {filteredIndicators.length ? (
        <div className={styles.cardGrid}>
          {filteredIndicators.map((indicator) => (
            <article className={styles.card} key={indicator.id}>
              <div className={styles.cardTop}>
                <span>
                  {indicator.policy_direction_code} / {indicator.policy_direction_name_original}
                </span>
                <StatusBadge label="Reviewed" tone="verified" />
              </div>

              <h3>{indicator.indicator_name_original}</h3>

              <div className={styles.badges}>
                {indicator.repost_of ? <span>再掲・重複集計しない</span> : null}
                {indicator.target_revision_status === "revised_in_2025_report" ? (
                  <span>進捗目標の改定あり</span>
                ) : null}
                {indicator.target_series_count === 0 ? <span>数値目標なし</span> : null}
              </div>

              <div className={styles.seriesList}>
                {indicator.series.map((series, seriesIndex) => (
                  <section key={`${indicator.id}-${seriesIndex}`}>
                    {series.label ? <h4>{series.label}</h4> : null}
                    <div className={styles.valueGrid}>
                      {series.values.map((value) => (
                        <div key={`${indicator.id}-${seriesIndex}-${value.role}-${value.period}`}>
                          <span>{aichiValueRoleLabels[value.role]}</span>
                          <strong>{value.value_text_original}</strong>
                          <small>{value.period}</small>
                        </div>
                      ))}
                    </div>
                    {series.comparability_note_original ? (
                      <p className={styles.note}>{series.comparability_note_original}</p>
                    ) : null}
                  </section>
                ))}
              </div>

              {indicator.quality_note ? (
                <div className={styles.boundary}>
                  <strong>データ上の境界</strong>
                  <p>{indicator.quality_note}</p>
                </div>
              ) : null}

              <footer>
                <span>公式指標一覧 p.{indicator.source_page}</span>
                <span>年次現状値 接続済み {indicator.linked_current_series_count}系列</span>
                <span>政策評価 未判定</span>
              </footer>
            </article>
          ))}
        </div>
      ) : (
        <div className={styles.emptyState}>
          <p>条件に一致する進捗管理指標はありません。</p>
          <button type="button" onClick={reset}>56件すべてを表示</button>
        </div>
      )}
    </div>
  );
}
