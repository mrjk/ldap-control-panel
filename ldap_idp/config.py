import os
from pathlib import Path
from dynaconf import Dynaconf

# Get the directory where this config.py file is located
config_dir = Path(__file__).parent

settings = Dynaconf(
    envvar_prefix="LDAPCP_",
    settings_files=[
        str(config_dir / 'settings.yaml'), 
        str(config_dir / '.secrets.yaml'),
        'settings.yaml', '.secrets.yaml'
    ],
    merge_enabled=True,
)

# `envvar_prefix` = export envvars with `export DYNACONF_FOO=bar`.
# `settings_files` = Load these files in the order.
