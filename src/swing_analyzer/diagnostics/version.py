"""Semver comparison utilities."""

from __future__ import annotations

import re


def parse_version(version: str) -> tuple[int, ...]:
    cleaned = version.strip()
    match = re.search(r"(\d+(?:\.\d+)*)", cleaned)
    if not match:
        raise ValueError(f"cannot parse version from: {version}")
    return tuple(int(part) for part in match.group(1).split("."))


def compare_versions(detected: str, minimum: str) -> int:
    """Return -1 if detected < minimum, 0 if equal, 1 if detected > minimum."""
    detected_parts = parse_version(detected)
    minimum_parts = parse_version(minimum)
    length = max(len(detected_parts), len(minimum_parts))
    detected_padded = detected_parts + (0,) * (length - len(detected_parts))
    minimum_padded = minimum_parts + (0,) * (length - len(minimum_parts))
    if detected_padded < minimum_padded:
        return -1
    if detected_padded > minimum_padded:
        return 1
    return 0


def version_meets_minimum(detected: str, minimum: str) -> bool:
    return compare_versions(detected, minimum) >= 0
