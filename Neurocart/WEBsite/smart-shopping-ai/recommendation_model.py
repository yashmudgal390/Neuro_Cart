import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
import sqlite3
import logging

# Configure logging
logger = logging.getLogger(__name__)

class RecommendationModel:
    def __init__(self):
        self.product_features = None
        self.products_df = None
        self.category_weights = {
            'Books': {
                'keywords': ['books', 'reading', 'literature', 'novel', 'story', 'education'],
                'subcategories': {
                    'Fiction': ['fiction', 'novel', 'story', 'fantasy', 'romance', 'thriller', 'mystery', 'sci-fi'],
                    'Non-Fiction': ['non-fiction', 'biography', 'self-help', 'business', 'history', 'science'],
                    'Academic': ['textbook', 'education', 'academic', 'study', 'learning', 'reference'],
                    'Children': ['children', 'kids', 'young adult', 'picture book', 'bedtime story']
                }
            },
            'Lifestyle': {
                'keywords': ['lifestyle', 'wellness', 'health', 'mindfulness', 'relaxation', 'self-care'],
                'subcategories': {
                    'Wellness': ['wellness', 'health', 'natural', 'organic', 'holistic', 'vitamins'],
                    'Home & Living': ['home', 'decor', 'furniture', 'organization', 'cleaning'],
                    'Beauty': ['beauty', 'skincare', 'cosmetics', 'personal care', 'grooming'],
                    'Hobbies': ['hobby', 'craft', 'art', 'DIY', 'creative', 'leisure']
                }
            },
            'Sports & Fitness': {
                'keywords': ['sports', 'fitness', 'workout', 'exercise', 'gym', 'training', 'athletic'],
                'subcategories': {
                    'Cardio': ['running', 'cardio', 'aerobic', 'cycling', 'swimming'],
                    'Strength': ['weights', 'strength', 'muscle', 'lifting', 'resistance'],
                    'Yoga': ['yoga', 'flexibility', 'stretching', 'meditation', 'pilates'],
                    'Team Sports': ['basketball', 'football', 'soccer', 'baseball', 'volleyball']
                }
            },
            'Electronics': {
                'keywords': ['tech', 'gadgets', 'devices', 'smart', 'electronic', 'digital', 'technology'],
                'subcategories': {
                    'Computers': ['laptop', 'desktop', 'computer', 'tablet', 'accessories'],
                    'Mobile': ['phone', 'smartphone', 'mobile', 'accessories', 'apps'],
                    'Audio': ['headphones', 'earbuds', 'speakers', 'sound', 'music'],
                    'Smart Home': ['smart home', 'automation', 'security', 'IoT']
                }
            },
            'Fashion': {
                'keywords': ['fashion', 'style', 'clothing', 'wear', 'apparel', 'outfit'],
                'subcategories': {
                    'Casual': ['casual', 'everyday', 'comfortable', 'basics', 'streetwear'],
                    'Athletic': ['athletic', 'activewear', 'sportswear', 'gym wear', 'performance'],
                    'Formal': ['formal', 'business', 'professional', 'dress', 'suits'],
                    'Accessories': ['accessories', 'bags', 'jewelry', 'watches', 'scarves']
                }
            },
            'Food & Beverage': {
                'keywords': ['food', 'drink', 'beverage', 'nutrition', 'cooking', 'kitchen'],
                'subcategories': {
                    'Health Foods': ['healthy', 'organic', 'natural', 'vegan', 'gluten-free'],
                    'Snacks': ['snacks', 'treats', 'chips', 'nuts', 'cookies'],
                    'Beverages': ['drinks', 'coffee', 'tea', 'juice', 'smoothie'],
                    'Cooking': ['ingredients', 'spices', 'cooking', 'baking', 'kitchen']
                }
            }
        }
        self.scaler = StandardScaler()
    
    def calculate_interest_score(self, product_category, product_name, product_description, user_interests):
        if not user_interests:
            return 0.5  # Default score for no interests
            
        # Convert everything to lowercase for matching
        interests_lower = [interest.lower().strip() for interest in user_interests]
        product_name_lower = product_name.lower()
        product_desc_lower = product_description.lower()
        category_lower = product_category.lower()
        
        # Initialize scores
        direct_match_score = 0
        category_score = 0
        keyword_score = 0
        
        # Get category info
        category_info = self.category_weights.get(product_category, {})
        category_keywords = [kw.lower() for kw in category_info.get('keywords', [])]
        subcategories = category_info.get('subcategories', {})
        
        # Check all categories for potential matches (cross-category recommendations)
        all_category_matches = []
        for cat, info in self.category_weights.items():
            cat_keywords = [kw.lower() for kw in info.get('keywords', [])]
            for interest in interests_lower:
                if any(kw in interest or interest in kw for kw in cat_keywords):
                    all_category_matches.append((cat, 0.6))  # Store matching category and base score
                
                # Check subcategories
                for subcat, sub_keywords in info.get('subcategories', {}).items():
                    sub_keywords = [kw.lower() for kw in sub_keywords]
                    if any(kw in interest or interest in kw for kw in sub_keywords):
                        all_category_matches.append((cat, 0.4))  # Store matching subcategory and score
        
        # Use the best category matches
        if all_category_matches:
            best_matches = sorted(all_category_matches, key=lambda x: x[1], reverse=True)[:3]
            category_score = sum(score for _, score in best_matches) / len(best_matches)
        
        for interest in interests_lower:
            # Direct matches with product name, description, or category
            if interest in product_name_lower:
                direct_match_score += 1.2  # Increased weight for product name match
            if interest in product_desc_lower:
                direct_match_score += 0.8  # Good weight for description match
            if interest in category_lower:
                direct_match_score += 1.0  # Strong weight for category match
            
            # Partial matches in name or description
            words = interest.split()
            for word in words:
                if len(word) > 3:  # Only check words longer than 3 characters
                    if word in product_name_lower:
                        keyword_score += 0.7
                    if word in product_desc_lower:
                        keyword_score += 0.4
        
        # Normalize scores
        max_direct_score = len(interests_lower) * 3  # Account for all types of direct matches
        max_category_score = 1.8  # Maximum possible from best matches
        max_keyword_score = len(interests_lower) * 1.1
        
        direct_match_score = min(direct_match_score / max_direct_score, 1.0) if max_direct_score > 0 else 0
        category_score = min(category_score / max_category_score, 1.0) if max_category_score > 0 else 0
        keyword_score = min(keyword_score / max_keyword_score, 1.0) if max_keyword_score > 0 else 0
        
        # Calculate final score with adjusted weights
        final_score = (
            direct_match_score * 0.5 +    # Direct matches are most important
            category_score * 0.3 +        # Category matches are second
            keyword_score * 0.2           # Partial matches are third
        )
        
        # Boost score if there's a very strong direct match
        if direct_match_score > 0.8:
            final_score = min(final_score * 1.2, 1.0)
        
        # Ensure minimum score of 0.1 for all products
        return max(0.1, final_score)

    def get_recommendations(self, user_interests, top_n=5):
        """Get personalized recommendations based on user interests."""
        try:
            if self.products_df is None or len(self.products_df) == 0:
                logger.error("No products available in the database")
                return []
            
            # Convert interests to list if string or dict
            if isinstance(user_interests, dict):
                interests = user_interests.get('interests', [])
                if isinstance(interests, str):
                    interests = [interest.strip() for interest in interests.split(',')]
            elif isinstance(user_interests, str):
                interests = [user_interests]
            else:
                interests = user_interests
            
            # Convert everything to lowercase for matching
            interests_lower = [interest.lower().strip() for interest in interests if interest.strip()]
            logger.info(f"Processing interests: {interests_lower}")
            
            # Calculate interest scores for each product
            self.products_df['interest_score'] = self.products_df.apply(
                lambda x: self.calculate_interest_score(
                    x['category'], 
                    x['name'], 
                    x['description'], 
                    interests_lower
                ), 
                axis=1
            )
            
            # Get primary category based on interests
            primary_category = None
            if any(book_term in ' '.join(interests_lower) for book_term in ['book', 'fiction', 'novel', 'reading', 'mystery']):
                primary_category = 'Books'
            elif any(tech_term in ' '.join(interests_lower) for tech_term in ['tech', 'gadget', 'electronic']):
                primary_category = 'Electronics'
            elif any(fashion_term in ' '.join(interests_lower) for fashion_term in ['fashion', 'clothing', 'wear', 'apparel']):
                primary_category = 'Fashion'
            
            logger.info(f"Primary category identified: {primary_category}")
            
            # Filter and sort products
            if primary_category:
                # Get products from primary category
                primary_products = self.products_df[
                    (self.products_df['category'] == primary_category)
                ].sort_values('interest_score', ascending=False)
                
                # Get complementary products from other categories
                other_products = self.products_df[
                    (self.products_df['category'] != primary_category)
                ].sort_values('interest_score', ascending=False)
                
                # Combine recommendations
                recommendations_df = pd.concat([
                    primary_products.head(4),  # Get top 4 from primary category
                    other_products.head(1)     # Get top 1 from other categories
                ])
            else:
                # If no primary category, get top products by interest score
                recommendations_df = self.products_df.sort_values('interest_score', ascending=False)
            
            # Ensure we have the right number of recommendations
            recommendations_df = recommendations_df.head(top_n)
            
            # Calculate final score combining interest score and popularity
            recommendations_df['final_score'] = (
                recommendations_df['interest_score'] * 0.7 +  # Interest match is most important
                recommendations_df['popularity'].astype(float) / 100 * 0.3  # Some weight for popularity
            )
            
            # Convert to list of dictionaries
            recommendations = []
            for _, row in recommendations_df.iterrows():
                recommendations.append({
                    'product_id': row['product_id'],
                    'name': row['name'],
                    'description': row['description'],
                    'price': float(row['price']),
                    'category': row['category'],
                    'final_score': float(row['final_score'])
                })
            
            logger.info(f"Generated {len(recommendations)} recommendations")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return []

    def load_data(self):
        """Load data from the SQLite database."""
        try:
            # Connect to database
            conn = sqlite3.connect('database/data.db')
            
            # Load products
            products_df = pd.read_sql_query("""
                SELECT product_id, name, description, price, category, 
                       popularity, stock 
                FROM product_catalog
            """, conn)
            
            # Load customer sessions (if any)
            customers_df = pd.read_sql_query("""
                SELECT * FROM customer_sessions
            """, conn)
            
            conn.close()
            return customers_df, products_df
            
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise
    
    def preprocess_product_features(self, products_df):
        """Preprocess product features for the recommendation model."""
        try:
            # Define numerical and categorical features
            numerical_features = ['price', 'popularity', 'stock']
            categorical_features = ['category']
            
            # Create a copy of the dataframe
            features_df = products_df.copy()
            
            # Handle missing values
            for col in numerical_features:
                features_df[col] = features_df[col].fillna(features_df[col].mean())
            
            # Scale numerical features
            features_df[numerical_features] = self.scaler.fit_transform(features_df[numerical_features])
            
            # One-hot encode categorical features
            features_df = pd.get_dummies(features_df, columns=categorical_features)
            
            return features_df
        
        except Exception as e:
            logger.error(f"Error preprocessing features: {e}")
            raise
    
    def calculate_similarity(self, user_interests, product_features):
        """Calculate similarity between user interests and product features."""
        try:
            # Convert interests to lowercase for matching
            interests = [interest.strip().lower() for interest in user_interests.split(',')]
            
            # Calculate scores based on category and description matches
            scores = []
            for _, product in product_features.iterrows():
                score = 0
                
                # Category match (60% weight)
                if any(interest in product['category'].lower() for interest in interests):
                    score += 0.6
                
                # Description match (40% weight)
                if any(interest in product['description'].lower() for interest in interests):
                    score += 0.4
                
                scores.append(score)
            
            return np.array(scores)
        
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            raise
    
    def train(self):
        """Train the recommendation model."""
        try:
            # Load and preprocess data
            _, products_df = self.load_data()
            
            # Store product features for later use
            self.products_df = products_df
            
            logger.info("Model trained successfully!")
            logger.info(f"Number of products: {len(products_df)}")
            logger.info(f"Product features: {len(products_df.columns)}")
            
            print("Model trained successfully!")
            print(f"Number of products: {len(products_df)}")
            print(f"Product features: {len(products_df.columns)}")
            
        except Exception as e:
            logger.error(f"Error training model: {e}")
            raise 