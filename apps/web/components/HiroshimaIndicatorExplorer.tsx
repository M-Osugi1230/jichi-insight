"use client";

import { useDeferredValue, useMemo, useState } from "react";

import {
  hiroshimaIndicatorAreas,
  reviewedHiroshimaIndicators,
} from "@/lib/hiroshimaIndicators";

import { StatusBadge } from "./StatusBadge";
import styles from "./HiroshimaIndicatorExplorer.module.css";

export function HiroshimaIndicatorExplorer() {
  const [query, setQuery] = useState("");
  const [area, setArea] = useState("all");
  const deferredQuery = useDeferredValue(query.trim().toLocaleLowerCase("ja-JP"));

  const filtered = useMemo(
    () =>
      reviewedHiroshimaIndicators.filter((indicator) => {
        const searchable = [
          indicator.area,
          indicator.name,
          indicator.baseline,
          indicator.current,
          indicator.target,
          indicator.target_period,
          indicator.source,
          indicator.change,
        ]
          .join(" ")
          .toLocaleLowerCase("ja-JP");
        return (
          (area === "all" || indicator.area === area) &&
          (deferredQuery.length === 0 || searchable.includes(deferredQuery))
        );
      }),
    [area, deferredQuery],
  );

  function reset() {
    setQuery("");
    setArea("all");
  }

  return (
    <div className={styles.explorer}>
      <div className={styles.controls}>
        <div>
          <label htmlFor="hiroshima-indicator-search">指標名・値・出典から探す</label>
          <input
            id="hiroshima-indicator-search"
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="例：健康寿命、観光、R10、平均"
          />
        </div>
        <div>
          <label htmlFor="hiroshima-indicator-area">政策分野</label>
          <select
            id="hiroshima-indicator-area"
            value={area}
            onChange={(event) => setArea(event.target.value)}
          >
            <option value="all">全分野</option>
            {hiroshimaIndicatorAreas.map((item) => (
              <option value={item} key={item}>{item}</option>
            ))}
          </select>
        </div>
      </div>

      <div className={styles.resultBar}>
        <p aria-live="polite"><strong>{filtered.length}</strong>件を表示</p>
        {query || area !== "all" ? (
          <button type="button" onClick={reset}>絞り込みを解除</button>
        ) : <span>改定版ビジョン掲載順</span>}
      </div>

      {filtered.length ? (
        <div className={styles.grid}>
          {filtered.map((indicator) => {
            const pending = indicator.current === "―" || indicator.current.includes("新たに調査");
            const qualitative = indicator.target.includes("全ての国が参加");
            return (
              <article className={styles.card} key={indicator.id}>
                <div className={styles.top}>
                  <span>{indicator.area} / p.{indicator.page}</span>
                  <StatusBadge label="Reviewed" tone="verified" />
                </div>
                <h3>{indicator.name}</h3>
                <div className={styles.badges}>
                  {pending ? <span>測定待ち</span> : null}
                  {qualitative ? <span>定性目標</span> : null}
                  {indicator.change.includes("revised") ? <span>改定あり</span> : null}
                  {indicator.change.includes("replacement") ? <span>指標変更</span> : null}
                </div>
                <dl className={styles.values}>
                  <div><dt>基準値</dt><dd>{indicator.baseline}</dd></div>
                  <div><dt>最新値</dt><dd>{indicator.current}</dd></div>
                  <div><dt>{indicator.target_period}目標</dt><dd>{indicator.target}</dd></div>
                </dl>
                <div className={styles.source}>
                  <strong>公式出典</strong>
                  <p>{indicator.source}</p>
                </div>
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
          <button type="button" onClick={reset}>62件すべてを表示</button>
        </div>
      )}
    </div>
  );
}
