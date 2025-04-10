import sqlite3
import os
from pathlib import Path

def init_database():
    # Get the absolute path to the database directory
    db_dir = Path(__file__).parent.absolute()
    db_path = db_dir / 'data.db'
    schema_path = db_dir / 'schema.sql'

    # Create database directory if it doesn't exist
    os.makedirs(db_dir, exist_ok=True)

    # Connect to database (this will create it if it doesn't exist)
    conn = sqlite3.connect(db_path)
    
    try:
        # Read schema file
        with open(schema_path, 'r') as f:
            schema = f.read()
        
        # Execute schema
        conn.executescript(schema)
        conn.commit()
        print(f"Database initialized successfully at {db_path}")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    init_database() 