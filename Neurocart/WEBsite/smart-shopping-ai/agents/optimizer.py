import os
import sqlite3
import pandas as pd
import numpy as np
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

class ShoppingOptimizer:
    def __init__(self):
        # Get the absolute path to the project root
        self.project_root = Path(__file__).parent.parent.absolute()
        
        # Set up paths
        self.db_path = self.project_root / 'database' / 'data.db'
        
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

    def calculate_metrics(self):
        try:
            # Calculate conversion rates
            query = """
                WITH recommendation_events AS (
                    SELECT 
                        r.customer_id,
                        json_each.value as recommended_product,
                        e.event_type,
                        e.product_id
                    FROM recommendation_results r
                    CROSS JOIN json_each(r.recommendations)
                    LEFT JOIN event_logs e ON 
                        e.customer_id = r.customer_id AND 
                        e.product_id = json_each.value AND
                        e.timestamp > r.timestamp
                ),
                conversion_stats AS (
                    SELECT
                        COUNT(DISTINCT customer_id) as total_customers,
                        COUNT(DISTINCT CASE WHEN event_type = 'click' THEN customer_id END) as clicked_customers,
                        COUNT(DISTINCT CASE WHEN event_type = 'add_to_cart' THEN customer_id END) as cart_customers,
                        COUNT(DISTINCT CASE WHEN event_type = 'purchase' THEN customer_id END) as purchase_customers
                    FROM recommendation_events
                )
                SELECT
                    COALESCE(CAST(clicked_customers AS FLOAT) / NULLIF(total_customers, 0), 0) as ctr,
                    COALESCE(CAST(cart_customers AS FLOAT) / NULLIF(clicked_customers, 0), 0) as cart_rate,
                    COALESCE(CAST(purchase_customers AS FLOAT) / NULLIF(cart_customers, 0), 0) as conversion_rate
                FROM conversion_stats
            """
            df = pd.read_sql_query(query, self.conn)
            
            # Calculate average order value
            query = """
                SELECT 
                    COALESCE(AVG(order_value), 0) as aov
                FROM (
                    SELECT 
                        e.customer_id,
                        SUM(p.price) as order_value
                    FROM event_logs e
                    JOIN product_catalog p ON e.product_id = p.product_id
                    WHERE e.event_type = 'purchase'
                    GROUP BY e.customer_id
                )
            """
            aov_df = pd.read_sql_query(query, self.conn)
            
            # Calculate metrics by segment
            query = """
                SELECT 
                    cs.segment_tag,
                    COUNT(DISTINCT e.customer_id) as active_customers,
                    COUNT(DISTINCT CASE WHEN e.event_type = 'purchase' THEN e.customer_id END) as purchasing_customers,
                    COALESCE(AVG(CASE WHEN e.event_type = 'purchase' THEN p.price ELSE NULL END), 0) as avg_purchase_value
                FROM customer_segments cs
                LEFT JOIN event_logs e ON cs.customer_id = e.customer_id
                LEFT JOIN product_catalog p ON e.product_id = p.product_id
                GROUP BY cs.segment_tag
            """
            segment_df = pd.read_sql_query(query, self.conn)
            
            # Combine metrics
            metrics = {
                'overall': {
                    'ctr': float(df['ctr'].iloc[0]),
                    'cart_rate': float(df['cart_rate'].iloc[0]),
                    'conversion_rate': float(df['conversion_rate'].iloc[0]),
                    'aov': float(aov_df['aov'].iloc[0])
                },
                'segments': segment_df.to_dict('records')
            }
            
            logger.info(f"Calculated metrics: {json.dumps(metrics['overall'], indent=2)}")
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating metrics: {e}")
            raise

    def save_metrics(self, metrics):
        try:
            # Convert metrics to JSON
            metrics_json = json.dumps(metrics)
            
            # Save to database
            self.cursor.execute("""
                INSERT INTO optimization_summary (metrics_json)
                VALUES (?)
            """, (metrics_json,))
            
            self.conn.commit()
            logger.info("Saved optimization metrics")
            
        except Exception as e:
            logger.error(f"Error saving metrics: {e}")
            raise

    def run(self):
        try:
            self.connect_db()
            
            # Calculate metrics
            metrics = self.calculate_metrics()
            
            # Save metrics
            self.save_metrics(metrics)
            
        except Exception as e:
            logger.error(f"Error in shopping optimizer agent: {e}")
            raise
        finally:
            if self.conn:
                self.conn.close()

def main():
    agent = ShoppingOptimizer()
    agent.run()

if __name__ == "__main__":
    main() 