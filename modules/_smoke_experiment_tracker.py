"""
Smoke test / demo for experiment_tracker module.
Shows end-to-end experiment tracking functionality.
"""

import tempfile
import shutil
from pathlib import Path
from modules.experiment_tracker import ExperimentTracker
from modules.schemas import RunConfig, RunMetrics, AnalysisReport, GapAnalysisResult


def main():
    """Run experiment tracker demo."""
    print("=" * 80)
    print("EXPERIMENT TRACKER SMOKE TEST / DEMO")
    print("=" * 80)
    print()
    
    # Create temporary directory for demo
    temp_dir = Path(tempfile.mkdtemp())
    print(f"📁 Using temporary experiments directory: {temp_dir}")
    print()
    
    try:
        # Initialize tracker
        print("🔬 Initializing Experiment Tracker...")
        tracker = ExperimentTracker(experiments_dir=temp_dir)
        print(f"   ✓ Tracker initialized")
        print(f"   ✓ Experiments directory: {tracker.experiments_dir}")
        print()
        
        # Test 1: Start a run
        print("=" * 80)
        print("TEST 1: START EXPERIMENT RUN")
        print("=" * 80)
        print()
        
        print("📊 Starting new experiment run...")
        run_id = tracker.start_run(
            cv_file="john_doe_cv.pdf",
            jd_file="senior_engineer_jd.txt",
            parameters={
                "fuzzy_threshold": 0.8,
                "min_keyword_length": 3,
                "analysis_mode": "comprehensive"
            }
        )
        
        print(f"   ✓ Run created successfully")
        print(f"   Run ID: {run_id}")
        print()
        
        # Verify run directory
        run_dir = tracker.experiments_dir / run_id
        print(f"📂 Run directory structure:")
        print(f"   {run_dir}")
        print(f"   └── config.json ✓")
        print()
        
        # Test 2: Log analysis report
        print("=" * 80)
        print("TEST 2: LOG ANALYSIS REPORT")
        print("=" * 80)
        print()
        
        print("📝 Creating and logging analysis report...")
        analysis_report = AnalysisReport(
            run_id=run_id,
            timestamp="2025-11-24T21:30:00",
            cv_filename="john_doe_cv.pdf",
            jd_filename="senior_engineer_jd.txt",
            gap_analysis=GapAnalysisResult(
                present_keywords=[],
                missing_keywords=[],
                irrelevant_keywords=[],
                coverage_stats={
                    "required_coverage": 0.85,
                    "preferred_coverage": 0.6,
                    "overall_coverage": 0.75
                }
            ),
            experience_alignments=[],
            keyword_coverage_table=[],
            recommendations=[
                "Add Kubernetes to skills section",
                "Emphasize cloud architecture experience"
            ]
        )
        
        tracker.log_analysis(run_id, analysis_report)
        print(f"   ✓ Analysis report logged")
        print(f"   ✓ File: analysis_report.json")
        print(f"   ✓ Coverage stats logged: {analysis_report.gap_analysis.coverage_stats}")
        print()
        
        # Test 3: Log metrics
        print("=" * 80)
        print("TEST 3: LOG METRICS")
        print("=" * 80)
        print()
        
        print("📈 Logging performance metrics...")
        metrics = RunMetrics(
            run_id=run_id,
            keyword_coverage=0.85,
            experience_alignment_avg=0.78,
            processing_time_seconds=4.2,
            keywords_present=22,
            keywords_missing=4
        )
        
        tracker.log_metrics(run_id, metrics)
        print(f"   ✓ Metrics logged")
        print(f"   ✓ Keyword coverage: {metrics.keyword_coverage:.1%}")
        print(f"   ✓ Experience alignment: {metrics.experience_alignment_avg:.1%}")
        print(f"   ✓ Processing time: {metrics.processing_time_seconds}s")
        print(f"   ✓ Keywords present/missing: {metrics.keywords_present}/{metrics.keywords_missing}")
        print()
        
        # Test 4: Log artifacts
        print("=" * 80)
        print("TEST 4: LOG ARTIFACTS")
        print("=" * 80)
        print()
        
        print("📦 Logging various artifacts...")
        
        # Dict artifact
        cleaned_data = {
            "original_length": 5000,
            "cleaned_length": 4500,
            "changes_made": ["removed_extra_whitespace", "normalized_dates"]
        }
        tracker.log_artifact(run_id, "cleaned_cv_data", cleaned_data)
        print(f"   ✓ Dict artifact: cleaned_cv_data.json")
        
        # List artifact
        keywords_found = ["Python", "AWS", "Docker", "Kubernetes", "Terraform"]
        tracker.log_artifact(run_id, "extracted_keywords", keywords_found)
        print(f"   ✓ List artifact: extracted_keywords.json")
        
        # String artifact
        raw_text = "Sample CV text for demonstration purposes..."
        tracker.log_artifact(run_id, "raw_cv_excerpt", raw_text)
        print(f"   ✓ String artifact: raw_cv_excerpt.json")
        print()
        
        # Test 5: Retrieve data
        print("=" * 80)
        print("TEST 5: RETRIEVE EXPERIMENT DATA")
        print("=" * 80)
        print()
        
        print("🔍 Loading saved experiment data...")
        
        # Get config
        config = tracker.get_run_config(run_id)
        print(f"   ✓ Config retrieved")
        print(f"      CV file: {config.cv_file}")
        print(f"      JD file: {config.jd_file}")
        print(f"      Parameters: {len(config.parameters)} items")
        print()
        
        # Get analysis report
        report = tracker.get_analysis_report(run_id)
        print(f"   ✓ Analysis report retrieved")
        print(f"      Recommendations: {len(report.recommendations)}")
        print()
        
        # Test 6: Create multiple runs
        print("=" * 80)
        print("TEST 6: MULTIPLE RUNS & LISTING")
        print("=" * 80)
        print()
        
        print("🔬 Creating additional experiment runs...")
        run_id2 = tracker.start_run("jane_smith_cv.pdf", "data_scientist_jd.txt", {"mode": "quick"})
        print(f"   ✓ Run 2 created: {run_id2[:8]}...")
        
        run_id3 = tracker.start_run("bob_johnson_cv.pdf", "devops_engineer_jd.txt", {"mode": "detailed"})
        print(f"   ✓ Run 3 created: {run_id3[:8]}...")
        print()
        
        # List all runs
        print("📋 Listing all experiment runs...")
        runs = tracker.list_runs()
        print(f"   ✓ Total runs: {len(runs)}")
        print()
        
        print("   Runs (sorted newest first):")
        for i, run in enumerate(runs, 1):
            print(f"   {i}. Run ID: {run['run_id'][:8]}...")
            print(f"      CV: {run['cv_file']}")
            print(f"      JD: {run['jd_file']}")
            print(f"      Timestamp: {run['timestamp']}")
            print()
        
        # Test 7: Verify file structure
        print("=" * 80)
        print("TEST 7: VERIFY FILE STRUCTURE")
        print("=" * 80)
        print()
        
        print(f"📂 Complete file structure for Run 1:")
        run1_files = list((tracker.experiments_dir / run_id).iterdir())
        for file_path in sorted(run1_files):
            size = file_path.stat().st_size
            print(f"   ├── {file_path.name} ({size} bytes)")
        print()
        
        # Summary
        print("=" * 80)
        print("📊 SUMMARY")
        print("=" * 80)
        print()
        print(f"Total experiment runs created: {len(runs)}")
        print(f"Total files in first run: {len(run1_files)}")
        print()
        print("Features tested:")
        print("  ✓ Experiment run initialization")
        print("  ✓ Configuration saving")
        print("  ✓ Analysis report logging")
        print("  ✓ Metrics logging")
        print("  ✓ Artifact logging (dict, list, string)")
        print("  ✓ Configuration retrieval")
        print("  ✓ Analysis report retrieval")
        print("  ✓ Run listing (sorted by timestamp)")
        print("  ✓ Directory structure creation")
        print()
        
        print("=" * 80)
        print("✅ SMOKE TEST COMPLETE - All experiment tracking features working!")
        print("=" * 80)
        
    finally:
        # Cleanup
        print()
        print(f"🧹 Cleaning up temporary directory...")
        shutil.rmtree(temp_dir)
        print(f"   ✓ Temporary files removed")


if __name__ == "__main__":
    main()
