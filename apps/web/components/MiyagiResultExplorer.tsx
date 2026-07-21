"use client";

import { useMemo, useState } from "react";

import {
  latestMiyagiAnnualResult,
  reviewedMiyagiKpiActualLinks,
  type MiyagiKpiActualLink,
} from "@/lib/miyagiActuals";
import {
  reviewedMiyagiKpiGroups,
  type MiyagiKpiValue,
} from "@/lib/miyagiPolicies";

import { StatusBadge } from "./StatusBadge";
import styles from "./MiyagiResultExplorer.module.css";

const evaluationDocumentUrl =
  "https://www.pref.miyagi.jp/documents/59769/r7-seikatohyouka_1.pdf";

type LinkFilter = "all" | MiyagiKpiActualLink["linkage_status"];

const matchBasisLabels: Record<MiyagiKpiActualLink["match_basis"], string> = {
  exact_name_and_unit: "名称・単位が一致",
  normalized_name_and_unit: "表記を正規化して一致",
  definition_changed: "定義・対象範囲に変更あり",
};

function formatPlanValue(value: MiyagiKpiValue | undefined, unit: string | undefined) {
  if (!value || value.status === "not_set") return "未設定";
  if (value.status === "not_available") return "未公表";
  return `${value.value_text_original}${unit ?? ""}`;
}

const resultRecords = reviewedMiyagiKpiActualLinks.map((actual) => {
  const group = reviewedMiyagiKpiGroups.find(
    (candidate) => candidate.id === actual.target_group_id,
  );
  const series = group?.series.find((candidate) => candidate.id === actual.series_id);
  const currentPlanTarget = series?.values.find((value) => value.role === "midterm_target");
  return {
    actual,
    group,
    series,
    currentPlanTarget,
    latest: latestMiyagiAnnualResult(actual),
  };
});

const measureOptions = Array.from(
  new Set(
    resultRecords
      .filter((record) => record.group?.scope_type === "measure")
      .map((record) => record.group?.scope_number ?? 0),
  ),
).sort((left, right) => left - right);

export function MiyagiResultExplorer() {
  const [query, setQuery] = useState("");
  const [linkFilter, setLinkFilter] = useState<LinkFilter>("all");
  const [measure, setMeasure] = useState("all");
  const [visibleCount, setVisibleCount] = useState(12);

  const filtered = useMemo(() => {
    const normalized = query.trim().toLocaleLowerCase("ja-JP");
    return resultRecords.filter(({ actual, group, series }) => {
      const matchesQuery =
        normalized.length === 0 ||
        [
          actual.source_indicator_name_original,
          series?.indicator_name_original ?? "",
          String(group?.target_group_number ?? ""),
          String(group?.scope_number ?? ""),
        ]
          .join(" ")
          .toLocaleLowerCase("ja-JP")
          .includes(normalized);
      const matchesLink = linkFilter === "all" || actual.linkage_status === linkFilter;
      const matchesMeasure =
        measure === "all" ||
        (group?.scope_type === "measure" && String(group.scope_number) === measure);
      return matchesQuery && matchesLink && matchesMeasure;
    });
  }, [linkFilter, measure, query]);

  const visible = filtered.slice(0, visibleCount);

  function resetVisible() {
    setVisibleCount(12);
  }

  return (
    <div className={styles.explorer}>
      <div className={styles.filterPanel}>
        <div className={styles.search}>
          <label htmlFor="miyagi-result-search">指標名・目標番号から探す</label>
          <input
            id="miyagi-result-search"
            type="search"
            value={query}
            onChange={(event) => { setQuery(event.target.value); resetVisible(); }}
            placeholder="例：企業立地、観光、目標12"
          />
        </div>
        <div className={styles.select}>
          <label htmlFor="miyagi-result-measure">取組</label>
          <select
            id="miyagi-result-measure"
            value={measure}
            onChange={(event) => { setMeasure(event.target.value); resetVisible(); }}
          >
            <option value="all">取組1〜15</option>
            {measureOptions.map((number) => (
              <option value={number} key={number}>取組{number}</option>
            ))}
          </select>
        </div>
        <fieldset>
          <legend>接続状態</legend>
          <div className={styles.chips}>
            <button
              type="button"
              aria-pressed={linkFilter === "all"}
              className={linkFilter === "all" ? styles.activeChip : undefined}
              onClick={() => { setLinkFilter("all"); resetVisible(); }}
            >すべて <strong>{resultRecords.length}</strong></button>
            <button
              type="button"
              aria-pressed={linkFilter === "linked"}
              className={linkFilter === "linked" ? styles.activeChip : undefined}
              onClick={() => { setLinkFilter("linked"); resetVisible(); }}
            >直接接続 <strong>{resultRecords.filter((record) => record.actual.linkage_status === "linked").length}</strong></button>
            <button
              type="button"
              aria-pressed={linkFilter === "needs_review"}
              className={linkFilter === "needs_review" ? styles.activeChip : undefined}
              onClick={() => { setLinkFilter("needs_review"); resetVisible(); }}
            >対応要確認 <strong>{resultRecords.filter((record) => record.actual.linkage_status === "needs_review").length}</strong></button>
          </div>
        </fieldset>
      </div>

      <div className={styles.resultBar}>
        <p aria-live="polite"><strong>{filtered.length}</strong>系列の年度実績</p>
        <span>{Math.min(visibleCount, filtered.length)}件を表示</span>
      </div>

      <div className={styles.resultGrid}>
        {visible.map(({ actual, group, series, currentPlanTarget, latest }) => (
          <article className={styles.resultCard} key={actual.id}>
            <div className={styles.cardTop}>
              <span>
                目標No.{group?.target_group_number ?? "—"}
                {group?.scope_type === "measure" ? ` / 取組${group.scope_number}` : ""}
              </span>
              <StatusBadge
                label={actual.linkage_status === "linked" ? "直接接続" : "対応要確認"}
                tone={actual.linkage_status === "linked" ? "verified" : "warning"}
              />
            </div>
            <h3>{series?.indicator_name_original ?? actual.source_indicator_name_original}</h3>

            <div className={styles.latest}>
              <div>
                <span>{latest.reporting_year}年度実績</span>
                <strong>{latest.value_text_original}<small>{latest.unit_original}</small></strong>
              </div>
              <div>
                <span>公式評価書の進捗率</span>
                <strong>{latest.achievement_rate_text_original}</strong>
                <small>判定 {latest.achievement_grade === "not_set" ? "—" : latest.achievement_grade}</small>
              </div>
            </div>

            <ol className={styles.timeline} aria-label="年度実績の推移">
              {actual.annual_results.map((result) => (
                <li key={result.reporting_year}>
                  <span>{result.reporting_year}</span>
                  <strong>{result.value_text_original}<small>{result.unit_original}</small></strong>
                  <em>{result.achievement_rate_text_original}</em>
                </li>
              ))}
            </ol>

            <div className={styles.targetComparison}>
              <div>
                <span>評価書の目標</span>
                <strong>{actual.evaluation_target.value_text_original}{actual.evaluation_target.unit_original}</strong>
                <small>{actual.evaluation_target.period_year}年度</small>
              </div>
              <div>
                <span>現行計画の中期末目標</span>
                <strong>{formatPlanValue(currentPlanTarget, series?.unit_original)}</strong>
                <small>{currentPlanTarget?.period_year ?? "—"}年度</small>
              </div>
            </div>

            {actual.linkage_status === "needs_review" ? (
              <p className={styles.reviewWarning}>定義や対象範囲に差があるため、同一系列としての利用には追加確認が必要です。</p>
            ) : null}

            <details className={styles.details}>
              <summary>根拠と比較上の注意</summary>
              <dl>
                <div><dt>対応根拠</dt><dd>{matchBasisLabels[actual.match_basis]}</dd></div>
                <div><dt>確信度</dt><dd>{actual.confidence === "high" ? "高" : "中"}</dd></div>
              </dl>
              <p>{actual.comparability_note_original}</p>
            </details>

            <footer>
              <span>評価書 指標No.{actual.source_indicator_number}</span>
              <a href={`${evaluationDocumentUrl}#page=${actual.source_pdf_page}`} target="_blank" rel="noreferrer">
                PDF {actual.source_pdf_page}ページ ↗
              </a>
            </footer>
          </article>
        ))}
      </div>

      {visibleCount < filtered.length ? (
        <button className={styles.moreButton} type="button" onClick={() => setVisibleCount((count) => count + 12)}>
          次の{Math.min(12, filtered.length - visibleCount)}件を表示
        </button>
      ) : null}
    </div>
  );
}
