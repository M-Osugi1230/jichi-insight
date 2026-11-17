import type { Metadata } from "next";

import { PolicyTargetDetail } from "@/components/PolicyTargetDetail";
import { canonicalFor } from "@/lib/pageMetadata";
import { policyTargetPage } from "@/lib/policyTargets";

export const metadata: Metadata = {
  alternates: {
    canonical: canonicalFor("/policies/fukuoka-prefecture/initiatives/25"),
  },
  title: "県内各地域の振興｜数値目標",
  description:
    "福岡県総合計画の取組25に設定された道路、無電柱化、駅、舟運、港湾の6指標を確認できます。",
};

export default function Initiative25Page() {
  return <PolicyTargetDetail definition={policyTargetPage("25")} />;
}
