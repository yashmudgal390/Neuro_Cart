import os
import sqlite3
import pandas as pd
import argparse
from pathlib import Path
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CustomerLoaderAgent:
    def __init__(self, input_file):
        # Get the absolute path to the project root
        self.project_root = Path(__file__).parent.parent.absolute()
        
        # Set up paths relative to project root
        self.db_path = self.project_root / 'database' / 'data.db'
        self.input_file = Path(input_file)
        
        # Ensure database directory exists
        os.makedirs(self.project_root / 'database', exist_ok=True)
        
        self.conn = None
        self.cursor = None

    def connect_db(self):
        """Establish database connection"""
        try:
            self.conn = sqlite3.connect(str(self.db_path))
            self.cursor = self.conn.cursor()
            logger.info(f"Connected to database at {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    def load_customers(self, file_path):
        """
        Load customer data from CSV into customer_sessions table.
        
        Args:
            file_path (str): Path to customers.csv
        """
        try:
            df = pd.read_csv(file_path)
            
            # Insert into database
            for _, row in df.iterrows():
                self.cursor.execute("""
                    INSERT INTO customer_sessions (customer_id, age, gender, location, start_time)
                    VALUES (?, ?, ?, ?, ?)
                """, (row['customer_id'], row['age'], row['gender'], row['location'], datetime.now()))
            
            self.conn.commit()
            logger.info(f"Loaded {len(df)} customer records")
            
        except Exception as e:
            logger.error(f"Error loading customers: {e}")
            raise

    def load_event_logs(self, file_path):
        """
        Load event logs from CSV into event_logs table.
        
        Args:
            file_path (str): Path to event_logs.csv
        """
        try:
            df = pd.read_csv(file_path)
            
            # Insert into database
            for _, row in df.iterrows():
                self.cursor.execute("""
                    INSERT INTO event_logs (session_id, customer_id, category, dwell_time, event_type, product_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (row['session_id'], row['customer_id'], row['category'], 
                     row['dwell_time'], row['event_type'], row['product_id']))
            
            self.conn.commit()
            logger.info(f"Loaded {len(df)} event logs")
            
        except Exception as e:
            logger.error(f"Error loading event logs: {e}")
            raise

    def run(self):
        """Execute the customer loader agent"""
        try:
            self.connect_db()
            
            # Load customers data
            if self.input_file.exists():
                self.load_customers(self.input_file)
            else:
                logger.warning(f"Customers file not found: {self.input_file}")
            
            # Load event logs data if it exists in the same directory
            event_logs_file = self.input_file.parent / "event_logs.csv"
            if event_logs_file.exists():
                self.load_event_logs(event_logs_file)
            
        except Exception as e:
            logger.error(f"Error in customer loader agent: {e}")
            raise
        finally:
            if self.conn:
                self.conn.close()

def main():
    parser = argparse.ArgumentParser(description='Load customer data into the database')
    parser.add_argument('--input', type=str, required=True,
                      help='Path to input CSV file containing customer data')
    
    args = parser.parse_args()
    
    agent = CustomerLoaderAgent(args.input)
    agent.run()

if __name__ == "__main__":
    main() 