import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from modules.feature_extractor import FeatureExtractor
from modules.ats_scorer import ATSScorer
from modules.jobfit_scorer import JobFitScorer

def verify_ats_weights():
    print("Verifying ATS Weights...")
    extractor = FeatureExtractor()
    scorer = ATSScorer(extractor)
    
    # Dummy Data
    cv_text = "Python Developer with AWS experience."
    jd_text = "Looking for a Python Developer with AWS skills."
    
    cv_dict = {"experience": [{"bullets": [{"text": cv_text}]}], "skills": [{"skills": ["Python", "AWS"]}]}
    jd_dict = {"required_skills": ["Python", "AWS"], "ats_keywords": ["cloud"]}
    
    # Run Scorer
    report = scorer.score(cv_dict, jd_dict, cv_text, jd_text)
    
    # Get Config Weights
    weights = scorer.config.ats_weights
    print(f"Loaded Config Weights: {weights}")
    
    # Components (0-100 scale)
    comps = report["components"]
    
    # Calculate expected score
    expected_score = (
        comps["lexical_coverage"] * weights.lexical_coverage +
        comps["fuzzy_coverage"] * weights.fuzzy_coverage +
        comps["tfidf_relevance"] * weights.tfidf_relevance +
        comps["tfidf_cosine_similarity"] * weights.tfidf_cosine_similarity +
        comps["section_distribution"] * weights.section_distribution
    )
    
    actual_score = report["ats_score"]
    
    print(f"Calculated: {expected_score:.4f}")
    print(f"Actual:     {actual_score:.4f}")
    
    if abs(expected_score - actual_score) < 0.001:
        print("✅ ATS Weights verified match!")
        return True
    else:
        print("❌ ATS Weights Mismatch!")
        return False

def verify_jobfit_weights():
    print("\nVerifying JobFit Weights...")
    extractor = FeatureExtractor()
    scorer = JobFitScorer(extractor)
    
    # Dummy Data (minimal structure)
    cv_dict = {
        "summary": {"text": "Senior Engineer"},
        "experience": [{"bullets": [{"text": "Built Python apps"}]}],
        "skills": [{"skills": ["Python"]}],
        "education": [{"degree": "Bachelor"}]
    }
    jd_dict = {
        "role_summary": "Senior Engineer needed",
        "key_responsibilities": ["Build Python apps"],
        "required_skills": ["Python"],
        "education": "Bachelor"
    }
    
    # Run Scorer
    report = scorer.score(cv_dict, jd_dict)
    
    # Get Config Weights
    weights = scorer.config.jobfit_weights
    print(f"Loaded Config Weights: {weights}")
    
    # Components (0-100 scale)
    comps = report["components"]
    
    # Calculate expected score
    expected_score = (
        comps["summary_similarity"] * weights.summary_similarity +
        comps["experience_alignment"] * weights.experience_alignment +
        comps["skills_alignment"] * weights.skills_alignment +
        comps["education_match"] * weights.education_match +
        comps["domain_relevance"] * weights.domain_relevance
    )
    
    actual_score = report["jobfit_score"]
    
    print(f"Calculated: {expected_score:.4f}")
    print(f"Actual:     {actual_score:.4f}")
    
    if abs(expected_score - actual_score) < 0.001:
        print("✅ JobFit Weights verified match!")
        return True
    else:
        print("❌ JobFit Weights Mismatch!")
        return False

if __name__ == "__main__":
    ats_ok = verify_ats_weights()
    jobfit_ok = verify_jobfit_weights()
    
    if ats_ok and jobfit_ok:
        sys.exit(0)
    else:
        sys.exit(1)
