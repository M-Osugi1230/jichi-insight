"use client";

import { useDeferredValue, useMemo, useState } from "react";

import {
  osakaIndicatorPillars,
  osakaLayerLabels,
  osakaValueRoleLabels,
  reviewedOsakaIndicators,
  type OsakaIndicator,
} from "@/lib/osakaIndicators";

import { StatusBadge } from "./StatusBadge";
import styles from "./OsakaIndicatorExplorer.module.css";

type LayerFilter = "all" | OsakaIndicator["indicator_layer"];

export function OsakaIndicatorExplorer() {
  const [query, setQuery] = useState("");
  const [layer, setLayer] = useState<LayerFilter>("all");
  const [pillar, setPillar] = useState("all");
  const deferredQuery = useDeferredValue(query.trim().toLocaleLowerCase("ja-JP"));

  const filtered = useMemo(
    () =>
      reviewedOsakaIndicators.filter((indicator) => {
        const matchesLayer = layer === "all" || indicator.indicator_layer === layer;
        const matchesPillar = pillar === "all" || indicator.pillar_original === pillar;
        const searchable = [
          indicator.indicator_name_original,
          indicator.pillar_original,
          indicator.category_original,
          indicator.comparability_note_original,
          ...indicator.series.flatMap((series) => [
            series.label_original ?? "",
            series.unit_original,
            ...series.values.flatMap((value) => [value.period, value.value_text_original]),
          ]),
        ]
          .join(" ")
          .toLocaleLowerCase("ja-JP");
        return matchesLayer && matchesPillar &&
          (deferredQuery.length === 0 || searchable.includes(deferredQuery));
      }),
    [deferredQuery, layer, pillar],
  );

  function reset() {
    setQuery("");
    setLayer("all");
    setPillar("all");
  }

  return (
    <div className={styles.explorer}>
      <div className={styles.controls}>
        <div>
          <label htmlFor="osaka-indicator-search">指標名・値・年度から探す</label>
          <input
            id="osaka-indicator-search"
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="例：GDP、健康寿命、幸福、2024年"
          />
        </div>
        <div>
          <label htmlFor="osaka-indicator-layer">指標レイヤー</label>
          <select id="osaka-indicator-layer" value={layer} onChange={(event) => setLayer(event.target.value as LayerFilter)}>
            <option value="all">すべて</option>
            <option value="strategy_target">戦略目標</option>
            <option value="objective_kpi">客観KPI</option>
            <option value="subjective_wellbeing">主観・Well-Being</option>
          </select>
        </div>
        <div>
          <label htmlFor="osaka-indicator-pillar">分野</label>
          <select id="osaka-indicator-pillar" value={pillar} onChange={(event) => setPillar(event.target.value)}>
            <option value="all">全分野</option>
            {osakaIndicatorPillars.map((item) => <option key={item} value={item}>{item}</option>)}
          </select>
        </div>
      </div>

      <div className={styles.resultBar}>
        <p aria-live="polite"><strong>{filtered.length}</strong>件を表示</p>
        {query || layer !== "all" || pillar !== "all" ? (
          <button type="button" onClick={reset}>絞り込みを解除</button>
        ) : <span>公式資料掲載順</span>}
      </div>

      {filtered.length ? (
        <div className={styles.grid}>
          {filtered.map((indicator) => (
            <article className={styles.card} key={indicator.id}>
              <div className={styles.top}>
                <span>{osakaLayerLabels[indicator.indicator_layer]} / {indicator.pillar_original}</span>
                <StatusBadge label="Reviewed" tone="verified" />
              </div>
              <p className={styles.category}>{indicator.category_original}</p>
              <h3>{indicator.indicator_name_original}</h3>
              <div className={styles.badges}>
                {indicator.response_scale === "0_to_10" ? <span>0〜10点尺度</span> : null}
                {indicator.response_scale === "1_to_5" ? <span>1〜5点尺度</span> : null}
                {indicator.response_scale === "1_to_5_reversed" ? <span>逆転項目</span> : null}
                {indicator.series.some((series) => series.values.some((value) => value.status === "missing")) ? <span>初回調査待ち</span> : null}
              </div>
              <div className={styles.seriesList}>
                {indicator.series.map((series, index) => (
                  <section key={`${indicator.id}-${index}`}>
                    {series.label_original ? <h4>{series.label_original}</h4> : null}
                    <div className={styles.values}>
                      {series.values.map((value) => (
                        <div key={`${indicator.id}-${index}-${value.role}-${value.period}`}>
                          <span>{osakaValueRoleLabels[value.role]}</span>
                          <strong>{value.value_text_original}</strong>
                          <small>{value.period}</small>
                        </div>
                      ))}
                    </div>
                  </section>
                ))}
              </div>
              <div className={styles.boundary}>
                <strong>比較上の境界</strong>
                <p>{indicator.comparability_note_original}</p>
              </div>
              <footer>
                <span>公式戦略 p.{indicator.source_page}</span>
                <span>旧ビジョン実績 別系統</span>
                <span>政策評価 未判定</span>
              </footer>
            </article>
          ))}
        </div>
      ) : (
        <div className={styles.empty}>
          <p>条件に一致する指標はありません。</p>
          <button type="button" onClick={reset}>83件すべてを表示</button>
        </div>
      )}
    </div>
  );
}
