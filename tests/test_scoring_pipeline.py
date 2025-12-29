import unittest
from unittest.mock import MagicMock, patch
from modules.scoring_pipeline import ScoringPipeline
from modules.feature_extractor import FeatureExtractor
from modules.ats_scorer import ATSScorer
from modules.jobfit_scorer import JobFitScorer

class TestScoringPipeline(unittest.TestCase):
    
    def setUp(self):
        # Mock FeatureExtractor
        self.mock_extractor = MagicMock(spec=FeatureExtractor)
        
        # Mock config
        self.mock_config = MagicMock()
        self.mock_config.score_bands = {
            "poor": [0, 50],
            "medium": [50, 75],
            "strong": [75, 90],
            "excellent": [90, 100]
        }
        self.mock_extractor.config = self.mock_config
        
        # Patch init to inject mocks
        with patch('modules.scoring_pipeline.FeatureExtractor', return_value=self.mock_extractor), \
             patch('modules.scoring_pipeline.ATSScorer') as MockATSScorer, \
             patch('modules.scoring_pipeline.JobFitScorer') as MockJobFitScorer:
            
            self.mock_ats_scorer = MockATSScorer.return_value
            self.mock_jobfit_scorer = MockJobFitScorer.return_value
            
            self.pipeline = ScoringPipeline()
            
            # Ensure pipeline uses our mocks
            self.pipeline.feature_extractor = self.mock_extractor
            self.pipeline.ats_scorer = self.mock_ats_scorer
            self.pipeline.jobfit_scorer = self.mock_jobfit_scorer

    def test_score_cv_jd_pair(self):
        cv_structured = {}
        jd_enhanced = {}
        cv_raw = ""
        jd_raw = ""
        
        # Mock scorer outputs
        self.mock_ats_scorer.score.return_value = {
            "ats_score": 85.0,
            "components": {"c1": 85.0},
            "features": {"f1": 1}
        }
        
        self.mock_jobfit_scorer.score.return_value = {
            "jobfit_score": 45.0,
            "components": {"c2": 45.0},
            "features": {"f2": 1}
        }
        
        report = self.pipeline.score_cv_jd_pair(cv_structured, jd_enhanced, cv_raw, jd_raw)
        
        # Verify structure
        self.assertIn("timestamp", report)
        self.assertEqual(report["ats_score"], 85.0)
        self.assertEqual(report["jobfit_score"], 45.0)
        self.assertEqual(report["ats_components"], {"c1": 85.0})
        self.assertEqual(report["jobfit_components"], {"c2": 45.0})
        
        # Verify interpretation
        interpretation = report["interpretation"]
        self.assertEqual(interpretation["ats_band"], "Strong")
        self.assertEqual(interpretation["jobfit_band"], "Poor")
        self.assertEqual(len(interpretation["feedback"]), 2)
        self.assertIn("ATS Score is strong", interpretation["feedback"][0])
        self.assertIn("Job-Compatibility is low", interpretation["feedback"][1])

    def test_interpret_scores_boundary(self):
        # Test boundary conditions
        
        # 50 -> medium (inclusive start)
        interp = self.pipeline._interpret_scores(50.0, 50.0)
        self.assertEqual(interp["ats_band"], "Medium")
        
        # 74.9 -> medium
        interp = self.pipeline._interpret_scores(74.9, 74.9)
        self.assertEqual(interp["ats_band"], "Medium")
        
        # 75 -> strong
        interp = self.pipeline._interpret_scores(75.0, 75.0)
        self.assertEqual(interp["ats_band"], "Strong")
        
        # 90 -> excellent
        interp = self.pipeline._interpret_scores(90.0, 90.0)
        self.assertEqual(interp["ats_band"], "Excellent")
        
        # 100 -> excellent (default fallback)
        interp = self.pipeline._interpret_scores(100.0, 100.0)
        self.assertEqual(interp["ats_band"], "Excellent")

if __name__ == '__main__':
    unittest.main()
