import type { Metadata } from "next";
import { TohokuMunicipalityReview } from "@/components/TohokuMunicipalityReview";
import { canonicalFor } from "@/lib/pageMetadata";

export const metadata: Metadata = {
  title: "福島県｜福島県総合計画・財政・知事公約・県議会",
  description: "福島県の福島県総合計画、2026年度予算、普通会計決算、重点事業、知事公約、県議会の一次資料を確認します。",
  alternates: { canonical: canonicalFor("/municipalities/fukushima-prefecture") },
};

export default function FukushimaPrefecturePage() {
  return <TohokuMunicipalityReview slug="fukushima-prefecture" />;
}
