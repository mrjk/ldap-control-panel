import logging
from typing import Any, Dict

from textual.message import Message
from textual.widgets import Tree
from textual.reactive import reactive

from ldap_idp.config import settings
from ldap_idp.lib_textual.wid_tree import TreeDataDir

logger = logging.getLogger(__name__)

# =============================================================
# Menu panel
# =============================================================


# List helpers
# def first(lst):
#     """Return the first element of a list"""
#     return lst[0] if lst else None


# def last(lst):
#     """Return the last element of a list"""
#     return lst[-1] if lst else None


# def head(lst, n=1):
#     """Return the first n elements of a list"""
#     return lst[:-n] if lst else []


# def tail(lst, n=1):
#     """Return the last n elements of a list"""
#     return lst[n:] if lst else []


class TreeView(TreeDataDir):
    """Left pane for the app.

    This widget demonstrates how to access other widgets using the app_widgets approach:
    - Parent SubAppWidget registers widgets in app_widgets dict
    - Child widgets can access other widgets via get_parent_app_widgets()
    - This avoids the need to use query() to find widgets
    """

    DEFAULT_CSS = """
    TreeView {
        # border: solid orange;
        height: 100%;
    }
    """

    current_ldap_connection = reactive(None)

    class LdapEntrySelection(Message):
        """Message sent when an LDAP entry is selected in the tree."""

        def __init__(self, node_data: dict):
            self.node_data = node_data
            super().__init__()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.containers_first = settings.browser.containers_first
        self.display_mode = settings.browser.display_mode
        self.auto_expand = settings.browser.auto_expand

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        """Handle tree node selection and send message to parent."""
        node = event.node
        node_data = node.data

        logger.info("Tree node selected: %s", node_data)
        self.post_message(self.LdapEntrySelection(node_data=node_data))

    def watch_current_ldap_connection(self, ldap_connection):
        "Update UI when current LDAP connection changes"

        if not ldap_connection:
            logger.error("No LDAP connection available")
            self.clear()
            return

        # Get the LDAP tree data recursively
        tree_data = ldap_connection.get_tree_recursive(max_depth=3, display_mode=self.display_mode)

        # Clear existing tree content
        self.clear()

        if "error" in tree_data["root"]:
            # Handle error case
            error_node = self.root.add(f"❌ Error: {tree_data['root']['error']}")
            error_node.expand_all()
            return

        # Build the tree from LDAP data recursively
        root_data = tree_data["root"]

        # Set root label
        self.root.label = root_data["label"]

        # Recursively build the tree structure
        self._build_tree_recursive(
            self.root,
            root_data["children"],
            containers_first=self.containers_first,
            depth=1,
        )

        # Expand root to show children
        if self.auto_expand:
            self.root.expand_all()
        else:
            self.root.expand()

        logger.info("Recursive tree updated")
        self.focus()

    def _build_tree_recursive(
        self, parent_node, children_data, containers_first=False, depth=0
    ):
        """Recursively build tree nodes from LDAP data."""
        if not children_data:
            return

        # Sort children if containers_first is enabled
        sorted_children = children_data
        if containers_first:
            # Separate containers (with children) and leaves (without children)
            containers = []
            leaves = []

            for child_data in children_data:
                if child_data["has_children"]:
                    containers.append(child_data)
                else:
                    leaves.append(child_data)

            # Sort each group alphabetically by label
            containers.sort(key=lambda x: x["label"].lower())
            leaves.sort(key=lambda x: x["label"].lower())

            # Combine: containers first, then leaves
            sorted_children = containers + leaves
            logger.debug(
                "Sorted %d containers and %d leaves", len(containers), len(leaves)
            )

        # Add children recursively
        for child_data in sorted_children:
            # Store DN and attributes in node data for future reference
            node_data = {
                "dn": child_data["dn"],
                "attributes": child_data["attributes"],
                "has_children": child_data["has_children"],
                "depth": depth,
            }

            if child_data["has_children"]:
                # Entry has children - add as expandable node
                child_node = parent_node.add(child_data["label"])
                child_node.data = node_data

                # Recursively add children if they exist
                if child_data.get("children"):
                    self._build_tree_recursive(
                        child_node, child_data["children"], containers_first, depth + 1
                    )
            else:
                # Entry has no children - add as leaf
                child_node = parent_node.add_leaf(child_data["label"])
                child_node.data = node_data
