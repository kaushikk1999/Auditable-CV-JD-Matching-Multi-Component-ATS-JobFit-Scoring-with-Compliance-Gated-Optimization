"""Unit tests for experiment_tracker module."""

import unittest
import tempfile
import shutil
from pathlib import Path
import json
from modules.experiment_tracker import ExperimentTracker
from modules.schemas import RunConfig, RunMetrics, AnalysisReport, GapAnalysisResult, ExperienceAlignment, KeywordCoverageTable


class TestExperimentTracker(unittest.TestCase):
    """Test cases for ExperimentTracker."""
    
    def setUp(self):
        """Set up test fixtures with temporary directory."""
        # Create temporary directory for experiments
        self.temp_dir = Path(tempfile.mkdtemp())
        self.tracker = ExperimentTracker(experiments_dir=self.temp_dir)
    
    def tearDown(self):
        """Clean up temporary directory."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test ExperimentTracker initialization."""
        self.assertTrue(self.tracker.experiments_dir.exists())
        self.assertEqual(self.tracker.experiments_dir, self.temp_dir)
    
    def test_start_run_creates_directory(self):
        """Test that start_run creates run directory and config."""
        run_id = self.tracker.start_run(
            cv_file="test_cv.pdf",
            jd_file="test_jd.txt",
            parameters={"param1": "value1"}
        )
        
        # Verify run_id is a valid UUID string
        self.assertIsInstance(run_id, str)
        self.assertEqual(len(run_id), 36)  # UUID format
        
        # Verify run directory exists
        run_dir = self.tracker.experiments_dir / run_id
        self.assertTrue(run_dir.exists())
        self.assertTrue(run_dir.is_dir())
    
    def test_start_run_creates_config_file(self):
        """Test that start_run creates config.json."""
        run_id = self.tracker.start_run(
            cv_file="cv.pdf",
            jd_file="jd.txt",
            parameters={"fuzzy_threshold": 0.8}
        )
        
        # Verify config.json exists
        config_path = self.tracker.experiments_dir / run_id / "config.json"
        self.assertTrue(config_path.exists())
        
        # Verify config content
        config_data = json.loads(config_path.read_text())
        self.assertEqual(config_data["run_id"], run_id)
        self.assertEqual(config_data["cv_file"], "cv.pdf")
        self.assertEqual(config_data["jd_file"], "jd.txt")
        self.assertEqual(config_data["parameters"]["fuzzy_threshold"], 0.8)
        self.assertIn("timestamp", config_data)
    
    def test_start_run_with_no_parameters(self):
        """Test start_run with no parameters dictionary."""
        run_id = self.tracker.start_run(
            cv_file="cv.pdf",
            jd_file="jd.txt"
        )
        
        config_path = self.tracker.experiments_dir / run_id / "config.json"
        config_data = json.loads(config_path.read_text())
        self.assertEqual(config_data["parameters"], {})
    
    def test_log_analysis(self):
        """Test logging analysis report."""
        run_id = self.tracker.start_run("cv.pdf", "jd.txt")
        
        # Create minimal analysis report
        analysis_report = AnalysisReport(
            run_id=run_id,
            timestamp="2025-11-24T21:00:00",
            cv_filename="cv.pdf",
            jd_filename="jd.txt",
            gap_analysis=GapAnalysisResult(),
            experience_alignments=[],
            keyword_coverage_table=[]
        )
        
        self.tracker.log_analysis(run_id, analysis_report)
        
        # Verify analysis_report.json exists
        report_path = self.tracker.experiments_dir / run_id / "analysis_report.json"
        self.assertTrue(report_path.exists())
        
        # Verify content
        report_data = json.loads(report_path.read_text())
        self.assertEqual(report_data["run_id"], run_id)
        self.assertEqual(report_data["cv_filename"], "cv.pdf")
    
    def test_log_analysis_nonexistent_run(self):
        """Test logging analysis to nonexistent run raises error."""
        fake_run_id = "nonexistent-run-id"
        analysis_report = AnalysisReport(
            run_id=fake_run_id,
            timestamp="2025-11-24T21:00:00",
            cv_filename="cv.pdf",
            jd_filename="jd.txt",
            gap_analysis=GapAnalysisResult(),
            experience_alignments=[],
            keyword_coverage_table=[]
        )
        
        with self.assertRaises(ValueError) as context:
            self.tracker.log_analysis(fake_run_id, analysis_report)
        
        self.assertIn("not found", str(context.exception))
    
    def test_log_metrics(self):
        """Test logging metrics."""
        run_id = self.tracker.start_run("cv.pdf", "jd.txt")
        
        metrics = RunMetrics(
            run_id=run_id,
            keyword_coverage=0.85,
            experience_alignment_avg=0.75,
            processing_time_seconds=2.5,
            keywords_present=20,
            keywords_missing=5
        )
        
        self.tracker.log_metrics(run_id, metrics)
        
        # Verify metrics.json exists
        metrics_path = self.tracker.experiments_dir / run_id / "metrics.json"
        self.assertTrue(metrics_path.exists())
        
        # Verify content
        metrics_data = json.loads(metrics_path.read_text())
        self.assertEqual(metrics_data["keyword_coverage"], 0.85)
        self.assertEqual(metrics_data["keywords_present"], 20)
    
    def test_log_metrics_nonexistent_run(self):
        """Test logging metrics to nonexistent run raises error."""
        fake_run_id = "nonexistent-run-id"
        metrics = RunMetrics(
            run_id=fake_run_id,
            keyword_coverage=0.5,
            experience_alignment_avg=0.6,
            processing_time_seconds=1.0,
            keywords_present=10,
            keywords_missing=10
        )
        
        with self.assertRaises(ValueError):
            self.tracker.log_metrics(fake_run_id, metrics)
    
    def test_log_artifact_dict(self):
        """Test logging dictionary artifact."""
        run_id = self.tracker.start_run("cv.pdf", "jd.txt")
        
        artifact_data = {"key1": "value1", "key2": [1, 2, 3]}
        self.tracker.log_artifact(run_id, "test_artifact", artifact_data)
        
        # Verify artifact file exists
        artifact_path = self.tracker.experiments_dir / run_id / "test_artifact.json"
        self.assertTrue(artifact_path.exists())
        
        # Verify content
        saved_data = json.loads(artifact_path.read_text())
        self.assertEqual(saved_data, artifact_data)
    
    def test_log_artifact_list(self):
        """Test logging list artifact."""
        run_id = self.tracker.start_run("cv.pdf", "jd.txt")
        
        artifact_data = [1, 2, 3, 4, 5]
        self.tracker.log_artifact(run_id, "numbers", artifact_data)
        
        artifact_path = self.tracker.experiments_dir / run_id / "numbers.json"
        saved_data = json.loads(artifact_path.read_text())
        self.assertEqual(saved_data, artifact_data)
    
    def test_log_artifact_string(self):
        """Test logging string artifact."""
        run_id = self.tracker.start_run("cv.pdf", "jd.txt")
        
        text_content = "This is raw text content"
        self.tracker.log_artifact(run_id, "raw_text", text_content)
        
        artifact_path = self.tracker.experiments_dir / run_id / "raw_text.json"
        saved_content = artifact_path.read_text()
        self.assertEqual(saved_content, text_content)
    
    def test_log_artifact_other_type(self):
        """Test logging non-standard type artifact."""
        run_id = self.tracker.start_run("cv.pdf", "jd.txt")
        
        # Log an integer (will be converted to string)
        self.tracker.log_artifact(run_id, "number", 42)
        
        artifact_path = self.tracker.experiments_dir / run_id / "number.json"
        self.assertTrue(artifact_path.exists())
    
    def test_get_run_config(self):
        """Test retrieving run configuration."""
        run_id = self.tracker.start_run(
            cv_file="cv.pdf",
            jd_file="jd.txt",
            parameters={"test": "value"}
        )
        
        config = self.tracker.get_run_config(run_id)
        
        # Verify config is RunConfig instance
        self.assertIsInstance(config, RunConfig)
        self.assertEqual(config.run_id, run_id)
        self.assertEqual(config.cv_file, "cv.pdf")
        self.assertEqual(config.jd_file, "jd.txt")
        self.assertEqual(config.parameters["test"], "value")
    
    def test_get_run_config_nonexistent(self):
        """Test retrieving nonexistent config raises error."""
        with self.assertRaises(FileNotFoundError):
            self.tracker.get_run_config("nonexistent-id")
    
    def test_get_analysis_report(self):
        """Test retrieving analysis report."""
        run_id = self.tracker.start_run("cv.pdf", "jd.txt")
        
        # Log analysis first
        analysis_report = AnalysisReport(
            run_id=run_id,
            timestamp="2025-11-24T21:00:00",
            cv_filename="cv.pdf",
            jd_filename="jd.txt",
            gap_analysis=GapAnalysisResult(),
            experience_alignments=[],
            keyword_coverage_table=[]
        )
        self.tracker.log_analysis(run_id, analysis_report)
        
        # Retrieve it
        retrieved_report = self.tracker.get_analysis_report(run_id)
        
        self.assertIsInstance(retrieved_report, AnalysisReport)
        self.assertEqual(retrieved_report.run_id, run_id)
        self.assertEqual(retrieved_report.cv_filename, "cv.pdf")
    
    def test_get_analysis_report_nonexistent(self):
        """Test retrieving nonexistent analysis report raises error."""
        run_id = self.tracker.start_run("cv.pdf", "jd.txt")
        
        with self.assertRaises(FileNotFoundError):
            self.tracker.get_analysis_report(run_id)
    
    def test_list_runs_empty(self):
        """Test listing runs when none exist."""
        runs = self.tracker.list_runs()
        self.assertEqual(runs, [])
    
    def test_list_runs_single(self):
        """Test listing single run."""
        run_id = self.tracker.start_run("cv.pdf", "jd.txt")
        
        runs = self.tracker.list_runs()
        self.assertEqual(len(runs), 1)
        self.assertEqual(runs[0]["run_id"], run_id)
        self.assertEqual(runs[0]["cv_file"], "cv.pdf")
        self.assertEqual(runs[0]["jd_file"], "jd.txt")
        self.assertIn("timestamp", runs[0])
    
    def test_list_runs_multiple_sorted(self):
        """Test listing multiple runs sorted by timestamp."""
        import time
        
        # Create multiple runs with slight delays
        run_id1 = self.tracker.start_run("cv1.pdf", "jd1.txt")
        time.sleep(0.1)
        run_id2 = self.tracker.start_run("cv2.pdf", "jd2.txt")
        time.sleep(0.1)
        run_id3 = self.tracker.start_run("cv3.pdf", "jd3.txt")
        
        runs = self.tracker.list_runs()
        
        # Should have 3 runs
        self.assertEqual(len(runs), 3)
        
        # Should be sorted newest first
        self.assertEqual(runs[0]["run_id"], run_id3)
        self.assertEqual(runs[1]["run_id"], run_id2)
        self.assertEqual(runs[2]["run_id"], run_id1)
    
    def test_full_workflow(self):
        """Test complete workflow: start, log, retrieve."""
        # Start run
        run_id = self.tracker.start_run(
            cv_file="complete_cv.pdf",
            jd_file="complete_jd.txt",
            parameters={"threshold": 0.8}
        )
        
        # Log analysis
        analysis = AnalysisReport(
            run_id=run_id,
            timestamp="2025-11-24T21:00:00",
            cv_filename="complete_cv.pdf",
            jd_filename="complete_jd.txt",
            gap_analysis=GapAnalysisResult(),
            experience_alignments=[],
            keyword_coverage_table=[]
        )
        self.tracker.log_analysis(run_id, analysis)
        
        # Log metrics
        metrics = RunMetrics(
            run_id=run_id,
            keyword_coverage=0.9,
            experience_alignment_avg=0.8,
            processing_time_seconds=3.5,
            keywords_present=25,
            keywords_missing=3
        )
        self.tracker.log_metrics(run_id, metrics)
        
        # Log artifact
        self.tracker.log_artifact(run_id, "extras", {"note": "test"})
        
        # Retrieve everything
        config = self.tracker.get_run_config(run_id)
        report = self.tracker.get_analysis_report(run_id)
        runs = self.tracker.list_runs()
        
        # Verify
        self.assertEqual(config.cv_file, "complete_cv.pdf")
        self.assertEqual(report.cv_filename, "complete_cv.pdf")
        self.assertEqual(len(runs), 1)
        
        # Verify all files exist
        run_dir = self.tracker.experiments_dir / run_id
        self.assertTrue((run_dir / "config.json").exists())
        self.assertTrue((run_dir / "analysis_report.json").exists())
        self.assertTrue((run_dir / "metrics.json").exists())
        self.assertTrue((run_dir / "extras.json").exists())


if __name__ == "__main__":
    unittest.main()
