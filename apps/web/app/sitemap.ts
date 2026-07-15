import type { MetadataRoute } from "next";

const siteUrl = "https://m-osugi1230.github.io/jichi-insight";
const routes = [
  "",
  "/about",
  "/corrections",
  "/data-quality",
  "/methodology",
  "/municipalities",
  "/municipalities/fukuoka-prefecture",
  "/municipalities/fukuoka-city",
  "/sources",
];

export const dynamic = "force-static";

export default function sitemap(): MetadataRoute.Sitemap {
  return routes.map((route) => ({
    url: `${siteUrl}${route}`,
    lastModified: new Date("2026-07-15"),
    changeFrequency: route === "" ? "weekly" : "monthly",
    priority: route === "" ? 1 : route.startsWith("/municipalities/") ? 0.9 : 0.8,
  }));
}
