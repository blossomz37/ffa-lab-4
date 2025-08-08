#!/usr/bin/env python3
"""
OpenAI API Key Management Tool

This script helps manage OpenAI API keys for the fine-tuning project.
"""

import os
import argparse
import json
from typing import Optional, Dict, Any

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'api_config.json')

def load_config() -> Dict[str, Any]:
    """Load configuration from file if it exists
    
    Returns:
        Dict[str, Any]: Configuration dictionary
    """
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
    return {}

def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to file
    
    Args:
        config (Dict[str, Any]): Configuration dictionary
    """
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"Error saving config: {e}")

def set_api_key(api_key: str, profile: str = "default") -> None:
    """Set OpenAI API key for a profile
    
    Args:
        api_key (str): OpenAI API key
        profile (str, optional): Profile name
    """
    config = load_config()
    
    if "profiles" not in config:
        config["profiles"] = {}
        
    config["profiles"][profile] = {"api_key": api_key}
    
    if "active_profile" not in config:
        config["active_profile"] = profile
        
    save_config(config)
    print(f"API key set for profile '{profile}'")
    
    # Also set as environment variable for current session
    os.environ["OPENAI_API_KEY"] = api_key
    print("API key set as OPENAI_API_KEY environment variable for current session")

def get_api_key(profile: Optional[str] = None) -> Optional[str]:
    """Get OpenAI API key for a profile
    
    Args:
        profile (str, optional): Profile name
        
    Returns:
        Optional[str]: API key if found, None otherwise
    """
    config = load_config()
    
    if not profile:
        if "active_profile" in config:
            profile = config["active_profile"]
        else:
            profile = "default"
            
    if "profiles" in config and profile in config["profiles"]:
        return config["profiles"][profile].get("api_key")
        
    return None

def list_profiles() -> None:
    """List all profiles"""
    config = load_config()
    
    if "profiles" not in config or not config["profiles"]:
        print("No profiles found")
        return
        
    active_profile = config.get("active_profile", "default")
    
    print("Profiles:")
    for profile in config["profiles"]:
        if profile == active_profile:
            print(f"* {profile} (active)")
        else:
            print(f"  {profile}")

def set_active_profile(profile: str) -> None:
    """Set active profile
    
    Args:
        profile (str): Profile name
    """
    config = load_config()
    
    if "profiles" not in config or profile not in config["profiles"]:
        print(f"Profile '{profile}' not found")
        return
        
    config["active_profile"] = profile
    save_config(config)
    
    # Set environment variable for current session
    api_key = config["profiles"][profile].get("api_key")
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
        
    print(f"Active profile set to '{profile}'")
    print("API key set as OPENAI_API_KEY environment variable for current session")

def delete_profile(profile: str) -> None:
    """Delete a profile
    
    Args:
        profile (str): Profile name
    """
    config = load_config()
    
    if "profiles" not in config or profile not in config["profiles"]:
        print(f"Profile '{profile}' not found")
        return
        
    del config["profiles"][profile]
    
    if config.get("active_profile") == profile:
        if config["profiles"]:
            config["active_profile"] = next(iter(config["profiles"]))
        else:
            config["active_profile"] = "default"
            
    save_config(config)
    print(f"Profile '{profile}' deleted")

def main():
    """Main function for API key management"""
    parser = argparse.ArgumentParser(description="Manage OpenAI API keys for fine-tuning project")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Set API key command
    set_parser = subparsers.add_parser("set", help="Set OpenAI API key")
    set_parser.add_argument("api_key", help="OpenAI API key")
    set_parser.add_argument("--profile", default="default", help="Profile name")
    
    # Get API key command
    get_parser = subparsers.add_parser("get", help="Get OpenAI API key")
    get_parser.add_argument("--profile", help="Profile name")
    
    # List profiles command
    list_parser = subparsers.add_parser("list", help="List all profiles")
    
    # Set active profile command
    active_parser = subparsers.add_parser("active", help="Set active profile")
    active_parser.add_argument("profile", help="Profile name")
    
    # Delete profile command
    delete_parser = subparsers.add_parser("delete", help="Delete a profile")
    delete_parser.add_argument("profile", help="Profile name")
    
    # Parse arguments
    args = parser.parse_args()
    
    if args.command == "set":
        set_api_key(args.api_key, args.profile)
    elif args.command == "get":
        api_key = get_api_key(args.profile)
        if api_key:
            print(f"API key: {api_key}")
        else:
            print("API key not found")
    elif args.command == "list":
        list_profiles()
    elif args.command == "active":
        set_active_profile(args.profile)
    elif args.command == "delete":
        delete_profile(args.profile)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
