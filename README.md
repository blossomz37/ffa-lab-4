# Writing Style Fine‑tuning Lab

This lab walks you through producing a small fine‑tuning dataset from narrative source material, validating it, submitting a fine‑tune job, and then using the resulting model for generation. All code is intentionally lightweight and heavily commented so you can adapt it to your own genre and style.

Use this repository as a *reference implementation*, not a black box. Read the comments, experiment with parameters, and iterate on your dataset quality.

---
## Learning Objectives
After completing this lab you should be able to:
1. Extract structured training examples (dialogue, narrative, description, plot development) from raw draft text.
2. Inspect and validate JSONL fine‑tuning datasets before spending credits.
3. Submit and monitor an OpenAI fine‑tuning job responsibly.
4. Run quick smoke tests on a fine‑tuned model and judge stylistic alignment.
5. Safely manage API keys using a `.env` file (never hard‑coding secrets).

---
## Key Concepts & Example Categories
The dataset builder classifies extracted passages into four instructional categories. Understanding these helps you reason about balance and coverage.

1. **Dialogue Writing**
   - Speaker attribution & relationship hints
   - Context‑aware exchanges
   - Multi‑character interactions
2. **Narrative Writing**
   - Scene transitions & pacing markers
   - Action / escalation cues
   - Character development beats
3. **Descriptive Writing**
   - Environmental (locations, setting)
   - Emotional & atmospheric tone
   - Physical / technical details
4. **Plot Development**
   - Discoveries & revelations
   - Decisions & consequence pivots
   - Conflict escalation / resolution

> Tip: Your *goal* isn’t to shove in everything—curate high‑quality, representative style slices. Quality > quantity.

---
## Project Structure

| Path | Purpose |
|------|---------|
| `original documents/` | Source draft markdown files (sample set included) |
| `datasets/` | Generated training / validation JSONL files |
| `prompts/` | JSON prompt templates (customize for your style) |
| `scripts/` | Python scripts (dataset prep, validation, fine‑tune, generation) |
| `output/` | (Optional) Saved generations from interactive runs |
| `tools/` | Utility helpers (API key manager, etc.) |

---
## Prerequisites
* Python 3.9+
* An OpenAI API key (only required for fine‑tune submission & generation)
* A virtual environment is recommended

> You can run dataset preparation & validation **without** an API key. The key is only needed for: `finetune_submit.py`, `generate.py`, and `test_model.py`.

---
## Quick Start (Happy Path)
```bash
# 1. Clone repository & enter it
git clone <your-fork-url>
cd ffa-lab-4

# 2. Create virtual environment (recommended)
python -m venv .venv && source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy env template & add your key (keep this file private!)
cp .env.example .env
echo "OPENAI_API_KEY=sk-..." >> .env

# 5. (Optional) Run setup helper
bash master_setup.sh

# 6. Build dataset (no key needed)
python scripts/prepare_dataset.py

# 7. Validate it
python scripts/validate_dataset.py datasets/training_finetune_dataset.jsonl --summary

# 8. Upload & submit fine‑tune (replace FILE IDs after upload)
python scripts/finetune_submit.py upload datasets/training_finetune_dataset.jsonl
# -> note returned file-id e.g. file-abc123
python scripts/finetune_submit.py submit --training-file file-abc123 --model gpt-4.1-nano-2025-04-14 --suffix style-lab

# 9. Monitor job
python scripts/finetune_submit.py monitor ftjob-XXXX

# 10. Test model once it succeeds
python scripts/test_model.py

# 11. Generate interactively
python scripts/generate.py interactive --model YOUR_FINE_TUNED_MODEL_ID
```

---
## Detailed Setup
1. Run the master setup (optional convenience):
   ```bash
   bash master_setup.sh
   ```
2. Install dependencies (alternative to above if you skip helper):
   ```bash
   pip install -r requirements.txt
   ```
3. Create `.env` from template:
   ```bash
   cp .env.example .env
   # then edit .env to add OPENAI_API_KEY and (later) FINE_TUNED_MODEL_ID
   ```
4. Confirm structure & permissions:
   ```bash
   python check_setup_status.py
   ```

---
## Dataset Preparation
Runs locally—no API calls.
```bash
python scripts/prepare_dataset.py
```
Options:
- `--source_dir` (default: `"original documents"`)
- `--output_dir` (default: `datasets`)
- `--file_pattern` (default: `*.md`) select a subset like `chapter_*.md`
- `--ignore_prefix` skip files starting with given prefix (repeatable)

### Recommended Naming Conventions (Students)
Adopt consistent, sortable names so ordering is predictable:

| Pattern | Example | Purpose |
|---------|---------|---------|
| `chapter_01.md` | chapter_01.md | Primary narrative sequence |
| `chapter_02.md` | chapter_02.md | Natural sort keeps order |
| `lore_*` | lore_factions.md | Background / world info (can ignore) |
| `char_*` | char_sienna.md | Character dossiers |
| `dossier_*` | dossier_style_guide.md | Story planning dossier (style guide, premise, outlines) |
| `discard_*` | discard_oldscene.md | Outdated (ignored via `--ignore_prefix discard_`) |

Ignore strategy examples:
```bash
python scripts/prepare_dataset.py --ignore_prefix discard_ --ignore_prefix lore_ --file_pattern "*.md"
```

If you want to exclude planning materials entirely you could also add `--ignore_prefix dossier_`; otherwise they're included and can provide stylistic context.

What happens:
1. Parses markdown documents.
2. Extracts candidate paragraphs via pattern heuristics (dialogue, descriptive, narrative, plot cues).
3. Builds conversation‑style training examples (`messages` list).
4. Shuffles & splits 80/20 into training / validation JSONL.

> Iterate: Adjust source docs or prompt templates, rerun, revalidate.

---
## Dataset Validation
Always validate before uploading (free, local):
```bash
python scripts/validate_dataset.py datasets/training_finetune_dataset.jsonl --summary
```
Useful flags:
- `--summary` Gives aggregate stats.
- `--verbose` Lists every structural issue.

Look for:
- Balanced category counts (not all descriptive, etc.)
- Reasonable avg tokens (avoid overly long examples early on)
- Proper role alternation ending with assistant

---
## Fine‑tuning Workflow
Upload then submit:
```bash
python scripts/finetune_submit.py upload datasets/training_finetune_dataset.jsonl
# -> Capture returned file id
python scripts/finetune_submit.py submit --training-file file-abc123 --model gpt-4.1-nano-2025-04-14 --suffix style-lab
```
Monitor:
```bash
python scripts/finetune_submit.py monitor ftjob-abc123
```
List jobs/models:
```bash
python scripts/finetune_submit.py list-jobs --limit 5
python scripts/finetune_submit.py list-models
```
Save details (for reports or grading):
```bash
python scripts/finetune_submit.py save-job ftjob-abc123 --output job_details.json
```

> Cost Reminder: Fine‑tuning consumes credits. Start with *small, high‑quality* sets.

---
## Testing & Generation
Smoke‑test your resulting model ID (store it in `.env` as `FINE_TUNED_MODEL_ID`):
```bash
python scripts/test_model.py
```
Interactive / template generation:
```bash
python scripts/generate.py list
python scripts/generate.py generate dialogue --model YOUR_FINE_TUNED_MODEL_ID
python scripts/generate.py interactive --model YOUR_FINE_TUNED_MODEL_ID
```
Listing / showing templates does *not* require an API key; actual generation does.

---
## Customizing Prompts
Edit JSON files in `prompts/`:
- Add or remove parameter arrays.
- Keep placeholders (`{character}`, `{scenario}`, etc.) consistent.
- Maintain a clear, *concise* `system` instruction (overly long instructions can dilute style learning).

After edits, re‑run generation or dataset prep as needed.

---
## Troubleshooting & Pitfalls
| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| `OPENAI_API_KEY not found` | Missing `.env` or var name mismatch | Copy `.env.example`, set key, restart shell |
| Zero dialogue examples | Source material lacks quote patterns | Add richer dialogue passages or adjust regex in `prepare_dataset.py` |
| Model outputs generic prose | Dataset too descriptive / unbalanced | Add more dialogue/narrative variety; trim repetitive examples |
| Fine‑tune stuck in `queued` | High service load | Wait; avoid re‑submitting duplicates |
| Validation role errors | Improper message sequence | Inspect offending lines with `--verbose` and repair generator logic |

> Debug Strategy: Start with a *tiny* dataset (20–30 examples) to validate pipeline speedily; scale only after correctness.

---
## Improving Quality (Extension Ideas)
- Add a script to compute distinctiveness / redundancy metrics.
- Implement a token length histogram to prune extremes.
- Introduce automated lexical style checks (e.g., adjective density).
- Add evaluation prompts & capture outputs for rubric‑based scoring.

---
## Safety & Ethics
- Don’t include sensitive or private data in training examples.
- Attribute or remove any third‑party copyrighted content.
- Keep keys private; rotate them if accidentally exposed.

---
## License / Usage
This lab (scripts + structure) is for educational use. All included sample narrative content (Vendetta Protocol materials) is provided for classroom experimentation—do **not** redistribute or publish commercially. Adapt with your own text for real projects.

---
## Attribution
If you extend this lab, consider adding a CHANGELOG or “Instructor Notes” section so future students can follow evolution clearly.

Happy experimenting—iterate thoughtfully and measure results!

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
- Fine-tuned model ID set in .env file (`FINE_TUNED_MODEL_ID`)

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

4. Create a .env file with your OpenAI API key (start from .env.example):
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

The project includes a fine-tuned model that has been trained on your writing style. The model ID is stored in your `.env` file as `FINE_TUNED_MODEL_ID`.

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
python scripts/finetune_submit.py submit --training-file file-abc123 --validation-file file-def456 --model gpt-4.1-nano-2025-04-14 --suffix vendetta-protocol
```

Monitor fine-tuning progress:

```bash
python scripts/finetune_submit.py monitor ftjob-abc123
```

### Content Generation

Generate content using your fine-tuned model:

```bash
# Interactive session
python scripts/generate.py interactive --model ft:gpt-4.1-nano-2025-04-14:my-org:vendetta-protocol:abc123

# Generate with specific template
python scripts/generate.py generate character_voice --model ft:gpt-4.1-nano-2025-04-14:my-org:vendetta-protocol:abc123
```

## Writing Categories

<!-- (Removed duplicate category section & simplified license moved earlier) -->
