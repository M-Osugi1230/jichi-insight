import type { Metadata } from "next";

import { PolicyTargetDetail } from "@/components/PolicyTargetDetail";
import { canonicalFor } from "@/lib/pageMetadata";
import { policyTargetPage } from "@/lib/policyTargets";

export const metadata: Metadata = {
  alternates: {
    canonical: canonicalFor("/policies/fukuoka-prefecture/initiatives/24"),
  },
  title: "地域の活力向上｜数値目標",
  description:
    "福岡県総合計画の取組24に設定された移住支援事業とサテライトオフィスの2指標を確認できます。",
};

export default function Initiative24Page() {
  return <PolicyTargetDetail definition={policyTargetPage("24")} />;
}
