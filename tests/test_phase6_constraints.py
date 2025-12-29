import unittest
import sys
from pathlib import Path
from typing import Dict, List

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.rewrite_validator import RewriteValidator

class TestPhase6Constraints(unittest.TestCase):
    def setUp(self):
        self.validator = RewriteValidator()
        self.maxDiff = None

    # =========================================================================
    # 3.2 Summary Validation Rules
    # =========================================================================
    
    def test_summary_line_count(self):
        """Rule: Rewritten summary is 2-3 lines."""
        # Fixtures
        valid_2_lines = "Line 1.\nLine 2."
        valid_3_lines = "Line 1.\nLine 2.\nLine 3."
        invalid_1_line = "Just one line."
        invalid_4_lines = "L1\nL2\nL3\nL4"
        
        # Test 2 lines (Pass)
        res = self.validator.validate_all_constraints({"summary": {"text": valid_2_lines}}, {}, [])
        rule = next(r for r in res["rules"] if r["rule_id"] == "SUMMARY_LINES_2_TO_3")
        self.assertTrue(rule["passed"], "2 lines should pass")
        
        # Test 3 lines (Pass)
        res = self.validator.validate_all_constraints({"summary": {"text": valid_3_lines}}, {}, [])
        rule = next(r for r in res["rules"] if r["rule_id"] == "SUMMARY_LINES_2_TO_3")
        self.assertTrue(rule["passed"], "3 lines should pass")
        
        # Test 1 line (Fail)
        res = self.validator.validate_all_constraints({"summary": {"text": invalid_1_line}}, {}, [])
        rule = next(r for r in res["rules"] if r["rule_id"] == "SUMMARY_LINES_2_TO_3")
        self.assertFalse(rule["passed"], "1 line should fail")
        
        # Test 4 lines (Fail)
        res = self.validator.validate_all_constraints({"summary": {"text": invalid_4_lines}}, {}, [])
        rule = next(r for r in res["rules"] if r["rule_id"] == "SUMMARY_LINES_2_TO_3")
        self.assertFalse(rule["passed"], "4 lines should fail")

    def test_summary_word_count(self):
        """Rule: Word count <= 60."""
        # Fixtures
        valid_60 = "word " * 60
        invalid_61 = "word " * 61
        
        # Test 60 words (Pass)
        res = self.validator.validate_all_constraints({"summary": {"text": valid_60}}, {}, [])
        rule = next(r for r in res["rules"] if r["rule_id"] == "SUMMARY_WORD_COUNT_MAX_60")
        self.assertTrue(rule["passed"], "60 words should pass")
        
        # Test 61 words (Fail)
        res = self.validator.validate_all_constraints({"summary": {"text": invalid_61}}, {}, [])
        rule = next(r for r in res["rules"] if r["rule_id"] == "SUMMARY_WORD_COUNT_MAX_60")
        self.assertFalse(rule["passed"], "61 words should fail")

    def test_summary_action_verb(self):
        """Rule: Starts with action verbs."""
        # Fixtures
        valid_verb = "Developed scalable systems.\nManaged teams."
        invalid_noun = "The developer built systems.\nHe managed teams."
        
        # Test valid verb (Pass)
        res = self.validator.validate_all_constraints({"summary": {"text": valid_verb}}, {}, [])
        rule = next(r for r in res["rules"] if r["rule_id"] == "SUMMARY_STARTS_WITH_ACTION_VERB")
        self.assertTrue(rule["passed"], "Starting with 'Developed' should pass")
        
        # Test invalid start (Fail)
        res = self.validator.validate_all_constraints({"summary": {"text": invalid_noun}}, {}, [])
        rule = next(r for r in res["rules"] if r["rule_id"] == "SUMMARY_STARTS_WITH_ACTION_VERB")
        self.assertFalse(rule["passed"], "Starting with 'The' should fail")

    def test_summary_stopwords(self):
        """Rule: No stopwords detected."""
        # Fixtures
        valid_clean = "Developed robust APIs using Python."
        invalid_stopword = "Developed the APIs."
        
        # Test clean (Pass)
        res = self.validator.validate_all_constraints({"summary": {"text": valid_clean}}, {}, [])
        rule = next(r for r in res["rules"] if r["rule_id"] == "SUMMARY_NO_STOPWORDS")
        self.assertTrue(rule["passed"], "No stopwords should pass")
        
        # Test stopword (Fail)
        res = self.validator.validate_all_constraints({"summary": {"text": invalid_stopword}}, {}, [])
        rule = next(r for r in res["rules"] if r["rule_id"] == "SUMMARY_NO_STOPWORDS")
        self.assertFalse(rule["passed"], "Stopword 'the' should fail")

    # =========================================================================
    # 3.3 Bullet Validation Rules
    # =========================================================================

    def test_bullet_single_line(self):
        """Rule: Single line (no newlines)."""
        # Fixtures
        valid_bullet = "Optimized database queries by 30%."
        invalid_bullet = "Optimized database\nqueries by 30%."
        
        cv = {"experience": [{"bullets": [{"text": valid_bullet}, {"text": invalid_bullet}]}]}
        res = self.validator.validate_all_constraints(cv, {}, [])
        
        rules = [r for r in res["rules"] if r["rule_id"] == "BULLET_SINGLE_LINE"]
        self.assertTrue(rules[0]["passed"], "Single line bullet should pass")
        self.assertFalse(rules[1]["passed"], "Multiline bullet should fail")

    def test_bullet_metric(self):
        """Rule: Contains quantifiable metric."""
        # Fixtures
        valid_metric = "Increased revenue by 20%."
        invalid_no_metric = "Increased revenue significantly."
        
        cv = {"experience": [{"bullets": [{"text": valid_metric}, {"text": invalid_no_metric}]}]}
        res = self.validator.validate_all_constraints(cv, {}, [])
        
        rules = [r for r in res["rules"] if r["rule_id"] == "BULLET_HAS_QUANTIFIABLE_METRIC"]
        self.assertTrue(rules[0]["passed"], "Metric present should pass")
        self.assertFalse(rules[1]["passed"], "No metric should fail")

    def test_bullet_repetition(self):
        """Rule: No word repetition across bullets."""
        # Fixtures
        # "Optimized" repeated
        bullets = [
            {"text": "Optimized SQL queries by 50%."},
            {"text": "Optimized Python scripts by 20%."}
        ]
        cv = {"experience": [{"bullets": bullets}]}
        
        res = self.validator.validate_all_constraints(cv, {}, [])
        rule = next(r for r in res["rules"] if r["rule_id"] == "BULLET_NO_WORD_REPETITION_ACROSS_BULLETS")
        self.assertFalse(rule["passed"], "Repeated word 'Optimized' should fail")
        
        # Unique words (ignoring stopwords)
        bullets_unique = [
            {"text": "Refactored SQL queries by 50%."},
            {"text": "Enhanced Python scripts by 20%."}
        ]
        cv_unique = {"experience": [{"bullets": bullets_unique}]}
        res = self.validator.validate_all_constraints(cv_unique, {}, [])
        rule = next(r for r in res["rules"] if r["rule_id"] == "BULLET_NO_WORD_REPETITION_ACROSS_BULLETS")
        self.assertTrue(rule["passed"], "Unique words should pass")

    # =========================================================================
    # 3.4 Skills Validation Rules
    # =========================================================================

    def test_skills_fabrication(self):
        """Rule: No fabricated skills."""
        original_skills = [{"category_name": "Lang", "skills": ["Python"]}]
        experience = [{"job_title": "Dev", "bullets": [{"text": "Used Java"}]}]
        original_cv = {"skills": original_skills, "experience": experience}
        
        # Valid: In original
        rewritten_valid = {"Lang": ["Python"]}
        res = self.validator.validate_all_constraints({"skills": rewritten_valid}, original_cv, [])
        rule = next(r for r in res["rules"] if r["rule_id"] == "SKILLS_NO_FABRICATED_SKILLS")
        self.assertTrue(rule["passed"], "Original skill should pass")
        
        # Valid: In experience
        rewritten_exp = {"Lang": ["Java"]}
        res = self.validator.validate_all_constraints({"skills": rewritten_exp}, original_cv, [])
        rule = next(r for r in res["rules"] if r["rule_id"] == "SKILLS_NO_FABRICATED_SKILLS")
        self.assertTrue(rule["passed"], "Experience skill should pass")
        
        # Invalid: Fabricated
        rewritten_fake = {"Lang": ["Rust"]}
        res = self.validator.validate_all_constraints({"skills": rewritten_fake}, original_cv, [])
        rule = next(r for r in res["rules"] if r["rule_id"] == "SKILLS_NO_FABRICATED_SKILLS")
        self.assertFalse(rule["passed"], "Fabricated skill should fail")

    def test_skills_categorization(self):
        """Rule: Skills categorized correctly."""
        # Allowed: "Programming Languages", "Frameworks/Libraries", "Tools/Platforms", "Databases", "Cloud/DevOps", "Methodologies"
        
        # Valid category
        rewritten_valid = {"Programming Languages": ["Python"]}
        res = self.validator.validate_all_constraints({"skills": rewritten_valid}, {}, [])
        rule = next(r for r in res["rules"] if r["rule_id"] == "SKILLS_CATEGORIZED_CORRECTLY")
        self.assertTrue(rule["passed"], "Valid category should pass")
        
        # Invalid category
        rewritten_invalid = {"My Skills": ["Python"]}
        res = self.validator.validate_all_constraints({"skills": rewritten_invalid}, {}, [])
        rule = next(r for r in res["rules"] if r["rule_id"] == "SKILLS_CATEGORIZED_CORRECTLY")
        self.assertFalse(rule["passed"], "Invalid category should fail")

    def test_skills_prioritization(self):
        """Rule: JD-required skills prioritized."""
        jd_skills = ["Python", "AWS"]
        
        # Valid: JD skills first
        rewritten_valid = {"Programming Languages": ["Python", "Java"], "Cloud/DevOps": ["AWS", "Docker"]}
        res = self.validator.validate_all_constraints({"skills": rewritten_valid}, {}, jd_skills)
        rule = next(r for r in res["rules"] if r["rule_id"] == "SKILLS_JD_REQUIRED_PRIORITIZED")
        self.assertTrue(rule["passed"], "Prioritized skills should pass")
        
        # Invalid: JD skill after non-JD skill
        rewritten_invalid = {"Programming Languages": ["Java", "Python"]} # Python is JD, Java is not
        res = self.validator.validate_all_constraints({"skills": rewritten_invalid}, {}, jd_skills)
        rule = next(r for r in res["rules"] if r["rule_id"] == "SKILLS_JD_REQUIRED_PRIORITIZED")
        self.assertFalse(rule["passed"], "Unprioritized skills should fail")

    # =========================================================================
    # 3.5 Entity Preservation Rules
    # =========================================================================

    def test_entity_preservation(self):
        """Rules: Job titles, companies, dates, education, count unchanged."""
        original_cv = {
            "experience": [
                {"job_title": "Dev", "company_name": "Corp", "start_date": "2020", "end_date": "2021"}
            ],
            "education": [{"degree": "BS", "institution": "Uni"}]
        }
        
        # Valid: No changes
        res = self.validator.validate_all_constraints(original_cv, original_cv, [])
        self.assertTrue(all(r["passed"] for r in res["rules"] if "ENTITY_" in r["rule_id"]))
        
        # Invalid: Changed job title
        changed_title = {
            "experience": [
                {"job_title": "Senior Dev", "company_name": "Corp", "start_date": "2020", "end_date": "2021"}
            ],
            "education": [{"degree": "BS", "institution": "Uni"}]
        }
        res = self.validator.validate_all_constraints(changed_title, original_cv, [])
        rule = next(r for r in res["rules"] if r["rule_id"] == "ENTITY_JOB_TITLES_UNCHANGED")
        self.assertFalse(rule["passed"], "Changed job title should fail")
        
        # Invalid: Changed count
        changed_count = {
            "experience": [],
            "education": [{"degree": "BS", "institution": "Uni"}]
        }
        res = self.validator.validate_all_constraints(changed_count, original_cv, [])
        rule = next(r for r in res["rules"] if r["rule_id"] == "ENTITY_EXPERIENCE_ENTRY_COUNT_UNCHANGED")
        self.assertFalse(rule["passed"], "Changed count should fail")

if __name__ == '__main__':
    unittest.main()
