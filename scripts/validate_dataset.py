#!/usr/bin/env python3
"""
JSONL Dataset Validator for OpenAI Fine-tuning

This script validates JSONL files for OpenAI fine-tuning, checking for proper
format, token limits, and other requirements.
"""

import json
import os
import sys
import argparse
from typing import List, Dict, Any, Tuple, Optional

def validate_jsonl(file_path: str, verbose: bool = False) -> Tuple[bool, List[str]]:
    """Validate a JSONL file for OpenAI fine-tuning
    
    Args:
        file_path (str): Path to the JSONL file
        verbose (bool): Whether to print detailed error messages
        
    Returns:
        Tuple[bool, List[str]]: (is_valid, error_messages)
    """
    errors = []
    line_number = 0
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_number, line in enumerate(f, 1):
                try:
                    # Check if line is valid JSON
                    example = json.loads(line)
                    
                    # Check for required fields
                    if not isinstance(example, dict):
                        errors.append(f"Line {line_number}: Not a JSON object")
                        continue
                        
                    if "messages" not in example:
                        errors.append(f"Line {line_number}: Missing 'messages' field")
                        continue
                        
                    messages = example["messages"]
                    
                    if not isinstance(messages, list) or len(messages) < 2:
                        errors.append(f"Line {line_number}: 'messages' must be a list with at least 2 entries")
                        continue
                        
                    # Check message format
                    for i, msg in enumerate(messages):
                        if not isinstance(msg, dict):
                            errors.append(f"Line {line_number}, message {i}: Not a JSON object")
                            continue
                            
                        if "role" not in msg:
                            errors.append(f"Line {line_number}, message {i}: Missing 'role' field")
                            continue
                            
                        if "content" not in msg:
                            errors.append(f"Line {line_number}, message {i}: Missing 'content' field")
                            continue
                            
                        role = msg["role"]
                        if role not in ["system", "user", "assistant"]:
                            errors.append(f"Line {line_number}, message {i}: Invalid role '{role}'")
                            continue
                            
                        content = msg["content"]
                        if not isinstance(content, str) or not content.strip():
                            errors.append(f"Line {line_number}, message {i}: 'content' must be a non-empty string")
                            continue
                            
                    # Check conversation format
                    roles = [msg["role"] for msg in messages]
                    
                    # Last message must be from assistant
                    if roles[-1] != "assistant":
                        errors.append(f"Line {line_number}: Last message must be from 'assistant'")
                        
                    # Check for alternating user/assistant messages (except for optional system at start)
                    start_idx = 0
                    if roles[0] == "system":
                        start_idx = 1
                        
                    for i in range(start_idx, len(roles) - 1):
                        if roles[i] == "user" and roles[i+1] != "assistant":
                            errors.append(f"Line {line_number}: 'user' message must be followed by 'assistant'")
                        elif roles[i] == "assistant" and roles[i+1] != "user":
                            errors.append(f"Line {line_number}: 'assistant' message must be followed by 'user'")
                            
                    # Rough token count estimate (not accurate but gives a warning)
                    total_tokens = sum(len(msg["content"].split()) * 1.3 for msg in messages)
                    if total_tokens > 4096:
                        errors.append(f"Line {line_number}: Estimated token count ({int(total_tokens)}) exceeds 4096 limit")
                        
                except json.JSONDecodeError:
                    errors.append(f"Line {line_number}: Invalid JSON")
                except Exception as e:
                    errors.append(f"Line {line_number}: {str(e)}")
                    
    except Exception as e:
        errors.append(f"Error reading file: {str(e)}")
        
    is_valid = len(errors) == 0
    
    if verbose:
        if is_valid:
            print(f"✅ File {file_path} is valid")
            print(f"Total examples: {line_number}")
        else:
            print(f"❌ File {file_path} has {len(errors)} errors:")
            for error in errors:
                print(f"  - {error}")
                
    return is_valid, errors

def summarize_jsonl(file_path: str) -> Dict[str, Any]:
    """Generate a summary of a JSONL file
    
    Args:
        file_path (str): Path to the JSONL file
        
    Returns:
        Dict[str, Any]: Summary statistics
    """
    summary = {
        "total_examples": 0,
        "has_system_message": 0,
        "avg_messages_per_example": 0,
        "avg_tokens_per_example": 0,
        "example_types": {}
    }
    
    total_messages = 0
    total_tokens = 0
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            summary["total_examples"] += 1
            
            example = json.loads(line)
            messages = example["messages"]
            
            # Count messages
            total_messages += len(messages)
            
            # Check for system message
            if messages[0]["role"] == "system":
                summary["has_system_message"] += 1
                
                # Categorize by system message content
                system_content = messages[0]["content"]
                category = "unknown"
                
                if "character voice" in system_content.lower():
                    category = "character_voice"
                elif "descriptive prose" in system_content.lower():
                    category = "descriptive_prose"
                elif "dialogue" in system_content.lower():
                    category = "dialogue"
                elif "narrative" in system_content.lower():
                    category = "narrative"
                    
                summary["example_types"][category] = summary["example_types"].get(category, 0) + 1
                
            # Estimate tokens
            example_tokens = sum(len(msg["content"].split()) * 1.3 for msg in messages)
            total_tokens += example_tokens
            
    # Calculate averages
    if summary["total_examples"] > 0:
        summary["avg_messages_per_example"] = total_messages / summary["total_examples"]
        summary["avg_tokens_per_example"] = total_tokens / summary["total_examples"]
        
    return summary

def main():
    """Main function to validate JSONL files"""
    parser = argparse.ArgumentParser(description="Validate JSONL files for OpenAI fine-tuning")
    parser.add_argument("file_paths", nargs="+", help="Paths to JSONL files to validate")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print detailed error messages")
    parser.add_argument("--summary", "-s", action="store_true", help="Print file summary statistics")
    
    args = parser.parse_args()
    
    all_valid = True
    
    for file_path in args.file_paths:
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            all_valid = False
            continue
            
        is_valid, errors = validate_jsonl(file_path, args.verbose)
        all_valid = all_valid and is_valid
        
        if args.summary:
            summary = summarize_jsonl(file_path)
            print(f"\nSummary for {file_path}:")
            print(f"  Total examples: {summary['total_examples']}")
            print(f"  Examples with system message: {summary['has_system_message']} ({summary['has_system_message']/summary['total_examples']:.1%})")
            print(f"  Avg messages per example: {summary['avg_messages_per_example']:.2f}")
            print(f"  Avg tokens per example (est.): {summary['avg_tokens_per_example']:.0f}")
            print("  Example types:")
            for category, count in summary["example_types"].items():
                print(f"    - {category}: {count} ({count/summary['total_examples']:.1%})")
    
    sys.exit(0 if all_valid else 1)

if __name__ == "__main__":
    main()
