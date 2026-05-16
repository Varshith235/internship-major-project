import sqlite3
import pandas as pd
import os
import hashlib
import random
from datetime import datetime, timedelta

DB_PATH = 'chat_logs.db'

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    """Initializes the SQLite database with necessary tables and seed data."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create Users table with role
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash TEXT,
            role TEXT DEFAULT 'user'
        )
    ''')
    
    # Create Interactions table with admin_response
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            user_query TEXT,
            predicted_intent TEXT,
            chatbot_response TEXT,
            escalated BOOLEAN,
            admin_response TEXT DEFAULT NULL,
            helpful BOOLEAN,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    
    seed_database()

def seed_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Seed 5 Admins if they don't exist
    for i in range(1, 6):
        admin_user = f"admin{i}"
        try:
            cursor.execute('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)', 
                           (admin_user, hash_password("admin123"), "admin"))
        except sqlite3.IntegrityError:
            pass # Already exists
            
    cursor.execute("SELECT COUNT(*) FROM interactions")
    if cursor.fetchone()[0] == 0:
        print("Seeding database with initial data...")
        queries = [
            ("Where is my refund?", "Refund Request", "Refunds take 5-7 days.", 0, None, 1),
            ("I need to speak to a manager", "Complex/Escalate", "Escalating ticket...", 1, "A manager has reviewed this. We are processing your request.", None),
            ("This is a legal issue", "Complex/Escalate", "Escalating ticket...", 1, None, None), # Unresolved ticket
            ("Payment failed", "Payment Issue", "Ensure card has balance.", 0, None, 0),
            ("Hi", "Greeting", "Hello! How can I help you?", 0, None, 1),
        ]
        
        for q, i, r, e, a_resp, h in queries:
            days_ago = random.randint(0, 7)
            random_time = datetime.now() - timedelta(days=days_ago)
            
            cursor.execute('''
                INSERT INTO interactions (username, user_query, predicted_intent, chatbot_response, escalated, admin_response, helpful, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', ("demo_user", q, i, r, e, a_resp, h, random_time.strftime("%Y-%m-%d %H:%M:%S")))
    
    conn.commit()
    conn.close()

def create_user(username, password, role='user'):
    """Creates a new user. Returns True if successful, False if username exists."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)', (username, hash_password(password), role))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def authenticate_user(username, password):
    """Authenticates a user. Returns (is_authenticated, role)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT password_hash, role FROM users WHERE username = ?', (username,))
    result = cursor.fetchone()
    conn.close()
    
    if result and result[0] == hash_password(password):
        return True, result[1]
    return False, None

def log_interaction(username, query, intent, response, escalated):
    """Logs a single user-chatbot interaction into the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    esc_val = 1 if escalated else 0
    
    cursor.execute('''
        INSERT INTO interactions (username, user_query, predicted_intent, chatbot_response, escalated)
        VALUES (?, ?, ?, ?, ?)
    ''', (username, query, intent, response, esc_val))
    
    interaction_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return interaction_id

def update_feedback(interaction_id, is_helpful):
    """Updates the feedback (Helpful/Not Helpful) for a specific interaction."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    help_val = 1 if is_helpful else 0
    cursor.execute('UPDATE interactions SET helpful = ? WHERE id = ?', (help_val, interaction_id))
    conn.commit()
    conn.close()

# --- ADMIN SPECIFIC DB FUNCTIONS ---

def get_pending_tickets():
    """Returns all escalated interactions that do not have an admin response yet."""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM interactions WHERE escalated = 1 AND admin_response IS NULL", conn)
    conn.close()
    return df

def get_resolved_tickets():
    """Returns all escalated interactions that have an admin response."""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM interactions WHERE escalated = 1 AND admin_response IS NOT NULL", conn)
    conn.close()
    return df

def reply_to_ticket(interaction_id, admin_response):
    """Updates an interaction with the admin's response."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE interactions SET admin_response = ? WHERE id = ?', (admin_response, interaction_id))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT id, username, role FROM users", conn)
    conn.close()
    return df

def get_all_interactions():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM interactions ORDER BY timestamp DESC", conn)
    conn.close()
    return df

def get_user_tickets(username):
    """Returns escalated tickets for a specific user to display in their module."""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM interactions WHERE username = ? AND escalated = 1", conn, params=(username,))
    conn.close()
    return df

def get_previous_admin_answer(query):
    """Checks if this exact query was previously answered by an admin."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT admin_response FROM interactions WHERE LOWER(user_query) = LOWER(?) AND admin_response IS NOT NULL LIMIT 1', (query,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    return None

# --- METRICS ---
def get_metrics():
    if not os.path.exists(DB_PATH):
        return {"total_queries": 0, "resolved": 0, "escalated": 0, "helpful_rate": "0%"}
        
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM interactions", conn)
    conn.close()
    
    if df.empty:
        return {"total_queries": 0, "resolved": 0, "escalated": 0, "helpful_rate": "0%"}
        
    total_queries = len(df)
    escalated = df['escalated'].sum()
    resolved = total_queries - escalated
    
    feedback_given = df.dropna(subset=['helpful'])
    if not feedback_given.empty:
        helpful_count = feedback_given['helpful'].sum()
        helpful_rate = f"{(helpful_count / len(feedback_given)) * 100:.1f}%"
    else:
        helpful_rate = "N/A"
        
    return {
        "total_queries": total_queries,
        "resolved": resolved,
        "escalated": escalated,
        "helpful_rate": helpful_rate
    }
