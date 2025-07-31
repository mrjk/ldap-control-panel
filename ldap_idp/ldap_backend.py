#!/usr/bin/env python3
"""
LDAP Backend - All LDAP related functions and connection management
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import ldap

# LDAP constants
SCOPE_BASE = 0
SCOPE_ONELEVEL = 1
SCOPE_SUBTREE = 2

logger = logging.getLogger(__name__)


# =============================================================
# LDAP models
# =============================================================


@dataclass
class LDAPConfig:
    """LDAP connection configuration"""

    uri: str
    bind_dn: str
    bind_password: str
    base_dn: str = ""


# =============================================================
# LDAP Helpers
# =============================================================


def has_children(entry: Dict[str, Any]) -> bool:
    """Check if an entry likely has children"""
    # Simple heuristic: if it's an organizational unit or has sub-entries, it might have children
    attrs = entry["attributes"]
    if b"objectClass" in attrs:
        object_classes = [oc.decode("utf-8").lower() for oc in attrs[b"objectClass"]]
        return "organizationalunit" in object_classes
    return True


def get_display_name(entry: Dict[str, Any]) -> str:
    """Get display name from LDAP entry"""
    dn = entry["dn"]
    attrs = entry["attributes"]

    # Get display name from commonName or cn, fallback to first part of DN
    if b"cn" in attrs:
        return attrs[b"cn"][0].decode("utf-8")
    elif b"commonName" in attrs:
        return attrs[b"commonName"][0].decode("utf-8")
    else:
        # Extract first part of DN
        return dn.split(",")[0].split("=")[1] if "=" in dn else dn


def get_rdn(entry: Dict[str, Any]) -> str:
    """Get the RDN (Relative Distinguished Name) value from an LDAP entry.

    Args:
        entry: LDAP entry dictionary containing 'dn' key

    Returns:
        The RDN value (part after = and before first comma in DN)
    """
    dn = entry["dn"]
    try:
        # Get first DN component and extract value after =
        rdn = dn.split(",")[0]
        return rdn  # .split("=")[1]
    except (IndexError, KeyError) as e:
        logging.error(f"Failed to extract RDN from DN {dn}: {e}")
        return dn


# Icon mapping configuration - case insensitive
ICON_MAPPING = {
    "inetorgperson": "👤",
    "posixaccount": "🏠",
    "groupofuniquenames": "🔗",
    "groupofurls": "🔧",
    "organizationalunit": "📁",
    "simpleSecurityObject": "🔑",
    "organizationalRole": "🔑",
    # "groupofnames": "👥",
    # "group": "👥",
    # "groupofuniquenames": "👤",
    # "inetorgperson": "👤",
    # "person": "👤",
    # "organization": "🏢",
    # "domain": "🌐",
    # "computer": "💻",
    # "server": "🖥️",
    # "contact": "📞",
    # "applicationprocess": "⚙️",
    # "applicationentity": "🔧",
    # "device": "📱",
    # "container": "📦",
    # "country": "🌍",
    # "locality": "🏘️",
    # "organizationalperson": "👤",
    # "residentialperson": "🏠",
    # "simplesecurityobject": "🔒",
    # "top": "📄",  # Default for top-level objects
}
ICON_MAPPING = {key.lower(): value for key, value in ICON_MAPPING.items()}


def get_icon(entry: Dict[str, Any]) -> str:
    """Get appropriate icon for LDAP entry based on objectClass"""
    attrs = entry["attributes"]
    icon = "📄"  # Default

    if "objectClass" in attrs:
        object_classes = [oc.lower() for oc in attrs["objectClass"]]
        logger.debug("Object classes: %s", object_classes)

        # Check each object class against the mapping (case insensitive)
        for obj_class in object_classes:
            if obj_class in ICON_MAPPING:
                icon = ICON_MAPPING[obj_class]
                break

    return icon


# =============================================================
# LDAP Main classes
# =============================================================


class LDAPConnection:
    """LDAP connection manager"""

    # def __init__(self, config: LDAPConfig):
    def __init__(self, config: LDAPConfig, base_dn: str = None, filter_config: Dict[str, Any] = None):

        assert isinstance(config, LDAPConfig), f"Type error: config is not a LDAPConfig: {config}   "
        assert isinstance(base_dn, (str, type(None))), f"Type error1: base_dn is not a string: {base_dn}   "
        assert isinstance(config.base_dn, (str, type(None))), f"Type error2: base_dn is not a string: {base_dn}   "



        self.config = config
        self.connection: Optional[ldap.ldapobject.LDAPObject] = None

        self.auto_connect = True
        self.filter_config = filter_config or {}

        self.base_dn_static = base_dn or config.base_dn
        self.base_dn_dynamic = None



    @property
    def base_dn(self) -> str:
        """Get the base DN. If base_dn_static is set, use it. If not, try to get it from the server."""
        if self.base_dn_static is not None:
            ret = self.base_dn_static
            assert isinstance(ret, str), f"Type error: base_dn_static is not a string: {ret}   "
            return ret
        
        if self.connection and self.connection.connected:
            ret = self.get_base_dn()
            assert isinstance(ret, str), f"Type error: base_dn from get_base_dn is not a string: {ret}   "
            return ret
        
        return ""

    def connect(self) -> None:
        """Establish LDAP connection"""
        try:
            self.connection = ldap.initialize(self.config.uri)
            self.connection.simple_bind_s(
                self.config.bind_dn, self.config.bind_password
            )
            logging.info(f"Connected to LDAP server: {self.config.uri}")
        except Exception as e:
            logging.error(f"LDAP connection failed: {e}")
            raise

    def disconnect(self) -> None:
        """Close LDAP connection"""
        if self.connection:
            self.connection.unbind_s()
            self.connection = None

    def search(
        self,
        base_dn: str = None,
        scope: int = SCOPE_ONELEVEL,
        filter_str: str = "(objectClass=*)",
        attributes: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Search LDAP directory"""
        if not self.connection:
            raise RuntimeError("LDAP connection not established")

        try:
            base_dn = base_dn or self.base_dn
            results = self.connection.search_s(base_dn, scope, filter_str, attributes)
            return [
                {"dn": dn, "attributes": self._decode_attributes(attrs)}
                for dn, attrs in results
                if dn is not None
            ]
        except Exception as e:
            logging.error(f"LDAP search failed {type(e)}: {e} with: base_dn={base_dn}, scope={scope}, filter_str={filter_str}, attributes={attributes}")
            return []

    def _decode_attributes(
        self, attrs: Dict[bytes, List[bytes]]
    ) -> Dict[str, List[str]]:
        """Decode LDAP attributes from bytes to strings"""
        decoded_attrs = {}
        for attr_name, attr_values in attrs.items():
            # Decode attribute name
            if isinstance(attr_name, bytes):
                attr_name_str = attr_name.decode("utf-8", errors="replace")
            else:
                attr_name_str = str(attr_name)

            # Decode attribute values
            decoded_values = []
            for value in attr_values:
                if isinstance(value, bytes):
                    try:
                        decoded_value = value.decode("utf-8")
                    except UnicodeDecodeError:
                        # If UTF-8 fails, try to decode as hex or show as hex string
                        decoded_value = f"<binary: {value.hex()}>"
                else:
                    decoded_value = str(value)
                decoded_values.append(decoded_value)

            decoded_attrs[attr_name_str] = decoded_values

        return decoded_attrs

    def get_base_dn(self) -> str:
        """Get the base DN by finding top-level DC elements"""

        # If base DN is configured, use it
        if self.config.base_dn:
            logging.info(f"Using configured base DN: {self.config.base_dn}")
            return self.config.base_dn

        if not self.connection:
            if self.auto_connect:
                self.connect()
            else:
                raise RuntimeError("LDAP connection not established")



        try:
            # Method 1: Search for root DSE and look for namingContexts
            logging.info("Attempting to get base DN from root DSE namingContexts...")
            results = self.connection.search_s("", SCOPE_BASE, "(objectClass=*)")
            if results:
                # Try to find namingContexts
                attrs = results[0][1]
                if b"namingContexts" in attrs:
                    # Return the first naming context
                    base_dn = attrs[b"namingContexts"][0].decode("utf-8")
                    logging.info(f"Found base DN from namingContexts: {base_dn}")
                    return base_dn
                else:
                    logging.info("No namingContexts found in root DSE")
                    # Log available attributes for debugging
                    available_attrs = [
                        attr.decode("utf-8") if isinstance(attr, bytes) else str(attr)
                        for attr in attrs.keys()
                    ]
                    logging.info(f"Available root DSE attributes: {available_attrs}")

            # Method 2: Try to find top-level DC entries (skip if we got error 32)
            logging.info("Attempting to find top-level DC entries...")
            try:
                results = self.connection.search_s("", SCOPE_ONELEVEL, "(dc=*)")
                if results:
                    base_dn = results[0][0]
                    logging.info(f"Found base DN from DC search: {base_dn}")
                    return base_dn
            except ldap.NO_SUCH_OBJECT:
                logging.info(
                    "Empty base DN search not allowed, trying alternative methods..."
                )
            except Exception as e:
                logging.debug(f"DC search failed: {e}")

            # Method 3: Try to extract base DN from bind DN
            logging.info("Attempting to extract base DN from bind DN...")
            if self.config.bind_dn:
                # Extract DC components from bind DN
                # Example: cn=admin,dc=example,dc=com -> dc=example,dc=com
                parts = self.config.bind_dn.split(",")
                dc_parts = [part for part in parts if part.lower().startswith("dc=")]
                if dc_parts:
                    base_dn = ",".join(dc_parts)
                    logging.info(f"Extracted base DN from bind DN: {base_dn}")
                    # Test if this base DN actually works
                    try:
                        test_results = self.connection.search_s(
                            base_dn, SCOPE_BASE, "(objectClass=*)"
                        )
                        if test_results:
                            logging.info(
                                f"Verified base DN from bind DN works: {base_dn}"
                            )
                            return base_dn
                        else:
                            logging.info(
                                f"Base DN from bind DN exists but is empty: {base_dn}"
                            )
                    except Exception as e:
                        logging.debug(f"Base DN from bind DN failed: {e}")

            # Method 4: Try to find any existing entries and derive base DN
            logging.info("Attempting to find existing entries to derive base DN...")
            try:
                # Try searching with a very broad filter to find any entries
                results = self.connection.search_s(
                    "", SCOPE_SUBTREE, "(objectClass=*)", attrlist=["dn"]
                )
                if results:
                    # Find the shortest DN (likely the base)
                    valid_results = [r for r in results if r[0] and r[0] != ""]
                    if valid_results:
                        shortest_dn = min(valid_results, key=lambda x: len(x[0]))
                        logging.info(
                            f"Found potential base DN from existing entries: {shortest_dn[0]}"
                        )
                        return shortest_dn[0]
                    else:
                        logging.info("No valid DNs found in search results")
                else:
                    logging.info("No search results returned")
            except ldap.NO_SUCH_OBJECT:
                logging.info("Subtree search with empty base DN not allowed")
            except Exception as e:
                logging.debug(f"Broad search failed: {e}")

            # Method 5: Try common base DNs
            logging.info("Trying common base DNs...")
            common_base_dns = [
                "dc=example,dc=com",
                "dc=test,dc=com",
                "dc=local",
                "dc=domain,dc=com",
                "dc=company,dc=com",
            ]

            for test_dn in common_base_dns:
                try:
                    logging.info(f"Testing base DN: {test_dn}")
                    results = self.connection.search_s(
                        test_dn, SCOPE_BASE, "(objectClass=*)"
                    )
                    if results:
                        logging.info(f"Found working base DN: {test_dn}")
                        return test_dn
                except Exception as e:
                    logging.debug(f"Base DN {test_dn} failed: {e}")
                    continue

            logging.error("No base DN found using any method")
            raise RuntimeError(
                "Could not determine base DN. Please specify it explicitly using --base-dn option."
            )

        except Exception as e:
            logging.error(f"Failed to get base DN: {e}")
            raise RuntimeError(f"Failed to determine base DN: {e}")


# =============================================================
# LDAP Function Helpers
# =============================================================


def filter_object_classes(
    entry: Dict[str, Any], silenced_ocs: List[str] = None
) -> Dict[str, Any]:
    """Filter out silenced object classes from LDAP entry.

    Args:
        entry: LDAP entry dictionary
        silenced_ocs: List of object class names to hide

    Returns:
        New entry dictionary with filtered object classes
    """
    if not silenced_ocs:
        return entry

    # Create a copy to avoid modifying the original
    filtered_entry = entry.copy()
    filtered_attrs = filtered_entry["attributes"].copy()

    # Filter objectClass attribute
    if "objectClass" in filtered_attrs:
        object_classes = filtered_attrs["objectClass"]
        # Keep only non-silenced object classes
        filtered_ocs = [oc for oc in object_classes if oc not in silenced_ocs]
        filtered_attrs["objectClass"] = filtered_ocs
        logging.debug(
            f"Filtered object classes for {entry.get('dn', 'unknown')}: {object_classes} -> {filtered_ocs}"
        )

    filtered_entry["attributes"] = filtered_attrs
    return filtered_entry


def filter_attributes(
    entry: Dict[str, Any], silenced_attrs: List[str] = None
) -> Dict[str, Any]:
    """Filter out silenced attributes from LDAP entry.

    Args:
        entry: LDAP entry dictionary
        silenced_attrs: List of attribute names to hide

    Returns:
        New entry dictionary with filtered attributes
    """
    if not silenced_attrs:
        return entry

    # Create a copy to avoid modifying the original
    filtered_entry = entry.copy()
    filtered_attrs = filtered_entry["attributes"].copy()

    # Remove silenced attributes
    removed_attrs = []
    for attr_name in silenced_attrs:
        if attr_name in filtered_attrs:
            del filtered_attrs[attr_name]
            removed_attrs.append(attr_name)

    if removed_attrs:
        logging.debug(
            f"Filtered attributes for {entry.get('dn', 'unknown')}: removed {removed_attrs}"
        )

    filtered_entry["attributes"] = filtered_attrs
    return filtered_entry


def apply_entry_filters(
    entry: Dict[str, Any], config: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Apply all entry filters based on configuration.

    Args:
        entry: LDAP entry dictionary
        config: Configuration dictionary containing filter options

    Returns:
        Filtered entry dictionary
    """
    if not config:
        return entry

    # Get filter options from config
    # general_config = config.get("config", {}).get("general", {})
    silenced_ocs = config.get("oc_silented", [])
    silenced_attrs = config.get("attr_silented", [])

    # Apply filters
    logging.warning(
        f"Applying filters to {entry.get('dn', 'unknown')}: oc_silented={silenced_ocs}, oc_attr_silented={silenced_attrs}"
    )
    filtered_entry = filter_object_classes(entry, silenced_ocs)
    filtered_entry = filter_attributes(filtered_entry, silenced_attrs)

    if silenced_ocs or silenced_attrs:
        logging.debug(
            f"Applied filters to {entry.get('dn', 'unknown')}: oc_silented={silenced_ocs}, oc_attr_silented={silenced_attrs}"
        )

    return filtered_entry


# =============================================================
# LDAP Class Overrides
# =============================================================


class LDAPConnectionImproved(LDAPConnection):
    "Better LDAP implementation"

    # def __init__(self, config: LDAPConfig, base_dn: str = None, filter_config: Dict[str, Any] = None):
    #     super().__init__(config)
    #     self.filter_config = filter_config or {}
    #     self.base_dn = base_dn or self.get_base_dn() or ""

    def get_tree_recursive(self, max_depth: int = 3, display_mode="full"):
        """Return the LDAP tree recursively loaded up to max_depth levels.

        Args:
            max_depth: Maximum depth to load (default 3 to avoid infinite recursion)
        """
        logger.info(f"STARTING RECURSIVE TREE LOADING (max_depth={max_depth})")

        # try:
        # Get base DN
        base_dn = self.base_dn
        logger.info(f"Base DN: {base_dn}")

        # Build tree structure recursively
        tree_data = {
            "root": {
                "label": base_dn,
                "dn": base_dn,
                "icon": "🌐",
                "children": self._load_children_recursive(
                    base_dn, max_depth, 0, display_mode=display_mode
                ),
            }
        }

        logger.info(f"Recursive tree structure built")
        return tree_data

        # except Exception as e:
        #     logger.error(f"Failed to build recursive tree: {e}")
        #     # Return a simple error structure
        #     return {
        #         "root": {
        #             "label": "Error",
        #             "dn": "",
        #             "icon": "❌",
        #             "children": [],
        #             "error": str(e),
        #         }
        #     }

    def _load_children_recursive(
        self, parent_dn: str, max_depth: int, current_depth: int, display_mode="simple"
    ):
        """Recursively load children for a given DN up to max_depth."""
        if current_depth >= max_depth:
            logger.debug(f"Reached max depth {max_depth} for {parent_dn}")
            return []

        try:
            # Search for entries at current level
            entries = self.search(parent_dn, scope=SCOPE_ONELEVEL)
            logger.debug(
                f"Found {len(entries)} entries at depth {current_depth} for {parent_dn}"
            )

        except Exception as e:
            logger.error(f"Error loading children recursively for {parent_dn}: {e}")
            return []

        children = []
        for entry in entries:
            # Apply filters to the entry
            filtered_entry = apply_entry_filters(entry, self.filter_config)

            dn = filtered_entry["dn"]
            attributes = filtered_entry["attributes"]

            # Get display name
            display_name = get_display_name(filtered_entry)
            rdn = get_rdn(filtered_entry)
            icon = get_icon(entry)
            # assert False, filtered_entry

            if display_mode == "full":
                label = f"{icon} {rdn}"
            elif display_mode == "simple":
                label = f"{icon} {display_name}"
            else:
                raise ValueError(f"Invalid display mode: {display_mode}")

            # Check if entry has children by searching
            try:
                child_entries = self.search(dn, scope=SCOPE_ONELEVEL)
                has_children_flag = len(child_entries) > 0
                logger.debug(f"Entry {dn} has {len(child_entries)} children")
            except Exception as e:
                logger.debug(f"Could not check children for {dn}: {e}")
                has_children_flag = False

            # Create node data
            node_data = {
                "label": label,
                "rdn": rdn,
                "dn": dn,
                "icon": icon,
                "attributes": attributes,
                "has_children": has_children_flag,
                "children": [],
            }

            # Recursively load children if this entry has children and we haven't reached max depth
            if has_children_flag and current_depth < max_depth - 1:
                node_data["children"] = self._load_children_recursive(
                    dn, max_depth, current_depth + 1, display_mode=display_mode
                )

            # Use circle icon for leaves without children
            # if not has_children_flag:
            #     node_data["label"] = "● " + node_data["label"]

            children.append(node_data)

        return children















    def get_ldap_entry(self, dn: str, sort=True):
        """Get one LDAP entry by DN."""
        ret = self.search(dn, scope=SCOPE_BASE)
        if len(ret) > 1:
            assert False, f"Multiple entries found for DN: {dn}"

        # Return nothing if not found
        if len(ret) != 1:
            return None
        entry = ret[0]

        # Apply filters to the entry
        filtered_entry = apply_entry_filters(entry, self.filter_config)
        logger.warning(f"Filtered entry: {filtered_entry} FROM {self.filter_config}")

        # Sort attributes alphabetically
        if "attributes" in filtered_entry and sort:
            sorted_attributes = dict(sorted(filtered_entry["attributes"].items()))
            # Create a new entry with sorted attributes
            filtered_entry = {
                "dn": filtered_entry["dn"],
                "attributes": sorted_attributes,
            }
        return filtered_entry
