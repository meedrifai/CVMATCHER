import os
import pandas as pd
from app.ai.cv_matcher import CVMatcher

def train_model(data_path, model_save_path):
    """Train CV matcher model and save it."""
    # Check if data file exists
    if not os.path.exists(data_path):
        print(f"Data file not found: {data_path}")
        return False
    
    # Initialize CV matcher
    cv_matcher = CVMatcher()
    
    try:
        # Train model
        print("Training model...")
        metrics = cv_matcher.train(data_path)
        
        # Print metrics
        print("\nModel Training Results:")
        print(f"Accuracy: {metrics['accuracy']:.4f}")
        print(f"Precision: {metrics['precision']:.4f}")
        print(f"Recall: {metrics['recall']:.4f}")
        print(f"F1 Score: {metrics['f1']:.4f}")
        
        # Save model
        print(f"\nSaving model to {model_save_path}")
        cv_matcher.save_model(model_save_path)
        
        return True
    
    except Exception as e:
        print(f"Error training model: {e}")
        return False

if __name__ == "__main__":
    # Set paths
    data_path = os.path.join("data", "raw", "cv_job_dataset.csv")
    model_path = os.path.join("data", "models", "cv_matcher_model.pkl")
    
    # Train and save model
    success = train_model(data_path, model_path)
    
    if success:
        print("Model training completed successfully!")
    else:
        print("Model training failed.")