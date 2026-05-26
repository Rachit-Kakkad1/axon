import sqlite3
import json
from typing import List, Optional
from agi_cli.models import Message, Role

class MemoryManager:
    def __init__(self, db_path: str = "memory.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS session_info (
                    key TEXT PRIMARY KEY,
                    
                    value TEXT
                )
            """)

    def add_message(self, message: Message):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO messages (role, content, metadata) VALUES (?, ?, ?)",
                (message.role.value, message.content, json.dumps(message.metadata))
            )

    def get_messages(self, limit: Optional[int] = None) -> List[Message]:
        query = "SELECT role, content, metadata FROM messages ORDER BY id ASC"
        if limit:
            query += f" LIMIT {limit}"
        
        messages = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query)
            for role_str, content, metadata_json in cursor:
                messages.append(Message(
                    role=Role(role_str),
                    content=content,
                    metadata=json.loads(metadata_json) if metadata_json else {}
                ))
        return messages

    def clear_memory(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM messages")

    def get_message_count(self) -> int:
        """Total number of stored synapses."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM messages")
            return cursor.fetchone()[0]

    def get_recent_activity(self, limit: int = 4):
        """Recent messages with timestamps for the welcome screen."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT role, substr(content, 1, 60), timestamp "
                "FROM messages ORDER BY id DESC LIMIT ?",
                (limit,)
            )
            return cursor.fetchall()
