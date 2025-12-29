import json
from typing import Dict
import google.generativeai as genai
from config.prompts import JD_KEYWORD_TAXONOMY_PROMPT
from modules.schemas import EnhancedJD, KeywordTaxonomy
from pydantic import ValidationError

class JDAnalyzer:
    """Enhances JD extraction with keyword taxonomy and requirement classification."""
    
    def __init__(self, gemini_model):
        self.model = gemini_model
    
    def enhance_jd(self, basic_jd: Dict, raw_jd_text: str) -> EnhancedJD:
        """
        Enhance basic JD structure from Phase 1 with taxonomy and requirements.
        
        Args:
            basic_jd: Dictionary from Phase 1 JD extraction
            raw_jd_text: Original JD text for re-analysis
            
        Returns:
            EnhancedJD with taxonomy and requirement levels
        """
        # Extract taxonomy and requirements
        taxonomy_data = self._extract_taxonomy(raw_jd_text)
        
        # Merge with Phase 1 data
        enhanced_data = {
            **basic_jd,
            **taxonomy_data
        }
        
        try:
            enhanced_jd = EnhancedJD(**enhanced_data)
            return enhanced_jd
        except ValidationError as e:
            raise ValueError(f"JD enhancement validation failed: {e}")
    
    def _extract_taxonomy(self, jd_text: str) -> Dict:
        """Extract keyword taxonomy and requirement levels using Gemini."""
        prompt = JD_KEYWORD_TAXONOMY_PROMPT.format(jd_text=jd_text)
        
        try:
            response = self.model.generate_content(prompt)
            raw_text = self._clean_response(response.text)
            taxonomy_data = json.loads(raw_text)
            return taxonomy_data
            
        except json.JSONDecodeError as e:
            # Fallback: return empty taxonomy
            return {
                "keyword_taxonomy": {
                    "technical_skills": [],
                    "tools_technologies": [],
                    "soft_skills": [],
                    "domain_knowledge": [],
                    "certifications": []
                },
                "must_have_requirements": [],
                "nice_to_have_requirements": []
            }
        except Exception as e:
            raise RuntimeError(f"Taxonomy extraction error: {e}")
    
    @staticmethod
    def _clean_response(text: str) -> str:
        """Remove markdown code fences."""
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()
    
    def get_all_keywords(self, enhanced_jd: EnhancedJD) -> list:
        """Flatten all keywords from taxonomy into a single list."""
        keywords = []
        tax = enhanced_jd.keyword_taxonomy
        
        keywords.extend(tax.technical_skills)
        keywords.extend(tax.tools_technologies)
        keywords.extend(tax.soft_skills)
        keywords.extend(tax.domain_knowledge)
        keywords.extend(tax.certifications)
        keywords.extend(enhanced_jd.ats_keywords)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = []
        for kw in keywords:
            kw_lower = kw.lower()
            if kw_lower not in seen:
                seen.add(kw_lower)
                unique_keywords.append(kw)
        
        return unique_keywords
