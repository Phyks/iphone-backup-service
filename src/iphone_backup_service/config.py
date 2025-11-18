import os
from pathlib import Path

# Root path for the backups, backups will be stored in a subfolder named after the iPhone friendly name
BACKUP_ROOT_PATH = Path(os.environ.get("BACKUP_ROOT_PATH", "./data"))

# Network switch to use. Defaults to backuping over the network.
if os.environ.get("NO_NETWORK_SWITCH"):
    NETWORK_SWITCH = []
else:
    NETWORK_SWITCH = ["-n"]
