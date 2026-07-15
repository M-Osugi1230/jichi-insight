import type { MetadataRoute } from "next";

const siteUrl = "https://m-osugi1230.github.io/jichi-insight";
const routes = [
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
  "/municipalities/fukuoka-prefecture",
  "/municipalities/fukuoka-city",
  "/municipalities/kitakyushu-city",
  "/policies",
  "/policies/fukuoka-prefecture/initiatives/01",
  "/policies/fukuoka-prefecture/initiatives/02",
  "/policies/fukuoka-prefecture/initiatives/03",
  "/policies/fukuoka-prefecture/initiatives/04",
  "/policies/fukuoka-prefecture/initiatives/05",
  "/policies/fukuoka-prefecture/initiatives/06",
  "/policies/fukuoka-prefecture/initiatives/07",
  "/policies/fukuoka-prefecture/initiatives/08",
  "/policies/fukuoka-prefecture/initiatives/09",
  "/policies/fukuoka-prefecture/initiatives/10",
  "/policy-sources",
  "/sources",
];

export const dynamic = "force-static";

export default function sitemap(): MetadataRoute.Sitemap {
  return routes.map((route) => ({
    url: `${siteUrl}${route}`,
    lastModified: new Date("2026-07-16"),
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
