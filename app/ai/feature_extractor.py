import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

class FeatureExtractor:
    """Extract features from resumes and job descriptions."""
    
    def __init__(self):
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000)
        self.is_fitted = False
    
    def fit(self, documents):
        """Fit the TF-IDF vectorizer on documents."""
        self.tfidf_vectorizer.fit(documents)
        self.is_fitted = True
    
    def extract_tfidf_features(self, documents):
        """Extract TF-IDF features from documents."""
        if not self.is_fitted:
            self.fit(documents)
        return self.tfidf_vectorizer.transform(documents)
    
    def extract_combined_features(self, resume_text, job_description):
        """Extract combined features from resume and job description."""
        if not self.is_fitted:
            self.fit([resume_text, job_description])
        
        resume_vector = self.tfidf_vectorizer.transform([resume_text])
        job_vector = self.tfidf_vectorizer.transform([job_description])
        
        # Combine features
        # You can try different methods of combining features
        # 1. Concatenate vectors
        # combined = np.hstack((resume_vector.toarray(), job_vector.toarray()))
        
        # 2. Compute similarity features
        similarity = resume_vector.dot(job_vector.T).toarray()[0][0]
        
        # 3. Element-wise operations
        difference = np.abs(resume_vector.toarray() - job_vector.toarray())
        product = resume_vector.toarray() * job_vector.toarray()
        
        combined = np.hstack((
            resume_vector.toarray(), 
            job_vector.toarray(),
            difference,
            product,
            np.array([[similarity]])
        ))
        
        return combined
    
    def extract_skills_features(self, resume_skills, job_skills):
        """Extract features based on skills match."""
        if not resume_skills or not job_skills:
            return np.array([[0, 0, 0]])
        
        # Calculate skill match metrics
        common_skills = set(resume_skills).intersection(set(job_skills))
        skill_match_ratio = len(common_skills) / len(job_skills) if job_skills else 0
        resume_skill_coverage = len(common_skills) / len(resume_skills) if resume_skills else 0
        
        # Create feature vector
        features = np.array([
            [len(common_skills), skill_match_ratio, resume_skill_coverage]
        ])
        
        return features