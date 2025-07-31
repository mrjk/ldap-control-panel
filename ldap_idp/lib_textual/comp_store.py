from typing import Any, Dict, List, Optional

# ------------------------------------------------------------
# Widget data sharing KV
# ------------------------------------------------------------


class AppStoreMixin:
    """Mixin to provide easy access to app configuration and config file utilities."""

    def get_app_store(self, key: str) -> Dict[str, Any]:
        """Walk up the widget tree to find the app store."""
        parent = self
        while parent is not None:
            if hasattr(parent, "__app_store__"):
                if key in parent.__app_store__:
                    return parent.__app_store__[key]
            parent = parent.parent
        return None


class AppStoreServerMixin(AppStoreMixin):
    """Mixin to provide easy access to app configuration and config file utilities."""

    def set_app_store(self, key: str, value: Any) -> None:
        """Set app runtime configuration by traversing up the widget tree."""
        store = getattr(self, "__app_store__", {})
        store[key] = value
        setattr(self, "__app_store__", store)
