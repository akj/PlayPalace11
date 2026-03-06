# Web Client Reconnect And Session UX Design

Date: 2026-03-05
Branch: `web-client`
Status: approved

## Goal
Improve web client reconnect and session UX so unexpected disconnects automatically retry for up to 60 seconds using saved auth state, then fall back cleanly to the login dialog if recovery fails.

## Scope
### In scope
- Automatic reconnect after unexpected disconnects and connection errors.
- Reuse saved session token and refresh token during reconnect.
- Limit reconnect attempts to a 60-second retry window.
- Improve user-visible status and activity messaging for reconnect/session states.
- Keep the login dialog closed during retry unless reconnect expires or auth is no longer usable.

### Out of scope
- Infinite reconnect behavior.
- Manual theme or layout changes.
- Server packet changes.
- New account/session features on the backend.
- Broad network transport redesign.

## Constraints
- Intentional user disconnects must not trigger auto reconnect.
- The reconnect policy should remain in the web client app layer, not the socket transport layer.
- Existing bootstrap auth behavior on page load must keep working.
- The web client should remain keyboard-first and screen-reader-friendly.

## Current Context
- [`clients/web/app.js`](/home/alek/git/PlayPalace/clients/web/app.js) already stores username, session token, refresh token, and expiry timestamps.
- The client already bootstraps from saved session or refresh tokens on load.
- Session refresh is already scheduled before session expiry.
- Unexpected disconnects currently send the user straight back to the login dialog with minimal differentiation between causes.
- [`clients/web/network.js`](/home/alek/git/PlayPalace/clients/web/network.js) is currently a thin WebSocket wrapper and should stay transport-focused.

## Approaches Considered
1. Reuse the existing auth bootstrap path with a reconnect controller (selected):
   - Extract or reuse a shared auth-attempt path.
   - Add reconnect timing, attempt gating, and user-visible status in `app.js`.
   - Lowest duplication and best fit with existing auth storage.
2. Put reconnect in the network layer:
   - Would reopen sockets automatically in `network.js`.
   - Wrong layer because reconnect depends on auth token selection and login UX policy.
3. Build a full connection/session state machine first:
   - Cleanest long-term architecture.
   - More change than needed for the current feature.

## Selected Architecture
Add a small reconnect controller in [`clients/web/app.js`](/home/alek/git/PlayPalace/clients/web/app.js).

The reconnect controller should:
- track whether the last disconnect was intentional
- track whether a reconnect window is active
- remember the reconnect deadline and attempt count
- reuse the existing session-token-first, refresh-token-second auth ordering
- retry within the 60-second window using scheduled backoff
- stop retrying when:
  - reconnect succeeds
  - the retry window expires
  - there is no usable saved auth state
  - the user explicitly disconnects

`network.js` should remain a transport wrapper, with only minimal additions if callback context becomes necessary.

## User Experience
- While reconnect is active:
  - show reconnect-specific status text
  - keep the login dialog closed
  - log reconnect progress in the activity/history buffer
- On reconnect success:
  - clear reconnect state
  - restore the normal connected/authenticated status
- On reconnect expiry:
  - stop retrying
  - show a clear “login required” message
  - open the login dialog
- On manual disconnect:
  - stop reconnect logic entirely
  - show normal disconnected state

## State Flow
1. Client is connected and authenticated.
2. Unexpected disconnect or socket error occurs.
3. If usable auth state exists:
   - start reconnect window
   - retry until success or 60-second deadline
4. If reconnect succeeds:
   - clear reconnect window
   - resume normal session refresh behavior
5. If reconnect cannot proceed or the deadline expires:
   - clear reconnect state
   - surface a clear failure reason
   - return to the login dialog

## Error Handling
- Missing or expired tokens should short-circuit reconnect and go directly to login with a clear explanation.
- Refresh-session failure should terminate reconnect and require login instead of looping.
- Reconnect retry timers must be cleared on success, manual disconnect, or reconnect abandonment.

## Verification Strategy
1. Verify initial bootstrap auth still works from valid saved tokens.
2. Verify unexpected disconnect starts reconnect mode.
3. Verify manual disconnect does not start reconnect mode.
4. Verify reconnect retries stop after 60 seconds.
5. Verify reconnect failure returns to login with a clear message.
6. Verify reconnect success clears temporary reconnect state and resumes normal session refresh behavior.

## Success Criteria
1. Unexpected disconnects attempt automatic reconnect for up to 60 seconds.
2. Intentional disconnects never auto reconnect.
3. The login dialog stays closed during active reconnect attempts.
4. Reconnect expiry or auth failure returns the user to login with a clear reason.
5. Initial token-based bootstrap continues to function.
