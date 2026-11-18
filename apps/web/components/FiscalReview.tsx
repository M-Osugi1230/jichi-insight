import { breakdownChildren, formatJapaneseYen, type FiscalRecord } from "@/lib/finance";
import { sourceCatalog } from "@/lib/catalog";
import styles from "./FiscalReview.module.css";

type Props = { municipality: string; records: FiscalRecord[] };
const metrics = [
  ["total_revenue", "歳入総額"], ["local_tax", "地方税収"], ["total_expenditure", "歳出総額"],
  ["formal_balance", "形式収支"], ["carryover_resources", "翌年度繰越財源"],
  ["real_balance", "実質収支"], ["real_balance_ratio", "実質収支比率"],
  ["standard_fiscal_scale", "標準財政規模"]
] as const;
const indicators = [
  ["current_balance_ratio", "経常収支比率"],
  ["real_debt_service_ratio", "実質公債費比率"],
  ["future_burden_ratio", "将来負担比率"],
  ["fiscal_strength_index", "財政力指数"]
] as const;
const yen = (value: number | null | undefined) => value == null ? "未収録" : formatJapaneseYen(value);
function display(record: FiscalRecord | undefined): string {
  if (!record || record.value_status !== "available") return "未収録";
  if (record.unit === "yen") return yen(record.amount_yen);
  if (record.value === null) return "未収録";
  if (record.unit === "percent") return `${record.value}%`;
  if ((record.unit === "people" || record.unit === "persons")) return `${record.value.toLocaleString("ja-JP")}人`;
  return `${record.value.toLocaleString("ja-JP")}${record.unit === "ratio" || record.unit === "index" ? "" : ` ${record.unit}`}`;
}
function SourceLinks({ records }: { records: (FiscalRecord | undefined)[] }) {
  const ids = [...new Set(records.flatMap(record => record?.sources ?? []))];
  const sources = ids.map(id => sourceCatalog.find(source => source.id === id)).filter((s): s is NonNullable<typeof s> => Boolean(s));
  if (!sources.length) return <p className={styles.muted}>出典リンク未収録</p>;
  return <p className={styles.sources}>一次資料：{sources.map((source, i) =>
    <span key={source.id}>{i > 0 ? " ／ " : ""}<a href={source.url} rel="noopener noreferrer" target="_blank">{source.title}</a>（索引更新 {source.indexed_at}）</span>)}</p>;
}
function YearRows({ records, metricKeys }: { records: FiscalRecord[]; metricKeys: readonly (readonly [string, string])[] }) {
  const years = [2022, 2023, 2024];
  return <div className={styles.scroll}><table className={styles.table}>
    <thead><tr><th scope="col">項目</th>{years.map(year => <th scope="col" key={year}>{year}年度 決算</th>)}</tr></thead>
    <tbody>{metricKeys.map(([key, label]) => <tr key={key}><th scope="row">{label}</th>{years.map(year => {
      const record = records.find(r => r.fiscal_year === year && r.metric === key);
      return <td key={year}>{display(record)}{record ? <SourceLinks records={[record]} /> : null}</td>;
    })}</tr>)}</tbody>
  </table></div>;
}
function Breakdown({ records, metric, title }: { records: FiscalRecord[]; metric: string; title: string }) {
  const record = records.find(r => r.fiscal_year === 2024 && r.metric === metric);
  const topLevel = record ? breakdownChildren(record, null) : [];
  const rows: { item: (typeof topLevel)[number]; depth: number }[] = [];
  function appendRows(items: typeof topLevel, depth: number, visited: Set<string>) {
    for (const item of items) {
      if (visited.has(item.key)) continue;
      rows.push({ item, depth });
      const nextVisited = new Set(visited);
      nextVisited.add(item.key);
      if (record) appendRows(breakdownChildren(record, item.key), depth + 1, nextVisited);
    }
  }
  appendRows(topLevel, 0, new Set());
  return <section className={styles.subsection}>
    <h3>{title}（2024年度・普通会計決算）</h3>
    {!topLevel.length ? <p>内訳は未収録です。</p> :
      <div className={styles.scroll}><table className={styles.table}><thead><tr><th>区分</th><th>決算額</th></tr></thead><tbody>
        {rows.map(({ item, depth }) => <tr key={item.key}><th scope="row" style={{ paddingLeft: 12 + depth * 18 }}>{depth > 0 ? "内訳： " : ""}{item.label}</th><td>{yen(item.amount_yen)}</td></tr>)}
      </tbody></table></div>}
    {record && breakdownChildren(record, null).some(item => breakdownChildren(record, item.key).length > 0) ?
      <p className={styles.muted}>字下げした内訳・内数（「うち」）は上位区分に含まれ、二重計上を避けるため上位区分の額に加算していません。</p> : null}
    <SourceLinks records={[record]} />
  </section>;
}
export function FiscalReview({ municipality, records }: Props) {
  const settlement = records.filter(r => r.stage === "settlement" && r.account_type === "ordinary" && r.review_status === "reviewed");
  const latest = (metric: string, year = 2024) => settlement.find(r => r.metric === metric && r.fiscal_year === year);
  const pop = latest("population");
  const population = pop?.value != null && pop.value > 0 ? pop.value : null;
  const revenue = latest("total_revenue"), expenditure = latest("total_expenditure"), taxes = latest("local_tax");
  return <section className={styles.section} aria-label={`${municipality}の普通会計決算3年度ビュー`}>
    <div className="sectionIntro"><p className="eyebrow">FY2022–FY2024 · reviewed settlement</p>
      <h2>3年度の財政実績（普通会計）</h2>
      <p>2022〜2024年度の決算です。2026年度の一般会計当初予算とは、年度・会計区分・段階が異なるため連結して比較しません。欠損は推計・補間せず「未収録」と記します。</p>
    </div>
    <div className={styles.cards}>
      {[[revenue,"歳入総額"],[expenditure,"歳出総額"],[taxes,"地方税収"]].map(([r,label]) => {
        const record = r as FiscalRecord | undefined;
        return <article className={styles.card} key={label as string}><small>2024年度 普通会計決算</small><h3>{label as string}</h3>
          <strong>{display(record)}</strong><SourceLinks records={[record]} /></article>;
      })}
    </div>
    <section className={styles.subsection}><h3>歳入・歳出・収支の推移（2022〜2024年度、普通会計決算）</h3>
      <YearRows records={settlement} metricKeys={metrics} /></section>
    <div className={styles.twoCols}>
      <Breakdown records={settlement} metric="expenditure_by_purpose" title="目的別歳出" />
      <Breakdown records={settlement} metric="expenditure_by_nature" title="性質別歳出" />
    </div>
    <section className={styles.subsection}><h3>基金・地方債残高（普通会計決算）</h3>
      <YearRows records={settlement} metricKeys={[["fund_balance","基金残高"],["debt_balance","地方債残高"]]} />
      <p className={styles.muted}>基金の内訳は下記の2024年度レコードに基づきます。</p>
      <Breakdown records={settlement} metric="fund_balance" title="基金内訳" />
    </section>
    <section className={styles.subsection}><h3>主要財政指標（普通会計決算）</h3>
      <YearRows records={settlement} metricKeys={indicators} />
      <p className={styles.muted}>指標の未収録項目や算定条件の異なる比率は補完しません。福岡県独自の性質別区分は標準区分と混用しません。</p>
    </section>
    <section className={styles.subsection}><h3>住民1人あたりの参考値（2024年度）</h3>
      <p>分子：2024年度普通会計決算／分母：同年度資料に記載された住民基本台帳人口。人口の基準日が異なる場合があるため、単純な参考計算であり自治体間順位ではありません。</p>
      <p>登録人口：{display(pop)}。人口の出典と基準日：{pop?.note ?? "未収録"}</p>
      <div className={styles.cards}>{[[revenue,"歳入"],[expenditure,"歳出"],[taxes,"地方税"]].map(([r,label]) => {
        const record = r as FiscalRecord | undefined;
        const perResident = population && record?.amount_yen != null ? Math.round(record.amount_yen / population) : null;
        return <article className={styles.card} key={label as string}><h3>{label as string}／人</h3><strong>{perResident === null ? "未収録" : `${perResident.toLocaleString("ja-JP")}円`}</strong><small>Jichi Insight 算出・参考値</small>
          <SourceLinks records={[record,pop]} /></article>;
      })}</div>
    </section>
    <p className={styles.muted}>出典鮮度：各表内の「索引更新」を参照。掲載数値は Reviewed の決算レコードに限定しています。比較は参考併記のみで順位・評価を示しません。</p>
  </section>;
}
