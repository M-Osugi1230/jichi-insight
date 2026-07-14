import type { MetadataRoute } from "next";

const siteUrl = "https://m-osugi1230.github.io/jichi-insight";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: "*",
      allow: "/",
    },
    sitemap: `${siteUrl}/sitemap.xml`,
  };
}
