from __future__ import annotations

import os
import shutil
from pathlib import Path

from tsumemi.src.tsumemi import files


def kifu_library_dir(app_paths: object) -> Path:
    """Return persistent directory for imported KIF/KIFU files."""
    data_dir = getattr(app_paths, "user_data_dir", None) or getattr(
        app_paths, "data", None
    )
    base = Path(data_dir) if data_dir else Path.home() / ".tsumemimobile"
    library = base / "kifus"
    library.mkdir(parents=True, exist_ok=True)
    return library


def list_kifu_files(library: Path) -> list[str]:
    return sorted(files.get_kif_files(library, recursive=False))


def import_kifu_files(source_paths: list[str], library: Path) -> list[str]:
    """Copy KIF/KIFU files into app storage; return destination paths."""
    imported: list[str] = []
    for src in source_paths:
        name = os.path.basename(src)
        if not name.endswith((".kif", ".kifu")):
            continue
        dest = library / name
        shutil.copy2(src, dest)
        imported.append(str(dest))
    return imported


def import_demo_kifus(demo_dir: Path, library: Path) -> list[str]:
    """Seed library from bundled demo problems."""
    sources = sorted(files.get_kif_files(demo_dir, recursive=False))
    return import_kifu_files(list(sources), library)


def resource_path(relative: str) -> Path:
    """Locate bundled resources (demo kifus) in dev and Briefcase builds."""
    start = Path(__file__).resolve().parent
    for base in [start, *start.parents]:
        candidate = base / "resources" / relative
        if candidate.is_dir():
            return candidate
    return start.parents[3] / "resources" / relative
