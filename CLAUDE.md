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
    - `--source_dir`: Directory containing source materials (default: "../original documents")
    - `--output_dir`: Directory to save output files (default: "../datasets")
    - `--scan_only`: Only scan source materials, don't generate dataset
    - `--upload`: Upload dataset to OpenAI after generation
    - `--submit`: Submit fine-tuning job after upload
    - `--suffix`: Suffix for the fine-tuned model name
    - `--model`: Base model to fine-tune (default: "gpt-3.5-turbo")

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
The fine-tuning dataset uses OpenAI's JSONL conversation format:
```json
{
  "messages": [
    {
      "role": "system", 
      "content": "You are a creative writing assistant that specializes in [SPECIFIC_WRITING_ELEMENT], maintaining the style patterns of the Vendetta Protocol series. Focus on [STYLE_GUIDELINE] and [CHARACTER_VOICE]."
    },
    {
      "role": "user", 
      "content": "[INSTRUCTION/REQUEST]"
    },
    {
      "role": "assistant", 
      "content": "[DESIRED_OUTPUT_IN_YOUR_STYLE]"
    }
  ]
}
```

### Core Categories for Training Examples
The training examples are organized into these categories:

1. **Character Voice Development**
   - For maintaining the distinct voices of key characters (Sienna Voss, Rocco Marconi, Carmine Rossi)
   - Includes perspective-specific narration

2. **Descriptive Prose**
   - Technical descriptions (AI systems, digital environments)
   - Emotional descriptions (character feelings, tension)
   - Physical descriptions (settings, people, actions)

3. **Dialogue**
   - Character-specific speech patterns
   - Relationship dynamics between characters

4. **Narrative Style**
   - Overall narrative flow and pacing
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
