import Link from "next/link";

import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";

import styles from "./not-found.module.css";

export default function NotFound() {
  return (
    <main>
      <SiteHeader />
      <section className={styles.errorPage}>
        <p className="eyebrow">404 / Not found</p>
        <h1>お探しのページは見つかりませんでした。</h1>
        <p>
          ページが移動したか、まだ公開されていない可能性があります。
          不明な情報を存在するように見せないため、準備中のページは公開していません。
        </p>
        <div className="heroActions">
          <Link className="primaryAction" href="/">
            ホームへ戻る
          </Link>
          <Link className="secondaryAction" href="/sources">
            公式資料を見る
          </Link>
        </div>
      </section>
      <SiteFooter />
    </main>
  );
}
