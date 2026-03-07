# Web Client Reconnect And Session UX Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add limited auto reconnect and clearer reconnect/session UX to the web client so unexpected disconnects retry for 60 seconds before returning the user to login.

**Architecture:** Keep reconnect policy in `clients/web/app.js`, where stored auth state and login UX already live. Reuse the existing session bootstrap/auth packet builders instead of duplicating auth logic. Leave `clients/web/network.js` transport-focused, changing it only if the reconnect controller needs slightly richer status signaling.

**Tech Stack:** Static HTML, browser WebSocket API, PlayPalace web client state store, token-based session auth, plain JavaScript modules

---

### Task 1: Add reconnect state scaffolding in the web client app layer

**Files:**
- Modify: `clients/web/app.js`

**Step 1: Write the failing test**

Define the failure condition from current behavior:
- unexpected disconnect immediately opens the login dialog
- there is no reconnect window, reconnect attempt count, or intentional-disconnect gate

Expected failure: `clients/web/app.js` has no reconnect controller state beyond `pendingAuthMethod` and `refreshTimerId`.

**Step 2: Verify the current gap**

Run: `rg -n "reconnect|intentional|retry|deadline|attempt" clients/web/app.js`
Expected: reconnect-specific state is missing or incomplete.

**Step 3: Write minimal implementation**

Add reconnect controller state in `clients/web/app.js`, such as:
- reconnect active flag
- reconnect deadline
- reconnect attempt count
- reconnect timer id
- intentional disconnect flag

Also add helpers to:
- clear reconnect timers/state
- determine whether reconnect should begin
- mark an intentional disconnect before user-driven socket close

Keep this task limited to state scaffolding and helpers. Do not wire retry flow yet.

**Step 4: Re-run verification**

Run: `rg -n "reconnect|intentional|retry|deadline|attempt" clients/web/app.js`
Expected: reconnect controller fields and helper functions now exist.

**Step 5: Commit**

```bash
git add clients/web/app.js
git commit -m "Add web client reconnect state scaffolding"
```

### Task 2: Reuse bootstrap auth logic for reconnect attempts

**Files:**
- Modify: `clients/web/app.js`

**Step 1: Write the failing test**

Define the failure condition:
- initial page-load bootstrap can authorize from saved tokens
- reconnect path does not reuse that logic and cannot cleanly retry in the same order

Expected failure: auth packet selection is duplicated or only available at bootstrap call sites.

**Step 2: Verify the current gap**

Run: `rg -n "buildAuthorizePacketFromSession|buildRefreshPacket|bootstrapAuthPacket|canUseSessionToken|canUseRefreshToken" clients/web/app.js`
Expected: auth packet selection is centered around boot only, not a shared reconnect helper.

**Step 3: Write minimal implementation**

Extract a shared helper in `clients/web/app.js` that:
- chooses session-token auth first
- falls back to refresh-token auth
- returns both the packet and the auth method label when available

Use that helper for initial bootstrap and future reconnect attempts.

**Step 4: Re-run verification**

Run: `rg -n "bootstrapAuthPacket|buildAuthAttempt|auth method|session_token|refresh_token" clients/web/app.js`
Expected: one shared path is responsible for choosing reconnect/bootstrap auth packets.

**Step 5: Commit**

```bash
git add clients/web/app.js
git commit -m "Share web client auth bootstrap and reconnect packet selection"
```

### Task 3: Implement limited reconnect retry flow

**Files:**
- Modify: `clients/web/app.js`
- Modify: `clients/web/network.js`

**Step 1: Write the failing test**

Define the failure condition manually:
- after an unexpected disconnect, the client opens login immediately instead of retrying for up to 60 seconds

Expected failure: no automatic reconnect occurs.

**Step 2: Verify the current failure path**

Read current handlers for:
- `onStatus("disconnected")`
- `onStatus("error")`
- `case "disconnect"`

Expected: all paths route directly to disconnected/login handling with no reconnect window.

**Step 3: Write minimal implementation**

In `clients/web/app.js`:
- start reconnect on unexpected disconnect/error when usable auth state exists
- retry using a timer-based backoff inside a 60-second deadline
- suppress login dialog opening while reconnect remains active
- stop reconnect when:
  - the user disconnected intentionally
  - reconnect succeeds
  - no auth packet can be built
  - reconnect deadline expires

Touch `clients/web/network.js` only if needed for a cleaner status distinction; otherwise leave it unchanged.

**Step 4: Re-run verification**

Run targeted static checks:
```bash
rg -n "reconnect" clients/web/app.js clients/web/network.js
```

Then manually simulate by reading the code path or, if a lightweight local check is practical, running the web client and forcing socket interruption.

Expected: unexpected disconnect path now schedules retries instead of opening login immediately.

**Step 5: Commit**

```bash
git add clients/web/app.js clients/web/network.js
git commit -m "Add limited auto reconnect to web client"
```

### Task 4: Improve reconnect and login-required messaging

**Files:**
- Modify: `clients/web/app.js`
- Modify: `clients/web/index.html`
- Modify: `clients/web/styles.css`

**Step 1: Write the failing test**

Define the failure condition:
- status text does not distinguish reconnecting, reconnect expired, or manual disconnect
- reconnect lifecycle messaging in history/activity is minimal or absent

Expected failure: user-visible state is ambiguous.

**Step 2: Verify the current gap**

Run: `rg -n "Disconnected|Connecting|Authorizing|login again|Connection error" clients/web/app.js`
Expected: status strings are too generic for reconnect flow.

**Step 3: Write minimal implementation**

Update user-visible UX so it can show:
- connecting
- connected, authorizing
- reconnecting with attempt progress
- reconnect expired / login required
- manual disconnect

Add only the minimal markup/style changes needed if the current status area is sufficient; do not redesign the page.

Also append reconnect lifecycle entries to the activity/history buffer in plain language.

**Step 4: Re-run verification**

Run:
```bash
rg -n "reconnect|login required|manual disconnect|Disconnected" clients/web/app.js
```

Expected: reconnect-specific status and history messages are now explicit.

**Step 5: Commit**

```bash
git add clients/web/app.js clients/web/index.html clients/web/styles.css
git commit -m "Clarify web client reconnect and login-required states"
```

### Task 5: Preserve refresh-session behavior and verify reconnect boundaries

**Files:**
- Modify: `clients/web/app.js`
- Modify: `clients/web/README.md`

**Step 1: Write the failing test**

Define the failure condition:
- reconnect logic could conflict with scheduled session refresh or undocumented recovery behavior

Expected failure: there is no explicit verification note for reconnect/session behavior.

**Step 2: Verify the current gap**

Run: `rg -n "reconnect|session refresh|refresh session|login required" clients/web/README.md`
Expected: reconnect/session verification guidance is missing.

**Step 3: Write minimal implementation**

In `clients/web/app.js`:
- ensure reconnect success clears reconnect timers/state
- ensure session refresh scheduling resumes after successful authorize/refresh
- ensure refresh-session failure terminates reconnect and returns to login cleanly

In `clients/web/README.md`:
- add a concise reconnect/session verification note covering:
  - initial token bootstrap
  - unexpected disconnect auto reconnect
  - manual disconnect no reconnect
  - 60-second timeout back to login

**Step 4: Run final verification**

Static checks:
```bash
git diff -- clients/web/app.js clients/web/network.js clients/web/README.md
```

Manual verification checklist:
1. Load with valid saved auth state and confirm bootstrap still works.
2. Trigger unexpected disconnect and confirm reconnect starts automatically.
3. Confirm login dialog stays closed during retry.
4. Confirm retry stops after about 60 seconds and returns to login.
5. Trigger manual disconnect and confirm no reconnect attempt starts.
6. Confirm a successful reauthorize clears reconnect state and resumes normal operation.

**Step 5: Commit**

```bash
git add clients/web/app.js clients/web/README.md
git commit -m "Document and verify web client reconnect boundaries"
```
