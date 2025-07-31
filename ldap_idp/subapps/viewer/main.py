#!/usr/bin/env python3
"""
LDAP Viewer
"""

import logging
from typing import Any, Dict
from types import SimpleNamespace

import ldap

from textual.app import ComposeResult
from textual.binding import Binding
from textual.widgets import ContentSwitcher
from textual import work
from textual.reactive import reactive

from ldap_idp.lib_textual.decorators import message, action, watch
from ldap_idp.ldap_backend import LDAPConfig, LDAPConnectionImproved
from ldap_idp.lib_textual.app_base import AppWrapper, WrappedAppBase
from ldap_idp.lib_textual.comp_store import AppStoreServerMixin
from ldap_idp.lib_textual.layouts import LayoutUI1
from ldap_idp.subapps.viewer.app_menu import TreeView
from ldap_idp.subapps.viewer.app_content import (
    ContentViewJSON,
    ContentViewTable,
    ContentViewBase,
    HeaderView,
    # ContentViewBeta,
)
from ldap_idp.config import settings

logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)


# =============================================================
# Content panel wrapper
# =============================================================

VIEWS = {
    # "view-default": ContentViewBase,
    # "view-table": ContentViewTable,
    "view-default": ContentViewTable,
    "view-json": ContentViewJSON,
    # "view-default": ContentViewBeta,
}


class ContentView(ContentSwitcher):
    """Right pane for the app."""

    views = []

    id = "subapp-content-view"

    def compose(self) -> ComposeResult:
        """Create child widgets for the right pane."""

        self.display = False
        self.views = list(VIEWS.keys())

        for view_id, view_class in VIEWS.items():
            yield view_class(id=view_id, classes="widget-ldap-entry")

    def get_active_view(self):
        """Return current active view"""
        ret = self.query_one(f"#{self.current}")
        return ret


# =============================================================
# Main App
# =============================================================


class SubAppViewerMixin:
    """Main container compound widget for the app."""

    current_ldap_connection = reactive(None)
    # current_ldap_entry = reactive(None)
    current_rule_entry = reactive(None)

    @work
    async def load_ldap_session(self) -> None:
        """Load data from the server."""

        ldap_uri = settings.authldap.uri
        # filter_config = {
        #     "oc_silented": settings.viewer.oc_silented,
        #     "oc_order": settings.viewer.oc_order,
        #     "attr_silented": settings.viewer.attr_silented,
        #     "attr_order": settings.viewer.attr_order,
        # }

        logger.info("Starting LDAP connection on %s", ldap_uri)
        ldap_connection = LDAPConnectionImproved(
            self.ldap_config,
            # filter_config
            )

        # Try to connect to LDAP server
        try:
            ldap_connection.connect()
        except ldap.SERVER_DOWN as err:
            logger.error("Error connecting to LDAP server: %s: %s", type(err.args), err.args)
            err = SimpleNamespace(**err.args[0])
            self.notify(f"{err.desc}: {err.info} ({err.errno})")
            return
        except Exception as err:
            logger.error("Error connecting to LDAP server: %s: %s", type(err), err)
            self.notify(f"Error connecting to LDAP server {ldap_uri}: {err}")
            return

        # If connected, let's continue
        self.current_ldap_connection = ldap_connection

        logger.info("LDAP session connected")
        # self.notify(f"Connected to remote LDAP server: {ldap_uri}")

    # Watchers handlers
    # =============================================================

    @watch("current_ldap_connection")
    def watch_current_ldap_connection33333(self, value):
        "Update UI when current LDAP connection changes"

        # Update sub elements
        self.query_one("TreeView").current_ldap_connection = value

    @watch("current_rule_entry")
    def watch_current_rule_entry444(self, rule_entry):
        "Update UI when current rule entry changes"

        # Update sub elements
        self.query_one("HeaderView").current_rule_entry = rule_entry
        active_view = self.query_one("ContentView").get_active_view()
        active_view.current_rule_entry = rule_entry
        active_view.current_ldap_connection = self.current_ldap_connection



    # Event handlers
    # =============================================================

    @message(TreeView.LdapEntrySelection)
    def on_tree_view_ldap_entry_selection22(
        self, msg: TreeView.LdapEntrySelection
    ) -> None:
        """Handle rule entry selection message from tree widget."""

        # # Ensure context is ready
        # if not self.current_ldap_connection:
        #     self.notify("No LDAP connection available")
        #     return

        rule_entry = None
        if isinstance(msg.node_data, dict) and "label" in msg.node_data:
            rule_entry = msg.node_data
            self.query_one(ContentSwitcher).display = True
        else:
            self.query_one(ContentSwitcher).display = False

        self.current_rule_entry = rule_entry


    @action("cycle_views")
    def action_cycle_views222(self) -> None:
        """Action triggered when 't' key is pressed."""
        logger.info("Test notification triggered by 't' key")

        # Cycle between ContentSwitcher views
        content_switcher = self.query_one(ContentSwitcher)
        current_view = content_switcher.current
        views = content_switcher.views

        current_index = views.index(current_view) if current_view in views else 0
        next_index = (current_index + 1) % len(views)
        content_switcher.current = views[next_index]

        # Refresh content switcher
        self.query_one("ContentView").get_active_view().current_rule_entry = (
            self.current_rule_entry
        )

        # Notify user
        logger.info(f"Switched from {current_view} to {views[next_index]}")

        self.refresh_bindings()


class SubAppWidget(WrappedAppBase, SubAppViewerMixin, AppStoreServerMixin):
    """Main container compound widget for the app."""

    DEFAULT_ID = "subapp-viewer"

    # Key bindings
    BINDINGS = [
        Binding("v", "cycle_views", "Cycle views"),
    ]

    id = "app-viewer"

    def __init__(self, *args, **kwargs):
        self.app_config = None
        self.ldap_config = None
        super().__init__(*args, **kwargs)



    def compose(self) -> ComposeResult:
        """Create child widgets for the main container."""

        new_conf = {
            "uri": settings.authldap.uri,
            "bind_dn": settings.authldap.bind_dn,
            "bind_password": settings.authldap.bind_pass,
            "base_dn": settings.authldap.base_dn,
        }
        self.ldap_config = LDAPConfig(**new_conf)

        initial_view = f"view-{settings.viewer.default_view}"
        assert initial_view in VIEWS, f"Invalid initial view: {initial_view}, available views: {VIEWS.keys()}"

        # Build UI
        logger.info("Composing main container widgets")

        # Create widgets
        tree_view = TreeView(
            "LDAP Viewer",
            containers_first=settings.browser.containers_first,
            classes="widget-ldap-selector",
            id="viewer-tree-view",
        )
        content_view = ContentView(initial=initial_view)
        header_view = HeaderView(classes="widget-ldap-entry")

        # Build layout
        yield LayoutUI1(
            layout_config={
                "menu": tree_view,
                "content": content_view,
                "header": header_view,
            },
        )

    def on_mount(self) -> None:
        """Ensure ldap widgets can load data"""
        self.load_ldap_session()


# Single app support
# =============================================================

from pprint import pprint

# For autonomous app
def main():
    """Main entry point for the application."""
    logger.info("Starting Viewer")



    pprint(settings)




    # print("YEAAHHHHHHHHH")
    # print(dir(settings))
    # print(settings.__dict__)



    # assert False, "TOFIX: settings.viewer_entities"


    app = AppWrapper(
        app_title="LDAP Viewer",
        app_class=SubAppWidget,
    )
    app.run()


if __name__ == "__main__":
    main()
