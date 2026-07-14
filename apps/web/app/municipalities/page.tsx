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
        <PageIntro eyebrow="Pilot municipalities" title="自治体ごとの物語を、一本につなぐ。">
          <p>
            現在は3自治体を対象に、財政、重点事業、公約、議会を横断するデータモデルを作っています。
            レビューが完了した範囲だけを自治体ページとして順次公開します。
          </p>
        </PageIntro>
        <div className="municipalityListPage">
          {keys.map((key, index) => {
            const municipality = municipalityMeta[key];
            const sourceCount = sourcesForMunicipality(key).length;
            return (
              <article className="municipalityRow" key={key}>
                <span className="municipalityNumber">
                  {String(index + 1).padStart(2, "0")}
                </span>
                <div className="municipalityRowMain">
                  <div className="municipalityRowHeading">
                    <div>
                      <p>{municipality.type}</p>
                      <h2>{municipality.name}</h2>
                    </div>
                    <StatusBadge
                      label={municipality.status}
                      tone={municipality.href ? "verified" : "progress"}
                    />
                  </div>
                  <p>{municipality.summary}</p>
                  <dl className="municipalityFacts">
                    <div>
                      <dt>公式資料入口</dt>
                      <dd>{sourceCount}件</dd>
                    </div>
                    <div>
                      <dt>財政データ</dt>
                      <dd>{municipality.href ? "当初予算2項目" : "整備前"}</dd>
                    </div>
                    <div>
                      <dt>評価</dt>
                      <dd>未実施</dd>
                    </div>
                  </dl>
                  <div className="heroActions">
                    {municipality.href ? (
                      <Link href={municipality.href}>自治体ページを見る</Link>
                    ) : null}
                    <Link href={`/sources#${key}`}>確認済み資料を見る</Link>
                  </div>
                </div>
              </article>
            );
          })}
        </div>
      </div>
      <SiteFooter />
    </main>
  );
}
