import os
import sqlite3
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from pathlib import Path
import json
import logging
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SegmentationAgent:
    def __init__(self):
        # Get the absolute path to the project root
        self.project_root = Path(__file__).parent.parent.absolute()
        
        # Set up paths
        self.db_path = self.project_root / 'database' / 'data.db'
        self.config_path = self.project_root / 'config' / 'segment_rules.json'
        
        # Load configuration
        self.config = self.load_config()
        
        self.conn = None
        self.cursor = None

    def load_config(self):
        try:
            with open(self.config_path) as f:
                config = json.load(f)
            logger.info("Loaded configuration successfully")
            return config
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            raise

    def connect_db(self):
        try:
            self.conn = sqlite3.connect(str(self.db_path))
            self.cursor = self.conn.cursor()
            logger.info(f"Connected to database at {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    def calculate_rfm_scores(self):
        try:
            # Get customer purchase data
            query = """
                SELECT 
                    e.customer_id,
                    COUNT(*) as frequency,
                    MAX(e.timestamp) as last_purchase,
                    SUM(p.price) as total_spent
                FROM event_logs e
                JOIN product_catalog p ON e.product_id = p.product_id
                WHERE e.event_type = 'purchase'
                GROUP BY e.customer_id
            """
            df = pd.read_sql_query(query, self.conn)
            
            if df.empty:
                logger.warning("No purchase data found")
                return pd.DataFrame()
            
            # Calculate RFM scores
            now = datetime.now()
            df['recency'] = (now - pd.to_datetime(df['last_purchase'])).dt.days
            
            # Normalize scores
            for col in ['recency', 'frequency', 'total_spent']:
                df[f'{col}_score'] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())
            
            # Invert recency score (lower is better)
            df['recency_score'] = 1 - df['recency_score']
            
            # Calculate weighted score
            weights = self.config['rfm_weights']
            df['total_score'] = (
                weights['recency'] * df['recency_score'] +
                weights['frequency'] * df['frequency_score'] +
                weights['monetary'] * df['total_spent_score']
            )
            
            return df[['customer_id', 'total_score']]
            
        except Exception as e:
            logger.error(f"Error calculating RFM scores: {e}")
            raise

    def cluster_customers(self, rfm_scores):
        try:
            if rfm_scores.empty:
                logger.warning("No RFM scores to cluster")
                return pd.DataFrame()
            
            # Prepare data for clustering
            X = rfm_scores[['total_score']].values
            
            # Apply KMeans clustering
            kmeans = KMeans(
                n_clusters=self.config['kmeans_clusters'],
                random_state=42
            )
            rfm_scores['cluster'] = kmeans.fit_predict(X)
            
            # Map clusters to segments based on centroid values
            centroids = kmeans.cluster_centers_.flatten()
            cluster_ranks = np.argsort(centroids)
            segment_map = dict(zip(
                cluster_ranks,
                self.config['segment_tags']
            ))
            
            # Assign segments
            rfm_scores['segment_tag'] = rfm_scores['cluster'].map(segment_map)
            
            return rfm_scores[['customer_id', 'segment_tag', 'total_score']]
            
        except Exception as e:
            logger.error(f"Error clustering customers: {e}")
            raise

    def save_segments(self, segments):
        try:
            if segments.empty:
                logger.warning("No segments to save")
                return
            
            # Clear existing segments
            self.cursor.execute("DELETE FROM customer_segments")
            
            # Insert new segments
            for _, row in segments.iterrows():
                self.cursor.execute("""
                    INSERT INTO customer_segments (customer_id, segment_tag, score)
                    VALUES (?, ?, ?)
                """, (row['customer_id'], row['segment_tag'], row['total_score']))
            
            self.conn.commit()
            logger.info(f"Saved {len(segments)} customer segments")
            
        except Exception as e:
            logger.error(f"Error saving segments: {e}")
            raise

    def run(self):
        try:
            self.connect_db()
            
            # Calculate RFM scores
            rfm_scores = self.calculate_rfm_scores()
            
            # Cluster customers and assign segments
            segments = self.cluster_customers(rfm_scores)
            
            # Save results
            self.save_segments(segments)
            
        except Exception as e:
            logger.error(f"Error in segmentation agent: {e}")
            raise
        finally:
            if self.conn:
                self.conn.close()

def main():
    agent = SegmentationAgent()
    agent.run()

if __name__ == "__main__":
    main() 