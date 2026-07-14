import type { ReactNode } from "react";

type PageIntroProps = {
  eyebrow: string;
  title: string;
  children: ReactNode;
};

export function PageIntro({ eyebrow, title, children }: PageIntroProps) {
  return (
    <section className="pageIntro">
      <p className="eyebrow">{eyebrow}</p>
      <h1>{title}</h1>
      <div className="pageIntroText">{children}</div>
    </section>
  );
}
