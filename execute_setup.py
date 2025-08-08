#!/usr/bin/env python3
import os
import subprocess

print("Making scripts executable...")
# Change permissions to make scripts executable
os.chmod('/Users/carlo/Lab-4/master_setup.sh', 0o755)
os.chmod('/Users/carlo/Lab-4/setup.sh', 0o755)
os.chmod('/Users/carlo/Lab-4/cleanup.sh', 0o755)
os.chmod('/Users/carlo/Lab-4/make_scripts_executable.sh', 0o755)
os.chmod('/Users/carlo/Lab-4/make_tools_executable.sh', 0o755)

# List scripts in scripts directory
scripts_dir = '/Users/carlo/Lab-4/scripts'
if os.path.exists(scripts_dir):
    for script in os.listdir(scripts_dir):
        if script.endswith('.py'):
            script_path = os.path.join(scripts_dir, script)
            os.chmod(script_path, 0o755)
            print(f"Made executable: {script_path}")

# List scripts in tools directory
tools_dir = '/Users/carlo/Lab-4/tools'
if os.path.exists(tools_dir):
    for tool in os.listdir(tools_dir):
        if tool.endswith('.py'):
            tool_path = os.path.join(tools_dir, tool)
            os.chmod(tool_path, 0o755)
            print(f"Made executable: {tool_path}")

# Execute the master setup script
print("\nExecuting master_setup.sh...")
try:
    result = subprocess.run(['/Users/carlo/Lab-4/master_setup.sh'], 
                           cwd='/Users/carlo/Lab-4',
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
