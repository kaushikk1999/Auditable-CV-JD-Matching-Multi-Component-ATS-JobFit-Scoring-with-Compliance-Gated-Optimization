import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.rewrite_validator import RewriteValidator

def test_manual():
    print("Starting manual test for RewriteValidator...")
    
    validator = RewriteValidator()
    
    # 1. Test Summary Validation
    print("\n--- Summary Validation ---")
    original_summary = "Old summary."
    # Valid summary: 2 lines, no stopwords/buzzwords (assuming simple words pass), < 60 words
    valid_summary = "Managed team effectively.\nDelivered project on time."
    is_valid, violations = validator.validate_summary(original_summary, valid_summary)
    print(f"Valid Summary Result: {is_valid}, Violations: {violations}")
    
    # Invalid summary: 1 line
    invalid_summary = "One line summary."
    is_valid, violations = validator.validate_summary(original_summary, invalid_summary)
    print(f"Invalid Summary Result: {is_valid}, Violations: {violations}")
    
    # 2. Test Bullet Validation
    print("\n--- Bullet Validation ---")
    used_words = set()
    # Valid bullet: Action verb + metric
    valid_bullet = "Designed scalable system handling 50% more traffic."
    is_valid, violations = validator.validate_bullet("orig", valid_bullet, used_words)
    print(f"Valid Bullet Result: {is_valid}, Violations: {violations}")
    
    # Invalid bullet: No metric
    invalid_bullet = "Designed scalable system."
    is_valid, violations = validator.validate_bullet("orig", invalid_bullet, used_words)
    print(f"Invalid Bullet Result: {is_valid}, Violations: {violations}")
    
    # 3. Test Skills Validation
    print("\n--- Skills Validation ---")
    original_skills = [{"skills": ["Python", "Java"]}]
    # Valid: only original skills
    valid_skills = {"Languages": ["Python"]}
    is_valid, violations = validator.validate_skills(original_skills, valid_skills, [])
    print(f"Valid Skills Result: {is_valid}, Violations: {violations}")
    
    # Invalid: fabricated skill
    invalid_skills = {"Languages": ["Rust"]}
    is_valid, violations = validator.validate_skills(original_skills, invalid_skills, [])
    print(f"Invalid Skills Result: {is_valid}, Violations: {violations}")
    
    # 4. Test Entity Changes
    print("\n--- Entity Validation ---")
    orig_cv = {"experience": [{"job_title": "Dev", "company_name": "Corp", "start_date": "2020", "end_date": "2021"}]}
    # Valid: no change
    valid_cv = {"experience": [{"job_title": "Dev", "company_name": "Corp", "start_date": "2020", "end_date": "2021"}]}
    is_valid, violations = validator.validate_no_entity_changes(orig_cv, valid_cv)
    print(f"Valid Entity Result: {is_valid}, Violations: {violations}")
    
    # Invalid: title change
    invalid_cv = {"experience": [{"job_title": "Senior Dev", "company_name": "Corp", "start_date": "2020", "end_date": "2021"}]}
    is_valid, violations = validator.validate_no_entity_changes(orig_cv, invalid_cv)
    print(f"Invalid Entity Result: {is_valid}, Violations: {violations}")

if __name__ == "__main__":
    test_manual()
