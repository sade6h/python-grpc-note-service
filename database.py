import sqlite3
import os

# Use a path inside the 'data' directory
DB_NAME = 'data/notes.db'

def init_db():
    # Ensure the 'data' directory exists
    os.makedirs(os.path.dirname(DB_NAME), exist_ok=True)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Define the SQL statement (removed extra '\' characters)
    create_table_query = """
    CREATE TABLE IF NOT EXISTS notes (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        content TEXT
    );
    """

    cursor.execute(create_table_query)
    conn.commit()
    conn.close()
    print(f"Database '{DB_NAME}' initialized successfully.")

if __name__ == '__main__':
    init_db()