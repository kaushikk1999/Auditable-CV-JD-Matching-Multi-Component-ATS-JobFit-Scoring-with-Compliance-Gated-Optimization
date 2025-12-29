import json
import google.generativeai as genai
from config.settings import GEMINI_API_KEY, GEMINI_MODEL
from config.prompts import JD_EXTRACTION_PROMPT

class GeminiClient:
    """Wrapper for Google Gemini API calls."""
    
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found in environment")
        
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel(GEMINI_MODEL)
    
    def extract_jd_structure(self, jd_text: str) -> dict:
        """
        Uses Gemini to extract structured fields from job description.
        
        Returns:
            Dictionary with 11+ structured fields
        """
        prompt = JD_EXTRACTION_PROMPT.format(jd_text=jd_text)
        
        try:
            response = self.model.generate_content(prompt)
            raw_text = response.text.strip()
            
            # Remove markdown code fences if present
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.startswith("```"):
                raw_text = raw_text[3:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
            
            parsed = json.loads(raw_text.strip())
            return self._validate_structure(parsed)
        
        except json.JSONDecodeError as e:
            raise ValueError(f"Gemini returned invalid JSON: {e}")
        except Exception as e:
            raise RuntimeError(f"Gemini API error: {e}")
    
    @staticmethod
    def _validate_structure(data: dict) -> dict:
        """Ensure all required keys exist."""
        required_keys = [
            "job_title", "company_name", "location", "work_type",
            "experience_required", "company_overview", "role_summary",
            "key_responsibilities", "required_skills", "preferred_skills",
            "education", "soft_skills", "diversity_statement",
            "recruiter_contact", "ats_keywords"
        ]
        
        list_fields = [
            "key_responsibilities", "required_skills", "preferred_skills",
            "soft_skills", "ats_keywords"
        ]
        
        for key in required_keys:
            if key not in data:
                if key in list_fields:
                    data[key] = []
                else:
                    data[key] = "Not specified"
        
        return data
