# Writing Style Fine-tuning Project

This repository contains tools for fine-tuning la### Writing Categories

The training examples are organized into these categories:

1. **Dialogue Writing**
   - Context-aware dialogue patterns
   - Speaker attribution with relationship dynamics
   - Multi-character interactions
   - Scene-specific dialogue

2. **Narrative Writing**
   - Scene transitions and flow
   - Action sequences and pacing
   - Character development moments
   - Story progression

3. **Descriptive Writing**
   - Environmental (settings, locations)
   - Emotional (feelings, atmosphere)
   - Physical (characters, objects)
   - Technical (systems, technology)
   - Atmospheric (mood, ambiance)

4. **Plot Development**
   - Critical discoveries and revelations
   - Character decisions and changes
   - Conflict escalation and resolution
   - Contextual story progression on your writing style. The project helps create specialized models that can generate content matching your preferred writing patterns for dialogue, narrative, and descriptive prose.

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
- Fine-tuned model ID set in .env file (`FINETUNED_MODEL`)

### Setup and Installation

1. Clone this repository
2. Run the master setup script:
   ```bash
   bash master_setup.sh
   ```
   This will:
   - Set up the required directory structure
   - Make all utility scripts executable
   - Configure Python environment
   
3. Install dependencies:
   ```bash
   python -m pip install openai python-dotenv
   ```

4. Create a .env file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your-api-key-here
   ```

5. Test environment setup:
   ```bash
   python scripts/check_setup_status.py
   ```

### Dataset Preparation

The project uses advanced pattern recognition to extract writing samples and create fine-tuning datasets:

```bash
python scripts/prepare_dataset.py
```

Options:
- `--source_dir`: Directory containing source materials (default: "original documents")
- `--output_dir`: Directory to save output files (default: "datasets")

Pattern extraction includes:
- Context-aware dialogue with speaker relationships
- Scene transitions and narrative flow markers
- Multi-category descriptive patterns (environmental, emotional, physical, etc.)
- Plot development with surrounding context
- Character development moments

The script automatically:
1. Processes all markdown files in the source directory
2. Extracts and categorizes writing patterns
3. Creates structured training examples
4. Splits data into training (80%) and validation (20%) sets

### Using the Fine-tuned Model

The project includes a fine-tuned model that has been trained on your writing style. The model ID is stored in your `.env` file as `FINETUNED_MODEL`.

To test the model:
```bash
python scripts/test_model.py
```

The test script will:
1. Load the model ID from your environment
2. Run a series of test prompts covering different writing scenarios
3. Generate responses that match your writing style

You can also use the model in your own scripts by initializing the OpenAI client with your API key and using the model ID from your environment variables.

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
