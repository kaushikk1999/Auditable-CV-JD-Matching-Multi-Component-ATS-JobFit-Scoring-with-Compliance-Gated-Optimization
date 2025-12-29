import os
import sys
from dotenv import load_dotenv

# Load env vars
load_dotenv()

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.rewriting_engine import RewritingEngine
from modules.parsers import CVParser, JDParser
from modules.gemini_client import GeminiClient

def verify_perplexity():
    print("Starting Perplexity Verification...")
    
    # Check Config
    api_key = os.getenv("PERPLEXITY_API_KEY")
    provider = os.getenv("AI_PROVIDER")
    print(f"Provider: {provider}")
    print(f"API Key Present: {bool(api_key)}")
    
    if provider != "perplexity":
        print("WARNING: AI_PROVIDER is not set to 'perplexity'. Setting it manually for this test.")
        os.environ["AI_PROVIDER"] = "perplexity"

    # Load Test Data
    try:
        with open("test_cv.txt", "r") as f:
            cv_text = f.read()
        with open("test_jd.txt", "r") as f:
            jd_text = f.read()
    except FileNotFoundError:
        print("Error: Test files not found. Please create test_cv.txt and test_jd.txt")
        return

    # 1. Parse CV (Mocking structure for simplicity or using parser if available)
    # Since we don't have the full CV parser logic easily available without dependencies, 
    # let's construct a simple structured CV manually based on the text.
    cv_structured = {
        "contact_info": {
            "full_name": "KAUSHIK KARMAKAR",
            "email": "john.doe@example.com",
            "phone": "+1-555-0100",
            "linkedin": "linkedin.com/in/kaushik99",
            "github": "github.com/kaushikk1999"
        },
        "summary": {
            "text": "Coding Educator focused holistic technology development children, creating next generation technology leaders. Instructed 500+ international students Python programming coding logic, achieving 4.9/5 satisfaction rating."
        },
        "skills": [
            {"category_name": "Programming", "skills": ["Python", "Java", "Scratch"]},
            {"category_name": "Teaching", "skills": ["Curriculum Development", "Mentoring", "Online Teaching"]}
        ],
        "experience": [
            {
                "job_title": "Machine Learning Coach internship",
                "company_name": "Clevered",
                "start_date": "Sep 2024",
                "end_date": "Present",
                "bullets": [
                    {"text": "Conducted 100+ interactive online sessions, teaching Python concepts diverse student groups globally."},
                    {"text": "Adapted instructional methods suit learning styles, ensuring 100% concept clarity via visual aids."}
                ]
            }
        ],
        "projects": [],
        "certifications": [],
        "education": []
    }

    # 2. Parse JD (Using GeminiClient if needed, or manual structure)
    # We'll use a manual structure for the test to avoid Gemini dependency if possible, 
    # but the engine might need it. Let's try manual first.
    jd_enhanced = {
        "job_title": "AI / Data Science Trainer",
        "company_name": "Elmond Online Educational Services",
        "keywords": ["AI", "Machine Learning", "Data Science", "Python", "NLP", "Teaching", "Training"],
        "responsibilities": [
            "Record structured, topic-wise training videos",
            "Explain concepts clearly with real-time demos"
        ],
        "required_skills": ["AI", "ML", "DS", "NLP", "Python", "Teaching"],
        "preferred_skills": ["Video Editing", "Content Creation"],
        "soft_skills": ["Communication", "Patience"],
        "ats_keywords": ["AI", "Machine Learning", "Data Science", "Python", "NLP"],
        "experience_required": "Training/teaching experience preferred",
        "keyword_taxonomy": {
            "technical_skills": ["AI", "ML", "DS", "NLP", "Python"],
            "soft_skills": ["Teaching", "Communication"],
            "tools_technologies": ["Zoom", "LMS"],
            "industry_keywords": ["EdTech", "Education"]
        }
    }

    # 3. Initialize Engine
    print("\nInitializing RewritingEngine...")
    engine = RewritingEngine(max_iterations=2, target_score=80.0)
    
    # Check if it's using Perplexity
    if hasattr(engine, 'ai_rewriter'):
        print(f"Engine Rewriter Type: {type(engine.ai_rewriter)}")
        from modules.perplexity_rewriter import PerplexityRewriter
        if isinstance(engine.ai_rewriter, PerplexityRewriter):
            print("✅ Engine is correctly using PerplexityRewriter")
        else:
            print("❌ Engine is NOT using PerplexityRewriter")
            return
    else:
        print("❌ Engine does not have ai_rewriter attribute")
        return

    # Wrap in SimpleNamespace to mimic Pydantic objects
    # Wrap in custom class to mimic Pydantic objects (attr access) AND dicts (.get)
    class MockModel:
        def __init__(self, d):
            for k, v in d.items():
                if isinstance(v, dict):
                    setattr(self, k, MockModel(v))
                elif isinstance(v, list):
                    setattr(self, k, [MockModel(i) if isinstance(i, dict) else i for i in v])
                else:
                    setattr(self, k, v)
            self._data = d
            
        def get(self, key, default=None):
            return self._data.get(key, default)
            
        def __getitem__(self, key):
             return self._data[key]
             
        def __contains__(self, key):
            return key in self._data
            
        def __iter__(self):
            return iter(self._data)
            
        def __setitem__(self, key, value):
            self._data[key] = value

    def dict_to_obj(d):
        if isinstance(d, dict):
            return MockModel(d)
        elif isinstance(d, list):
            return [dict_to_obj(i) for i in d]
        else:
            return d

    cv_obj = dict_to_obj(cv_structured)
    jd_obj = dict_to_obj(jd_enhanced)

    # 4. Run Optimization
    print("\nRunning Optimization (this calls the API)...")
    try:
        result = engine.optimize_cv(
            cv_obj, jd_obj,
            cv_text, jd_text,
            rewrite_projects=False,
            rewrite_certificates=False
        )
        
        print("\nOptimization Complete!")
        print(f"Initial Scores: {result['iterations'][0]['ats_score']} / {result['iterations'][0]['jobfit_score']}")
        print(f"Final Scores: {result['iterations'][-1]['ats_score']} / {result['iterations'][-1]['jobfit_score']}")
        
        final_summary = result['final_cv']['summary']['text']
        print(f"\nRewritten Summary Preview:\n{final_summary[:100]}...")
        
        if result['iterations'][-1]['ats_score'] > 0:
             print("\n✅ Verification SUCCESS: Perplexity API returned valid results.")
        else:
             print("\n❌ Verification FAILED: Scores are 0.")

    except Exception as e:
        print(f"\n❌ Verification FAILED with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_perplexity()
