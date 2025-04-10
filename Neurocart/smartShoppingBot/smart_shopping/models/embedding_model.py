import ollama
import numpy as np

class EmbeddingModel:
    def __init__(self, model="tinyllama"):
        self.model = model

    def embed(self, text):
        return ollama.embeddings(model=self.model, prompt=text)["embedding"]

    def cosine_similarity(self, vec1, vec2):
        vec1, vec2 = np.array(vec1), np.array(vec2)
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

if __name__ == "__main__":
    em = EmbeddingModel()
    emb1 = em.embed("Books")
    emb2 = em.embed("Fashion")
    sim = em.cosine_similarity(emb1, emb2)
    print(f"Similarity between 'Books' and 'Fashion': {sim}")