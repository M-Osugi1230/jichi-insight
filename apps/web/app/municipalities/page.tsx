import Link from "next/link";

import { PageIntro } from "@/components/PageIntro";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { StatusBadge } from "@/components/StatusBadge";
import { municipalityMeta, sourcesForMunicipality, type MunicipalityKey } from "@/lib/catalog";

const keys = Object.keys(municipalityMeta) as MunicipalityKey[];

export default function MunicipalitiesPage() {
  return (
    <main>
      <SiteHeader />
      <div className="pageShell">
        <PageIntro eyebrow="Pilot municipalities" title="自治体ごとの物語を、一本につなぐ。"><p>現在は3自治体を対象に、財政、重点事業、公約、議会を横断するデータモデルを作っています。自治体ページは、レビュー済み財政データの収録後に順次公開します。</p></PageIntro>
        <div className="municipalityListPage">
          {keys.map((key, index) => {
            const municipality = municipalityMeta[key];
            const sourceCount = sourcesForMunicipality(key).length;
            return <article className="municipalityRow" key={key}><span className="municipalityNumber">{String(index + 1).padStart(2, "0")}</span><div className="municipalityRowMain"><div className="municipalityRowHeading"><div><p>{municipality.type}</p><h2>{municipality.name}</h2></div><StatusBadge label={municipality.status} tone="progress" /></div><p>{municipality.summary}</p><dl className="municipalityFacts"><div><dt>公式資料入口</dt><dd>{sourceCount}件</dd></div><div><dt>財政データ</dt><dd>整備前</dd></div><div><dt>重点事業</dt><dd>選定前</dd></div></dl><Link href={`/sources#${key}`}>確認済み資料を見る</Link></div></article>;
          })}
        </div>
      </div>
      <SiteFooter />
    </main>
  );
}
