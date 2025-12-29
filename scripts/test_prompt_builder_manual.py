import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.prompt_builder import PromptBuilder

def test_manual():
    print("Starting manual test...")
    
    # Mock data
    jd_enhanced = {
        "key_responsibilities": ["Resp 1", "Resp 2", "Resp 3", "Resp 4"],
        "role_summary": "Role Summary Text",
        "required_skills": ["Skill A", "Skill B"],
        "preferred_skills": ["Skill C", "Skill D"]
    }
    missing_keywords = [f"Missing {i}" for i in range(20)]
    used_words = {f"Used {i}" for i in range(60)}
    
    pb = PromptBuilder(jd_enhanced, missing_keywords, used_words)
    
    # Test Summary Prompt
    print("\n--- Summary Prompt ---")
    summary_prompt = pb.build_summary_prompt("Original Summary")
    print(summary_prompt[:100] + "...")
    assert "Resp 1" in summary_prompt
    assert "Resp 3" in summary_prompt
    assert "Missing 0" in summary_prompt
    
    # Test Bullet Prompt
    print("\n--- Bullet Prompt ---")
    relevant_keywords = ["KW1", "KW2", "KW3", "KW4", "KW5", "KW6"]
    bullet_prompt = pb.build_bullet_prompt("Original Bullet", relevant_keywords)
    print(bullet_prompt[:100] + "...")
    assert "Original Bullet" in bullet_prompt
    assert "Role Summary Text" in bullet_prompt
    assert "KW1" in bullet_prompt
    
    # Test Skills Prompt
    print("\n--- Skills Prompt ---")
    original_skills = [{"skills": ["Old Skill 1", "Old Skill 2"]}, {"skills": ["Old Skill 3"]}]
    skills_prompt = pb.build_skills_prompt(original_skills, "Experience Summary Text")
    print(skills_prompt[:100] + "...")
    assert "Old Skill 1" in skills_prompt
    assert "Skill A" in skills_prompt
    assert "Missing 0" in skills_prompt
    
    print("\nManual test passed!")

if __name__ == "__main__":
    test_manual()
