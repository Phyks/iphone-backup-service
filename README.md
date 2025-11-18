iPhone Backup Service
=====================

A convenient web wrapper around `idevicebackup2` to allow users to backup their iPhone over USB / network and have live feedback through command line streaming.

## Installation

You will need `stdbuf` on your system (usually provided by GNU coreutils package). You will also need to install `libimobiledevice` on your system, which provides the useful tools to talk to your iPhone (including `idevicebackup2`).

If you intend to use this tool over the network (default configuration), then follow [this guide](https://valinet.ro/2021/01/20/Automatically-backup-the-iPhone-to-the-Raspberry-Pi.html) to install the specific version of `libimobiledevice` with network support.

Ensure you have [uv](https://docs.astral.sh/uv/getting-started/) on your system. Then,

```
git clone …  # Clone the repository
cd iphone-backup-service
uv sync  # Install dependencies, use --all-extras flag if you want the development tools as well
```

## Running

To run the tool, you can use the built-in `uvicorn` webserver:

```
uv run uvicorn iphone_backup_service.main:app
```

Use the following environment variables to customize the tool:
* `BACKUP_ROOT_PATH=/path/to/folder` to define the root folder in which backups should be stored.
* `NO_NETWORK_SWITCH=1` to use `idevicebackup2` over USB and not network.


## License

The content of this repository is licensed under an MIT license, unless explicitly mentionned otherwise.
