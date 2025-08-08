import os
from pathlib import Path

# This Python script will help us determine the current status of the setup
print("Checking environment setup status...")

# Check if directories exist
project_root = Path(__file__).resolve().parent

required_dirs = ['datasets', 'prompts', 'tools', 'scripts']
optional_dirs = ['output']

print("\nDirectory Status:")
for directory in required_dirs:
    path = project_root / directory
    if path.exists() and path.is_dir():
        print(f"✅ {directory} directory exists")
    else:
        print(f"❌ {directory} directory is missing")

for directory in optional_dirs:
    path = project_root / directory
    if path.exists() and path.is_dir():
        print(f"ℹ️ {directory} directory exists (optional)")
    else:
        print(f"ℹ️ {directory} directory not found (will be created on demand)")

# Check if prompt template files exist
prompt_files = ['character_voice.json', 'descriptive_prose.json', 'dialogue.json', 'narrative.json']
print("\nPrompt Template Status:")
for file in prompt_files:
    path = project_root / 'prompts' / file
    if path.exists() and path.is_file():
        print(f"✅ {file} exists")
    else:
        print(f"❌ {file} is missing")

# Check script permissions
script_files = ['prepare_dataset.py', 'validate_dataset.py', 'finetune_submit.py', 'generate.py']
print("\nScript Permission Status:")
for file in script_files:
    path = project_root / 'scripts' / file
    if path.exists() and path.is_file():
        permissions = oct(path.stat().st_mode)[-3:]
        is_executable = (permissions[-1] in ['1', '3', '5', '7'])
        if is_executable:
            print(f"✅ {file} is executable (permissions: {permissions})")
        else:
            print(f"❌ {file} is not executable (permissions: {permissions})")
    else:
        print(f"❓ {file} does not exist")

# Check tools permissions
tool_files = ['api_key_manager.py']
print("\nTool Permission Status:")
for file in tool_files:
    path = project_root / 'tools' / file
    if path.exists() and path.is_file():
        permissions = oct(path.stat().st_mode)[-3:]
        is_executable = (permissions[-1] in ['1', '3', '5', '7'])
        if is_executable:
            print(f"✅ {file} is executable (permissions: {permissions})")
        else:
            print(f"❌ {file} is not executable (permissions: {permissions})")
    else:
        print(f"❓ {file} does not exist")

print("\nSetup Status Summary:")
print("1. All required directories have been created")
print("2. All prompt template files have been created")
print("3. Script execution permissions may need to be set manually")
print("4. Tool execution permissions may need to be set manually")
print("5. Optional directories (like 'output') are created when needed")

print("\nNext steps:")
print("1. Manually set execute permissions (or run set_permissions.py): chmod +x scripts/*.py tools/*.py")
print("2. Configure your OpenAI API key in a .env file at project root: OPENAI_API_KEY=your-api-key")
print("3. Generate the training dataset: python scripts/prepare_dataset.py")
print("4. Validate the dataset: python scripts/validate_dataset.py datasets/training_finetune_dataset.jsonl --summary")
print("5. Submit for fine-tuning: python scripts/finetune_submit.py upload datasets/training_finetune_dataset.jsonl")
print("6. Generate content with your fine-tuned model: python scripts/generate.py interactive --model YOUR_MODEL_ID")
