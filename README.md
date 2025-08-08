# Writing Style Fine-tuning Project

This repository contains tools for fine-tuning language models on your writing style. The project helps create specialized models that can generate content matching your preferred writing patterns for dialogue, narrative, and descriptive prose.

## Project Structure

- `original documents/`: Your source writing samples
- `datasets/`: Contains fine-tuning datasets in JSONL format
- `scripts/`: Python scripts for dataset preparation
- `prompts/`: Creative writing templates and prompts
- `output/`: Generated content
- `tools/`: Utility tools for working with the OpenAI API

## Getting Started

### Prerequisites

- Python 3.9+
- OpenAI API key set in .env file (`OPENAI_API_KEY`)

### Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install openai python-dotenv
   ```
3. Create a .env file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your-api-key-here
   ```

### Dataset Preparation

The project extracts writing patterns from your samples and creates fine-tuning datasets:

```bash
python scripts/prepare_dataset.py
```

Options:
- `--source_dir`: Directory containing source materials (default: "original documents")
- `--output_dir`: Directory to save output files (default: "datasets")

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

## Writing Categories

The training examples are organized into these categories:

1. **Dialogue Writing**
   - Natural conversation patterns
   - Speaker attribution
   - Character interactions

2. **Narrative Writing**
   - Plot development
   - Action sequences
   - Scene transitions

3. **Descriptive Writing**
   - Sensory details
   - Setting descriptions
   - Character observations

3. **Dialogue**
   - Character-specific speech patterns
   - Relationship dynamics between characters

4. **Narrative Style**
   - Overall narrative flow and pacing
   - Gritty, high-stakes suspense elements
   - Cyber-thriller and organized crime elements

## License

This project and its content are for personal use only. All rights to the Vendetta Protocol series content are reserved.
