import Link from "next/link";

const primaryNavigation = [
  { href: "/municipalities", label: "自治体" },
  { href: "/policies", label: "政策" },
  { href: "/compare", label: "財政比較" },
  { href: "/executives", label: "首長" },
  { href: "/assemblies", label: "議会" },
];

const evidenceNavigation = [
  { href: "/policy-sources", label: "政策資料" },
  { href: "/sources", label: "公式資料" },
  { href: "/data-quality", label: "データ品質" },
  { href: "/methodology", label: "評価方法" },
  { href: "/corrections", label: "訂正・反論" },
];

export function SiteHeader() {
  return (
    <header className="siteHeader">
      <Link className="brand" href="/" aria-label="Jichi Insight ホーム">
        Jichi Insight
      </Link>
      <nav className="desktopNav" aria-label="主要ナビゲーション">
        {primaryNavigation.map((item) => (
          <Link href={item.href} key={item.href}>
            {item.label}
          </Link>
        ))}
        <details className="navMore">
          <summary>根拠・運営</summary>
          <div className="navMorePanel">
            {evidenceNavigation.map((item) => (
              <Link href={item.href} key={item.href}>
                {item.label}
              </Link>
            ))}
          </div>
        </details>
      </nav>
      <details className="mobileNav">
        <summary aria-label="ナビゲーションを開く">メニュー</summary>
        <nav aria-label="モバイルナビゲーション">
          <p>調べる</p>
          {primaryNavigation.map((item) => (
            <Link href={item.href} key={item.href}>
              {item.label}
            </Link>
          ))}
          <p>根拠・運営</p>
          {evidenceNavigation.map((item) => (
            <Link href={item.href} key={item.href}>
              {item.label}
            </Link>
          ))}
        </nav>
      </details>
    </header>
  );
}
