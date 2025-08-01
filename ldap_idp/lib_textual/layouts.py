# from ldap_idp.poc_multiapps.app_lib import AppWrapper, WrappedAppBase
# from ldap_idp.textual_multiapp import AppWrapper, WrappedAppBase

import logging

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static

logger = logging.getLogger(__name__)


# UI1 layout
# +------+ +---------------+
# |      | |               |
# |      | +---------------+
# |      | +---------------+
# |      | |               |
# |      | |               |
# |      | |               |
# |      | |               |
# |      | |               |
# +------+ +---------------+


class LayoutContainer(Container):
    """Generic layout container that can compose different layouts based on layout_config."""

    DEFAULT_CSS = """
    # LayoutContainer {
    #     border: solid purple;
    # }
    
    .left-pane {
        border-right: heavy $background;
        width: 30%;
        max-width: 50;
    }
    
    # .right-pane {
    #     border: solid green;
    # }
    
    # .tree-container {
    #     border: solid orange;
    # }
    
    .header-container {
        height: auto;
        max-height: 10;
    }
    
    # .content-container {
    #     # border: solid red;
    # }
    
    .split-view {
        height: 100%;
    }
    
    .content-view {
        height: 100%;
    }
    """

    def __init__(self, layout_config=None, *args, **kwargs):
        self.layout_config = layout_config or {}
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        """Create child widgets based on layout type and config."""
        yield from self._compose_ui1()

    def _compose_ui1(self) -> ComposeResult:
        """Compose UI1 layout: left pane + right pane."""

        # Left pane with tree view
        left_pane = Container(
            Vertical(
                Container(
                    self.layout_config.get("menu", Static("Tree view menu")),
                    classes="tree-container",
                    id="tree_container",
                ),
            ),
            classes="left-pane",
        )

        # Right pane with content
        right_pane = Container(
            Vertical(
                Container(
                    self.layout_config.get("header", Static("Header")),
                    classes="header-container",
                ),
                Container(
                    self.layout_config.get("content", Static("Content")),
                    classes="content-container",
                ),
                classes="content-view",
            ),
            classes="right-pane",
        )

        yield Horizontal(left_pane, right_pane, classes="split-view")


# Legacy alias for backward compatibility
LayoutUI1 = LayoutContainer
