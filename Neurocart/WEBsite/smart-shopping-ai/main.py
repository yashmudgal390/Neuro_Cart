#!/usr/bin/env python
"""
Smart Shopping AI - Main Application
A multi-agent system for hyper-personalized product recommendations
"""

import os
import argparse
import logging
from pathlib import Path
import time
from datetime import datetime
import sqlite3
import json
from flask import Flask, render_template, jsonify

# Import agents
from agents.customer_loader import CustomerLoaderAgent
from agents.segmenter import SegmentationAgent
from agents.product_catalog import ProductCatalogAgent
from agents.recommendation_engine import RecommendationEngine
from agents.optimizer import ShoppingOptimizer
from agents.reporter import InsightsReporter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("smart_shopping_ai.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SmartShoppingAI:
    def __init__(self):
        # Get the absolute path to the project root
        self.project_root = Path(__file__).parent.absolute()
        
        # Set up paths
        self.data_dir = self.project_root / 'data'
        self.db_path = self.project_root / 'database' / 'data.db'
        
        # Ensure directories exist
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.project_root / 'database', exist_ok=True)
        os.makedirs(self.project_root / 'reports', exist_ok=True)
        os.makedirs(self.project_root / 'embeddings', exist_ok=True)
        
        # Initialize agents
        self.customer_loader = None
        self.segmenter = None
        self.product_catalog = None
        self.recommendation_engine = None
        self.optimizer = None
        self.reporter = None
        
        logger.info(f"Smart Shopping AI initialized at {self.project_root}")

    def initialize_database(self):
        """Initialize the database using the schema.sql file."""
        try:
            from database.init_db import init_database
            init_database()
            logger.info("Database initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            return False

    def load_customer_data(self):
        """Load customer data from CSV files."""
        try:
            customers_file = self.data_dir / 'customers.csv'
            self.customer_loader = CustomerLoaderAgent(str(customers_file))
            self.customer_loader.run()
            logger.info("Customer data loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to load customer data: {e}")
            return False

    def segment_customers(self):
        """Segment customers using RFM and KMeans clustering."""
        try:
            self.segmenter = SegmentationAgent()
            self.segmenter.run()
            logger.info("Customer segmentation completed successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to segment customers: {e}")
            return False

    def process_product_catalog(self):
        """Process product catalog and generate embeddings."""
        try:
            products_file = self.data_dir / 'products.csv'
            self.product_catalog = ProductCatalogAgent(str(products_file))
            self.product_catalog.run()
            logger.info("Product catalog processed successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to process product catalog: {e}")
            return False

    def generate_recommendations(self):
        """Generate personalized product recommendations."""
        try:
            self.recommendation_engine = RecommendationEngine()
            self.recommendation_engine.run()
            logger.info("Recommendations generated successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            return False

    def optimize_shopping(self):
        """Track and optimize shopping performance."""
        try:
            self.optimizer = ShoppingOptimizer()
            self.optimizer.run()
            logger.info("Shopping optimization completed successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to optimize shopping: {e}")
            return False

    def generate_reports(self):
        """Generate insights and reports."""
        try:
            self.reporter = InsightsReporter()
            self.reporter.run()
            logger.info("Reports generated successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to generate reports: {e}")
            return False

    def run_pipeline(self, steps=None):
        """
        Run the entire pipeline or specific steps.
        
        Args:
            steps (list): List of steps to run. If None, run all steps.
        """
        pipeline = {
            'init_db': self.initialize_database,
            'load_customers': self.load_customer_data,
            'segment_customers': self.segment_customers,
            'process_products': self.process_product_catalog,
            'generate_recommendations': self.generate_recommendations,
            'optimize_shopping': self.optimize_shopping,
            'generate_reports': self.generate_reports
        }
        
        if steps is None:
            steps = list(pipeline.keys())
        
        results = {}
        for step in steps:
            if step in pipeline:
                logger.info(f"Running step: {step}")
                start_time = time.time()
                success = pipeline[step]()
                end_time = time.time()
                duration = end_time - start_time
                
                results[step] = {
                    'success': success,
                    'duration': duration
                }
                
                if success:
                    logger.info(f"Step '{step}' completed successfully in {duration:.2f} seconds")
                else:
                    logger.error(f"Step '{step}' failed after {duration:.2f} seconds")
            else:
                logger.warning(f"Unknown step: {step}")
        
        return results

def main():
    parser = argparse.ArgumentParser(description='Smart Shopping AI - Multi-agent recommendation system')
    parser.add_argument('--steps', nargs='+', 
                      choices=['init_db', 'load_customers', 'segment_customers', 
                               'process_products', 'generate_recommendations', 
                               'optimize_shopping', 'generate_reports'],
                      help='Specific steps to run. If not provided, all steps will run.')
    
    args = parser.parse_args()
    
    app = SmartShoppingAI()
    results = app.run_pipeline(args.steps)
    
    # Print summary
    print("\n=== Pipeline Execution Summary ===")
    for step, result in results.items():
        status = "✅ SUCCESS" if result['success'] else "❌ FAILED"
        print(f"{step}: {status} ({result['duration']:.2f} seconds)")
    
    print("\nCheck smart_shopping_ai.log for detailed logs.")

if __name__ == "__main__":
    main() 