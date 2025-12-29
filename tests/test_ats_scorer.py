import unittest
from unittest.mock import MagicMock
from modules.ats_scorer import ATSScorer
from modules.feature_extractor import FeatureExtractor

class TestATSScorer(unittest.TestCase):
    
    def setUp(self):
        # Mock FeatureExtractor
        self.mock_extractor = MagicMock(spec=FeatureExtractor)
        
        # Mock config
        self.mock_config = MagicMock()
        self.mock_config.ats_weights.lexical_coverage = 0.2
        self.mock_config.ats_weights.fuzzy_coverage = 0.2
        self.mock_config.ats_weights.tfidf_relevance = 0.2
        self.mock_config.ats_weights.tfidf_cosine_similarity = 0.2
        self.mock_config.ats_weights.section_distribution = 0.2
        
        self.mock_config.normalization.tfidfcos_min = 0.0
        self.mock_config.normalization.tfidfcos_max = 10.0
        
        self.mock_extractor.config = self.mock_config
        
        self.scorer = ATSScorer(self.mock_extractor)

    def test_lexical_coverage(self):
        jd_keywords = {"python", "java", "sql"}
        cv_keywords = {"python", "c++"}
        
        # 1 match (python) out of 3 JD keywords = 1/3
        coverage = self.scorer._lexical_coverage(jd_keywords, cv_keywords)
        self.assertAlmostEqual(coverage, 1/3)
        
        # Empty JD keywords
        self.assertEqual(self.scorer._lexical_coverage(set(), cv_keywords), 0.0)

    def test_fuzzy_coverage(self):
        jd_keywords = {"python", "javascript", "kubernetes"}
        cv_keywords = {"python", "kubernets"} # Typo
        
        # Mock fuzzy matching
        # Unmatched JD: javascript, kubernetes
        # Fuzzy match: kubernetes -> kubernets
        self.mock_extractor.fuzzy_match_keywords.return_value = {
            "kubernetes": {"match": "kubernets", "score": 95}
        }
        
        # 1 fuzzy match out of 2 unmatched JD keywords = 0.5
        coverage = self.scorer._fuzzy_coverage(jd_keywords, cv_keywords)
        self.assertEqual(coverage, 0.5)
        
        # All matched exactly
        self.assertEqual(self.scorer._fuzzy_coverage({"python"}, {"python"}), 1.0)

    def test_tfidf_relevance(self):
        jd_text = "python java"
        cv_text = "python"
        jd_keywords = {"python", "java"}
        cv_keywords = {"python"}
        
        # Mock TF-IDF weights
        self.mock_extractor.compute_tfidf_weights.return_value = {
            "python": 0.6,
            "java": 0.4
        }
        
        # Matched: python (0.6)
        # Total: 0.6 + 0.4 = 1.0
        # Relevance: 0.6 / 1.0 = 0.6
        relevance = self.scorer._tfidf_relevance(jd_text, cv_text, jd_keywords, cv_keywords)
        self.assertAlmostEqual(relevance, 0.6)
        
        # Total weight 0
        self.mock_extractor.compute_tfidf_weights.return_value = {}
        self.assertEqual(self.scorer._tfidf_relevance(jd_text, cv_text, jd_keywords, cv_keywords), 0.0)

    def test_tfidf_cosine_similarity(self):
        jd_text = "doc1"
        cv_text = "doc2"
        
        # Mock TF-IDF Cosine score
        self.mock_extractor.compute_tfidf_cosine_similarity.return_value = 5.0
        
        # Min 0.0, Max 10.0 -> (5.0 - 0.0) / (10.0 - 0.0) = 0.5
        similarity = self.scorer._tfidf_cosine_similarity(jd_text, cv_text)
        self.assertEqual(similarity, 0.5)
        
        # Clipping
        self.mock_extractor.compute_tfidf_cosine_similarity.return_value = 15.0
        self.assertEqual(self.scorer._tfidf_cosine_similarity(jd_text, cv_text), 1.0)
        
        self.mock_extractor.compute_tfidf_cosine_similarity.return_value = -5.0
        self.assertEqual(self.scorer._tfidf_cosine_similarity(jd_text, cv_text), 0.0)

    def test_section_distribution(self):
        cv_keywords = {
            "summary": {"a", "b"},
            "skills": {"c", "d"},
            "experience": {"e", "f"}
        }
        # Counts: 2, 2, 2. Total 6. Probs: 1/3, 1/3, 1/3.
        # Entropy: -3 * (1/3 * log2(1/3)) = -log2(1/3) = log2(3)
        # Max entropy: log2(3)
        # Normalized: 1.0
        # Need JD keywords that match all CV keywords to get counts 2, 2, 2
        jd_keywords = {"a", "b", "c", "d", "e", "f"}
        entropy = self.scorer._section_distribution(jd_keywords, cv_keywords)
        self.assertAlmostEqual(entropy, 1.0)
        
        # Empty
        self.assertEqual(self.scorer._section_distribution(set(), {}), 0.0)

    def test_score_integration(self):
        cv_dict = {}
        jd_dict = {}
        cv_text = ""
        jd_text = ""
        
        # Mock extractor outputs
        self.mock_extractor.extract_cv_keywords.return_value = {
            "summary": set(), "skills": set(), "experience": set(), "all": {"python"}
        }
        self.mock_extractor.extract_jd_keywords.return_value = {
            "required": set(), "preferred": set(), "all": {"python"}
        }
        self.mock_extractor.fuzzy_match_keywords.return_value = {}
        self.mock_extractor.compute_tfidf_weights.return_value = {"python": 1.0}
        self.mock_extractor.compute_tfidf_weights.return_value = {"python": 1.0}
        self.mock_extractor.compute_tfidf_cosine_similarity.return_value = 10.0
        
        # Expected components:
        # Lexical: 1.0 (1/1)
        # Fuzzy: 1.0 (all matched)
        # TF-IDF: 1.0 (1.0/1.0)
        # TF-IDF Cosine: 1.0 (10.0 normalized to 1.0)
        # Section: 0.0 (empty sections)
        
        # Score: 0.2*1 + 0.2*1 + 0.2*1 + 0.2*1 + 0.2*0 = 0.8
        # Scaled: 80.0
        
        result = self.scorer.score(cv_dict, jd_dict, cv_text, jd_text)
        
        self.assertAlmostEqual(result["ats_score"], 80.0)
        self.assertAlmostEqual(result["components"]["lexical_coverage"], 100.0)
        self.assertAlmostEqual(result["components"]["section_distribution"], 0.0)
        self.assertIn("features", result)

if __name__ == '__main__':
    unittest.main()
