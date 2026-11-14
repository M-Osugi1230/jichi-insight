import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";

import styles from "./not-found.module.css";

export default function Loading() {
  return (
    <main>
      <SiteHeader />
      <section className={styles.errorPage}>
        <p aria-live="polite" role="status">
          ページを読み込んでいます。しばらくお待ちください。
        </p>
      </section>
      <SiteFooter />
    </main>
  );
}
