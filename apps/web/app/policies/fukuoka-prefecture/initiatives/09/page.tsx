import type { Metadata } from "next";

import { PolicyTargetDetail } from "@/components/PolicyTargetDetail";
import { policyTargetPage } from "@/lib/policyTargets";

export const metadata: Metadata = {
  title: "農林水産業の振興｜数値目標",
  description:
    "福岡県総合計画の取組9に設定された6つの固有数値目標を、生産、販売、人材、ワンヘルス、GAPの基準値と目標値、再掲範囲、実績未接続状態とともに確認できます。",
};

export default function Initiative09Page() {
  return <PolicyTargetDetail definition={policyTargetPage("09")} />;
}
