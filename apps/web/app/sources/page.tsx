import { PageIntro } from "@/components/PageIntro";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { SourceCard } from "@/components/SourceCard";
import { StatusBadge } from "@/components/StatusBadge";
import { catalogStats, municipalityMeta, sourcesForMunicipality, type MunicipalityKey } from "@/lib/catalog";

const municipalityKeys = Object.keys(municipalityMeta) as MunicipalityKey[];

export default function SourcesPage() {
  return (
    <main>
      <SiteHeader />
      <div className="pageShell">
        <PageIntro eyebrow="Official source catalog" title="公式資料の所在から、透明にする。"><p>ここでは、評価結果ではなく、調査に使用する自治体・議会の公式ページを公開しています。一つの数字を確定するには、各入口から年度別資料と該当ページまで確認します。</p></PageIntro>
        <section className="catalogSummary" aria-label="資料カタログ概要">
          <div><strong>{catalogStats.officialSources}</strong><span>確認済み公式入口</span></div>
          <div><strong>{catalogStats.municipalities}</strong><span>初期対象自治体</span></div>
          <div><strong>0</strong><span>公開済み評価</span></div>
          <p><StatusBadge label="索引段階" tone="progress" />資料の存在確認と分類が完了した入口のみ掲載しています。数値や評価は、年度別資料を人が確認した後に公開します。</p>
        </section>
        {municipalityKeys.map((key) => {
          const municipality = municipalityMeta[key];
          const sources = sourcesForMunicipality(key);
          return <section className="sourceGroup" id={key} key={key}><div className="sourceGroupHeader"><div><p className="eyebrow">{municipality.type}</p><h2>{municipality.name}</h2></div><p>{sources.length}件の公式入口を確認済み</p></div><div className="sourceGrid">{sources.map((source) => <SourceCard source={source} key={source.id} />)}</div></section>;
        })}
      </div>
      <SiteFooter />
    </main>
  );
}
