import sqlite3
import json
import os

class CustomerAgent:
    def __init__(self, db_path=os.path.join(os.path.dirname(__file__), '..', 'db', 'ecommerce.db')):
        self.db_path = os.path.abspath(db_path)
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database file not found at: {self.db_path}")

    def get_customer_profile(self, customer_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM customers WHERE Customer_ID = ?", (customer_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            raise ValueError(f"Customer {customer_id} not found!")
        
        columns = ["Customer_ID", "Age", "Gender", "Location", "Browsing_History", 
                   "Purchase_History", "Customer_Segment", "Avg_Order_Value", "Holiday", "Season"]
        customer = dict(zip(columns, row))
        customer["Browsing_History"] = json.loads(customer["Browsing_History"])
        customer["Purchase_History"] = json.loads(customer["Purchase_History"])

        preferences = list(set(customer["Browsing_History"] + customer["Purchase_History"]))
        profile = {
            "customer_id": customer["Customer_ID"],
            "preferences": preferences,
            "budget": customer["Avg_Order_Value"],
            "season": customer["Season"],
            "holiday": customer["Holiday"] == "Yes",
            "location": customer["Location"]
        }
        return profile

if __name__ == "__main__":
    agent = CustomerAgent()
    try:
        profile = agent.get_customer_profile("C1000")
        print("Customer Profile:", profile)
    except Exception as e:
        print(f"Error: {e}")