import os
import numpy as np
import pandas as pd
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.preprocessing import StandardScaler

from .text_processor import TextProcessor
from .feature_extractor import FeatureExtractor

class CVMatcher:
    """CV Matcher model for predicting resume-job match."""
    
    def __init__(self):
        self.model = None
        self.text_processor = TextProcessor()
        self.feature_extractor = FeatureExtractor()
        self.scaler = StandardScaler()
    
    def load_model(self, model_path):
        """Load a trained model from file."""
        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            return True
        return False
    
    def save_model(self, model_path):
        """Save the trained model to file."""
        if self.model:
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            with open(model_path, 'wb') as f:
                pickle.dump(self.model, f)
            return True
        return False
    
    def preprocess_data(self, df):
        """Preprocess dataset for training."""
        # Process resumes and job descriptions
        df['processed_resume'] = df['Resume'].apply(self.text_processor.process_text)
        df['processed_job'] = df['Job Description'].apply(self.text_processor.process_text)
        
        # Extract skills
        df['resume_skills'] = df['Resume'].apply(self.text_processor.extract_skills)
        df['job_skills'] = df['Job Description'].apply(self.text_processor.extract_skills)
        
        return df
    
    def extract_features(self, df):
        """Extract features from preprocessed data."""
        # Create a list to store all feature arrays
        all_features = []
        
        # Extract TF-IDF features for all document pairs
        all_documents = list(df['processed_resume']) + list(df['processed_job'])
        self.feature_extractor.fit(all_documents)
        
        # Extract features for each resume-job pair
        for i, row in df.iterrows():
            # Extract text features
            text_features = self.feature_extractor.extract_combined_features(
                row['processed_resume'], 
                row['processed_job']
            )
            
            # Extract skills features
            skills_features = self.feature_extractor.extract_skills_features(
                row['resume_skills'],
                row['job_skills']
            )
            
            # Combine features
            combined_features = np.hstack((text_features, skills_features))
            all_features.append(combined_features)
        
        # Convert list of arrays to a single array
        X = np.vstack(all_features)
        
        # Scale features
        X = self.scaler.fit_transform(X)
        
        return X
    
    def train(self, data_path):
        """Train the model using the dataset."""
        # Load dataset
        df = pd.read_csv(data_path)
        
        # Preprocess data
        df = self.preprocess_data(df)
        
        # Extract features
        X = self.extract_features(df)
        y = df['Best Match'].astype(int)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train model
        self.model = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            class_weight='balanced'
        )
        self.model.fit(X_train, y_train)
        
        # Evaluate model
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        
        # Return metrics
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1
        }
    
    def predict_match(self, resume_text, job_description):
        """Predict match percentage between resume and job description."""
        if not self.model:
            # Return default score if model is not trained
            return 0.5
        
        # Preprocess texts
        processed_resume = self.text_processor.process_text(resume_text)
        processed_job = self.text_processor.process_text(job_description)
        
        # Extract skills
        resume_skills = self.text_processor.extract_skills(resume_text)
        job_skills = self.text_processor.extract_skills(job_description)
        
        # Extract text features
        text_features = self.feature_extractor.extract_combined_features(
            processed_resume, processed_job
        )
        
        # Extract skills features
        skills_features = self.feature_extractor.extract_skills_features(
            resume_skills, job_skills
        )
        
        # Combine features
        combined_features = np.hstack((text_features, skills_features))
        
        # Scale features
        X = self.scaler.transform(combined_features)
        
        # Make prediction
        if hasattr(self.model, 'predict_proba'):
            # If model supports probability prediction
            match_proba = self.model.predict_proba(X)[0][1]
            return match_proba
        else:
            # Binary prediction
            match_pred = self.model.predict(X)[0]
            return float(match_pred)