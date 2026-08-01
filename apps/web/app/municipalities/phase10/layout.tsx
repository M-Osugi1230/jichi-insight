import Link from "next/link";
import type { ReactNode } from "react";

import styles from "./layout.module.css";

export default function Phase10Layout({ children }: { children: ReactNode }) {
  return (
    <>
      <nav className={styles.phaseNav} aria-label="Phase 10地域進捗">
        <div>
          <span>PHASE 10</span>
          <Link href="/municipalities/phase10">全国深度マトリクス</Link>
          <Link href="/municipalities/phase10/tohoku">東北5県</Link>
          <Link href="/municipalities/phase10/kanto">関東6県</Link>
          <Link href="/municipalities/phase10/chubu">中部8県</Link>
          <Link href="/municipalities/phase10/kinki">近畿6府県</Link>
          <Link href="/municipalities/phase10/chugoku">中国4県</Link>
          <Link href="/municipalities/phase10/shikoku">四国3県</Link>
          <Link href="/municipalities/phase10/kyushu">九州6県</Link>
        </div>
      </nav>
      {children}
    </>
  );
}
