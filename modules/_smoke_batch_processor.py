"""
Smoke test for BatchProcessor.
Verifies end-to-end batch processing with real components.
"""

import shutil
import tempfile
from pathlib import Path
from modules.batch_processor import BatchProcessor
from modules.experiment_tracker import ExperimentTracker
from modules.schemas import StructuredCV, EnhancedJD, ContactInfo, KeywordTaxonomy, ExperienceEntry, ExperienceBullet

def create_dummy_cv():
    """Create a minimal valid StructuredCV."""
    return StructuredCV(
        contact_info=ContactInfo(
            full_name="John Doe",
            email="john@example.com",
            phone="555-1234",
            location="New York, NY"
        ),
        skills=[],
        experience=[
            ExperienceEntry(
                job_title="Junior Dev",
                company_name="StartUp Inc",
                start_date="2020",
                end_date="2022",
                description="Did stuff",
                bullets=[
                    ExperienceBullet(text="Wrote code"),
                    ExperienceBullet(text="Fixed bugs")
                ]
            )
        ],
        projects=[],
        education=[],
        certifications=[]
    )

def create_dummy_jd():
    """Create a minimal valid EnhancedJD."""
    return EnhancedJD(
        job_title="Software Engineer",
        company_name="Tech Corp",
        location="Remote",
        work_type="Full-time",
        experience_required="3+ years",
        company_overview="Great place to work",
        role_summary="Build things",
        key_responsibilities=["Write code", "Debug"],
        required_skills=["Python", "AWS"],
        preferred_skills=["Docker"],
        education="BS CS",
        soft_skills=["Communication"],
        diversity_statement="Equal opportunity",
        recruiter_contact="hr@techcorp.com",
        ats_keywords=["Python", "Cloud"],
        keyword_taxonomy=KeywordTaxonomy(
            technical_skills=["Python"],
            tools_technologies=["AWS"],
            soft_skills=["Communication"],
            domain_knowledge=[]
        ),
        must_have_requirements=[],
        nice_to_have_requirements=[]
    )

def main():
    print("=" * 80)
    print("BATCH PROCESSOR SMOKE TEST")
    print("=" * 80)
    
    # Setup
    temp_dir = Path(tempfile.mkdtemp())
    print(f"📁 Using temp dir: {temp_dir}")
    
    try:
        # Initialize components
        tracker = ExperimentTracker(experiments_dir=temp_dir)
        processor = BatchProcessor(tracker=tracker)
        print("✓ Components initialized")
        
        # Prepare batch
        cv = create_dummy_cv()
        jd = create_dummy_jd()
        
        pairs = [
            {
                "cv": cv,
                "jd": jd,
                "cv_file": "cv1.pdf",
                "jd_file": "jd1.txt"
            },
            {
                "cv": cv,
                "jd": jd,
                "cv_file": "cv2.pdf",
                "jd_file": "jd2.txt"
            }
        ]
        print(f"✓ Prepared batch of {len(pairs)} pairs")
        
        # Run batch processing
        print("\n🚀 Running batch processing...")
        df = processor.process_batch(pairs)
        
        # Verify results
        print("\n📊 Results Summary:")
        print(df)
        
        if len(df) == 2:
            print("\n✅ Smoke test passed: Processed 2 pairs successfully")
        else:
            print(f"\n❌ Smoke test failed: Expected 2 results, got {len(df)}")
            
        # Verify tracker logs
        runs = tracker.list_runs()
        print(f"\n📝 Tracker logs: Found {len(runs)} runs")
        if len(runs) == 2:
            print("✅ Tracker verification passed")
        else:
            print("❌ Tracker verification failed")
            
    finally:
        shutil.rmtree(temp_dir)
        print("\n🧹 Cleanup complete")

if __name__ == "__main__":
    main()
