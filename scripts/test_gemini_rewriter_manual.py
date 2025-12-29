import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock google.generativeai before importing the module to avoid actual API calls during this check
# We just want to verify the class structure and logic, not the API key or quota.
# However, the user instructions asked for a "dry run" which might imply real calls if key is present.
# But since I don't know if the key is valid, I'll mock the network call part but allow the init to run.
# Actually, the init checks for API key presence. I should assume the environment has it or mock it.

from modules.gemini_rewriter import GeminiRewriter

def test_manual():
    print("Starting manual test for GeminiRewriter...")
    
    # Check if API key is present in env, if not, we can't instantiate without error unless we mock settings
    from config.settings import GEMINI_API_KEY
    
    if not GEMINI_API_KEY:
        print("WARNING: GEMINI_API_KEY not found in settings. Skipping instantiation test.")
        return

    try:
        # Instantiate
        rewriter = GeminiRewriter()
        print("Successfully instantiated GeminiRewriter.")
        
        # Mock the model.generate_content to avoid real API calls and costs
        # We want to test the cleaning logic.
        
        # 1. Test Summary Cleaning
        mock_response = MagicMock()
        mock_response.text = "```\nLine 1\nLine 2\nLine 3\n```"
        rewriter.model.generate_content = MagicMock(return_value=mock_response)
        
        summary = rewriter.rewrite_summary("test prompt")
        print(f"Rewritten Summary: {summary}")
        # Expecting "Line 1\nLine 2\nLine 3"
        assert summary == "Line 1\nLine 2\nLine 3"
        
        # 2. Test Bullet Cleaning (First line only)
        mock_response.text = "Bullet Line 1\nBullet Line 2"
        rewriter.model.generate_content = MagicMock(return_value=mock_response)
        
        bullet = rewriter.rewrite_bullet("test prompt")
        print(f"Rewritten Bullet: {bullet}")
        assert bullet == "Bullet Line 1"
        
        # 3. Test Skills JSON Cleaning
        mock_response.text = "```json\n{\"Category\": [\"Skill\"]}\n```"
        rewriter.model.generate_content = MagicMock(return_value=mock_response)
        
        skills = rewriter.rewrite_skills("test prompt")
        print(f"Rewritten Skills: {skills}")
        assert skills == {"Category": ["Skill"]}
        
        print("Manual test passed (with mocked API calls)!")
        
    except Exception as e:
        print(f"Manual test failed: {e}")
        raise

if __name__ == "__main__":
    test_manual()
