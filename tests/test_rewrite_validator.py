import unittest
from unittest.mock import MagicMock, patch
from modules.rewrite_validator import RewriteValidator

class TestRewriteValidator(unittest.TestCase):
    def setUp(self):
        self.validator = RewriteValidator()
        # Mock the compliance checker to isolate validator logic
        self.validator.compliance_checker = MagicMock()
        
        # Default mock behaviors
        self.validator.compliance_checker.check_stopwords.return_value = {"passed": True, "violation_count": 0, "violations": []}
        self.validator.compliance_checker.check_buzzwords.return_value = {"passed": True, "violation_count": 0, "violations": []}
        self.validator.compliance_checker._starts_with_action_verb.return_value = True
        self.validator.compliance_checker._contains_metric.return_value = True

    def test_validate_summary_valid(self):
        original = "Old summary."
        rewritten = "Line 1 content.\nLine 2 content."
        is_valid, violations = self.validator.validate_summary(original, rewritten)
        self.assertTrue(is_valid)
        self.assertEqual(len(violations), 0)

    def test_validate_summary_invalid_lines(self):
        original = "Old summary."
        rewritten = "Line 1 only."
        is_valid, violations = self.validator.validate_summary(original, rewritten)
        self.assertFalse(is_valid)
        self.assertIn("Summary must be 2-3 lines", violations[0])

    def test_validate_summary_stopwords(self):
        self.validator.compliance_checker.check_stopwords.return_value = {"passed": False, "violation_count": 1, "violations": ["the"]}
        original = "Old summary."
        rewritten = "Line 1.\nLine 2."
        is_valid, violations = self.validator.validate_summary(original, rewritten)
        self.assertFalse(is_valid)
        self.assertIn("Stopwords present", violations[0])

    def test_validate_bullet_valid(self):
        is_valid, violations = self.validator.validate_bullet("orig", "Valid bullet.", set())
        self.assertTrue(is_valid)
        self.assertEqual(len(violations), 0)

    def test_validate_bullet_multiline(self):
        is_valid, violations = self.validator.validate_bullet("orig", "Line 1\nLine 2", set())
        self.assertFalse(is_valid)
        self.assertIn("Bullet must be single line", violations)

    def test_validate_bullet_duplicates(self):
        used_words = {"duplicate"}
        is_valid, violations = self.validator.validate_bullet("orig", "This has a duplicate word.", used_words)
        self.assertFalse(is_valid)
        self.assertTrue(any("Duplicate words" in v for v in violations))

    def test_validate_skills_valid(self):
        original = [{"skills": ["Python"]}]
        rewritten = {"Lang": ["Python"]}
        is_valid, violations = self.validator.validate_skills(original, rewritten, [])
        self.assertTrue(is_valid)

    def test_validate_skills_fabrication(self):
        original = [{"skills": ["Python"]}]
        rewritten = {"Lang": ["Rust"]} # Not in original, not in experience
        is_valid, violations = self.validator.validate_skills(original, rewritten, [])
        self.assertFalse(is_valid)
        self.assertTrue(any("Potential fabricated skill: rust" in v for v in violations))

    def test_validate_no_entity_changes_valid(self):
        cv = {"experience": [{"job_title": "Dev", "company_name": "Corp", "start_date": "2020", "end_date": "2021"}], "education": []}
        is_valid, violations = self.validator.validate_no_entity_changes(cv, cv)
        self.assertTrue(is_valid)

    def test_validate_no_entity_changes_invalid(self):
        orig = {"experience": [{"job_title": "Dev", "company_name": "Corp", "start_date": "2020", "end_date": "2021"}], "education": []}
        rewritten = {"experience": [{"job_title": "Senior Dev", "company_name": "Corp", "start_date": "2020", "end_date": "2021"}], "education": []}
        is_valid, violations = self.validator.validate_no_entity_changes(orig, rewritten)
        self.assertFalse(is_valid)
        self.assertTrue(any("Job title changed" in v for v in violations))

if __name__ == '__main__':
    unittest.main()
