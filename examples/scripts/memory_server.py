from mcp.server.fastmcp import FastMCP
import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

# Constants
DB_PATH = ".context/memori.db"

# Initialize FastMCP Server
mcp = FastMCP("Antigravity")

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    # Ensure directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dict-like objects
    return conn

@mcp.tool()
def init_memory() -> str:
    """
    Initialize the memory database table if it doesn't exist.
    Creates a 'memory' table with columns: category, key, value, updated_at.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memory (
                category TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (category, key)
            )
        ''')
        conn.commit()
        conn.close()
        return "Memory initialized successfully."
    except Exception as e:
        return f"Error initializing memory: {str(e)}"

@mcp.tool()
def store_memory(category: str, key: str, value: str) -> str:
    """
    Store or update a memory item.
    
    Args:
        category: The category of the memory (e.g., 'user_profile', 'session_log')
        key: The unique key within the category (e.g., 'risk_tolerance', 'session_123')
        value: The string value to store.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO memory (category, key, value, updated_at) 
            VALUES (?, ?, ?, ?)
            ON CONFLICT(category, key) DO UPDATE SET
                value=excluded.value,
                updated_at=excluded.updated_at
        ''', (category, key, value, datetime.now()))
        conn.commit()
        conn.close()
        return f"Stored: [{category}/{key}]"
    except Exception as e:
        return f"Error storing memory: {str(e)}"

@mcp.tool()
def query_memory(query: str, parameters: List[Any] = []) -> str:
    """
    Execute a read-only SQL query against the memory database.
    Restricted to SELECT statements for safety.
    
    Args:
        query: The SQL query string (must start with SELECT).
        parameters: Optional list of parameters for sanitized execution.
    """
    if not query.strip().upper().startswith("SELECT"):
        return "Error: Only SELECT queries are allowed via this tool."

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, parameters)
        rows = cursor.fetchall()
        conn.close()
        
        # Convert rows to list of dicts for JSON serialization
        results = [dict(row) for row in rows]
        return str(results)
    except Exception as e:
        return f"Error querying memory: {str(e)}"

@mcp.tool()
def get_memory(category: str, key: str) -> str:
    """
    Retrieve a specific memory value by category and key.
    Returns the value string directly, or "NOT FOUND".
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM memory WHERE category = ? AND key = ?", (category, key))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return row['value']
        else:
            return "NOT FOUND"
    except Exception as e:
        return f"Error retrieving memory: {str(e)}"

if __name__ == "__main__":
    # When running directly, we simply run the server
    # It communicates via stdio by default for FastMCP
    mcp.run()
