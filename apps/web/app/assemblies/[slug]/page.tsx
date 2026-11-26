import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { ProgressiveRecordFilter } from "@/components/ProgressiveRecordFilter";
import { canonicalFor } from "@/lib/pageMetadata";
import {
  assemblies, assemblySlugs, evidenceFor, isAssemblySlug,
  type AssemblySource, type Evidence,
} from "@/lib/assemblyRegistry";
import styles from "../assembly.module.css";

type PageProps = { params: Promise<{ slug: string }> };
export function generateStaticParams() { return assemblySlugs.map(slug => ({ slug })); }
export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { slug } = await params;
  if (!isAssemblySlug(slug)) return {};
  return { title: `${assemblies[slug].assembly.name}｜議案・表決・政務活動費・視察`,
    alternates: {canonical:canonicalFor(`/assemblies/${slug}`)} };
}
const names:Record<string,string>={
 member_roster:"議員名簿", faction_composition:"会派構成",committee_composition:"委員会",
 proposals_and_results:"議案・議決結果",faction_votes:"会派別賛否",member_votes:"議員別賛否",
 political_activity_expense_reports:"政務活動費の収支報告書",
 political_activity_expense_receipts:"政務活動費の領収書",inspection_trip_reports:"視察報告書",
 meeting_minutes:"会議録",session_broadcast:"議会中継",petition_results:"請願・陳情の審議結果",
};
const availability:Record<string,string>={
 published:"公表あり",not_published:"公表されていません",
 restricted:"窓口等で閲覧",unknown:"公開状況未確認",not_found:"確認できず",
};
const granularity:Record<string,string>={
 member:"議員単位",faction:"会派単位",assembly:"議会単位",
 document:"資料単位",none:"公開単位なし",unknown:"公開粒度未確認",
};
const positions:Record<string,string>={
 for:"賛成",against:"反対",split:"会派内で賛否が分かれた",
 abstain:"棄権",absent:"欠席",unknown:"賛否未確認",
};
const yen=(amount:number|null)=>amount===null?"未収録":`${amount.toLocaleString("ja-JP")}円`;
const date=(value:string|null)=>value??"未収録";
function Sources({ ids, available }:{ ids:string[];available:AssemblySource[] }) {
  const unique=[...new Set(ids)];
  if (!unique.length) return <p className={styles.source}>対応する出典IDは未収録です。</p>;
  return <p className={styles.source}>公式出典：{unique.map((id,i)=>{
    const source=available.find(s=>s.id===id);
    return <span key={id}>{i>0?" ／ ":""}
      {source?.url ? <a href={source.url} target="_blank" rel="noopener noreferrer">{source.title}</a> : `${id}（リンク未収録）`}
      {source ? `（確認索引日 ${source.indexed_at}）` : ""}
    </span>;
  })}</p>;
}
function EvidenceLink({ packets, sources, hideOpenQuestions = false }:{ packets:Evidence[];sources:AssemblySource[];hideOpenQuestions?:boolean }) {
  if (!packets.length) return <p className={styles.warning}>証拠パケット：未収録（該当資料で追加確認が必要）</p>;
  const ids=[...new Set(packets.flatMap(packet=>packet.claims.flatMap(c=>c.source_ids)))];
  return <details><summary>Evidence Packet（{packets.length}件・該当箇所と確認範囲）</summary>
    <p className={styles.note}>レビュー状態：{[...new Set(packets.map(p=>p.review_status))].join("／")}</p>
    {packets.flatMap(packet=>packet.claims).map((claim,i)=><p className={styles.note} key={i}>
      {claim.field}：{claim.statement}。資料の位置：{claim.location_note??"詳細位置未収録"}
    </p>)}
    {!hideOpenQuestions ? <p className={styles.note}>未解決の確認事項：{packets.flatMap(p=>p.open_questions).join("／")||"記載なし"}</p> : null}
    <Sources ids={ids} available={sources} />
  </details>;
}
export default async function AssemblyDetailPage({params}:PageProps){
  const {slug}=await params;
  if(!isAssemblySlug(slug)) notFound();
  const data=assemblies[slug]; const assembly=data.assembly;
  // Saitama prefectural assembly has three unaffiliated members represented by individual-name columns.
  const members=slug==="hyogo-prefecture" ? 82 : slug==="miyagi-prefecture" ? 56 : slug==="shizuoka-prefecture" ? 67 : slug==="hamamatsu-city" ? 44 : assembly.factions.reduce((total,f)=>total+f.member_count,0) + (slug==="saitama-prefecture" ? 3 : slug==="chiba-prefecture" ? 2 : 0);
  const receipt=data.disclosure.items.find(item=>item.item==="political_activity_expense_receipts");
  const votingInfo=data.disclosure.items.find(item=>item.item==="faction_votes");
  const noFactionVotes=votingInfo?.availability==="not_published";
  const votesByProposal=new Map(data.votes.map(v=>[v.proposal_id,v]));
  const factionByVote=new Map<string,typeof data.factionVotes>();
  for(const faction of data.factionVotes){
    const list=factionByVote.get(faction.vote_id)??[];
    list.push(faction); factionByVote.set(faction.vote_id,list);
  }
  return <><SiteHeader/><main><div className="pageShell">
    <header className={styles.intro}>
      <p className="eyebrow">Reviewed · Assembly accountability</p><h1>{assembly.name}</h1>
      <p>自治体議会の議案と表決、政務活動費、視察および情報公開範囲を公式資料に沿って表示します。議会が審議した予算と執行部の事業成果を、議会・議員の成績として結びつけません。</p>
      <p className={styles.attention}>確認できること：議案・議決結果と登録済みの公式資料。会派別・議員別の賛否は各議会の公開範囲でのみ表示します。議員や会派を採点・順位付けしません。</p>
      {slug==="hokkaido-prefecture" ? <p className={styles.attention}>北海道議会は議員個人別・会派別の賛否を公表していません。政務活動費は集計値と閲覧制度のみを登録しています。委員会視察・議員派遣の個別資料は公表されていません。</p> : null}
      {slug==="saitama-prefecture" ? <p className={styles.attention}>会派別賛否は議会運営委員会で確認した態度であり本会議の投票記録ではありません。個人名列は無所属3名のみです。</p> : null}
      {slug==="saitama-city" ? <p className={styles.attention}>会派別の賛否と無所属議員の個人名列のみ公表されています。会派所属議員の個人票を復元しません。</p> : null}
      {slug==="kawaguchi-city" ? <p className={styles.attention}>川口市議会は賛否の公式公表なし（not_published）。会派別・議員個人別の内訳は推定しません。</p> : null}
      {slug==="sapporo-city" ? <p className={styles.attention}>札幌市議会の賛否は会派別のみ公表され、議員個人別の賛否は公表されていません。政務活動費の領収書は閲覧申請形式のため登録対象外です。</p> : null}
      {slug==="asahikawa-city" ? <p className={styles.attention}>旭川市議会の議員別賛否は賛否が分かれた8件のみ公表されています。全会一致の案件には議員別内訳がありません。陳情の賛否は「採択への賛否」であり、陳情内容への賛否と混同しません。</p> : null}
      {slug==="aichi-prefecture" ? <p className={styles.attention}>愛知県議会の会派の態度は、採決に先立って議会運営委員会で確認したもので、本会議の投票記録そのものではありません。無所属の内訳は原資料の印字に従い、議員数との不一致を補完・推計しません。</p> : null}
      {slug==="nagoya-city" ? <p className={styles.attention}>名古屋市会の議員別賛否は第134号（名古屋城天守閣の契約変更）のみ68人分が公表されています。他の登録議案は全会一致です。「議決に参加できない」は議長の立場を示し、欠席ではありません。</p> : null}
      {slug==="toyota-city" ? <p className={styles.attention}>豊田市議会の会派別採決人数は公式の印字どおりです。自民クラブは議長を除く・欠席1名の人数であり、会派所属人数と表決人数を同一視しません。</p> : null}
      {slug==="osaka-prefecture" ? <p className={styles.attention}>大阪府議会の賛否は会派別のみ公表され、議員個人別の賛否は公表されていません。請願第36号は第1〜4項と第5項を分けた項目別採決で、項目群によって態度が異なります。令和7年度決算認定関連の18件は閉会中継続審査中であり、確定した決算認定として扱いません。</p> : null}
      {slug==="osaka-city" ? <p className={styles.attention}>大阪市会の賛否は会派別のみ公表されています。政務活動費は会派交付分の収支報告書・領収書がWeb公表されていますが、交付対象議員個人分の収支報告書はWeb公表されず、市会図書室での閲覧のみです。</p> : null}
      {slug==="sakai-city" ? <p className={styles.attention}>堺市議会の会派別賛否は「主な議案」10件のみ公表され、その他の議案の会派別賛否は公表されていません。陳情19件は請願・議案の採決とは別系統の「陳情回答綴」で回答文が公表され、採択・不採択の結論とは扱いません。</p> : null}
      {slug==="kanagawa-prefecture" ? <p className={styles.attention}>神奈川県議会の賛否は会派別のみ公表され、議員個人別の賛否は公表されていません。凡例に欠席者等（▲）がありますが、登録対象の令和8年第2回定例会では▲は使われていません。欠席者等は備考欄の記載をそのまま扱います。</p> : null}
      {slug==="yokohama-city" ? <p className={styles.attention}>横浜市会の議員個人別賛否は、議員別賛否表に記載された「委員会報告への賛否」です。請願の賛否は請願内容への賛否ではなく、採択への賛否として登録しています。令和7年度決算関係27件は第4回定例会（2026年10月29日開会）の決算特別委員会で継続審査中です。政務活動費の領収書はWeb公表されず、市会図書室での閲覧のみです。</p> : null}
      {slug==="kawasaki-city" ? <p className={styles.attention}>川崎市議会は無所属議員5名について個人名の列で賛否を公表しています。会派所属議員の個人別賛否は公表されていません。政務活動費はWeb公開がなく、議会局での閲覧制度のみを登録しています。陳情は委員会で審査され、本会議での表決対象ではありません。</p> : null}
      {slug==="saitama-prefecture" ? <p className={styles.attention}>埼玉県議会の会派別賛否は、採決に先立つ議会運営委員会で確認した態度です。本会議の投票記録そのものではありません。無所属3名は個人名列で公表され、会派所属議員の個人票は公表されていません。政務活動費の収支報告書・領収書はWeb公開されています。</p> : null}
      {slug==="saitama-city" ? <p className={styles.attention}>さいたま市議会の賛否は会派別と無所属議員の個人名列で公表されます。全議員の個人別賛否表ではありません。政務活動費は会派分と議員個人分を半期ごとの公式公開単位で表示します。領収書も公開されています。</p> : null}
      {slug==="kawaguchi-city" ? <p className={styles.attention}>川口市議会の会派別・議員個人別賛否は公式公表なし（not_published）です。議決結果のみから賛否を推定しません。政務活動費は会派分と議員個人分の収支報告書・領収書をWeb公開しています。令和7年度決算認定4件は継続審査中です。</p> : null}
      {slug==="shizuoka-prefecture" ? <p className={styles.attention}>静岡県議会・令和8年9月定例会の議決結果一覧は本会議の表決そのものの事後記録です。採決前の会派態度表明の集約ではありません。会派3団体の賛否と無所属6名の個人名列を区別し、会派所属議員の個人別投票を推測しません。令和7年度決算認定17件は未議決（pending）であり、議決済みとは表示しません。</p> : null}
      {slug==="shizuoka-city" ? <p className={styles.attention}>静岡市議会・令和8年9月定例会の賛否は9会派の会派別公表です。議員個人別の賛否は公表されていません。会派票を個人票として復元しません。</p> : null}
      {slug==="hamamatsu-city" ? <p className={styles.attention}>浜松市議会・令和8年第3回定例会の賛否は議員個人別の事後表決記録です。会派別の賛否集計は公表されていません。議員別賛否2,728件は公式PDFの登録値であり、会派態度として再集計しません。</p> : null}
      {slug==="shizuoka-prefecture" || slug==="shizuoka-city" || slug==="hamamatsu-city" ? <p className={styles.attention}>登録議案等{data.proposals.length}件、表決{data.votes.length}件、会派別賛否{data.factionVotes.length}件、政務活動費{data.expenses.length}単位、視察{data.trips.length}件を登録しています。</p> : null}
      {slug==="miyagi-prefecture" ? <p className={styles.attention}>宮城県議会・第401回9月定例会の「各議員の表決状況」は、本会議の表決そのものの事後記録です。採決に先立つ会派態度の集約ではありません。議員個人別の賛否、議長・欠席、表決方法や人数を公式資料の印字に従って表示し、会派別賛否は再集計・推測しません。定数59人・会期時点の現員56人です。</p> : null}
      {slug==="sendai-city" ? <p className={styles.attention}>仙台市議会・令和8年第3回定例会は会派別の賛否を公表します。会派内で賛否が分かれた案件は公式の人数内訳の範囲で表示します。議員個人別の賛否は公表されておらず、復元しません。</p> : null}
      {slug==="miyagi-prefecture" || slug==="sendai-city" ? <p className={styles.attention}>登録議案{data.proposals.length}件、表決{data.votes.length}件、会派別賛否{data.factionVotes.length}件、政務活動費{data.expenses.length}単位、委員会調査{data.trips.length}件。登録データの件数に基づきます。</p> : null}
      {slug==="hyogo-prefecture" ? <p className={styles.attention}>「議案等に対する会派態度」は、表決そのものの記録ではなく、採決に先立って各会派・議員が表明した態度を議会事務局が集約した資料です。本会議の議員別投票記録として扱いません。無所属5名についてのみ個人名列があり、会派所属議員の個人別賛否は公表されていません。議員定数86人・現員82人（2026年11月2日更新の公式名簿）。会派所属人数は令和7年度政務活動費の交付名簿に基づくため、現在の構成と同一視しません。</p> : null}
      {slug==="kobe-city" ? <p className={styles.attention}>正式名称は神戸市会です。議員定数65人・登録名簿の現員63人。会派別賛否と無所属2名（平野章三・上原みなみ）の個人名列を公表していますが、会派所属議員の個人別賛否は公表されていません。</p> : null}
      {slug==="hyogo-prefecture" || slug==="kobe-city" ? <p className={styles.attention}>登録議案{data.proposals.length}件、議決結果等の記録{data.votes.length}件、会派態度・賛否{data.factionVotes.length}件、政務活動費{data.expenses.length}単位、視察・委員会調査{data.trips.length}件を登録しています。</p> : null}
      {slug==="chiba-prefecture" ? <p className={styles.attention}>千葉県議会の賛否一覧は3表で○の意味が異なります。議案表の○は原案に反対する会派等、発議案表の○は賛成会派等の内訳、請願表の○は採択に賛成する会派等を示します。表の種類をまたいで○を同じ意味として解釈しません。令和7年度決算認定「決算認定について」は継続審査中（pending）です。個人名列は無所属議員2名のみで、会派所属議員の個人票は公表されていません。</p> : null}
      {slug==="chiba-prefecture" || slug==="chiba-city" ? <p className={styles.attention}>登録議案{data.proposals.length}件、表決{data.votes.length}件、会派別賛否{data.factionVotes.length}件、政務活動費{data.expenses.length}単位、視察{data.trips.length}件を登録しています。件数はこのページのReviewed登録データに基づきます。</p> : null}
      <p><Link href="/assemblies">33議会の一覧に戻る</Link></p>
      <nav aria-label="ページ内のセクション">
        <a href="#basic">基本情報</a> ／ <a href="#proposals">会期と議案</a> ／ <a href="#votes">表決</a> ／ <a href="#expenses">政務活動費</a> ／ <a href="#trips">視察</a> ／ <a href="#disclosure">情報公開</a>
      </nav>
    </header>

    <section id="basic" className={styles.section}>
      <h2>基本情報</h2>
      <dl className={styles.facts}>
        <div><dt>任期</dt><dd>{assembly.term_start} 〜 {assembly.term_end}</dd></div>
        <div><dt>定数／名簿上の現員</dt><dd>{assembly.seat_count}人／{members}人{members<assembly.seat_count?`（欠員 ${assembly.seat_count-members}人）`:""}</dd></div>
        <div><dt>登録委員会数</dt><dd>{assembly.committees.length}委員会</dd></div>
      </dl>
      <h3>会派構成（名簿登録順）</h3>
      <ul className={styles.factions}>{assembly.factions.map(f=><li key={f.name}>{f.name}：{f.member_count}人</li>)}</ul>
      <details><summary>登録委員会の名称</summary><ul>{assembly.committees.map(c=><li key={c}>{c}</li>)}</ul></details>
      <Sources ids={assembly.sources} available={data.sources}/>
      <EvidenceLink packets={evidenceFor(data,assembly.id)} sources={data.sources}/>
    </section>

    <section id="proposals" className={styles.section}>
      <h2>会期と議案</h2>
      <p className={styles.note}>登録議案を会期・議案番号・件名から探せます。絞り込みを解除すると全登録議案が表示されます。出典リンクは各会期・議案名のすぐ下に表示しています。</p>
      {slug==="osaka-prefecture" ? <p className={styles.attention}>請願第36号は第1〜4項と第5項を別々に採決した記録です。項目ごとの賛否を一括の結論として扱いません。令和7年度決算認定関連18件は閉会中継続審査中です。</p> : null}\n      {slug==="sakai-city" ? <p className={styles.attention}>「主な議案」に掲載された10件のみ会派別賛否が公表されています。その他の議案の賛否は未公表です。陳情19件は議案・請願の採決とは別系統の「陳情回答綴」で回答文を公開し、採択・不採択の決定とは扱いません。</p> : null}
      <p className={styles.note}>出典に議決結果の原文言が登録されていない項目では、正確な文言を推測せず「登録結果コード」をそのまま表示します。原文は各出典をご確認ください。日付や提出者の欠損も補完しません。</p>
      <ProgressiveRecordFilter
        kind="proposals"
        total={data.proposals.length}
        sessions={data.sessions.map((session) => ({ id: session.id, name: session.name }))}
      >
      {data.sessions.map(session=><section key={session.id} data-filter-section="">
        <h3>{session.name}</h3><p className={styles.note}>段階：議決結果（登録コード）／確認基準日：{data.disclosure.as_of}／会期開始：{date(session.start_date)}／終了：{date(session.end_date)}</p>
        <Sources ids={session.sources} available={data.sources}/>
        <div className={styles.tableWrap}><table className={styles.table}>
          <thead><tr><th>議案番号</th><th>議案名・出典</th><th>提出者（登録値）</th><th>議決日</th><th>登録結果コード・表決</th></tr></thead>
          <tbody>{data.proposals.filter(p=>p.session_id===session.id).map(proposal=>{
            const vote=votesByProposal.get(proposal.id);
            const factionVotes=vote?factionByVote.get(vote.id)??[]:[];
            return <tr key={proposal.id} id={proposal.id} data-filter-entry="" data-filter-group={session.id} data-search-text={`${proposal.proposal_number} ${proposal.title}`}>
              <td>{proposal.proposal_number}</td>
              <td><strong>{proposal.title}</strong>
                {proposal.related_fiscal_record_ids.length>0 ? <p><Link href={`/municipalities/${slug}`}>関連する財政ビューへ（接続済み fiscal record {proposal.related_fiscal_record_ids.length}件）</Link></p> : null}
                <Sources ids={proposal.sources} available={data.sources}/>
                <EvidenceLink packets={evidenceFor(data,proposal.id)} sources={data.sources} hideOpenQuestions={slug==="nagoya-city" && proposal.proposal_number==="第134号"}/>
              </td>
              <td>{proposal.submitted_by||"未収録"}</td>
              <td>{date(proposal.decided_at)}</td>
              <td>{proposal.outcome||"未収録"}
                {vote ? <details><summary>表決の公開範囲・会派別内訳</summary>\n                  {vote.item_scope ? <p className={styles.note}>採決対象項目：{vote.item_scope}。項目ごとに採決された記録です。</p> : null}
                  {vote.member_vote_availability==="published" && vote.member_votes?.length
                    ? <div>
                        <p>公式公表の議員別賛否（{vote.member_votes.length}人分）。「議決に参加できない」は議長の扱いであり、欠席ではありません。</p>
                        <ul>{vote.member_votes.map((member,index)=>
                          <li key={`${member.member_name}-${index}`}>{member.member_name}：{member.position==="for"?"賛成":member.position==="against"?"反対":member.position==="excused"?"議決に参加できない":positions[member.position]??member.position}</li>
                        )}</ul>
                      </div>
                    : <p>{slug==="nagoya-city" && vote.method==="unanimous"
                      ? "全会一致（議員別賛否の個票は作成・公表されていません）"
                      : "議員ごとの賛否は公表されていません。"}</p>}
                  {slug==="aichi-prefecture" ? <p className={styles.attention}>会派の態度は、採決に先立って議会運営委員会で確認したもので、本会議の投票記録そのものではありません。無所属の内訳は原資料の印字どおりです。</p> : null}
                  {slug==="toyota-city" ? <p className={styles.note}>会派別人数は印字どおりです。自民クラブは議長を除く・欠席1名であり、所属人数とは一致しない場合があります。</p> : null}
                  {noFactionVotes?<p>会派ごとの賛否は公表されていません。</p>:
                    factionVotes.length ? <ul>{factionVotes.map(f=><li key={f.id}>{f.faction_name}（会派人数：{f.member_count??"未収録"}人）：{positions[f.position]??`登録値 ${f.position}`}{f.for_count!==null && f.for_count!==undefined ? `／賛成 ${f.for_count}人` : ""}{f.against_count!==null && f.against_count!==undefined ? `／反対 ${f.against_count}人` : ""}</li>)}</ul>
                    : <p>この議案の会派別賛否は未収録です。</p>}
                  <p className={styles.note}>賛否人数の集計：{vote.totals===null?"公表されていません（人数の推計・復元はしません）":"出典記録の範囲のみ。会派人数と採決人数を同一視しません。"}</p>
                  <Sources ids={vote.sources} available={data.sources}/>
                  <EvidenceLink packets={evidenceFor(data,vote.id)} sources={data.sources} hideOpenQuestions={slug==="nagoya-city" && vote.member_vote_availability==="published"}/>
                </details>:<p>表決レコード未収録</p>}
              </td>
            </tr>;
          })}</tbody>
        </table></div>
      </section>)}
      </ProgressiveRecordFilter>
      {!data.sessions.length?<p>会期と議案は未収録です。</p>:null}
    </section>

    <section id="votes" className={styles.section}>
      <h2>表決の公開範囲</h2>
      <p className={styles.attention}>{slug==="osaka-prefecture" ? "大阪府議会は会派別の賛否のみ公表し、議員個人別の賛否は公表されていません。請願第36号は第1〜4項と第5項を分けた項目別採決です。" : slug==="sakai-city" ? "堺市議会は「主な議案」10件のみ会派別賛否を公表し、その他の議案は未公表です。陳情19件は別系統の陳情回答綴で扱います。" : slug==="osaka-city" ? "大阪市会は会派別賛否のみ公表し、議員個人別の賛否は公表されていません。" : slug==="asahikawa-city" ? "議員ごとの賛否は賛否が分かれた8件のみ公表されています。全会一致の案件には個別内訳がなく、陳情の表決は採択への賛否です。" : slug==="nagoya-city"
        ? "議員ごとの賛否は第134号のみ68人分が公式公表されています。残る議案は全会一致です。議長の「議決に参加できない」は欠席ではありません。"
        : "議員ごとの賛否は公表されていません。議員名簿や会派の表決から、個人の賛否を推測・復元することはしません。"}</p>
      {slug==="sapporo-city" ? <p className={styles.attention}>札幌市議会は会派別の賛否のみ公表し、議員個人別の賛否は公表されていません。</p> : null}
      {noFactionVotes?<p className={styles.attention}>会派ごとの賛否は公表されていません。</p>:
        <p>会派別賛否は登録済み議案の「表決の公開範囲・会派別内訳」から確認できます。会派内で賛否が分かれた場合はその旨を記し、議員個人の賛否は特定しません。</p>}
      {slug==="aichi-prefecture" ? <p className={styles.attention}>会派別態度は採決に先立ち議会運営委員会で確認した態度であり、本会議の投票記録そのものではありません。無所属の人数内訳は原資料の印字を保持します。</p> : null}
      {slug==="toyota-city" ? <p className={styles.attention}>自民クラブは議長を除く・欠席1名。会派別の賛否人数は公式印字のまま表示します。</p> : null}
      <p className={styles.note}>採決人数 totals が公表されていない議案では賛否人数の合計を表示しません。特に県議会の結果文言は議案別の原文がない場合、推測で「原案可決」等へ置き換えません。</p>
      <Sources ids={data.disclosure.sources} available={data.sources}/>
    </section>

    <section id="expenses" className={styles.section}>
      <h2>政務活動費（登録年度別）</h2>
      <p className={styles.attention}>{slug==="saitama-prefecture" ? "令和7年度の政務活動費は会派分11単位で公開されています。" : slug==="saitama-city" ? "政務活動費は会派と議員個人の半期単位で公開され、領収書もWebで公開されています。" : slug==="kawaguchi-city" ? "政務活動費は会派分5単位と議員個人43単位でWeb公開され、領収書も公表されています。" : slug==="osaka-city" ? "大阪市会の個人交付分の政務活動費収支報告書はWeb公表されておらず、市会図書室での閲覧のみです。会派交付分の公表資料と混同しません。" : slug==="hokkaido-prefecture" ? "北海道議会の政務活動費は集計値と閲覧制度のみが登録されています。領収書・個別支出を推計しません。" : slug==="sapporo-city" ? "札幌市議会の領収書は閲覧申請形式のため登録対象外です。" : slug==="fukuoka-city"?
        "福岡市議会は公式公開単位どおり会派交付分と議員個人分を併記します。":
        "公式公開単位は会派単位です。議員個人分の収支報告書は本登録に収録されておらず、個人別支出額を推測しません。"}
        {slug==="aichi-prefecture"
          ? "領収書等の写しは公式の収支報告書 PDF に含まれます。"
          : slug==="toyota-city"
            ? "政務活動費は会派別集計のみが Web 公表され、詳細の収支報告書・領収書等は Web 公表されていません（市政情報コーナーで閲覧）。"
            : "領収書は窓口でのみ閲覧可能です。"}支出額の順位付けはしません。</p>
      {slug==="saitama-prefecture" ? <p className={styles.attention}>埼玉県議会は令和7年度の会派交付分11単位。収支報告書と領収書等をWebで公開しています。</p> : null}
      {slug==="saitama-city" ? <p className={styles.attention}>さいたま市議会は会派分と議員個人分を半期単位でWeb公開し、領収書を含む報告書の公開単位を保持します。全議員に個人報告書があるとは限りません。</p> : null}
      {slug==="kawaguchi-city" ? <p className={styles.attention}>川口市議会は令和7年度分の会派5単位・議員個人43単位をWeb公開。収支報告書の残額不一致は公表値を改変せず保持します。</p> : null}
      <p className={styles.note}>掲載順は Reviewed 原資料の登録順です。交付額・支出額・残額は年度と公開単位を保ち、会派と議員の額を合算して個人の支出に帰属させません。</p>
      {slug==="osaka-prefecture" ? <p className={styles.attention}>令和7年度分は会派9・議員80の計89単位をWeb公開。収支報告書と領収書の公開範囲を確認できます。</p> : null}
      <div className={styles.recordList}>
      {data.expenses.map(exp=><article className={styles.record} key={exp.id}>
        <h3>{exp.recipient_name}</h3>
        <p className={styles.note}>公開単位：{exp.recipient_type==="member"?"議員個人":"会派"}／年度：{exp.fiscal_year}</p>
        <dl className={styles.facts}>
          <div><dt>交付額</dt><dd>{yen(exp.granted_yen)}</dd></div>
          <div><dt>支出額</dt><dd>{yen(exp.spent_yen)}</dd></div>
          <div><dt>差引残額</dt><dd>{exp.returned_yen===null?
            "支出が交付額を超過（詳細は出典資料）":yen(exp.returned_yen)}</dd></div>
        </dl>
        {exp.breakdown.length > 0 ? (
          <details><summary>支出の内訳（報告書上の区分）</summary>
            <ul>{exp.breakdown.map((b,i)=><li key={`${b.category}-${i}`}>{b.category}：{yen(b.amount_yen)}</li>)}</ul>
          </details>
        ) : <p className={styles.note}>支出の内訳：集計値のみ登録（科目別内訳は未収録）</p>}
        <p className={styles.note}>領収書：{exp.receipt_access==="in_person_only"?"窓口でのみ閲覧可能":exp.receipt_access==="published"?"Web 公表あり":exp.receipt_access==="not_published"?"Web では公表されていません":"公開状況を要確認"}。報告書：{exp.report_status==="published"?"公表あり":"公開状況未確認"}。</p>
        <Sources ids={exp.sources} available={data.sources}/>
        <EvidenceLink packets={evidenceFor(data,exp.id)} sources={data.sources}/>
      </article>)}
      </div>
      {!data.expenses.length?<p>政務活動費の登録済みレコードはありません。</p>:null}
      <p className={styles.note}>領収書の公開条件：{receipt?.note??"未収録"}</p>
    </section>

    <section id="trips" className={styles.section}>
      <h2>視察・海外活動（現任期）</h2>
      {slug==="hokkaido-prefecture" ? <p className={styles.attention}>北海道議会の委員会視察・議員派遣の資料は公表されておらず、個別レコードは未登録です。</p> : null}
      {slug==="kitakyushu-city" ? <p className={styles.attention}>北九州市議会では現任期分の視察報告書は公表されていません。確認できた過去の視察資料は現任期より前のため、現任期の実績として表示しません。</p>:null}
      {slug==="aichi-prefecture" || slug==="nagoya-city" ? <p className={styles.attention}>この議会の委員会視察報告書・一覧は公式 Web 上で公表が確認できず、本サイトでは未登録です。別制度の海外調査団・議員派遣報告書を委員会視察の実績へ転用しません。</p> : null}
      {data.trips.length ? <div className={styles.recordList}>
        {data.trips.map(trip=><article key={trip.id} className={styles.record}>
          <h3>{trip.title}</h3>
          <p className={styles.note}>日程：{date(trip.start_date)} 〜 {date(trip.end_date)}／行先：{trip.destinations.join("、")||"未収録"}</p>
          <p>目的：{trip.purpose??"未収録"}</p>
          <p>参加人数：{trip.participant_count===null?"未収録":`${trip.participant_count}人`}</p>
          <p><strong>費用：{trip.total_cost_yen!==null&&trip.cost_status==="available"?
            yen(trip.total_cost_yen):"費用は公表されていません"}</strong></p>
          <p>報告書：{trip.report_status==="published"?"公表あり（下記公式資料リンク）":"公表・確認状況は出典を参照"}</p>
          <details><summary>登録された参加者</summary>
            {trip.participants.length?<ul>{trip.participants.map((p,i)=><li key={`${p.name}-${i}`}>{p.name}（{p.role}／{p.participant_type==="elected_member"?"議員":"同行者等"}）</li>)}</ul>:<p>参加者名簿は未収録です。</p>}
          </details>
          <details><summary>その後の政策反映・未確認事項</summary>
            {trip.policy_follow_up.length?<ul>{trip.policy_follow_up.map((note,i)=><li key={i}>{note}</li>)}</ul>:<p>政策反映の事実は未収録です。視察実施自体を政策成果とは扱いません。</p>}
          </details>
          <Sources ids={trip.sources} available={data.sources}/>
          <EvidenceLink packets={evidenceFor(data,trip.id)} sources={data.sources}/>
        </article>)}
      </div>:<p>現任期に属する視察の Reviewed レコードは未収録です。過去の訪問を現任期へ移し替えません。</p>}
    </section>

    <section id="disclosure" className={styles.section}>
      <h2>この議会の情報公開</h2>
      <p className={styles.note}>DisclosureProfile の各項目を、登録済み availability／granularity／note を変更せず掲載します。確認日：{data.disclosure.as_of}</p>
      <div className={styles.tableWrap}><table className={styles.table}>
        <thead><tr><th>公開項目</th><th>availability（登録値）</th><th>granularity（登録値）</th><th>公開範囲・注意書き／出典</th></tr></thead>
        <tbody>{data.disclosure.items.map(item=><tr key={item.item}>
          <th scope="row">{names[item.item]??item.item}</th>
          <td>{availability[item.availability]??item.availability}（{item.availability}）</td>
          <td>{granularity[item.granularity]??item.granularity}（{item.granularity}）</td>
          <td>{item.note||"注記未収録"}
            {item.source_url?<p className={styles.source}><a href={item.source_url} target="_blank" rel="noopener noreferrer">公式公開ページ</a></p>:
              <p className={styles.note}>項目固有の出典URLは未収録（下記資料索引を参照）</p>}
          </td>
        </tr>)}</tbody>
      </table></div>
      <Sources ids={data.disclosure.sources} available={data.sources}/>
      <p className={styles.note}>未公表は未実施・反対・非活動を意味しません。資料の不足から議員・会派の評価を導きません。</p>
    </section>
  </div></main><SiteFooter/></>;
}
