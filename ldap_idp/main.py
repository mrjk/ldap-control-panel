#!/usr/bin/env python3
"""
Simple Textual CLI App - Hello World
A demonstration of a basic textual application with header and footer.
"""

# pylint: disable=logging-fstring-interpolation


import logging
from pprint import pprint

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.widget import Widget
from textual.widgets import (
    Footer,
    Header,
    Label,
    Markdown,
    Static,
    TabbedContent,
    TabPane,
)

from ldap_idp.lib_textual.app_base import AppWrapper, WrappedAppBase

# Configure logging - only to file, not console
logging.basicConfig(
    level=logging.INFO, handlers=[], force=True  # No handlers = no console output
)
logger = logging.getLogger(__name__)


# Real apps
from ldap_idp.subapps.browser.main import SubAppWidget as BrowserApp
from ldap_idp.subapps.viewer.main import SubAppWidget as ViewerApp

# Demo Apps
#from ldap_idp.subapps.hello.main import SubAppWidget as HelloApp

# APP_LIST = [
#     HelloApp(app_name="App 1", message_content="First App! 🌍", variant="green"),
#     HelloApp(app_name="Second App", message_content="Second App! 🌍", variant="blue"),
#     HelloApp(app_name="3eme app", message_content="Yep am the third", variant="red"),
#     HelloApp,
#     HelloApp(app_name="Last app", message_content="Fourth App! 🌍", variant="yellow"),
# ]


APP_LIST = [
    BrowserApp(app_name="Browser"),
    ViewerApp(app_name="Viewer"),
    # HelloApp(app_name="Second App", message_content="Second App! 🌍", variant="blue"),
]


class CustomTabbedContent(TabbedContent):
    """Custom TabbedContent with down arrow binding to move focus to next element."""
    
    BINDINGS = [
        Binding("down", "next_focus", "Next Focus", show=False),
    ]
    
    def action_next_focus(self) -> None:
        """Move focus to the next focusable element."""
        self.screen.focus_next()


class BigApp(WrappedAppBase):
    """Main container compound widget for the app."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set direct styles using keyword arguments
        self.set_styles(height="100%", align=("center", "middle"))
        self.active_subapp = None
        self.subapp_widgets = []
        self.active_bindings = []

    def compose(self) -> ComposeResult:
        """Create child widgets for the main container."""
        logger.info("Composing main container widgets")

        # Select mode
        MODE = "vertical"
        MODE = "horizontal"
        MODE = "tabbed"

        if MODE == "tabbed":
            first_app = None
            with CustomTabbedContent(id="main-tabbed-content") as tabbed_content:
                idx = 0

                for app_cls in APP_LIST:
                    app = app_cls
                    if isinstance(app_cls, type):
                        # Autocreate instance if not already done
                        logger.info(f"Auto-creating instance of {app_cls}")
                        app = app_cls(app_name=f"Instance {idx}", id=app_cls.DEFAULT_ID)

                    assert isinstance(
                        app.app_name, str
                    ), f"App must have a name, not {type(app.app_name)}: {app.app_name}"

                    # Class must now have a preset ID
                    with TabPane(app.app_name, classes="main-tabbed-content-pane"):
                        self.subapp_widgets.append(app)
                        yield app

                    if idx == 0:
                        self.active_subapp = app

                    idx += 1

        else:
            apps = []
            for idx, app_cls in enumerate(APP_LIST):
                app = app_cls
                if isinstance(app_cls, type):
                    # Autocreate instance if not already done
                    logger.info(f"Auto-creating instance of {app_cls}")
                    app = app_cls(app_name=f"Instance {idx}")
                apps.append(app)

            cls = Horizontal
            if MODE == "vertical":
                cls = Vertical

            # Assemble horizontally or vertically
            yield cls(*apps, classes="main-content")

    # def render(self, *args, **kwargs):
    #     """Render the app."""
    #     logger.info(f"Rendering app with {len(self.subapp_widgets)} subapps")

    #     # if len(self.subapp_widgets) > 0:
    #     #     self.active_subapp = self.subapp_widgets[0]
    #     #     self.update_footer_with_bindings(self.active_subapp)
    #     super().render(*args, **kwargs)

    def on_tabbed_content_tab_activated(
        self, event: TabbedContent.TabActivated
    ) -> None:
        """Handle tab activation and update footer with active subapp's bindings."""
        logger.info(f"Tab activated: {event.tab.id}")

        # Find the active subapp widget
        active_tab_id = event.tab.id
        active_subapp = None

        # Extract the subapp index from the tab ID
        # Tab ID format is "--content-tab-subapp-{index}"
        if "--content-tab-subapp-" in active_tab_id:
            try:
                index_str = active_tab_id.split("--content-tab-subapp-")[1]
                index = int(index_str)
                if 0 <= index < len(self.subapp_widgets):
                    active_subapp = self.subapp_widgets[index]
                    logger.info(f"Active subapp: {active_subapp.app_name}")
                    self.active_subapp = active_subapp
                    self.update_footer_with_bindings(active_subapp)
                else:
                    logger.warning(
                        f"Tab index {index} out of range for {len(self.subapp_widgets)} subapps"
                    )
            except (ValueError, IndexError) as e:
                logger.warning(f"Could not parse tab index from {active_tab_id}: {e}")
        else:
            logger.warning(f"Unexpected tab ID format: {active_tab_id}")

    def on_mount(self) -> None:
        """Called when the widget is mounted."""
        logger.info("BigApp mounted")
        # Set initial active subapp to the first one if available
        if self.subapp_widgets and self.active_subapp:
            self.update_footer_with_bindings(self.active_subapp)
            logger.info(f"Initial active subapp set to: {self.active_subapp.app_name}")
        elif self.subapp_widgets:
            # Fallback: set the first subapp as active
            self.active_subapp = self.subapp_widgets[0]
            self.update_footer_with_bindings(self.active_subapp)
            logger.info(f"Initial active subapp set to: {self.active_subapp.app_name}")

    def update_footer_with_bindings(self, subapp_widget) -> None:
        """Update the footer with the active subapp's bindings."""
        logger.info(f"Updating footer with bindings from {subapp_widget.app_name}")

        # Get bindings from the subapp widget
        bindings = []
        if hasattr(subapp_widget, "BINDINGS"):
            bindings = subapp_widget.BINDINGS
        elif hasattr(subapp_widget.__class__, "BINDINGS"):
            bindings = subapp_widget.__class__.BINDINGS

        logger.info(f"Found {len(bindings)} bindings for {subapp_widget.app_name}")

        # Store the active bindings
        self.active_bindings = bindings

        # Refresh the app's bindings to update the footer
        app = self.app
        if app:
            # Use call_later to ensure the app is fully ready
            app.call_later(self._refresh_bindings_delayed)
            logger.info(
                f"Scheduled binding refresh with {len(bindings)} bindings from {subapp_widget.app_name}"
            )

    def _refresh_bindings_delayed(self) -> None:
        """Refresh bindings after a short delay to ensure app is ready."""
        app = self.app
        if app:
            app.refresh_bindings()
            logger.info("Delayed binding refresh completed")

    def get_bindings(self):
        """Return the active subapp's bindings."""
        if self.active_bindings:
            return self.active_bindings
        return super().get_bindings()


def main():
    """Main entry point for the application."""
    logger.info("Starting Hello World CLI App")
    app = AppWrapper(
        app_title="LDAP Control Panel",
        app_class=BigApp,
    )
    app.run()


if __name__ == "__main__":
    main()
