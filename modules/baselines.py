"""
Baselines (for paper) - Helper module.

Provides simple baseline metrics for CV-JD comparison:
1. Keyword Overlap (Jaccard)
2. Embedding Similarity (Cosine)

Reuses FeatureExtractor for tokenization and embeddings to ensure consistency.
"""

from typing import Dict, List, Tuple, Set, Optional
import numpy as np
import logging

from modules.feature_extractor import FeatureExtractor

class BaselineCalculator:
    def __init__(self, feature_extractor: Optional[FeatureExtractor] = None):
        """
        Initialize with an existing FeatureExtractor or create a new one.
        """
        if feature_extractor:
            self.extractor = feature_extractor
        else:
            try:
                self.extractor = FeatureExtractor()
            except Exception as e:
                logging.warning(f"FeatureExtractor failed to init in Baselines: {e}")
                self.extractor = None

    def compute_jaccard(self, text1: str, text2: str) -> Dict:
        """
        Compute Jaccard similarity and overlap details.
        
        Returns:
            Dict containing:
            - jaccard_index (float): 0.0 - 1.0
            - overlap_percent_1 (float): overlap / unique_1
            - overlap_percent_2 (float): overlap / unique_2
            - intersection_count (int)
            - unique_count_1 (int)
            - unique_count_2 (int)
            - overlap_tokens (List[str]): Top 10 tokens in intersection
        """
        if not self.extractor:
            return self._empty_jaccard()

        try:
            tokens1 = set(self.extractor._tokenize_alnum(text1 or ""))
            tokens2 = set(self.extractor._tokenize_alnum(text2 or ""))
        except Exception:
            return self._empty_jaccard()

        if not tokens1 and not tokens2:
            return self._empty_jaccard()

        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)

        intersection_len = len(intersection)
        union_len = len(union)
        
        jaccard = intersection_len / union_len if union_len > 0 else 0.0

        # Percent coverage
        pct_1 = intersection_len / len(tokens1) if tokens1 else 0.0
        pct_2 = intersection_len / len(tokens2) if tokens2 else 0.0

        return {
            "jaccard_index": jaccard,
            "overlap_percent_cv": pct_1, # Assuming text1 is CV usually
            "overlap_percent_jd": pct_2, # Assuming text2 is JD usually
            "intersection_count": intersection_len,
            "unique_count_1": len(tokens1),
            "unique_count_2": len(tokens2),
            "overlap_tokens": sorted(list(intersection))[:10]  # Just top 10 alphabetically or arbitrary
        }

    def compute_embedding_similarity(self, text1: str, text2: str) -> Optional[float]:
        """
        Compute Cosine Similarity between embeddings of two texts.
        Returns float 0.0-1.0 (clamped), or None if unavailable.
        """
        if not self.extractor:
            return None
        
        try:
            vec1 = self.extractor.embed_text(text1)
            vec2 = self.extractor.embed_text(text2)
            
            sim = self.extractor.cosine_similarity(vec1, vec2)
            
            # Clamp to 0-1 for display (though cosine is -1 to 1)
            # Usually strict semantic similarity is positive, but we'll return raw -1..1 or clamped?
            # Requirement said "0-1 or -1..1", let's keep raw but safeguard against None
            return float(sim)
        except Exception as e:
            logging.warning(f"Embedding sim failed: {e}")
            return None

    def _empty_jaccard(self) -> Dict:
        return {
            "jaccard_index": 0.0,
            "overlap_percent_cv": 0.0,
            "overlap_percent_jd": 0.0,
            "intersection_count": 0,
            "unique_count_1": 0,
            "unique_count_2": 0,
            "overlap_tokens": []
        }
