import type { Metadata } from "next";
import { TohokuMunicipalityReview } from "@/components/TohokuMunicipalityReview";
import { canonicalFor } from "@/lib/pageMetadata";

export const metadata: Metadata = {
  title: "岩手県｜いわて県民計画（2019～2028）・財政・知事公約・県議会",
  description: "岩手県のいわて県民計画（2019～2028）、当初予算・決算・重点事業・知事公約・県議会のReviewed登録を確認します。",
  alternates: { canonical: canonicalFor("/municipalities/iwate-prefecture") },
};

export default function IwatePrefecturePage() {
  return <TohokuMunicipalityReview slug="iwate-prefecture" />;
}
