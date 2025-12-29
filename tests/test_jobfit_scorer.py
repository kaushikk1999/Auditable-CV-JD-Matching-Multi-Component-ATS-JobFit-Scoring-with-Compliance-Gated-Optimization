import unittest
from unittest.mock import MagicMock
import numpy as np
from modules.jobfit_scorer import JobFitScorer
from modules.feature_extractor import FeatureExtractor

class TestJobFitScorer(unittest.TestCase):
    
    def setUp(self):
        # Mock FeatureExtractor
        self.mock_extractor = MagicMock(spec=FeatureExtractor)
        
        # Mock config
        self.mock_config = MagicMock()
        self.mock_config.jobfit_weights.summary_similarity = 0.2
        self.mock_config.jobfit_weights.experience_alignment = 0.2
        self.mock_config.jobfit_weights.skills_alignment = 0.2
        self.mock_config.jobfit_weights.education_match = 0.2
        self.mock_config.jobfit_weights.domain_relevance = 0.2
        
        self.mock_extractor.config = self.mock_config
        
        self.scorer = JobFitScorer(self.mock_extractor)

    def test_summary_similarity(self):
        cv_dict = {"summary": {"text": "CV Summary"}}
        jd_dict = {"role_summary": "JD Summary"}
        
        # Mock embeddings
        self.mock_extractor.embed_text.side_effect = [
            np.array([1.0, 0.0]), # CV
            np.array([0.0, 1.0])  # JD
        ]
        
        # Mock cosine similarity (orthogonal vectors = 0.0)
        self.mock_extractor.cosine_similarity.return_value = 0.0
        
        # Normalized: (0.0 + 1) / 2 = 0.5
        score = self.scorer._summary_similarity(cv_dict, jd_dict)
        self.assertEqual(score, 0.5)
        
        # Missing text
        self.assertEqual(self.scorer._summary_similarity({}, {}), 0.0)

    def test_experience_alignment(self):
        cv_dict = {"experience": [{"bullets": [{"text": "Bullet 1"}]}]}
        jd_dict = {"key_responsibilities": ["Resp 1"]}
        
        # Mock embeddings
        self.mock_extractor.embed_texts.side_effect = [
            [np.array([1.0])], # CV bullets
            [np.array([1.0])]  # JD responsibilities
        ]
        
        # Mock cosine similarity (identical = 1.0)
        self.mock_extractor.cosine_similarity.return_value = 1.0
        
        # Max sim 1.0 -> Normalized (1.0 + 1) / 2 = 1.0
        score = self.scorer._experience_alignment(cv_dict, jd_dict)
        self.assertEqual(score, 1.0)
        
        # Missing data
        self.assertEqual(self.scorer._experience_alignment({}, {}), 0.0)

    def test_skills_alignment(self):
        cv_dict = {"skills": [{"skills": ["Python", "Java"]}]}
        jd_dict = {
            "required_skills": ["Python", "C++"],
            "preferred_skills": ["Java", "Go"]
        }
        
        # Required: Python matches (1/2 = 0.5)
        # Preferred: Java matches (1/2 = 0.5)
        # Weighted: 0.7 * 0.5 + 0.3 * 0.5 = 0.5
        score = self.scorer._skills_alignment(cv_dict, jd_dict)
        self.assertAlmostEqual(score, 0.5)
        
        # No requirements
        self.assertEqual(self.scorer._skills_alignment(cv_dict, {}), 1.0)

    def test_education_match(self):
        # Bachelor vs Bachelor -> 1.0
        cv_dict = {"education": [{"degree": "Bachelor of Science"}]}
        jd_dict = {"education": "Bachelor degree required"}
        self.assertEqual(self.scorer._education_match(cv_dict, jd_dict), 1.0)
        
        # Master vs Bachelor -> 1.0
        cv_dict = {"education": [{"degree": "Master of Science"}]}
        self.assertEqual(self.scorer._education_match(cv_dict, jd_dict), 1.0)
        
        # Bachelor vs Master -> 0.5 (one level below)
        jd_dict = {"education": "Master degree required"}
        cv_dict = {"education": [{"degree": "Bachelor of Science"}]}
        self.assertEqual(self.scorer._education_match(cv_dict, jd_dict), 0.5)
        
        # Associate vs Master -> 0.0 (two levels below)
        cv_dict = {"education": [{"degree": "Associate Degree"}]}
        self.assertEqual(self.scorer._education_match(cv_dict, jd_dict), 0.0)

    def test_domain_relevance(self):
        cv_dict = {"experience": [{"job_title": "Software Engineer"}]}
        jd_dict = {"keyword_taxonomy": {"domain_knowledge": ["Software Development"]}}
        
        # Mock embeddings
        self.mock_extractor.embed_texts.return_value = [np.array([1.0])]
        self.mock_extractor.embed_text.return_value = np.array([1.0])
        
        # Mock cosine similarity
        self.mock_extractor.cosine_similarity.return_value = 1.0
        
        # Normalized: (1.0 + 1) / 2 = 1.0
        score = self.scorer._domain_relevance(cv_dict, jd_dict)
        self.assertEqual(score, 1.0)
        
        # Missing data
        self.assertEqual(self.scorer._domain_relevance({}, {}), 0.5)

    def test_score_integration(self):
        cv_dict = {}
        jd_dict = {}
        
        # Mock component methods to return known values
        self.scorer._summary_similarity = MagicMock(return_value=1.0)
        self.scorer._experience_alignment = MagicMock(return_value=1.0)
        self.scorer._skills_alignment = MagicMock(return_value=1.0)
        self.scorer._education_match = MagicMock(return_value=1.0)
        self.scorer._domain_relevance = MagicMock(return_value=1.0)
        
        # Score: 0.2*1 + 0.2*1 + 0.2*1 + 0.2*1 + 0.2*1 = 1.0
        # Scaled: 100.0
        
        result = self.scorer.score(cv_dict, jd_dict)
        
        self.assertAlmostEqual(result["jobfit_score"], 100.0)
        self.assertAlmostEqual(result["components"]["summary_similarity"], 100.0)
        self.assertIn("features", result)

if __name__ == '__main__':
    unittest.main()
