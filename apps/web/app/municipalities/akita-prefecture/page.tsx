import type { Metadata } from "next";
import { TohokuMunicipalityReview } from "@/components/TohokuMunicipalityReview";
import { canonicalFor } from "@/lib/pageMetadata";

export const metadata: Metadata = {
  title: "秋田県｜秋田県総合計画 ～秋田再興への第一歩～・財政・知事公約・県議会",
  description: "秋田県の秋田県総合計画 ～秋田再興への第一歩～、2026年度予算、普通会計決算、重点事業、知事公約、県議会の一次資料を確認します。",
  alternates: { canonical: canonicalFor("/municipalities/akita-prefecture") },
};

export default function AkitaPrefecturePage() {
  return <TohokuMunicipalityReview slug="akita-prefecture" />;
}
