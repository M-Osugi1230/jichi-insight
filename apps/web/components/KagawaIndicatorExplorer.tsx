"use client";

import { useDeferredValue, useMemo, useState } from "react";

import { reviewedKagawaIndicators } from "@/lib/kagawaIndicators";

import { StatusBadge } from "./StatusBadge";
import styles from "./KagawaIndicatorExplorer.module.css";

type Filter = "all" | "revised" | "unchanged" | "reposted";

const filters: Array<{ value: Filter; label: string }> = [
  { value: "all", label: "すべて" },
  { value: "revised", label: "目標更新あり" },
  { value: "unchanged", label: "目標据え置き" },
  { value: "reposted", label: "再掲指標" },
];

export function KagawaIndicatorExplorer() {
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState<Filter>("all");
  const deferredQuery = useDeferredValue(query.trim().toLocaleLowerCase("ja-JP"));

  const filtered = useMemo(
    () =>
      reviewedKagawaIndicators.filter((indicator) => {
        const matchesFilter =
          filter === "all" ||
          (filter === "revised" && indicator.targetRevised) ||
          (filter === "unchanged" && !indicator.targetRevised) ||
          (filter === "reposted" && indicator.reposted);
        const searchable = [
          indicator.number,
          indicator.name,
          indicator.currentValue,
          indicator.targetR7,
          indicator.targetR8,
          indicator.sourcePage,
        ]
          .join(" ")
          .toLocaleLowerCase("ja-JP");
        return matchesFilter && (
          deferredQuery.length === 0 || searchable.includes(deferredQuery)
        );
      }),
    [deferredQuery, filter],
  );

  function reset() {
    setQuery("");
    setFilter("all");
  }

  return (
    <div className={styles.explorer}>
      <div className={styles.controls}>
        <div className={styles.search}>
          <label htmlFor="kagawa-indicator-search">指標名・値・番号から探す</label>
          <input
            id="kagawa-indicator-search"
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="例：待機児童、観光、135、R12"
          />
        </div>
        <fieldset>
          <legend>目標の変更状態</legend>
          <div className={styles.chips}>
            {filters.map((item) => (
              <button
                type="button"
                aria-pressed={filter === item.value}
                className={filter === item.value ? styles.active : undefined}
                onClick={() => setFilter(item.value)}
                key={item.value}
              >
                {item.label}
              </button>
            ))}
          </div>
        </fieldset>
      </div>

      <div className={styles.resultBar}>
        <p aria-live="polite"><strong>{filtered.length}</strong>指標を表示</p>
        {query || filter !== "all" ? (
          <button type="button" onClick={reset}>絞り込みを解除</button>
        ) : <span>指標番号順</span>}
      </div>

      {filtered.length ? (
        <div className={styles.grid}>
          {filtered.map((indicator) => (
            <article className={styles.card} key={indicator.id}>
              <div className={styles.top}>
                <span>指標 {indicator.number} / p.{indicator.sourcePage}</span>
                <StatusBadge label="Reviewed" tone="verified" />
              </div>
              <h3>{indicator.name}</h3>
              <div className={styles.badges}>
                {indicator.targetRevised ? <span>目標更新</span> : <span>据え置き</span>}
                {indicator.reposted ? <span>再掲あり</span> : null}
                {indicator.number === 135 ? <span>参考指標</span> : null}
              </div>
              <dl>
                <div><dt>現状値</dt><dd>{indicator.currentValue}</dd></div>
                <div><dt>延長前の目標</dt><dd>{indicator.targetR7}</dd></div>
                <div><dt>延長後の目標</dt><dd>{indicator.targetR8}</dd></div>
              </dl>
              <footer>
                <span>{indicator.evidenceId}</span>
                <span>政策評価 未判定</span>
              </footer>
            </article>
          ))}
        </div>
      ) : (
        <div className={styles.empty}>
          <p>条件に一致する指標はありません。</p>
          <button type="button" onClick={reset}>135指標をすべて表示</button>
        </div>
      )}
    </div>
  );
}
