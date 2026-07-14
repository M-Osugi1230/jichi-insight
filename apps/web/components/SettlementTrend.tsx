import {
  formatExactYen,
  formatJapaneseYen,
  settlementRecord,
  settlementTrend,
  sourcesForRecord,
} from "@/lib/finance";

import styles from "./SettlementTrend.module.css";

export function SettlementTrend() {
  const trend = settlementTrend();
  const latestRevenue = settlementRecord(2024, "total_revenue");
  const latestExpenditure = settlementRecord(2024, "total_expenditure");
  const latestLocalTax = settlementRecord(2024, "local_tax");
  const taxShare =
    latestRevenue.amount_yen && latestLocalTax.amount_yen
      ? (latestLocalTax.amount_yen / latestRevenue.amount_yen) * 100
      : null;
  const peakRevenue = Math.max(
    ...trend.map((year) => year.revenue.amount_yen ?? 0),
  );
  const sources = [
    ...sourcesForRecord(latestRevenue),
    ...sourcesForRecord(latestLocalTax),
  ].filter(
    (source, index, all) =>
      all.findIndex((item) => item.id === source.id) === index,
  );

  return (
    <section className={styles.section} aria-labelledby="settlement-trend-title">
      <div className={styles.intro}>
        <p className="eyebrow">2020–2024 ordinary-account settlement</p>
        <h2 id="settlement-trend-title">5年間の「実績」を、予算とは別に見る。</h2>
        <p>
          福岡県が公表した2024年度決算資料から、普通会計の歳入・歳出総額を5年度分収録しました。
          2026年度の一般会計当初予算とは、年度も会計範囲も異なるため、同じ系列には並べません。
        </p>
      </div>

      <div className={styles.notice}>
        <strong>会計区分に注意</strong>
        <p>
          普通会計は、総務省の地方財政状況調査のため、一般会計と一部の特別会計を再構成した統計上の会計です。
          一般会計単独の予算額との単純比較はできません。
        </p>
      </div>

      <div className={styles.summaryGrid}>
        <article className={styles.summaryCard}>
          <span>2024年度 普通会計歳入</span>
          <strong>{formatJapaneseYen(latestRevenue.amount_yen)}</strong>
          <small>{formatExactYen(latestRevenue.amount_yen)}</small>
          <p>前年度比1.9%増。公式資料では2兆937億円と表示。</p>
        </article>
        <article className={styles.summaryCard}>
          <span>2024年度 普通会計歳出</span>
          <strong>{formatJapaneseYen(latestExpenditure.amount_yen)}</strong>
          <small>{formatExactYen(latestExpenditure.amount_yen)}</small>
          <p>前年度比2.0%増。歳入との差額は610億7,400万円。</p>
        </article>
        <article className={styles.summaryCard}>
          <span>2024年度 県税収入</span>
          <strong>{formatJapaneseYen(latestLocalTax.amount_yen)}</strong>
          <small>{taxShare === null ? "評価不能" : `歳入総額の${taxShare.toFixed(1)}%`}</small>
          <p>公式資料では過去最高、歳入構成比37.5%と記載。</p>
        </article>
      </div>

      <div className={styles.tableWrap}>
        <table className={styles.table}>
          <caption>
            金額は公式資料の百万円単位を円へ換算。差額はJichi Insightによる計算。
          </caption>
          <thead>
            <tr>
              <th scope="col">年度</th>
              <th scope="col">歳入総額</th>
              <th scope="col">歳出総額</th>
              <th scope="col">歳入−歳出</th>
            </tr>
          </thead>
          <tbody>
            {trend.map((year) => (
              <tr key={year.fiscalYear}>
                <td className={styles.yearCell}>
                  {year.fiscalYear}年度
                  {year.revenue.amount_yen === peakRevenue ? (
                    <span className={styles.peak}>5年最大</span>
                  ) : null}
                </td>
                <td>{formatJapaneseYen(year.revenue.amount_yen)}</td>
                <td>{formatJapaneseYen(year.expenditure.amount_yen)}</td>
                <td className={styles.derived}>
                  {formatJapaneseYen(year.formalBalanceYen)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className={styles.sources}>
        <span>一次資料</span>
        {sources.map((source) => (
          <a href={source.url} target="_blank" rel="noreferrer" key={source.id}>
            {source.title} ↗
          </a>
        ))}
      </div>
    </section>
  );
}
