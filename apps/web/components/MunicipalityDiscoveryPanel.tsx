import Link from "next/link";

import { municipalityDiscoveryAvailability } from "@/lib/municipalityDiscovery";

import styles from "./MunicipalityDiscoveryPanel.module.css";

type Props = {
  officialCode: string;
  /** Section IDs on this page; no disabled or fake anchors are created. */
  planHref: string;
  budgetHref: string;
  settlementHref?: string;
  fiscalDetailHref?: string;
  /** Link directly to a registered project list or section when available. */
  projectHref?: string;
};

export function MunicipalityDiscoveryPanel({
  officialCode,
  planHref,
  budgetHref,
  settlementHref,
  fiscalDetailHref,
  projectHref,
}: Props) {
  const available = municipalityDiscoveryAvailability(officialCode);
  const items = [
    {
      label: "財政の詳細（3年推移・財政指標）",
      enabled: available.finance && Boolean(fiscalDetailHref),
      href: fiscalDetailHref,
    },
    {
      label: "首長の公約",
      enabled: available.promises,
      href: available.key ? `/promises#${available.key}` : undefined,
    },
    {
      label: "議会（議案・表決・政務活動費・視察）",
      enabled: available.assembly,
      href: available.key ? `/assemblies/${available.key}` : undefined,
    },
    {
      label: "重点事業",
      enabled: available.projects,
      href: projectHref ?? "/projects",
    },
  ];

  return (
    <section className={styles.panel} aria-labelledby="municipality-discovery-title">
      <h2 id="municipality-discovery-title">この自治体で調べられること</h2>
      <p className={styles.note}>
        公約・議会の深掘りは、その自治体の Reviewed レコードが登録されている場合に限って案内します。重点事業も Reviewed 事業の登録と自治体コードの一致を確認した場合に限って案内します。
        「対象外」は本サイトの深掘り対象外を意味します。
      </p>
      <ul className={styles.list}>
        <li className={styles.item}>
          <span className={styles.label}>計画・予算・決算</span>
          <span className={styles.links}>
            <Link href={planHref}>計画・概要を見る</Link>
            <Link href={budgetHref}>予算・決算を見る</Link>
            {settlementHref && settlementHref !== budgetHref ? (
              <Link href={settlementHref}>決算の詳細を見る</Link>
            ) : null}
          </span>
        </li>
        {items.map((item) => (
          <li className={styles.item} key={item.label}>
            <span className={styles.label}>{item.label}</span>
            {item.enabled && item.href ? (
              <Link href={item.href}>{item.label}を見る</Link>
            ) : (
              <span className={styles.unavailable}>対象外</span>
            )}
          </li>
        ))}
      </ul>
    </section>
  );
}
