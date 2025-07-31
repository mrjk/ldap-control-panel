import logging
from typing import Any, Dict

from textual.message import Message
from textual.widgets import Tree
from textual.reactive import reactive

from ldap_idp.config import settings
from ldap_idp.lib_textual.comp_config import AppConfigMixin
from ldap_idp.lib_textual.wid_tree import TreeDataDir

logger = logging.getLogger(__name__)

# =============================================================
# Menu panel
# =============================================================


class TreeView(TreeDataDir, AppConfigMixin):
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

    def __init__(self, *args, containers_first: bool = False, **kwargs):
        super().__init__(*args, **kwargs)
        self.containers_first = containers_first
        self.display_mode = "full"
        self.auto_expand = True

        self.read_config()

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        """Handle tree node selection and send message to parent."""
        node = event.node
        node_data = node.data

        # logger.info("Tree node selected: %s", node_data)
        self.post_message(self.LdapEntrySelection(node_data=node_data))


    def read_config(self):
        """Build the tree recursively."""
        
        parent_node = self.root
        entities = settings.viewer_entities

        for entity_name, ent_conf in entities.items():
            icon = ent_conf.icon or "💾"
            entity_data = {
                "label": f"{icon} {entity_name}",
                "children": list(ent_conf.keys()),
                "config": ent_conf,
                "type": "entity",

                "ldap_filter": ent_conf.get('ldap_filter',None),

            }

            # Entry has children - add as expandable node
            entity_node = parent_node.add(entity_data["label"])
            entity_node.data = entity_data

            # Add rules
            profiles = ent_conf.profiles.to_dict()
            for rule_name, rule_conf in profiles.items():
                rule_data = {
                    "label": rule_name,
                    "config": rule_conf,
                    "type": "profile",

                    "ldap_filter": rule_conf.get('ldap_filter',None),
                }
                rule_data.update(rule_conf)
                
                rule_node = entity_node.add_leaf(rule_data["label"])
                rule_node.data = rule_data


        # Make the widget first on update
        # self.focus()
        parent_node.expand_all()

