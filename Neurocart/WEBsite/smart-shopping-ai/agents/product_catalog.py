import os
import sqlite3
import pandas as pd
import numpy as np
import argparse
from pathlib import Path
import logging
import pickle
import json
import requests

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProductCatalogAgent:
    def __init__(self, input_file):
        # Get the absolute path to the project root
        self.project_root = Path(__file__).parent.parent.absolute()
        
        # Set up paths
        self.db_path = self.project_root / 'database' / 'data.db'
        self.input_file = Path(input_file)
        self.embeddings_dir = self.project_root / 'embeddings'
        
        # Ensure embeddings directory exists
        os.makedirs(self.embeddings_dir, exist_ok=True)
        
        self.conn = None
        self.cursor = None

    def connect_db(self):
        try:
            self.conn = sqlite3.connect(str(self.db_path))
            self.cursor = self.conn.cursor()
            logger.info(f"Connected to database at {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    def load_products(self):
        try:
            df = pd.read_csv(self.input_file)
            
            # Clear existing products
            self.cursor.execute("DELETE FROM product_catalog")
            
            # Insert products
            for _, row in df.iterrows():
                self.cursor.execute("""
                    INSERT INTO product_catalog 
                    (product_id, name, description, price, category, popularity, stock)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    row['product_id'],
                    row['name'],
                    row['description'],
                    float(row['price']),
                    row['category'],
                    int(row['popularity']),
                    int(row['stock'])
                ))
            
            self.conn.commit()
            logger.info(f"Loaded {len(df)} products")
            return df
            
        except Exception as e:
            logger.error(f"Error loading products: {e}")
            raise

    def generate_embeddings(self, products_df):
        try:
            embeddings = {}
            
            for _, row in products_df.iterrows():
                # Combine product name and description
                text = f"{row['name']} {row['description']}"
                
                # Get embedding from Ollama API
                response = requests.post(
                    'http://localhost:11434/api/embeddings',
                    json={
                        'model': 'tinyllama',
                        'prompt': text
                    }
                )
                
                if response.status_code != 200:
                    raise Exception(f"Ollama API error: {response.text}")
                
                # Parse embedding from response
                embedding = np.array(response.json()['embedding'])
                embeddings[row['product_id']] = embedding
                
                logger.info(f"Generated embedding for product {row['product_id']}")
            
            # Save embeddings to file
            embeddings_file = self.embeddings_dir / 'product_vectors.pkl'
            with open(embeddings_file, 'wb') as f:
                pickle.dump(embeddings, f)
            
            logger.info(f"Generated embeddings for {len(embeddings)} products")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise

    def save_embeddings(self, embeddings):
        try:
            # Clear existing embeddings
            self.cursor.execute("DELETE FROM product_embeddings")
            
            # Insert embeddings
            for product_id, vector in embeddings.items():
                self.cursor.execute("""
                    INSERT INTO product_embeddings (product_id, vector_blob)
                    VALUES (?, ?)
                """, (product_id, pickle.dumps(vector)))
            
            self.conn.commit()
            logger.info(f"Saved {len(embeddings)} embeddings to database")
            
        except Exception as e:
            logger.error(f"Error saving embeddings: {e}")
            raise

    def run(self):
        try:
            self.connect_db()
            
            # Load products
            products_df = self.load_products()
            
            # Generate embeddings
            embeddings = self.generate_embeddings(products_df)
            
            # Save embeddings
            self.save_embeddings(embeddings)
            
        except Exception as e:
            logger.error(f"Error in product catalog agent: {e}")
            raise
        finally:
            if self.conn:
                self.conn.close()

def main():
    parser = argparse.ArgumentParser(description='Product Catalog Agent')
    parser.add_argument('--input', type=str, required=True,
                      help='Path to input CSV file containing product data')
    
    args = parser.parse_args()
    
    agent = ProductCatalogAgent(args.input)
    agent.run()

if __name__ == "__main__":
    main() 