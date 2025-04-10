import os
import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
import json
import logging
import pickle
from sklearn.metrics.pairwise import cosine_similarity

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RecommendationEngine:
    def __init__(self):
        # Get the absolute path to the project root
        self.project_root = Path(__file__).parent.parent.absolute()
        
        # Set up paths
        self.db_path = self.project_root / 'database' / 'data.db'
        self.embeddings_path = self.project_root / 'embeddings' / 'product_vectors.pkl'
        
        self.conn = None
        self.cursor = None
        self.product_embeddings = None

    def connect_db(self):
        try:
            self.conn = sqlite3.connect(str(self.db_path))
            self.cursor = self.conn.cursor()
            logger.info(f"Connected to database at {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    def load_embeddings(self):
        try:
            with open(self.embeddings_path, 'rb') as f:
                self.product_embeddings = pickle.load(f)
            logger.info(f"Loaded embeddings for {len(self.product_embeddings)} products")
        except Exception as e:
            logger.error(f"Error loading embeddings: {e}")
            raise

    def get_customer_interests(self, customer_id):
        try:
            # Get customer's interaction history
            query = """
                SELECT 
                    e.product_id,
                    e.event_type,
                    COUNT(*) as interaction_count
                FROM event_logs e
                WHERE e.customer_id = ?
                GROUP BY e.product_id, e.event_type
            """
            df = pd.read_sql_query(query, self.conn, params=(customer_id,))
            
            if df.empty:
                return None
            
            # Weight different event types
            weights = {
                'click': 1,
                'add_to_cart': 2,
                'purchase': 3
            }
            
            # Calculate weighted interest score for each product
            product_scores = {}
            for _, row in df.iterrows():
                score = weights.get(row['event_type'], 1) * row['interaction_count']
                product_scores[row['product_id']] = score
            
            return product_scores
            
        except Exception as e:
            logger.error(f"Error getting customer interests: {e}")
            raise

    def get_segment_preferences(self, customer_id):
        try:
            # Get customer's segment
            query = """
                SELECT segment_tag
                FROM customer_segments
                WHERE customer_id = ?
            """
            self.cursor.execute(query, (customer_id,))
            result = self.cursor.fetchone()
            
            if not result:
                return None
            
            segment_tag = result[0]
            
            # Get popular products in the segment
            query = """
                SELECT 
                    p.product_id,
                    COUNT(*) as purchase_count
                FROM event_logs e
                JOIN customer_segments cs ON e.customer_id = cs.customer_id
                JOIN product_catalog p ON e.product_id = p.product_id
                WHERE cs.segment_tag = ?
                AND e.event_type = 'purchase'
                GROUP BY p.product_id
                ORDER BY purchase_count DESC
            """
            df = pd.read_sql_query(query, self.conn, params=(segment_tag,))
            
            if df.empty:
                return None
            
            return dict(zip(df['product_id'], df['purchase_count']))
            
        except Exception as e:
            logger.error(f"Error getting segment preferences: {e}")
            raise

    def generate_recommendations(self, customer_id, n_recommendations=5):
        try:
            # Get customer interests
            interests = self.get_customer_interests(customer_id)
            
            # Get segment preferences
            segment_prefs = self.get_segment_preferences(customer_id)
            
            # If no history, use segment preferences or popularity
            if not interests:
                if segment_prefs:
                    recommendations = list(segment_prefs.keys())[:n_recommendations]
                else:
                    # Use overall popularity
                    query = """
                        SELECT product_id
                        FROM product_catalog
                        ORDER BY popularity DESC
                        LIMIT ?
                    """
                    self.cursor.execute(query, (n_recommendations,))
                    recommendations = [r[0] for r in self.cursor.fetchall()]
                
                confidence_scores = [0.5] * len(recommendations)  # Lower confidence for non-personalized recs
                return recommendations, confidence_scores
            
            # Calculate similarity scores
            product_scores = {}
            for product_id, embedding in self.product_embeddings.items():
                # Skip products the customer has already interacted with
                if product_id in interests:
                    continue
                
                # Calculate similarity with interested products
                similarities = []
                for int_prod_id, int_score in interests.items():
                    if int_prod_id in self.product_embeddings:
                        sim = cosine_similarity(
                            embedding.reshape(1, -1),
                            self.product_embeddings[int_prod_id].reshape(1, -1)
                        )[0][0]
                        similarities.append(sim * int_score)
                
                if similarities:
                    # Combine similarity with segment preference
                    score = np.mean(similarities)
                    if segment_prefs and product_id in segment_prefs:
                        score *= 1.2  # Boost score for products popular in segment
                    
                    product_scores[product_id] = score
            
            # Sort by score and get top N
            sorted_products = sorted(product_scores.items(), key=lambda x: x[1], reverse=True)
            recommendations = [p[0] for p in sorted_products[:n_recommendations]]
            confidence_scores = [p[1] for p in sorted_products[:n_recommendations]]
            
            return recommendations, confidence_scores
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            raise

    def save_recommendations(self, customer_id, recommendations, confidence_scores):
        try:
            # Convert lists to JSON strings
            rec_json = json.dumps(recommendations)
            conf_json = json.dumps(confidence_scores)
            
            # Save to database
            self.cursor.execute("""
                INSERT INTO recommendation_results 
                (customer_id, recommendations, confidence_scores)
                VALUES (?, ?, ?)
            """, (customer_id, rec_json, conf_json))
            
            self.conn.commit()
            logger.info(f"Saved recommendations for customer {customer_id}")
            
        except Exception as e:
            logger.error(f"Error saving recommendations: {e}")
            raise

    def run(self):
        try:
            self.connect_db()
            self.load_embeddings()
            
            # Get all customers
            self.cursor.execute("SELECT customer_id FROM customer_sessions")
            customers = [r[0] for r in self.cursor.fetchall()]
            
            # Generate recommendations for each customer
            for customer_id in customers:
                recommendations, confidence_scores = self.generate_recommendations(customer_id)
                self.save_recommendations(customer_id, recommendations, confidence_scores)
            
            logger.info(f"Generated recommendations for {len(customers)} customers")
            
        except Exception as e:
            logger.error(f"Error in recommendation engine agent: {e}")
            raise
        finally:
            if self.conn:
                self.conn.close()

def main():
    agent = RecommendationEngine()
    agent.run()

if __name__ == "__main__":
    main() 