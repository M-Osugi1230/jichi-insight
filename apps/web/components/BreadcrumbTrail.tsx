import Link from "next/link";
import { canonicalFor } from "@/lib/pageMetadata";
import styles from "./BreadcrumbTrail.module.css";

export type BreadcrumbItem = {
  /** Human-readable name must be identical in the visible trail and JSON-LD. */
  name: string;
  /** A public, canonical route, starting with '/'. */
  href: string;
};

/**
 * Server-rendered, visible navigation and matching BreadcrumbList data.
 * Do not include a page in structured data unless it is also a visible crumb.
 * No client runtime, external SDK or tracking is needed.
 */
export function BreadcrumbTrail({ items }: { items: readonly BreadcrumbItem[] }) {
  const crumbs = items.filter((item) => item.href.startsWith("/") && item.name.trim());
  if (crumbs.length < 2) return null;

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: crumbs.map((item, index) => ({
      "@type": "ListItem",
      position: index + 1,
      name: item.name,
      item: canonicalFor(item.href === "/" ? "" : item.href.replace(/\/$/, "")),
    })),
  };

  return (
    <>
      <nav className={styles.trail} aria-label="パンくずリスト">
        <ol>
          {crumbs.map((item, index) => (
            <li key={item.href}>
              {index === crumbs.length - 1 ? (
                <span aria-current="page">{item.name}</span>
              ) : (
                <Link href={item.href}>{item.name}</Link>
              )}
            </li>
          ))}
        </ol>
      </nav>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(jsonLd).replace(/</g, "\\u003c"),
        }}
      />
    </>
  );
}
