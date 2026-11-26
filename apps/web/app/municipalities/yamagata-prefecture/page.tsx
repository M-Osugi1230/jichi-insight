import type { Metadata } from "next";
import { TohokuMunicipalityReview } from "@/components/TohokuMunicipalityReview";
import { canonicalFor } from "@/lib/pageMetadata";

export const metadata: Metadata = {
  title: "山形県｜第4次山形県総合発展計画・財政・知事公約・県議会",
  description: "山形県の第4次山形県総合発展計画、2026年度予算、普通会計決算、重点事業、知事公約、県議会の一次資料を確認します。",
  alternates: { canonical: canonicalFor("/municipalities/yamagata-prefecture") },
};

export default function YamagataPrefecturePage() {
  return <TohokuMunicipalityReview slug="yamagata-prefecture" />;
}
