import type { MetadataRoute } from "next";

const basePath = process.env.NEXT_PUBLIC_BASE_PATH ?? "";

export const dynamic = "force-static";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "Jichi Insight | 自治体インサイト",
    short_name: "Jichi Insight",
    description:
      "自治体の政策目標・予算・実行・成果を、住民が一次資料から確かめるための公共データ基盤。",
    start_url: `${basePath}/`,
    scope: `${basePath}/`,
    display: "standalone",
    background_color: "#f5f3ed",
    theme_color: "#102e46",
    lang: "ja",
  };
}
