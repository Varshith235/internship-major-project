import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class FAQRetriever:
    def __init__(self, data_path='data/faqs.csv'):
        """Initializes the TF-IDF vectorizer and loads the FAQ dataset."""
        self.df = pd.read_csv(data_path)
        self.questions = self.df['Question'].tolist()
        self.answers = self.df['Answer'].tolist()
        
        # Build the index using TF-IDF
        self._build_index()
        
    def _build_index(self):
        """Encodes all FAQ questions using TF-IDF."""
        self.vectorizer = TfidfVectorizer()
        # Fit and transform the questions into a TF-IDF matrix
        self.question_vectors = self.vectorizer.fit_transform(self.questions)
        
    def get_relevant_answer(self, user_query, threshold=0.3):
        """
        Retrieves the most relevant FAQ answer for the user query using Cosine Similarity.
        Returns None if the similarity score is below the threshold.
        """
        # Encode the user query
        query_vector = self.vectorizer.transform([user_query])
        
        # Calculate cosine similarity between the query and all FAQ questions
        similarities = cosine_similarity(query_vector, self.question_vectors).flatten()
        
        # Find the index of the highest similarity score
        best_index = np.argmax(similarities)
        best_score = similarities[best_index]
        
        # If the score is high enough, return the matching answer
        if best_score >= threshold:
            return self.answers[best_index]
        else:
            return None
