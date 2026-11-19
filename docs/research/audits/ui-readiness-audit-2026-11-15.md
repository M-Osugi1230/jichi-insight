# Jichi Insight UI readiness / discoverability audit — 2026-11-15

- Target: live production site https://m-osugi1230.github.io/jichi-insight/ (checked 2026-11-15, after the formal release switch PR #494)
- Method: live HTML fetched for 15 page types (home, municipalities index, a prefecture page, a phase9 page, review-progress, methodology, about, sources, data-quality, compare, executives, assemblies, policies, corrections/history, 404) + static analysis of the repo (`apps/web`). No real-device rendering, no lab performance measurement, no human comprehension test — those remain unperformed (see Larger Work #4). Asset sizes are byte counts of the actual served files (raw and gzip as served by GitHub Pages).
- Constraint observed: audit only, no code or repo files were changed.

## Executive summary

The site's content model and transparency machinery are strong: the hero states the purpose plainly, evidence links to official sources work, the corrections flow is real and tested, and trust pages are one click away. The gaps are concentrated in three places:

1. **Sharing/SEO basics are unfinished** — no `og:image`, no canonical, no structured data anywhere; every shared link previews with the same generic title; three trust pages (about / methodology / sources) have no page-specific title or description at all.
2. **The newest reviewed work is not on the website** — the 9 Phase 15 reviewed cities （函館・旭川・青森・八戸・盛岡・秋田・山形・福島・郡山） have no web pages; from the review-progress list their only link leads to a raw JSON file on GitHub. A resident who finds their city cannot read anything.
3. **First-visit comprehension risk is vocabulary, not layout** — the homepage is long and dense with project jargon (Evidence Packet, Phase 10, v1, 要確認 / 評価不能）, and the 3-minute first-time-user test has never been run.

---

## 1. First-visit experience

**What works**
- Hero (homepage, first screen): eyebrow "PUBLIC EVIDENCE FOR LOCAL GOVERNMENT", H1 「自治体を、根拠から読む。」, one-sentence explanation （計画、予算、事業、成果、議会。ばらばらに公開された一次資料を、住民が自分で判断できる順序へつなぎ直します), status badge 「正式公開中」, and three CTAs: 「47都道府県から探す」 / 「このサイトの目的」 / 「67自治体のレビュー進捗」. Trust badges under the CTAs: 一次資料を表示 / 未確認を明記 / 単純ランキングなし.
- The Promise→Money→Action→Result→Accountability chain is explained mid-page in plain Japanese with numbered steps （何を目指すか / いくら使うか / 何をしたか / 何が変わったか / どう説明したか）.
- Click path home → municipality → evidence works: home CTA → `/municipalities/` (search box + prefecture cards) → e.g. `/municipalities/hokkaido/` → 109 outbound links to official prefectural source documents (PDFs on pref.hokkaido.lg.jp).
- Navigation labels are concrete Japanese （全国から探す / 政策と成果 / 予算・財政 / 首長 / 議会 / 根拠・運営）, duplicated consistently in header, mobile menu, and footer.

**Problems**
- **Length and jargon density.** The homepage carries ~300 lines of visible text: stats blocks, entry cards for 宮城県・福岡県・Phase 10, the five-question chain, a three-tier coverage explanation, and a "Facts before scores" section. Terms a first-time resident has never seen — "Evidence Packet", "Reviewed", "Phase 9/10/15", "v1基盤", "文書スコープ", "要確認", "評価不能", "接続" — appear without glosses on the homepage itself (definitions live on /methodology and /data-quality). This is exactly what the never-performed 3-minute comprehension test was designed to catch.
- **The header freshness signal looks stale.** Every page's top bar reads "DATA UPDATE 2026-08-01" (from `reviewedCoverageStats.updatedAt`, the coverage dataset's stamp, rendered in `components/SiteHeader.tsx`). The review-progress page's canonical queue was updated 2026-11-15 and the site formally launched 2026-11-15, but the most prominent date on every page is from August — a first-time visitor can reasonably conclude the site has not been updated in 3+ months.
- **No "my city" entry point.** The homepage's mental model is prefectures. A resident of, say, Morioka City has no path from the homepage that ends at readable content about their city (see §4).
- Entry cards privilege the project's internal milestones （宮城県の実績接続， 福岡県， Phase 10 完了範囲） over a resident's likely first question ("what about my municipality?"). The Phase 10 card's copy is project-internal language.

## 2. Mobile rendering and readability

Evidence from `apps/web/app/globals.css` and module CSS (no device rendering was performed):

- **Good:** viewport meta is standard (`width=device-width, initial-scale=1`, no zoom lock). Body text is the browser-default 16px with `line-height: 1.75`; the font stack is system fonts only (Hiragino Sans / Yu Gothic / Noto Sans JP) — zero webfont cost. Primary CTAs have `min-height: 48px`. The mobile menu is a native `<details>` element (keyboard- and AT-operable without JS). Breakpoints at 980px / 700px / 440px; `prefers-reduced-motion` is respected.
- **Tables are handled where they exist.** Only two fetched pages use `<table>` at all (/compare, /data-quality, one table each), and both wrap it in a horizontally scrolling container (`.tableWrap` with `overflow-x: auto` in `app/compare/page.module.css` and `app/data-quality/page.module.css`; same pattern in phase10 modules and `components/SettlementTrend.module.css`). Data-heavy pages are card/list-based instead — e.g. /municipalities/hokkaido renders 108 indicators as cards (111 `<h3>`, 0 `<table>`), so no page-level horizontal-scroll risk was found.
- **Small chrome text.** Several persistent UI texts are far below body size: `.dataPulse` 0.68rem (~10.9px), `.brandText small` 0.59rem (~9.4px — the header brand sub-line), `.statusBadge` 0.65rem, footer bottom row 0.65rem, mobile-nav section labels 0.62rem. For the resident audience (including older readers) the ~9.4px brand subtext and ~11px data-pulse are legibility risks even though contrast passes WCAG AA (verified earlier by PR #483 work).
- **Mobile menu tap targets are slightly small.** `.mobileNav nav a` is 0.88rem text with 10px vertical padding → roughly 40px tall, under the 44px guideline used by Apple HIG / WCAG 2.5.8's spirit (24px is the WCAG 2.2 AA minimum, so this is a comfort issue, not a conformance failure).
- Long pages: /municipalities/hokkaido is 280,923 bytes of HTML (108 indicator cards on one page). It is server-rendered, so it reads progressively, but on a phone it is a very long scroll with no in-page jump index observed in the fetched HTML beyond the explorer filters.

## 3. Sharing / discoverability basics (actual HTML)

Checked in the served `<head>` of 15 page types.

**Present**
- `<title>` and meta description: unique and page-specific on most page types (e.g. /municipalities 「47都道府県の政策目標を根拠から探す」, /compare 「福岡市・北九州市の財政比較」, phase9 city pages via `generateMetadata`).
- Open Graph basics on all pages: og:title, og:description, og:url, og:site_name, og:locale=ja_JP, og:type=website.
- robots.txt: `Allow: /` with a Sitemap reference. sitemap.xml: 105 URLs, all reachable, with changefreq/priority.
- Favicon: SVG icon served and linked. Web manifest served with name/short_name/description/theme colors. `<html lang="ja">`. `meta robots: index, follow`.

**Missing or wrong — on every page checked**
- **No `og:image` and no `twitter:image` anywhere; `twitter:card` is `summary` (small) on every page.** Any link shared to X/LINE/Facebook renders as a bare text card with no visual identity. For a launch whose next goal is access growth, this is the single cheapest high-impact gap.
- **OG tags do not follow the page.** Pages with their own metadata still emit the layout's generic og:title 「Jichi Insight | 自治体インサイト」 and generic og:description (verified in served HTML for /assemblies and /compare). A shared link to the fiscal-comparison page previews with the site-generic title, not 「福岡市・北九州市の財政比較」.
- **No `<link rel="canonical">` on any page.** (Next.js emits one only when `alternates.canonical` is set; `app/layout.tsx` does not set it.)
- **No structured data (JSON-LD) anywhere** — no WebSite / Organization / Dataset markup for search engines.
- **Three pages have no page metadata at all** — /about, /methodology, /sources fall back to the layout default, so their served `<title>` is the generic 「Jichi Insight | 自治体インサイト」 and their description is the site default, identical to the homepage's. /methodology （読み方・評価方法） is a core trust page and is indistinguishable in search results. (Source: `app/about/page.tsx`, `app/methodology/page.tsx`, `app/sources/page.tsx` contain no `export const metadata`; confirmed in served HTML.)
- **Sitemap has no `<lastmod>`** on any of its 105 URLs, so crawlers get no freshness signal despite the site updating its data (sitemap generated by `app/sitemap.ts`, which sets changefreq/priority only).
- **Manifest has no `icons` array** (`app/manifest.ts` returns name/description/colors but no icons), so "add to home screen" falls back to a generic icon even though a site icon exists.

## 4. Internal linking and content discovery

- **Prefectures are findable.** /municipalities has a client-side search input (`#coverage-search`, placeholder 「例：宮城県、沖縄、総合計画」), one select, and prefecture cards; the homepage links to it 8 times. Search is JS-driven (CoverageExplorer component) — the underlying cards are server-rendered, so the list itself is readable without JS, but filtering is not.
- **Cities are not findable — the audit's biggest structural finding.** The 67 Phase 15 municipalities （中核市・県庁所在地） and the 20 designated cities have no pages on the site. /municipalities mentions none of them （盛岡市・函館市・いわき市・川口市・宇都宮市： 0 occurrences). They appear only as rows on /review-progress, and for each of the 9 reviewed cities the row's only outbound link is to a **raw JSON file on GitHub** (`https://github.com/M-Osugi1230/jichi-insight/blob/main/data/catalog/morioka_phase15_completion.json`, same pattern for the other 8). The page itself says 「資料索引と完了記録はGitHub上の公開原本です」. Nine cities' worth of completed, owner-approved review work is effectively invisible to a non-technical resident.
- **/review-progress is a transparency ledger, not a resident page.** It is honest and well-explained (9/67 complete, 58 waiting, next target いわき市， "not a ranking" disclaimers, updated 2026-11-15), but its audience is project followers; a newcomer landing there from search gets process, not answers about their city.
- **404 page is good.** Plain-language heading 「お探しのページは見つかりませんでした。」, an on-brand explanation (pages that aren't ready aren't published), and two recovery links （ホームへ戻る / 公式資料を見る）. Served correctly as HTTP 404 via the site's not-found page.
- Internal linking density is otherwise high (footer nav groups 調べる / 信頼のために / 運営方針・利用規約・プライバシー・免責事項； header menu repeats them).

## 5. Trust signals

- **Findable within 2 clicks: yes.** From the homepage, the header's 根拠・運営 menu and the footer expose このサイトの目的 (/about), 読み方・評価方法 (/methodology), データ品質 (/data-quality), 自治体レビュー進捗 (/review-progress), 公式資料 (/sources), 訂正・反論 (/corrections) — all one click. The corrections history page (/corrections/history) shows the real correction-2026-001 entry with before/after and reasons.
- **The corrections flow is real but has a hard gate.** /corrections explains what to report, the evidence required, and the 5-step process well, with clear privacy warnings. The only submission route, however, is a GitHub Issue form (`github.com/M-Osugi1230/jichi-insight/issues/new?template=data-correction.yml`) — it requires a GitHub account, and the page does not say so before the click. For a resident, and even for a municipal official filing an official rebuttal （反論）, this is a significant barrier.
- **No license notice on the site.** The rendered HTML contains no "CC BY", "MIT", "©", or ライセンス string (checked on the homepage). The project adopted MIT (code) + CC BY 4.0 (methodology/data) in the repository (LICENSE + docs/LICENSING.md, PR #462), and /terms §2 describes reuse conditions in prose, but a visitor who wants to reuse the data cannot discover the actual licenses from the website. For a public-data project, the license *is* a trust and reuse signal.
- **No named operator.** /terms (last updated 2026-07-29) speaks of 「本サイト」 generically; neither /about nor the footer names who operates the site or gives a non-GitHub contact. (Whether to name the operator is an owner decision; the absence is noted as a trust-signal gap, not a defect per se.)

## 6. Performance signals (static analysis of served files only)

- **Homepage weight:** HTML 67,940 bytes; 20 referenced static assets totaling **3,339,201 bytes raw / ~546,922 bytes gzip** as served. 17 of the assets are JS chunks. The two largest raw chunks (741,196B and 660,660B) are data-heavy and compress to ~73KB / ~81KB gzip, but every page loads a similar 17–18-chunk set (Hokkaido page: 18 scripts), including on purely textual pages like /methodology (44,889B HTML). Client components (the "Explorer" family) appear to pull their datasets into the shared chunk graph.
- **Deep pages are HTML-heavy:** /municipalities/hokkaido 280,923B, /review-progress 148,549B, /municipalities 125,561B, /sources 109,090B, /policies 94,420B (raw HTML; gzip reduces these substantially). All content is server-rendered, so first paint does not wait for JS — the cost is download/parse on low-end phones, not blank screens.
- **Nothing else heavy:** no webfonts, no content images at all (the only image asset is the SVG favicon — which is also why shares have no visual, §3), no third-party embeds, no analytics or advertising tags observed in any fetched page.
- These are byte counts, not lab scores; the earlier sandbox Lighthouse run (Accessibility/Best Practices/SEO 100) is consistent with a fast-rendering but JS-bulky site.

---

## Prioritized fix list

### Quick wins (one small PR each), in impact order

1. **Add a share image and large-card Twitter tags.** Create an OG image (1200×630) and set `openGraph.images` + `twitter: { card: "summary_large_image", images: [...] }`.
   Files: `apps/web/app/layout.tsx`; new asset via `apps/web/app/opengraph-image.png` (Next file convention) or `apps/web/public/og-image.png` + explicit URL in layout metadata.
2. **Make OG title/description follow each page.** Add an `openGraph` block alongside the existing `metadata` on the main landing pages so shared links preview with the page's own title/description instead of the site generic one.
   Files: `apps/web/app/layout.tsx` (helper/defaults) + `apps/web/app/municipalities/page.tsx`, `app/policies/page.tsx`, `app/compare/page.tsx`, `app/executives/page.tsx`, `app/assemblies/page.tsx`, `app/data-quality/page.tsx`, `app/review-progress/page.tsx`, `app/corrections/page.tsx` (the pages that already export metadata).
3. **Give /about, /methodology, /sources their own title + description.** Three small `export const metadata` additions; methodology especially is a search landing page for trust queries.
   Files: `apps/web/app/about/page.tsx`, `apps/web/app/methodology/page.tsx`, `apps/web/app/sources/page.tsx`.
4. **Add canonical URLs.** Set `alternates.canonical` per route (can ride along with #2/#3 edits; layout can hold the pattern).
   Files: `apps/web/app/layout.tsx` + the same page files as #2/#3.
5. **Put the licenses and a copyright line on the site.** One footer line — e.g. 「© 2026 Jichi Insight — コード: MIT / データ・方法論: CC BY 4.0」 — linking to the repo's LICENSE / docs/LICENSING.md. Matches the already-decided licensing (PR #462) and makes reuse terms discoverable.
   Files: `apps/web/components/SiteFooter.tsx`.
6. **Add icons to the web manifest** so home-screen installs use the site icon.
   Files: `apps/web/app/manifest.ts` (icons array referencing the existing icon asset; add PNG sizes if the SVG alone is not accepted by target browsers).
7. **Fix the freshness signal.** Either label the header pulse precisely （収録データの更新日） or show the newest update across datasets (the review queue's 2026-11-15 date) next to it, so the top bar never looks 3 months stale on launch day.
   Files: `apps/web/components/SiteHeader.tsx` (+ the stats data source it reads, `reviewedCoverageStats`).
8. **Add `<lastmod>` to the sitemap** from the data update dates already in the repo.
   Files: `apps/web/app/sitemap.ts`.
9. **Mobile comfort pass:** raise mobile-menu link height to ≥44px and lift the smallest chrome text (brand sub-line 0.59rem, data pulse 0.68rem) by a step.
   Files: `apps/web/app/globals.css`.
10. **Warn before the GitHub gate on /corrections:** one line stating that submission opens a GitHub Issue form and requires a GitHub account, so residents are not surprised after the click.
    Files: `apps/web/app/corrections/page.tsx`.

### Larger work, in impact order

1. **Publish the Phase 15 reviewed cities as web pages.** Generate a readable city page per reviewed municipality from the existing reviewed packages (plan framework, fiscal top lines, evidence links, deferred items) and link them from /review-progress rows and a city index/search on /municipalities. This converts 9 completed reviews (and every future one) from GitHub JSON into the site's actual product, gives each city a shareable/indexable URL, and is the precondition for any "find my city" homepage entry. New route under `apps/web/app/municipalities/` + data loading from `data/reviewed/` and `data/catalog/`.
2. **Homepage plain-language pass, driven by the first real comprehension test.** Run the prepared 3-minute first-visit test (kit exists: human-testing-kit-2026-11-15) with a few first-time users, then act on it: likely outcomes are a one-line "what you can do here" for residents, glosses or replacements for Evidence Packet / Reviewed / Phase jargon, and demoting project-milestone cards (Phase 10) below the resident entry points.
3. **A non-GitHub correction/contact route.** Add a submission path that does not require a GitHub account (e.g. a form service that files into the same triage, or a published contact address for official rebuttals), keeping the GitHub flow for those who prefer it. Needs an owner decision on the channel; the corrections page and runbook then document both routes.
4. **Real-device and assistive-tech verification.** The checks that have never been done: current iPhone/Android rendering, keyboard-only navigation, VoiceOver/TalkBack pass over the header menu, explorers, and a prefecture page. Lighthouse scores do not cover these.
5. **Reduce the JS every page ships.** Investigate why content-only pages load the full 17–18 chunk set (~547KB gzip on the homepage) and code-split the Explorer components/datasets so text pages ship close to zero JS; keep an eye on total HTML weight for the largest pages (Hokkaido 281KB) via pagination or collapsed sections if real-device checks show scroll/parse pain.
6. **Structured data.** After canonical/OG land, add JSON-LD (WebSite + Organization on the layout; Dataset on data pages) to help search engines present the site as a data source.

## Notes on what was NOT verified

- No real-device, keyboard, or screen-reader behavior (audit was HTML/CSS static analysis).
- No lab performance measurement; §6 is served-byte analysis only.
- Search-engine indexing status (e.g. whether the sitemap has been submitted anywhere) is not observable from the site or repo and was not checked.
