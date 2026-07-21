"use client";

import { useDeferredValue, useMemo, useState } from "react";

import {
  reviewedTokyoPolicyAreas,
  reviewedTokyoPolicyTargetCards,
  tokyoSemanticFlagLabels,
} from "@/lib/tokyoPolicyTargets";

import { StatusBadge } from "./StatusBadge";
import styles from "./TokyoPolicyTargetExplorer.module.css";

export function TokyoPolicyTargetExplorer() {
  const [query, setQuery] = useState("");
  const [areaCode, setAreaCode] = useState("all");
  const deferredQuery = useDeferredValue(query.trim().toLocaleLowerCase("ja-JP"));

  const filteredCards = useMemo(
    () =>
      reviewedTokyoPolicyTargetCards.filter((card) => {
        const matchesArea = areaCode === "all" || card.policy_area_code === areaCode;
        const searchable = [
          card.policy_area_name_original,
          card.policy_measure_original ?? "",
          card.target_name_original,
          card.highlighted_target_text_original.join(" "),
          card.periods_original.join(" "),
          card.units_original.join(" "),
          card.semantic_flags.map((flag) => tokyoSemanticFlagLabels[flag]).join(" "),
        ]
          .join(" ")
          .toLocaleLowerCase("ja-JP");
        return matchesArea && (deferredQuery.length === 0 || searchable.includes(deferredQuery));
      }),
    [areaCode, deferredQuery],
  );

  const selectedArea = reviewedTokyoPolicyAreas.find((area) => area.code === areaCode);

  function reset() {
    setQuery("");
    setAreaCode("all");
  }

  return (
    <div className={styles.explorer}>
      <div className={styles.controls}>
        <div className={styles.searchField}>
          <label htmlFor="tokyo-target-search">目標名・値・期間から探す</label>
          <input
            id="tokyo-target-search"
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="例：2035、待機児童、ゼロエミッション"
          />
        </div>
        <div className={styles.areaField}>
          <label htmlFor="tokyo-target-area">政策分野</label>
          <select
            id="tokyo-target-area"
            value={areaCode}
            onChange={(event) => setAreaCode(event.target.value)}
          >
            <option value="all">25分野すべて</option>
            {reviewedTokyoPolicyAreas.map((area) => (
              <option value={area.code} key={area.code}>
                {area.code} {area.name_original}（{area.target_card_count}件）
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className={styles.resultBar}>
        <p aria-live="polite">
          <strong>{filteredCards.length}</strong>件を表示
          {selectedArea ? (
            <span>
              {selectedArea.name_original}・PDF p.{selectedArea.page_start}
              {selectedArea.page_end !== selectedArea.page_start
                ? `–${selectedArea.page_end}`
                : ""}
            </span>
          ) : null}
        </p>
        {query || areaCode !== "all" ? (
          <button type="button" onClick={reset}>絞り込みを解除</button>
        ) : (
          <span>公式PDF掲載順</span>
        )}
      </div>

      {filteredCards.length ? (
        <div className={styles.cardGrid}>
          {filteredCards.map((card) => (
            <article className={styles.card} key={card.id}>
              <div className={styles.cardTop}>
                <span>
                  {card.policy_area_code} / {card.policy_area_name_original}
                </span>
                <StatusBadge
                  label={
                    card.detailed_series_status === "reviewed"
                      ? "点列までReviewed"
                      : "目標カードReviewed"
                  }
                  tone={card.detailed_series_status === "reviewed" ? "verified" : "progress"}
                />
              </div>
              <p className={styles.measure}>
                {card.policy_measure_original ?? "分野横断の政策目標"}
              </p>
              <h3>{card.target_name_original}</h3>

              <div className={styles.targetValues} aria-label="公式資料で強調された目標">
                {card.highlighted_target_text_original.map((text, index) => (
                  <strong key={`${card.id}-highlight-${index}`}>{text}</strong>
                ))}
              </div>

              {card.semantic_flags.length ? (
                <div className={styles.flags} aria-label="目標の型">
                  {card.semantic_flags.map((flag) => (
                    <span key={flag}>{tokyoSemanticFlagLabels[flag]}</span>
                  ))}
                </div>
              ) : null}

              <dl className={styles.facts}>
                <div>
                  <dt>期間表記</dt>
                  <dd>{card.periods_original.length ? card.periods_original.join(" / ") : "記載なし"}</dd>
                </div>
                <div>
                  <dt>単位表記</dt>
                  <dd>{card.units_original.length ? card.units_original.join(" / ") : "定性・本文型"}</dd>
                </div>
              </dl>

              <details className={styles.sourceText}>
                <summary>公式カード全文を確認</summary>
                <p>{card.source_card_text_original}</p>
              </details>

              <footer>
                <span>公式PDF p.{card.source_page}</span>
                <span>年度実績 未接続</span>
                <span>政策評価 未判定</span>
              </footer>
            </article>
          ))}
        </div>
      ) : (
        <div className={styles.emptyState}>
          <p>条件に一致する政策目標はありません。</p>
          <button type="button" onClick={reset}>304件すべてを表示</button>
        </div>
      )}
    </div>
  );
}
