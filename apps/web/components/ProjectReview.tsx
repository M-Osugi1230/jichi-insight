import Link from "next/link";
import { formatJapaneseYen } from "@/lib/finance";
import { projectSourceCatalog } from "@/lib/projectRegistry";
import type { ProjectRecord, KpiRecord } from "@/lib/kitakyushuProjects";
import styles from "./ProjectReview.module.css";

const show = (v: string | number | null | undefined) => v === null || v === undefined || v === "" ? "未収録" : String(v);
function stageLabel(area: string, stage: string, year: number) {
  if (area === "nagoya-city" && stage === "initial_budget") return "予算案段階の予定額（成立後の事業別予算額ではありません）";
  if (area === "aichi-prefecture" && stage === "initial_budget" && year === 2026) return "FY2026 当初予算・億円単位で公表された概数（千円単位の確定額ではありません）";
  if (area === "fukuoka-city" && stage === "initial_budget") return "当初予算案段階の額（成立後の事業別額は未確認）";
  if (area === "fukuoka-prefecture" && stage === "initial_budget" && year === 2026) return "令和8年度 予算案の額（成立額ではありません）";
  if (area === "kitakyushu-city" && stage === "settlement") return "決算額（令和7年8月公表時点・議会認定前）";
  return ({initial_budget:"当初予算",revised_budget:"補正後予算",execution:"執行額",settlement:"決算額"} as Record<string,string>)[stage] ?? stage;
}
function sourceLinks(ids: string[]) {
  return <p className={styles.sourceList}>出典：{ids.length ? ids.map((id,i) => {
    const source = projectSourceCatalog.find(item => item.id === id);
    return <span key={id}>{i ? " ／ " : ""}{source ? <a className={styles.link} href={source.url} target="_blank" rel="noreferrer">{source.title}</a> : id}{source ? `（索引 ${source.indexed_at}）` : "（参照ID・出典URL未連携）"}</span>;
  }) : "未収録"}</p>;
}
function value(v: string | number | null | undefined, unit: string) {
  return v === null || v === undefined ? "未公表・未収録" : `${v}${unit}`;
}
export function ProjectReview({area, record, kpis}:{area:string;record:ProjectRecord;kpis:KpiRecord[]}) {
  const budgets = [...record.budget_records].sort((a,b) => a.fiscal_year - b.fiscal_year);
  const hasSettlement = budgets.some(b => b.kind === "settlement" && b.amount_yen !== null);
  const end = record.official_evaluation?.direction;
  return <section className={styles.section}>
    <p className={styles.meta}>Reviewed / {record.fiscal_year}年度 / 対象：{show(record.target_population)} / 担当：{show(record.responsible_department)} / 上位施策：{show(record.parent_policy)}</p>
    <div className={styles.detail}><h2>目的と対象</h2><p>{record.purpose}</p><p className={styles.meta}>首長公約との接続：{record.related_promise_ids.length ? "関連候補（自動推定を含む・要確認）。確信度：低（inferred）／証拠パケット：needs_review。確定的な因果接続や達成判定ではありません。" : "接続公約なし（未着手・未達を意味しません）"}</p>
      {record.related_promise_ids.length ? <ul>{record.related_promise_ids.map(id=><li key={id}><Link className={styles.link} href={`/promises#${id}`}>公約原文を見る</Link> <span className={styles.meta}>（公約ID: {id}、自動推定を含む・確信度低・要レビュー）</span></li>)}</ul> : null}</div>
    <div className={styles.detail}><h2>予算から成果までの記録</h2>
      <ol className={styles.lifecycle}>
        <li><strong>計画・公約との接続</strong>要確認。関連性の自動推定を含み、確定済みの接続ではありません。</li>
        {budgets.map((budget,i)=><li key={`${budget.fiscal_year}-${budget.kind}-${i}`}>
          <strong>{budget.fiscal_year}年度 — {stageLabel(area,budget.kind,budget.fiscal_year)}</strong>
          <span>{budget.amount_yen === null ? "未取得" : formatJapaneseYen(budget.amount_yen)}</span>
          <p className={styles.meta}>{budget.note ?? "段階に関する注記なし"}</p>
        </li>)}
        {!hasSettlement ? <li><strong>事業別決算額</strong>未取得（公式資料で接続できた金額なし。推測補完しません）</li> : null}
        <li><strong>KPI 実績</strong>以下に基準値・目標・実績を分離して表示</li>
        <li><strong>自治体の公式評価・次年度方向性</strong>
          {record.official_evaluation
            ? `${show(record.official_evaluation.rating)}／${show(end)}`
            : area === "toyota-city" ? "事業単位の公式評価は公表されていません" : "未収録"}
          <p className={styles.meta}>{record.official_evaluation?.note ??
            (area === "toyota-city"
              ? "目標・施策単位の進捗や叙述を、この事業の公式評価に読み替えません。"
              : "公式評価は未収録")}</p></li>
      </ol>
      {end && /廃止|終了|完了/.test(end+" "+record.official_evaluation?.rating) ? <p className={styles.warning}>この事業は終了・廃止等の終端として記録されています。後継事業の有無は公式評価の注記をご確認ください。</p> : null}
    </div>
    <div className={styles.detail}><h2>KPI（目標と実績は別項目）</h2>
      {kpis.length ? kpis.map(kpi=><article className={styles.kpi} key={kpi.id}><h3>{kpi.name}</h3>
        <p className={styles.meta}>{kpi.definition}</p>
        <dl className={styles.kpiGrid}>
          <div><dt>基準値 {kpi.baseline?.period ?? ""}</dt><dd>{value(kpi.baseline?.value,kpi.unit)}</dd></div>
          <div><dt>目標値 {kpi.target?.period ?? ""}</dt><dd>{value(kpi.target?.value,kpi.unit)}</dd></div>
          <div><dt>実績（公表値のみ）</dt><dd>{kpi.actuals?.length ? kpi.actuals.map((actual,i)=><p key={i}>{actual.period}: {value(actual.value,kpi.unit)}</p>) : "未公表・未収録"}</dd></div>
        </dl>
        <p className={styles.meta}>評価状態：{kpi.assessment === "not_assessable" ? "評価材料なし（未接続）" : kpi.assessment === "not_published" ? "未公表" : kpi.assessment === "in_progress" ? "進行中" : kpi.assessment === "achieved" ? "達成（登録された評価）" : kpi.assessment === "not_achieved" ? "未達（登録された評価）" : kpi.assessment}</p>
        <p className={styles.warning}>因果関係の限界：{kpi.causality_note ?? "未収録"}</p>
        {sourceLinks(kpi.sources)}
      </article>) : <p>この事業のKPIは未収録です。</p>}
    </div>
    <div className={styles.detail}><h2>証拠・未収録の範囲</h2>
      {sourceLinks(record.sources)}
      <p>契約・議会審議・監査と事業の対応：未収録。公約との関係は確信度・レビュー状態の検証が必要です。</p>
      <Link className={styles.link} href="/projects">重点事業一覧に戻る</Link>
    </div>
  </section>;
}
