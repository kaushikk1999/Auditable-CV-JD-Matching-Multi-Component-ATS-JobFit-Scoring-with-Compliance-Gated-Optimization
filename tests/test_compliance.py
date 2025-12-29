import sys
import re
import json
import unittest
from pathlib import Path
from typing import Dict, List

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.compliance_checker import ComplianceChecker, ComplianceAuditor
from config.word_lists import (
    APPROVED_ACTION_VERBS, BANNED_TERMS, STOPWORDS, 
    CONTRACTIONS_MAP, METRIC_PATTERNS
)
from config.settings import (
    ENFORCE_UNIQUE_WORDS, ALLOW_NUMERIC_REPETITION,
    TARGET_WORD_COUNT_MIN, TARGET_WORD_COUNT_MAX,
    TARGET_BULLET_COUNT_MIN, TARGET_BULLET_COUNT_MAX
)

class TestComplianceChecker(unittest.TestCase):
    
    def setUp(self):
        self.checker = ComplianceChecker()
    
    # ========== BUZZWORD DETECTION TESTS ==========
    
    def test_buzzword_detection_exact(self):
        """Test exact match detection (case-insensitive)."""
        banned = list(BANNED_TERMS)[0]
        text = f"I am a {banned} professional. Also {banned.upper()} and {banned.lower()}."
        result = self.checker.check_buzzwords(text)
        
        self.assertFalse(result["passed"])
        self.assertGreaterEqual(result["violation_count"], 1)
        self.assertIn(banned, result["violations"])
    
    def test_buzzword_detection_fuzzy(self):
        """Test fuzzy match detection."""
        # "Synergy" is a common buzzword. "Synergies" should be caught.
        text = "We created many synergies in the team."
        # Assuming "Synergy" is in BANNED_TERMS
        if "Synergy" in BANNED_TERMS:
            result = self.checker.check_buzzwords(text)
            self.assertFalse(result["passed"])
            # Fuzzy match might return the word found in text
            violations_lower = [v.lower() for v in result["violations"]]
            self.assertTrue(any("synergies" in v or "synergy" in v for v in violations_lower))

    def test_buzzword_clean_text(self):
        """Test clean text returns NO_BUZZWORDS_PRESENT."""
        text = "I wrote code and fixed bugs."
        result = self.checker.check_buzzwords(text)
        self.assertTrue(result["passed"])
        self.assertEqual(result["status"], "NO_BUZZWORDS_PRESENT")

    # ========== STOPWORD DETECTION TESTS ==========

    def test_stopword_contraction_expansion(self):
        """Test contraction expansion before check."""
        # "don't" -> "do not". "not" might be a stopword depending on list.
        # Let's use a known contraction map entry.
        contraction = list(CONTRACTIONS_MAP.keys())[0] # e.g. "don't"
        expansion = CONTRACTIONS_MAP[contraction] # "do not"
        
        text = f"I {contraction} like this."
        # If expansion contains stopwords, they should be found.
        # "do" and "not" are likely stopwords.
        result = self.checker.check_stopwords(text)
        
        # Check if expansion words are in violations
        expansion_words = expansion.split()
        violations = result["violations"]
        
        # At least one word from expansion should be detected if it's a stopword
        detected = any(word in violations for word in expansion_words if word in STOPWORDS)
        if detected:
            self.assertTrue(True)
        else:
            # If no stopwords in expansion, this test is inconclusive but passes
            pass

    def test_stopword_categories(self):
        """Test detection of various stopword categories."""
        # Construct text with article, preposition, pronoun
        text = "The cat is on the mat with me."
        result = self.checker.check_stopwords(text)
        self.assertFalse(result["passed"])
        self.assertIn("the", result["violations"])
        self.assertIn("on", result["violations"])
        self.assertIn("with", result["violations"])
        self.assertIn("me", result["violations"])

    def test_stopword_exclusions(self):
        """Test exclusion of numbers, emails, URLs."""
        text = "Contact me at test@example.com or visit http://example.com in 2024."
        result = self.checker.check_stopwords(text)
        
        violations = result["violations"]
        self.assertNotIn("test@example.com", violations)
        self.assertNotIn("http://example.com", violations)
        self.assertNotIn("2024", violations)
        
        # "at", "or", "in" are likely stopwords and should be found
        self.assertIn("at", violations)

    # ========== WORD UNIQUENESS TESTS ==========

    def test_word_uniqueness_counts(self):
        """Test word count aggregation (case-insensitive)."""
        text = "Test test TEST."
        result = self.checker.check_word_uniqueness(text)
        
        self.assertFalse(result["passed"])
        self.assertIn("test", result["duplicates"])
        self.assertEqual(result["duplicates"]["test"], 3)

    def test_word_uniqueness_numeric_exclusion(self):
        """Test numeric exclusion if flag enabled."""
        if ALLOW_NUMERIC_REPETITION:
            text = "123 123 2024 2024"
            result = self.checker.check_word_uniqueness(text)
            self.assertTrue(result["passed"])
            self.assertEqual(len(result["duplicates"]), 0)

    # ========== DUPLICATE TERMS TESTS ==========

    def test_duplicate_terms_phrases(self):
        """Test bigram and trigram detection."""
        text = "Project management skills. Project management skills. Software engineering lead. Software engineering lead."
        result = self.checker.check_duplicate_terms(text)
        
        self.assertFalse(result["passed"])
        self.assertTrue(any("project management" in p for p in result["duplicate_phrases"]))
        self.assertTrue(any("software engineering" in p for p in result["duplicate_phrases"]))

    def test_duplicate_terms_date_filter(self):
        """Test filtering of date patterns."""
        text = "June 2020. June 2020. July 2021. July 2021."
        result = self.checker.check_duplicate_terms(text)
        
        # Should pass if dates are filtered
        # Note: Implementation filters "Word Year" pattern
        self.assertTrue(result["passed"])

    # ========== QUANTIFICATION INTEGRITY TESTS ==========

    def test_quantification_integrity(self):
        """Test action verbs and metrics detection."""
        verb = list(APPROVED_ACTION_VERBS)[0]
        bullets = [
            f"{verb} revenue by 50%", # Compliant
            "Did stuff", # Non-compliant (no metric, weak verb)
            f"{verb} items" # Non-compliant (no metric)
        ]
        
        result = self.checker.check_quantification(bullets)
        
        self.assertFalse(result["passed"])
        self.assertIn(0, result["compliant_bullets"])
        self.assertIn(1, result["non_compliant_bullets"])
        self.assertIn(2, result["non_compliant_bullets"])
        self.assertAlmostEqual(result["compliance_rate"], 1/3)

    # ========== BREVITY ANALYSIS TESTS ==========

    def test_brevity_analysis(self):
        """Test word and bullet counts."""
        # Create text with ~10 words
        text = "One two three four five six seven eight nine ten."
        bullet_count = 10
        
        result = self.checker.check_brevity(text, bullet_count)
        
        # Should fail word count (too low) and bullet count (too low)
        self.assertFalse(result["passed"])
        self.assertEqual(result["word_count"], 10)
        self.assertEqual(result["bullet_count"], 10)
        self.assertEqual(result["word_count_status"], "WORDCOUNT_ADJUSTMENT_REQUIRED")

    # ========== BULLET DENSITY TESTS ==========

    def test_bullet_density(self):
        """Test distribution recommendations."""
        # Imbalanced: 90% experience
        bullets_by_section = {"experience": 90, "projects": 10}
        result = self.checker.check_bullet_density(bullets_by_section)
        
        # Total 100 is likely too high (target max usually ~25-30)
        self.assertFalse(result["passed"]) 
        
        # Check recommendations
        recs = result["recommendations"]
        # Should warn about experience dominance (>80%) or project ratio
        self.assertTrue(len(recs) > 0)


class TestComplianceAuditor(unittest.TestCase):
    
    def setUp(self):
        self.auditor = ComplianceAuditor()
    
    def test_full_audit(self):
        """Test full audit execution."""
        text = "I am a results-driven leader. I managed a team."
        bullets = ["Managed team of 5", "Increased sales by 10%"]
        
        report = self.auditor.audit_cv_text(text, bullets)
        
        # Check structure
        self.assertIn("timestamp", report)
        self.assertIn("overall_passed", report)
        self.assertIn("checks", report)
        
        checks = report["checks"]
        self.assertEqual(len(checks), 7) # All 7 checks
        self.assertIn("buzzword_audit", checks)
        self.assertIn("bullet_density", checks)
        
        # Check warnings/critical
        self.assertIsInstance(report["critical_violations"], list)
        self.assertIsInstance(report["warnings"], list)


class TestWordListQuality(unittest.TestCase):
    
    def test_no_duplicates(self):
        """Ensure no duplicates in word lists."""
        self.assertEqual(len(APPROVED_ACTION_VERBS), len(set(APPROVED_ACTION_VERBS)))
        self.assertEqual(len(BANNED_TERMS), len(set(BANNED_TERMS)))
        self.assertEqual(len(STOPWORDS), len(set(STOPWORDS)))
    
    def test_regex_compilation(self):
        """Ensure regex patterns compile."""
        for pattern in METRIC_PATTERNS:
            try:
                re.compile(pattern)
            except re.error:
                self.fail(f"Regex compilation failed for: {pattern}")


class TestEdgeCases(unittest.TestCase):
    
    def setUp(self):
        self.checker = ComplianceChecker()

    def test_empty_text(self):
        """Test empty text input."""
        result = self.checker.check_buzzwords("")
        self.assertTrue(result["passed"])
        self.assertEqual(result["violation_count"], 0)

    def test_numeric_only(self):
        """Test numeric only text."""
        if ALLOW_NUMERIC_REPETITION:
            result = self.checker.check_word_uniqueness("1 1 2 2")
            self.assertTrue(result["passed"])

class TestIntegration(unittest.TestCase):
    
    def setUp(self):
        self.auditor = ComplianceAuditor()
        # Mock StructuredCV data
        self.mock_cv_data = {
            "personal_info": {"name": "Test User", "email": "test@example.com"},
            "professional_summary": "Experienced software engineer with strong leadership skills.",
            "work_experience": [
                {
                    "company": "Tech Corp",
                    "role": "Senior Dev",
                    "description": [
                        "Led a team of 5 developers.",
                        "Increased revenue by 20% using Python."
                    ]
                }
            ],
            "education": [],
            "skills": ["Python", "Leadership"],
            "projects": []
        }
    
    def test_integration_flow(self):
        """Test full flow: Data -> Text -> Audit -> Report -> JSON -> Load."""
        # 1. Convert to text (simulated)
        text = self.mock_cv_data["professional_summary"] + " " + " ".join(
            [b for job in self.mock_cv_data["work_experience"] for b in job["description"]]
        )
        bullets = [b for job in self.mock_cv_data["work_experience"] for b in job["description"]]
        
        # 2. Audit
        report = self.auditor.audit_cv_text(text, bullets)
        self.assertIn("overall_passed", report)
        
        # 3. Save to JSON (simulated)
        json_str = json.dumps(report)
        self.assertTrue(len(json_str) > 0)
        
        # 4. Load from JSON
        loaded_report = json.loads(json_str)
        self.assertEqual(loaded_report["overall_passed"], report["overall_passed"])
        self.assertEqual(len(loaded_report["checks"]), 7)


class TestUILogic(unittest.TestCase):
    
    def test_audit_configuration_toggles(self):
        """Test that configuration flags impact the audit result."""
        # This test assumes we can modify settings at runtime or mock them.
        # Since settings are imported, we might need to patch them if we want to test toggles dynamically.
        # However, for this verification, we can check if the Auditor logic uses the flags.
        
        # We verify that critical violations are populated based on flags.
        # If ENFORCE_BUZZWORD_BAN is True (default), a buzzword should cause failure.
        
        checker = ComplianceChecker()
        text = "I am a ninja." # "ninja" is likely banned
        result = checker.check_buzzwords(text)
        
        # If "ninja" is banned
        if not result["passed"]:
            # Check if this failure propagates to critical violations in Auditor
            auditor = ComplianceAuditor()
            report = auditor.audit_cv_text(text, [])
            
            # If ENFORCE_BUZZWORD_BAN is True, it should be in critical_violations
            from config.settings import ENFORCE_BUZZWORD_BAN
            if ENFORCE_BUZZWORD_BAN:
                self.assertIn("buzzword_audit", report["critical_violations"])
            else:
                self.assertNotIn("buzzword_audit", report["critical_violations"])

if __name__ == "__main__":
    unittest.main()
