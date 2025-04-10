import os
import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
import json
import logging
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class InsightsReporter:
    def __init__(self):
        # Get project root directory (parent of agents directory)
        self.project_root = Path(__file__).parent.parent
        self.db_path = self.project_root / 'database' / 'data.db'
        self.reports_dir = self.project_root / 'reports'
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Set default style for plots
        plt.style.use('seaborn-v0_8-darkgrid')
        
    def connect_db(self):
        """Connect to the SQLite database."""
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found at {self.db_path}. Please run init_db.py first.")
        return sqlite3.connect(self.db_path)

    def get_best_performing_products(self, conn, limit=10):
        """Retrieve best performing products based on conversion rate and revenue."""
        try:
            query = """
            WITH product_metrics AS (
                SELECT 
                    p.product_id,
                    p.name,
                    COALESCE(COUNT(DISTINCT r.customer_id), 0) as recommendation_count,
                    COALESCE(COUNT(DISTINCT CASE WHEN e.event_type = 'purchase' THEN e.customer_id END), 0) as purchase_count,
                    COALESCE(AVG(p.price), 0) as avg_price
                FROM product_catalog p
                LEFT JOIN recommendation_results r ON p.product_id = r.recommendations
                LEFT JOIN event_logs e ON p.product_id = e.product_id
                GROUP BY p.product_id, p.name
            )
            SELECT 
                product_id,
                name,
                recommendation_count,
                purchase_count,
                CASE 
                    WHEN recommendation_count = 0 THEN 0 
                    ELSE ROUND(CAST(purchase_count AS FLOAT) / recommendation_count * 100, 2)
                END as conversion_rate,
                ROUND(avg_price * purchase_count, 2) as total_revenue
            FROM product_metrics
            WHERE recommendation_count > 0
            ORDER BY total_revenue DESC
            LIMIT ?
            """
            df = pd.read_sql_query(query, conn, params=(limit,))
            return df if not df.empty else None
        except Exception as e:
            logger.error(f"Error retrieving best performing products: {str(e)}")
            return None

    def get_segment_conversion_metrics(self, conn):
        """Retrieve conversion metrics by customer segment."""
        try:
            query = """
            WITH segment_metrics AS (
                SELECT 
                    cs.segment_tag,
                    COUNT(DISTINCT r.customer_id) as total_recommendations,
                    COUNT(DISTINCT CASE WHEN e.event_type = 'purchase' THEN e.customer_id END) as purchases
                FROM customer_segments cs
                LEFT JOIN recommendation_results r ON cs.customer_id = r.customer_id
                LEFT JOIN event_logs e ON cs.customer_id = e.customer_id
                GROUP BY cs.segment_tag
            )
            SELECT 
                segment_tag,
                total_recommendations,
                purchases,
                CASE 
                    WHEN total_recommendations = 0 THEN 0 
                    ELSE ROUND(CAST(purchases AS FLOAT) / total_recommendations * 100, 2)
                END as conversion_rate
            FROM segment_metrics
            ORDER BY conversion_rate DESC
            """
            df = pd.read_sql_query(query, conn)
            return df if not df.empty else None
        except Exception as e:
            logger.error(f"Error retrieving segment conversion metrics: {str(e)}")
            return None

    def get_engagement_heatmap_data(self, conn):
        """Retrieve engagement data for heatmap visualization."""
        try:
            query = """
            SELECT 
                cs.segment_tag,
                pc.category,
                COUNT(e.id) as engagement_count
            FROM customer_segments cs
            JOIN event_logs e ON cs.customer_id = e.customer_id
            JOIN product_catalog pc ON e.product_id = pc.product_id
            GROUP BY cs.segment_tag, pc.category
            """
            df = pd.read_sql_query(query, conn)
            if df.empty:
                return None
            
            # Pivot the data for heatmap
            heatmap_data = df.pivot(
                index='segment_tag', 
                columns='category', 
                values='engagement_count'
            ).fillna(0)
            return heatmap_data
        except Exception as e:
            logger.error(f"Error retrieving engagement heatmap data: {str(e)}")
            return None

    def generate_visualizations(self, products_df, segments_df, heatmap_data):
        """Generate and save visualizations."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if products_df is not None and not products_df.empty:
                # Best performing products
                plt.figure(figsize=(12, 6))
                sns.barplot(data=products_df, x='name', y='total_revenue')
                plt.xticks(rotation=45, ha='right')
                plt.title('Best Performing Products by Revenue')
                plt.tight_layout()
                plt.savefig(self.reports_dir / f'product_performance_{timestamp}.png')
                plt.close()

            if segments_df is not None and not segments_df.empty:
                # Segment conversion rates
                plt.figure(figsize=(10, 6))
                sns.barplot(data=segments_df, x='segment_tag', y='conversion_rate')
                plt.title('Conversion Rates by Customer Segment')
                plt.tight_layout()
                plt.savefig(self.reports_dir / f'segment_conversion_{timestamp}.png')
                plt.close()

            if heatmap_data is not None and not heatmap_data.empty:
                # Engagement heatmap
                plt.figure(figsize=(12, 8))
                sns.heatmap(heatmap_data, annot=True, fmt='.0f', cmap='YlOrRd')
                plt.title('Customer Segment vs Category Engagement')
                plt.tight_layout()
                plt.savefig(self.reports_dir / f'engagement_heatmap_{timestamp}.png')
                plt.close()

        except Exception as e:
            logger.error(f"Error generating visualizations: {str(e)}")
            raise

    def save_report(self, conn, products_df, segments_df, heatmap_data):
        """Save report data to database."""
        try:
            timestamp = datetime.now().isoformat()
            report_data = {
                'timestamp': timestamp,
                'best_performing_products': products_df.to_dict('records') if products_df is not None else [],
                'segment_metrics': segments_df.to_dict('records') if segments_df is not None else [],
                'engagement_heatmap': heatmap_data.to_dict() if heatmap_data is not None else {}
            }
            
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO reports (report_type, data_blob) VALUES (?, ?)",
                ('performance_insights', json.dumps(report_data))
            )
            conn.commit()
            logger.info(f"Report saved successfully at {timestamp}")
            
        except Exception as e:
            logger.error(f"Error saving report: {str(e)}")
            conn.rollback()
            raise

    def run(self):
        """Run the insights reporter agent."""
        try:
            conn = self.connect_db()
            logger.info(f"Connected to database at {self.db_path}")

            # Retrieve data
            products_df = self.get_best_performing_products(conn)
            segments_df = self.get_segment_conversion_metrics(conn)
            heatmap_data = self.get_engagement_heatmap_data(conn)

            if all(data is None for data in [products_df, segments_df, heatmap_data]):
                logger.warning("No data available for reporting. Please ensure the database has been populated.")
                return

            # Generate visualizations
            self.generate_visualizations(products_df, segments_df, heatmap_data)
            
            # Save report
            self.save_report(conn, products_df, segments_df, heatmap_data)
            
            logger.info("Report generation completed successfully")
            
        except Exception as e:
            logger.error(f"Error in insights reporter agent: {str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()

if __name__ == '__main__':
    reporter = InsightsReporter()
    reporter.run() 