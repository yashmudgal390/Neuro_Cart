import os
import json
import sqlite3
import pandas as pd
from pathlib import Path
import logging
from flask import Flask, request, jsonify, render_template, send_from_directory
from datetime import datetime
from werkzeug.utils import secure_filename

# Import agents
from agents.recommendation_engine import RecommendationEngine
from agents.reporter import InsightsReporter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("api.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Get the absolute path to the project root
PROJECT_ROOT = Path(__file__).parent.absolute()
DB_PATH = PROJECT_ROOT / 'database' / 'data.db'
UPLOAD_FOLDER = PROJECT_ROOT / "data"
ALLOWED_EXTENSIONS = {'csv'}

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def connect_db():
    """Connect to the SQLite database."""
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found at {DB_PATH}. Please run init_db.py first.")
    return sqlite3.connect(DB_PATH)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    """Create a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Web routes
@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/upload')
def upload_page():
    """Render the upload page."""
    return render_template('upload.html')

@app.route('/recommendations')
def recommendations_page():
    """Render the recommendations page."""
    return render_template('recommendations.html')

@app.route('/segments')
def segments_page():
    """Render the segments page."""
    return render_template('segments.html')

@app.route('/reports')
def reports_page():
    """Render the reports page."""
    return render_template('reports.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    try:
        conn = connect_db()
        conn.execute('SELECT 1')
        conn.close()
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@app.route('/api/upload', methods=['POST'])
def upload_files():
    """Handle file uploads."""
    try:
        if 'customers' not in request.files or 'products' not in request.files:
            return jsonify({'error': 'Missing required files'}), 400
            
        customers_file = request.files['customers']
        products_file = request.files['products']
        events_file = request.files.get('events')
        
        if not all(allowed_file(f.filename) for f in [customers_file, products_file] if f):
            return jsonify({'error': 'Invalid file type. Only CSV files are allowed.'}), 400
            
        # Save files
        customers_path = UPLOAD_FOLDER / secure_filename(customers_file.filename)
        products_path = UPLOAD_FOLDER / secure_filename(products_file.filename)
        
        customers_file.save(customers_path)
        products_file.save(products_path)
        
        if events_file:
            events_path = UPLOAD_FOLDER / secure_filename(events_file.filename)
            events_file.save(events_path)
            
        # Process the files
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Load customers data
        customers_df = pd.read_csv(customers_path)
        customers_df.to_sql('customer_sessions', conn, if_exists='replace', index=False)
        
        # Load products data
        products_df = pd.read_csv(products_path)
        products_df.to_sql('product_catalog', conn, if_exists='replace', index=False)
        
        # Load events data if provided
        if events_file:
            events_df = pd.read_csv(events_path)
            events_df.to_sql('event_logs', conn, if_exists='replace', index=False)
            
        conn.commit()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'message': 'Files uploaded and processed successfully'
        })
        
    except Exception as e:
        logger.error(f"Error uploading files: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/recommendations/<customer_id>', methods=['GET'])
def get_recommendations(customer_id):
    """Get personalized recommendations for a customer."""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        # Get customer's segment
        cursor.execute('''
            SELECT segment_tag, score 
            FROM customer_segments 
            WHERE customer_id = ?
        ''', (customer_id,))
        segment = cursor.fetchone()
        
        if not segment:
            return jsonify({
                'error': 'Customer not found'
            }), 404
            
        # Get recommendations
        cursor.execute('''
            SELECT recommendations, confidence_scores
            FROM recommendation_results
            WHERE customer_id = ?
            ORDER BY timestamp DESC
            LIMIT 1
        ''', (customer_id,))
        result = cursor.fetchone()
        
        if not result:
            return jsonify({
                'error': 'No recommendations found'
            }), 404
            
        recommendations = json.loads(result['recommendations'])
        confidence_scores = json.loads(result['confidence_scores'])
        
        # Get product details for recommendations
        product_ids = recommendations[:5]  # Get top 5 recommendations
        placeholders = ','.join('?' * len(product_ids))
        cursor.execute(f'''
            SELECT product_id, name, price, category
            FROM product_catalog
            WHERE product_id IN ({placeholders})
        ''', product_ids)
        
        products = cursor.fetchall()
        
        response = {
            'customer_id': customer_id,
            'segment': dict(segment),
            'recommendations': [
                {
                    'product': dict(product),
                    'confidence_score': confidence_scores[i]
                }
                for i, product in enumerate(products)
            ]
        }
        
        conn.close()
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/products/<product_id>', methods=['GET'])
def get_product(product_id):
    """Get product details."""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT *
            FROM product_catalog
            WHERE product_id = ?
        ''', (product_id,))
        
        product = cursor.fetchone()
        conn.close()
        
        if not product:
            return jsonify({
                'error': 'Product not found'
            }), 404
            
        return jsonify(dict(product))
        
    except Exception as e:
        logger.error(f"Error getting product: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/segments', methods=['GET'])
def get_segments():
    """Get customer segment distribution."""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT segment_tag, COUNT(*) as count
            FROM customer_segments
            GROUP BY segment_tag
        ''')
        
        segments = cursor.fetchall()
        conn.close()
        
        return jsonify({
            'segments': [dict(segment) for segment in segments]
        })
        
    except Exception as e:
        logger.error(f"Error getting segments: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports/latest', methods=['GET'])
def get_latest_report():
    """Get the latest insights report."""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT report_type, data_blob
            FROM reports
            ORDER BY timestamp DESC
            LIMIT 1
        ''')
        
        report = cursor.fetchone()
        conn.close()
        
        if not report:
            return jsonify({
                'error': 'No reports found'
            }), 404
            
        return jsonify({
            'type': report['report_type'],
            'data': json.loads(report['data_blob'])
        })
        
    except Exception as e:
        logger.error(f"Error getting report: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/track_event', methods=['POST'])
def track_event():
    """Track customer events (views, clicks, purchases)."""
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ['customer_id', 'event_type', 'product_id']):
            return jsonify({
                'error': 'Missing required fields'
            }), 400
            
        conn = connect_db()
        cursor = conn.cursor()
        
        # Insert event into event_logs
        cursor.execute('''
            INSERT INTO event_logs (
                session_id, category, dwell_time, event_type
            ) VALUES (
                ?, ?, ?, ?
            )
        ''', (
            f"S{datetime.now().strftime('%Y%m%d%H%M%S')}",
            data.get('category', 'unknown'),
            data.get('dwell_time', 0),
            data['event_type']
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error tracking event: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Ensure database exists
    if not DB_PATH.exists():
        logger.warning(f"Database not found at {DB_PATH}. Please run init_db.py first.")
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True) 