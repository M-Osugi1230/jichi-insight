import type { Metadata, Viewport } from "next";
import type { ReactNode } from "react";

import "./globals.css";

const siteUrl = "https://m-osugi1230.github.io/jichi-insight";

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: "Jichi Insight | 自治体インサイト",
    template: "%s | Jichi Insight",
  },
  description:
    "住民が自治体を自分で評価できるよう、政策計画・予算・事業・年度実績・議会を一次資料からつなぐ公共データ基盤。",
  applicationName: "Jichi Insight",
  manifest: `${siteUrl}/manifest.webmanifest`,
  openGraph: {
    type: "website",
    locale: "ja_JP",
    url: siteUrl,
    siteName: "Jichi Insight",
    title: "Jichi Insight | 自治体インサイト",
    description:
      "自治体を、自分で確かめる。政策目標・予算・実行・成果を一次資料からつなぎます。",
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
