
import sys
import os
import json
from dotenv import load_dotenv

# Enhance path to import core
sys.path.append(os.getcwd())

load_dotenv()

from core.phase6_engine import generate_suggestions

def run_repro():
    print("Starting reproduction...")
    
    # Dummy Data matching _load_debug_data in pages/6_Rewrite.py
    cv_shell = {
        "summary": "Innovative data enthusiast.",
        "skills": ["Python", "Pandas"],
        "experience": [
            {
                "title": "ML Coach",
                "company": "Clevered",
                "dates": "2024",
                "bullets": ["I am a hard-working professional."],
            }
        ],
        "projects": [],
        "certificates": [],
    }
    mapping = {
        "present": ["python", "machine learning"],
        "missing_critical": [{"keyword": "SQL", "source": "jd"}],
        "missing_bonus": [],
        "irrelevant": [],
    }
    phase4_report = {
        "buzzwords": ["innovative"],
        "stopwords": ["and", "in", "for"],
        "duplicate_words": [],
        "duplicate_lines": [],
    }
    phase5_bundle = {
        "ats": {
            "score": 55.0,
            "components": {
                "coverage": {"value": 60.0},
                "quantified": {"value": 40.0},
                "uniqueness": {"value": 70.0},
                "buzzword": {"value": 80.0},
                "stopword": {"value": 75.0},
            },
        },
        "job_compatibility": {"score": 50.0},
        "scorecard": {},
    }
    jd_structured = {
        "title": "Data Scientist – Education",
        "must_have_skills": ["Python", "SQL", "Statistics"],
        "nice_to_have_skills": ["Cloud", "BigQuery"],
    }

    try:
        print("Calling generate_suggestions...")
        bundle = generate_suggestions(
            cv_shell=cv_shell,
            mapping=mapping,
            phase4_report=phase4_report,
            phase5_bundle=phase5_bundle,
            jd_structured=jd_structured,
            target_min_score=80.0,
        )
        print("Result Bundle Keys:", list(bundle.__dict__.keys()) if hasattr(bundle, "__dict__") else "Not an object")
        print("Bullets:", len(bundle.bullets))
        print("Summary:", len(bundle.summary))
        print("Skills:", len(bundle.skills))
        
        if not bundle.bullets and not bundle.skills:
            print("FAILURE: No suggestions generated.")
        else:
            print("SUCCESS: Suggestions generated.")
            
    except Exception as e:
        print(f"CRASH: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_repro()
