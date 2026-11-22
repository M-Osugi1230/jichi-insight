import type { Metadata } from "next";
import Link from "next/link";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { assemblies, assemblySlugs } from "@/lib/assemblyRegistry";
import { canonicalFor } from "@/lib/pageMetadata";
import styles from "./assembly.module.css";

export const metadata: Metadata = {
  title: "議会アカウンタビリティ｜35議会の議案・表決・政務活動費・視察",
  description: "北海道・大阪・福岡・愛知・神奈川・埼玉・千葉・兵庫・宮城・静岡・広島・京都・新潟・岡山の35議会について、公式資料と情報公開状況を確認します。議員スコアや活動量ランキングは作りません。",
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
      <p className={styles.attention}>確認できること：35議会の登録済み議案・議決結果と資料ごとの公開範囲。岡山県議会・岡山市議会・新潟県議会・新潟市議会・京都府議会・京都市会・広島県議会・広島市議会・千葉県議会・千葉市議会・兵庫県議会・神戸市会・宮城県議会・仙台市議会・静岡県議会・静岡市議会・浜松市議会を含みます。岡山県議会は賛否の公表自体がなく、会派別・議員別賛否を未公表として扱い推測していません。岡山市議会の政務活動費は令和7年度分が未公表で、過年度の公表状況から補完していません。京都府議会の賛否表は賛成の場合のみ表示され、空欄は未確定（unknown）として登録し、反対票と推測していません。京都市会の賛否は会派別と結果ページの無所属議員7名分の個人名列のみです。全議員分の個人別賛否は市会だより公表後に追加する予定であり、推計しません。京都府議会・京都市会とも令和7年度決算は認定済みです。静岡県議会の会派・無所属議員別の賛否は本会議表決後の公式記録で、令和7年度決算認定17件は未議決（pending）です。静岡市議会の賛否は会派別、浜松市議会は議員個人別であり、未公表の単位へ変換・推測しません。宮城県議会の議員個人別表決状況は本会議での表決そのものの事後記録で、採決前の会派態度集約ではありません。宮城県議会の会派別賛否は公表・登録されていません。仙台市議会の賛否は会派別公表で、議員個人票を推測しません。兵庫県議会の会派態度は、表決そのものの記録ではなく採決に先立って各会派・議員が表明した態度を議会事務局が集約したものです。千葉県議会の賛否一覧は3表で○の意味が異なります。議案表は反対、発議案表は賛成内訳、請願表は採択賛成を示します。令和7年度決算認定は継続審査中（pending）です。千葉県議会の会派別賛否と無所属議員の個人名列を区別し、会派所属議員の個人票を推測しません。埼玉県議会の会派別賛否は議会運営委員会で確認した態度で、本会議の投票記録ではありません。さいたま市議会の賛否は会派別と無所属議員の個人名列であり、全議員の個人別記録ではありません。川口市議会の賛否は公式公表なし（not_published）です。名古屋市会では第134号のみ議員別賛否68人分を確認でき、他の登録議案は全会一致です。愛知県議会の会派態度は採決前に議会運営委員会で確認されたもので、本会議の投票記録そのものではありません。福岡県議会の会派別・議員別賛否など、公表されていない情報は推測しません。</p>
    </header>
    <section aria-label="35議会の情報公開状況" className={styles.grid}>
      {assemblySlugs.map(slug => {
        const entry=assemblies[slug]; const assembly=entry.assembly;
        const members=slug==="hyogo-prefecture" ? 82 : slug==="miyagi-prefecture" ? 56 : slug==="shizuoka-prefecture" ? 67 : slug==="hamamatsu-city" ? 44 : assembly.factions.reduce((sum,faction)=>sum+faction.member_count,0) + (slug==="chiba-prefecture" ? 2 : 0);
        return <article className={styles.card} key={slug}>
          <p className="eyebrow">Reviewed</p><h2>{assembly.name}</h2>
          <p className={styles.note}>現任期：{assembly.term_start} 〜 {assembly.term_end}</p>
          {slug==="shizuoka-prefecture" ? <p className={styles.note}>県議会の現員は67人（定数68人）。会派別の賛否は採決後の表決記録です。未議決の令和7年度決算認定17件を可決済みとして扱いません。</p> : null}
          {slug==="hamamatsu-city" ? <p className={styles.note}>浜松市議会の定数46人・現員44人。賛否は議員個人別の事後記録で、会派別賛否表は公表されていません。</p> : null}
          {slug==="miyagi-prefecture" ? <p className={styles.note}>現員56人は第401回定例会時点の公式議員名簿と表決状況の列構成によります。会派別賛否の推計には使用しません。</p> : null}
          {slug==="hyogo-prefecture" ? <p className={styles.note}>現員82人は2026年11月2日時点の公式名簿によります。会派の人数は令和7年度政務活動費の交付名簿に基づき、同じ時点の構成とみなしません。</p> : null}
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
