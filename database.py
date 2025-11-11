import sqlite3
import os

# Use a path inside the 'data' directory
DB_NAME = 'data/notes.db'

def init_db():
    # --- THIS IS THE CHANGE ---
    # Only create a directory if we are NOT using an in-memory DB
    if DB_NAME != ":memory:":
        os.makedirs(os.path.dirname(DB_NAME), exist_ok=True)
    # --- END OF CHANGE ---

    conn = sqlite3.connect(DB_NAME)
    # Create a cursor object
    cursor = conn.cursor()

    # Define the SQL statement (no backslashes)
    create_table_query = """
    CREATE TABLE IF NOT EXISTS notes (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        content TEXT
    );
    """

    # Execute the SQL statement
    cursor.execute(create_table_query)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    print(f"Database '{DB_NAME}' initialized successfully.")

if __name__ == '__main__':
    init_db()