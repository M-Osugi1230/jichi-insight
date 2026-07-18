import type { MetadataRoute } from "next";

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
  "/municipalities/hokkaido",
  "/municipalities/miyagi",
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
const routes = [...staticRoutes, ...policyTargetRoutes];

export const dynamic = "force-static";

export default function sitemap(): MetadataRoute.Sitemap {
  return routes.map((route) => ({
    url: `${siteUrl}${route}`,
    lastModified: new Date("2026-07-18"),
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
