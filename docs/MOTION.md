# UI Motion System

This site uses a restrained CSS-only motion system. Motion supports orientation and feedback; it is not used to decorate data or delay access to content.

## Principles and implementation

| Disney principle | UI application | Token / rule |
| --- | --- | --- |
| Slow In and Slow Out | Smooth starts and stops for entrance and interaction feedback | `--motion-ease-standard`, `--motion-ease-enter`, `--motion-ease-feedback` |
| Timing | Short feedback, moderate state changes, slower section entrances | 120 / 200 / 320 / 480 ms duration scale |
| Staging | A clear reading order with small, restrained section delays | `--motion-stagger-step: 48ms` |
| Secondary action / Follow Through | Small hover and open-state cues that do not compete with content | 2–5 px translation; no bounce or overshoot |

## Tokens

- Easing: standard `cubic-bezier(.22, 1, .36, 1)`; entrance `cubic-bezier(.16, 1, .3, 1)`; feedback `cubic-bezier(.2, .75, .25, 1)`.
- Durations: quick 120 ms, standard 200 ms, entrance 320 ms, emphasis 480 ms.
- Stagger: 48 ms per step.
- Entrance distance: 5 px.

## Scope

- Page-level section entrances use a subtle opacity change from 0.94 to 1 and a 5 px upward settle.
- Cards receive a 2 px hover lift and restrained shadow/border feedback.
- Buttons, navigation links, mobile navigation and footer links use short color, border, shadow and transform feedback.
- Native disclosure panels and navigation menus animate only when opened. Their content remains present in the document and does not rely on JavaScript.
- Focus-visible outlines and existing semantic disclosure behavior are unchanged.

## Accessibility and performance constraints

- All effects are inside `prefers-reduced-motion: no-preference`.
- `prefers-reduced-motion: reduce` disables every animation, transition and transform and forces zero-duration motion tokens. Smooth scrolling is disabled.
- Print styles disable animation and transition and force full opacity.
- Only `transform` and `opacity` are animated. No width, height, margin, padding, position, grid or other layout property is animated.
- No parallax, flashing, large movement, JavaScript animation, or new runtime dependency.
- Entrance keyframes start at opacity 0.94 rather than hiding content. Base styles remain fully visible if animation is unsupported, disabled, interrupted, or unavailable.
