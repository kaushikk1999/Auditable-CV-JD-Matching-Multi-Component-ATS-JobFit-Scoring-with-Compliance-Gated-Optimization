from typing import Dict, List
from config.word_lists import APPROVED_ACTION_VERBS
from modules.evidence_mapper import build_evidence_map, EvidenceEntry
import json

class PromptBuilder:
    """Builds parameterized Gemini prompts for CV rewriting."""
    
    def __init__(self, jd_enhanced: Dict, missing_keywords: List[str], 
                 used_words: set = None):
        self.jd = jd_enhanced
        self.missing_keywords = missing_keywords
        self.used_words = used_words or set()
    
    def build_summary_prompt(self, original_summary: str) -> str:
        """Build summary rewriting prompt."""
        from config.rewriting_prompts import SUMMARY_REWRITE_PROMPT
        
        # Top 3 JD requirements
        top_requirements = self.jd.get("key_responsibilities", [])[:3]
        
        # Sample action verbs
        action_verbs_sample = APPROVED_ACTION_VERBS[:20]
        
        # AGGRESSIVE MODE: No evidence filtering
        # Treat all missing keywords as allowed
        allowed_kws = self.missing_keywords[:15]
        forbidden_kws = []
        
        # Calculate minimum keywords to mandate
        min_keywords = max(3, len(allowed_kws) // 2)
        
        return SUMMARY_REWRITE_PROMPT.format(
            action_verbs=", ".join(action_verbs_sample),
            original_summary=original_summary,
            jd_requirements="\n".join(f"- {req}" for req in top_requirements),
            # Fabrication Mode parameters
            allowed_keywords=", ".join(allowed_kws),
            forbidden_keywords="None - You may fabricate details to fit keywords",
            evidence_snippets="AGGRESSIVE MODE: You are authorized to hallucinate/fabricate details to align with these keywords.",
            target_keyword_count=len(allowed_kws),
            min_keywords=min_keywords
        )
    
    def build_bullet_prompt(self, original_bullet: str, 
                           relevant_keywords: List[str]) -> str:
        """Build experience bullet rewriting prompt."""
        from config.rewriting_prompts import BULLET_REWRITE_PROMPT
        
        jd_focus = self.jd.get("role_summary", "")
        
        # AGGRESSIVE MODE: No evidence filtering
        allowed_kws = relevant_keywords[:8]
        forbidden_kws = []
        
        # Calculate minimum keywords
        min_keywords = min(3, len(allowed_kws)) if allowed_kws else 1
        
        return BULLET_REWRITE_PROMPT.format(
            action_verbs=", ".join(APPROVED_ACTION_VERBS[:30]),
            original_bullet=original_bullet,
            jd_focus_areas=jd_focus,
            # Fabrication Mode parameters
            allowed_keywords=", ".join(allowed_kws),
            forbidden_keywords="None - You may fabricate details",
            bullet_evidence="AGGRESSIVE MODE: You are authorized to hallucinate/fabricate details to align with these keywords. PRESERVE DATES AND TITLES.",
            min_keywords=min_keywords
        )
    
    def build_skills_prompt(self, original_skills: List[Dict],
                           experience_summary: str) -> str:
        """Build skills optimization prompt."""
        from config.rewriting_prompts import SKILLS_REWRITE_PROMPT
        
        # Flatten original skills
        original_skills_flat = []
        for cat in original_skills:
            original_skills_flat.extend(cat.get("skills", []))
        
        # AGGRESSIVE MODE: No evidence filtering
        allowed_skills = self.missing_keywords[:20]
        forbidden_skills = []
        
        return SKILLS_REWRITE_PROMPT.format(
            original_skills=", ".join(original_skills_flat),
            jd_required_skills=", ".join(self.jd.get("required_skills", [])),
            jd_preferred_skills=", ".join(self.jd.get("preferred_skills", [])),
            # Fabrication Mode parameters
            allowed_skills=", ".join(allowed_skills),
            forbidden_skills="None - You may add skills required by JD",
            skills_evidence="AGGRESSIVE MODE: Add JD skills even if not in original CV."
        )

    def build_project_prompt(self, project: Dict, target_keywords: List[str]) -> str:
        """Build project rewriting prompt."""
        from config.rewriting_prompts import PROJECT_REWRITE_PROMPT
        
        # Extract bullet texts from list of dicts
        bullets = project.get("bullets", [])
        bullet_texts = [b.get("text", "") if isinstance(b, dict) else str(b) for b in bullets]
        
        return PROJECT_REWRITE_PROMPT.format(
            project_name=project.get("project_name", ""),
            project_description=project.get("description", ""),
            project_technologies=", ".join(project.get("technologies", [])),
            project_bullets="; ".join(bullet_texts),
            jd_focus_areas=self.jd.get("role_summary", ""),
            target_keywords=", ".join(target_keywords[:5])
        )

    def build_certificate_prompt(self, certificates: List[Dict], target_keywords: List[str] = None) -> str:
        """Build certificate optimization prompt."""
        from config.rewriting_prompts import CERTIFICATE_REWRITE_PROMPT
        
        target_kws = target_keywords if target_keywords else []
        
        # Format certs for prompt
        certs_text = "\n".join([
            f"- {c.get('name', '')} ({c.get('issuer', '')}, {c.get('date', '')})"
            for c in certificates
        ])
        
        return CERTIFICATE_REWRITE_PROMPT.format(
            original_certificates=certs_text,
            jd_certifications=", ".join(self.jd.get("certifications", [])),
            target_keywords=", ".join(target_kws[:10])
        )
