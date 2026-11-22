import kumamotoPrefectureMunicipality from "../../../data/reviewed/kumamoto-prefecture/municipality.json";
import kumamotoCityMunicipality from "../../../data/reviewed/kumamoto-city/municipality.json";
import okayamaPrefectureMunicipality from "../../../data/reviewed/okayama-prefecture/municipality.json";
import okayamaCityMunicipality from "../../../data/reviewed/okayama-city/municipality.json";
import niigataPrefectureMunicipality from "../../../data/reviewed/niigata-prefecture/municipality.json";
import niigataCityMunicipality from "../../../data/reviewed/niigata-city/municipality.json";
import kyotoPrefectureMunicipality from "../../../data/reviewed/kyoto-prefecture/municipality.json";
import kyotoCityMunicipality from "../../../data/reviewed/kyoto-city/municipality.json";
import hiroshimaPrefectureMunicipality from "../../../data/reviewed/hiroshima-prefecture/municipality.json";
import hiroshimaCityMunicipality from "../../../data/reviewed/hiroshima-city/municipality.json";
import shizuokaPrefectureMunicipality from "../../../data/reviewed/shizuoka-prefecture/municipality.json";
import shizuokaCityMunicipality from "../../../data/reviewed/shizuoka-city/municipality.json";
import hamamatsuMunicipality from "../../../data/reviewed/hamamatsu-city/municipality.json";
import type { MetadataRoute } from "next";

import { correctionsHistory } from "@/lib/correctionsHistory";
import { loadPhase15CitySummaries } from "@/lib/phase15Cities";
import { phase15Progress } from "@/lib/phase15Progress";
import { loadPhase10RegionalDepthBySlug } from "@/lib/phase10RegionalDepth";
import { loadPhase9Catalog, loadPhase9Summary } from "@/lib/phase9Targets";
import { policyTargetPages } from "@/lib/policyTargets";
import { reviewedCoverageStats } from "@/lib/reviewedCoverage";

import aichiReviewManifest from "../../../data/catalog/aichi_policy_indicator_review_manifest.json";
import executiveSources from "../../../data/catalog/executive_sources.json";
import fukuokaActualLinkage from "../../../data/catalog/fukuoka_annual_actual_linkage.json";
import fukuokaAssemblySources from "../../../data/catalog/fukuoka_assembly_sources.json";
import fukuokaCityFinanceSources from "../../../data/catalog/fukuoka_city_finance_sources.json";
import fukuokaCityProjectSources from "../../../data/catalog/fukuoka_city_project_sources.json";
import fukuokaFinanceSources from "../../../data/catalog/fukuoka_finance_sources.json";
import fukuokaProjectLinkage from "../../../data/catalog/fukuoka_project_linkage.json";
import fukuokaProjectSources from "../../../data/catalog/fukuoka_project_sources.json";
import hiroshimaReviewManifest from "../../../data/catalog/hiroshima_revised_vision_indicator_review_manifest.json";
import hokkaidoActualLinkage from "../../../data/catalog/hokkaido_annual_actual_linkage.json";
import hokkaidoReviewManifest from "../../../data/catalog/hokkaido_policy_review_manifest.json";
import kagawaReviewManifest from "../../../data/catalog/kagawa_extended_plan_indicator_review_manifest.json";
import kitakyushuFinanceSources from "../../../data/catalog/kitakyushu_finance_sources.json";
import kitakyushuProjectSources from "../../../data/catalog/kitakyushu_project_sources.json";
import miyagiMoneyLinkage from "../../../data/catalog/miyagi_project_money_linkage.json";
import miyagiReviewManifest from "../../../data/catalog/miyagi_policy_review_manifest.json";
import officialSources from "../../../data/catalog/official_sources.json";
import okinawaReviewManifest from "../../../data/catalog/okinawa_midterm_indicator_review_manifest.json";
import osakaReviewManifest from "../../../data/catalog/osaka_beyond_expo_indicator_review_manifest.json";
import phase10Completion from "../../../data/catalog/phase10_completion.json";
import phase10ExecutionQueue from "../../../data/catalog/phase10_execution_queue.json";
import policySourcesCatalog from "../../../data/catalog/policy_sources.json";
import tokyoChildrenLinkage from "../../../data/catalog/tokyo_children_annual_actual_linkage.json";
import tokyoReviewManifest from "../../../data/catalog/tokyo_policy_target_review_manifest.json";
import sourceRequests from "../../../data/entities/executives/source_requests.json";

const siteUrl = "https://jimieru.com";
const staticRoutes = [
  "",
  "/about",
  "/assemblies",
  "/assemblies/fukuoka-prefecture/overseas-activities",
  "/compare",
  "/corrections",
  "/corrections/history",
  "/data-quality",
  "/executives",
  "/executives/source-requests",
  "/methodology",
  "/municipalities",
  "/municipalities/phase9",
  "/municipalities/phase10",
  "/municipalities/phase10/hokkaido-actuals",
  "/municipalities/phase10/tokyo-children-actuals",
  "/municipalities/phase10/miyagi-money",
  "/municipalities/phase10/fukuoka-actuals",
  "/municipalities/phase10/fukuoka-projects",
  "/municipalities/phase10/tohoku",
  "/municipalities/phase10/kanto",
  "/municipalities/phase10/chubu",
  "/municipalities/phase10/kinki",
  "/municipalities/phase10/chugoku",
  "/municipalities/phase10/shikoku",
  "/municipalities/phase10/kyushu",
  "/municipalities/hokkaido",
  "/municipalities/miyagi",
  "/municipalities/tokyo",
  "/municipalities/aichi",
  "/municipalities/osaka",
  "/municipalities/hiroshima",
  "/municipalities/kagawa",
  "/municipalities/okinawa",
  "/municipalities/kyoto-prefecture",
  "/municipalities/kyoto-city",
  "/municipalities/niigata-prefecture",
  "/municipalities/niigata-city",
  "/municipalities/okayama-prefecture",
  "/municipalities/okayama-city",
  "/municipalities/kumamoto-prefecture",
  "/municipalities/kumamoto-city",
  "/municipalities/hiroshima-prefecture",
  "/municipalities/hiroshima-city",
  "/municipalities/shizuoka-prefecture",
  "/municipalities/shizuoka-city",
  "/municipalities/hamamatsu-city",
  "/municipalities/fukuoka-prefecture",
  "/municipalities/fukuoka-city",
  "/municipalities/kitakyushu-city",
  "/policies",
  "/policy-sources",
  "/review-progress",
  "/sources",
];
const policyTargetRoutes = policyTargetPages.map(
  (page) => `/policies/fukuoka-prefecture/initiatives/${page.slug}`,
);
const phase9Summary = loadPhase9Summary();
const phase9Routes = phase9Summary.records.map((record) => record.route);
const phase15Cities = loadPhase15CitySummaries();
const phase15CityRoutes = phase15Cities.map((city) => `/municipalities/${city.slug}`);
const routes = [...staticRoutes, ...policyTargetRoutes, ...phase9Routes, ...phase15CityRoutes];

function latestOf(...dates: Array<string | null | undefined>): string {
  return dates
    .filter((date): date is string => typeof date === "string")
    .sort()
    .at(-1) as string;
}

// One lastmod rule for every route: the date is the newest content stamp
// carried by the repository data the page is rendered from — a completion
// record's completed_at, a review manifest's or source catalog's
// updated_at / reviewed_at, or the coverage freshness stamp for pages that
// aggregate the public datasets. No date is invented: the three static
// prose pages whose content has no data stamp (/about, /methodology,
// /corrections) omit lastModified rather than displaying an unverified
// or unchanging date.
const lastModifiedByRoute = new Map<string, string>();

// Phase 15 city pages carry their review completion date, and the two
// pages whose content is driven by the Phase 15 queue carry the queue's
// own updated_at stamp (the pre-existing rule, unchanged).
for (const city of phase15Cities) {
  lastModifiedByRoute.set(`/municipalities/${city.slug}`, city.completedAt);
}
lastModifiedByRoute.set("/municipalities/kyoto-prefecture", kyotoPrefectureMunicipality.last_verified_at);
lastModifiedByRoute.set("/municipalities/kyoto-city", kyotoCityMunicipality.last_verified_at);
lastModifiedByRoute.set("/municipalities/niigata-prefecture", niigataPrefectureMunicipality.last_verified_at);
lastModifiedByRoute.set("/municipalities/niigata-city", niigataCityMunicipality.last_verified_at);
lastModifiedByRoute.set("/municipalities/okayama-prefecture", okayamaPrefectureMunicipality.last_verified_at);
lastModifiedByRoute.set("/municipalities/okayama-city", okayamaCityMunicipality.last_verified_at);
lastModifiedByRoute.set("/municipalities/kumamoto-prefecture", kumamotoPrefectureMunicipality.last_verified_at);
lastModifiedByRoute.set("/municipalities/kumamoto-city", kumamotoCityMunicipality.last_verified_at);
lastModifiedByRoute.set("/municipalities/hiroshima-prefecture", hiroshimaPrefectureMunicipality.last_verified_at);
lastModifiedByRoute.set("/municipalities/hiroshima-city", hiroshimaCityMunicipality.last_verified_at);
lastModifiedByRoute.set("/municipalities/shizuoka-prefecture", shizuokaPrefectureMunicipality.last_verified_at);
lastModifiedByRoute.set("/municipalities/shizuoka-city", shizuokaCityMunicipality.last_verified_at);
lastModifiedByRoute.set("/municipalities/hamamatsu-city", hamamatsuMunicipality.last_verified_at);
lastModifiedByRoute.set("/municipalities", phase15Progress.updatedAt);
lastModifiedByRoute.set("/review-progress", phase15Progress.updatedAt);

// The homepage and the data-quality page render the reviewed-coverage
// aggregates, so they carry the same freshness stamp the site displays.
lastModifiedByRoute.set("", reviewedCoverageStats.updatedAt);
lastModifiedByRoute.set("/data-quality", reviewedCoverageStats.updatedAt);

// Phase 9: the summary stamp for the index, each prefecture catalog's own
// updated_at for its page.
lastModifiedByRoute.set("/municipalities/phase9", phase9Summary.updated_at);
for (const record of phase9Summary.records) {
  const catalog = loadPhase9Catalog(record.slug);
  if (catalog) {
    lastModifiedByRoute.set(record.route, catalog.updated_at);
  }
}

// Phase 10: the queue/completion stamps for the index, each linkage
// catalog's updated_at for the actuals pages, and each regional batch's
// updated_at for the regional pages.
lastModifiedByRoute.set(
  "/municipalities/phase10",
  latestOf(phase10ExecutionQueue.updated_at, phase10Completion.updated_at),
);
lastModifiedByRoute.set(
  "/municipalities/phase10/hokkaido-actuals",
  hokkaidoActualLinkage.updated_at,
);
lastModifiedByRoute.set(
  "/municipalities/phase10/tokyo-children-actuals",
  tokyoChildrenLinkage.updated_at,
);
lastModifiedByRoute.set("/municipalities/phase10/miyagi-money", miyagiMoneyLinkage.updated_at);
lastModifiedByRoute.set(
  "/municipalities/phase10/fukuoka-actuals",
  fukuokaActualLinkage.updated_at,
);
lastModifiedByRoute.set(
  "/municipalities/phase10/fukuoka-projects",
  fukuokaProjectLinkage.updated_at,
);
for (const region of ["tohoku", "kanto", "chubu", "kinki", "chugoku", "shikoku", "kyushu"]) {
  lastModifiedByRoute.set(
    `/municipalities/phase10/${region}`,
    loadPhase10RegionalDepthBySlug(region).updated_at,
  );
}

// Prefecture pages carry their policy review manifest's stamp, which is
// the newest stamp across the datasets each page renders.
const prefectureManifestDates: Record<string, string> = {
  "/municipalities/hokkaido": hokkaidoReviewManifest.updated_at,
  "/municipalities/miyagi": miyagiReviewManifest.updated_at,
  "/municipalities/tokyo": tokyoReviewManifest.updated_at,
  "/municipalities/aichi": aichiReviewManifest.updated_at,
  "/municipalities/osaka": osakaReviewManifest.updated_at,
  "/municipalities/hiroshima": hiroshimaReviewManifest.updated_at,
  "/municipalities/kagawa": kagawaReviewManifest.updated_at,
  "/municipalities/okinawa": okinawaReviewManifest.updated_at,
};
for (const [route, date] of Object.entries(prefectureManifestDates)) {
  lastModifiedByRoute.set(route, date);
}

// The three deep-dive municipality pages and the comparison page are
// rendered from the reviewed finance/project packages, whose source
// catalogs carry the registration stamp.
lastModifiedByRoute.set(
  "/municipalities/fukuoka-prefecture",
  latestOf(fukuokaFinanceSources.updated_at, fukuokaProjectSources.updated_at),
);
lastModifiedByRoute.set(
  "/municipalities/fukuoka-city",
  latestOf(fukuokaCityFinanceSources.updated_at, fukuokaCityProjectSources.updated_at),
);
lastModifiedByRoute.set(
  "/municipalities/kitakyushu-city",
  latestOf(kitakyushuFinanceSources.updated_at, kitakyushuProjectSources.updated_at),
);
lastModifiedByRoute.set(
  "/compare",
  latestOf(fukuokaCityFinanceSources.updated_at, kitakyushuFinanceSources.updated_at),
);

// Policy pages: each initiative catalog's reviewed_at, and the newest of
// the datasets the hub page aggregates.
for (const page of policyTargetPages) {
  lastModifiedByRoute.set(
    `/policies/fukuoka-prefecture/initiatives/${page.slug}`,
    page.catalog.reviewed_at,
  );
}
lastModifiedByRoute.set(
  "/policies",
  latestOf(
    ...policyTargetPages.map((page) => page.catalog.reviewed_at),
    hokkaidoReviewManifest.updated_at,
    miyagiReviewManifest.updated_at,
  ),
);
lastModifiedByRoute.set("/policy-sources", policySourcesCatalog.updated_at);

// Source and assembly catalogs.
lastModifiedByRoute.set(
  "/sources",
  latestOf(
    officialSources.updated_at,
    fukuokaFinanceSources.updated_at,
    fukuokaCityFinanceSources.updated_at,
    kitakyushuFinanceSources.updated_at,
    fukuokaAssemblySources.updated_at,
  ),
);
lastModifiedByRoute.set("/assemblies", fukuokaAssemblySources.updated_at);
lastModifiedByRoute.set(
  "/assemblies/fukuoka-prefecture/overseas-activities",
  fukuokaAssemblySources.updated_at,
);

// Executive pages: the executive source catalog's stamp, and the newest
// preparation date among the source requests the page lists.
lastModifiedByRoute.set("/executives", executiveSources.updated_at);
lastModifiedByRoute.set(
  "/executives/source-requests",
  latestOf(...sourceRequests.map((request) => request.prepared_at)),
);

// Corrections history carries its file's updated_at stamp.
lastModifiedByRoute.set("/corrections/history", correctionsHistory.updatedAt);

export const dynamic = "force-static";

export default function sitemap(): MetadataRoute.Sitemap {
  return routes.map((route) => ({
    // The homepage entry needs the trailing slash so it matches the
    // canonical root URL ("https://jimieru.com/") exactly.
    url: route === "" ? `${siteUrl}/` : `${siteUrl}${route}`,
    ...(lastModifiedByRoute.has(route)
      ? { lastModified: lastModifiedByRoute.get(route) }
      : {}),
    changeFrequency: route === "" ? "weekly" : "monthly",
    priority:
      route === ""
        ? 1
        : route === "/compare" ||
            route === "/executives" ||
            route === "/policies" ||
            route.startsWith("/policies/") ||
            route === "/policy-sources" ||
            route.startsWith("/municipalities/") ||
            route.startsWith("/assemblies/")
          ? 0.9
          : 0.8,
  }));
}
