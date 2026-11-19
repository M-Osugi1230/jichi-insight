"use client";

import { useEffect } from "react";

/**
 * Keep every source anchor in the DOM and accessible to screen readers.
 * On the Phase 15 city page, only the first currently available link to an
 * identical absolute URL should be a sequential keyboard Tab stop.
 *
 * Closed <details> content is skipped so a hidden anchor never takes the
 * "first" slot from a visible one. When a <details> opens or closes, update
 * the Tab order without changing labels, destinations, or click behavior.
 *
 * This is progressive enhancement: without JavaScript, every link remains
 * normally keyboard-accessible rather than becoming inaccessible.
 */
export function DeduplicateCitySourceTabStops() {
  useEffect(() => {
    const root = document.querySelector<HTMLElement>("[data-city-source-tab-scope]");
    if (!root) return;

    const refresh = () => {
      const seen = new Set<string>();
      const anchors = root.querySelectorAll<HTMLAnchorElement>("a[href]");

      for (const anchor of anchors) {
        if (anchor.dataset.duplicateSourceTabStop === "true") {
          anchor.removeAttribute("tabindex");
          delete anchor.dataset.duplicateSourceTabStop;
        }
      }

      for (const anchor of anchors) {
        // Preserve author-defined Tab-order exclusions.
        if (anchor.hasAttribute("tabindex") && anchor.tabIndex < 0) continue;
        // A link inside a collapsed details body cannot receive Tab focus.
        if (anchor.closest("details:not([open])") && !anchor.closest("summary")) continue;

        const url = new URL(anchor.href, window.location.href);
        if (!["http:", "https:"].includes(url.protocol)) continue;
        if (url.origin === window.location.origin) continue;

        // Use the full resolved URL: links to separate sections of a source
        // document retain their own Tab stop.
        const key = url.href;
        if (seen.has(key)) {
          anchor.tabIndex = -1;
          anchor.dataset.duplicateSourceTabStop = "true";
        } else {
          seen.add(key);
        }
      }
    };

    refresh();
    // The details toggle event does not bubble, but can be captured.
    // Recompute after expanding evidence: the first available anchor stays
    // tabbable even if an earlier copy lives inside collapsed content.
    root.addEventListener("toggle", refresh, true);

    return () => {
      root.removeEventListener("toggle", refresh, true);
      for (const anchor of root.querySelectorAll<HTMLAnchorElement>(
        'a[data-duplicate-source-tab-stop="true"]',
      )) {
        anchor.removeAttribute("tabindex");
        delete anchor.dataset.duplicateSourceTabStop;
      }
    };
  }, []);

  return null;
}
