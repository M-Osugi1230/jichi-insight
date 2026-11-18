import type { Metadata } from "next";

/**
 * Shared metadata defaults for every page.
 *
 * The root layout declares the default Open Graph image from here, and page
 * templates that had no canonical URL declare theirs through canonicalFor,
 * so the site's public origin and social image exist in exactly one place.
 * Pages that already declare their own canonical or images keep them; these
 * helpers are only the fallback for pages that declare neither.
 */
export const siteUrl = "https://jimieru.com";

/**
 * The site-wide Open Graph image (app/opengraph-image.png, 1200x630).
 * Pages whose generateMetadata replaces the inherited Open Graph object
 * (the Phase 15 city template) must pass this explicitly, because the
 * file-convention image is not merged into a returned openGraph object.
 */
export const defaultOgImages: NonNullable<Metadata["openGraph"]>["images"] = [
  {
    url: `${siteUrl}/opengraph-image.png`,
    width: 1200,
    height: 630,
    type: "image/png",
  },
];

/**
 * Absolute canonical URL for a route path such as "/municipalities/hokkaido".
 * Canonical URLs on this site end with a trailing slash, matching the
 * trailingSlash build setting and the URLs the sitemap publishes.
 */
export function canonicalFor(path: string): string {
  return path === "" ? `${siteUrl}/` : `${siteUrl}${path}/`;
}
