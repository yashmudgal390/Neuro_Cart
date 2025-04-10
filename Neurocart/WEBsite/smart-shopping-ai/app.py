import os
import argparse
import logging
from pathlib import Path
import time
from datetime import datetime
import sqlite3
import json
import pandas as pd
import numpy as np
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, IntegerField, TextAreaField, FloatField, BooleanField
from wtforms.validators import DataRequired, Optional, NumberRange
import sys
from recommendation_model import RecommendationModel
import uuid
import random

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

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this to a secure key in production

# Initialize recommendation model
recommendation_model = RecommendationModel()

# Database connection function
def get_db_connection():
    """Get a connection to the SQLite database."""
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database', 'data.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# Form for user input
class UserForm(FlaskForm):
    age = IntegerField('Age', validators=[DataRequired(), NumberRange(min=1, max=120)])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    location = StringField('Location', validators=[DataRequired()])
    interests = TextAreaField('Interests', validators=[DataRequired()])

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

# Flask routes
@app.route('/')
def index():
    form = UserForm()
    return render_template('index.html', form=form)

@app.route('/recommendations', methods=['GET', 'POST'])
def get_recommendations():
    if request.method == 'POST':
        try:
            # Get form data
            age = request.form.get('age', type=int)
            gender = request.form.get('gender')
            location = request.form.get('location')
            interests = request.form.get('interests', '').split(',')
            interests = [interest.strip() for interest in interests if interest.strip()]
            
            # Generate a temporary customer ID for the session
            temp_customer_id = str(uuid.uuid4())[:8]
            
            # Store user data in database
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO customer_sessions 
                (customer_id, age, gender, location, interests, registration_date, last_active)
                VALUES (?, ?, ?, ?, ?, date('now'), date('now'))
            """, (temp_customer_id, age, gender, location, json.dumps(interests)))
            
            conn.commit()
            
            # Get personalized recommendations
            recommendations = recommendation_model.get_recommendations({
                'customer_id': temp_customer_id,
                'age': age,
                'gender': gender,
                'location': location,
                'interests': interests
            })
            
            # Track this recommendation request
            if recommendations:
                for rec in recommendations:
                    cursor.execute("""
                        INSERT INTO event_logs 
                        (interaction_id, customer_id, product_id, event_type, timestamp, dwell_time)
                        VALUES (?, ?, ?, ?, datetime('now'), ?)
                    """, (str(uuid.uuid4()), temp_customer_id, rec['product_id'], 'recommendation', random.randint(1, 10)))
            
            conn.commit()
            conn.close()
            
            app.logger.info(f"Generated recommendations for user {temp_customer_id}: {len(recommendations)} items")
            
            return render_template(
                'recommendations.html',
                customer_id=temp_customer_id,
                age=age,
                gender=gender,
                location=location,
                interests=interests,
                recommendations=recommendations
            )
            
        except Exception as e:
            app.logger.error(f"Error generating recommendations: {e}")
            flash("An error occurred while generating recommendations. Please try again.", "error")
            return redirect(url_for('index'))
    
    return redirect(url_for('index'))

@app.route('/reports')
def reports():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get overall statistics
    cursor.execute("""
        SELECT 
            COUNT(DISTINCT c.customer_id) as total_customers,
            COUNT(DISTINCT CASE WHEN e.event_type = 'purchase' THEN c.customer_id END) as purchasing_customers,
            COUNT(CASE WHEN e.event_type = 'purchase' THEN 1 END) as total_purchases,
            COUNT(CASE WHEN e.event_type = 'view' THEN 1 END) as total_views,
            ROUND(AVG(CASE WHEN e.event_type = 'view' THEN e.dwell_time END), 2) as avg_view_time
        FROM customer_sessions c
        LEFT JOIN event_logs e ON c.customer_id = e.customer_id
    """)
    stats = cursor.fetchone()
    
    # Get top products
    cursor.execute("""
        SELECT 
            p.name,
            p.category,
            COUNT(CASE WHEN e.event_type = 'view' THEN 1 END) as views,
            COUNT(CASE WHEN e.event_type = 'purchase' THEN 1 END) as purchases,
            ROUND(AVG(CASE WHEN e.event_type = 'view' THEN e.dwell_time END), 2) as avg_view_time
        FROM product_catalog p
        LEFT JOIN event_logs e ON p.product_id = e.product_id
        GROUP BY p.product_id, p.name, p.category
        ORDER BY purchases DESC, views DESC
        LIMIT 10
    """)
    top_products = cursor.fetchall()
    
    # Get customer segments
    cursor.execute("""
        SELECT 
            c.location,
            COUNT(DISTINCT c.customer_id) as customer_count,
            ROUND(AVG(c.age)) as avg_age,
            COUNT(DISTINCT CASE WHEN e.event_type = 'purchase' THEN c.customer_id END) as purchasing_customers
        FROM customer_sessions c
        LEFT JOIN event_logs e ON c.customer_id = e.customer_id
        GROUP BY c.location
        ORDER BY customer_count DESC
        LIMIT 10
    """)
    segments = cursor.fetchall()
    
    return render_template('reports.html',
                         stats=stats,
                         top_products=top_products,
                         segments=segments)

@app.route('/api/health')
def health_check():
    return jsonify({"status": "healthy"})

@app.route('/api/recommendations/<customer_id>')
def get_customer_recommendations(customer_id):
    try:
        recommendations = recommendation_model.get_recommendations({'customer_id': customer_id})
        return jsonify(recommendations)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/products/<product_id>')
def get_product(product_id):
    try:
        # Load product data
        products_df = pd.read_csv('data/products.csv')
        product = products_df[products_df['Product_ID'] == product_id].iloc[0]
        
        return jsonify({
            'product_id': product_id,
            'category': product['Category'],
            'subcategory': product['Subcategory'],
            'price': float(product['Price']),
            'brand': product['Brand'],
            'average_rating': float(product['Average_Rating']),
            'product_rating': float(product['Product_Rating']),
            'customer_rating': float(product['Customer_Rating']),
            'holiday_item': product['Holiday_Item'] == 'Yes',
            'season': product['Season'],
            'geographic_origin': product['Geographic_Origin'],
            'similar_products': eval(product['Similar_Products']),
            'probability': float(product['Probability'])
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/api/track_event', methods=['POST'])
def track_event():
    event_data = request.json
    # Log the event data
    print(f"Event tracked: {event_data}")
    return jsonify({"status": "success"})

def run_pipeline():
    """Run the pipeline from the command line."""
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
    # Check if we're running the pipeline or the web server
    if len(sys.argv) > 1 and sys.argv[1] == '--pipeline':
        # Run the pipeline
        run_pipeline()
    else:
        # Train the recommendation model
        print("Training recommendation model...")
        recommendation_model.train()
        print("Model training completed!")
        
        # Run the Flask app
        app.run(debug=True, port=5000) 