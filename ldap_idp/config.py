
from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="LDAPCP_",
    settings_files=['settings.yaml', '.secrets.yaml'],
    merge_enabled=True,
)

# `envvar_prefix` = export envvars with `export DYNACONF_FOO=bar`.
# `settings_files` = Load these files in the order.
