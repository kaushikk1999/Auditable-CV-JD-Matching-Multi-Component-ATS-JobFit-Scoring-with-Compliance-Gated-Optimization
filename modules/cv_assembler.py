from typing import Dict, List, Optional
from datetime import datetime
import re

class CVAssembler:
    """Assembles final optimized CV from rewritten and preserved sections."""
    
    def __init__(self):
        self.section_order = [
            "contact_info",
            "summary",
            "skills",
            "experience",
            "projects",
            "education",
            "certifications"
        ]
    
    def assemble(self, optimized_cv: Dict, original_cv: Dict) -> Dict:
        """
        Merge optimized sections with preserved original sections.
        
        Args:
            optimized_cv: CV after Phase 6 rewriting
            original_cv: Original CV from Phase 2
        
        Returns:
            Final assembled CV dictionary
        """
        final_cv = {}
        
        # Contact info (always from original, never rewritten)
        final_cv["contact_info"] = original_cv.get("contact_info", {})
        
        # Summary (from optimized if present)
        final_cv["summary"] = optimized_cv.get("summary", original_cv.get("summary"))
        
        # Skills (from optimized if present)
        final_cv["skills"] = optimized_cv.get("skills", original_cv.get("skills", []))
        
        # Experience (merge: titles/companies/dates from original, bullets from optimized)
        final_cv["experience"] = self._merge_experience(
            optimized_cv.get("experience", []),
            original_cv.get("experience", [])
        )
        
        # Projects (from optimized if rewritten, else original)
        final_cv["projects"] = optimized_cv.get("projects", original_cv.get("projects", []))
        
        # Education (always from original, never rewritten)
        final_cv["education"] = original_cv.get("education", [])
        
        # Certifications (from optimized if reordered, else original)
        final_cv["certifications"] = optimized_cv.get(
            "certifications", 
            original_cv.get("certifications", [])
        )
        
        # Add metadata
        final_cv["metadata"] = {
            "assembled_at": datetime.now().isoformat(),
            "version": "1.0",
            "pipeline": "Phases 1-7 Complete"
        }
        
        return final_cv
    
    def _merge_experience(self, optimized_exp: List[Dict], 
                         original_exp: List[Dict]) -> List[Dict]:
        """
        Merge experience: preserve titles/companies/dates, use optimized bullets.
        """
        merged = []
        
        for opt_exp, orig_exp in zip(optimized_exp, original_exp):
            merged_entry = {
                # From original (never changed)
                "job_title": orig_exp.get("job_title"),
                "company_name": orig_exp.get("company_name"),
                "location": orig_exp.get("location"),
                "start_date": orig_exp.get("start_date"),
                "end_date": orig_exp.get("end_date"),
                
                # From optimized (rewritten bullets)
                "bullets": opt_exp.get("bullets", orig_exp.get("bullets", []))
            }
            merged.append(merged_entry)
        
        return merged
    
    def to_text(self, cv: Dict) -> str:
        """
        Convert structured CV to formatted plain text.
        
        Returns:
            ATS-friendly plain text CV
        """
        sections = []
        
        # Contact Info
        contact = cv.get("contact_info", {})
        sections.append(contact.get("full_name", "").upper())
        contact_line = " | ".join(filter(None, [
            contact.get("email"),
            contact.get("phone"),
            contact.get("location")
        ]))
        if contact_line:
            sections.append(contact_line)
        
        if contact.get("linkedin"):
            sections.append(f"LinkedIn: {contact['linkedin']}")
        if contact.get("github"):
            sections.append(f"GitHub: {contact['github']}")
        
        sections.append("")  # Blank line
        
        # Summary
        if cv.get("summary"):
            sections.append("PROFESSIONAL SUMMARY")
            sections.append(cv["summary"].get("text", ""))
            sections.append("")
        
        # Skills
        if cv.get("skills"):
            sections.append("TECHNICAL SKILLS")
            for skill_cat in cv["skills"]:
                cat_name = skill_cat.get("category_name", "Skills")
                skills = skill_cat.get("skills", [])
                sections.append(f"{cat_name}: {', '.join(skills)}")
            sections.append("")
        
        # Experience
        if cv.get("experience"):
            sections.append("PROFESSIONAL EXPERIENCE")
            for exp in cv["experience"]:
                # Header
                title_company = f"{exp.get('job_title')} | {exp.get('company_name')}"
                if exp.get("location"):
                    title_company += f" | {exp['location']}"
                sections.append(title_company)
                
                # Dates
                date_range = f"{exp.get('start_date')} – {exp.get('end_date')}"
                sections.append(date_range)
                
                # Bullets
                for bullet in exp.get("bullets", []):
                    sections.append(f"• {bullet.get('text', '')}")
                
                sections.append("")  # Blank line between experiences
        
        # Projects
        if cv.get("projects"):
            sections.append("PROJECTS")
            for proj in cv["projects"]:
                proj_name = proj.get("project_name", "")
                sections.append(proj_name)
                
                if proj.get("technologies"):
                    sections.append(f"Technologies: {', '.join(proj['technologies'])}")
                
                for bullet in proj.get("bullets", []):
                    sections.append(f"• {bullet.get('text', '')}")
                
                sections.append("")
        
        # Education
        if cv.get("education"):
            sections.append("EDUCATION")
            for edu in cv["education"]:
                degree_inst = f"{edu.get('degree')} | {edu.get('institution')}"
                sections.append(degree_inst)
                
                if edu.get("graduation_date"):
                    sections.append(f"Graduated: {edu['graduation_date']}")
                if edu.get("gpa"):
                    sections.append(f"GPA: {edu['gpa']}")
                
                sections.append("")
        
        # Certifications
        if cv.get("certifications"):
            sections.append("CERTIFICATIONS")
            for cert in cv["certifications"]:
                cert_line = f"{cert.get('name')} | {cert.get('issuer')}"
                if cert.get("date_obtained"):
                    cert_line += f" | {cert['date_obtained']}"
                sections.append(cert_line)
            sections.append("")
        
        return "\n".join(sections)
