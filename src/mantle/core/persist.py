#!/usr/bin/env python3
"""Small persistence primitives shared by Mantle Body checkpoints."""
from __future__ import annotations

import json
import os
import tempfile
from typing import Any


OWNER_DIRECTORY_MODE = 0o700
OWNER_FILE_MODE = 0o600
_STAGE_PREFIX = ".mantle-stage-"


def ensure_owner_directory(path: str) -> None:
    """Create or harden a state directory so only its owner can traverse it."""
    os.makedirs(path, mode=OWNER_DIRECTORY_MODE, exist_ok=True)
    os.chmod(path, OWNER_DIRECTORY_MODE)


def harden_owner_file(path: str) -> None:
    """Remove group/world permissions from a persisted artifact."""
    os.chmod(path, OWNER_FILE_MODE)


def atomic_write_json(path: str, value: Any) -> None:
    """Serialize JSON beside its destination, fsync it, then atomically replace."""
    directory = os.path.dirname(os.path.abspath(path))
    ensure_owner_directory(directory)
    fd, staged = tempfile.mkstemp(prefix=_STAGE_PREFIX, dir=directory, text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(value, stream, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(staged, OWNER_FILE_MODE)
        os.replace(staged, path)
        harden_owner_file(path)
    except BaseException:
        try:
            os.unlink(staged)
        except FileNotFoundError:
            pass
        raise
