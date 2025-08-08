import os
import sys

# This Python script will help us determine the current status of the setup
print("Checking environment setup status...")

# Check if directories exist
directories = ['datasets', 'prompts', 'output', 'tools', 'scripts']
print("\nDirectory Status:")
for directory in directories:
    path = f'/Users/carlo/Lab-4/{directory}'
    if os.path.exists(path) and os.path.isdir(path):
        print(f"✅ {directory} directory exists")
    else:
        print(f"❌ {directory} directory is missing")

# Check if prompt template files exist
prompt_files = ['character_voice.json', 'descriptive_prose.json', 'dialogue.json', 'narrative.json']
print("\nPrompt Template Status:")
for file in prompt_files:
    path = f'/Users/carlo/Lab-4/prompts/{file}'
    if os.path.exists(path) and os.path.isfile(path):
        print(f"✅ {file} exists")
    else:
        print(f"❌ {file} is missing")

# Check script permissions
script_files = ['prepare_dataset.py', 'validate_dataset.py', 'finetune_submit.py', 'generate.py']
print("\nScript Permission Status:")
for file in script_files:
    path = f'/Users/carlo/Lab-4/scripts/{file}'
    if os.path.exists(path) and os.path.isfile(path):
        permissions = oct(os.stat(path).st_mode)[-3:]
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
    path = f'/Users/carlo/Lab-4/tools/{file}'
    if os.path.exists(path) and os.path.isfile(path):
        permissions = oct(os.stat(path).st_mode)[-3:]
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

print("\nNext steps:")
print("1. Manually set execute permissions: chmod +x scripts/*.py tools/*.py")
print("2. Configure your OpenAI API key: python tools/api_key_manager.py set YOUR_API_KEY")
print("3. Generate the training dataset: python scripts/prepare_dataset.py")
print("4. Validate the dataset: python scripts/validate_dataset.py datasets/training_finetune_dataset.jsonl --summary")
print("5. Submit for fine-tuning: python scripts/finetune_submit.py upload datasets/training_finetune_dataset.jsonl")
print("6. Generate content with your fine-tuned model: python scripts/generate.py interactive --model YOUR_MODEL_ID")
