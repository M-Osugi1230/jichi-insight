import type { MetadataRoute } from "next";

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
  "/data-quality",
  "/executives",
  "/executives/source-requests",
  "/methodology",
  "/municipalities",
  "/municipalities/phase9",
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
  "/sources",
];
const policyTargetRoutes = policyTargetPages.map(
  (page) => `/policies/fukuoka-prefecture/initiatives/${page.slug}`,
);
const phase9Routes = loadPhase9Summary().records.map((record) => record.route);
const routes = [...staticRoutes, ...policyTargetRoutes, ...phase9Routes];

export const dynamic = "force-static";

export default function sitemap(): MetadataRoute.Sitemap {
  return routes.map((route) => ({
    url: `${siteUrl}${route}`,
    lastModified: new Date("2026-07-22"),
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
