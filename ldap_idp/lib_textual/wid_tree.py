import logging

from textual.widgets import Tree
from textual.binding import Binding
from textual import events

logger = logging.getLogger(__name__)


class TreeDataDir(Tree):
    """Enhanced Tree widget with improved keyboard navigation.

    This subclass of Tree provides:
    - Simplified keyboard bindings focused on left/right navigation
    - Left arrow collapses current node or moves to parent
    - Right arrow expands current node or moves to first child
    - Removes default Tree bindings that could conflict with navigation
    """

    # Only include the bindings you want to keep
    BINDINGS = [
        # Binding(
        #     "shift+left",
        #     # "cursor_parent",
        #     "disabled",
        #     "Cursor to parent",
        #     show=False,
        # ),
        # Binding(
        #     "shift+right",
        #     # "cursor_parent_next_sibling",
        #     # "shift_right",
        #     "disabled",
        #     "Cursor to next ancestor",
        #     show=False,
        # ),
        # Binding(
        #     "shift+up",
        #     "disabled",
        #     # "cursor_previous_sibling2",
        #     "Cursor to previous sibling",
        #     show=False,
        # ),
        # Binding(
        #     "shift+down",
        #     "disabled",
        #     # "cursor_next_sibling",
        #     "Cursor to next sibling",
        #     show=False,
        # ),
        # Binding("enter", "select_cursor", "Select", show=False),
        # Binding("space", "toggle_node", "Toggle", show=False),
        # Binding(
        #     "shift+space",
        #     "toggle_expand_all",
        #     "Expand or collapse all",
        #     show=False,
        # ),
        # Binding("up", "disabled", "Cursor Up", show=False),
        # Binding(
        #     "down", "disabled", "Cursor Down", show=False
        # ),
        Binding("right", "move_right", "Toggle node", show=False),
        Binding("left", "move_left", "Go up", show=False),
        # Binding("up", "cursor_up", "Cursor Up", show=False),
        # Binding(
        #     "down", "cursor_down", "Cursor Down", show=False
        # ),
        Binding("up", "move_up", "Cursor Up", show=False),
        Binding("down", "move_down", "Cursor Down", show=False),
    ]

    # Number of spaces/characters to indent each tree level
    TREE_SHIFT_SIZE = 4

    # Base indentation offset for the first level
    TREE_SHIFT_OFFSET = 4

    # Override methods to disable unwanted actions
    def action_disabled(self) -> None:
        """Disable existing actions navigation"""
        pass

    def on_click(self, event: events.Click) -> None:
        "Handle better mouse support"

        if event.style.meta:
            node = self.get_node_at_line(event.style.meta["line"])
            if node is not None:
                if node.data:
                    # TOFIX:
                    node_depth = node.data.get("depth", 1) or 1
                    toggle_section = (
                        node_depth * self.TREE_SHIFT_SIZE + self.TREE_SHIFT_OFFSET
                    )

                    if event.x >= toggle_section:
                        node.toggle()

    def action_move_right(self) -> None:
        """Toggle the expanded state of the target node."""
        try:
            line = self._tree_lines[self.cursor_line]
        except IndexError:
            pass
        else:
            node = line.path[-1]

            if node.allow_expand:
                if not node.is_expanded:
                    node.expand()

    def action_move_left(self) -> None:
        """Toggle the expanded state of the target node."""
        try:
            line = self._tree_lines[self.cursor_line]
        except IndexError:
            pass
        else:
            node = line.path[-1]

            if node.allow_expand:
                if node.is_expanded:
                    node.collapse()

    def action_move_down(self) -> None:
        """Move down in the tree."""
        self.action_cursor_down()

        try:
            line = self._tree_lines[self.cursor_line]
        except IndexError:
            pass
        else:
            node = line.path[-1]
            payload = Tree.NodeSelected(node)
            self.on_tree_node_selected(payload)

    def action_move_up(self) -> None:
        """Move up in the tree."""
        self.action_cursor_up()

        try:
            line = self._tree_lines[self.cursor_line]
        except IndexError:
            pass
        else:
            node = line.path[-1]
            payload = Tree.NodeSelected(node)
            self.on_tree_node_selected(payload)

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        """Handle tree node selection and send message to parent."""
        node = event.node
        node_data = node.data
        logger.info("Tree node selected: %s", node_data)
