import Link from "next/link";

import type { Phase15City, Phase15FiscalRecord } from "@/lib/phase15Cities";

import styles from "./CityOverview.module.css";

type Props = {
  city: Phase15City;
};

const numberFormatter = new Intl.NumberFormat("ja-JP");
const compactFormatter = new Intl.NumberFormat("ja-JP", {
  maximumFractionDigits: 1,
});

function pickRecord(
  records: Phase15FiscalRecord[],
  stage: "initial_budget" | "settlement",
  metric: "total_expenditure" | "total_revenue",
) {
  return records.find(
    (record) => record.stage === stage && record.metric === metric,
  );
}

function summaryAmount(record: Phase15FiscalRecord | undefined) {
  if (
    !record ||
    record.valueStatus !== "available" ||
    record.amountYen === null
  ) {
    return "未確認";
  }

  const amount = record.amountYen;
  if (Math.abs(amount) >= 100_000_000) {
    return `${compactFormatter.format(amount / 100_000_000)}億円`;
  }
  return `${numberFormatter.format(amount)}円`;
}

function exactAmount(record: Phase15FiscalRecord | undefined) {
  if (
    !record ||
    record.valueStatus !== "available" ||
    record.amountYen === null
  ) {
    return "公式資料から金額を確定できていません";
  }
  return `原資料の値（円換算）: ${numberFormatter.format(record.amountYen)}円`;
}

export function CityOverview({ city }: Props) {
  const fiscalMetrics = [
    {
      key: "budget",
      label: "当初予算",
      caption: "予算と決算は異なる段階です",
      record: pickRecord(city.fiscalRecords, "initial_budget", "total_expenditure"),
    },
    {
      key: "revenue",
      label: "決算・歳入",
      caption: "当該年度における収入済額",
      record: pickRecord(city.fiscalRecords, "settlement", "total_revenue"),
    },
    {
      key: "expenditure",
      label: "決算・歳出",
      caption: "当該年度における支出済額",
      record: pickRecord(city.fiscalRecords, "settlement", "total_expenditure"),
    },
  ];

  const knownPlan = city.planRecords.find(
    (record) => record.evidenceRole === "current_plan_identity" && record.decision === "accepted",
  );

  return (
    <div className={styles.wrapper}>
      <nav className={styles.jumpNav} aria-label="この自治体ページの目次">
        <a href="#city-summary-title">概要</a>
        <a href="#promise-title">政策計画</a>
        <a href="#money-title">予算・決算</a>
        <a href="#linkage-title">実績との接続</a>
        <a href="#sources-title">公式資料</a>
        <a href="#boundary-title">確認の範囲</a>
      </nav>

      <section className={styles.summary} aria-labelledby="city-summary-title">
        <div className={styles.header}>
          <div>
            <p className={styles.kicker}>LOCAL GOVERNMENT PROFILE</p>
            <h2 id="city-summary-title">{city.name}の概要</h2>
            <p className={styles.subtitle}>
              公開された資料で確認できたことを、最初にまとめました。
            </p>
          </div>
          <span className={styles.verified}>一次資料を照合済み</span>
        </div>

        <div className={styles.fiscalGrid}>
          {fiscalMetrics.map(({ key, label, caption, record }) => {
            const available = Boolean(record && record.valueStatus === "available" && record.amountYen !== null);
            return (
              <article className={styles.metric} key={key}>
                <div className={styles.metricTop}>
                  <span>{label}</span>
                  <span>{record ? `${record.fiscalYear}年度` : "対象年度未確認"}</span>
                </div>
                <strong className={styles.metricValue}>{summaryAmount(record)}</strong>
                <span className={styles.metricLabel}>
                  {record?.metricLabel ?? "該当レコードなし"}
                </span>
                <p className={styles.metricCaption}>{caption}</p>
                <p className={styles.metricExact}>{exactAmount(record)}</p>
                {available && record?.sources[0] ? (
                  <a
                    className={styles.metricSource}
                    href={record.sources[0].officialUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    根拠となる公式資料を開く <span aria-hidden="true">↗</span>
                  </a>
                ) : (
                  <span className={styles.metricUnavailable}>
                    この項目は確認済みの金額として表示できません
                  </span>
                )}
              </article>
            );
          })}
        </div>

        <div className={styles.bottom}>
          <div>
            <h3>確認した政策計画</h3>
            <p>{knownPlan?.title ?? "現行計画の正式名称はこの概要では特定できていません"}</p>
            <span>資料・計画の詳しい内容は下の「政策計画」から確認できます。</span>
          </div>
          <div className={styles.facts}>
            <span>最終資料確認日</span>
            <strong><time dateTime={city.lastVerifiedAt}>{city.lastVerifiedAt}</time></strong>
            <span>レビュー済みの範囲は限定されています</span>
          </div>
        </div>
        <p className={styles.disclaimer}>
          億円表記は閲覧用に小数第1位まで丸めた概数です。原資料の円換算値を各カードにも併記しています。
          予算と決算は年度・会計・段階が異なる場合があり、単純な増減比較や政策達成評価は行いません。
        </p>
        <div className={styles.actions}>
          <a href="#money-title">財政の詳細・照合記録を見る <span aria-hidden="true">↓</span></a>
          <Link href="/corrections">掲載内容の訂正を依頼する</Link>
        </div>
      </section>
    </div>
  );
}
