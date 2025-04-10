import sys
import os
import sqlite3
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from agents.customer_agent import CustomerAgent
from agents.product_agent import ProductAgent
from agents.recommendation_agent import RecommendationAgent

def main():
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'db', 'ecommerce.db'))
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database file not found at: {db_path}")

    ca = CustomerAgent()
    pa = ProductAgent()
    ra = RecommendationAgent()

    customer_id = input("Enter Customer ID (e.g., C1000): ").strip()

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT Customer_ID FROM customers WHERE Customer_ID = ?", (customer_id,))
        if not cursor.fetchone():
            print(f"Customer {customer_id} not found in the database!")
            conn.close()
            return
        conn.close()

        print(f"Processing recommendations for {customer_id}...")
        profile = ca.get_customer_profile(customer_id)
        products = pa.get_products(profile)
        print(f"Found {len(products)} matching products for filtering.")
        
        if not products:
            print(f"No matching products found for {customer_id}")
            return
        
        recommendations = ra.recommend(profile, products)
        print(f"Generated {len(recommendations)} recommendations.")
        if recommendations:
            print(f"\nTop 3 Recommendations for {customer_id}:")
            for product, score in recommendations:
                print(f"{product['Product_ID']} - {product['Subcategory']} (${product['Price']}), Score: {score}")
        else:
            print("No recommendations generated!")

    except Exception as e:
        print(f"Error for {customer_id}: {e}")

if __name__ == "__main__":
    main()