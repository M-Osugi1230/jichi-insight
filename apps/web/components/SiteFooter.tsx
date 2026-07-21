import Link from "next/link";

import { nationwideCoverageStats } from "@/lib/nationwideCoverage";

export function SiteFooter() {
  return (
    <footer className="siteFooter">
      <div className="footerMission">
        <p className="footerBrand">Jichi Insight</p>
        <p>住民が、自分自身で自治体、知事・市長、議会を評価できる情報環境をつくる。</p>
        <span>最終データ更新 {nationwideCoverageStats.updatedAt}</span>
      </div>
      <div className="footerNavGroup">
        <p>調べる</p>
        <Link href="/municipalities">全国から探す</Link>
        <Link href="/policies">政策と成果</Link>
        <Link href="/compare">予算・財政</Link>
        <Link href="/executives">首長</Link>
        <Link href="/assemblies">議会</Link>
      </div>
      <div className="footerNavGroup">
        <p>信頼のために</p>
        <Link href="/about">このサイトの目的</Link>
        <Link href="/methodology">読み方・評価方法</Link>
        <Link href="/data-quality">データ品質</Link>
        <Link href="/sources">公式資料</Link>
        <Link href="/corrections">訂正・反論</Link>
      </div>
      <div className="footerBottom">
        <span>Facts before scores.</span>
        <span>一次資料・更新日・未確認範囲を表示します。</span>
      </div>
    </footer>
  );
}
