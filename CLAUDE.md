# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
This is a novel-writing fine-tuning lab that creates specialized AI models trained on an author's unique writing style. The repository contains a complete pipeline for extracting writing patterns from source materials, creating fine-tuning datasets, and generating content that matches the author's voice across dialogue, narrative, and descriptive prose.

## Commands

### Initial Setup
```bash
# Create virtual environment and install dependencies
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Configure environment (copy .env.example and add your OpenAI API key)
cp .env.example .env
# Edit .env to add: OPENAI_API_KEY=sk-...

# Optional: Run master setup for permissions and structure
bash master_setup.sh

# Verify setup
python check_setup_status.py
```

### Dataset Preparation (No API key required)
```bash
# Build dataset from source materials
python scripts/prepare_dataset.py
# Options: --source_dir, --output_dir, --file_pattern, --ignore_prefix

# Validate before submission
python scripts/validate_dataset.py datasets/training_finetune_dataset.jsonl --summary
```

### Fine-tuning Workflow (API key required)
```bash
# 1. Upload training file
python scripts/finetune_submit.py upload datasets/training_finetune_dataset.jsonl

# 2. Submit fine-tuning job (use file ID from upload)
python scripts/finetune_submit.py submit --training-file file-abc123 --model gpt-3.5-turbo --suffix style-lab

# 3. Monitor job progress
python scripts/finetune_submit.py monitor ftjob-XXXX

# 4. Save job details for records
python scripts/finetune_submit.py save-job ftjob-XXXX --output job_details.json
```

### Testing & Generation (API key + model ID required)
```bash
# Test fine-tuned model (reads FINE_TUNED_MODEL_ID from .env)
python scripts/test_model.py

# Generate content interactively
python scripts/generate.py interactive --model YOUR_FINE_TUNED_MODEL_ID

# Generate with specific template
python scripts/generate.py generate dialogue --model YOUR_FINE_TUNED_MODEL_ID
```

## Architecture Overview

### Dataset Extraction Pipeline
The `prepare_dataset.py` script implements a multi-stage pattern extraction system:
1. **Pattern Detection**: Uses regex patterns to identify dialogue, narrative, descriptive, and plot elements
2. **Context Preservation**: Captures surrounding paragraphs for contextual understanding
3. **Category Classification**: Routes examples to appropriate prompt templates based on content type
4. **JSONL Generation**: Creates OpenAI-compatible conversation format with system/user/assistant roles

### Fine-tuning Data Structure
```json
{
  "messages": [
    {"role": "system", "content": "Creative writing assistant specializing in [CATEGORY]"},
    {"role": "user", "content": "Write [TYPE] about [SCENARIO]"},
    {"role": "assistant", "content": "[EXTRACTED_EXAMPLE] + Context: [SURROUNDING_TEXT]"}
  ]
}
```

### Writing Categories & Templates
Located in `/prompts/`, each JSON template defines:
- **dialogue.json**: Character relationships, speaker attribution, scene context
- **narrative.json**: Scene transitions, action pacing, development beats
- **descriptive_prose.json**: Environmental, emotional, physical, technical descriptions
- **plot_development.json**: Revelations, decisions, conflict escalation

### Model Configuration
- Base Model: GPT-3.5 Turbo (cost-effective for style learning)
- Training Split: 80/20 (training/validation)
- Token Limits: Max 500 tokens per example (prevent overfitting)
- Temperature: 0.7-0.9 for generation (balances creativity/consistency)

## Key Implementation Details

### Environment Variables (.env)
```
OPENAI_API_KEY=sk-...           # Required for API calls
FINE_TUNED_MODEL_ID=ft:gpt...   # Your trained model ID
OPENAI_ORG_ID=                  # Optional: Organization ID
OPENAI_BASE_URL=                # Optional: API proxy endpoint
```

### Source File Naming Conventions
For consistent dataset extraction:
- `chapter_##.md`: Primary narrative content
- `char_*.md`: Character profiles/dialogue samples
- `dossier_*.md`: Style guides and planning documents
- `discard_*.md`: Excluded via `--ignore_prefix discard_`

### API Rate Limits & Error Handling
- Scripts use `tenacity` library for automatic retries
- Exponential backoff on rate limit errors
- Validation runs locally (no API calls) to prevent wasted credits

## Content Safety & Author Context
- Professional novelist creating adult fiction (ages 25-45)
- All characters are fictional adults (25+)
- Content includes mature themes appropriate for the genre
- No minors or non-consensual scenarios in any generated content
