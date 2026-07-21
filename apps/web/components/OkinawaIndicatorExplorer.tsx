"use client";

import { useDeferredValue, useMemo, useState } from "react";

import {
  compactOkinawaText,
  hasOkinawaNationalComparator,
  isOkinawaQualitativeTarget,
  reviewedOkinawaIndicators,
  type OkinawaIndicatorLayer,
} from "@/lib/okinawaIndicators";

import { StatusBadge } from "./StatusBadge";
import styles from "./OkinawaIndicatorExplorer.module.css";

type LayerFilter = "all" | OkinawaIndicatorLayer;
type AttributeFilter =
  | "all"
  | "remote_island"
  | "sdgs"
  | "national_present"
  | "national_missing"
  | "qualitative";

const attributeFilters: Array<{ value: AttributeFilter; label: string }> = [
  { value: "all", label: "すべて" },
  { value: "remote_island", label: "離島指標" },
  { value: "sdgs", label: "SDGs優先課題" },
  { value: "national_present", label: "全国比較あり" },
  { value: "national_missing", label: "全国比較なし" },
  { value: "qualitative", label: "定性目標" },
];

export function OkinawaIndicatorExplorer() {
  const [query, setQuery] = useState("");
  const [layer, setLayer] = useState<LayerFilter>("all");
  const [attribute, setAttribute] = useState<AttributeFilter>("all");
  const deferredQuery = useDeferredValue(query.trim().toLocaleLowerCase("ja-JP"));

  const filtered = useMemo(
    () =>
      reviewedOkinawaIndicators.filter((indicator) => {
        const hasNational = hasOkinawaNationalComparator(indicator);
        const matchesAttribute =
          attribute === "all" ||
          (attribute === "remote_island" &&
            Boolean(indicator.remote_island_marker_original)) ||
          (attribute === "sdgs" && Boolean(indicator.sdgs_priority_original)) ||
          (attribute === "national_present" && hasNational) ||
          (attribute === "national_missing" && !hasNational) ||
          (attribute === "qualitative" && isOkinawaQualitativeTarget(indicator));
        const searchable = [
          indicator.display_order,
          compactOkinawaText(indicator.policy_original),
          compactOkinawaText(indicator.indicator_name_original),
          compactOkinawaText(indicator.baseline_original),
          compactOkinawaText(indicator.target_r9_original),
          compactOkinawaText(indicator.national_current_original),
          compactOkinawaText(indicator.sdgs_priority_original),
        ]
          .join(" ")
          .toLocaleLowerCase("ja-JP");
        return (
          (layer === "all" || indicator.indicator_layer === layer) &&
          matchesAttribute &&
          (deferredQuery.length === 0 || searchable.includes(deferredQuery))
        );
      }),
    [attribute, deferredQuery, layer],
  );

  function reset() {
    setQuery("");
    setLayer("all");
    setAttribute("all");
  }

  const hasFilters = query.length > 0 || layer !== "all" || attribute !== "all";

  return (
    <div className={styles.explorer}>
      <div className={styles.controls}>
        <div className={styles.search}>
          <label htmlFor="okinawa-indicator-search">政策・指標名・値から探す</label>
          <input
            id="okinawa-indicator-search"
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="例：平均寿命、離島、観光、可能な限り減少"
          />
        </div>
        <div className={styles.layer}>
          <label htmlFor="okinawa-indicator-layer">指標レイヤー</label>
          <select
            id="okinawa-indicator-layer"
            value={layer}
            onChange={(event) => setLayer(event.target.value as LayerFilter)}
          >
            <option value="all">主要＋成果</option>
            <option value="major">主要指標</option>
            <option value="outcome">成果指標</option>
          </select>
        </div>
        <fieldset>
          <legend>属性</legend>
          <div className={styles.chips}>
            {attributeFilters.map((filter) => (
              <button
                type="button"
                aria-pressed={attribute === filter.value}
                className={attribute === filter.value ? styles.active : undefined}
                onClick={() => setAttribute(filter.value)}
                key={filter.value}
              >
                {filter.label}
              </button>
            ))}
          </div>
        </fieldset>
      </div>

      <div className={styles.resultBar}>
        <p aria-live="polite"><strong>{filtered.length}</strong>指標を表示</p>
        {hasFilters ? (
          <button type="button" onClick={reset}>絞り込みを解除</button>
        ) : <span>公式附属資料の掲載順</span>}
      </div>

      {filtered.length ? (
        <div className={styles.grid}>
          {filtered.map((indicator) => {
            const hasNational = hasOkinawaNationalComparator(indicator);
            const qualitative = isOkinawaQualitativeTarget(indicator);
            return (
              <article className={styles.card} key={indicator.indicator_id}>
                <div className={styles.top}>
                  <span>
                    {indicator.indicator_layer === "major" ? "主要" : "成果"}
                    {" / "}No.{indicator.display_order} / p.{indicator.source_pdf_page}
                  </span>
                  <StatusBadge label="Reviewed" tone="verified" />
                </div>
                <p className={styles.policy}>{compactOkinawaText(indicator.policy_original)}</p>
                <h3>{compactOkinawaText(indicator.indicator_name_original)}</h3>
                <div className={styles.badges}>
                  {indicator.remote_island_marker_original ? <span>離島指標</span> : null}
                  {indicator.sdgs_priority_original ? (
                    <span>{compactOkinawaText(indicator.sdgs_priority_original)}</span>
                  ) : null}
                  {hasNational ? <span>全国比較あり</span> : <span>全国比較なし</span>}
                  {qualitative ? <span>定性目標</span> : null}
                </div>
                <dl>
                  <div>
                    <dt>基準値</dt>
                    <dd>{compactOkinawaText(indicator.baseline_original)}</dd>
                  </div>
                  <div>
                    <dt>令和9年度目標</dt>
                    <dd>{compactOkinawaText(indicator.target_r9_original)}</dd>
                  </div>
                  <div>
                    <dt>全国の現状値</dt>
                    <dd>{compactOkinawaText(indicator.national_current_original)}</dd>
                  </div>
                </dl>
                <footer>
                  <span>{indicator.evidence_id}</span>
                  <span>政策評価 未判定</span>
                </footer>
              </article>
            );
          })}
        </div>
      ) : (
        <div className={styles.empty}>
          <p>条件に一致する指標はありません。</p>
          <button type="button" onClick={reset}>376指標をすべて表示</button>
        </div>
      )}
    </div>
  );
}
