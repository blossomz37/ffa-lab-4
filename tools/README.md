# Tools Directory

This directory contains utility tools for the Vendetta Protocol Fine-tuning Project.

## API Key Manager

The `api_key_manager.py` script helps manage OpenAI API keys for different profiles.

### Usage

```bash
# Set API key for a profile
python api_key_manager.py set sk-your-api-key-here --profile project1

# Get API key for current active profile
python api_key_manager.py get

# Get API key for specific profile
python api_key_manager.py get --profile project1

# List all profiles
python api_key_manager.py list

# Set active profile
python api_key_manager.py active project1

# Delete a profile
python api_key_manager.py delete project1
```

The active profile's API key will be automatically set as the `OPENAI_API_KEY` environment variable for the current session.

## Configuration

API keys and profile information are stored in `api_config.json` in this directory. Do not share this file as it contains sensitive information.
