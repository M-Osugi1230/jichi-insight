import type { Metadata, Viewport } from "next";
import type { ReactNode } from "react";

import { defaultOgImages, siteUrl } from "@/lib/pageMetadata";

import "./globals.css";

export const metadata: Metadata = {
  // metadataBase is the origin only, on purpose: Next.js prefixes
  // file-convention asset paths (icon, opengraph-image) with basePath
  // before resolving them against metadataBase, so a metadataBase that
  // already contains a path would double the path segment in
  // the emitted og:image URL.
  metadataBase: new URL("https://jimieru.com"),
  title: {
    default: "Jichi Insight | 自治体インサイト",
    template: "%s | Jichi Insight",
  },
  description:
    "住民が自治体を自分で評価できるよう、政策計画・予算・事業・年度実績・議会を一次資料からつなぐ公共データ基盤。",
  applicationName: "Jichi Insight",
  manifest: `${siteUrl}/manifest.webmanifest`,
  // og:title / og:description are intentionally NOT set here: Next.js falls
  // back to each page's own title/description, so shared links preview with
  // the page's content instead of this generic copy. The homepage sets its
  // own openGraph in app/page.tsx. The default image is declared here (and
  // in lib/pageMetadata) so pages that declare no image of their own share
  // the site image; templates whose generateMetadata replaces the inherited
  // openGraph object pass the same default explicitly.
  openGraph: {
    type: "website",
    locale: "ja_JP",
    url: siteUrl,
    siteName: "Jichi Insight",
    images: defaultOgImages,
  },
  twitter: {
    card: "summary_large_image",
  },
  robots: {
    index: true,
    follow: true,
  },
  // Google Search Console ownership verification (token issued for the
  // pre-migration URL-prefix property on the old github.io URL; the
  // jimieru.com domain property is verified separately via DNS).
  // Rendered as the google-site-verification meta tag in every page's
  // <head>.
  verification: {
    google: "y5HZtY4bPWD9Jj8-sXA48x0v61gP1xpOAqWxfQuvY48",
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  colorScheme: "light",
  themeColor: "#102e46",
};

// Minimal WebSite structured data so search engines can identify the site
// itself (name, canonical URL, purpose). Static JSON-LD only: no external
// script, no analytics or tracking payload.
const websiteJsonLd = {
  "@context": "https://schema.org",
  "@type": "WebSite",
  name: "Jichi Insight",
  alternateName: "自治体インサイト",
  url: `${siteUrl}/`,
  inLanguage: "ja",
  description:
    "住民が自治体を自分で評価できるよう、政策計画・予算・事業・年度実績・議会を一次資料からつなぐ公共データ基盤。",
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="ja">
      <body>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(websiteJsonLd) }}
        />
        {children}
      </body>
    </html>
  );
}
