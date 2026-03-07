# Web Client System Theme Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add system-driven light/dark UI color support to the web client without introducing a manual theme toggle or changing client behavior.

**Architecture:** Keep theme handling CSS-first in `clients/web/styles.css` using semantic custom properties and one `@media (prefers-color-scheme: dark)` override block. Avoid JavaScript theme state. Touch HTML only where document-level browser hints are needed, and keep all interaction code in `clients/web/app.js` unchanged unless verification shows a browser-control issue.

**Tech Stack:** Static HTML, CSS custom properties, `prefers-color-scheme`, browser-native dialogs/forms, PlayPalace web client assets

---

### Task 1: Audit current hardcoded colors and define semantic token targets

**Files:**
- Modify: `clients/web/styles.css`

**Step 1: Write the failing test**

There is no existing automated theme test harness in `clients/web`. Instead, define the failure condition as a token audit:

- Search `clients/web/styles.css` for hardcoded UI colors that bypass the existing token layer.
- Record every selector that still depends on a light-only literal value.

Expected failure: multiple selectors still use fixed light values such as `#fff`, `#fbfdff`, and hardcoded active-row colors.

**Step 2: Run audit to verify the current stylesheet fails the theme requirement**

Run: `rg -n "#|rgba\\(" clients/web/styles.css`
Expected: multiple hardcoded colors are present outside a reusable semantic token system.

**Step 3: Write minimal implementation**

Add or rename semantic custom properties in `:root` for:
- page background
- page gradient start
- panel surface
- raised/read-only surface
- text
- muted text
- border
- primary button
- primary button text
- secondary button
- secondary button text
- danger text
- focus ring
- selected menu surface
- selected menu outline
- shadow color

Do not add dark-mode overrides yet in this task. First make the stylesheet consume semantic tokens everywhere practical.

**Step 4: Re-run audit to verify the stylesheet is tokenized**

Run: `rg -n "#|rgba\\(" clients/web/styles.css`
Expected: only root token declarations, unavoidable shadow values, and intentionally preserved literals remain.

**Step 5: Commit**

```bash
git add clients/web/styles.css
git commit -m "Tokenize web client theme colors"
```

### Task 2: Add system dark-mode overrides

**Files:**
- Modify: `clients/web/styles.css`

**Step 1: Write the failing test**

Define the failure condition manually:
- In a browser with dark system theme enabled, open the web client.
- Observe that the UI still renders with the light palette.

Expected failure: page, panels, controls, and history surfaces remain light-themed in dark mode.

**Step 2: Run manual verification to confirm failure**

Run the web client locally and inspect it in a browser with dark theme enabled.

Suggested local run:
```bash
python3 -m http.server 8080
```

Open:
`http://127.0.0.1:8080/clients/web/`

Expected: the UI does not yet adapt to dark mode.

**Step 3: Write minimal implementation**

In `clients/web/styles.css`:
- add `color-scheme: light dark` on `:root` or `html`
- add `@media (prefers-color-scheme: dark)` token overrides
- keep selectors unchanged where possible by relying on the semantic token layer from Task 1

Dark tokens should specifically cover:
- page background and gradient
- panel surfaces
- read-only surfaces
- text and muted text
- borders
- primary and secondary buttons
- active menu row treatment
- focus ring visibility

**Step 4: Re-run manual verification**

Repeat the browser check in dark mode.
Expected: the client follows the system dark theme and remains readable.

**Step 5: Commit**

```bash
git add clients/web/styles.css
git commit -m "Add system dark mode styling for web client"
```

### Task 3: Fix document-level browser control behavior

**Files:**
- Modify: `clients/web/index.html`
- Modify: `clients/web/styles.css`

**Step 1: Write the failing test**

Define the failure condition manually:
- In dark mode, verify whether browser-native dialogs, inputs, and form controls render inconsistently with the themed page.

Expected failure: one or more native controls may still look mismatched depending on browser defaults.

**Step 2: Run manual verification to confirm whether this issue exists**

Open the login dialog and actions dialog in both light and dark system themes.
Expected: if controls mismatch, this task is required; if they already match, keep the implementation minimal.

**Step 3: Write minimal implementation**

If needed:
- add or adjust document-level theme hints in `clients/web/index.html`
- keep CSS hints in `clients/web/styles.css`
- avoid any JavaScript theme logic

Do not add a theme toggle or persisted preference.

**Step 4: Re-run manual verification**

Verify dialogs, text inputs, checkboxes, range sliders, and buttons align with the active system theme.
Expected: consistent browser-control rendering in both modes.

**Step 5: Commit**

```bash
git add clients/web/index.html clients/web/styles.css
git commit -m "Align web client native controls with system theme"
```

### Task 4: Update web client version and verify cache-busted asset loading

**Files:**
- Modify: `clients/web/version.js`
- Check: `clients/web/index.html`

**Step 1: Write the failing test**

Define the failure condition:
- the web client version string still reflects the pre-theme-build version after theme changes ship

Expected failure: `clients/web/version.js` has not been incremented.

**Step 2: Verify current version before changing it**

Run: `sed -n '1,80p' clients/web/version.js`
Expected: existing version is older than the new theme work.

**Step 3: Write minimal implementation**

Increment `window.PLAYPALACE_WEB_VERSION` in `clients/web/version.js` using the repository’s monotonic format.

Do not move versioning into config.

**Step 4: Verify cache busting still works**

Run: `sed -n '1,220p' clients/web/index.html`
Expected: the versioned `app.js` loader path still uses `window.PLAYPALACE_WEB_VERSION`.

**Step 5: Commit**

```bash
git add clients/web/version.js
git commit -m "Bump web client version for system theme support"
```

### Task 5: Run verification and record manual test results

**Files:**
- Modify: `clients/web/README.md`

**Step 1: Write the failing test**

Define the failure condition:
- there is no record of how to verify system theme behavior for future web-client changes

Expected failure: `clients/web/README.md` does not mention theme verification at all.

**Step 2: Verify the gap**

Run: `rg -n "theme|dark|light" clients/web/README.md`
Expected: no relevant verification guidance exists.

**Step 3: Write minimal implementation**

Add a short verification note to `clients/web/README.md` covering:
- how to run the client locally
- that the client follows system dark/light theme automatically
- what key UI areas to check during manual verification

Keep the note concise.

**Step 4: Run final verification**

Run:
```bash
python3 -m http.server 8080
```

Manual checks:
1. Verify light theme on desktop width.
2. Verify dark theme on desktop width.
3. Verify light theme on narrow/mobile width.
4. Verify dark theme on narrow/mobile width.
5. Open login and actions dialogs in both themes.
6. Check menu selection, history panes, chat input, buttons, and status text for readability.

Expected: all listed surfaces remain readable and behavior is unchanged.

**Step 5: Commit**

```bash
git add clients/web/README.md
git commit -m "Document web client system theme verification"
```
