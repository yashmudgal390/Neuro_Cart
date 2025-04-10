import sqlite3
import json
from datetime import datetime
from pathlib import Path

def generate_test_report():
    # Get the database path
    db_path = Path(__file__).parent / 'database' / 'data.db'
    
    # Sample report data
    report_data = {
        'best_performing_products': [
            {'product_id': 'P001', 'name': 'Wireless Headphones', 'sales': 150, 'revenue': 29998.50},
            {'product_id': 'P002', 'name': 'Smart Watch', 'sales': 120, 'revenue': 35998.80},
            {'product_id': 'P003', 'name': 'Running Shoes', 'sales': 200, 'revenue': 17998.00}
        ],
        'conversion_by_segment': [
            {'segment': 'frequent_buyer', 'conversion_rate': 0.85},
            {'segment': 'discount_seeker', 'conversion_rate': 0.45},
            {'segment': 'new_user', 'conversion_rate': 0.25}
        ],
        'engagement_heatmap': {
            'Electronics': {'frequent_buyer': 0.8, 'discount_seeker': 0.6, 'new_user': 0.4},
            'Sports': {'frequent_buyer': 0.7, 'discount_seeker': 0.5, 'new_user': 0.3},
            'Home': {'frequent_buyer': 0.6, 'discount_seeker': 0.4, 'new_user': 0.2}
        },
        'metrics': {
            'average_order_value': 299.99,
            'conversion_rate': 0.65,
            'retention_rate': 0.75
        }
    }
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Insert the report
        cursor.execute('''
            INSERT INTO reports (report_type, data_blob, timestamp)
            VALUES (?, ?, ?)
        ''', (
            'insights',
            json.dumps(report_data),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        print("✅ Test report generated and inserted successfully")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    generate_test_report() 