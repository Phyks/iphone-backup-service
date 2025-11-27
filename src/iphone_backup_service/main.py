#!/usr/bin/env python3
from __future__ import annotations

import asyncio
import subprocess
from pathlib import Path
from typing import AsyncGenerator

import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from slugify import slugify

from iphone_backup_service import config

app = FastAPI(title="iPhone Backup Service", version="1.0.0")

# DeviceID type is an alias for string
DeviceID = str


async def run_command(
    cmd: list[str], slug: str, cwd: Path | None = None
) -> AsyncGenerator[str, None]:
    """
    Async subprocess helper

    :param cmd: The command to start as a list of arguments.
    :param slug: Device slug to infer the HealthChecks endpoint URL.
    :param cwd: The working directory (optional).
    :return: A generator for the subprocess stdout.
    """
    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            limit=1024 * 128,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=str(cwd) if cwd else None,
        )
    except Exception as exc:
        raise HTTPException(500, f"Failed to start process: {exc}") from exc

    assert process.stdout is not None

    while True:
        try:
            async for raw_line in process.stdout:
                yield raw_line.decode(errors="replace")
        except ValueError:
            continue
        else:
            break

    rc = await process.wait()
    if rc != 0:
        yield f"\n[ERROR] exited with code {rc}\n"
        if config.HC_ENDPOINT:
            try:
                req = requests.get(f"{config.HC_ENDPOINT}/{slug}/fail")
                req.raise_for_status()
            except requests.exceptions.RequestException:
                yield "\n[ERROR] UNABLE TO REACH HEALTHCHECKS INSTANCE"
    elif config.HC_ENDPOINT:
        try:
            req = requests.get(f"{config.HC_ENDPOINT}/{slug}")
            req.raise_for_status()
        except requests.exceptions.RequestException:
            yield "\n[ERROR] UNABLE TO REACH HEALTHCHECKS INSTANCE"

    yield "\n\n=====================\n"
    yield f"DONE WITH EXIT CODE {rc}\n"
    yield "=====================\n"


def get_device_name(device_id: DeviceID) -> str | None:
    """
    Get the device name (friendly name) from the device id.

    :param device_id: A device identifier (UUID).
    :return: The device name or ``None`` if device cannot be found.
    """
    try:
        info = (
            subprocess.check_output(
                ["ideviceinfo"] + config.NETWORK_SWITCH + ["-u", device_id],
                stderr=subprocess.STDOUT,
            )
            .decode()
            .splitlines()
        )
        return next(
            line.split(":")[1].strip()
            for line in info
            if line.startswith("DeviceName:")
        )
    except (StopIteration, subprocess.CalledProcessError):
        return None


@app.get("/", include_in_schema=False)
async def root() -> FileResponse:
    """
    Serve the webpage on root URL.
    """
    return FileResponse("index.html")


@app.get("/devices")
async def list_devices() -> dict[DeviceID, str | None]:
    """
    Get the list of available devices.

    :return: A dict mapping found device IDs with their friendly name.
    """
    uuids = (
        subprocess.check_output(["idevice_id"] + config.NETWORK_SWITCH)
        .decode()
        .splitlines()
    )
    return {uuid: get_device_name(uuid) for uuid in uuids}


@app.get("/backup/{device_id}")
async def backup_device(device_id: DeviceID) -> StreamingResponse:
    """
    Run the device backup with idevicebackup2 and stream output to the browser.

    :param device_id: A device UUID.
    """
    device_name = get_device_name(device_id)
    if not device_name:
        return StreamingResponse(
            f"ERROR: Device {device_id} not found!", media_type="text/plain"
        )

    backup_dir = config.BACKUP_ROOT_PATH / device_name
    backup_dir.mkdir(parents=True, exist_ok=True)

    # Use stdbuf to ensure proper buffering of idevicebackup2 output.
    cmd = (
        ["stdbuf", "-oL", "idevicebackup2", "backup", "-u", device_id]
        + config.NETWORK_SWITCH
        + ["."]
    )

    # Read and stream output from the idevicebackup2 command
    async def stream() -> AsyncGenerator[str, None]:
        slug = slugify(device_name)
        yield f"Device slug is {slug}."
        if config.HC_ENDPOINT:
            yield f"\nWill ping HealthChecks instance at {config.HC_ENDPOINT}/{slug}\n"
        async for line in run_command(cmd, slug, cwd=backup_dir):
            yield line

    return StreamingResponse(stream(), media_type="text/plain")
