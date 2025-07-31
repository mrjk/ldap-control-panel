#!/usr/bin/env python3
"""
LDAP Browser
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

from ldap_idp.ldap_backend import LDAPConfig, LDAPConnectionImproved
from ldap_idp.lib_textual.app_base import AppWrapper, WrappedAppBase
from ldap_idp.lib_textual.layouts import LayoutUI1
from ldap_idp.subapps.browser.app_menu import TreeView
from ldap_idp.subapps.browser.app_content import (
    ContentViewJSON,
    ContentViewTable,
    HeaderView,
)
from ldap_idp.config import settings

logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)


# =============================================================
# Content panel wrapper
# =============================================================

VIEWS = {
    "view-table": ContentViewTable,
    "view-json": ContentViewJSON,
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

class SubAppBrowserMixin:
    """Main container compound widget for the app."""

    current_ldap_connection = reactive(None)
    current_ldap_entry = reactive(None)

    @work
    async def load_ldap_session(self) -> None:
        """Load data from the server."""

        ldap_uri = settings.authldap.uri
        filter_config = {
            "oc_silented": settings.browser.oc_silented,
            "oc_order": settings.browser.oc_order,
            "attr_silented": settings.browser.attr_silented,
            "attr_order": settings.browser.attr_order,
        }

        logger.info("Starting LDAP connection on %s", ldap_uri)
        ldap_connection = LDAPConnectionImproved(
            self.ldap_config, filter_config=filter_config)

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

    def watch_current_ldap_connection(self, value):
        "Update UI when current LDAP connection changes"

        # Update sub elements
        self.query_one("TreeView").current_ldap_connection = value

    def watch_current_ldap_entry(self, ldap_entry):
        "Update UI when current LDAP entry changes"

        # Update sub elements
        self.query_one("HeaderView").current_ldap_entry = ldap_entry
        self.query_one("ContentView").get_active_view().current_ldap_entry = ldap_entry

    # Event handlers
    # =============================================================

    def on_tree_view_ldap_entry_selection(
        self, message: TreeView.LdapEntrySelection
    ) -> None:
        """Handle LDAP entry selection message from tree widget."""
        logger.info("LDAP entry selection message received")

        # Ensure context is ready
        if not self.current_ldap_connection:
            self.notify("No LDAP connection available")
            return

        # ldap_entry = message.node_data
        ldap_entry = None
        if isinstance(message.node_data, dict) and "dn" in message.node_data:

            # Fetch LDAP entry
            dn = message.node_data["dn"]
            ldap_entry = self.current_ldap_connection.get_ldap_entry(dn)
            logger.info("LDAP entry: %s", ldap_entry)

            self.query_one(ContentSwitcher).display = True
        else:
            self.query_one(ContentSwitcher).display = False

        self.current_ldap_entry = ldap_entry

    def action_cycle_views(self) -> None:
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
        self.query_one("ContentView").get_active_view().current_ldap_entry = (
            self.current_ldap_entry
        )

        # Notify user
        logger.info(f"Switched from {current_view} to {views[next_index]}")

        self.refresh_bindings()


class SubAppWidget(WrappedAppBase, SubAppBrowserMixin):
    """Main container compound widget for the app."""

    DEFAULT_ID = "subapp-browser"

    # Key bindings
    BINDINGS = [
        Binding("v", "cycle_views", "Cycle views"),
    ]

    id = "app-browser"

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

        initial_view = f"view-{settings.browser.default_view}"
        assert initial_view in VIEWS, f"Invalid initial view: {initial_view}, available views: {VIEWS.keys()}"

        # Build UI
        logger.info("Composing main container widgets")

        # Create widgets
        tree_view = TreeView(
            "LDAP Server",
            classes="widget-ldap-selector",
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


# For autonomous app
def main():
    """Main entry point for the application."""
    logger.info("Starting Browser")
    app = AppWrapper(
        app_title="LDAP Browser",
        app_class=SubAppWidget,
    )
    app.run()


if __name__ == "__main__":
    main()
