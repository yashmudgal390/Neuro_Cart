import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.embedding_model import EmbeddingModel
from agents.customer_agent import CustomerAgent
from agents.product_agent import ProductAgent

class RecommendationAgent:
    def __init__(self):
        self.embedding_model = EmbeddingModel()

    def recommend(self, customer_profile, product_list):
        print(f"Received {len(product_list)} products to recommend from.")
        pref_text = " ".join(customer_profile["preferences"])
        print(f"Preferences text: {pref_text}")
        try:
            pref_embedding = self.embedding_model.embed(pref_text)
            print("Generated preference embedding.")
        except Exception as e:
            print(f"Error generating preference embedding: {e}")
            return []

        product_scores = []
        for i, product in enumerate(product_list):
            prod_text = f"{product['Category']} {product['Subcategory']}"
            try:
                prod_embedding = self.embedding_model.embed(prod_text)
                similarity = self.embedding_model.cosine_similarity(pref_embedding, prod_embedding)
                score = (0.4 * similarity + 
                         0.3 * product["Probability_of_Recommendation"] +
                         0.2 * product["Customer_Review_Sentiment_Score"] +
                         0.1 * (1 - abs(product["Price"] - customer_profile["budget"]) / customer_profile["budget"]))
                product_scores.append((product, score))
                if i % 1000 == 0:  # Progress update
                    print(f"Scored {i+1} products...")
            except Exception as e:
                print(f"Error scoring product {product['Product_ID']}: {e}")
                continue

        print(f"Scored {len(product_scores)} products total.")
        if not product_scores:
            print("No scores generated!")
            return []

        sorted_recs = sorted(product_scores, key=lambda x: x[1], reverse=True)
        top_3 = sorted_recs[:3]
        print(f"Returning top {len(top_3)} recommendations.")
        return top_3

if __name__ == "__main__":
    ca = CustomerAgent()
    pa = ProductAgent()
    try:
        profile = ca.get_customer_profile("C1000")
        products = pa.get_products(profile)
        ra = RecommendationAgent()
        recs = ra.recommend(profile, products)
        for product, score in recs:
            print(f"Recommended: {product['Product_ID']} - {product['Subcategory']} (${product['Price']}), Score: {score}")
    except Exception as e:
        print(f"Error: {e}")