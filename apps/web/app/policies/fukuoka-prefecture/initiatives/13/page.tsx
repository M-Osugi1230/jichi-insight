import type { Metadata } from "next";

import { PolicyTargetDetail } from "@/components/PolicyTargetDetail";
import { policyTargetPage } from "@/lib/policyTargets";

export const metadata: Metadata = {
  title: "出会い・結婚・出産・子育て支援｜数値目標",
  description:
    "福岡県総合計画の取組13に設定された成婚者数の数値目標を、基準値、目標値、期間、実績未接続状態とともに確認できます。",
};

export default function Initiative13Page() {
  return <PolicyTargetDetail definition={policyTargetPage("13")} />;
}
