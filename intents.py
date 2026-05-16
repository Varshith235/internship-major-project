import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# Define basic intents for our classifier to learn
TRAINING_DATA = [
    ("I cannot log in to my account", "Login Problem"),
    ("Forgot my password", "Login Problem"),
    ("My account is locked", "Login Problem"),
    ("How do I pay?", "Payment Issue"),
    ("My card was charged twice", "Payment Issue"),
    ("Payment failed", "Payment Issue"),
    ("Where is my refund?", "Refund Request"),
    ("I want my money back", "Refund Request"),
    ("When will I get refunded?", "Refund Request"),
    ("My order is late", "Delivery Delay"),
    ("Where is my package?", "Delivery Delay"),
    ("Delivery hasn't arrived", "Delivery Delay"),
    ("What are your hours?", "General Query"),
    ("Do you have a physical store?", "General Query"),
    ("I want to speak to a manager", "Complex/Escalate"),
    ("This is a legal issue", "Complex/Escalate"),
    ("I am suing you", "Complex/Escalate"),
    ("I need human support", "Complex/Escalate"),
    ("Talk to a real person", "Complex/Escalate")
]

class IntentClassifier:
    def __init__(self):
        """Initializes and trains the intent classifier using simple ML."""
        self.vectorizer = TfidfVectorizer()
        self.classifier = LogisticRegression()
        self._train_model()
        
    def _train_model(self):
        """Trains a TF-IDF + Logistic Regression model on dummy data."""
        # Split training data into texts and labels
        texts = [item[0] for item in TRAINING_DATA]
        labels = [item[1] for item in TRAINING_DATA]
        
        # Transform text into numerical vectors
        X = self.vectorizer.fit_transform(texts)
        
        # Train the model
        self.classifier.fit(X, labels)

    def predict_intent(self, user_query):
        """Predicts the intent of a given user query.
        Returns: tuple(predicted_intent: str, confidence: float)
        """
        # Transform query using the fitted vectorizer
        X_query = self.vectorizer.transform([user_query])
        
        # Predict class and probabilities
        predicted_class = self.classifier.predict(X_query)[0]
        probabilities = self.classifier.predict_proba(X_query)[0]
        max_prob = max(probabilities)
        
        # If confidence is too low, default to escalate
        if max_prob < 0.2:
            return "Unknown/Escalate", max_prob
            
        return predicted_class, max_prob
