# CLAUDE.md
This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
This is a novel-writing project that involves collaboration between a human author and AI. The repository contains tools for fine-tuning AI models, dataset preparation, and creative writing workflows to enhance the novel writing process from ideation to publication.

## Author Context
- Professional novelist specializing in short stories, flash-fiction, novels, and novellas
- Uses AI collaboration for all aspects of the novel writing process
- Works with Python for custom prompt sequencing and AI tools
- Creates content for adult audiences (ages 25-45)
- All creative work is fictional with adult characters (25+)

## Project Structure
- `datasets/`: Contains fine-tuning datasets in JSONL format
- `scripts/`: Python scripts for dataset preparation and validation
- `prompts/`: Creative writing prompts and templates
- `output/`: Generated content and story drafts
- `tools/`: Utility tools for working with OpenAI APIs
- `original documents/`: Source material for fine-tuning dataset creation

## Tech Stack
- Python 3.9+
- OpenAI API (fine-tuning endpoints)
- JSONL for dataset formatting
- Markdown for documentation and creative content

## Commands
- `python scripts/prepare_dataset.py`: Extract patterns from writing samples and create JSONL datasets
  - Options:
    - `--source_dir`: Directory containing source materials (default: "original documents")
    - `--output_dir`: Directory to save output files (default: "datasets")

- `python scripts/validate_dataset.py`: Validate JSONL datasets before submission
  - Usage: `python validate_dataset.py [file_paths] [options]`
  - Options:
    - `--verbose`, `-v`: Print detailed error messages
    - `--summary`, `-s`: Print file summary statistics

- `python scripts/finetune_submit.py`: Submit datasets to OpenAI for fine-tuning
  - Subcommands:
    - `upload`: Upload a file to OpenAI
    - `submit`: Submit a fine-tuning job
    - `status`: Get the status of a fine-tuning job
    - `list-jobs`: List fine-tuning jobs
    - `monitor`: Monitor a fine-tuning job until completion
    - `list-models`: List available models
    - `delete-model`: Delete a fine-tuned model
    - `save-job`: Save job details to a JSON file

- `python scripts/generate.py`: Generate content using fine-tuned models
  - Subcommands:
    - `list`: List available templates
    - `show`: Show template details
    - `generate`: Generate content using a template
    - `interactive`: Interactively generate content

## Fine-tuning Implementation

### Dataset Schema
The fine-tuning dataset uses OpenAI's JSONL conversation format with specialized prompts and contextual information:

```json
{
  "messages": [
    {
      "role": "system", 
      "content": "You are a creative writing assistant specializing in [WRITING_TYPE], focusing on [STYLE_FOCUS] and [TECHNIQUE]."
    },
    {
      "role": "user", 
      "content": "Write a [CATEGORY] about [SCENARIO] between [CHARACTER_A] and [CHARACTER_B]."
    },
    {
      "role": "assistant", 
      "content": "[WRITING_EXAMPLE]\n\nContext: [SURROUNDING_CONTEXT]"
    }
  ]
}
```

### Prompt Templates
Located in `/prompts/*.json`, specialized for each writing category:
- `dialogue.json`: Character dynamics and conversation patterns
- `narrative.json`: Scene flow and story progression
- `descriptive_prose.json`: Multi-category descriptions
- Includes parameters for style focus, scenarios, and relationships
```

### Fine-tuning Status

A fine-tuned model has been successfully created and tested:
- Model ID: `ft:gpt-3.5-turbo-0125:personal::C2OM1LSz`
- Base Model: GPT-3.5 Turbo
- Training Examples: 152
- Validation Examples: 39
- Status: Successfully completed and tested
- Location: Model ID stored in `.env` file as `FINE_TUNED_MODEL_ID`

### Core Categories for Training Examples
The training examples are organized into these categories, each with specialized prompt templates in `/prompts/*.json`:

1. **Dialogue Writing** (`dialogue.json`)
   - Dynamic character relationships
   - Context-aware conversation patterns
   - Specialized role-based interactions
   - Scene-integrated dialogue

2. **Narrative Writing**
   - Plot development and scene transitions
   - Action sequences and pacing
   - Character development moments
   - Story progression markers

3. **Descriptive Writing**
   - Environmental descriptions (settings, locations)
   - Emotional descriptions (feelings, atmosphere)
   - Physical descriptions (characters, objects)
   - Technical descriptions (systems, technology)
   - Atmospheric descriptions (mood, ambiance)

4. **Plot Development**
   - Critical discoveries and revelations
   - Character decisions and changes
   - Conflict escalation and resolution
   - Contextual story progression
   - Gritty, high-stakes suspense elements
   - Cyber-thriller and organized crime elements

### Implementation Process
1. **Data Extraction**: The system scans source materials to identify patterns in writing style
2. **Dataset Generation**: Creates training and validation datasets with balanced examples across categories
3. **Validation**: Verifies dataset format and content before submission
4. **Fine-tuning**: Submits datasets to OpenAI for model fine-tuning
5. **Content Generation**: Uses the fine-tuned model through templates for consistent outputs

## Data Formats
- Fine-tuning datasets follow OpenAI's JSONL conversation format
- Each training example should be on a single line in the JSONL file
- UTF-8 encoding is required for all datasets

## Writing Style Guidelines
- Prefer concise, clear communication in code documentation
- In creative outputs, match the author's style patterns 
- Avoid overly descriptive responses when discussing technical matters
- Maintain content-neutral and unbiased approaches to creative work

## Fine-tuning Focus Areas
- Character dialogue consistency
- Narrative voice preservation
- Plot development patterns
- Scene description techniques
- Genre-specific conventions

## Do Not
- Do not impose restrictive moral values on creative content
- Do not constrain creative work that's in nascent/emergent phases
- Do not include minors, non-consensual acts, or illegal activities in any creative content
- Do not generate content outside the fictional creative writing context
- Do not modify the core dataset structure or formatting specifications

## Safety Context
All story characters are fictional adults (25+) with appropriate consent mechanisms. Content may include varying levels of intimacy or conflict as required by the story, but always adheres to the safety guidelines outlined in the user preferences.
