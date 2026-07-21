import Link from "next/link";

import { nationwideCoverageStats } from "@/lib/nationwideCoverage";

const primaryNavigation = [
  { href: "/municipalities", label: "全国から探す" },
  { href: "/policies", label: "政策と成果" },
  { href: "/compare", label: "予算・財政" },
  { href: "/executives", label: "首長" },
  { href: "/assemblies", label: "議会" },
];

const evidenceNavigation = [
  { href: "/about", label: "このサイトの目的" },
  { href: "/data-quality", label: "データ品質" },
  { href: "/methodology", label: "読み方・評価方法" },
  { href: "/policy-sources", label: "政策資料" },
  { href: "/sources", label: "公式資料" },
  { href: "/corrections", label: "訂正・反論" },
];

export function SiteHeader() {
  return (
    <>
      <div className="dataPulse" role="status">
        <div>
          <span className="dataPulseDot" aria-hidden="true" />
          <span className="dataPulseLabel">DATA UPDATE</span>
          <span>{nationwideCoverageStats.updatedAt}</span>
          <span className="dataPulseDivider" aria-hidden="true" />
          <span>全国 {nationwideCoverageStats.currentPlanConfirmedPrefectures}/47 の現行計画を確認</span>
        </div>
      </div>
      <header className="siteHeader">
        <Link className="brand" href="/" aria-label="Jichi Insight ホーム">
          <span className="brandMark" aria-hidden="true">JI</span>
          <span className="brandText">
            <strong>Jichi Insight</strong>
            <small>自治体を、自分で確かめる。</small>
          </span>
        </Link>
        <nav className="desktopNav" aria-label="主要ナビゲーション">
          {primaryNavigation.map((item) => (
            <Link href={item.href} key={item.href}>{item.label}</Link>
          ))}
          <details className="navMore">
            <summary>根拠・運営</summary>
            <div className="navMorePanel">
              {evidenceNavigation.map((item) => (
                <Link href={item.href} key={item.href}>{item.label}</Link>
              ))}
            </div>
          </details>
        </nav>
        <details className="mobileNav">
          <summary aria-label="ナビゲーションを開く"><span>メニュー</span></summary>
          <nav aria-label="モバイルナビゲーション">
            <p>調べる</p>
            {primaryNavigation.map((item) => (
              <Link href={item.href} key={item.href}>{item.label}</Link>
            ))}
            <p>根拠と運営</p>
            {evidenceNavigation.map((item) => (
              <Link href={item.href} key={item.href}>{item.label}</Link>
            ))}
          </nav>
        </details>
      </header>
    </>
  );
}
