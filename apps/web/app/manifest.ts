import type { MetadataRoute } from "next";

const basePath = process.env.NEXT_PUBLIC_BASE_PATH ?? "";

export const dynamic = "force-static";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "Jichi Insight | 自治体インサイト",
    short_name: "Jichi Insight",
    description:
      "自治体の約束・予算・実行・成果を、一次資料に基づいてつなぐ自治体IR基盤。",
    start_url: `${basePath}/`,
    scope: `${basePath}/`,
    display: "standalone",
    background_color: "#f4f3ee",
    theme_color: "#173f35",
    lang: "ja",
  };
}
