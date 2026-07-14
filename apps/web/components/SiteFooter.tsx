import Link from "next/link";

export function SiteFooter() {
  return (
    <footer className="siteFooter">
      <div>
        <p className="footerBrand">Jichi Insight</p>
        <p>約束・予算・実行・成果を、ひとつにつなぐ。</p>
      </div>
      <div className="footerLinks">
        <Link href="/about">このサイトの目的</Link>
        <Link href="/methodology">方法論</Link>
        <Link href="/sources">公式資料カタログ</Link>
        <Link href="/corrections">訂正・反論</Link>
      </div>
    </footer>
  );
}
