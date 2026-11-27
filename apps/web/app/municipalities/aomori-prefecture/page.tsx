import type { Metadata } from "next";
import { TohokuMunicipalityReview } from "@/components/TohokuMunicipalityReview";
import { canonicalFor } from "@/lib/pageMetadata";

export const metadata: Metadata = {
  title: "青森県｜青森県基本計画「青森新時代」への架け橋・財政・知事公約・県議会",
  description: "青森県の青森県基本計画「青森新時代」への架け橋、当初予算・決算・重点事業・知事公約・県議会のReviewed登録を確認します。",
  alternates: { canonical: canonicalFor("/municipalities/aomori-prefecture") },
};

export default function AomoriPrefecturePage() {
  return <TohokuMunicipalityReview slug="aomori-prefecture" />;
}
