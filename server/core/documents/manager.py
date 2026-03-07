"""Document manager for loading, editing, and versioning server documents."""

import json
import logging
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path

LOG = logging.getLogger("playpalace.documents")

_MAX_HISTORY_PER_LOCALE = 5


class DocumentManager:
    """Manages document metadata, content, edit locks, and version history.

    Documents live in a directory tree where each subfolder is a document,
    containing locale-specific ``.md`` files and a ``_metadata.json``.
    """

    def __init__(self, documents_dir: Path):
        self._dir = documents_dir
        self._categories: dict = {}  # slug -> {sort, name: {locale: str}}
        self._documents: dict = {}  # folder_name -> document metadata dict
        self._edit_locks: dict = {}  # (folder_name, locale) -> {user, timestamp}

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    def load(self) -> int:
        """Load document metadata from disk.

        Returns the number of documents loaded.
        """
        self._dir.mkdir(parents=True, exist_ok=True)

        # Load or create root metadata
        root_meta_path = self._dir / "_metadata.json"
        if root_meta_path.exists():
            with open(root_meta_path, "r", encoding="utf-8") as f:
                root_meta = json.load(f)
            self._categories = root_meta.get("categories", {})
        else:
            self._categories = {}
            self._save_root_metadata()

        # Scan document subfolders
        self._documents.clear()
        for entry in sorted(self._dir.iterdir()):
            if not entry.is_dir():
                continue
            if entry.name.startswith("_"):
                continue

            doc_meta_path = entry / "_metadata.json"
            if doc_meta_path.exists():
                with open(doc_meta_path, "r", encoding="utf-8") as f:
                    self._documents[entry.name] = json.load(f)
            else:
                # Auto-generate metadata for existing document folders
                self._documents[entry.name] = self._generate_default_metadata(entry)
                self._save_document_metadata(entry.name)

        return len(self._documents)

    def _generate_default_metadata(self, folder: Path) -> dict:
        """Generate default metadata for a document folder without one."""
        now = datetime.now(timezone.utc).isoformat()
        title = folder.name.replace("_", " ").title()

        # Detect existing locale files
        locales = {}
        locale_codes = []
        for md_file in sorted(folder.glob("*.md")):
            locale_code = md_file.stem
            locale_codes.append(locale_code)
            locales[locale_code] = {
                "created": now,
                "modified_contents": now,
                "public": True,
            }

        # Ensure at least an 'en' entry
        if not locales:
            locale_codes.append("en")
            locales["en"] = {
                "created": now,
                "modified_contents": now,
                "public": True,
            }

        titles = {code: title for code in locale_codes}

        return {
            "categories": [],
            "source_locale": "en",
            "titles": titles,
            "locales": locales,
        }

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_categories(self, locale: str) -> list[dict]:
        """Return categories sorted by sort order with display names.

        Each entry has keys ``slug`` and ``name``.
        """
        result = []
        for slug, info in self._categories.items():
            names = info.get("name", {})
            display = names.get(locale) or names.get("en") or slug
            result.append({"slug": slug, "name": display})
        result.sort(key=lambda c: c["name"].lower())
        return result

    def get_documents_in_category(
        self, category_slug: str | None, locale: str
    ) -> list[dict]:
        """Return documents in a category.

        Args:
            category_slug: Category slug to filter by.  ``None`` returns all
                documents, ``""`` returns uncategorized documents.
            locale: Locale for display title resolution.

        Returns a list of dicts with ``folder_name`` and ``title``.
        """
        results = []
        for folder_name, meta in self._documents.items():
            cats = meta.get("categories", [])
            if category_slug is None:
                pass  # include all
            elif category_slug == "":
                if cats:
                    continue
            else:
                if category_slug not in cats:
                    continue

            titles = meta.get("titles", {})
            title = titles.get(locale) or titles.get("en") or folder_name
            results.append({"folder_name": folder_name, "title": title})

        results.sort(key=lambda d: d["title"].lower())
        return results

    def get_document_metadata(self, folder_name: str) -> dict | None:
        """Return the full metadata dict for a document, or None."""
        return self._documents.get(folder_name)

    def get_document_locale_count(self, folder_name: str) -> int:
        """Return the number of locales for a document."""
        meta = self._documents.get(folder_name)
        if meta is None:
            return 0
        return len(meta.get("locales", {}))

    def get_document_content(self, folder_name: str, locale: str) -> str | None:
        """Read a document's ``.md`` file for the given locale."""
        if folder_name not in self._documents:
            return None
        md_path = self._dir / folder_name / f"{locale}.md"
        if not md_path.exists():
            return None
        return md_path.read_text(encoding="utf-8")

    # ------------------------------------------------------------------
    # Writing
    # ------------------------------------------------------------------

    def save_document_content(
        self,
        folder_name: str,
        locale: str,
        content: str,
        editor_username: str,
    ) -> bool:
        """Write document content, back up the previous version, and release lock.

        Returns ``True`` on success, ``False`` if the document doesn't exist.
        """
        if folder_name not in self._documents:
            return False

        md_path = self._dir / folder_name / f"{locale}.md"

        # Back up existing version before overwriting
        if md_path.exists():
            self._backup_version(folder_name, locale)

        md_path.write_text(content, encoding="utf-8")

        # Update metadata timestamp
        meta = self._documents[folder_name]
        locales = meta.setdefault("locales", {})
        now = datetime.now(timezone.utc).isoformat()
        if locale in locales:
            locales[locale]["modified_contents"] = now
        else:
            locales[locale] = {
                "created": now,
                "modified_contents": now,
                "public": True,
            }
        self._save_document_metadata(folder_name)

        # Release edit lock
        self.release_edit_lock(folder_name, locale, editor_username)
        return True

    def create_document(
        self,
        folder_name: str,
        categories: list[str],
        locale: str,
        title: str,
        content: str,
    ) -> bool:
        """Create a new document folder with initial content.

        Returns ``False`` if a document with that folder name already exists.
        """
        if folder_name in self._documents:
            return False

        doc_dir = self._dir / folder_name
        doc_dir.mkdir(parents=True, exist_ok=True)

        now = datetime.now(timezone.utc).isoformat()
        meta = {
            "categories": categories,
            "source_locale": locale,
            "titles": {locale: title},
            "locales": {
                locale: {
                    "created": now,
                    "modified_contents": now,
                    "public": True,
                }
            },
        }
        self._documents[folder_name] = meta
        self._save_document_metadata(folder_name)

        md_path = doc_dir / f"{locale}.md"
        md_path.write_text(content, encoding="utf-8")
        return True

    def set_document_title(
        self, folder_name: str, locale: str, title: str
    ) -> bool:
        """Update the title for a locale in document metadata.

        Titles are stored separately from locale entries, so setting a title
        for a locale that has no translation yet does not create a locale entry.

        Returns ``True`` on success, ``False`` if the document is not found.
        """
        meta = self._documents.get(folder_name)
        if meta is None:
            return False
        titles = meta.setdefault("titles", {})
        titles[locale] = title
        self._save_document_metadata(folder_name)
        return True

    def set_document_visibility(
        self, folder_name: str, locale: str, public: bool
    ) -> bool:
        """Update the public flag for a locale in document metadata.

        Returns ``True`` on success, ``False`` if document or locale not found.
        """
        meta = self._documents.get(folder_name)
        if meta is None:
            return False
        locales = meta.get("locales", {})
        if locale not in locales:
            return False
        locales[locale]["public"] = public
        self._save_document_metadata(folder_name)
        return True

    def set_document_categories(
        self, folder_name: str, categories: list[str]
    ) -> bool:
        """Replace the category list for a document.

        Returns ``True`` on success, ``False`` if document not found.
        """
        meta = self._documents.get(folder_name)
        if meta is None:
            return False
        meta["categories"] = categories
        self._save_document_metadata(folder_name)
        return True

    def add_document_translation(
        self, folder_name: str, locale: str, title: str, content: str
    ) -> bool:
        """Create a new locale entry (private by default) and write the .md file.

        Returns ``False`` if the document doesn't exist or the locale already exists.
        """
        meta = self._documents.get(folder_name)
        if meta is None:
            return False
        locales = meta.setdefault("locales", {})
        if locale in locales:
            return False
        now = datetime.now(timezone.utc).isoformat()
        locales[locale] = {
            "created": now,
            "modified_contents": now,
            "public": False,
        }
        titles = meta.setdefault("titles", {})
        titles[locale] = title
        md_path = self._dir / folder_name / f"{locale}.md"
        md_path.write_text(content, encoding="utf-8")
        self._save_document_metadata(folder_name)
        return True

    def remove_document_translation(self, folder_name: str, locale: str) -> bool:
        """Delete a locale entry, its .md file, and history backups.

        Returns ``False`` if the locale is the source locale or doesn't exist.
        """
        meta = self._documents.get(folder_name)
        if meta is None:
            return False
        if meta.get("source_locale") == locale:
            return False
        locales = meta.get("locales", {})
        if locale not in locales:
            return False
        del locales[locale]
        meta.get("titles", {}).pop(locale, None)
        md_path = self._dir / folder_name / f"{locale}.md"
        if md_path.exists():
            md_path.unlink()
        # Remove history backups for this locale
        history_dir = self._dir / folder_name / "_history"
        if history_dir.exists():
            for backup in history_dir.glob(f"{locale}_*.md"):
                backup.unlink()
        self._save_document_metadata(folder_name)
        return True

    def delete_document(self, folder_name: str) -> bool:
        """Remove a document folder from disk and from memory.

        Returns ``False`` if the document doesn't exist.
        """
        if folder_name not in self._documents:
            return False
        doc_dir = self._dir / folder_name
        if doc_dir.exists():
            shutil.rmtree(doc_dir)
        del self._documents[folder_name]
        return True

    def create_category(self, slug: str, name: str, locale: str) -> bool:
        """Create a new category.

        Returns ``False`` if the slug already exists.
        """
        if slug in self._categories:
            return False
        self._categories[slug] = {
            "sort": "alphabetical",
            "name": {locale: name},
        }
        self._save_root_metadata()
        return True

    # ------------------------------------------------------------------
    # Edit locks
    # ------------------------------------------------------------------

    def acquire_edit_lock(
        self, folder_name: str, locale: str, username: str
    ) -> str | None:
        """Attempt to acquire an edit lock.

        Returns ``None`` on success, or the locking username on failure.
        """
        self.cleanup_stale_locks()
        key = (folder_name, locale)
        existing = self._edit_locks.get(key)
        if existing and existing["user"] != username:
            return existing["user"]
        self._edit_locks[key] = {"user": username, "timestamp": time.time()}
        return None

    def release_edit_lock(
        self, folder_name: str, locale: str, username: str
    ) -> None:
        """Release an edit lock if held by *username*."""
        key = (folder_name, locale)
        existing = self._edit_locks.get(key)
        if existing and existing["user"] == username:
            del self._edit_locks[key]

    def cleanup_stale_locks(self, timeout_seconds: int = 1800) -> None:
        """Remove locks older than *timeout_seconds*."""
        now = time.time()
        stale = [
            key
            for key, lock in self._edit_locks.items()
            if now - lock["timestamp"] > timeout_seconds
        ]
        for key in stale:
            del self._edit_locks[key]

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------

    def _save_root_metadata(self) -> None:
        """Write categories to the root ``_metadata.json``."""
        path = self._dir / "_metadata.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"categories": self._categories}, f, indent=4, ensure_ascii=False)

    def _save_document_metadata(self, folder_name: str) -> None:
        """Write a document's ``_metadata.json``."""
        meta = self._documents.get(folder_name)
        if meta is None:
            return
        path = self._dir / folder_name / "_metadata.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=4, ensure_ascii=False)

    def _backup_version(self, folder_name: str, locale: str) -> None:
        """Copy the current ``.md`` to ``_history/`` and enforce version cap."""
        md_path = self._dir / folder_name / f"{locale}.md"
        if not md_path.exists():
            return

        history_dir = self._dir / folder_name / "_history"
        history_dir.mkdir(exist_ok=True)

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup_name = f"{locale}_{timestamp}.md"
        shutil.copy2(md_path, history_dir / backup_name)

        # Enforce per-locale cap
        backups = sorted(
            history_dir.glob(f"{locale}_*.md"),
            key=lambda p: p.name,
        )
        while len(backups) > _MAX_HISTORY_PER_LOCALE:
            oldest = backups.pop(0)
            oldest.unlink()
