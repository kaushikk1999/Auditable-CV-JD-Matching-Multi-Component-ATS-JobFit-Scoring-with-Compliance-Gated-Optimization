import json
from typing import Dict, Any
import google.generativeai as genai
from config.prompts import CV_STRUCTURE_EXTRACTION_PROMPT
from modules.schemas import StructuredCV
from pydantic import ValidationError

class CVStructurer:
    """Extracts structured sections from raw CV text using Gemini."""
    
    def __init__(self, gemini_model):
        """
        Args:
            gemini_model: Configured Gemini GenerativeModel instance
        """
        self.model = gemini_model
    
    def parse(self, cv_text: str) -> StructuredCV:
        """
        Parse raw CV text into structured sections.
        
        Args:
            cv_text: Raw CV text from Phase 1
            
        Returns:
            Validated StructuredCV object
            
        Raises:
            ValueError: If Gemini returns invalid JSON or schema validation fails
        """
        prompt = CV_STRUCTURE_EXTRACTION_PROMPT.format(cv_text=cv_text)
        
        try:
            response = self.model.generate_content(prompt)
            raw_text = self._clean_response(response.text)
            parsed_data = json.loads(raw_text)
            
            # Validate and construct Pydantic model
            structured_cv = StructuredCV(**parsed_data)
            return structured_cv
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Gemini returned invalid JSON: {e}\nRaw response: {response.text[:500]}")
        except ValidationError as e:
            raise ValueError(f"CV structure validation failed: {e}")
        except Exception as e:
            raise RuntimeError(f"CV structuring error: {e}")
    
    @staticmethod
    def _clean_response(text: str) -> str:
        """Remove markdown code fences from Gemini response."""
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()
    
    def validate_structure(self, structured_cv: StructuredCV) -> Dict[str, Any]:
        """
        Perform quality checks on extracted CV structure.
        
        Returns:
            Dictionary with validation results
        """
        issues = []
        warnings = []
        
        # Check for critical missing data
        if not structured_cv.contact_info.email:
            warnings.append("No email address found")
        
        if not structured_cv.experience:
            issues.append("No work experience found - CV must have at least one experience entry")
        
        # Check experience bullets
        total_bullets = sum(len(exp.bullets) for exp in structured_cv.experience)
        if total_bullets == 0:
            warnings.append("No experience bullets found - consider adding achievements")
        
        # Check skills
        if not structured_cv.skills:
            warnings.append("No skills section found")
        
        # Check education
        if not structured_cv.education:
            warnings.append("No education found")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "stats": {
                "experience_count": len(structured_cv.experience),
                "total_bullets": total_bullets,
                "project_count": len(structured_cv.projects),
                "skill_categories": len(structured_cv.skills),
                "certifications": len(structured_cv.certifications)
            }
        }
