import type { Metadata, Viewport } from "next";
import type { ReactNode } from "react";

import "./globals.css";

const siteUrl = "https://m-osugi1230.github.io/jichi-insight";

export const metadata: Metadata = {
  // metadataBase is the origin only, on purpose: Next.js prefixes
  // file-convention asset paths (icon, opengraph-image) with basePath
  // before resolving them against metadataBase, so a metadataBase that
  // already contains "/jichi-insight" would double the path segment in
  // the emitted og:image URL.
  metadataBase: new URL("https://m-osugi1230.github.io"),
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
  // own openGraph in app/page.tsx. Images come from app/opengraph-image.png.
  openGraph: {
    type: "website",
    locale: "ja_JP",
    url: siteUrl,
    siteName: "Jichi Insight",
  },
  twitter: {
    card: "summary_large_image",
  },
  robots: {
    index: true,
    follow: true,
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  colorScheme: "light",
  themeColor: "#102e46",
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="ja">
      <body>{children}</body>
    </html>
  );
}
