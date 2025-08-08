#!/usr/bin/env python3
"""
Content Generation with Fine-tuned Models (student-friendly)

What this script does:
- Loads prompt templates from the prompts/ folder
- Lets you list or inspect templates (no API key required)
- Generates content with your fine-tuned model (API key required)

Adult learner notes:
- Costs: Generation uses credits. Listing templates is free.
- Safety: Keep your API key in .env and never commit it.
- Workflow: Start by listing templates, then try interactive generation with --model.
"""

import os
import json
import argparse
from typing import Dict, Any, List, Optional
from openai import OpenAI
from tenacity import retry, wait_random_exponential, stop_after_attempt
from dotenv import load_dotenv

class ContentGenerator:
    def __init__(self, model_id: str, api_key: Optional[str] = None):
        """Initialize the content generator
        
        Args:
            model_id (str): ID of the fine-tuned model
            api_key (str, optional): OpenAI API key (defaults to environment variable)
        """
        # Load environment variables from .env file (if present)
        load_dotenv()

        # Lazy client creation: we only need the key/client when generating
        self._api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.client: Optional[OpenAI] = None
        self.model_id = model_id
        self.templates = self._load_templates()

    def _ensure_client(self) -> None:
        """Create the OpenAI client on first use.

        Listing and showing templates do not need the client.
        Generation will initialize this if missing.
        """
        if self.client is None:
            if not self._api_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables. Please check your .env file.")
            self.client = OpenAI(api_key=self._api_key)
        
    def _load_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load templates from the templates directory
        
        Returns:
            Dict[str, Dict[str, Any]]: Dictionary of templates
        """
        templates = {}
        templates_dir = os.path.join(os.path.dirname(__file__), "../prompts")
        
        if not os.path.exists(templates_dir):
            print(f"Creating templates directory: {templates_dir}")
            os.makedirs(templates_dir)
            self._create_default_templates(templates_dir)
            
        for filename in os.listdir(templates_dir):
            if filename.endswith(".json"):
                template_path = os.path.join(templates_dir, filename)
                with open(template_path, 'r', encoding='utf-8') as f:
                    template = json.load(f)
                    template_name = os.path.splitext(filename)[0]
                    templates[template_name] = template
                    
        return templates
    
    def _create_default_templates(self, templates_dir: str) -> None:
        """Create default templates
        
        Args:
            templates_dir (str): Path to the templates directory
        """
        default_templates = {
            "character_voice": {
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
            },
            "descriptive_prose": {
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
            },
            "dialogue": {
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
            },
            "narrative": {
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
        }
        
        for template_name, template in default_templates.items():
            template_path = os.path.join(templates_dir, f"{template_name}.json")
            with open(template_path, 'w', encoding='utf-8') as f:
                json.dump(template, f, indent=2)
                
        print(f"Created default templates in {templates_dir}")
    
    def list_templates(self) -> List[str]:
        """List available templates
        
        Returns:
            List[str]: List of template names
        """
        return list(self.templates.keys())
    
    def get_template_details(self, template_name: str) -> Dict[str, Any]:
        """Get details of a template
        
        Args:
            template_name (str): Name of the template
            
        Returns:
            Dict[str, Any]: Template details
        """
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found")
            
        return self.templates[template_name]
    
    @retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
    def generate_content(self, template_name: str, params: Optional[Dict[str, Any]] = None) -> str:
        """Generate content using a template.

        Args:
            template_name (str): Name of the template
            params (Optional[Dict[str, Any]]): Template parameters

        Returns:
            str: Generated content
        """
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found")

        template = self.templates[template_name]

        # Fill in template parameters
        system_prompt = template["system"]
        user_prompt = template["user"]

        if params:
            system_prompt = system_prompt.format(**params)
            user_prompt = user_prompt.format(**params)

        # Generate content
        self._ensure_client()
        # Type assertion for static checkers
        assert self.client is not None
        response = self.client.chat.completions.create(
            model=self.model_id,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )

        content = response.choices[0].message.content or ""
        return content
    
    def fill_template_params(self, template_name: str) -> Dict[str, Any]:
        """Interactively fill template parameters
        
        Args:
            template_name (str): Name of the template
            
        Returns:
            Dict[str, Any]: Filled parameters
        """
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found")
            
        template = self.templates[template_name]
        
        if "parameters" not in template:
            return {}
            
        params = {}
        template_params = template["parameters"]
        
        for param_name, param_values in template_params.items():
            if isinstance(param_values, list):
                # Parameter has a list of possible values
                print(f"\n{param_name}:")
                for i, value in enumerate(param_values):
                    print(f"  {i+1}. {value}")
                    
                choice = input(f"Choose {param_name} (1-{len(param_values)}, or enter custom): ")
                
                try:
                    choice_idx = int(choice) - 1
                    if 0 <= choice_idx < len(param_values):
                        params[param_name] = param_values[choice_idx]
                    else:
                        params[param_name] = choice
                except ValueError:
                    params[param_name] = choice
                    
            elif isinstance(param_values, dict):
                # Parameter has dependent values
                print(f"\n{param_name}:")
                options = list(param_values.keys())
                for i, value in enumerate(options):
                    print(f"  {i+1}. {value}")
                    
                choice = input(f"Choose {param_name} (1-{len(options)}, or enter custom): ")
                
                try:
                    choice_idx = int(choice) - 1
                    if 0 <= choice_idx < len(options):
                        chosen_key = options[choice_idx]
                        params[param_name] = chosen_key
                        
                        # Set dependent value if available
                        dependent_value = param_values[chosen_key]
                        dependent_param = next((p for p in template["system"].split("{") if "}" in p and param_name not in p), None)
                        
                        if dependent_param:
                            dependent_name = dependent_param.split("}")[0]
                            params[dependent_name] = dependent_value
                    else:
                        params[param_name] = choice
                except ValueError:
                    params[param_name] = choice
            else:
                # Simple parameter
                params[param_name] = input(f"{param_name}: ")
                
        return params
    
    def interactive_session(self) -> None:
        """Run an interactive content generation session"""
        print(f"Interactive content generation with model: {self.model_id}")
        print("Type 'exit' to quit, 'templates' to list available templates")
        
        while True:
            command = input("\nCommand: ").strip().lower()
            
            if command == "exit":
                break
                
            elif command == "templates":
                templates = self.list_templates()
                print("\nAvailable templates:")
                for template in templates:
                    print(f"  - {template}")
                    
            elif command in self.templates:
                try:
                    params = self.fill_template_params(command)
                    content = self.generate_content(command, params)
                    
                    print("\nGenerated content:")
                    print("=" * 50)
                    print(content)
                    print("=" * 50)
                    
                    save = input("Save to file? (y/n): ").strip().lower()
                    if save == "y":
                        filename = input("Filename: ").strip()
                        if not filename:
                            filename = f"{command}_output.txt"
                            
                        output_dir = os.path.join(os.path.dirname(__file__), "../output")
                        os.makedirs(output_dir, exist_ok=True)
                        
                        output_path = os.path.join(output_dir, filename)
                        with open(output_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                            
                        print(f"Content saved to {output_path}")
                        
                except Exception as e:
                    print(f"Error: {str(e)}")
                    
            else:
                print(f"Unknown command: {command}")
                print("Type 'exit' to quit, 'templates' to list available templates")


def main():
    """Main function for content generation"""
    parser = argparse.ArgumentParser(description="Generate content using fine-tuned models")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # List templates command
    list_parser = subparsers.add_parser("list", help="List available templates")
    
    # Show template command
    show_parser = subparsers.add_parser("show", help="Show template details")
    show_parser.add_argument("template_name", help="Name of the template")
    
    # Generate content command
    generate_parser = subparsers.add_parser("generate", help="Generate content using a template")
    generate_parser.add_argument("template_name", help="Name of the template")
    generate_parser.add_argument("--model", required=True, help="ID of the fine-tuned model")
    generate_parser.add_argument("--output", help="Path to the output file")
    
    # Interactive content generation command
    interactive_parser = subparsers.add_parser("interactive", help="Interactively generate content")
    interactive_parser.add_argument("--model", required=True, help="ID of the fine-tuned model")
    
    # Parse arguments
    args = parser.parse_args()
    
    if args.command == "list":
        # Just initialize with a placeholder model ID for listing templates
        generator = ContentGenerator("placeholder")
        templates = generator.list_templates()
        print("Available templates:")
        for template in templates:
            print(f"  - {template}")
            
    elif args.command == "show":
        # Just initialize with a placeholder model ID for showing template details
        generator = ContentGenerator("placeholder")
        try:
            template = generator.get_template_details(args.template_name)
            print(f"Template: {args.template_name}")
            print(json.dumps(template, indent=2))
        except ValueError as e:
            print(f"Error: {str(e)}")
            
    elif args.command == "generate":
        generator = ContentGenerator(args.model)
        try:
            params = generator.fill_template_params(args.template_name)
            content = generator.generate_content(args.template_name, params)
            
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Content saved to {args.output}")
            else:
                print("\nGenerated content:")
                print("=" * 50)
                print(content)
                print("=" * 50)
        except Exception as e:
            print(f"Error: {str(e)}")
            
    elif args.command == "interactive":
        generator = ContentGenerator(args.model)
        generator.interactive_session()
        
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
