#!/usr/bin/env python3
"""
Fine-tuning Job Submission

This script submits fine-tuning jobs to OpenAI, monitors progress, and manages models.
"""

import os
import json
import time
import argparse
from typing import Dict, Any, List, Optional
from openai import OpenAI
from tenacity import retry, wait_random_exponential, stop_after_attempt
from dotenv import load_dotenv

class FineTuningManager:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the fine-tuning manager
        
        Args:
            api_key (str, optional): OpenAI API key (defaults to environment variable)
        """
        # Load environment variables from .env file
        load_dotenv()
        
        # Use provided API key or get from environment
        if api_key is None:
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables. Please check your .env file.")
        
        self.client = OpenAI(api_key=api_key)
        
    @retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
    def upload_file(self, file_path: str, purpose: str = "fine-tune") -> str:
        """Upload a file to OpenAI with retries
        
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
    
    def submit_fine_tuning_job(self, 
                             training_file_id: str, 
                             validation_file_id: Optional[str] = None, 
                             model: str = "gpt-3.5-turbo", 
                             suffix: Optional[str] = None,
                             hyperparameters: Optional[Dict[str, Any]] = None) -> str:
        """Submit a fine-tuning job to OpenAI
        
        Args:
            training_file_id (str): ID of the training file
            validation_file_id (str, optional): ID of the validation file
            model (str): Base model to fine-tune
            suffix (str, optional): Suffix for the fine-tuned model name
            hyperparameters (Dict, optional): Fine-tuning hyperparameters
            
        Returns:
            str: ID of the fine-tuning job
        """
        print(f"Submitting fine-tuning job for model {model}...")
        
        job_args = {
            "training_file": training_file_id,
            "model": model,
        }
        
        if validation_file_id:
            job_args["validation_file"] = validation_file_id
            
        if suffix:
            job_args["suffix"] = suffix
            
        if hyperparameters:
            job_args["hyperparameters"] = hyperparameters
        
        job = self.client.fine_tuning.jobs.create(**job_args)
        
        print(f"Fine-tuning job submitted with ID: {job.id}")
        print(f"Status: {job.status}")
        return job.id
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get the status of a fine-tuning job
        
        Args:
            job_id (str): ID of the fine-tuning job
            
        Returns:
            Dict[str, Any]: Job status information
        """
        job = self.client.fine_tuning.jobs.retrieve(job_id)
        return {
            "id": job.id,
            "status": job.status,
            "created_at": job.created_at,
            "finished_at": job.finished_at,
            "model": job.model,
            "fine_tuned_model": job.fine_tuned_model,
            "training_file": job.training_file,
            "validation_file": job.validation_file,
            "error": job.error,
        }
    
    def list_jobs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """List fine-tuning jobs
        
        Args:
            limit (int): Maximum number of jobs to list
            
        Returns:
            List[Dict[str, Any]]: List of job information
        """
        jobs = self.client.fine_tuning.jobs.list(limit=limit)
        return [{
            "id": job.id,
            "status": job.status,
            "created_at": job.created_at,
            "model": job.model,
            "fine_tuned_model": job.fine_tuned_model,
        } for job in jobs.data]
    
    def monitor_job(self, job_id: str, interval: int = 60, max_time: int = 7200) -> Dict[str, Any]:
        """Monitor a fine-tuning job until completion
        
        Args:
            job_id (str): ID of the fine-tuning job
            interval (int): Check interval in seconds
            max_time (int): Maximum monitoring time in seconds
            
        Returns:
            Dict[str, Any]: Final job status
        """
        print(f"Monitoring fine-tuning job {job_id}...")
        start_time = time.time()
        
        while True:
            job_status = self.get_job_status(job_id)
            status = job_status["status"]
            
            print(f"Status: {status}")
            
            if status in ["succeeded", "failed", "cancelled"]:
                print(f"Job {status}!")
                if status == "succeeded":
                    print(f"Fine-tuned model: {job_status['fine_tuned_model']}")
                elif status == "failed" and job_status["error"]:
                    print(f"Error: {job_status['error']}")
                return job_status
                
            elapsed_time = time.time() - start_time
            if elapsed_time > max_time:
                print(f"Reached maximum monitoring time ({max_time} seconds)")
                return job_status
                
            print(f"Next check in {interval} seconds...")
            time.sleep(interval)
    
    def list_models(self) -> List[Dict[str, Any]]:
        """List available models
        
        Returns:
            List[Dict[str, Any]]: List of model information
        """
        models = self.client.models.list()
        return [{"id": model.id, "created": model.created} for model in models.data]
    
    def delete_model(self, model_id: str) -> bool:
        """Delete a fine-tuned model
        
        Args:
            model_id (str): ID of the model to delete
            
        Returns:
            bool: Whether the deletion was successful
        """
        try:
            response = self.client.models.delete(model_id)
            print(f"Model {model_id} deleted")
            return response.deleted
        except Exception as e:
            print(f"Error deleting model {model_id}: {str(e)}")
            return False
    
    def save_job_details(self, job_id: str, output_file: str) -> None:
        """Save job details to a JSON file
        
        Args:
            job_id (str): ID of the fine-tuning job
            output_file (str): Path to the output file
        """
        job_status = self.get_job_status(job_id)
        
        # Get job events
        events = []
        for event in self.client.fine_tuning.jobs.list_events(fine_tuning_job_id=job_id).data:
            events.append({
                "created_at": event.created_at,
                "level": event.level,
                "message": event.message
            })
        
        job_status["events"] = events
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(job_status, f, indent=2)
            
        print(f"Job details saved to {output_file}")


def main():
    """Main function to submit fine-tuning jobs"""
    parser = argparse.ArgumentParser(description="Submit fine-tuning jobs to OpenAI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Upload file command
    upload_parser = subparsers.add_parser("upload", help="Upload a file to OpenAI")
    upload_parser.add_argument("file_path", help="Path to the file to upload")
    upload_parser.add_argument("--purpose", default="fine-tune", help="Purpose of the file")
    
    # Submit job command
    submit_parser = subparsers.add_parser("submit", help="Submit a fine-tuning job")
    submit_parser.add_argument("--training-file", required=True, help="ID of the training file")
    submit_parser.add_argument("--validation-file", help="ID of the validation file")
    submit_parser.add_argument("--model", default="gpt-3.5-turbo", help="Base model to fine-tune")
    submit_parser.add_argument("--suffix", help="Suffix for the fine-tuned model name")
    submit_parser.add_argument("--epochs", type=int, help="Number of training epochs")
    submit_parser.add_argument("--batch-size", help="Batch size for training")
    submit_parser.add_argument("--learning-rate", type=float, help="Learning rate multiplier")
    
    # Get job status command
    status_parser = subparsers.add_parser("status", help="Get the status of a fine-tuning job")
    status_parser.add_argument("job_id", help="ID of the fine-tuning job")
    
    # List jobs command
    list_parser = subparsers.add_parser("list-jobs", help="List fine-tuning jobs")
    list_parser.add_argument("--limit", type=int, default=10, help="Maximum number of jobs to list")
    
    # Monitor job command
    monitor_parser = subparsers.add_parser("monitor", help="Monitor a fine-tuning job until completion")
    monitor_parser.add_argument("job_id", help="ID of the fine-tuning job")
    monitor_parser.add_argument("--interval", type=int, default=60, help="Check interval in seconds")
    monitor_parser.add_argument("--max-time", type=int, default=7200, help="Maximum monitoring time in seconds")
    
    # List models command
    list_models_parser = subparsers.add_parser("list-models", help="List available models")
    
    # Delete model command
    delete_parser = subparsers.add_parser("delete-model", help="Delete a fine-tuned model")
    delete_parser.add_argument("model_id", help="ID of the model to delete")
    
    # Save job details command
    save_parser = subparsers.add_parser("save-job", help="Save job details to a JSON file")
    save_parser.add_argument("job_id", help="ID of the fine-tuning job")
    save_parser.add_argument("--output", default="job_details.json", help="Path to the output file")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Initialize fine-tuning manager
    manager = FineTuningManager()
    
    # Execute command
    if args.command == "upload":
        file_id = manager.upload_file(args.file_path, args.purpose)
        print(f"File ID: {file_id}")
        
    elif args.command == "submit":
        # Build hyperparameters dictionary
        hyperparameters = {}
        if args.epochs is not None:
            hyperparameters["n_epochs"] = args.epochs
        if args.batch_size is not None:
            hyperparameters["batch_size"] = args.batch_size
        if args.learning_rate is not None:
            hyperparameters["learning_rate_multiplier"] = args.learning_rate
            
        job_id = manager.submit_fine_tuning_job(
            training_file_id=args.training_file,
            validation_file_id=args.validation_file,
            model=args.model,
            suffix=args.suffix,
            hyperparameters=hyperparameters if hyperparameters else None
        )
        print(f"Job ID: {job_id}")
        
    elif args.command == "status":
        job_status = manager.get_job_status(args.job_id)
        print(json.dumps(job_status, indent=2))
        
    elif args.command == "list-jobs":
        jobs = manager.list_jobs(args.limit)
        print(json.dumps(jobs, indent=2))
        
    elif args.command == "monitor":
        final_status = manager.monitor_job(args.job_id, args.interval, args.max_time)
        print(json.dumps(final_status, indent=2))
        
    elif args.command == "list-models":
        models = manager.list_models()
        print(json.dumps(models, indent=2))
        
    elif args.command == "delete-model":
        success = manager.delete_model(args.model_id)
        print(f"Deletion {'successful' if success else 'failed'}")
        
    elif args.command == "save-job":
        manager.save_job_details(args.job_id, args.output)
        
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
