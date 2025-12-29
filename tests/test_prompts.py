import unittest
from config.prompts import JD_EXTRACTION_PROMPT, CV_STRUCTURE_EXTRACTION_PROMPT, JD_KEYWORD_TAXONOMY_PROMPT

class TestPrompts(unittest.TestCase):
    def test_jd_extraction_prompt_integrity(self):
        # Check if constant is a string
        self.assertIsInstance(JD_EXTRACTION_PROMPT, str)
        
        # Check for placeholder
        self.assertIn("{jd_text}", JD_EXTRACTION_PROMPT)
        
        # Check for some required keys to ensure integrity
        self.assertIn("job_title", JD_EXTRACTION_PROMPT)
        self.assertIn("key_responsibilities", JD_EXTRACTION_PROMPT)
        self.assertIn("ats_keywords", JD_EXTRACTION_PROMPT)
    
    def test_cv_structure_extraction_prompt_integrity(self):
        # Check if constant is a string and non-empty
        self.assertIsInstance(CV_STRUCTURE_EXTRACTION_PROMPT, str)
        self.assertGreater(len(CV_STRUCTURE_EXTRACTION_PROMPT), 0)
        
        # Check for required placeholder
        self.assertIn("{cv_text}", CV_STRUCTURE_EXTRACTION_PROMPT)
        
        # Check for JSON return instruction
        self.assertIn("Return ONLY valid JSON", CV_STRUCTURE_EXTRACTION_PROMPT)
        self.assertIn("no markdown", CV_STRUCTURE_EXTRACTION_PROMPT.lower())
        
        # Check for key schema components
        self.assertIn("contact_info", CV_STRUCTURE_EXTRACTION_PROMPT)
        self.assertIn("experience", CV_STRUCTURE_EXTRACTION_PROMPT)
        self.assertIn("education", CV_STRUCTURE_EXTRACTION_PROMPT)
        self.assertIn("CRITICAL RULES", CV_STRUCTURE_EXTRACTION_PROMPT)
    
    def test_jd_keyword_taxonomy_prompt_integrity(self):
        # Check if constant is a string and non-empty
        self.assertIsInstance(JD_KEYWORD_TAXONOMY_PROMPT, str)
        self.assertGreater(len(JD_KEYWORD_TAXONOMY_PROMPT), 0)
        
        # Check for required placeholder
        self.assertIn("{jd_text}", JD_KEYWORD_TAXONOMY_PROMPT)
        
        # Check for JSON return instruction
        self.assertIn("Return ONLY valid JSON", JD_KEYWORD_TAXONOMY_PROMPT)
        self.assertIn("no markdown", JD_KEYWORD_TAXONOMY_PROMPT.lower())
        
        # Check for key schema components
        self.assertIn("keyword_taxonomy", JD_KEYWORD_TAXONOMY_PROMPT)
        self.assertIn("must_have_requirements", JD_KEYWORD_TAXONOMY_PROMPT)
        self.assertIn("nice_to_have_requirements", JD_KEYWORD_TAXONOMY_PROMPT)
        self.assertIn("EXTRACTION RULES", JD_KEYWORD_TAXONOMY_PROMPT)

if __name__ == '__main__':
    unittest.main()

