# Next Steps for Writing Style Fine-tuning Project

## Your Tasks:

1. **Set up the environment**
   - Run the master setup script to prepare the directory structure:
     ```bash
     bash master_setup.sh
     ```
   - Make sure all scripts are executable

2. **Configure API access**
   - Create a .env file in the project root
   - Add your OpenAI API key:
     ```
     OPENAI_API_KEY=your-api-key-here
     ```
   - Test API access by running the dataset preparation script

3. **Review source material**
   - Ensure all necessary source materials are in the `/original documents` folder
   - Consider adding any additional writing samples if available (character sheets, dialogue examples, etc.)

4. **Prepare training data**
   - Run the dataset preparation script:
     ```bash
     python scripts/prepare_dataset.py
     ```
   - Review the generated datasets in the `datasets` directory:
     - `training_finetune_dataset.jsonl`
     - `validation_finetune_dataset.jsonl`
   - Check the console output for pattern extraction statistics

5. **Review examples by category**
   - Examine dialogue patterns and speaker attribution
   - Check narrative passages for plot development
   - Verify descriptive writing samples
   - Ensure balance across categories

6. **Review JSON format**
   - Check that each example follows the format:
     ```json
     {
       "messages": [
         {"role": "system", "content": "..."},
         {"role": "user", "content": "..."},
         {"role": "assistant", "content": "..."}
       ]
     }
     ```
   - Verify proper JSON formatting and escape characters

7. **Organize new writing samples**
   - Add new source materials to `original documents` as needed
   - Rerun dataset preparation with new samples
   - Compare datasets for improved coverage

## Next Steps:

1. **Add writing prompts**
   - Create prompt templates for each category:
     - Dialogue prompts
     - Narrative prompts
     - Descriptive prompts
   - Save prompts as JSON files in the `prompts` directory

2. **Improve pattern extraction**
   - Add more pattern recognition for:
     - Complex dialogue exchanges
     - Scene transitions
     - Character development moments
   - Refine pattern matching expressions

3. **Documentation**
   - Document extracted pattern types
   - Note any limitations or specific requirements
   - Add examples of successful patterns

## Timeline:

1. **Initial setup**: 10-15 minutes
2. **Dataset preparation**: 30-60 minutes depending on source material
3. **Review and refinement**: 30 minutes

Tips:
- Start with a small set of high-quality writing samples
- Review extracted patterns before generating the full dataset
- Add more samples incrementally to improve coverage