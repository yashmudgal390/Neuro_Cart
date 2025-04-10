import sqlite3
import random
from faker import Faker
import json
from datetime import datetime, timedelta
import uuid
import os
from pathlib import Path

fake = Faker()

# Categories and their properties
CATEGORIES = {
    'Books': {
        'min_price': 9.99,
        'max_price': 49.99,
        'descriptions': [
            'A captivating {genre} that will keep you engaged',
            'Bestselling {genre} from acclaimed author',
            'Award-winning {genre} exploring {theme}',
            'Must-read {genre} for {audience}'
        ],
        'genres': ['novel', 'mystery', 'thriller', 'romance', 'sci-fi', 'fantasy', 'biography', 'self-help'],
        'themes': ['love', 'adventure', 'mystery', 'personal growth', 'success', 'relationships'],
        'audience': ['young adults', 'professionals', 'students', 'book lovers', 'enthusiasts']
    },
    'Electronics': {
        'min_price': 29.99,
        'max_price': 999.99,
        'descriptions': [
            'High-quality {type} with advanced features',
            'Premium {type} for optimal performance',
            'Next-generation {type} with {feature}',
            'Professional-grade {type} for {usage}'
        ],
        'types': ['headphones', 'smartwatch', 'tablet', 'laptop', 'camera', 'speaker'],
        'features': ['wireless connectivity', 'long battery life', 'HD display', 'noise cancellation'],
        'usage': ['work', 'entertainment', 'gaming', 'content creation']
    },
    'Fashion': {
        'min_price': 19.99,
        'max_price': 199.99,
        'descriptions': [
            'Stylish {item} perfect for {occasion}',
            'Trendy {item} with {material} material',
            'Comfortable {item} for everyday wear',
            'Designer {item} in {color}'
        ],
        'items': ['shirt', 'jeans', 'dress', 'jacket', 'sweater', 'shoes'],
        'occasions': ['casual wear', 'office', 'special events', 'outdoor activities'],
        'materials': ['cotton', 'leather', 'denim', 'silk', 'wool'],
        'colors': ['black', 'navy', 'white', 'gray', 'brown']
    }
}

def create_database():
    # Ensure database directory exists
    db_dir = Path('database')
    db_dir.mkdir(exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect('database/data.db')
    cursor = conn.cursor()
    
    # Read and execute schema
    with open('database/schema.sql', 'r') as f:
        schema = f.read()
        cursor.executescript(schema)
    
    conn.commit()
    conn.close()
    print("Database and tables created successfully!")

def generate_product(category, product_number):
    category_data = CATEGORIES[category]
    
    if category == 'Books':
        genre = random.choice(category_data['genres'])
        theme = random.choice(category_data['themes'])
        audience = random.choice(category_data['audience'])
        desc_template = random.choice(category_data['descriptions'])
        description = desc_template.format(genre=genre, theme=theme, audience=audience)
        name = f"The {fake.word().title()} {genre.title()}"
    
    elif category == 'Electronics':
        type_ = random.choice(category_data['types'])
        feature = random.choice(category_data['features'])
        usage = random.choice(category_data['usage'])
        desc_template = random.choice(category_data['descriptions'])
        description = desc_template.format(type=type_, feature=feature, usage=usage)
        name = f"{fake.company()} {type_.title()}"
    
    else:  # Fashion
        item = random.choice(category_data['items'])
        occasion = random.choice(category_data['occasions'])
        material = random.choice(category_data['materials'])
        color = random.choice(category_data['colors'])
        desc_template = random.choice(category_data['descriptions'])
        description = desc_template.format(item=item, occasion=occasion, material=material, color=color)
        name = f"{color.title()} {material.title()} {item.title()}"
    
    return {
        'product_id': f"P{category[0]}{product_number:05d}",  # Ensures unique IDs like PB00001, PE00002, etc.
        'name': name,
        'description': description,
        'price': round(random.uniform(category_data['min_price'], category_data['max_price']), 2),
        'category': category,
        'popularity': random.randint(1, 100),
        'stock': random.randint(0, 1000)
    }

def generate_customer():
    interests = []
    for category in CATEGORIES.keys():
        if random.random() < 0.3:  # 30% chance to be interested in each category
            interests.append(category.lower())
    
    return {
        'customer_id': str(uuid.uuid4())[:8],
        'age': random.randint(18, 70),
        'gender': random.choice(['Male', 'Female', 'Other']),
        'location': fake.city(),
        'interests': json.dumps(interests),
        'registration_date': fake.date_between(start_date='-1y', end_date='today').strftime('%Y-%m-%d'),
        'last_active': fake.date_between(start_date='-1m', end_date='today').strftime('%Y-%m-%d')
    }

def generate_event(customer_id, product_id):
    event_types = ['view', 'click', 'add_to_cart', 'purchase']
    weights = [0.4, 0.3, 0.2, 0.1]  # Probability distribution
    
    return {
        'interaction_id': str(uuid.uuid4()),
        'customer_id': customer_id,
        'product_id': product_id,
        'event_type': random.choices(event_types, weights=weights)[0],
        'timestamp': fake.date_time_between(start_date='-6m', end_date='now').strftime('%Y-%m-%d %H:%M:%S'),
        'dwell_time': random.randint(5, 300)  # 5 seconds to 5 minutes
    }

def main():
    try:
        # Create database and tables
        create_database()
        
        # Connect to database
        conn = sqlite3.connect('database/data.db')
        cursor = conn.cursor()
        
        # Clear existing data
        tables = ['product_catalog', 'customer_sessions', 'event_logs', 'customer_segments']
        for table in tables:
            cursor.execute(f"DELETE FROM {table}")
        
        # Generate 500 products (distributed across categories)
        products = []
        product_number = 1
        for _ in range(500):
            category = random.choice(list(CATEGORIES.keys()))
            products.append(generate_product(category, product_number))
            product_number += 1
        
        # Generate 500 customers
        customers = [generate_customer() for _ in range(500)]
        
        # Generate events (multiple events per customer)
        events = []
        for customer in customers:
            # Generate 1-10 events per customer
            num_events = random.randint(1, 10)
            for _ in range(num_events):
                product = random.choice(products)
                events.append(generate_event(customer['customer_id'], product['product_id']))
        
        # Insert products
        cursor.executemany("""
            INSERT INTO product_catalog 
            (product_id, name, description, price, category, popularity, stock)
            VALUES (:product_id, :name, :description, :price, :category, :popularity, :stock)
        """, products)
        
        # Insert customers
        cursor.executemany("""
            INSERT INTO customer_sessions 
            (customer_id, age, gender, location, interests, registration_date, last_active)
            VALUES (:customer_id, :age, :gender, :location, :interests, :registration_date, :last_active)
        """, customers)
        
        # Insert events
        cursor.executemany("""
            INSERT INTO event_logs 
            (interaction_id, customer_id, product_id, event_type, timestamp, dwell_time)
            VALUES (:interaction_id, :customer_id, :product_id, :event_type, :timestamp, :dwell_time)
        """, events)
        
        # Generate segments based on customer behavior
        for customer in customers:
            segment_score = random.random()  # Random score between 0 and 1
            
            if segment_score > 0.8:
                segment = 'premium'
            elif segment_score > 0.5:
                segment = 'regular'
            else:
                segment = 'new_user'
                
            cursor.execute("""
                INSERT INTO customer_segments (customer_id, segment_tag, score)
                VALUES (?, ?, ?)
            """, (customer['customer_id'], segment, segment_score))
        
        conn.commit()
        conn.close()
        
        print(f"Successfully generated:")
        print(f"- {len(products)} products")
        print(f"- {len(customers)} customers")
        print(f"- {len(events)} events")
        
    except Exception as e:
        print(f"Error generating sample data: {e}")
        raise

if __name__ == '__main__':
    main() 