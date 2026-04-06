"""
Selection management for wxPython tree controls.

Provides a mixin and ready-to-use control that automatically manages selection
state for tree controls:
- Auto-focus first item when control gains focus with no selection
- Helper to maintain valid selection after item deletion

Includes:
- TreeSelectionManagerMixin: For wx.TreeCtrl-style controls
- ManagedTreeCtrl: Ready-to-use tree with selection management

Requires: wxPython
"""

from __future__ import annotations

from typing import Any

import wx

from .list_selection import FocusAfterDelete


# =============================================================================
# MIXIN
# =============================================================================


class TreeSelectionManagerMixin:
    """
    Mixin that manages selection for wx.TreeCtrl-style controls.

    Features:
    - Auto-selects first visible item when focused with no selection
    - Provides select_after_delete() to maintain valid selection after removal

    Args:
        focus_after_delete: Where to focus after deleting an item.
            FocusAfterDelete.PREVIOUS (default) or FocusAfterDelete.NEXT
    """

    def __init__(
        self,
        *args: Any,
        focus_after_delete: FocusAfterDelete = FocusAfterDelete.PREVIOUS,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.focus_after_delete = focus_after_delete
        self.Bind(wx.EVT_SET_FOCUS, self._on_tree_focus_ensure_selection)

    def _on_tree_focus_ensure_selection(self, evt: wx.FocusEvent) -> None:
        """Auto-select first visible item when tree gains focus with no selection."""
        evt.Skip()
        sel = self.GetSelection()
        if sel.IsOk():
            return
        root = self.GetRootItem()
        if not root.IsOk():
            return
        first_child, _ = self.GetFirstChild(root)
        if first_child.IsOk():
            self.SelectItem(first_child)

    def select_after_delete(
        self,
        parent: wx.TreeItemId,
        prev_sibling: wx.TreeItemId | None,
        next_sibling: wx.TreeItemId | None,
    ) -> None:
        """Select an appropriate item after deletion.

        Call this AFTER deleting a tree item to move selection to the
        previous sibling, next sibling, or parent -- in order of preference
        based on the focus_after_delete setting.

        Args:
            parent: Parent of the deleted item.
            prev_sibling: Sibling before the deleted item, or None.
            next_sibling: Sibling after the deleted item, or None.
        """
        if self.focus_after_delete == FocusAfterDelete.PREVIOUS:
            primary, fallback = prev_sibling, next_sibling
        else:
            primary, fallback = next_sibling, prev_sibling

        target = None
        if primary and primary.IsOk():
            target = primary
        elif fallback and fallback.IsOk():
            target = fallback
        elif parent and parent.IsOk() and parent != self.GetRootItem():
            target = parent

        if target:
            self.SelectItem(target)


# =============================================================================
# READY-TO-USE CONTROL
# =============================================================================


class ManagedTreeCtrl(TreeSelectionManagerMixin, wx.TreeCtrl):
    """A wx.TreeCtrl with automatic selection management."""

    pass
