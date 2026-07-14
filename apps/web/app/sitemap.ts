import type { MetadataRoute } from "next";

const siteUrl = "https://m-osugi1230.github.io/jichi-insight";
const routes = ["", "/about", "/methodology", "/municipalities", "/sources"];

export default function sitemap(): MetadataRoute.Sitemap {
  return routes.map((route) => ({
    url: `${siteUrl}${route}`,
    lastModified: new Date("2026-07-15"),
    changeFrequency: route === "" ? "weekly" : "monthly",
    priority: route === "" ? 1 : 0.8,
  }));
}
