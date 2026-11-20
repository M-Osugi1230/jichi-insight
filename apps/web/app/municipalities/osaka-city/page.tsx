import type { Metadata } from "next";

import { OsakaClusterCityPage } from "@/components/OsakaClusterCityPage";
import { canonicalFor } from "@/lib/pageMetadata";

export const metadata: Metadata = {
  title: "大阪市｜財政・重点事業・市長公約の一次資料レビュー",
  description: "大阪市のReviewed財政・重点事業・市長の現任期と公約の登録範囲を一次資料に基づいて公開します。",
  alternates: { canonical: canonicalFor("/municipalities/osaka-city") },
};

export default function Page() {
  return <OsakaClusterCityPage slug="osaka-city" />;
}
