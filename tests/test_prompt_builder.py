import unittest
from modules.prompt_builder import PromptBuilder

class TestPromptBuilder(unittest.TestCase):
    def setUp(self):
        self.jd_enhanced = {
            "key_responsibilities": ["Resp 1", "Resp 2", "Resp 3", "Resp 4"],
            "role_summary": "Role Summary Text",
            "required_skills": ["Skill A", "Skill B"],
            "preferred_skills": ["Skill C", "Skill D"]
        }
        self.missing_keywords = [f"Missing {i}" for i in range(20)]
        self.used_words = {f"Used {i}" for i in range(60)}
        self.pb = PromptBuilder(self.jd_enhanced, self.missing_keywords, self.used_words)

    def test_init(self):
        self.assertEqual(self.pb.jd, self.jd_enhanced)
        self.assertEqual(self.pb.missing_keywords, self.missing_keywords)
        self.assertEqual(self.pb.used_words, self.used_words)
        
        pb_none = PromptBuilder(self.jd_enhanced, self.missing_keywords)
        self.assertEqual(pb_none.used_words, set())

    def test_build_summary_prompt(self):
        prompt = self.pb.build_summary_prompt("Original Summary")
        self.assertIn("Resp 1", prompt)
        self.assertIn("Resp 3", prompt)
        self.assertIn("Original Summary", prompt)
        # Check slicing
        self.assertIn("Missing 9", prompt)
        self.assertNotIn("Missing 10", prompt) # Sliced to 10

    def test_build_bullet_prompt(self):
        relevant_keywords = ["KW1", "KW2", "KW3", "KW4", "KW5", "KW6"]
        prompt = self.pb.build_bullet_prompt("Original Bullet", relevant_keywords)
        self.assertIn("Original Bullet", prompt)
        self.assertIn("Role Summary Text", prompt)
        self.assertIn("KW1", prompt)
        # Check slicing
        self.assertIn("KW5", prompt) # Sliced to 5 for relevant_keywords
        self.assertNotIn("KW6", prompt)
        
        # Check used_words slicing (limit 50)
        # Since set order is not guaranteed, we just check it's in there
        # but we can check if it runs without error.
        pass

    def test_build_skills_prompt(self):
        original_skills = [{"skills": ["Old Skill 1", "Old Skill 2"]}, {"skills": ["Old Skill 3"]}]
        prompt = self.pb.build_skills_prompt(original_skills, "Experience Summary Text")
        self.assertIn("Old Skill 1", prompt)
        self.assertIn("Skill A", prompt)
        self.assertIn("Missing 0", prompt)
        # Check slicing
        self.assertIn("Missing 14", prompt)
        self.assertNotIn("Missing 15", prompt) # Sliced to 15

    def test_missing_optional_keys(self):
        jd_empty = {}
        pb = PromptBuilder(jd_empty, [], set())
        
        # Should not crash
        summary_prompt = pb.build_summary_prompt("Summary")
        self.assertIsInstance(summary_prompt, str)
        
        bullet_prompt = pb.build_bullet_prompt("Bullet", [])
        self.assertIsInstance(bullet_prompt, str)
        
        skills_prompt = pb.build_skills_prompt([], "Exp")
        self.assertIsInstance(skills_prompt, str)

if __name__ == '__main__':
    unittest.main()
