import sqlite3
import random

# Sample products with meaningful descriptions
sample_products = [
    # Books
    ("Books", "The Art of Mindful Living", "A comprehensive guide to mindfulness and meditation, perfect for beginners seeking inner peace and stress reduction.", 24.99, 85, 50),
    ("Books", "Python Programming Masterclass", "Advanced programming concepts and practical examples for building modern applications. Includes AI and machine learning topics.", 49.99, 92, 30),
    ("Books", "The Fantasy Chronicles", "Epic fantasy novel series with rich world-building and compelling characters. Perfect for fantasy and adventure lovers.", 19.99, 88, 75),
    ("Books", "Healthy Cooking Made Simple", "200+ nutritious recipes with step-by-step instructions. Focus on whole foods and balanced nutrition.", 34.99, 90, 45),
    
    # Lifestyle
    ("Lifestyle", "Zen Meditation Cushion Set", "Premium meditation cushion with matching mat, designed for comfort during long meditation sessions.", 79.99, 87, 25),
    ("Lifestyle", "Aromatherapy Essential Oils Kit", "Collection of 12 pure essential oils for relaxation and wellness. Includes lavender, eucalyptus, and peppermint.", 45.99, 93, 40),
    ("Lifestyle", "Natural Skincare Collection", "Organic skincare set with cleanser, toner, and moisturizer. Made with natural ingredients.", 89.99, 91, 30),
    ("Lifestyle", "Home Organization System", "Complete home organization solution with modular components. Perfect for decluttering.", 129.99, 86, 20),
    
    # Sports & Fitness
    ("Sports & Fitness", "Premium Yoga Mat Bundle", "Extra-thick eco-friendly yoga mat with alignment lines. Includes carrying strap and blocks.", 69.99, 94, 35),
    ("Sports & Fitness", "Smart Fitness Tracker", "Advanced fitness tracking with heart rate monitoring, sleep analysis, and workout guidance.", 149.99, 95, 50),
    ("Sports & Fitness", "Adjustable Dumbbell Set", "Space-saving adjustable dumbbells from 5-52.5 lbs. Perfect for home workouts.", 299.99, 89, 15),
    ("Sports & Fitness", "Professional Running Shoes", "Lightweight running shoes with advanced cushioning and support. Ideal for marathon training.", 129.99, 92, 40),
    
    # Electronics
    ("Electronics", "Noise-Cancelling Headphones", "Premium wireless headphones with active noise cancellation and 30-hour battery life.", 249.99, 96, 30),
    ("Electronics", "Smart Home Hub", "Central control for all your smart home devices. Voice-controlled with AI assistance.", 179.99, 88, 25),
    ("Electronics", "4K Streaming Media Player", "Stream your favorite content in 4K HDR. Includes voice remote and gaming capabilities.", 89.99, 91, 45),
    ("Electronics", "Portable Power Bank", "20000mAh high-capacity power bank with fast charging. Charges multiple devices simultaneously.", 49.99, 87, 60),
    
    # Fashion
    ("Fashion", "Athleisure Comfort Set", "Matching set of moisture-wicking, breathable athletic wear. Perfect for gym or casual wear.", 89.99, 90, 40),
    ("Fashion", "Sustainable Cotton Collection", "Eco-friendly clothing made from organic cotton. Includes basic tees and loungewear.", 59.99, 89, 50),
    ("Fashion", "Active Performance Jacket", "Lightweight, water-resistant jacket for outdoor activities. Available in multiple colors.", 129.99, 88, 35),
    ("Fashion", "Compression Fitness Wear", "High-performance compression gear for improved muscle support and recovery.", 79.99, 92, 45),
    
    # Food & Beverage
    ("Food & Beverage", "Organic Superfood Blend", "Premium blend of organic superfoods including spirulina, chia seeds, and goji berries.", 39.99, 93, 55),
    ("Food & Beverage", "Gourmet Tea Collection", "Selection of premium loose-leaf teas from around the world. Includes brewing accessories.", 49.99, 91, 40),
    ("Food & Beverage", "Healthy Snack Box", "Curated selection of nutritious snacks. All natural, no artificial ingredients.", 34.99, 89, 65),
    ("Food & Beverage", "Protein Smoothie Kit", "Complete smoothie kit with protein powder, superfoods, and recipe guide.", 59.99, 90, 50)
]

def insert_sample_data():
    try:
        # Connect to database
        conn = sqlite3.connect('database/data.db')
        cursor = conn.cursor()
        
        # Clear existing products
        cursor.execute('DELETE FROM product_catalog')
        
        # Insert new products
        for product in sample_products:
            cursor.execute('''
                INSERT INTO product_catalog 
                (category, name, description, price, popularity, stock)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', product)
        
        conn.commit()
        print(f"Successfully inserted {len(sample_products)} products")
        
    except Exception as e:
        print(f"Error inserting sample data: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    insert_sample_data() 