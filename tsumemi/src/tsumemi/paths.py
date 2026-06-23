from __future__ import annotations

import os

_PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
RESOURCES_ROOT = os.path.normpath(os.path.join(_PACKAGE_DIR, "..", "..", "resources"))


def resource_path(*parts: str) -> str:
    return os.path.join(RESOURCES_ROOT, *parts)
