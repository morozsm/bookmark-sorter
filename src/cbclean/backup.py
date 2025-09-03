from __future__ import annotations

from pathlib import Path
from .utils import ensure_dir, now_ts


def backup_file(src: Path, dst_dir: Path) -> Path:
    ensure_dir(dst_dir)
    ts = now_ts()
    dst = dst_dir / f"backup-{ts}-{src.name}"
    data = src.read_bytes()
    dst.write_bytes(data)
    return dst

