import sqlite3
import json
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.customer_agent import CustomerAgent

class ProductAgent:
    def __init__(self, db_path=os.path.join(os.path.dirname(__file__), '..', 'db', 'ecommerce.db')):
        self.db_path = os.path.abspath(db_path)
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database file not found at: {self.db_path}")

    def get_products(self, customer_profile):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products")
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return []

        columns = ["Product_ID", "Category", "Subcategory", "Price", "Brand", "Average_Rating_of_Similar_Products",
                   "Product_Rating", "Customer_Review_Sentiment_Score", "Holiday", "Season", "Geographical_Location",
                   "Similar_Product_List", "Probability_of_Recommendation"]
        products = [dict(zip(columns, row)) for row in rows]
        for p in products:
            p["Similar_Product_List"] = json.loads(p["Similar_Product_List"])

        # Stricter filtering: Must match preferences AND budget
        filtered = [p for p in products if p["Category"] in customer_profile["preferences"] and 
                    p["Price"] <= customer_profile["budget"] * 1.5]
        
        # Limit to 100 products to avoid overloading RecommendationAgent
        return filtered[:100]

if __name__ == "__main__":
    ca = CustomerAgent()
    try:
        profile = ca.get_customer_profile("C1000")
        pa = ProductAgent()
        products = pa.get_products(profile)
        for p in products:
            print(f"Product: {p['Product_ID']} - {p['Subcategory']} (${p['Price']})")
    except Exception as e:
        print(f"Error: {e}")