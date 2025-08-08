# Vendetta Protocol Fine-tuning Project

This repository contains tools for fine-tuning language models on the Vendetta Protocol series writing style. The project aims to create specialized models that can generate content matching the author's unique style, character voices, and narrative techniques.

## Project Structure

- `original documents/`: Source material from the Vendetta Protocol series
- `datasets/`: Contains fine-tuning datasets in JSONL format
- `scripts/`: Python scripts for dataset preparation and fine-tuning
- `prompts/`: Creative writing templates for content generation
- `output/`: Generated content and story drafts
- `tools/`: Utility tools for working with the OpenAI API

## Getting Started

### Prerequisites

- Python 3.9+
- OpenAI API key set as an environment variable (`OPENAI_API_KEY`)

### Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install openai tenacity
   ```

### Dataset Preparation

The project extracts patterns from your writing style and creates fine-tuning datasets:

```bash
python scripts/prepare_dataset.py
```

Options:
- `--source_dir`: Directory containing source materials (default: "../original documents")
- `--output_dir`: Directory to save output files (default: "../datasets")
- `--scan_only`: Only scan source materials, don't generate dataset
- `--upload`: Upload dataset to OpenAI after generation
- `--submit`: Submit fine-tuning job after upload
- `--suffix`: Suffix for the fine-tuned model name
- `--model`: Base model to fine-tune (default: "gpt-3.5-turbo")

### Validating Datasets

Validate your JSONL datasets before submission:

```bash
python scripts/validate_dataset.py datasets/training_finetune_dataset.jsonl --summary
```

Options:
- `--verbose`, `-v`: Print detailed error messages
- `--summary`, `-s`: Print file summary statistics

### Fine-tuning Submission

Submit your datasets for fine-tuning:

```bash
# Upload training file
python scripts/finetune_submit.py upload datasets/training_finetune_dataset.jsonl

# Submit fine-tuning job
python scripts/finetune_submit.py submit --training-file file-abc123 --validation-file file-def456 --model gpt-3.5-turbo --suffix vendetta-protocol
```

Monitor fine-tuning progress:

```bash
python scripts/finetune_submit.py monitor ftjob-abc123
```

### Content Generation

Generate content using your fine-tuned model:

```bash
# Interactive session
python scripts/generate.py interactive --model ft:gpt-3.5-turbo:my-org:vendetta-protocol:abc123

# Generate with specific template
python scripts/generate.py generate character_voice --model ft:gpt-3.5-turbo:my-org:vendetta-protocol:abc123
```

## Fine-tuning Categories

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

## License

This project and its content are for personal use only. All rights to the Vendetta Protocol series content are reserved.
