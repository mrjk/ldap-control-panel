import logging
import os
from typing import Any, Dict, List, Optional

import yaml

# from ldap_idp.lib_textual.comp_store import AppStoreMixin, AppStoreServerMixin

logger = logging.getLogger(__name__)

# ------------------------------------------------------------
# Subapp automatic config management
# ------------------------------------------------------------


class TMPConfigMixin:
    """Mixin to provide simple configuration management with dot notation support."""
    
    def get_config(self, key_name: str) -> Any:
        """Get configuration value using dot notation (e.g., 'app.viewer.default_view')."""
        if not hasattr(self, '__config__'):
            return None
            
        keys = key_name.split('.')
        current = self.__config__
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
                
        return current
    
    def set_config(self, config: Dict[str, Any]) -> None:
        """Set the configuration dictionary."""
        self.__config__ = config
    
    def dump_config(self) -> Dict[str, Any]:
        """Return the complete configuration dictionary."""
        if not hasattr(self, '__config__'):
            return {}
        return self.__config__.copy()
    
    def show_config(self) -> Dict[str, Any]:
        """Return a flattened configuration dictionary with dot notation keys."""
        if not hasattr(self, '__config__'):
            return {}
        
        def flatten_dict(d: Dict[str, Any], parent_key: str = '') -> Dict[str, Any]:
            items = []
            for k, v in d.items():
                new_key = f"{parent_key}.{k}" if parent_key else k
                if isinstance(v, dict):
                    items.extend(flatten_dict(v, new_key).items())
                else:
                    items.append((new_key, v))
            return dict(items)
        
        return flatten_dict(self.__config__)


# # class AppConfigMixin(AppStoreMixin):
class AppConfigMixin():
    """Mixin to provide easy access to app configuration and config file utilities."""

#     DEFAULT_CONFIG = {}

#     # def get_app_config(self) -> Dict[str, Any]:
#     #     """Get app runtime configuration by traversing up the widget tree."""
#     #     return self.get_app_store("app_config")

#         # if hasattr(self, '__app_store__'):
#         #     return self.__app_store__

#         # # Traverse up to find parent with __app_store__
#         # parent = self.parent
#         # while parent is not None:
#         #     if hasattr(parent, '__app_store__'):
#         #         return parent.__app_store__
#         #     parent = parent.parent

#         # return {}

#     # def get_app_config_value(self, key: str, default: Any = None) -> Any:
#     #     """Get a specific configuration value."""
#     #     return self.get_app_config().get(key, default)


# class AppConfigLoaderMixin(AppConfigMixin, AppStoreServerMixin):
class AppConfigLoaderMixin(TMPConfigMixin):
    """Mixin to provide easy access to app configuration and config file utilities."""



    # ===============================================================
    def find_config_file(self, config_files: List[str] = None) -> Optional[str]:
        """Find config file in current directory"""
        config_files = config_files or ["config.yaml", "config.yml"]
        if not isinstance(config_files, list):
            config_files = [config_files]
        for config_file in config_files:
            if os.path.exists(config_file):
                return config_file
        return None

    def load_data_from_file(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(config_path, "r") as f:
                config_data = yaml.safe_load(f) or {}
                return config_data
        except Exception as e:
            assert False, f"Error loading config file {config_path}: {e}"
            return {}


    # ===============================================================



    def read_config(
        self, app_name: str = "app", app_config: dict = None
    ) -> Dict[str, Any]:
        """Load and merge configuration from multiple sources."""

        # Start with default configuration
        config_data = dict(getattr(self, "DEFAULT_CONFIG", {}))

        # Load config from different sources
        config_file = (
            self.find_config_file(f"{app_name}.yaml") or self.find_config_file()
        )
        if config_file:
            config_file_content = self.load_data_from_file(config_file)
            config_data.update(config_file_content)
        if app_config:
            config_data.update(app_config)

        return config_data





    # ===============================================================

    def get_nested(self, path: str, default: Any = None) -> Any:
        """Get a nested configuration value using dot notation (e.g., 'config.viewer.default_view')"""
        keys = path.split(".")
        current = self._loaded_config

        # Try to find in loaded config first
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                # Fall back to default config
                current = self._config
                for k in keys:
                    if isinstance(current, dict) and k in current:
                        current = current[k]
                    else:
                        return default
                break

        return current if current is not None else default
    

    # ===============================================================


    # DEPRECATED
    def set_app_config(
        self, app_name: str = "app", app_config: dict = None
    ) -> Dict[str, Any]:
        """Load and merge configuration from multiple sources."""

        # Start with default configuration
        config_data = dict(getattr(self, "DEFAULT_CONFIG", {}))

        # Load config from different sources
        config_file = (
            self.find_config_file(f"{app_name}.yaml") or self.find_config_file()
        )
        if config_file:
            config_file_content = self.load_data_from_file(config_file)
            config_data.update(config_file_content)
        if app_config:
            config_data.update(app_config)

        self.set_app_store("app_config", config_data)


    # DEPRECATED
    def set_app_store(self, key: str, value: Any) -> None:
        """Set app runtime configuration by traversing up the widget tree."""
        store = getattr(self, "__app_store__", {})
        store[key] = value
        setattr(self, "__app_store__", store)