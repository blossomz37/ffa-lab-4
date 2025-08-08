#!/usr/bin/env python3
"""Dataset Builder for Fine-tuning (no API key required)

What this script does:
- Reads your source texts from the "original documents" folder
- Extracts patterns (dialogue, narrative, descriptive, plot cues)
- Formats examples into JSONL for training/validation

Recommended naming conventions (you can still use others):
- chapter_01.md, chapter_02.md ... main narrative sequence
- char_<name>.md character dossiers (char_sienna.md)
- lore_<topic>.md setting / world-building (lore_factions.md)
- dossier_<aspect>.md planning docs like style guide, premise, outline (dossier_outline.md)
- discard_<anything>.md outdated pieces you want to skip

To exclude any category supply --ignore_prefix for each (e.g. --ignore_prefix discard_ --ignore_prefix dossier_).

Notes for students:
- You do NOT need an OpenAI API key to run this script.
- Output files go to the datasets/ folder.
- Iterate safely: edit sources, re-run, then validate again.
"""

import json
import os
import re
import glob
import random
from typing import List, Dict, Any, Optional, Iterable

class DatasetBuilder:
    def __init__(self, source_dir: str, output_dir: str, file_pattern: str = "*.md", ignore_prefixes: Optional[Iterable[str]] = None):
        """Initialize the dataset builder.

        Args:
            source_dir: Directory containing source material (markdown files).
            output_dir: Directory to save output JSONL datasets.
            file_pattern: Glob pattern to match source files (default: *.md).
            ignore_prefixes: Iterable of filename prefixes (e.g. ("draft_", "old_")) to skip.

        Notes:
            - No API calls are made here; everything is local text processing.
            - Natural sorting is applied so chapter2 comes before chapter10.
        """
        self.source_dir = source_dir
        self.output_dir = output_dir
        self.file_pattern = file_pattern
        self.ignore_prefixes = tuple(ignore_prefixes) if ignore_prefixes else tuple()
        os.makedirs(output_dir, exist_ok=True)

        # Initialize pattern storage
        self.dialogue_patterns: List[Dict[str, Any]] = []
        self.narrative_patterns: List[str] = []
        self.descriptive_patterns: List[Dict[str, Any]] = []
        self.plot_patterns: List[Dict[str, Any]] = []

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
    
    def _natural_key(self, name: str):
        """Return a key for natural sorting (chapter2 before chapter10)."""
        import re as _re
        return [int(text) if text.isdigit() else text.lower() for text in _re.split(r'(\d+)', name)]

    def process_files(self) -> None:
        """Process all matching files in the source directory respecting ignore rules."""
        print(f"Processing files in {self.source_dir} (pattern: {self.file_pattern})...")

        pattern_path = os.path.join(self.source_dir, self.file_pattern)
        candidate_files = glob.glob(pattern_path)

        def _is_ignored(filename: str) -> bool:
            base = os.path.basename(filename)
            if base.startswith('.'):
                return True
            return any(base.startswith(pref) for pref in self.ignore_prefixes)

        markdown_files = [f for f in candidate_files if f.lower().endswith('.md') and not _is_ignored(f)]
        markdown_files.sort(key=lambda p: self._natural_key(os.path.basename(p)))

        if not markdown_files:
            print("⚠️  No source files matched. Adjust naming or pattern.")
            return

        # Report category counts (helps students verify naming)
        categories = {"chapter_":0, "char_":0, "lore_":0, "dossier_":0, "discard_":0, "other":0}
        for fp in markdown_files:
            base = os.path.basename(fp).lower()
            matched = False
            for pref in list(categories.keys())[:-1]:  # exclude 'other'
                if base.startswith(pref):
                    categories[pref] += 1
                    matched = True
                    break
            if not matched:
                categories["other"] += 1
        print("Category counts:")
        for k,v in categories.items():
            print(f"  {k:<9} {v}")

        for file_path in markdown_files:
            print(f"Processing {os.path.basename(file_path)}...")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.extract_patterns(content)
            except UnicodeDecodeError:
                print(f"Skipping (decode error): {file_path}")
            except OSError as e:
                print(f"Skipping ({e.__class__.__name__}): {file_path} -> {e}")
        
        print("\nProcessing complete!")
        print(f"Found {len(self.dialogue_patterns)} dialogue patterns")
        print(f"Found {len(self.narrative_patterns)} narrative patterns")
        print(f"Found {len(self.descriptive_patterns)} descriptive patterns")
        print(f"Found {len(self.plot_patterns)} plot patterns")
        

    def extract_patterns(self, content: str) -> None:
        """Extract writing patterns from content"""
        paragraphs = content.split('\n\n')
        
        for i, para in enumerate(paragraphs):
            para = para.strip()
            if len(para) < 100:  # Skip short paragraphs
                continue
                
            # Extract dialogue with context
            dialogue_matches = list(re.finditer(r'["\']([^"\']+)[\'"][\s,.]+((?:[^."\']+)?(?:said|asked|replied|murmured|whispered|called))', para))
            if dialogue_matches:
                context = para  # Full paragraph for context
                for match in dialogue_matches:
                    self.dialogue_patterns.append({
                        'dialogue': match.group(1).strip(),
                        'speaker': match.group(2).strip() if match.group(2) else 'character',
                        'context': context
                    })
            
            # Extract scene transitions
            transition_indicators = ['later', 'meanwhile', 'that evening', 'the next day', 'moments later', 'hours later']
            if any(indicator in para.lower() for indicator in transition_indicators):
                self.narrative_patterns.append(para)
                
            # Extract character development moments
            character_dev_indicators = [
                'realized', 'understood', 'felt', 'decided', 'changed', 
                'remembered', 'questioned', 'wondered', 'recognized'
            ]
            if any(indicator in para.lower() for indicator in character_dev_indicators):
                self.narrative_patterns.append(para)
            
            # Extract action and plot development
            action_indicators = [
                'suddenly', 'quickly', 'immediately', 'rushed', 'leaped',
                'spun', 'grabbed', 'attacked', 'defended', 'escaped'
            ]
            if any(indicator in para.lower() for indicator in action_indicators):
                self.narrative_patterns.append(para)
            
            # Extract descriptive passages
            descriptive_indicators = {
                'environmental': ['room', 'building', 'city', 'street', 'office', 'space'],
                'emotional': ['felt', 'feeling', 'emotion', 'anxiety', 'fear', 'hope'],
                'physical': ['looked', 'appeared', 'wore', 'carried', 'moved'],
                'atmospheric': ['air', 'light', 'shadow', 'silence', 'sound'],
                'technical': ['system', 'code', 'network', 'device', 'screen', 'data']
            }
            
            for desc_type, indicators in descriptive_indicators.items():
                if any(indicator in para.lower() for indicator in indicators):
                    self.descriptive_patterns.append({
                        'content': para,
                        'type': desc_type
                    })
            
            # Extract plot developments with context
            plot_indicators = [
                'discovered', 'revealed', 'changed', 'learned', 'understood',
                'planned', 'decided', 'confronted', 'escaped', 'succeeded', 'failed'
            ]
            matches = [k for k in plot_indicators if k in para.lower()]
            if matches:
                # Get surrounding context if available
                context_start = max(0, i - 1)
                context_end = min(len(paragraphs), i + 2)
                context = '\n\n'.join(paragraphs[context_start:context_end])
                
                self.plot_patterns.append({
                    'content': para,
                    'context': context,
                    'keywords': matches,
                    'type': 'plot_development'
                })
        
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
        for match in dialogue_matches:
            if len(match) >= 2:  # We have the quote and the speaker attribution
                self.dialogue_patterns.append({
                    "speaker": match[1].strip(),
                    "dialogue": match[0].strip()
                })
            
        # Process dialogue exchanges
        for match in dialogue_exchanges:
            if len(match) >= 2:
                self.dialogue_patterns.append({
                    "dialogue": match[0].strip() + ' ' + match[1].strip(),
                    "speaker": "multiple"
                })
    
    def _extract_narrative_patterns(self, content):
        """Extract narrative style patterns
        
        Args:
            content (str): The file content
        """
        # Extract longer narrative paragraphs
        paragraphs = re.split(r'\n\n+', content)
        for para in paragraphs:
            # Skip dialogue-heavy paragraphs
            if para.count('"') < 4 and len(para.strip()) > 200:
                self.narrative_patterns.append(para.strip())
    
    def create_examples(self) -> List[Dict[str, Any]]:
        """Create training examples from extracted patterns"""
        examples = []
        
        # Create dialogue examples
        for pattern in self.dialogue_patterns:
            # Format system prompt with character roles if available
            system_prompt = self.prompts["dialogue"]["system"].replace(
                "{character_a}", "the speaker"
            ).replace(
                "{character_b}", "the listener"
            )
            
            example = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "Write a dialogue line with speaker attribution and context."},
                    {
                        "role": "assistant", 
                        "content": f"\"{pattern['dialogue']}\" {pattern['speaker']} said.\n\nContext: {pattern.get('context', '')}"
                    }
                ]
            }
            examples.append(example)
        
        # Create narrative examples
        for pattern in self.narrative_patterns:
            # Get pattern type based on content
            if "suddenly" in pattern.lower() or "quickly" in pattern.lower():
                scenario = "an action sequence"
            elif "later" in pattern.lower() or "meanwhile" in pattern.lower():
                scenario = "a scene transition"
            elif "realized" in pattern.lower() or "felt" in pattern.lower():
                scenario = "a character development moment"
            else:
                scenario = "advancing the plot"
                
            user_prompt = self.prompts["narrative"]["user"].replace("{scenario}", scenario)
            
            example = {
                "messages": [
                    {"role": "system", "content": self.prompts["narrative"]["system"]},
                    {"role": "user", "content": user_prompt},
                    {"role": "assistant", "content": pattern}
                ]
            }
            examples.append(example)
        
        # Create descriptive examples
        for pattern in self.descriptive_patterns:
            desc_type = pattern.get('type', 'physical')
            content = pattern.get('content', pattern)  # Fallback for old format
            
            system_prompt = self.prompts["descriptive_prose"]["system"].replace(
                "{desc_type}", desc_type
            ).replace(
                "{style_focus}", self.prompts["descriptive_prose"]["parameters"]["style_focus"].get(desc_type, "sensory details")
            )
            
            # Select appropriate element based on type
            elements = self.prompts["descriptive_prose"]["parameters"]["element"]
            if desc_type == "environmental":
                element = "a significant location"
            elif desc_type == "emotional":
                element = "a tense confrontation scene"
            elif desc_type == "technical":
                element = "a complex system or process"
            else:
                element = elements[0]
                
            user_prompt = self.prompts["descriptive_prose"]["user"].replace("{element}", element)
            
            example = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                    {"role": "assistant", "content": content}
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
        # Plot development keywords
        plot_keywords = [
            'motivation', 'conflict', 'plan', 'mission', 'goal', 'discover', 
            'reveal', 'change', 'decision', 'consequence', 'react', 'impact',
            'begin', 'end', 'finally', 'suddenly', 'realize'
        ]
        
        # Look for paragraphs with plot development
        paragraphs = content.split('\n\n')
        for para in paragraphs:
            if len(para.strip()) > 100:  # Substantial paragraph
                # Check for plot keywords
                matches = [k for k in plot_keywords if k.lower() in para.lower()]
                if matches:
                    # Check if paragraph advances the plot
                    signals = ['but', 'however', 'suddenly', 'realized', 'decided',
                             'changed', 'discovered', 'revealed', 'finally']
                    has_plot_signal = any(s in para.lower() for s in signals)
                    
                    if has_plot_signal or len(matches) >= 2:
                        self.plot_patterns.append({
                            'content': para.strip(),
                            'keywords': matches,
                            'type': 'plot_development'
                        })

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
        for pattern in self.dialogue_patterns:
            # Randomly select a character pair and topic
            char_pair = random.choice(character_pairs)
            topic = random.choice(topics)
            
            if pattern["speaker"] == "multiple":
                # It's a dialogue exchange
                dialogues = pattern["dialogue"].split('" "')  # Split at dialogue boundary
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
                            "content": f"\"{dialogues[0]}\" {char_pair[0]} said.\n\n\"{dialogues[1]}\" {char_pair[1]} replied."
                        }
                    ]
                }
            else:
                # Single line dialogue
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
        examples = []
        
        # Plot scenario templates
        scenarios = {
            'discovered': 'a character discovering a crucial plot element',
            'revealed': 'revealing a hidden truth',
            'changed': 'a significant change in circumstances',
            'planned': 'characters planning their next move',
            'confronted': 'a confrontation between key characters',
            'escaped': 'characters escaping a dangerous situation',
            'failed': 'dealing with failure and its consequences',
            'succeeded': 'achieving a goal with unexpected results'
        }
        
        for pattern in self.plot_patterns:
            # Get the primary plot development type
            keywords = pattern.get('keywords', [])
            plot_type = keywords[0] if keywords else 'general'
            scenario = scenarios.get(plot_type, 'advancing the plot')
            
            example = {
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a creative writing assistant specializing in plot development for high-stakes thrillers. Focus on creating compelling story developments that maintain tension and reader engagement."
                    },
                    {
                        "role": "user",
                        "content": f"Write a scene about {scenario}. Include context and consequences."
                    },
                    {
                        "role": "assistant",
                        "content": pattern.get('content', '') + '\n\nContext: ' + pattern.get('context', '')
                    }
                ]
            }
            examples.append(example)
                
        return examples
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
    



def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Build fine-tuning dataset from writing samples")
    parser.add_argument("--source_dir", default="original documents",
                       help="Directory containing source materials")
    parser.add_argument("--output_dir", default="datasets",
                       help="Directory to save output files")
    parser.add_argument("--file_pattern", default="*.md",
                        help="Glob pattern to select source files (default: *.md)")
    parser.add_argument("--ignore_prefix", action="append", default=[],
                        help="Filename prefix to ignore (repeatable). Common: discard_, dossier_, lore_, draft_, old_")
    
    args = parser.parse_args()
    
    # Convert relative paths to absolute
    source_dir = os.path.abspath(args.source_dir)
    output_dir = os.path.abspath(args.output_dir)
    
    # Create and run builder
    builder = DatasetBuilder(source_dir, output_dir,
                             file_pattern=args.file_pattern,
                             ignore_prefixes=args.ignore_prefix)
    builder.process_files()
    builder.generate_datasets()

if __name__ == "__main__":
    main()
