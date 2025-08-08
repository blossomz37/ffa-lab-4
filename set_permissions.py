#!/usr/bin/env python3
"""Set executable permissions for project scripts in a repo-friendly way.

This script:
- Uses paths relative to the repo (no user-specific absolute paths)
- Sets +x on Python scripts in scripts/ and tools/
- Sets +x on any shell scripts (*.sh) in the repo root
- Skips missing files gracefully

Note: On Windows, execute bits are largely ignored; this script is most
useful on POSIX systems and CI environments (e.g., GitHub Actions).
"""

import os
import stat
from pathlib import Path


def make_executable(path: Path) -> bool:
    """Ensure the file at path has executable bits set for user/group/others.

    Returns True if chmod was applied successfully, False otherwise.
    """
    try:
        mode = path.stat().st_mode
        new_mode = mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
        if new_mode != mode:
            os.chmod(path, new_mode)
        return True
    except FileNotFoundError:
        print(f"Skip (not found): {path}")
        return False
    except PermissionError:
        print(f"Skip (permission denied): {path}")
        return False
    except OSError as e:
        print(f"Skip ({e.__class__.__name__}): {path} -> {e}")
        return False


def collect_targets(project_root: Path) -> list[Path]:
    targets: list[Path] = []

    scripts_dir = project_root / "scripts"
    tools_dir = project_root / "tools"

    if scripts_dir.is_dir():
        targets.extend(sorted(scripts_dir.glob("*.py")))

    if tools_dir.is_dir():
        targets.extend(sorted(tools_dir.glob("*.py")))

    # Shell scripts in repo root
    targets.extend(sorted(project_root.glob("*.sh")))

    # De-duplicate while preserving order
    seen = set()
    unique_targets = []
    for t in targets:
        if t not in seen:
            unique_targets.append(t)
            seen.add(t)
    return unique_targets


def main() -> int:
    project_root = Path(__file__).resolve().parent

    print("Setting executable permissions...")
    targets = collect_targets(project_root)

    if not targets:
        print("No target files found (scripts/, tools/, or *.sh in repo root).")
        return 0

    made = 0
    for path in targets:
        if make_executable(path):
            made += 1
            print(f"+x set: {path.relative_to(project_root)}")

    print(f"Done. Updated {made}/{len(targets)} files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
