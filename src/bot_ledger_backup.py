"""Consistent SQLite backup primitive for the isolated ledger prototype.

Not a scheduler or production backup system. Caller owns encryption, retention,
offsite copy, access controls, and restore procedure.
"""
import os
import sqlite3
from pathlib import Path

def backup_ledger(source_path, destination_path):
    source = Path(source_path).resolve()
    dest = Path(destination_path).resolve()
    if source == dest:
        raise ValueError("backup must differ from source")
    if not source.is_file():
        raise FileNotFoundError(source)
    if dest.exists():
        raise FileExistsError(dest)
    if not dest.parent.is_dir():
        raise FileNotFoundError(dest.parent)
    # Require a live SQLite database: do not create a missing input silently.
    with sqlite3.connect(f"file:{source}?mode=ro", uri=True) as src:
        with sqlite3.connect(dest) as dst:
            src.backup(dst)
            check = dst.execute("PRAGMA integrity_check").fetchone()[0]
            if check != "ok":
                raise RuntimeError("backup integrity check failed")
    os.chmod(dest, 0o600)
    return dest
