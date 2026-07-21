import { PageIntro } from "@/components/PageIntro";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { StatusBadge } from "@/components/StatusBadge";

const layers = [
  ["Fact", "事実", "公式資料に記載された数値、日付、発言、採決、契約。"],
  ["Comparison", "比較", "年度、人口、自治体区分、単位をそろえた比較。"],
  ["Interpretation", "解釈", "公開ルールに基づく「類似団体より高い」「目標に遅れ」などの説明。"],
  ["Evaluation", "評価", "複数の事実と比較から、明示した基準で行う判定。"],
];

export default function MethodologyPage() {
  return (
    <main>
      <SiteHeader />
      <div className="pageShell">
        <PageIntro eyebrow="Methodology" title="評価の前に、評価できる状態かを確認する。"><p>数字があるだけでは、公平な評価はできません。年度、単位、自治体の権限、比較対象、外部要因、データの欠損を確認し、根拠が不足する場合は「評価不能」と表示します。</p></PageIntro>
        <section className="contentSection"><div className="sectionHeadingWithBadge"><div><p className="eyebrow">Four layers</p><h2>事実から評価までを、混ぜない。</h2></div><StatusBadge label="総合点は未導入" tone="warning" /></div><div className="layerList">{layers.map(([label, title, text], index) => <article key={label}><span>{String(index + 1).padStart(2, "0")}</span><div><p>{label}</p><h3>{title}</h3><p>{text}</p></div></article>)}</div></section>
        <section className="contentSection roleSection"><p className="eyebrow">Role-based evaluation</p><h2>自治体、首長、議会は、別の役割で見る。</h2><div className="roleGrid"><article><h3>自治体</h3><p>財政健全性、行政効率、住民サービス、政策成果、将来持続性、情報公開。</p></article><article><h3>知事・市長</h3><p>公約の具体性、実行状況、成果、財政運営、方針変更の説明、組織統治。</p></article><article><h3>議会</h3><p>審議、修正、行政監視、政策提案、情報公開、住民参加、倫理・統治。</p></article></div></section>
        <section className="contentSection"><p className="eyebrow">Data quality</p><h2>データの深さを7段階で表示する。</h2><ol className="qualitySteps"><li><strong>Coverage</strong><span>資料・対象の存在を把握</span></li><li><strong>Indexed</strong><span>公式ページと資料位置を特定</span></li><li><strong>Current</strong><span>現行資料・有効期間を確認</span></li><li><strong>Extracted</strong><span>候補値を抽出、未レビュー</span></li><li><strong>Reviewed</strong><span>一次資料と人が照合</span></li><li><strong>Verified</strong><span>独立した二重確認を完了</span></li><li><strong>Published</strong><span>公開基準と画面検証を通過</span></li></ol></section>
        <section className="callout callout--dark"><div><p className="eyebrow">Scoring policy</p><h2>アルファ版では、人物の単一総合点を出しません。</h2><p>主要データ充足率、比較可能性、評価式公開、人手レビュー、訂正・反論手続がそろうまで、領域別の事実と進捗だけを表示します。</p></div></section>
      </div>
      <SiteFooter />
    </main>
  );
}
