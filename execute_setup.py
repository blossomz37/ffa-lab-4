#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path

project_root = Path(__file__).resolve().parent

print("Making scripts executable...")

def make_x(p: Path):
    try:
        os.chmod(p, os.stat(p).st_mode | 0o111)
        print(f"Made executable: {p}")
    except FileNotFoundError:
        print(f"Skip (not found): {p}")

# Shell helpers
for sh in ["master_setup.sh", "setup.sh", "cleanup.sh", "make_scripts_executable.sh", "make_tools_executable.sh"]:
    make_x(project_root / sh)

# Python scripts
for d in [project_root / "scripts", project_root / "tools"]:
    if d.is_dir():
        for f in d.glob("*.py"):
            make_x(f)

# Execute the master setup script
print("\nExecuting master_setup.sh...")
try:
    result = subprocess.run([str(project_root / 'master_setup.sh')],
                            cwd=str(project_root),
                            check=True,
                            text=True,
                            capture_output=True)
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
except subprocess.CalledProcessError as e:
    print(f"Error executing master_setup.sh: {e}")
    print(f"Output: {e.stdout}")
    print(f"Error: {e.stderr}")
