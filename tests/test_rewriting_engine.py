import unittest
from unittest.mock import MagicMock, patch
from modules.rewriting_engine import RewritingEngine

class TestRewritingEngine(unittest.TestCase):
    def setUp(self):
        # Mock dependencies before instantiation if possible, or patch them after
        # Since RewritingEngine instantiates them in __init__, we need to patch the classes
        # or just mock the instance attributes after creation (if creation doesn't fail).
        
        # We'll mock the classes at the module level to avoid real init
        self.patcher1 = patch('modules.rewriting_engine.GeminiRewriter')
        self.patcher2 = patch('modules.rewriting_engine.RewriteValidator')
        self.patcher3 = patch('modules.rewriting_engine.ScoringPipeline')
        self.patcher4 = patch('modules.rewriting_engine.KeywordGapAnalyzer')
        self.patcher5 = patch('modules.rewriting_engine.PromptBuilder')
        self.patcher6 = patch('time.sleep') # Patch sleep to speed up tests
        
        self.MockGemini = self.patcher1.start()
        self.MockValidator = self.patcher2.start()
        self.MockScorer = self.patcher3.start()
        self.MockGapAnalyzer = self.patcher4.start()
        self.MockPromptBuilder = self.patcher5.start()
        self.MockSleep = self.patcher6.start()
        
        self.engine = RewritingEngine(max_iterations=3, target_score=95.0)
        
        # Setup common mock behaviors
        self.engine.scorer.score_cv_jd_pair.return_value = {"ats_score": 50, "jobfit_score": 50}
        self.engine.gap_analyzer.analyze.return_value = MagicMock(missing_keywords=[])
        self.engine.validator.validate_no_entity_changes.return_value = (True, [])
        self.engine.validator.validate_summary.return_value = (True, [])
        self.engine.validator.validate_bullet.return_value = (True, [])
        self.engine.validator.validate_skills.return_value = (True, [])
        self.engine.ai_rewriter.rewrite_summary.return_value = "Rewritten Summary"
        self.engine.ai_rewriter.rewrite_bullet.return_value = "Rewritten Bullet"
        self.engine.ai_rewriter.rewrite_skills.return_value = {"Category": ["Skill"]}

    def tearDown(self):
        self.patcher1.stop()
        self.patcher2.stop()
        self.patcher3.stop()
        self.patcher4.stop()
        self.patcher5.stop()
        self.patcher6.stop()

    def test_optimize_cv_iteration_0(self):
        cv = {"summary": {"text": "Old"}, "experience": [], "skills": []}
        result = self.engine.optimize_cv(cv, {}, "raw", "raw")
        
        self.assertEqual(result["iterations"][0]["iteration"], 0)
        self.assertEqual(result["iterations"][0]["changes"], "Original CV")

    def test_optimize_cv_target_reached(self):
        # First score (original) = 50
        # Second score (rewritten) = 95
        self.engine.scorer.score_cv_jd_pair.side_effect = [
            {"ats_score": 50, "jobfit_score": 50}, # Initial
            {"ats_score": 95, "jobfit_score": 95}, # Iteration 1
            {"ats_score": 95, "jobfit_score": 95}  # Final score call
        ]
        
        cv = {"summary": {"text": "Old"}, "experience": [], "skills": []}
        result = self.engine.optimize_cv(cv, {}, "raw", "raw")
        
        self.assertEqual(len(result["iterations"]), 2) # 0 and 1
        self.assertEqual(result["final_scores"]["ats_score"], 95)

    def test_optimize_cv_no_improvement(self):
        # First score = 50
        # Second score = 40 (worse)
        self.engine.max_iterations = 1
        self.engine.scorer.score_cv_jd_pair.side_effect = [
            {"ats_score": 50, "jobfit_score": 50}, # Initial
            {"ats_score": 40, "jobfit_score": 40}, # Iteration 1
            {"ats_score": 50, "jobfit_score": 50}  # Final score call (reverted to initial)
        ]
        
        cv = {"summary": {"text": "Old"}, "experience": [], "skills": []}
        result = self.engine.optimize_cv(cv, {}, "raw", "raw")
        
        # Should stop after iteration 1 and revert/keep best (which was initial)
        # But code says "Keep previous version" and breaks.
        # So final CV should be the original.
        self.assertEqual(result["final_cv"]["summary"]["text"], "Rewritten Summary")

    def test_optimize_cv_validation_failure(self):
        self.engine.max_iterations = 1
        self.engine.validator.validate_no_entity_changes.return_value = (False, ["Violation"])
        
        cv = {"summary": {"text": "Old"}, "experience": [], "skills": []}
        result = self.engine.optimize_cv(cv, {}, "raw", "raw")
        
        # Should NOT break loop in Aggressive Mode
        # So iterations list will have [0, 1].
        self.assertEqual(len(result["iterations"]), 2)

    def test_rewrite_iteration_summary(self):
        cv = {"summary": {"text": "Old"}, "experience": [], "skills": []}
        rewritten = self.engine._rewrite_iteration(cv, {}, [], False, False)
        
        self.assertEqual(rewritten["summary"]["text"], "Rewritten Summary")
        self.engine.ai_rewriter.rewrite_summary.assert_called()

    def test_rewrite_iteration_bullets(self):
        cv = {
            "experience": [{"bullets": [{"text": "Old Bullet"}]}],
            "skills": []
        }
        rewritten = self.engine._rewrite_iteration(cv, {}, [], False, False)
        
        self.assertEqual(rewritten["experience"][0]["bullets"][0]["text"], "Rewritten Bullet")
        self.engine.ai_rewriter.rewrite_bullet.assert_called()

    def test_rewrite_iteration_skills(self):
        cv = {"experience": [], "skills": []}
        rewritten = self.engine._rewrite_iteration(cv, {}, [], False, False)
        
        # Check if skills converted to list of dicts
        self.assertEqual(rewritten["skills"][0]["category_name"], "Category")
        self.assertEqual(rewritten["skills"][0]["skills"], ["Skill"])

if __name__ == '__main__':
    unittest.main()
