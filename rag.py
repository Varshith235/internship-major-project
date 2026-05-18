import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import database

class FAQRetriever:
    def __init__(self):
        """Initializes the TF-IDF vectorizer and loads the FAQ dataset from the SQLite DB."""
        self.retrain()
        
    def retrain(self):
        """Fetches the latest knowledge from the database and rebuilds the TF-IDF matrix."""
        self.df = database.get_knowledge_base()
        
        if self.df.empty:
            self.questions = ["Placeholder Question"]
            self.answers = ["I am still learning. Please check back later."]
        else:
            self.questions = self.df['question'].tolist()
            self.answers = self.df['answer'].tolist()
            
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
