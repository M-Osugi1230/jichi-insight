"use client";

import { useEffect, useRef, useState, type ReactNode } from "react";

import styles from "./ProgressiveRecordFilter.module.css";

type Props = {
  kind: "projects" | "proposals";
  total: number;
  themes?: string[];
  sessions?: Array<{ id: string; name: string }>;
  children: ReactNode;
};

export function ProgressiveRecordFilter({ kind, total, themes = [], sessions = [], children }: Props) {
  const rootRef = useRef<HTMLDivElement>(null);
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState("");
  const [count, setCount] = useState(total);
  const [enhanced, setEnhanced] = useState(false);

  useEffect(() => { setEnhanced(true); }, []);

  useEffect(() => {
    const root = rootRef.current;
    if (!root) return;
    const needle = query.trim().normalize("NFKC").toLocaleLowerCase("ja-JP");
    let visible = 0;
    for (const entry of root.querySelectorAll<HTMLElement>("[data-filter-entry]")) {
      const searchable = (entry.dataset.searchText ?? "").normalize("NFKC").toLocaleLowerCase("ja-JP");
      const match = (!needle || searchable.includes(needle)) &&
        (!selected || entry.dataset.filterGroup === selected);
      entry.hidden = !match;
      if (match) visible += 1;
    }
    // Keep empty session/municipality groups out of the filtered view.
    for (const group of root.querySelectorAll<HTMLElement>("[data-filter-section]")) {
      group.hidden = !group.querySelector("[data-filter-entry]:not([hidden])");
    }
    setCount(visible);
    return () => {
      for (const item of root.querySelectorAll<HTMLElement>("[data-filter-entry], [data-filter-section]")) {
        item.hidden = false;
      }
    };
  }, [query, selected]);

  const isProjects = kind === "projects";
  const chosenLabel = isProjects
    ? themes.find((item) => item === selected)
    : sessions.find((item) => item.id === selected)?.name;
  const active = Boolean(query.trim() || selected);

  return (
    <div className={styles.root}>
      <div className={styles.controls} role="search" aria-label={isProjects ? "登録事業の絞り込み" : "登録議案の絞り込み"}>
        <div className={styles.fields}>
          <label>
            <span>{isProjects ? "事業名・キーワード" : "議案番号・件名"}</span>
            <input
              type="search"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder={isProjects ? "例：子育て" : "議案番号や件名で検索"}
            />
          </label>
          <label>
            <span>{isProjects ? "政策分野" : "会期"}</span>
            <select value={selected} onChange={(event) => setSelected(event.target.value)}>
              <option value="">すべて</option>
              {isProjects
                ? themes.map((theme) => <option value={theme} key={theme}>{theme}</option>)
                : sessions.map((session) => <option value={session.id} key={session.id}>{session.name}</option>)}
            </select>
          </label>
          <button type="button" onClick={() => { setQuery(""); setSelected(""); }} disabled={!active}>
            絞り込みを解除
          </button>
        </div>
        <p className={styles.status} role="status" aria-live="polite" aria-atomic="true">
          {enhanced ? `表示 ${count}件 / 登録済み全${total}件` : `登録済み全${total}件を表示`}
          {active ? `（条件：${[query.trim() ? `キーワード「${query.trim()}」` : "", chosenLabel ? `${isProjects ? "政策分野" : "会期"}「${chosenLabel}」` : ""].filter(Boolean).join("、")}）` : "（条件：すべて）"}
        </p>
        {enhanced && count === 0 ? (
          <p className={styles.empty} role="status">
            {isProjects ? "該当する収録事業がありません" : "該当する収録議案がありません"}
          </p>
        ) : null}
      </div>
      <div ref={rootRef}>{children}</div>
    </div>
  );
}
