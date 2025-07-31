import logging
from typing import Any, Dict, List, Optional

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.widgets import Footer, Header, Static
from textual.drivers.web_driver import WebDriver

from ldap_idp.lib_textual.comp_config import AppConfigLoaderMixin

from ldap_idp.config import settings

# Configure logging - only to file, not console
logging.basicConfig(
    level=logging.INFO, handlers=[], force=True  # No handlers = no console output
)
logger = logging.getLogger()


# ------------------------------------------------------------
# Main Sub App widget base class
# ------------------------------------------------------------

class WrappedAppBase(Container, AppConfigLoaderMixin):
    """Base class for all subapps widgets."""

    id = "app-wrapped-widget"
    DEFAULT_CLASSES = "subapp-widget"

    def __init__(self, *args, app_name: str = None, app_config: dict = None, **kwargs):
        self.app_name = app_name or None  # "NO NAME APP"
        self.app_config = app_config or {}

        logger.info("Loading %s app configuration", self)
        self.set_app_config(app_name=self.app_name, app_config=self.app_config)

        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        """Create child widgets for the main container."""
        logger.info("Composing main container widgets")

        msg = self.app_config.get("msg", f"{self.app_name} DEFAULT APP")
        yield Container(Static(msg, classes="hello-message"), classes="main-content")

# ------------------------------------------------------------
# Main Container
# ------------------------------------------------------------


class WrappedAppDefault(WrappedAppBase):
    """Main container compound widget for the app."""

    def compose(self) -> ComposeResult:
        """Create child widgets for the main container."""
        logger.info("Composing main container widgets")
        yield Container(
            Static("No widget app embedded :(", classes="hello-message"),
            classes="main-content",
        )


class AppWrapper(App):
    """A simple hello world application with header and footer."""

    TITLE = "LDAP Control Panel"

    BINDINGS = [
        Binding("ctrl+c", "quit_shell", "Quit", show=True),
    ]

    DEFAULT_LOG_FILE = "APP.log"


    # init
    # ---------------------------
    def __init__(
        self,
        app_class=WrappedAppDefault,
        app_title=None,
        app_subtitle="",
        log_file=DEFAULT_LOG_FILE,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.app_class = app_class
        self.title = app_title
        self.sub_title = app_subtitle
        self.active_subapp = None  # Track the active subapp

        # pprint(self.app_class)
        assert isinstance(
            self.app_class, type
        ), f"App class must be a class, not {type(self.app_class)}"
        assert issubclass(
            self.app_class, WrappedAppBase
        ), f"App class must be a subclass of WrappedAppBase, not {self.app_class.__name__}: {self.app_class.__mro__}"

        # Set up file logging only
        file_handler = logging.FileHandler(log_file, mode="a")
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)

        # Remove any existing handlers to avoid duplicates
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # Add only file handler
        root_logger.addHandler(file_handler)
        root_logger.setLevel(logging.INFO)
        logger.info(f"AppWrapper initialized. Logging to: {log_file}")



        # current_config = self.read_config()
        # self.set_config(current_config)

        # from pprint import pprint


        # ret = self.show_config()
        # pprint(ret)

        # assert False, ret

        # assert False, "WIPPP CONFIG"

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        logger.info("Composing app widgets")
        yield Header(id="app-header")
        yield Footer(id="app-footer")
        yield self.app_class(id="app-wrapped-widget")


    # Events
    # ---------------------------

    def on_mount(self) -> None:
        """Called when the app is mounted."""
        logger.info("App mounted successfully")

    def on_exit(self) -> None:
        """Called when the app is exiting."""
        logger.info("App exiting")


    # Helpers
    # ---------------------------

    def is_web_mode(self) -> bool:
        """Check if the application is running in web mode."""
        return isinstance(self.app._driver, WebDriver)

    def is_cli_mode(self) -> bool:
        """Check if the application is running in CLI mode."""
        return not self.is_web_mode()
    
    # Bindings
    # ---------------------------


    def action_quit_shell(self) -> None:
        """Quit the shell."""
        logger.info("Quitting application")

        if self.is_cli_mode():
            # We restore the usual exit behavior -- Does not work in embedded mode ?
            # self.action_quit()
            logger.info("App exiting")
            self.exit()

        # Implement press-papier/clipboard here
