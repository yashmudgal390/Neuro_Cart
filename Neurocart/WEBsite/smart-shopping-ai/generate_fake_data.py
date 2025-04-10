import sqlite3
from faker import Faker
import random
from datetime import datetime, timedelta
import json

fake = Faker()

def generate_fake_users(num_users=100):
    users = []
    interests = ['sports', 'fitness', 'yoga', 'fashion', 'electronics', 'outdoor', 
                'wellness', 'nutrition', 'adventure', 'lifestyle', 'tech', 'running']
    
    for _ in range(num_users):
        user = {
            'customer_id': fake.uuid4()[:8],
            'age': random.randint(18, 70),
            'gender': random.choice(['M', 'F']),
            'location': fake.city(),
            'interests': json.dumps(random.sample(interests, random.randint(2, 5))),
            'registration_date': fake.date_between(start_date='-1y', end_date='today').strftime('%Y-%m-%d'),
            'last_active': fake.date_between(start_date='-1m', end_date='today').strftime('%Y-%m-%d')
        }
        users.append(user)
    return users

def generate_fake_products(num_products=50):
    categories = {
        'Sports & Fitness': ['Premium Yoga Mat', 'Resistance Bands Set', 'Adjustable Dumbbells', 
                            'Exercise Ball', 'Jump Rope', 'Weight Bench', 'Kettlebell Set'],
        'Fashion': ['Athletic Leggings', 'Sports Bra', 'Running Shoes', 'Workout Tank Top', 
                   'Compression Socks', 'Training Shorts', 'Gym Bag'],
        'Electronics': ['Fitness Tracker', 'Wireless Earbuds', 'Smart Watch', 'Heart Rate Monitor', 
                       'Bluetooth Speaker', 'Smart Scale'],
        'Outdoor': ['Hiking Backpack', 'Water Bottle', 'Camping Tent', 'Trekking Poles', 
                   'Sleeping Bag', 'Outdoor GPS'],
        'Nutrition': ['Protein Powder', 'Pre-workout Supplement', 'Vitamin Complex', 
                     'Energy Bars', 'BCAA Powder', 'Meal Replacement Shake']
    }
    
    products = []
    for _ in range(num_products):
        category = random.choice(list(categories.keys()))
        product_type = random.choice(categories[category])
        brand = fake.company()
        
        product = {
            'product_id': f'P{fake.unique.random_number(5)}',
            'name': f'{brand} {product_type}',
            'description': fake.text(max_nb_chars=200),
            'price': round(random.uniform(19.99, 299.99), 2),
            'category': category,
            'popularity': random.randint(60, 100),
            'stock': random.randint(0, 500)
        }
        products.append(product)
    return products

def generate_fake_interactions(users, products, num_interactions=1000):
    interactions = []
    for _ in range(num_interactions):
        user = random.choice(users)
        product = random.choice(products)
        timestamp = fake.date_time_between(start_date='-6M', end_date='now')
        
        interaction = {
            'interaction_id': fake.uuid4(),
            'customer_id': user['customer_id'],
            'product_id': product['product_id'],
            'event_type': random.choice(['view', 'cart', 'purchase']),
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'dwell_time': random.randint(5, 300)
        }
        interactions.append(interaction)
    return interactions

def insert_fake_data():
    conn = sqlite3.connect('database/data.db')
    cursor = conn.cursor()
    
    # Generate fake data
    users = generate_fake_users()
    products = generate_fake_products()
    interactions = generate_fake_interactions(users, products)
    
    # Clear existing data
    cursor.execute("DELETE FROM customer_sessions")
    cursor.execute("DELETE FROM product_catalog")
    cursor.execute("DELETE FROM event_logs")
    
    # Insert users
    cursor.executemany("""
        INSERT INTO customer_sessions 
        (customer_id, age, gender, location, interests, registration_date, last_active)
        VALUES (:customer_id, :age, :gender, :location, :interests, :registration_date, :last_active)
    """, users)
    
    # Insert products
    cursor.executemany("""
        INSERT INTO product_catalog 
        (product_id, name, description, price, category, popularity, stock)
        VALUES (:product_id, :name, :description, :price, :category, :popularity, :stock)
    """, products)
    
    # Insert interactions
    cursor.executemany("""
        INSERT INTO event_logs 
        (interaction_id, customer_id, product_id, event_type, timestamp, dwell_time)
        VALUES (:interaction_id, :customer_id, :product_id, :event_type, :timestamp, :dwell_time)
    """, interactions)
    
    conn.commit()
    conn.close()
    
    print(f"Successfully generated and inserted:")
    print(f"- {len(users)} users")
    print(f"- {len(products)} products")
    print(f"- {len(interactions)} interactions")

if __name__ == "__main__":
    insert_fake_data() 