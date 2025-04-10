import sqlite3
import os

def init_database():
    # Create database directory if it doesn't exist
    os.makedirs('database', exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect('database/data.db')
    cursor = conn.cursor()
    
    # Drop existing tables
    cursor.executescript("""
        DROP TABLE IF EXISTS customer_sessions;
        DROP TABLE IF EXISTS product_catalog;
        DROP TABLE IF EXISTS event_logs;
        DROP TABLE IF EXISTS reports;
    """)
    
    # Create tables
    cursor.executescript("""
        -- Customer Sessions Table
        CREATE TABLE customer_sessions (
            customer_id TEXT PRIMARY KEY,
            age INTEGER,
            gender TEXT,
            location TEXT,
            interests TEXT,
            registration_date TEXT,
            last_active TEXT
        );

        -- Product Catalog Table
        CREATE TABLE product_catalog (
            product_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            price REAL,
            category TEXT,
            popularity INTEGER,
            stock INTEGER
        );

        -- Event Logs Table
        CREATE TABLE event_logs (
            interaction_id TEXT PRIMARY KEY,
            customer_id TEXT,
            product_id TEXT,
            event_type TEXT,
            timestamp TEXT,
            dwell_time INTEGER,
            FOREIGN KEY (customer_id) REFERENCES customer_sessions(customer_id),
            FOREIGN KEY (product_id) REFERENCES product_catalog(product_id)
        );

        -- Reports Table
        CREATE TABLE reports (
            report_id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_type TEXT,
            data TEXT,
            timestamp TEXT
        );
    """)
    
    conn.commit()
    print("Database schema initialized successfully!")
    conn.close()

if __name__ == "__main__":
    init_database() 