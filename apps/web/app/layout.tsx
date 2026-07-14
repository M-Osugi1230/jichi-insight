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
    "自治体の約束・予算・実行・成果を、一次資料に基づいてつなぐ自治体IR・行政アカウンタビリティ基盤。",
  applicationName: "Jichi Insight",
  manifest: `${siteUrl}/manifest.webmanifest`,
  openGraph: {
    type: "website",
    locale: "ja_JP",
    url: siteUrl,
    siteName: "Jichi Insight",
    title: "Jichi Insight | 自治体インサイト",
    description:
      "約束・予算・実行・成果を、一次資料に基づいてひとつにつなぐ。",
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
  themeColor: "#173f35",
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="ja">
      <body>{children}</body>
    </html>
  );
}
