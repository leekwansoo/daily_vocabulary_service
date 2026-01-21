# Subscriber db_handler.py
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

APP_TZ = ZoneInfo("Asia/Seoul")
DB_PATH = "subscribers.db"

# -------------------------
# Data Models
# -------------------------
@dataclass
class Subscriber:
    id: int
    email: str
    name: str
    level: int
    media: str
    subscribed_at: datetime
    
    @property
    def level_display(self) -> str:
        """Return formatted level display string"""
        return f"level {self.level}"

def to_subscriber(row) -> Subscriber:
    (sid, email, name, level, media, subscribed_iso) = row
    subscribed_at = datetime.fromisoformat(subscribed_iso)
    return Subscriber(
        id=sid,
        email=email,
        name=name,
        level=level,
        media=media,
        subscribed_at=subscribed_at,
    )

# -------------------------
# DB
# -------------------------
def db_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def db_init():
    with db_conn() as conn:
        # Create the table with the original structure first
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS subscribers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                name TEXT NOT NULL,
                level INTEGER NOT NULL,
                media TEXT,
                subscribed_at TEXT NOT NULL
            )
          """
        )
        
        # Check if level column exists and add it if it doesn't
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(subscribers)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'level' not in columns:
            conn.execute("ALTER TABLE subscribers ADD COLUMN level INTEGER DEFAULT 1")
        else:
            # Check if level column is TEXT and needs migration to INTEGER
            cursor.execute("PRAGMA table_info(subscribers)")
            column_info = cursor.fetchall()
            level_column = next((col for col in column_info if col[1] == 'level'), None)
            if level_column and level_column[2] == 'TEXT':
                # Migrate existing TEXT values to INTEGER
                conn.execute("UPDATE subscribers SET level = 1 WHERE level = 'level1' OR level = '1'")
                conn.execute("UPDATE subscribers SET level = 2 WHERE level = 'level2' OR level = '2'")
                conn.execute("UPDATE subscribers SET level = 3 WHERE level = 'level3' OR level = '3'")
                # Set any remaining non-integer values to 1
                conn.execute("UPDATE subscribers SET level = 1 WHERE level NOT IN ('1', '2', '3')")
        
        conn.commit()
db_init()

def add_subscriber(subscribed_at: datetime, email: str, name: str, level: int, media: str):
    """Add a new subscriber to the database"""
    conn = db_conn()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO subscribers (subscribed_at, email, name, level, media) VALUES (?, ?, ?, ?, ?)", (subscribed_at, email, name, level, media))
    conn.commit()
    conn.close()
    
def delete_subscriber(email: str):
    """Delete a subscriber from the database"""
    conn = db_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM subscribers WHERE email = ?", (email,))
    conn.commit()
    conn.close()
    
def list_subscribers():
    """List all subscribers"""
    conn = db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, name, level, media, subscribed_at FROM subscribers")
    subscribers = cursor.fetchall()
    conn.close()
    return [to_subscriber(s) for s in subscribers]

def update_subscriber(old_email: str, new_email: str = None, new_name: str = None, new_level: int = None, new_media: str = None):
    """Update a subscriber's information"""
    conn = db_conn()
    cursor = conn.cursor()
    
    # Build update query dynamically based on provided parameters
    updates = []
    params = []
    
    if new_email is not None:
        updates.append("email = ?")
        params.append(new_email)
    if new_name is not None:
        updates.append("name = ?")
        params.append(new_name)
    if new_level is not None:
        updates.append("level = ?")
        params.append(new_level)
    if new_media is not None:
        updates.append("media = ?")
        params.append(new_media)
    
    if updates:
        params.append(old_email)
        query = f"UPDATE subscribers SET {', '.join(updates)} WHERE email = ?"
        cursor.execute(query, params)
        conn.commit()
    
    conn.close()