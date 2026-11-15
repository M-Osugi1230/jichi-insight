"use client";

import { useRef, type FocusEvent, type KeyboardEvent, type ReactNode } from "react";

// A <details> dropdown used for header navigation, with the focus
// management the native element does not provide on its own:
// - When the menu is open and focus moves past the last item, focus lands
//   on content behind the still-open menu and becomes invisible. Closing
//   the menu as soon as focus leaves it entirely removes that dead end.
// - Escape closes the menu and returns focus to the <summary> (the menu
//   button), matching the disclosure navigation pattern.
// A closed menu keeps the native behaviour: its links stay out of the tab
// order because a closed <details> does not render its content.
export function DetailsNavMenu({
  className,
  children,
}: {
  className: string;
  children: ReactNode;
}) {
  const detailsRef = useRef<HTMLDetailsElement>(null);

  function handleKeyDown(event: KeyboardEvent<HTMLDetailsElement>) {
    if (event.key !== "Escape") return;
    const details = detailsRef.current;
    if (!details?.open) return;
    event.preventDefault();
    details.open = false;
    details.querySelector("summary")?.focus();
  }

  // React's onBlur is delivered on focusout, so it fires as focus moves
  // between descendants and carries the destination in relatedTarget.
  function handleBlur(event: FocusEvent<HTMLDetailsElement>) {
    const details = detailsRef.current;
    if (!details?.open) return;
    const next = event.relatedTarget as Node | null;
    if (next && !details.contains(next)) {
      details.open = false;
    }
  }

  return (
    <details
      ref={detailsRef}
      className={className}
      onKeyDown={handleKeyDown}
      onBlur={handleBlur}
    >
      {children}
    </details>
  );
}
