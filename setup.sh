#!/bin/bash
# Setup and organize directory structure for the Vendetta Protocol Fine-tuning Project

# Remove old empty directories if they exist
rm -rf dpo_finetune finetune

# Create required directories if they don't exist
mkdir -p datasets
mkdir -p prompts
mkdir -p output
mkdir -p tools

# Create initial template files
cat > prompts/character_voice.json << 'EOL'
{
  "system": "You are a creative writing assistant specializing in character voice development for the Vendetta Protocol series. Maintain the specific voice of {character} characterized by {traits}.",
  "user": "Write a paragraph from {character}'s perspective about {scenario}.",
  "parameters": {
    "character": ["Sienna Voss", "Rocco Marconi", "Carmine Rossi"],
    "traits": {
      "Sienna Voss": "technical brilliance, idealism, determination, analytical thinking",
      "Rocco Marconi": "ruthless authority, strategic thinking, cold calculation, traditional power",
      "Carmine Rossi": "nervous energy, detail-oriented, fear of failure, procedural thinking"
    },
    "scenario": [
      "discovering a security breach",
      "planning a counterattack",
      "reflecting on recent events",
      "confronting an enemy",
      "making a crucial decision"
    ]
  }
}
EOL

cat > prompts/descriptive_prose.json << 'EOL'
{
  "system": "You are a creative writing assistant specializing in descriptive prose for the Vendetta Protocol series. Focus on {desc_type} descriptions with emphasis on {style_focus}.",
  "user": "Describe {element} in the style of Vendetta Protocol.",
  "parameters": {
    "desc_type": ["technical", "emotional", "physical"],
    "style_focus": {
      "technical": "technical precision and futuristic terminology",
      "emotional": "psychological depth and emotional intensity",
      "physical": "sensory details and atmospheric elements"
    },
    "element": [
      "a high-tech urban apartment",
      "a digital breach into a secure network",
      "a clandestine meeting between criminals",
      "the tension during a confrontation",
      "a criminal's private office"
    ]
  }
}
EOL

cat > prompts/dialogue.json << 'EOL'
{
  "system": "You are a creative writing assistant specializing in dialogue for the Vendetta Protocol series. Create dialogue that reflects the relationship between {character_a} and {character_b}.",
  "user": "Write a dialogue exchange between {character_a} and {character_b} about {topic}.",
  "parameters": {
    "character_a": ["Sienna Voss", "Rocco Marconi", "Carmine Rossi"],
    "character_b": ["ArgusNet AI Interface", "Enzo Bellini", "Leo"],
    "topic": [
      "a security breach",
      "identifying the source of attacks",
      "planning the next move",
      "trust and betrayal",
      "the future of their operation"
    ]
  }
}
EOL

cat > prompts/narrative.json << 'EOL'
{
  "system": "You are a creative writing assistant specializing in narrative prose for the Vendetta Protocol series. Focus on gritty, high-stakes narrative that blends cyber-thriller elements with organized crime drama.",
  "user": "Write a narrative paragraph {scenario} in the style of Vendetta Protocol.",
  "parameters": {
    "scenario": [
      "introducing a new technological threat",
      "revealing a character's hidden motivations",
      "describing the escalation of conflict",
      "exploring the consequences of a digital breach",
      "setting up a confrontation between adversaries"
    ]
  }
}
EOL

# Make all Python scripts executable
chmod +x scripts/prepare_dataset.py
chmod +x scripts/validate_dataset.py
chmod +x scripts/finetune_submit.py
chmod +x scripts/generate.py

echo "Directory structure has been set up and organized."
echo "Template files have been created in the prompts directory."
echo "All scripts are now executable."
