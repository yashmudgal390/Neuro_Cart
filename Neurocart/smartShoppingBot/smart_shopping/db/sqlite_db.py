import sqlite3
import json
import pandas as pd
import os

def clean_list_field(value):
    """Convert a string like "['Books', 'Fashion']" or 'Books,Fashion' to a clean JSON list."""
    if pd.isna(value):
        return "[]"
    # Remove quotes and brackets if already a JSON-like string, then split and clean
    value = str(value).replace('"', '').replace("'", "").replace("[", "").replace("]", "").strip()
    items = [item.strip() for item in value.split(",") if item.strip()]
    return json.dumps(items)

def create_database(products_file="products.csv", customers_file="customers.csv"):
    base_dir = os.path.dirname(__file__)
    products_path = os.path.join(base_dir, products_file)
    customers_path = os.path.join(base_dir, customers_file)

    if not os.path.exists(products_path):
        raise FileNotFoundError(f"Products file not found at: {products_path}")
    if not os.path.exists(customers_path):
        raise FileNotFoundError(f"Customers file not found at: {customers_path}")

    products_df = pd.read_csv(products_path)
    customers_df = pd.read_csv(customers_path)

    # Clean and convert list fields to proper JSON
    products_df["Similar_Product_List"] = products_df["Similar_Product_List"].apply(clean_list_field)
    customers_df["Browsing_History"] = customers_df["Browsing_History"].apply(clean_list_field)
    customers_df["Purchase_History"] = customers_df["Purchase_History"].apply(clean_list_field)

    products_data = products_df.to_dict(orient='records')
    customers_data = customers_df.to_dict(orient='records')

    conn = sqlite3.connect("ecommerce.db")
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS products (
        Product_ID TEXT PRIMARY KEY, Category TEXT, Subcategory TEXT, Price REAL, Brand TEXT,
        Average_Rating_of_Similar_Products REAL, Product_Rating REAL, Customer_Review_Sentiment_Score REAL,
        Holiday TEXT, Season TEXT, Geographical_Location TEXT, Similar_Product_List TEXT,
        Probability_of_Recommendation REAL)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS customers (
        Customer_ID TEXT PRIMARY KEY, Age INTEGER, Gender TEXT, Location TEXT,
        Browsing_History TEXT, Purchase_History TEXT, Customer_Segment TEXT,
        Avg_Order_Value REAL, Holiday TEXT, Season TEXT)''')

    for product in products_data:
        cursor.execute('INSERT OR REPLACE INTO products VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                       (product["Product_ID"], product["Category"], product["Subcategory"], product["Price"],
                        product["Brand"], product["Average_Rating_of_Similar_Products"], product["Product_Rating"],
                        product["Customer_Review_Sentiment_Score"], product["Holiday"], product["Season"],
                        product["Geographical_Location"], product["Similar_Product_List"],
                        product["Probability_of_Recommendation"]))

    for customer in customers_data:
        cursor.execute('INSERT OR REPLACE INTO customers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                       (customer["Customer_ID"], customer["Age"], customer["Gender"], customer["Location"],
                        customer["Browsing_History"], customer["Purchase_History"],
                        customer["Customer_Segment"], customer["Avg_Order_Value"], customer["Holiday"],
                        customer["Season"]))

    conn.commit()
    conn.close()
    print("Database created and populated from CSV files!")

if __name__ == "__main__":
    try:
        create_database()
    except Exception as e:
        print(f"Error: {e}")