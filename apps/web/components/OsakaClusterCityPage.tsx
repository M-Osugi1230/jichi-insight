import Link from "next/link";

import osakaMunicipality from "../../../data/reviewed/osaka-city/municipality.json";
import sakaiMunicipality from "../../../data/reviewed/sakai-city/municipality.json";
import osakaFiscal from "../../../data/reviewed/osaka-city/fiscal_records.json";
import sakaiFiscal from "../../../data/reviewed/sakai-city/fiscal_records.json";
import osakaSettlements from "../../../data/reviewed/osaka-city/settlement_records.json";
import sakaiSettlements from "../../../data/reviewed/sakai-city/settlement_records.json";

import { SiteHeader } from "@/components/SiteHeader";
import { SiteFooter } from "@/components/SiteFooter";
import { currentExecutiveTerms, promisesForExecutive } from "@/lib/executives";
import { projectRegistry } from "@/lib/projectRegistry";

type OsakaCitySlug = "osaka-city" | "sakai-city";

const municipalities = {
  "osaka-city": { municipality: osakaMunicipality, fiscal: [...osakaFiscal, ...osakaSettlements] },
  "sakai-city": { municipality: sakaiMunicipality, fiscal: [...sakaiFiscal, ...sakaiSettlements] },
};

function formatAmount(amount: number | null): string {
  return amount === null ? "未収録" : `${new Intl.NumberFormat("ja-JP").format(amount)}円`;
}

/** Dedicated static routes for Reviewed Osaka cities not in the Phase 15 route manifest. */
export function OsakaClusterCityPage({ slug }: { slug: OsakaCitySlug }) {
  const { municipality, fiscal } = municipalities[slug];
  const mayor = currentExecutiveTerms.find(
    (term) => term.municipality_id === municipality.id &&
      term.office === "mayor" && term.status === "current" &&
      (term.review_status === "reviewed" || term.review_status === "verified"),
  );
  const promises = mayor
    ? promisesForExecutive(mayor).filter(
        (promise) => promise.review_status === "reviewed" || promise.review_status === "verified",
      )
    : [];
  const projects = projectRegistry[slug].projects.filter(
    (project) => project.review_status === "reviewed" && project.municipality_id === municipality.id,
  );
  const seriesCount = new Set(projects.map((project) => project.series_id)).size;
  const fiscalRecords = fiscal.filter(
    (record) => record.review_status === "reviewed" && record.municipality_id === municipality.id,
  );

  return (
    <>
      <SiteHeader />
      <main>
        <div className="pageShell">
          <section className="pageIntro">
            <p className="eyebrow">Reviewed municipality</p>
            <h1>{municipality.name_ja}</h1>
            <p>公式資料を根拠に、財政・重点事業・市長の現任期と公約の登録範囲を区別して掲載します。事業成果や公約達成率を独自に判定しません。</p>
            <p><a href={municipality.official_url} target="_blank" rel="noreferrer">自治体公式サイトを開く</a></p>
          </section>

          <section className="contentSection" id="city-finance">
            <div className="sectionIntro">
              <p className="eyebrow">Finance</p>
              <h2>Reviewed 財政レコード：{fiscalRecords.length}件</h2>
              <p>当初予算と普通会計決算は会計区分・年度・段階が異なるため、金額を直接比較しません。</p>
            </div>
            <ul>
              {fiscalRecords.map((record) => (
                <li key={record.id}>
                  <strong>{record.fiscal_year}年度・{record.metric_label}</strong>
                  <p>{formatAmount(record.amount_yen)}（{record.stage === "settlement" ? "決算" : "予算"}）</p>
                  <p>{record.note}</p>
                </li>
              ))}
            </ul>
          </section>

          <section className="contentSection" id="mayor-promises">
            <div className="sectionIntro">
              <p className="eyebrow">Executive / Promises</p>
              <h2>市長の現任期と公約</h2>
              <p>市長：{mayor?.person_name ?? "現任期の確認中"}</p>
              <p>{promises.length > 0 ? `Reviewed 公約原文：${promises.length}件` : "公約原文：未登録"}</p>
              <p>公約の未登録は、実際の公約や活動が存在しないことを意味しません。</p>
            </div>
            {promises.length > 0 ? (
              <ul>
                {promises.map((promise) => <li key={promise.id}>{promise.title}</li>)}
              </ul>
            ) : null}
            <p><Link href={`/promises#${slug}`}>公約の根拠とレビュー状態を見る</Link></p>
          </section>

          <section className="contentSection" id="priority-projects">
            <div className="sectionIntro">
              <p className="eyebrow">Reviewed projects</p>
              <h2>重点事業：{seriesCount}系列</h2>
              <p>登録対象は公式資料から選定した事業です。自治体の全事業を網羅したものではありません。</p>
            </div>
            <ul>
              {projects.map((project) => (
                <li key={project.id}>
                  <Link href={`/projects/${slug}/${project.series_id}`}>{project.name}</Link>
                </li>
              ))}
            </ul>
            <p><Link href={`/projects#${slug}`}>重点事業の一覧と出典を見る</Link></p>
          </section>
        </div>
      </main>
      <SiteFooter />
    </>
  );
}
