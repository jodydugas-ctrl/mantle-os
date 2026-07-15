#!/usr/bin/env python3
"""Small persistence primitives shared by Mantle Body checkpoints."""
from __future__ import annotations

import json
import os
from pathlib import Path
import stat
import tempfile
from typing import Any


OWNER_DIRECTORY_MODE = 0o700
OWNER_FILE_MODE = 0o600
_STAGE_PREFIX = ".mantle-stage-"


def _refuse_symbolic_links(path: str) -> None:
    """Reject a symlink at the path or in any existing parent component."""
    absolute = Path(path).absolute()
    proc_fd = Path("/proc/self/fd")
    try:
        proc_parts = absolute.relative_to(proc_fd).parts
    except ValueError:
        proc_parts = ()
    if proc_parts and proc_parts[0].isdigit():
        descriptor = int(proc_parts[0])
        if not stat.S_ISDIR(os.fstat(descriptor).st_mode):
            raise NotADirectoryError(f"persistence descriptor is not a directory: {descriptor}")
        current = proc_fd / proc_parts[0]
        nodes = []
        for component in proc_parts[1:]:
            current /= component
            nodes.append(current)
    else:
        nodes = [*reversed(absolute.parents), absolute]
    for node in nodes:
        try:
            info = node.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode):
            raise OSError(f"persistence path contains a symbolic link: {node}")


def ensure_owner_directory(path: str) -> None:
    """Create or harden a state directory so only its owner can traverse it."""
    _refuse_symbolic_links(path)
    os.makedirs(path, mode=OWNER_DIRECTORY_MODE, exist_ok=True)
    _refuse_symbolic_links(path)
    if not hasattr(os, "O_DIRECTORY") or not hasattr(os, "fchmod"):
        os.chmod(path, OWNER_DIRECTORY_MODE)
        return
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags)
    try:
        if not stat.S_ISDIR(os.fstat(fd).st_mode):
            raise NotADirectoryError(path)
        os.fchmod(fd, OWNER_DIRECTORY_MODE)
    finally:
        os.close(fd)


def harden_owner_file(path: str) -> None:
    """Remove group/world permissions from a persisted artifact."""
    _refuse_symbolic_links(path)
    if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "fchmod"):
        os.chmod(path, OWNER_FILE_MODE)
        return
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise OSError(f"persisted artifact is not a regular file: {path}")
        os.fchmod(fd, OWNER_FILE_MODE)
    finally:
        os.close(fd)


def atomic_write_json(path: str, value: Any) -> None:
    """Serialize JSON beside its destination, fsync it, then atomically replace."""
    directory = os.path.dirname(os.path.abspath(path))
    ensure_owner_directory(directory)
    _refuse_symbolic_links(path)
    fd, staged = tempfile.mkstemp(prefix=_STAGE_PREFIX, dir=directory, text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(value, stream, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(staged, OWNER_FILE_MODE)
        _refuse_symbolic_links(path)
        os.replace(staged, path)
        harden_owner_file(path)
    except BaseException:
        try:
            os.unlink(staged)
        except FileNotFoundError:
            pass
        raise
