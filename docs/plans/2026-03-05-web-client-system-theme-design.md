# Web Client System Theme Design

Date: 2026-03-05
Branch: `web-client`
Status: approved

## Goal
Add automatic light/dark theme detection to the web client so UI colors follow the user's system color scheme without introducing a manual theme setting.

## Scope
### In scope
- Add semantic theme tokens to the web client stylesheet.
- Follow system light/dark preference automatically.
- Update existing web client surfaces to render correctly in both schemes.
- Limit the change to UI colors only.

### Out of scope
- Manual theme selection or persistence.
- Layout, spacing, typography, or interaction redesign.
- Reduced-motion, contrast-mode, or sound behavior changes.
- Server-side theme preferences or packet changes.

## Constraints
- Use system theme only for this phase.
- Keep the current web client structure and interaction model unchanged.
- Preserve keyboard-first and screen-reader-friendly behavior.
- Avoid JavaScript-managed theme state unless CSS alone cannot cover the requirement.

## Current Context
- [`clients/web/styles.css`](/home/alek/git/PlayPalace/clients/web/styles.css) currently defines a single light-oriented palette in `:root`.
- [`clients/web/index.html`](/home/alek/git/PlayPalace/clients/web/index.html) loads one stylesheet and does not advertise any theme behavior.
- [`clients/web/app.js`](/home/alek/git/PlayPalace/clients/web/app.js) has no theme management or `matchMedia` integration.
- There is no dedicated web-theme test harness in the current client code.

## Approaches Considered
1. CSS-first system theme detection (selected):
   - Use semantic CSS custom properties.
   - Keep light tokens as default.
   - Add `@media (prefers-color-scheme: dark)` overrides.
   - Lowest complexity and best fit for system-only scope.
2. JavaScript-managed theme state:
   - Watch `matchMedia("(prefers-color-scheme: dark)")` and set `data-theme`.
   - Useful if manual theme controls are imminent.
   - Adds state and behavior that are unnecessary for this phase.
3. Combined theme plus broader UI refresh:
   - Higher visual upside.
   - Too much risk and scope for the first pass.

## Selected Architecture
The web client will remain single-stylesheet and CSS-driven.

- Define semantic tokens for page background, elevated panel surfaces, text, muted text, borders, primary action color, secondary action color, focus outline, selected menu row, and read-only history surfaces.
- Keep the light palette in the base `:root`.
- Add one dark override block using `@media (prefers-color-scheme: dark)`.
- Add `color-scheme: light dark` at the document level so browser-native form controls and dialogs align with the active scheme.

No JavaScript theme controller will be added in this phase.

## Affected UI Areas
- Page background and shell container
- Panels and dialogs
- Buttons, including secondary buttons and disabled state
- Inputs, selects, textareas, and dialog fields
- Menu list rows and active selection state
- History panes and chat-adjacent content
- Status text and error text
- Focus-visible outlines

## Error Handling
- There is no runtime theme error path in the selected design.
- Browsers without `prefers-color-scheme` support will continue using the default light theme.
- If any token is missed, the fallback should remain readable in light mode and be caught during manual verification.

## Verification Strategy
1. Verify the client in a light system theme on desktop width.
2. Verify the client in a dark system theme on desktop width.
3. Verify both themes again on a narrow/mobile width.
4. Check readability and contrast for dialogs, buttons, menu selection, history panes, status text, and form inputs.
5. Confirm there is no behavior change in login, chat, menu navigation, or dialog flow.

## Immediate Follow-On Opportunities
1. Mobile action and navigation improvements for touch use.
2. Reconnect and session-state UX cleanup.
3. Desktop layout refinement after interaction polish is in place.

## Success Criteria
1. The web client follows the operating system light/dark theme automatically.
2. No manual theme toggle or stored preference is introduced.
3. Existing UI remains behaviorally unchanged.
4. Core surfaces remain readable and visually coherent in both themes on desktop and mobile widths.
