import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Download necessary NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')

class TextProcessor:
    """Text preprocessing utilities for resumes and job descriptions."""
    
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
    
    def clean_text(self, text):
        """Clean and normalize text."""
        if not isinstance(text, str):
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove phone numbers
        text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '', text)
        
        # Remove special characters and punctuation
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def tokenize(self, text):
        """Tokenize text into words."""
        return word_tokenize(text)
    
    def remove_stopwords(self, tokens):
        """Remove stop words from tokens."""
        return [word for word in tokens if word not in self.stop_words]
    
    def lemmatize(self, tokens):
        """Lemmatize tokens."""
        return [self.lemmatizer.lemmatize(word) for word in tokens]
    
    def process_text(self, text):
        """Apply full text processing pipeline."""
        cleaned_text = self.clean_text(text)
        tokens = self.tokenize(cleaned_text)
        tokens = self.remove_stopwords(tokens)
        tokens = self.lemmatize(tokens)
        return ' '.join(tokens)
    
    def extract_skills(self, text):
        """Extract skills from text."""
        # In a real implementation, this would use a skills database or ML model
        # For simplicity, we'll use a basic approach here
        common_skills = [
            'python', 'java', 'javascript', 'sql', 'machine learning',
            'data analysis', 'project management', 'communication',
            'leadership', 'teamwork', 'problem solving', 'aws', 'azure',
            'cloud', 'devops', 'agile', 'scrum', 'react', 'angular', 'vue',
            'django', 'flask', 'express', 'node', 'php', 'html', 'css',
            'software development', 'database', 'docker', 'kubernetes',
            'linux', 'windows', 'excel', 'powerpoint', 'word', 'writing',
            'editing', 'marketing', 'sales', 'customer service', 'finance',
            'accounting', 'hr', 'recruitment', 'negotiation', 'research'
        ]
        
        found_skills = []
        cleaned_text = self.clean_text(text)
        
        for skill in common_skills:
            if re.search(r'\b' + re.escape(skill) + r'\b', cleaned_text):
                found_skills.append(skill)
        
        return found_skills