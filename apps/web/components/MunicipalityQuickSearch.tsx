"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useMemo, useRef, useState, type FormEvent } from "react";

import styles from "./MunicipalityQuickSearch.module.css";

export type MunicipalitySearchEntry = {
  id: string;
  name: string;
  prefectureOrRegion: string;
  kind: "prefecture" | "city";
  href: string;
  keywords: string[];
};

type Props = {
  entries: MunicipalitySearchEntry[];
};

function normalize(value: string) {
  return value.normalize("NFKC").replace(/\s+/g, "").toLocaleLowerCase("ja-JP");
}

export function MunicipalityQuickSearch({ entries }: Props) {
  const router = useRouter();
  const firstResult = useRef<HTMLAnchorElement>(null);
  const [query, setQuery] = useState("");
  const normalizedQuery = normalize(query);
  const cityCount = entries.filter((entry) => entry.kind === "city").length;

  const matches = useMemo(() => {
    if (!normalizedQuery) return [];

    return entries.filter((entry) =>
      normalize(
        [entry.name, entry.prefectureOrRegion, ...entry.keywords].join(" "),
      ).includes(normalizedQuery),
    );
  }, [entries, normalizedQuery]);

  const shownMatches = matches.slice(0, 8);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (matches.length === 1) {
      router.push(matches[0].href);
    } else if (matches.length > 1) {
      firstResult.current?.focus();
    }
  }

  return (
    <section className={styles.search} aria-labelledby="home-municipality-search-heading">
      <div className={styles.heading}>
        <h2 id="home-municipality-search-heading">自治体を検索</h2>
        <p>都道府県や、詳細レビュー済みの市を名前で探せます。</p>
      </div>
      <form className={styles.form} role="search" onSubmit={handleSubmit}>
        <label className={styles.visuallyHidden} htmlFor="home-municipality-search">
          自治体名または地域名
        </label>
        <input
          id="home-municipality-search"
          type="search"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="例：宮城県、函館市"
          autoComplete="off"
          enterKeyHint="search"
          aria-controls="home-municipality-results"
          aria-describedby="home-municipality-search-scope"
        />
        <button type="submit">検索</button>
      </form>
      <p id="home-municipality-search-scope" className={styles.scope}>
        検索対象：47都道府県と詳細レビュー済み{cityCount}市。全国すべての市区町村ではありません。
      </p>
      <div id="home-municipality-results" aria-live="polite" aria-atomic="false">
        {normalizedQuery ? (
          <div className={styles.results}>
            <p className={styles.resultsHeading}>
              {matches.length
                ? `${matches.length}件の候補が見つかりました`
                : "一致する自治体は見つかりませんでした"}
            </p>
            {shownMatches.length > 0 ? (
              <ul className={styles.resultList}>
                {shownMatches.map((entry, index) => (
                  <li key={entry.id}>
                    <Link
                      href={entry.href}
                      ref={index === 0 ? firstResult : undefined}
                      className={styles.resultLink}
                    >
                      <span>
                        <strong>{entry.name}</strong>
                        <small>
                          {entry.kind === "prefecture"
                            ? `都道府県・${entry.prefectureOrRegion}`
                            : `市・${entry.prefectureOrRegion}`}
                        </small>
                      </span>
                      <span aria-hidden="true">→</span>
                    </Link>
                  </li>
                ))}
              </ul>
            ) : (
              <p className={styles.emptyMessage}>
                未レビューの市は検索候補に表示されません。公開範囲は自治体一覧で確認できます。
              </p>
            )}
            {matches.length > shownMatches.length && (
              <p className={styles.moreMessage}>
                候補が多いため先頭8件を表示中です。自治体名をもう少し詳しく入力してください。
              </p>
            )}
          </div>
        ) : (
          <div className={styles.examples}>
            <span>検索例</span>
            <button type="button" onClick={() => setQuery("宮城県")}>
              宮城県
            </button>
            <button type="button" onClick={() => setQuery("函館市")}>
              函館市
            </button>
            <Link href="/municipalities#prefectures">47都道府県の一覧へ</Link>
          </div>
        )}
      </div>
    </section>
  );
}
