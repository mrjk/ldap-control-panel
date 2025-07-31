import logging
from types import SimpleNamespace
from typing import Any, Dict


from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.widgets import DataTable, Static, Markdown
from textual.widget import Widget
from textual.reactive import reactive
from textual.widgets import Pretty
from textual import work

from ldap_idp.lib_textual.decorators import message, action, watch
from ldap_idp.ldap_backend import get_rdn, SCOPE_SUBTREE
from ldap_idp.config import settings

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

    HEADER_TEMPLATE_PROFILE = """\
Profile: {data.label}    
Desc: {data.desc}    
Pattern: {data.pattern}
Attributes: {data.attr}    
"""

    HEADER_TEMPLATE_ENTITY = """\
Entity: {data.icon} {data.name}    
Desc: {data.desc}    
Pattern: {data.pattern}    
Children: {data.children}
"""

    current_rule_entry: reactive[dict | None] = reactive(None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loading = False
        self.can_focus = False

    def on_mount(self):
        """Define default text for the header view."""

        self.update("Please select entry")

    def render(self) -> str:
        rule_entry = self.current_rule_entry

        ret = None
        if not rule_entry:
            self.styles.height = 1
            return "No entry selected"
        elif rule_entry.get("type") == "profile":
            ret = self._render_profile(rule_entry)
        elif rule_entry.get("type") == "entity":
            ret = self._render_entity(rule_entry)
        else:
            ret = "Please select entry"
    
        return ret


    def _render_profile(self, rule_entry):
        """Render the profile header."""

        deff = {
            "label": "",
            "desc": "",
            "pattern": "",
            "attr": "",
        }
        deff.update(rule_entry)

        # Generate data
        payload = self.HEADER_TEMPLATE_PROFILE.format(
            data=SimpleNamespace(**deff),
            # object_class=", ".join(object_class),
            # rdn=rdn,
        )
        self.styles.height = len(payload.split("\n")) - 1

        return payload

    def _render_entity(self, rule_entry):
        """Render the entity header."""

        deff = {
            "name": "<NO NAME>",
            "desc": "",
            "pattern": "",
            # "attr": "",
            "icon": "💾",
            "children": [],
            "profiles": {},
        }
        deff.update(rule_entry)
        deff.update(rule_entry["config"].to_dict())
        del deff["config"]
        # deff["icon"] = deff["icon"] or "💾"

            # Generate data
        payload = self.HEADER_TEMPLATE_ENTITY.format(
            data=SimpleNamespace(**deff),
            # object_class=", ".join(object_class),
            # rdn=rdn,
        )
        self.styles.height = len(payload.split("\n")) - 1
        return payload




# =============================================================
# Content panels
# =============================================================

class ContentViewBase(ScrollableContainer, can_focus=False):
    """Base class for content views."""

    current_ldap_connection: reactive[Any] = reactive(None)
    current_rule_entry: reactive[dict | None] = reactive(None)
    content_widget = None
    styles = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._pending_rule_entry = None

    @watch("current_rule_entry")
    def watch_current_rule_entry_____(self, rule_entry):
        """Update the content view with LDAP entry information."""
        logger.info("watch_current_rule_entry called with rule_entry: %s", rule_entry)

        # self.notify(f"watch_current_rule_entry called with rule_entry: {rule_entry}")

        if not rule_entry:
            logger.info("No rule entry provided, returning early")
            return
        
        if not self.current_ldap_connection:
            # Store the rule entry to process when connection becomes available
            self._pending_rule_entry = rule_entry
            logger.info("No LDAP connection available, storing pending rule entry")
            self.notify("Waiting for LDAP connection...")
            self.loading = True
            return
        
        # Clear any pending rule entry since we have a connection
        self._pending_rule_entry = None
        logger.info("LDAP connection available, processing rule entry")
        
        # Query data
        query = rule_entry.get("ldap_filter")
        # if not query:
        #     assert False, "TOFIX: no query"
        results = []
        if isinstance(query, str):
            logger.info("Executing LDAP query: %s", query)
            results = self.current_ldap_connection.search(scope=SCOPE_SUBTREE, filter_str=query)
        self.loading = False


        # Process widget data ...
        self.view_result_process(rule_entry, results)

    @work
    async def watch_current_ldap_connection(self, connection):
        """Handle LDAP connection changes."""
        logger.info("watch_current_ldap_connection called with connection: %s", connection)
        if connection and hasattr(self, '_pending_rule_entry') and self._pending_rule_entry:
            # Connection is now available and we have a pending rule entry
            logger.info("LDAP connection available, processing pending rule entry")
            # await asyncio.sleep(3)
            self.watch_current_rule_entry(self._pending_rule_entry)


    def view_result_process(self, rule_entry, results):
        """Process the results and update the content view."""
        # self.notify(f"results: {results}", markup=False)
        assert False, "NOT IMPLEMENTED VIEW PROCESSING"




# class ContentViewBeta(ContentViewBase):
#     """Right pane for the app."""

#     DEFAULT_CSS = """
#     ContentViewBeta {
#         border: solid $primary;
#     }
#     """

#     BORDER_TITLE = "JSON view"

    
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.loading = False
#         self.content_widget = None
#         # self.current_ldap_connection = None

#     def compose(self) -> ComposeResult:
#         """Create child widgets for the scrollable container."""
#         self.content_widget = Pretty(self.current_rule_entry, id="content-static")

#         yield self.content_widget



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
        self.content_widget = Pretty(self.current_rule_entry, id="content-static")

        yield self.content_widget


    def view_result_process(self, rule_entry, results):
        # if self.content_widget and self.current_rule_entry:
        self.content_widget.update(results)



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
        yield self.content_widget


    def view_result_process(self, rule_entry, results):
        """Process the results and update the content view."""


        # Early quit
        if not rule_entry:
            ret = "Please select entry"
            self.display = False
            return ret

        # Process type
        self._render_results(rule_entry, results)


    def _render_results(self, rule_entry, results):
        """Render the entity."""

        # Reset table and remove all columns
        self.content_widget.clear()
        for col in list(self.content_widget.columns):
            self.content_widget.remove_column(col)

        # Early quit and hide table if no results
        if not results:
            self.notify("No results found for this query")
            self.display = False
            return
        
        self.display = True


        # Clear existing table and reset sorting
        self.current_sort_column = None
        self.current_sort_reverse = False
        columns = rule_entry.get("attr") or ["dn"]
        columns = [col.lower() for col in columns]
        self.content_widget.add_columns(*columns)
        missing_placeholder = settings.viewer.missing_value_placeholder

        for result in results:

            dn = result.get("dn")
            attrs = result.get("attributes")
            attrs = {k.lower(): v for k, v in attrs.items()}

            fields2 = []
            for field in columns:
                value = missing_placeholder

                if field == "dn":
                    value = dn
                elif field in attrs:
                    value = attrs[field]

                    # # TOFIX HERE
                    if isinstance(value, list):
                        if len(value) > 0:
                            value = value[0]
                        else:
                            value = missing_placeholder

                fields2.append(value)
            
            
            # self.content_widget.add_row(str(dn), *fields)
            self.content_widget.add_row(*fields2)
 
            
    @message(DataTable.HeaderSelected)
    def on_content_widget_header_selected999(
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
