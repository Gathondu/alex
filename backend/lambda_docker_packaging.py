"""Shared helpers for agent ``package_docker.py`` scripts."""

from __future__ import annotations

import os
from typing import List


def docker_run_host_user_args() -> List[str]:
    """Return extra ``docker run`` flags so bind-mounted files are owned by the host user.

    The Lambda base image runs as root by default. ``pip install`` into a mounted volume
    then leaves root-owned files on the host, and :class:`tempfile.TemporaryDirectory`
    cleanup fails on GitHub Actions with ``PermissionError``.
    """
    getuid = getattr(os, "getuid", None)
    getgid = getattr(os, "getgid", None)
    if callable(getuid) and callable(getgid):
        return ["--user", f"{getuid()}:{getgid()}"]
    return []
