"use client";

import Link from "next/link";

import "./globals.css";
import styles from "./not-found.module.css";

export default function GlobalError({
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <html lang="ja">
      <body>
        <main>
          <section className={styles.errorPage}>
            <p className="eyebrow">Error / 表示エラー</p>
            <h1>ページを表示できませんでした。</h1>
            <p>
              一時的な問題が発生し、このページの内容を表示できませんでした。
              問題の詳細は表示していません。再度お試しいただくか、時間をおいてアクセスしてください。
            </p>
            <div className="heroActions">
              <button
                className={`primaryAction ${styles.retryButton}`}
                onClick={reset}
                type="button"
              >
                もう一度試す
              </button>
              <Link className="secondaryAction" href="/">
                ホームへ戻る
              </Link>
            </div>
          </section>
        </main>
      </body>
    </html>
  );
}
