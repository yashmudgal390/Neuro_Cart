import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_sample_events():
    # Connect to database
    conn = sqlite3.connect('database/data.db')
    
    # Get customer IDs
    customers_df = pd.read_sql_query("""
        SELECT customer_id FROM customer_sessions
    """, conn)
    
    # Get product IDs
    products_df = pd.read_sql_query("""
        SELECT product_id, category FROM product_catalog
    """, conn)
    
    # Generate events
    events = []
    event_types = ['view', 'click', 'cart', 'purchase']
    event_weights = [0.5, 0.3, 0.15, 0.05]  # Probabilities for each event type
    
    # Generate events for each customer
    for customer_id in customers_df['customer_id']:
        # Random number of events per customer (5-20)
        n_events = random.randint(5, 20)
        
        # Random products for this customer
        customer_products = products_df.sample(n=min(n_events, len(products_df)))
        
        # Generate events
        for _, product in customer_products.iterrows():
            # Random event type based on weights
            event_type = random.choices(event_types, weights=event_weights)[0]
            
            # Random dwell time (10-300 seconds)
            dwell_time = random.randint(10, 300)
            
            events.append({
                'customer_id': customer_id,
                'product_id': product['product_id'],
                'category': product['category'],
                'event_type': event_type,
                'dwell_time': dwell_time
            })
    
    # Convert to DataFrame
    events_df = pd.DataFrame(events)
    
    # Insert into database
    events_df.to_sql('event_logs', conn, if_exists='append', index=False)
    
    print(f"Generated {len(events)} sample events")
    conn.close()

if __name__ == '__main__':
    generate_sample_events() 