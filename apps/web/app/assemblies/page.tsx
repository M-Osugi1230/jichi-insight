import type { Metadata } from "next";
import Link from "next/link";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { assemblies, assemblySlugs } from "@/lib/assemblyRegistry";
import { canonicalFor } from "@/lib/pageMetadata";
import styles from "./assembly.module.css";

export const metadata: Metadata = {
  title: "議会アカウンタビリティ｜12議会の議案・表決・政務活動費・視察",
  description: "北海道3議会、大阪府議会・大阪市会・堺市議会、福岡3議会と愛知3議会の公式資料と情報公開状況を確認します。議員スコアや活動量ランキングは作りません。",
  alternates: { canonical: canonicalFor("/assemblies") },
};
const status: Record<string,string> = {
  published:"公表あり", not_published:"公表されていません",
  restricted:"窓口等で閲覧", unknown:"公開状況未確認",
};
const keyItems = ["proposals_and_results","faction_votes","member_votes",
  "political_activity_expense_reports","political_activity_expense_receipts","inspection_trip_reports"] as const;
const names: Record<string,string> = {
  proposals_and_results:"議案・議決結果",faction_votes:"会派別の賛否",
  member_votes:"議員ごとの賛否",political_activity_expense_reports:"政務活動費",
  political_activity_expense_receipts:"領収書",inspection_trip_reports:"視察報告書",
};
export default function AssembliesPage() {
  return <><SiteHeader/><main><div className="pageShell">
    <header className={styles.intro}>
      <p className="eyebrow">Assembly accountability</p>
      <h1>議会を、質問数ではなく役割と根拠で見る。</h1>
      <p>議会の審議・表決・情報公開と、執行部が実施した政策成果は別のものです。公開されていない議員別賛否を推測して再現したり、議員や会派を活動量・支出額で順位付けしたりしません。総合点や会派ランキングは出しません。</p>
      <p className={styles.attention}>確認できること：12議会の登録済み議案・議決結果と資料ごとの公開範囲。名古屋市会では第134号のみ議員別賛否68人分を確認でき、他の登録議案は全会一致です。愛知県議会の会派態度は採決前に議会運営委員会で確認されたもので、本会議の投票記録そのものではありません。福岡県議会の会派別・議員別賛否など、公表されていない情報は推測しません。</p>
    </header>
    <section aria-label="12議会の情報公開状況" className={styles.grid}>
      {assemblySlugs.map(slug => {
        const entry=assemblies[slug]; const assembly=entry.assembly;
        const members=assembly.factions.reduce((sum,faction)=>sum+faction.member_count,0);
        return <article className={styles.card} key={slug}>
          <p className="eyebrow">Reviewed</p><h2>{assembly.name}</h2>
          <p className={styles.note}>現任期：{assembly.term_start} 〜 {assembly.term_end}</p>
          <p>議員定数 {assembly.seat_count}人／登録名簿の現員 {members}人
          {assembly.seat_count > members ? `（欠員 ${assembly.seat_count-members}人）`:""}</p>
          <h3>この議会で公開されているもの</h3>
          <ul>{keyItems.map(item => {
            const profile=entry.disclosure.items.find(row=>row.item===item);
            return <li key={item}>{names[item]}：{status[profile?.availability??"unknown"]??profile?.availability??"未収録"}</li>;
          })}</ul>
          <p className={styles.note}>確認時点：{entry.disclosure.as_of}。公開範囲は資料ごとに異なります。</p>
          <Link href={`/assemblies/${slug}`}>公式データと議案・視察の詳細を見る</Link>
        </article>;
      })}
    </section>
    <p className={styles.note}>上記は公開状況を並べたものであり、議会の優劣を評価する比較表ではありません。出典リンクと項目ごとの注意書きは各詳細ページに掲載しています。</p>
  </div></main><SiteFooter/></>;
}
