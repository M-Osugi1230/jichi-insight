import type { MetadataRoute } from "next";

import { loadPhase15CitySummaries } from "@/lib/phase15Cities";
import { phase15Progress } from "@/lib/phase15Progress";
import { loadPhase9Summary } from "@/lib/phase9Targets";
import { policyTargetPages } from "@/lib/policyTargets";

const siteUrl = "https://m-osugi1230.github.io/jichi-insight";
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
const phase9Routes = loadPhase9Summary().records.map((record) => record.route);
const phase15Cities = loadPhase15CitySummaries();
const phase15CityRoutes = phase15Cities.map((city) => `/municipalities/${city.slug}`);
const routes = [...staticRoutes, ...policyTargetRoutes, ...phase9Routes, ...phase15CityRoutes];

// lastModified is emitted only where a canonical, verifiable content date
// exists in the repository data: each Phase 15 city page carries its review
// completion date (completed_at in its completion record), and the two pages
// whose content is driven by the Phase 15 queue carry the queue's own
// updated_at stamp. Routes without such a date omit lastModified rather
// than displaying an unverified or unchanging date.
const lastModifiedByRoute = new Map<string, string>(
  phase15Cities.map((city) => [`/municipalities/${city.slug}`, city.completedAt]),
);
lastModifiedByRoute.set("/municipalities", phase15Progress.updatedAt);
lastModifiedByRoute.set("/review-progress", phase15Progress.updatedAt);

export const dynamic = "force-static";

export default function sitemap(): MetadataRoute.Sitemap {
  return routes.map((route) => ({
    // The homepage entry needs the trailing slash: the Search Console
    // URL-prefix property is "https://m-osugi1230.github.io/jichi-insight/"
    // and the bare ".../jichi-insight" URL falls outside that prefix.
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
