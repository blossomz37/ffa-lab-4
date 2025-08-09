#!/bin/bash
# Master setup script for Vendetta Protocol Fine-tuning Project

echo "Setting up Vendetta Protocol Fine-tuning Project..."

# Clean up unused directories
echo "Cleaning up unused directories..."
bash cleanup.sh

# Set up directory structure
echo "Setting up directory structure..."
bash setup.sh

# Make scripts executable
echo "Making scripts executable..."
bash make_scripts_executable.sh

# Make tools executable
echo "Making tools executable..."
bash make_tools_executable.sh

echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Configure your OpenAI API key: copy .env.example to .env and set OPENAI_API_KEY"
echo "2. Generate the training dataset: python scripts/prepare_dataset.py"
echo "3. Validate the dataset: python scripts/validate_dataset.py datasets/training_finetune_dataset.jsonl --summary"
echo "4. Submit for fine-tuning: python scripts/finetune_submit.py upload datasets/training_finetune_dataset.jsonl"
echo "5. Generate content with your fine-tuned model: python scripts/generate.py interactive --model YOUR_MODEL_ID"
