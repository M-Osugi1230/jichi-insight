import type { Metadata } from "next";
import type { ReactNode } from "react";

import "./globals.css";

export const metadata: Metadata = {
  title: "Jichi Insight | 自治体インサイト",
  description:
    "自治体の約束・予算・実行・成果を、一次資料に基づいてつなぐ自治体IR基盤。",
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="ja">
      <body>{children}</body>
    </html>
  );
}
