import sqlite3
import os
import logging

logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), "avni_data.db")

CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER UNIQUE NOT NULL,
    first_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_FACTS_TABLE = """
CREATE TABLE IF NOT EXISTS facts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    fact_key TEXT NOT NULL,
    fact_value TEXT NOT NULL,
    fact_type TEXT DEFAULT 'profile',
    importance INTEGER DEFAULT 50,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(telegram_id),
    UNIQUE(user_id, fact_key)
);
"""

CREATE_CONVERSATION_TABLE = """
CREATE TABLE IF NOT EXISTS conversation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    role TEXT NOT NULL,
    message TEXT NOT NULL,
    token_estimate INTEGER DEFAULT 0,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(telegram_id)
);
"""

CREATE_SUMMARIES_TABLE = """
CREATE TABLE IF NOT EXISTS summaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    summary_text TEXT NOT NULL,
    token_count INTEGER DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(telegram_id)
);
"""

CREATE_INDEX_FACTS = "CREATE INDEX IF NOT EXISTS idx_facts_user ON facts(user_id);"
CREATE_INDEX_CONVERSATION = "CREATE INDEX IF NOT EXISTS idx_conv_user ON conversation(user_id);"

def init_db():
    """Initializes SQLite database and indexes safely."""
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        cursor = conn.cursor()
        
        cursor.execute(CREATE_USERS_TABLE)
        cursor.execute(CREATE_FACTS_TABLE)
        cursor.execute(CREATE_CONVERSATION_TABLE)
        cursor.execute(CREATE_SUMMARIES_TABLE)
        
        cursor.execute(CREATE_INDEX_FACTS)
        cursor.execute(CREATE_INDEX_CONVERSATION)
        
        conn.commit()
        conn.close()
        logger.info("[SQLITE DB]: Database & Indexes initialized successfully at %s", DB_PATH)
    except Exception as e:
        logger.exception("[SQLITE DB ERROR]: Initialization failed: %s", e)
        raise e