
import sys
import os

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.baselines import BaselineCalculator

def test_baselines():
    print("Initializing BaselineCalculator...")
    # It will try to load FeatureExtractor -> SentenceTransformer, might take a moment
    calc = BaselineCalculator()
    
    cv_text = "python java software engineer machine learning"
    jd_text = "python c++ software developer deep learning"
    
    print(f"\nComparing:\nCV: {cv_text}\nJD: {jd_text}")
    
    # 1. Jaccard
    jaccard_res = calc.compute_jaccard(cv_text, jd_text)
    print("\n--- Jaccard ---")
    print(jaccard_res)
    
    # Check tokens
    # python, software (learning? software? engineer!=developer)
    extract1 = set(["python", "java", "software", "engineer", "machine", "learning"])
    extract2 = set(["python", "c", "software", "developer", "deep", "learning"])
    # intersection: python, software, learning
    
    assert jaccard_res["intersection_count"] >= 3, "Should have at least python, software, learning"
    
    # 2. Embedding
    print("\n--- Embedding ---")
    sim = calc.compute_embedding_similarity(cv_text, jd_text)
    print(f"Similarity: {sim}")
    
    if sim is not None:
        assert -1.0 <= sim <= 1.0, "Cosine sim must be in [-1, 1]"
        print("Embedding test passed.")
    else:
        print("Embedding ignored/unavailable.")

if __name__ == "__main__":
    test_baselines()
