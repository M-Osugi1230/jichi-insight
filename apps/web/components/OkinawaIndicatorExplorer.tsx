"use client";

import { useDeferredValue, useMemo, useState } from "react";

import { reviewedOkinawaIndicators } from "@/lib/okinawaIndicators";

import { StatusBadge } from "./StatusBadge";
import styles from "./OkinawaIndicatorExplorer.module.css";

type LevelFilter = "all" | "major" | "outcome";
type AttributeFilter =
  | "all"
  | "island"
  | "sdgs"
  | "qualitative"
  | "national"
  | "source_note";

const levelFilters: Array<{ value: LevelFilter; label: string }> = [
  { value: "all", label: "すべて" },
  { value: "major", label: "主要指標" },
  { value: "outcome", label: "成果指標" },
];

const attributeFilters: Array<{ value: AttributeFilter; label: string }> = [
  { value: "all", label: "条件なし" },
  { value: "island", label: "離島指標" },
  { value: "sdgs", label: "SDGs優先課題" },
  { value: "qualitative", label: "定性目標" },
  { value: "national", label: "全国値あり" },
  { value: "source_note", label: "原資料注記あり" },
];

const INITIAL_VISIBLE = 48;

export function OkinawaIndicatorExplorer() {
  const [query, setQuery] = useState("");
  const [level, setLevel] = useState<LevelFilter>("all");
  const [attribute, setAttribute] = useState<AttributeFilter>("all");
  const [visibleCount, setVisibleCount] = useState(INITIAL_VISIBLE);
  const deferredQuery = useDeferredValue(query.trim().toLocaleLowerCase("ja-JP"));

  const filtered = useMemo(
    () =>
      reviewedOkinawaIndicators.filter((indicator) => {
        const matchesLevel = level === "all" || indicator.level === level;
        const matchesAttribute =
          attribute === "all" ||
          (attribute === "island" && indicator.islandIndicator) ||
          (attribute === "sdgs" && indicator.sdgsPriority !== null) ||
          (attribute === "qualitative" && indicator.qualitativeTarget) ||
          (attribute === "national" && indicator.nationalComparisonProvided) ||
          (attribute === "source_note" && indicator.sourceValueNote !== null);
        const searchable = [
          indicator.policyCode,
          indicator.policyTitle,
          indicator.name,
          indicator.baseline,
          indicator.targetR9,
          indicator.nationalCurrent,
          indicator.rationaleSource,
          indicator.sdgsPriority ?? "",
          indicator.sourcePage,
        ]
          .join(" ")
          .toLocaleLowerCase("ja-JP");
        return (
          matchesLevel &&
          matchesAttribute &&
          (deferredQuery.length === 0 || searchable.includes(deferredQuery))
        );
      }),
    [attribute, deferredQuery, level],
  );

  const visible = filtered.slice(0, visibleCount);

  function reset() {
    setQuery("");
    setLevel("all");
    setAttribute("all");
    setVisibleCount(INITIAL_VISIBLE);
  }

  return (
    <div className={styles.explorer}>
      <div className={styles.controls}>
        <div className={styles.search}>
          <label htmlFor="okinawa-indicator-search">指標名・政策・値・出典から探す</label>
          <input
            id="okinawa-indicator-search"
            type="search"
            value={query}
            onChange={(event) => {
              setQuery(event.target.value);
              setVisibleCount(INITIAL_VISIBLE);
            }}
            placeholder="例：子どもの貧困、離島、観光、健康寿命"
          />
        </div>
        <fieldset>
          <legend>指標の階層</legend>
          <div className={styles.chips}>
            {levelFilters.map((item) => (
              <button
                type="button"
                aria-pressed={level === item.value}
                className={level === item.value ? styles.active : undefined}
                onClick={() => {
                  setLevel(item.value);
                  setVisibleCount(INITIAL_VISIBLE);
                }}
                key={item.value}
              >
                {item.label}
              </button>
            ))}
          </div>
        </fieldset>
        <fieldset>
          <legend>属性</legend>
          <div className={styles.chips}>
            {attributeFilters.map((item) => (
              <button
                type="button"
                aria-pressed={attribute === item.value}
                className={attribute === item.value ? styles.active : undefined}
                onClick={() => {
                  setAttribute(item.value);
                  setVisibleCount(INITIAL_VISIBLE);
                }}
                key={item.value}
              >
                {item.label}
              </button>
            ))}
          </div>
        </fieldset>
      </div>

      <div className={styles.resultBar}>
        <p aria-live="polite">
          <strong>{filtered.length}</strong>指標のうち{visible.length}件を表示
        </p>
        {query || level !== "all" || attribute !== "all" ? (
          <button type="button" onClick={reset}>絞り込みを解除</button>
        ) : (
          <span>主要指標、成果指標の順</span>
        )}
      </div>

      {visible.length ? (
        <>
          <div className={styles.grid}>
            {visible.map((indicator) => (
              <article className={styles.card} key={indicator.id}>
                <div className={styles.top}>
                  <span>{indicator.policyCode} / p.{indicator.sourcePage}</span>
                  <StatusBadge label="Reviewed" tone="verified" />
                </div>
                <div className={styles.levelLabel}>
                  {indicator.level === "major" ? "主要指標" : "成果指標"}
                </div>
                <h3>{indicator.name}</h3>
                <p className={styles.policy}>{indicator.policyTitle}</p>
                <div className={styles.badges}>
                  {indicator.islandIndicator ? <span>離島指標</span> : null}
                  {indicator.sdgsPriority ? <span>{indicator.sdgsPriority}</span> : null}
                  {indicator.qualitativeTarget ? <span>定性目標</span> : null}
                  {!indicator.nationalComparisonProvided ? <span>全国値なし</span> : null}
                  {indicator.sourceValueNote ? <span>原資料注記</span> : null}
                </div>
                <dl>
                  <div><dt>基準値</dt><dd>{indicator.baseline}</dd></div>
                  <div><dt>R9年度目標</dt><dd>{indicator.targetR9}</dd></div>
                  <div><dt>全国の現状値</dt><dd>{indicator.nationalCurrent}</dd></div>
                </dl>
                {indicator.sourceValueNote ? (
                  <p className={styles.sourceNote}>{indicator.sourceValueNote}</p>
                ) : null}
                <details>
                  <summary>設定の考え方・出典を読む</summary>
                  <p>{indicator.rationaleSource}</p>
                </details>
                <footer>
                  <span>{indicator.evidenceId}</span>
                  <span>政策評価 未判定</span>
                  <a
                    href={`${indicator.sourceUrl}#page=${indicator.sourcePage}`}
                    target="_blank"
                    rel="noreferrer"
                  >
                    公式資料 ↗
                  </a>
                </footer>
              </article>
            ))}
          </div>
          {visible.length < filtered.length ? (
            <div className={styles.loadMore}>
              <button
                type="button"
                onClick={() => setVisibleCount((count) => count + INITIAL_VISIBLE)}
              >
                さらに{Math.min(INITIAL_VISIBLE, filtered.length - visible.length)}件表示
              </button>
            </div>
          ) : null}
        </>
      ) : (
        <div className={styles.empty}>
          <p>条件に一致する指標はありません。</p>
          <button type="button" onClick={reset}>375指標をすべて表示</button>
        </div>
      )}
    </div>
  );
}
