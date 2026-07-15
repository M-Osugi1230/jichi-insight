import type { Metadata } from "next";
import { PolicyTargetDetail } from "@/components/PolicyTargetDetail";
import { policyTargetPage } from "@/lib/policyTargets";

export const metadata: Metadata = {
  title: "安全で安心して暮らせる地域づくり｜数値目標",
  description: "福岡県総合計画の取組20に設定された7つの固有数値目標を、犯罪、飲酒運転、交通事故、消費者安全、食品監視、再掲範囲、実績未接続状態とともに確認できます。",
};

export default function Initiative20Page() {
  return <PolicyTargetDetail definition={policyTargetPage("20")} />;
}
