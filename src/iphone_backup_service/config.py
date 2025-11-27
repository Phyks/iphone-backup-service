import os
from pathlib import Path

# Root path for the backups, backups will be stored in a subfolder named after the iPhone friendly name
BACKUP_ROOT_PATH = Path(os.environ.get("BACKUP_ROOT_PATH", "./data"))

# Network switch to use. Defaults to backuping over the network.
if os.environ.get("NO_NETWORK_SWITCH"):
    NETWORK_SWITCH = []
else:
    NETWORK_SWITCH = ["-n"]

# Base HealtChecks endpoint including ping key.
# See https://blog.healthchecks.io/2021/09/new-feature-slug-urls/
# To use HealthChecks, ensure you have a task created with a slug matching the
# slugified DeviceName of your device.
# HC_ENDPOINT = "https://hc-ping.com/<ping-key>/"
HC_ENDPOINT = os.environ.get("HC_ENDPOINT", "").rstrip("/")
