"""
Database module for bot management and trade history
"""
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

DB_PATH = Path("repo/data/bots.db")

def get_connection():
    """Get database connection, create dirs if needed"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    """Initialize database schema"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        path TEXT NOT NULL,
        status TEXT DEFAULT 'stopped',
        last_heartbeat TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trade_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bot_id INTEGER NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        side TEXT NOT NULL,
        pair TEXT NOT NULL,
        price REAL NOT NULL,
        amount REAL NOT NULL,
        fee REAL DEFAULT 0,
        meta TEXT,
        FOREIGN KEY (bot_id) REFERENCES bots(id)
    )
    """)
    
    conn.commit()
    conn.close()

def seed_bot(name: str, path: str) -> int:
    """Register a new bot"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO bots (name, path) VALUES (?, ?)", (name, path))
    bot_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return bot_id

def get_bot(bot_id: int) -> Optional[Dict[str, Any]]:
    """Get bot by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bots WHERE id = ?", (bot_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def list_bots() -> List[Dict[str, Any]]:
    """List all bots"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bots ORDER BY id")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_bot_status(bot_id: int, status: str, heartbeat: bool = False):
    """Update bot status and optionally heartbeat"""
    conn = get_connection()
    cursor = conn.cursor()
    if heartbeat:
        cursor.execute(
            "UPDATE bots SET status = ?, last_heartbeat = ? WHERE id = ?",
            (status, datetime.now().isoformat(), bot_id)
        )
    else:
        cursor.execute("UPDATE bots SET status = ? WHERE id = ?", (status, bot_id))
    conn.commit()
    conn.close()

def log_trade(bot_id: int, side: str, pair: str, price: float, amount: float, fee: float = 0, meta: str = ""):
    """Log a trade to database"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO trade_history (bot_id, side, pair, price, amount, fee, meta) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (bot_id, side, pair, price, amount, fee, meta)
    )
    conn.commit()
    conn.close()

def list_trades(bot_id: int, limit: int = 100) -> List[Dict[str, Any]]:
    """Get trade history for a bot"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM trade_history WHERE bot_id = ? ORDER BY timestamp DESC LIMIT ?",
        (bot_id, limit)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
