# Documents System Implementation Progress
Reference file: docs/design/plans/documents_system.md

## Architecture Rule
**No document-related code in `server/core/server.py`.** All document system
logic — menu handlers, editbox handlers, dispatch entries — must live in the
mixin modules under `server/core/documents/`:

| Module | Responsibility |
|---|---|
| `manager.py` | Data layer (`DocumentManager`): metadata, content, locks, history |
| `browsing.py` | `DocumentBrowsingMixin`: browsing menus, action menu, settings, editing flows |
| `transcriber_role.py` | `TranscriberRoleMixin`: transcriber assignment and management menus |

The Server class inherits both mixins and wires them into the central dispatch
via two hooks — **do not add individual entries to `server.py`**:

- **Menu dispatch**: `_get_document_menu_handlers(user, selection_id, state)` on `DocumentBrowsingMixin` returns a dict of all document + transcriber menu handlers. It is unpacked into the `handlers` dict inside `_dispatch_menu_selection`.
- **Editbox dispatch**: `_handle_document_editbox(user, current_menu, packet, state)` on `DocumentBrowsingMixin` is called early in `_handle_editbox` and returns `True` if handled.

New document menus or editboxes should be added to these methods (or to `_get_transcriber_menu_handlers` for transcriber-specific menus), never directly to `server.py`.

## Completed (Sessions 1 through 3)

### Database Layer (session 1)
- `fluent_languages` column on `users` table (JSON text)
- `transcriber_assignments` table with full CRUD methods
- Migration support in `server/persistence/database.py`

### Backend Infrastructure (session 1)
- **NetworkUser.fluent_languages**: property, setter, plumbed from DB on login/reconnect (`server/core/users/network_user.py`, `server/core/server.py`)
- **Fluent languages option**: toggle menu in options, uses `show_language_menu` with on/off status labels, saves to DB (`server/core/server.py`, `server/locales/en/main.ftl`)
- **Localization.get_available_locale_codes()**: warmup-safe method that returns language codes from directory names without triggering bundle compilation (`server/messages/localization.py`)
- **DocumentManager class**: `server/core/documents/manager.py`
  - Startup loading with auto-generated metadata for existing folders
  - Category queries with locale fallback (en -> slug)
  - Document filtering by category (all / specific / uncategorized)
  - Content read on demand, write with metadata timestamp update
  - Edit locks: acquire, release, conflict detection, stale cleanup (30min timeout)
  - Version history: backup on save, 5-version cap per locale
  - Create document and create category operations
- **Server wiring**: DocumentManager initialized and loaded on startup
- **Tests**: 29 DocumentManager tests, 4 new fluent languages tests in options menu suite
- **Locale completeness**: fixed missing .ftl files across 28 locales, added Serbian (sr)

### Document Browsing — Read-Only (session 2)
- "Documents" item in main menu for all users (approved and unapproved)
- `_show_documents_menu`: category list + "All documents" + "Uncategorized"
- `_show_documents_list`: document titles for a given category
- `_show_document_view`: read-only editbox with locale fallback to English
- Dispatch table entries for `documents_menu`, `documents_list_menu`

### Transcriber Management (session 3)
- "View transcribers by language" and "View transcribers by user" items added to documents menu
- **By language flow**: `show_language_menu` with per-language user counts → user list for selected language → admin can click to remove (with confirmation) or "Add users" to show toggle list of eligible users (filtered by fluent_languages)
- **By user flow**: transcriber list with language counts → language list for selected user → admin can click to remove (with confirmation) or "Add languages" to show toggle list of unassigned fluent languages
- Validation: only users with a language in `fluent_languages` can be assigned as transcribers
- Toggle sounds: `checkbox_list_on.wav` / `checkbox_list_off.wav` for add/remove
- Dispatch table entries: `transcribers_for_language_menu`, `transcriber_remove_confirm`, `transcribers_by_user_menu`, `transcriber_user_languages_menu`, `transcriber_remove_lang_confirm`
- 20 new locale strings in `server/locales/en/main.ftl`

### Module Refactor (session 4)
- Moved document browsing and transcriber management code out of `server/core/server.py` into mixin modules
- Module structure under `server/core/documents/`:
  - `manager.py` — data layer (DocumentManager)
  - `browsing.py` — `DocumentBrowsingMixin` (document menus, list, view)
  - `transcriber_role.py` — `TranscriberRoleMixin` (transcriber assignment/management menus)
- Server class inherits both mixins; cross-mixin calls resolve via MRO

### Document Actions (session 5)
- Action menu for transcribers/admins (View, Edit placeholder, Document settings)
- Document settings submenu with title, visibility, categories, add/remove translation, delete
- New DocumentManager data methods: get/set title, visibility, categories; add/remove translation; delete document
- Menu and editbox dispatch entries moved entirely out of `server/core/server.py` via `_get_document_menu_handlers()` and `_handle_document_editbox()` on the browsing mixin
- Transcriber menu dispatch entries also moved out via `_get_transcriber_menu_handlers()` on the transcriber role mixin

---

## Chunk 4: Document Actions (Admin & Transcriber)

The action menu that appears when a transcriber or admin clicks a document.

### Scope
- Role-based behavior: normal users auto-view, transcribers/admins see action menu
- Action menu: View, Edit, Document settings
- Document settings submenu:
  - Change title (per locale)
  - Manage visibility (public/private toggles per locale)
  - Modify category list (admin, boolean toggle list)
  - ~~Add translation~~ — deferred to Chunk 5 (shares the document contents dialog for content entry)
  - Remove translation (admin, confirmation with safeguards)
  - Delete document (admin, confirmation with translation count)
- Permission checks: transcribers limited to their assigned languages
- Locale strings for all prompts and confirmations
- Tests for action menu routing and permission checks

### Files modified
- `server/core/documents/manager.py` — new data methods (get/set title, visibility, categories; add/remove translation; delete)
- `server/core/documents/browsing.py` — action menu, settings submenu, all management handlers; dispatch via `_get_document_menu_handlers` and `_handle_document_editbox`
- `server/core/documents/transcriber_role.py` — dispatch via `_get_transcriber_menu_handlers`
- `server/locales/en/main.ftl` — 24 new locale strings

---

## Chunk 5: Document Editing & Add Translation

The document contents dialog — used any time document content is shown for editing (editing an existing document, adding a translation, creating a new document). Also includes the "Add translation" flow deferred from Chunk 4, since the content entry step should reuse this same dialog. Read-only viewing remains a simple editbox.

### Scope
- **Document contents dialog**: multiline editbox with current content, edit locks, save/cancel
- Side-by-side source display: if editing a non-source locale, show source content in a read-only editbox
- Save handler: calls `DocumentManager.save_document_content()` (handles backup + lock release)
- Cancel handler: release edit lock, return to document actions
- Escape = cancel, with confirmation if content changed
- Lock acquisition on edit open, conflict message if locked by another user
- **Add translation**: locale selection + title editbox, then open the document contents dialog for content entry
- Locale strings for editor prompts, save/cancel confirmations, lock conflict messages
- Tests for edit flow, lock integration, save with version backup

### Design notes: shared handlers and reuse

**Shared title editbox**: The title editbox handler must be a single reusable handler used by all flows that set a document title: changing an existing title, naming a new translation, and naming a new document. Do not duplicate the title prompt/save logic across these flows.

**Shared document contents dialog**: The document contents dialog (multiline editbox with save/cancel/lock) must be a single reusable flow. Callers: edit existing document, add translation (after title entry), create new document (Chunk 6). Each caller passes context (folder_name, locale, whether it's a new translation/document) and the dialog handles save uniformly.

**Shared locale picker for document operations**: Change title, manage visibility, remove translation, and add translation all need to show the document's locales filtered by the user's assigned transcriber languages. This should be a single helper (e.g. `_get_user_accessible_locales(user, folder_name)`) rather than repeating the filter logic in each handler. Note: Chunk 4's implementation currently repeats this filter — consolidate when implementing Chunk 5.

**Shared category toggle list**: Chunk 4's "modify categories" and Chunk 6's "new document category selection" both present a toggle list of categories. Reuse the same display/toggle handler for both.

### Files to modify
- `server/core/documents/browsing.py` — editor handlers (or a new `document_editor.py` mixin); add new editbox entries to `_handle_document_editbox`
- `server/locales/en/main.ftl` — locale strings
- **Not** `server/core/server.py` — see Architecture Rule above

---

## Chunk 6: Document & Category Creation

Admin flows for creating new documents and categories.

### Scope
- New document flow: category selection (reuse shared category toggle list) -> title editbox (reuse shared title handler) -> document contents dialog (reuse shared contents dialog) -> auto-generate folder slug from title
- Slug collision detection with user-friendly error
- New category flow: slug editbox -> display name editbox
- Category management: rename (per locale), change sort method, delete (with document cleanup)
- Locale strings for creation flows
- Tests for creation flows and edge cases (duplicate slugs, empty input)
- See Chunk 5 design notes for all shared handlers that must be reused here

### Files to modify
- `server/core/documents/browsing.py` — creation handlers (or a new `document_creation.py` mixin); add new menu/editbox entries to `_get_document_menu_handlers` and `_handle_document_editbox`
- `server/core/documents/manager.py` — possibly add slug generation helper, delete methods
- `server/locales/en/main.ftl` — locale strings
- **Not** `server/core/server.py` — see Architecture Rule above
