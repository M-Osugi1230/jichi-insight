import Link from "next/link";

const navigation = [
  { href: "/municipalities", label: "自治体" },
  { href: "/compare", label: "都市比較" },
  { href: "/sources", label: "公式資料" },
  { href: "/data-quality", label: "データ品質" },
  { href: "/methodology", label: "評価方法" },
  { href: "/about", label: "目的" },
];

export function SiteHeader() {
  return (
    <header className="siteHeader">
      <Link className="brand" href="/" aria-label="Jichi Insight ホーム">
        Jichi Insight
      </Link>
      <nav aria-label="主要ナビゲーション">
        {navigation.map((item) => (
          <Link href={item.href} key={item.href}>
            {item.label}
          </Link>
        ))}
      </nav>
    </header>
  );
}
