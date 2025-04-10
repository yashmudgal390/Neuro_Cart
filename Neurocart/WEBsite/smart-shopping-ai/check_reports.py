import sqlite3
import json
from pathlib import Path

def check_reports():
    # Get the database path
    db_path = Path(__file__).parent / 'database' / 'data.db'
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the reports table exists
        cursor.execute('''
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='reports'
        ''')
        if not cursor.fetchone():
            print("❌ Reports table does not exist!")
            return
        
        # Count reports
        cursor.execute('SELECT COUNT(*) FROM reports')
        count = cursor.fetchone()[0]
        print(f"📊 Found {count} reports in the database")
        
        # Get the latest report
        cursor.execute('''
            SELECT report_type, data_blob, timestamp 
            FROM reports 
            ORDER BY timestamp DESC 
            LIMIT 1
        ''')
        report = cursor.fetchone()
        
        if report:
            print("\n📝 Latest Report:")
            print(f"Type: {report[0]}")
            print(f"Timestamp: {report[2]}")
            try:
                data = json.loads(report[1])
                print("\nData Preview:")
                print(json.dumps(data, indent=2)[:500] + "...")
            except json.JSONDecodeError:
                print("\n❌ Error: Report data is not valid JSON")
        else:
            print("\n❌ No reports found in the database")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_reports() 