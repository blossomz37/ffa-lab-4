#!/usr/bin/env python3
"""
Vendetta Protocol Fine-tuning Dataset Builder

This script processes writing samples from the Vendetta Protocol series and
prepares them as training data for fine-tuning language models.
"""

import json
import os
import re
import glob
import io
import random
from typing import List, Dict, Any, Tuple, Optional
from tenacity import retry, wait_random_exponential, stop_after_attempt
from openai import OpenAI
from dotenv import load_dotenv

class FineTuneDatasetBuilder:
    def __init__(self, source_dir, output_dir):
        """Initialize the dataset builder with source and output directories.
        
        Args:
            source_dir (str): Directory containing source material
            output_dir (str): Directory to save output files
        """
        # Load environment variables from .env file
        load_dotenv()
        
        self.source_dir = source_dir
        self.output_dir = output_dir
        self.style_patterns = {}
        self.character_voices = {
            "sienna_voss": {},
            "rocco_marconi": {},
            "carmine_rossi": {}
        }
        self.narrative_patterns = {}
        self.descriptive_patterns = {}
        self.dialogue_patterns = {}
        
        # Initialize OpenAI client with API key from environment
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables. Please check your .env file.")
        self.client = OpenAI(api_key=api_key)
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
    def scan_source_materials(self):
        """Scan all source materials and extract writing patterns"""
        print(f"Scanning source materials in {self.source_dir}...")
        
        chapter_files = sorted(glob.glob(f"{self.source_dir}/Vendetta_Protocol_Chapter_*.md"))
        dossier_files = glob.glob(f"{self.source_dir}/*dossier*.md")
        
        for file_path in chapter_files + dossier_files:
            print(f"Processing {os.path.basename(file_path)}...")
            self._process_file(file_path)
            
        print("Scanning complete!")
        
    def _process_file(self, file_path):
        """Process individual file to extract style elements
        
        Args:
            file_path (str): Path to the file to process
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        filename = os.path.basename(file_path)
        
        # Extract character dialogue and perspectives based on chapter focus
        if "Chapter_1" in filename or "Chapter_2" in filename or "Chapter_5" in filename:
            # These chapters focus on Sienna Voss
            self._extract_character_voice(content, "sienna_voss")
            self._extract_descriptive_patterns(content, "technical")
            
        if "Chapter_3" in filename:
            # This chapter focuses on Carmine Rossi
            self._extract_character_voice(content, "carmine_rossi")
            self._extract_descriptive_patterns(content, "emotional")
            
        if "Chapter_4" in filename:
            # This chapter focuses on Rocco Marconi
            self._extract_character_voice(content, "rocco_marconi")
            self._extract_descriptive_patterns(content, "physical")
            
        # Extract dialogue patterns from all chapters
        self._extract_dialogue_patterns(content)
        
        # Extract narrative style from all files
        self._extract_narrative_patterns(content)
        
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
        # Look for dialogue patterns with quotes
        dialogue_matches = re.findall(r'"([^"]+)"[^"]+?"([^"]+)"', content)
        
        for i, match in enumerate(dialogue_matches):
            if len(match) >= 2:  # Ensure we have a dialogue exchange
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
    
    def _create_character_voice_examples(self) -> List[Dict]:
        """Create training examples for character voice
        
        Returns:
            List[Dict]: List of formatted training examples
        """
        examples = []
        
        # Character voice examples for each character
        for character, paragraphs in self.character_voices.items():
            if not paragraphs:
                continue
                
            display_name = character.replace("_", " ").title()
            
            # Characteristics by character
            characteristics = {
                "sienna_voss": "technical brilliance, idealism, determination, analytical thinking",
                "rocco_marconi": "ruthless authority, strategic thinking, cold calculation, traditional power",
                "carmine_rossi": "nervous energy, detail-oriented, fear of failure, procedural thinking"
            }
            
            # Scenarios by character
            scenarios = {
                "sienna_voss": [
                    "observing ArgusNet's operations",
                    "planning a digital attack",
                    "analyzing data from a breach",
                    "reflecting on the criminal underworld",
                    "working with complex technology"
                ],
                "rocco_marconi": [
                    "confronting a subordinate",
                    "planning to identify a threat",
                    "reflecting on the family's operations",
                    "dealing with a breach in security",
                    "considering the future of the organization"
                ],
                "carmine_rossi": [
                    "discovering financial irregularities",
                    "reporting problems to superiors",
                    "trying to understand the AI threat",
                    "feeling pressure from above",
                    "analyzing business operations"
                ]
            }
            
            # Create examples for this character
            for i, (_, paragraph) in enumerate(paragraphs.items()):
                if i >= 5:  # Limit number of examples per character
                    break
                    
                scenario = random.choice(scenarios[character])
                
                example = {
                    "messages": [
                        {
                            "role": "system",
                            "content": f"You are a creative writing assistant specializing in character voice development for the Vendetta Protocol series. Maintain the specific voice of {display_name} characterized by {characteristics[character]}."
                        },
                        {
                            "role": "user",
                            "content": f"Write a paragraph from {display_name}'s perspective about {scenario}."
                        },
                        {
                            "role": "assistant",
                            "content": paragraph
                        }
                    ]
                }
                examples.append(example)
                
        return examples
    
    def _create_descriptive_examples(self) -> List[Dict]:
        """Create training examples for descriptive writing
        
        Returns:
            List[Dict]: List of formatted training examples
        """
        examples = []
        
        for desc_type, paragraphs in self.descriptive_patterns.items():
            if not paragraphs:
                continue
                
            # Elements to describe by type
            elements = {
                "technical": [
                    "an advanced AI system breaching security",
                    "a digital attack on financial networks",
                    "a secure hacker workspace",
                    "the processing of stolen data",
                    "a cybersecurity defense system"
                ],
                "emotional": [
                    "the tension during a financial crisis",
                    "the fear of an unknown threat",
                    "the anxiety of losing control",
                    "the paranoia within a criminal organization",
                    "the growing frustration of a trapped operative"
                ],
                "physical": [
                    "a crime boss's private office",
                    "a clandestine meeting between criminals",
                    "a high-tech urban apartment",
                    "the physical manifestation of digital power",
                    "a confrontation between rivals"
                ]
            }
            
            style_focus = {
                "technical": "technical precision and futuristic terminology",
                "emotional": "psychological depth and emotional intensity",
                "physical": "sensory details and atmospheric elements"
            }
            
            # Create examples for this description type
            for i, (_, paragraph) in enumerate(paragraphs.items()):
                if i >= 5:  # Limit number of examples per type
                    break
                    
                element = random.choice(elements[desc_type])
                
                example = {
                    "messages": [
                        {
                            "role": "system",
                            "content": f"You are a creative writing assistant specializing in descriptive prose for the Vendetta Protocol series. Focus on {desc_type} descriptions with emphasis on {style_focus[desc_type]}."
                        },
                        {
                            "role": "user",
                            "content": f"Describe {element} in the style of Vendetta Protocol."
                        },
                        {
                            "role": "assistant",
                            "content": paragraph
                        }
                    ]
                }
                examples.append(example)
                
        return examples
    
    def _create_dialogue_examples(self) -> List[Dict]:
        """Create training examples for dialogue
        
        Returns:
            List[Dict]: List of formatted training examples
        """
        examples = []
        
        # Character pairs for dialogue
        character_pairs = [
            ("Sienna Voss", "ArgusNet AI Interface"),
            ("Rocco Marconi", "Carmine Rossi"),
            ("Rocco Marconi", "Enzo Bellini"),
            ("Carmine Rossi", "Leo"),
            ("Sienna Voss", "Rocco Marconi")
        ]
        
        # Topics by character pair
        topics = {
            ("Sienna Voss", "ArgusNet AI Interface"): [
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
    
    @retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
    def upload_file(self, file_path, purpose="fine-tune"):
        """Upload file to OpenAI with retries
        
        Args:
            file_path (str): Path to the file to upload
            purpose (str): Purpose of the file
            
        Returns:
            str: ID of the uploaded file
        """
        print(f"Uploading {file_path} to OpenAI...")
        with open(file_path, "rb") as file:
            response = self.client.files.create(file=file, purpose=purpose)
        print(f"File uploaded with ID: {response.id}")
        return response.id
    
    def submit_fine_tuning_job(self, training_file_id, validation_file_id, model="gpt-3.5-turbo", suffix=None):
        """Submit fine-tuning job to OpenAI
        
        Args:
            training_file_id (str): ID of the training file
            validation_file_id (str): ID of the validation file
            model (str): Base model to fine-tune
            suffix (str): Suffix for the fine-tuned model name
            
        Returns:
            str: ID of the fine-tuning job
        """
        print(f"Submitting fine-tuning job for model {model}...")
        job = self.client.fine_tuning.jobs.create(
            training_file=training_file_id,
            validation_file=validation_file_id,
            model=model,
            suffix=suffix
        )
        print(f"Fine-tuning job submitted with ID: {job.id}")
        return job.id
    
    def evaluate_model(self, fine_tuned_model, test_prompts, base_model="gpt-3.5-turbo"):
        """Compare fine-tuned model against base model
        
        Args:
            fine_tuned_model (str): ID of the fine-tuned model
            test_prompts (List[Dict]): List of test prompts
            base_model (str): Base model to compare against
            
        Returns:
            Dict: Evaluation results
        """
        results = {
            "fine_tuned": [],
            "base": []
        }
        
        print(f"Evaluating fine-tuned model {fine_tuned_model} against {base_model}...")
        
        for i, prompt in enumerate(test_prompts):
            print(f"Testing prompt {i+1}/{len(test_prompts)}...")
            
            # Get response from fine-tuned model
            ft_response = self.client.chat.completions.create(
                model=fine_tuned_model,
                messages=[
                    {"role": "system", "content": prompt["system"]},
                    {"role": "user", "content": prompt["user"]}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            # Get response from base model
            base_response = self.client.chat.completions.create(
                model=base_model,
                messages=[
                    {"role": "system", "content": prompt["system"]},
                    {"role": "user", "content": prompt["user"]}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            results["fine_tuned"].append({
                "prompt": prompt,
                "response": ft_response.choices[0].message.content
            })
            
            results["base"].append({
                "prompt": prompt,
                "response": base_response.choices[0].message.content
            })
        
        # Save results to file
        results_path = os.path.join(self.output_dir, "evaluation_results.json")
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
            
        print(f"Evaluation results saved to: {results_path}")
        return results


def main():
    """Main function to run the dataset builder"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Build fine-tuning dataset from Vendetta Protocol source materials")
    parser.add_argument("--source_dir", default="../original documents", help="Directory containing source materials")
    parser.add_argument("--output_dir", default="../datasets", help="Directory to save output files")
    parser.add_argument("--scan_only", action="store_true", help="Only scan source materials, don't generate dataset")
    parser.add_argument("--upload", action="store_true", help="Upload dataset to OpenAI after generation")
    parser.add_argument("--submit", action="store_true", help="Submit fine-tuning job after upload")
    parser.add_argument("--suffix", default=None, help="Suffix for the fine-tuned model name")
    parser.add_argument("--model", default="gpt-3.5-turbo", help="Base model to fine-tune")
    
    args = parser.parse_args()
    
    builder = FineTuneDatasetBuilder(args.source_dir, args.output_dir)
    builder.scan_source_materials()
    
    if args.scan_only:
        print("Scan complete. Exiting without generating dataset.")
        return
    
    training_path, validation_path = builder.generate_jsonl_dataset()
    
    if args.upload:
        training_file_id = builder.upload_file(training_path)
        validation_file_id = builder.upload_file(validation_path)
        
        if args.submit:
            job_id = builder.submit_fine_tuning_job(
                training_file_id, 
                validation_file_id,
                model=args.model,
                suffix=args.suffix
            )
            print(f"Fine-tuning job submitted with ID: {job_id}")


if __name__ == "__main__":
    main()
