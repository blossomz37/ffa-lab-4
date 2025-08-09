#!/bin/bash
# Clean up unused directories

# Remove empty directories we don't need
if [ -d "dpo_finetune" ]; then
  rmdir dpo_finetune
  echo "Removed empty directory: dpo_finetune"
fi

if [ -d "finetune" ]; then
  rmdir finetune
  echo "Removed empty directory: finetune"
fi

if [ -d "temp_empty_dir" ]; then
  rmdir temp_empty_dir
  echo "Removed temporary directory: temp_empty_dir"
fi

echo "Cleanup complete."
