import logging
from typing import Any, Dict

import yaml
from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.widgets import DataTable, Static, Markdown
from textual.widget import Widget
from textual.reactive import reactive
from textual.widgets import Pretty


from ldap_idp.ldap_backend import get_rdn

logger = logging.getLogger(__name__)


# =============================================================
# Header panel
# =============================================================


class HeaderView(Static):
    """Header for the app."""

    DEFAULT_CSS = """
    HeaderView {
        background: $background ;
    }
    """

    HEADER_TEMPLATE = """\
dn: {dn}    
rdn: {rdn}    
objectClass: {object_class}
"""

    current_ldap_entry: reactive[dict | None] = reactive(None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loading = False
        self.can_focus = False

    def on_mount(self):
        """Define default text for the header view."""

        self.update("Please select entry")

    def render(self) -> str:
        if self.current_ldap_entry:
            # Build data
            ldap_entry = self.current_ldap_entry
            dn = ldap_entry["dn"]
            object_class = ldap_entry["attributes"].get("objectClass")
            rdn = get_rdn(ldap_entry).split("=")[0]

            # Generate data
            payload = self.HEADER_TEMPLATE.format(
                dn=dn,
                object_class=", ".join(object_class),
                rdn=rdn,
            )
            self.styles.height = len(payload.split("\n")) - 1

            return payload

        self.styles.height = 1
        return "No entry selected"


# =============================================================
# Content panels
# =============================================================


class ContentViewBase(ScrollableContainer, can_focus=False):
    """Base class for content views."""

    current_ldap_entry: reactive[dict | None] = reactive(None)
    content_widget = None
    styles = None


class ContentViewJSON(ContentViewBase, can_focus=True):
    """Right pane for the app."""

    DEFAULT_CSS = """
    ContentViewJSON {
        border: solid $primary;
    }
    """

    BORDER_TITLE = "JSON view"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loading = False
        self.content_widget = None

    def compose(self) -> ComposeResult:
        """Create child widgets for the scrollable container."""
        self.content_widget = Pretty(self.current_ldap_entry, id="content-static")

        yield self.content_widget

    def watch_current_ldap_entry(self, ldap_entry):
        """Update the content view with LDAP entry information."""
        if self.content_widget and self.current_ldap_entry:
            self.content_widget.update(ldap_entry)


class ContentViewTable(ContentViewBase):
    """Right pane for the app displaying LDAP entries in table format."""

    DEFAULT_CSS = """
    ContentViewTable {
        border: solid $primary;
    }
    """

    BORDER_TITLE = "Table view"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loading = False
        self.content_widget = None
        self.current_sort_column = None
        self.current_sort_reverse = False

    def compose(self) -> ComposeResult:
        """Create child widgets for the scrollable container."""
        self.content_widget = DataTable(id="table-container")
        self.content_widget.can_focus = False
        # Add columns with proper names
        self.content_widget.add_columns("Attribute", "Values")
        yield self.content_widget

    def watch_current_ldap_entry(self, ldap_entry):
        """Update the content view with LDAP entry information."""

        logger.info(f"Updating ContentViewTable with entry data: {ldap_entry}")

        if ldap_entry and "dn" in ldap_entry:
            dn = ldap_entry["dn"]
            logger.info(f"Updating ContentViewTable with DN: {dn}")

            # Clear existing table and reset sorting
            self.content_widget.clear()
            self.current_sort_column = None
            self.current_sort_reverse = False

            # Add rows for each attribute
            longuest_value = 0
            if "attributes" in ldap_entry:
                for attr_name, attr_values in ldap_entry["attributes"].items():

                    if attr_name in ["objectClass"]:
                        # Skip since already displayed in header
                        continue

                    # Handle multiple values - create separate row for each value
                    if isinstance(attr_values, list):
                        for value in attr_values:
                            self.content_widget.add_row(attr_name, str(value))
                            longuest_value = (
                                longuest_value
                                if longuest_value > len(value)
                                else len(value)
                            )
                    else:
                        self.content_widget.add_row(attr_name, str(attr_values))
                        longuest_value = (
                            longuest_value
                            if longuest_value > len(attr_values)
                            else len(attr_values)
                        )

            logger.info(f"DEBUG: longuest_value={longuest_value}")
            self.content_widget.ordered_columns[1].content_width = longuest_value  # + 1

    def on_content_widget_header_selected(
        self, event: DataTable.HeaderSelected
    ) -> None:
        """Handle header click for sorting using built-in sort method."""
        column_key = event.column_key

        # Toggle sort direction if same column, otherwise start ascending
        if self.current_sort_column == column_key:
            self.current_sort_reverse = not self.current_sort_reverse
        else:
            self.current_sort_column = column_key
            self.current_sort_reverse = False

        # Use built-in sort method
        self.content_widget.sort(column_key, reverse=self.current_sort_reverse)
