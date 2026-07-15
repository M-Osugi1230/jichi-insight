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
  "/policy-sources",
  "/sources",
];

export const dynamic = "force-static";

export default function sitemap(): MetadataRoute.Sitemap {
  return routes.map((route) => ({
    url: `${siteUrl}${route}`,
    lastModified: new Date("2026-07-15"),
    changeFrequency: route === "" ? "weekly" : "monthly",
    priority:
      route === ""
        ? 1
        : route === "/compare" ||
            route === "/executives" ||
            route === "/policies" ||
            route === "/policy-sources" ||
            route.startsWith("/municipalities/") ||
            route.startsWith("/assemblies/")
          ? 0.9
          : 0.8,
  }));
}
