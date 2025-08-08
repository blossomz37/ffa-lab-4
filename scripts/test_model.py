#!/usr/bin/env python3
"""
Fine-tuned Model Smoke Test (student-friendly)

What this script does:
- Loads your API key and model ID from the environment (.env)
- Sends a few representative prompts (dialogue, description, scene)
- Prints raw outputs so you can eyeball style alignment

Adult learner notes:
- Keep tests short: long outputs consume credits.
- If you change prompts, keep them consistent across model comparisons.
- FAIL FAST: If the first response is clearly off-style, stop and revisit your dataset.
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

def test_model():
    # Load environment variables
    load_dotenv()
    
    # Initialize OpenAI client
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    # Prefer FINE_TUNED_MODEL_ID, fall back to FINETUNED_MODEL for backward compatibility
    model_id = os.getenv('FINE_TUNED_MODEL_ID') or os.getenv('FINETUNED_MODEL')
    if not model_id:
        raise ValueError("FINE_TUNED_MODEL_ID not found in environment variables")
    
    # Test prompts
    test_prompts = [
        "Generate a dialogue exchange between two characters who are having a tense confrontation.",
        "Write a descriptive passage about a character walking through a dystopian cityscape.",
        "Create a scene where a character discovers a mysterious object."
    ]
    
    print(f"Testing fine-tuned model: {model_id}\n")
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\nTest {i}: {prompt}\n")
        try:
            response = client.chat.completions.create(
                model=model_id,
                messages=[
                    {"role": "system", "content": "You are a creative writing assistant specializing in immersive narrative fiction."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            print("Response:")
            print(response.choices[0].message.content)
            print("\n" + "="*50 + "\n")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_model()
