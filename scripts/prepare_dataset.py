#!/usr/bin/env python3
"""
Dataset Builder for Fine-tuning

This script processes writing samples and prepares them as training data for fine-tuning
language models, with a focus on dialogue, narrative, and descriptive writing.
"""

import json
import os
import re
import glob
import random
from typing import List, Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

class DatasetBuilder:
    def __init__(self, source_dir: str, output_dir: str):
        """Initialize the dataset builder
        
        Args:
            source_dir: Directory containing source material
            output_dir: Directory to save output files
        """
        # Load environment variables
        load_dotenv()
        
        # Initialize OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables. Please check your .env file.")
        self.client = OpenAI(api_key=api_key)
        
        # Setup directories
        self.source_dir = source_dir
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize pattern storage
        self.dialogue_patterns = []
        self.narrative_patterns = []
        self.descriptive_patterns = []
        self.plot_patterns = []
        
        # Load prompt templates
        self.prompts = self._load_prompts()
        
    def _load_prompts(self) -> Dict[str, Any]:
        """Load prompt templates from JSON files"""
        prompts = {}
        prompt_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'prompts')
        
        for prompt_file in glob.glob(f"{prompt_dir}/*.json"):
            prompt_type = os.path.splitext(os.path.basename(prompt_file))[0]
            with open(prompt_file, 'r', encoding='utf-8') as f:
                prompts[prompt_type] = json.load(f)
                
        return prompts
    
    def process_files(self) -> None:
        """Process all files in the source directory"""
        print(f"Processing files in {self.source_dir}...")
        
        # Get all markdown files
        markdown_files = glob.glob(f"{self.source_dir}/*.md")
        for file_path in sorted(markdown_files):
            print(f"Processing {os.path.basename(file_path)}...")
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.extract_patterns(content)
            self._process_file(file_path)
            
        print("Scanning complete!")
        
    def _process_dossier(self, file_path):
        """Process the story dossier to extract story structure and character information
        
        Args:
            file_path (str): Path to the dossier file
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract themes
        theme_match = re.search(r'themes:.*?\n((?:- [^\n]+\n)+)', content, re.DOTALL)
        if theme_match:
            self.themes = [t.strip('- ').strip() for t in theme_match.group(1).split('\n') if t.strip()]
            
        # Extract stakes and conflict
        stakes_match = re.search(r'stakes_and_conflict:.*?\n((?:[^\n]+\n)+?)(?:\n|$)', content, re.DOTALL)
        if stakes_match:
            self.stakes = [s.strip() for s in stakes_match.group(1).split('.') if s.strip()]
            
        # Extract character information
        char_sections = re.finditer(r'character_name:\s*([^\n]+).*?(?=character_name:|$)', content, re.DOTALL)
        for char in char_sections:
            char_block = char.group(0)
            name = re.search(r'character_name:\s*([^\n]+)', char_block).group(1).strip().lower()
            role = re.search(r'role(?:_in_prequel)?:\s*([^\n]+)', char_block)
            role = role.group(1) if role else ""
            
            self.characters[name] = {
                'role': role,
                'voice_samples': [],
                'dialogue_samples': []
            }
            
        # Extract relationships and dynamics
        for char1 in self.characters:
            for char2 in self.characters:
                if char1 != char2:
                    key = f"{char1}_{char2}"
                    self.character_relationships[key] = []
                    
    def _process_summary(self, file_path):
        """Process the story summary to extract additional context
        
        Args:
            file_path (str): Path to the summary file
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract high-level plot points and story structure
        # This will help with plot development examples
        plot_points = re.findall(r'^-\s*(.+)$', content, re.MULTILINE)
        for point in plot_points:
            if len(point) > 50:  # Substantial plot point
                self.plot_patterns[len(self.plot_patterns)] = {
                    'content': point,
                    'type': 'major_plot_point'
                }
                    
    def extract_patterns(self, content: str) -> None:
        """Extract writing patterns from content"""
        # Extract dialogue
        dialogue_matches = re.finditer(r'["\']([^"\']+)[\'"][\s,.]+((?:[^."\']+)?(?:said|asked|replied|murmured|whispered|called))', content)
        for match in dialogue_matches:
            self.dialogue_patterns.append({
                'dialogue': match.group(1).strip(),
                'speaker': match.group(2).strip() if match.group(2) else 'character'
            })
        
        # Extract narrative passages (paragraphs with action or plot development)
        narrative_indicators = ['suddenly', 'then', 'finally', 'but', 'however', 'despite', 'realized']
        paragraphs = content.split('\n\n')
        for para in paragraphs:
            if len(para.strip()) > 100:  # Substantial paragraph
                if any(indicator in para.lower() for indicator in narrative_indicators):
                    self.narrative_patterns.append(para.strip())
        
        # Extract descriptive passages (rich in sensory details)
        descriptive_indicators = ['looked', 'felt', 'smelled', 'sounded', 'tasted', 'appeared', 'seemed']
        for para in paragraphs:
            if len(para.strip()) > 100:
                if any(indicator in para.lower() for indicator in descriptive_indicators):
                    self.descriptive_patterns.append(para.strip())
        
        # Extract plot developments
        plot_indicators = ['decided', 'discovered', 'revealed', 'changed', 'learned', 'understood']
        for para in paragraphs:
            if len(para.strip()) > 100:
                if any(indicator in para.lower() for indicator in plot_indicators):
                    self.plot_patterns.append(para.strip())
        
    def _extract_character_voice(self, content, character_name):
        """Extract character voice patterns from content
        
        Args:
            content (str): The file content
            character_name (str): Name of the character to extract voice for
        """
        # For Sienna, look for technical descriptions, idealistic perspectives
        if character_name == "sienna_voss":
            # Simple pattern matching - can be enhanced with NLP
            paragraphs = re.split(r'\n\n+', content)
            for para in paragraphs:
                if "Sienna" in para and len(para) > 200:
                    # Store longer paragraphs focused on Sienna
                    self.character_voices[character_name][len(self.character_voices[character_name])] = para
                    
        # For Rocco, look for strategic thinking, authority, ruthlessness
        elif character_name == "rocco_marconi":
            paragraphs = re.split(r'\n\n+', content)
            for para in paragraphs:
                if ("Rocco" in para or "I " in para) and len(para) > 150:
                    # First-person narrative or mentions of Rocco
                    self.character_voices[character_name][len(self.character_voices[character_name])] = para
                    
        # For Carmine, look for anxiety, detail-oriented descriptions
        elif character_name == "carmine_rossi":
            paragraphs = re.split(r'\n\n+', content)
            for para in paragraphs:
                if "Carmine" in para and len(para) > 150:
                    self.character_voices[character_name][len(self.character_voices[character_name])] = para
    
    def _extract_descriptive_patterns(self, content, desc_type):
        """Extract descriptive writing patterns
        
        Args:
            content (str): The file content
            desc_type (str): Type of description (technical, emotional, physical)
        """
        paragraphs = re.split(r'\n\n+', content)
        
        # Store descriptive paragraphs by type
        if desc_type not in self.descriptive_patterns:
            self.descriptive_patterns[desc_type] = {}
            
        for para in paragraphs:
            # Technical descriptions (AI, code, digital systems)
            if desc_type == "technical" and any(term in para.lower() for term in ["ai", "algorithm", "digital", "code", "argusnet", "server"]):
                if len(para) > 100:
                    self.descriptive_patterns[desc_type][len(self.descriptive_patterns[desc_type])] = para
            
            # Emotional descriptions (character feelings, tension)
            elif desc_type == "emotional" and any(term in para.lower() for term in ["felt", "feeling", "anxiety", "fear", "panic", "tension"]):
                if len(para) > 100:
                    self.descriptive_patterns[desc_type][len(self.descriptive_patterns[desc_type])] = para
            
            # Physical descriptions (settings, people, actions)
            elif desc_type == "physical" and not any(term in para.lower() for term in ["ai", "algorithm", "digital", "code"]):
                if len(para) > 150 and any(term in para.lower() for term in ["room", "office", "face", "body", "stood", "sat"]):
                    self.descriptive_patterns[desc_type][len(self.descriptive_patterns[desc_type])] = para
    
    def _extract_dialogue_patterns(self, content):
        """Extract dialogue patterns from content
        
        Args:
            content (str): The file content
        """
        # Look for any quoted speech with speaker attribution
        dialogue_matches = re.findall(r'["\']([^"\']+)[\'"]\s*(?:,\s*|\.?\s+)([^\.]+?)(?:said|murmured|whispered|spoke|called|replied|asked|answered)', content)
        
        # Also look for dialogue exchanges
        dialogue_exchanges = re.findall(r'["\']([^"\']+)[\'"]\s*(?:[^"\']{1,100})\s*["\']([^"\']+)[\'"]', content)
        
        # Process single dialogue lines
        for i, match in enumerate(dialogue_matches):
            if len(match) >= 2:  # We have the quote and the speaker attribution
                self.dialogue_patterns[len(self.dialogue_patterns)] = {
                    "speaker": match[1].strip(),
                    "dialogue": match[0].strip()
                }
                
                # Add to character voice samples if it's a known character
                speaker_lower = match[1].strip().lower()
                for char_name in self.characters:
                    if char_name in speaker_lower:
                        self.characters[char_name]['dialogue_samples'].append(match[0].strip())
            
        # Process dialogue exchanges
        for i, match in enumerate(dialogue_exchanges):
            if len(match) >= 2:
                self.dialogue_patterns[len(self.dialogue_patterns)] = {
                    "speaker1": match[0],
                    "speaker2": match[1]
                }
    
    def _extract_narrative_patterns(self, content):
        """Extract narrative style patterns
        
        Args:
            content (str): The file content
        """
        # Extract longer narrative paragraphs
        paragraphs = re.split(r'\n\n+', content)
        for para in paragraphs:
            # Skip dialogue-heavy paragraphs
            if para.count('"') < 4 and len(para) > 200:
                self.narrative_patterns[len(self.narrative_patterns)] = para
    
    def create_examples(self) -> List[Dict[str, Any]]:
        """Create training examples from extracted patterns"""
        examples = []
        
        # Create dialogue examples
        for pattern in self.dialogue_patterns:
            example = {
                "messages": [
                    {"role": "system", "content": self.prompts["dialogue"]["system"]},
                    {"role": "user", "content": self.prompts["dialogue"]["user"]},
                    {"role": "assistant", "content": f"\"{pattern['dialogue']}\" {pattern['speaker']} said."}
                ]
            }
            examples.append(example)
        
        # Create narrative examples
        for pattern in self.narrative_patterns:
            example = {
                "messages": [
                    {"role": "system", "content": self.prompts["narrative"]["system"]},
                    {"role": "user", "content": "Write a narrative paragraph that builds tension and advances the plot."},
                    {"role": "assistant", "content": pattern}
                ]
            }
            examples.append(example)
        
        # Create descriptive examples
        for pattern in self.descriptive_patterns:
            example = {
                "messages": [
                    {"role": "system", "content": self.prompts["descriptive_prose"]["system"]},
                    {"role": "user", "content": "Write a descriptive paragraph that creates a vivid scene."},
                    {"role": "assistant", "content": pattern}
                ]
            }
            examples.append(example)
        
        return examples
    
    def generate_datasets(self) -> tuple[str, str]:
        """Generate training and validation datasets
        
        Returns:
            tuple[str, str]: Paths to training and validation files
        """
        examples = self.create_examples()
        random.shuffle(examples)
        
        # Split into training (80%) and validation (20%) sets
        split_point = int(len(examples) * 0.8)
        training_examples = examples[:split_point]
        validation_examples = examples[split_point:]
        
        # Save datasets
        training_path = os.path.join(self.output_dir, 'training_finetune_dataset.jsonl')
        validation_path = os.path.join(self.output_dir, 'validation_finetune_dataset.jsonl')
        
        with open(training_path, 'w', encoding='utf-8') as f:
            for example in training_examples:
                f.write(json.dumps(example) + '\n')
                
        with open(validation_path, 'w', encoding='utf-8') as f:
            for example in validation_examples:
                f.write(json.dumps(example) + '\n')
        
        print(f"\nDataset generation complete!")
        print(f"Training examples: {len(training_examples)}")
        print(f"Validation examples: {len(validation_examples)}")
        print(f"\nFiles saved to:")
        print(f"Training: {training_path}")
        print(f"Validation: {validation_path}")
        
        return training_path, validation_path
    
    def _extract_plot_patterns(self, content):
        """Extract plot development patterns from content
        
        Args:
            content (str): The file content
        """
        # Plot development keywords from the dossier and common narrative elements
        plot_keywords = [
            'motivation', 'conflict', 'plan', 'mission', 'goal', 'discover', 
            'reveal', 'change', 'decision', 'consequence', 'react', 'impact',
            'begin', 'end', 'finally', 'suddenly', 'realize'
        ] + self.themes + [s.split()[0].lower() for s in self.stakes if s]
        
        # Look for paragraphs with plot development
        paragraphs = re.split(r'\n\n+', content)
        for para in paragraphs:
            if len(para) > 100:  # Substantial paragraph
                # Check for plot keywords
                matches = [k for k in plot_keywords if k.lower() in para.lower()]
                if matches:
                    # Check if paragraph advances the plot
                    signals = ['but', 'however', 'suddenly', 'realized', 'decided',
                             'changed', 'discovered', 'revealed', 'finally']
                    has_plot_signal = any(s in para.lower() for s in signals)
                    
                    if has_plot_signal or len(matches) >= 2:
                        self.plot_patterns[len(self.plot_patterns)] = {
                            'content': para,
                            'keywords': matches,
                            'type': 'plot_development'
                        }
                        
                # Look for character development
                for char_name in self.characters:
                    if char_name in para.lower():
                        char_signals = ['felt', 'thought', 'decided', 'realized',
                                      'changed', 'learned', 'understood']
                        if any(s in para.lower() for s in char_signals):
                            self.plot_patterns[len(self.plot_patterns)] = {
                                'content': para,
                                'character': char_name,
                                'type': 'character_development'
                            }

    def _create_dialogue_examples(self) -> List[Dict]:
        """Create training examples for dialogue
        
        Returns:
            List[Dict]: List of formatted training examples
        """
        examples = []
        
        # Character roles and relationships
        character_pairs = [
            ("mentor", "student"),
            ("rival", "competitor"),
            ("authority", "subordinate"),
            ("protagonist", "adversary"),
            ("ally", "confidant")
        ]
        
        # Topics for dialogue
        topics = [
            "discovered threat",
            "crucial information",
            "strategic planning",
            "loyalty question",
            "hidden truth",
            "negotiation",
            "confrontation",
            "revelation"
        ]
        
        # Create examples for each dialogue pattern
        for pattern in self.dialogue_patterns.values():
            if "speaker" in pattern and "dialogue" in pattern:
                # Single line dialogue
                for char_pair in character_pairs:
                    topic = random.choice(topics)
                    example = {
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a creative writing assistant specializing in dialogue. Create natural, character-driven conversations that reveal personality and advance the story."
                            },
                            {
                                "role": "user",
                                "content": f"Write a brief dialogue about {topic} between two characters: {char_pair[0]} and {char_pair[1]}."
                            },
                            {
                                "role": "assistant",
                                "content": f"\"{pattern['dialogue']}\" {pattern['speaker']} said."
                            }
                        ]
                    }
                    examples.append(example)
            
            # For multi-line dialogues
            elif "dialogue1" in pattern and "dialogue2" in pattern:
                for char_pair in character_pairs:
                    topic = random.choice(topics)
                    example = {
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a creative writing assistant specializing in dialogue. Create natural, character-driven conversations that reveal personality and advance the story."
                            },
                            {
                                "role": "user",
                                "content": f"Write a dialogue exchange about {topic} between {char_pair[0]} and {char_pair[1]}."
                            },
                            {
                                "role": "assistant",
                                "content": f"\"{pattern['dialogue1']}\" {char_pair[0]} said.\n\n\"{pattern['dialogue2']}\" {char_pair[1]} replied."
                            }
                        ]
                    }
                    examples.append(example)
                    
        return examples
                "the progress of a digital infiltration",
                "security vulnerabilities in the target system",
                "ethical implications of their actions",
                "detection risks and countermeasures",
                "next steps in their operation"
            ],
            ("Rocco Marconi", "Carmine Rossi"): [
                "the mysterious financial losses",
                "identifying the source of the attacks",
                "consequences of failure",
                "family business security",
                "traditional versus digital threats"
            ],
            ("Rocco Marconi", "Enzo Bellini"): [
                "hunting down the digital attacker",
                "changing tactics to counter the invisible threat",
                "enforcing loyalty in the organization",
                "the future of their operations",
                "assigning responsibilities for the investigation"
            ],
            ("Carmine Rossi", "Leo"): [
                "analyzing the breach data",
                "explaining the severity of the situation",
                "technical details of the intrusion",
                "possible countermeasures",
                "reporting requirements to higher-ups"
            ],
            ("Sienna Voss", "Rocco Marconi"): [
                "a confrontation about digital warfare",
                "philosophical differences about power",
                "mutual respect between adversaries",
                "threats and counter-threats",
                "negotiating boundaries"
            ]
        }
        
        # Use available dialogue patterns and create examples
        dialogue_count = min(len(self.dialogue_patterns), 10)
        for i in range(dialogue_count):
            if i >= len(self.dialogue_patterns):
                break
                
            # Select random character pair and topic
            char_pair = random.choice(character_pairs)
            topic = random.choice(topics[char_pair])
            
            # Create a dialogue example using pattern structure but with character names
            dialogue_content = f"\"{self.dialogue_patterns[i]['speaker1']}\" {char_pair[0]} said, his eyes narrowing.\n\n\"{self.dialogue_patterns[i]['speaker2']}\" {char_pair[1]} replied firmly."
            
            example = {
                "messages": [
                    {
                        "role": "system",
                        "content": f"You are a creative writing assistant specializing in dialogue for the Vendetta Protocol series. Create dialogue that reflects the relationship between {char_pair[0]} and {char_pair[1]}."
                    },
                    {
                        "role": "user",
                        "content": f"Write a dialogue exchange between {char_pair[0]} and {char_pair[1]} about {topic}."
                    },
                    {
                        "role": "assistant",
                        "content": dialogue_content
                    }
                ]
            }
            examples.append(example)
                
        return examples
    
    def _create_narrative_examples(self) -> List[Dict]:
        """Create training examples for narrative style
        
        Returns:
            List[Dict]: List of formatted training examples
        """
        examples = []
        
        # Narrative scenarios
        scenarios = [
            "introducing a new technological threat",
            "revealing a character's hidden motivations",
            "describing the escalation of conflict",
            "exploring the consequences of a digital breach",
            "setting up a confrontation between adversaries",
            "revealing the interconnectedness of the criminal world",
            "showing the vulnerability behind a powerful façade",
            "exploring the clash between traditional and modern power"
        ]
        
        # Create examples from available narrative patterns
        narrative_count = min(len(self.narrative_patterns), 8)
        for i in range(narrative_count):
            if i >= len(self.narrative_patterns):
                break
                
            scenario = scenarios[i % len(scenarios)]
            
            example = {
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a creative writing assistant specializing in narrative prose for the Vendetta Protocol series. Focus on gritty, high-stakes narrative that blends cyber-thriller elements with organized crime drama."
                    },
                    {
                        "role": "user",
                        "content": f"Write a narrative paragraph {scenario} in the style of Vendetta Protocol."
                    },
                    {
                        "role": "assistant",
                        "content": self.narrative_patterns[i]
                    }
                ]
            }
            examples.append(example)
                
        return examples
    
    def _create_plot_examples(self) -> List[Dict]:
        """Create training examples for plot development
        
        Returns:
            List[Dict]: List of formatted training examples
        """
        # This would use the chapter summaries to create plot development examples
        # For now, returning an empty list as implementation depends on specific needs
        return []
    
    def generate_jsonl_dataset(self, output_filename="finetune_dataset.jsonl", validation_split=0.2):
        """Generate JSONL dataset with training examples and validation split
        
        Args:
            output_filename (str): Name of the output file
            validation_split (float): Fraction of data to use for validation
            
        Returns:
            Tuple[str, str]: Paths to training and validation files
        """
        examples = []
        
        # Generate examples from different categories
        character_examples = self._create_character_voice_examples()
        descriptive_examples = self._create_descriptive_examples()
        dialogue_examples = self._create_dialogue_examples()
        narrative_examples = self._create_narrative_examples()
        plot_examples = self._create_plot_examples()
        
        print(f"Generated {len(character_examples)} character voice examples")
        print(f"Generated {len(descriptive_examples)} descriptive writing examples")
        print(f"Generated {len(dialogue_examples)} dialogue examples")
        print(f"Generated {len(narrative_examples)} narrative style examples")
        print(f"Generated {len(plot_examples)} plot development examples")
        
        # Combine all examples
        examples = character_examples + descriptive_examples + dialogue_examples + narrative_examples + plot_examples
        
        # Shuffle and split for validation
        random.shuffle(examples)
        split_index = int(len(examples) * (1 - validation_split))
        training_examples = examples[:split_index]
        validation_examples = examples[split_index:]
        
        print(f"Total examples: {len(examples)}")
        print(f"Training examples: {len(training_examples)}")
        print(f"Validation examples: {len(validation_examples)}")
        
        # Write to output files
        training_path = os.path.join(self.output_dir, f"training_{output_filename}")
        validation_path = os.path.join(self.output_dir, f"validation_{output_filename}")
        
        with open(training_path, 'w', encoding='utf-8') as f:
            for example in training_examples:
                f.write(json.dumps(example) + '\n')
                
        with open(validation_path, 'w', encoding='utf-8') as f:
            for example in validation_examples:
                f.write(json.dumps(example) + '\n')
        
        print(f"Training data saved to: {training_path}")
        print(f"Validation data saved to: {validation_path}")
        
        return training_path, validation_path
    



def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Build fine-tuning dataset from writing samples")
    parser.add_argument("--source_dir", default="original documents",
                       help="Directory containing source materials")
    parser.add_argument("--output_dir", default="datasets",
                       help="Directory to save output files")
    
    args = parser.parse_args()
    
    # Convert relative paths to absolute
    source_dir = os.path.abspath(args.source_dir)
    output_dir = os.path.abspath(args.output_dir)
    
    # Create and run builder
    builder = DatasetBuilder(source_dir, output_dir)
    builder.process_files()
    builder.generate_datasets()

if __name__ == "__main__":
    main()
