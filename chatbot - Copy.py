import re
import datetime
import wikipedia
from sympy import sympify, SympifyError
from intents import IntentClassifier
from rag import FAQRetriever
import database

class SupportCopilot:
    def __init__(self):
        """Initializes the chatbot with Intent Classification and RAG."""
        self.classifier = IntentClassifier()
        self.retriever = FAQRetriever()
        
    def _handle_math(self, query):
        """Attempts to solve math problems."""
        clean_q = re.sub(r'(what is|calculate|solve|math|how much is)', '', query, flags=re.IGNORECASE).strip()
        clean_q = re.sub(r'[^0-9+\-*/().]', '', clean_q) # Keep only math chars
        if not clean_q:
            return None
        try:
            result = sympify(clean_q)
            return f"The answer is {result}"
        except (SympifyError, TypeError, ValueError, Exception):
            return None

    def _handle_science_and_knowledge(self, query):
        """Uses Wikipedia to answer general knowledge questions."""
        match = re.match(r'(what is|who is|tell me about|explain)\s+(.*)', query, flags=re.IGNORECASE)
        if match:
            topic = match.group(2).strip()
            try:
                summary = wikipedia.summary(topic, sentences=2)
                return f"According to my knowledge base: {summary}"
            except wikipedia.exceptions.DisambiguationError as e:
                return f"There are multiple topics for '{topic}'. Can you be more specific?"
            except wikipedia.exceptions.PageError:
                return None
            except Exception:
                return None
        return None

    def _handle_places(self, query):
        """Handles nearby places query."""
        if re.search(r'(nearby|places to visit|good places near)', query, flags=re.IGNORECASE):
            match = re.search(r'in\s+([a-zA-Z\s]+)', query, flags=re.IGNORECASE)
            if match:
                city = match.group(1).strip()
                try:
                    summary = wikipedia.summary(f"Tourist attractions in {city}", sentences=2)
                    return f"Here is some info about places in {city}: {summary}"
                except:
                    return f"I recommend checking local travel guides for the best places in {city}!"
            else:
                return "I'd love to recommend some nearby places! Could you please tell me which city you are in?"
        return None

    def process_query(self, user_query):
        """
        Processes a user query:
        1. Checks for previous admin answers (Learning Memory)
        2. Checks for dynamic triggers (Math, Time, Greeting, Wiki, Places)
        3. Classifies intent
        4. Routes logic (Escalate vs Automated)
        5. Fetches answer via RAG
        6. Fallbacks to generative/mock response if needed
        
        Returns: tuple(response_text: str, escalated: bool, intent: str)
        """
        user_query_clean = user_query.strip()
        
        # --- 1. PREVIOUS ADMIN KNOWLEDGE (Highest Priority) ---
        past_admin_answer = database.get_previous_admin_answer(user_query_clean)
        if past_admin_answer:
            return f"*(An expert previously answered this)*\n\n{past_admin_answer}", False, "Resolved by Past Ticket"
            
        q_lower = user_query_clean.lower()
        
        # --- DYNAMIC INTERCEPTORS (ChatGPT-like conversational skills) ---
        # 1. Greetings / Small Talk
        if re.search(r'\b(hi+|hello+|hey+|greetings|good morning|good evening)\b', q_lower):
            return "Hello! How can I help you today?", False, "Greeting"
        if re.search(r'(how are you|how do you do|how r u|how are u)', q_lower):
            return "I'm functioning perfectly and ready to help! What can I do for you?", False, "Small Talk"
        if re.search(r'(who made you|who created you|what are you)', q_lower):
            return "I am an Autonomous Customer Support Copilot, a smart AI assistant built to help you!", False, "Small Talk"
        if 'joke' in q_lower:
            return "Why do programmers prefer dark mode? Because light attracts bugs! 🐛", False, "Small Talk"
            
        # 2. Time
        if 'time' in q_lower and ('what' in q_lower or 'current' in q_lower):
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            return f"The current local time is {current_time}.", False, "Time"
            
        # 3. Places
        places_resp = self._handle_places(user_query_clean)
        if places_resp:
            return places_resp, False, "Places"

        # 4. Math
        if any(op in q_lower for op in ['+', '-', '*', '/', 'calculate']):
            math_resp = self._handle_math(user_query_clean)
            if math_resp:
                return math_resp, False, "Math"
                
        # 5. Science & General Knowledge (Wikipedia)
        wiki_resp = self._handle_science_and_knowledge(user_query_clean)
        if wiki_resp:
            return wiki_resp, False, "Science/Knowledge"
            
        # --- RAG & INTENT FALLBACK ---
        
        # Intent Classification
        intent, confidence = self.classifier.predict_intent(user_query_clean)
        
        # Retrieve answer using RAG (Now powered by SQLite)
        rag_answer = self.retriever.get_relevant_answer(user_query_clean)
        if rag_answer:
            return rag_answer, False, intent
            
        # Smart Routing: Check for escalation if no answer is found
        if intent == "Complex/Escalate" or intent == "Unknown/Escalate":
            return (
                "This seems to be a complex issue. I am escalating your ticket to our human support team. "
                "A representative will be with you shortly.", 
                True, 
                intent
            )
            
        # Fallback mock response
        return (
            f"I understand you are having a '{intent}' related issue. "
            "I couldn't find an exact match in my knowledge base, but I can help you file a ticket or "
            "you can try rephrasing your question."
        ), False, intent
