"""Unit tests for batch_processor module."""

import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
from modules.batch_processor import BatchProcessor
from modules.schemas import StructuredCV, EnhancedJD, AnalysisReport, GapAnalysisResult, ExperienceAlignment, KeywordMatch
from modules.experiment_tracker import ExperimentTracker

class TestBatchProcessor(unittest.TestCase):
    """Test cases for BatchProcessor."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_tracker = MagicMock(spec=ExperimentTracker)
        self.processor = BatchProcessor(tracker=self.mock_tracker)
        
        # Mock internal components to isolate BatchProcessor logic
        self.processor.analyzer = MagicMock()
        self.processor.aligner = MagicMock()
        self.processor.redactor = MagicMock()
        
        # Create dummy data
        self.cv = MagicMock(spec=StructuredCV)
        self.jd = MagicMock(spec=EnhancedJD)
        
        # Mock gap analysis result
        self.gap_analysis = MagicMock(spec=GapAnalysisResult)
        self.gap_analysis.coverage_stats = {
            "overall_coverage": 0.5,
            "required_coverage": 0.6,
            "preferred_coverage": 0.4,
            "required_present": 6,
            "required_total": 10
        }
        self.gap_analysis.present_keywords = [MagicMock(spec=KeywordMatch)] * 5
        self.gap_analysis.missing_keywords = [
            MagicMock(spec=KeywordMatch, keyword="missing_req", jd_priority="required"),
            MagicMock(spec=KeywordMatch, keyword="missing_opt", jd_priority="optional")
        ]
        self.gap_analysis.irrelevant_keywords = ["irrelevant1"]
        
        # Mock alignments
        self.alignments = [
            MagicMock(spec=ExperienceAlignment, relevance_score=0.8),
            MagicMock(spec=ExperienceAlignment, relevance_score=0.2)
        ]
        
        # Configure mocks
        self.processor.analyzer.analyze.return_value = self.gap_analysis
        self.processor.analyzer.build_coverage_table.return_value = []
        self.processor.aligner.align.return_value = self.alignments

    def test_process_pair(self):
        """Test processing a single pair."""
        report = self.processor.process_pair(
            cv=self.cv,
            jd=self.jd,
            cv_filename="cv.pdf",
            jd_filename="jd.txt"
        )
        
        # Verify report structure
        self.assertIsInstance(report, AnalysisReport)
        self.assertEqual(report.cv_filename, "cv.pdf")
        self.assertEqual(report.jd_filename, "jd.txt")
        self.assertEqual(report.gap_analysis, self.gap_analysis)
        
        # Verify interactions
        self.processor.analyzer.analyze.assert_called_once_with(self.cv, self.jd)
        self.processor.aligner.align.assert_called_once()
        self.mock_tracker.log_analysis.assert_called_once()
    
    def test_process_batch(self):
        """Test processing a batch of pairs."""
        pairs = [
            {"cv": self.cv, "jd": self.jd, "cv_file": "cv1.pdf", "jd_file": "jd1.txt"},
            {"cv": self.cv, "jd": self.jd, "cv_file": "cv2.pdf", "jd_file": "jd2.txt"}
        ]
        
        df = self.processor.process_batch(pairs)
        
        # Verify DataFrame
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 2)
        self.assertEqual(list(df.columns), [
            "run_id", "cv_file", "jd_file", 
            "overall_coverage", "required_coverage", "preferred_coverage",
            "keywords_present", "keywords_missing", "top_experience_relevance"
        ])
        
        # Verify values
        self.assertEqual(df.iloc[0]["cv_file"], "cv1.pdf")
        self.assertEqual(df.iloc[1]["cv_file"], "cv2.pdf")
        self.assertEqual(df.iloc[0]["required_coverage"], 0.6)
    
    def test_recommendations_generation(self):
        """Test recommendation logic."""
        # Case 1: Low coverage
        self.gap_analysis.coverage_stats["required_coverage"] = 0.5
        recs = self.processor._generate_recommendations(
            self.gap_analysis, self.alignments, []
        )
        self.assertTrue(any("Critical" in r for r in recs))
        
        # Case 2: High priority missing keywords
        self.assertTrue(any("Add these high-priority keywords" in r for r in recs))
        
        # Case 3: Low relevance experience
        self.assertTrue(any("low relevance" in r for r in recs))
        
        # Case 4: Irrelevant keywords
        self.gap_analysis.irrelevant_keywords = ["irr"] * 15
        recs = self.processor._generate_recommendations(
            self.gap_analysis, self.alignments, []
        )
        self.assertTrue(any("not relevant" in r for r in recs))

if __name__ == "__main__":
    unittest.main()
