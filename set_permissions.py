#!/usr/bin/env python3
import os

print("Making scripts executable...")

scripts = [
    '/Users/carlo/Lab-4/scripts/prepare_dataset.py',
    '/Users/carlo/Lab-4/scripts/validate_dataset.py',
    '/Users/carlo/Lab-4/scripts/finetune_submit.py',
    '/Users/carlo/Lab-4/scripts/generate.py'
]

for script in scripts:
    os.chmod(script, 0o755)
    print(f"Made executable: {script}")

print("Making tools executable...")
os.chmod('/Users/carlo/Lab-4/tools/api_key_manager.py', 0o755)
print("Made executable: /Users/carlo/Lab-4/tools/api_key_manager.py")

print("All scripts are now executable.")
