# Tools Directory

This directory contains utility tools for the project.

## API Key Manager

The `api_key_manager.py` script can manage OpenAI API keys for different profiles. Prefer using a `.env` file at the repo root for simplicity and portability.

### Usage

```bash
# Preferred: add your key to .env at repo root
# .env
# OPENAI_API_KEY=sk-...your-key...

# Optional: Set API key for a profile via manager
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

The active profile's API key will be set as the `OPENAI_API_KEY` environment variable for the current session. Do not commit real keys to the repo.

## Configuration

API keys and profile information are stored in `api_config.json` in this directory. Do not commit real keys; the default file in this repo contains an empty value.
