import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_FILE = "edugenie.db"

def init_db():
    """Initialize SQLite database tables."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Q&A History
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS qa_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            mode TEXT DEFAULT 'general',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Quizzes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quizzes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            quiz_data TEXT NOT NULL, -- JSON string
            score INTEGER DEFAULT NULL,
            total_questions INTEGER DEFAULT 0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Learning Paths
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS learning_paths (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            path_data TEXT NOT NULL, -- JSON string
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Summaries
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_text TEXT NOT NULL,
            summary_text TEXT NOT NULL,
            key_points TEXT NOT NULL, -- JSON string
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def save_qa(question: str, answer: str, mode: str = 'general') -> int:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO qa_history (question, answer, mode) VALUES (?, ?, ?)",
        (question, answer, mode)
    )
    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    return row_id

def get_qa_history(limit: int = 20) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, question, answer, mode, timestamp FROM qa_history ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {"id": r[0], "question": r[1], "answer": r[2], "mode": r[3], "timestamp": r[4]}
        for r in rows
    ]

def save_quiz(topic: str, quiz_data: Dict[str, Any]) -> int:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    total_q = len(quiz_data.get("questions", []))
    cursor.execute(
        "INSERT INTO quizzes (topic, quiz_data, total_questions) VALUES (?, ?, ?)",
        (topic, json.dumps(quiz_data), total_q)
    )
    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    return row_id

def save_learning_path(topic: str, path_data: Dict[str, Any]) -> int:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO learning_paths (topic, path_data) VALUES (?, ?)",
        (topic, json.dumps(path_data))
    )
    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    return row_id

def save_summary(original_text: str, summary_text: str, key_points: List[str]) -> int:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO summaries (original_text, summary_text, key_points) VALUES (?, ?, ?)",
        (original_text, summary_text, json.dumps(key_points))
    )
    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    return row_id

# Initialize DB on module import
init_db()
