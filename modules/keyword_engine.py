"""
Keyword Engine - Extract and prioritize JD keywords for evidence-based optimization.

This module implements Step 0A of the evidence-grounded 90+ system.
Extracts, normalizes, and prioritizes keywords from job descriptions.
"""
from typing import List, Dict, Set, Optional
from pydantic import BaseModel, Field
import re
from collections import Counter

class TargetKeywords(BaseModel):
    """Structured representation of JD keywords with priorities."""
    
    role_title: str = Field(..., description="Job title from JD")
    required: List[str] = Field(default_factory=list, description="Required/must-have skills")
    preferred: List[str] = Field(default_factory=list, description="Nice-to-have skills")
    responsibilities: List[str] = Field(default_factory=list, description="Key responsibility terms")
    raw_all: List[str] = Field(default_factory=list, description="All extracted keywords")
    importance_scores: Dict[str, int] = Field(default_factory=dict, description="Keyword importance 0-100")


class KeywordEngine:
    """Extract, normalize, and prioritize JD keywords."""
    
    # Common section headers to identify keyword zones
    SECTION_HEADERS = {
        "required": ["required", "must have", "qualifications", "requirements", "essential"],
        "preferred": ["preferred", "nice to have", "desired", "bonus", "plus"],
        "responsibilities": ["responsibilities", "duties", "you will", "role involves"],
        "skills": ["skills", "technologies", "tools", "technical skills"]
    }
    
    # Stopwords to exclude from keywords (ATS-irrelevant terms)
    STOPWORDS = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "up", "about", "into", "through", "during",
        "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
        "do", "does", "did", "will", "would", "should", "could", "may", "might",
        "must", "can", "this", "that", "these", "those", "we", "you", "our", "your"
    }
    
    def __init__(self):
        pass
    
    def extract_target_keywords(self, jd_text: str, jd_dict: Optional[Dict] = None) -> TargetKeywords:
        """
        Extract and categorize keywords from JD text.
        
        Args:
            jd_text: Raw JD text
            jd_dict: Optional structured JD data (from Phase 1 parsing)
        
        Returns:
            TargetKeywords with categorized and scored keywords
        """
        # Extract role title
        role_title = self._extract_role_title(jd_text, jd_dict)
        
        # Extract keywords by section
        required_kws = self._extract_from_section(jd_text, "required", jd_dict)
        preferred_kws = self._extract_from_section(jd_text, "preferred", jd_dict)
        responsibilities_kws = self._extract_from_section(jd_text, "responsibilities", jd_dict)
        
        # Extract from structured data if available
        if jd_dict:
            required_kws.update(jd_dict.get("required_skills", []))
            preferred_kws.update(jd_dict.get("preferred_skills", []))
        
        # Combine and deduplicate
        raw_all = list(required_kws | preferred_kws | responsibilities_kws)
        
        # Normalize all keywords
        normalized_map = {self.normalize_keyword(kw): kw for kw in raw_all}
        
        # Score importance
        importance_scores = {}
        for norm_kw, orig_kw in normalized_map.items():
            score = self.score_keyword_importance(
                orig_kw, jd_text,
                is_required=(orig_kw in required_kws),
                is_preferred=(orig_kw in preferred_kws),
                is_in_title=(orig_kw.lower() in role_title.lower())
            )
            importance_scores[orig_kw] = score
        
        return TargetKeywords(
            role_title=role_title,
            required=sorted(required_kws, key=lambda k: importance_scores.get(k, 0), reverse=True),
            preferred=sorted(preferred_kws, key=lambda k: importance_scores.get(k, 0), reverse=True),
            responsibilities=list(responsibilities_kws),
            raw_all=raw_all,
            importance_scores=importance_scores
        )
    
    def _extract_role_title(self, jd_text: str, jd_dict: Optional[Dict]) -> str:
        """Extract job title from JD."""
        if jd_dict and "job_title" in jd_dict:
            return jd_dict["job_title"]
        
        # Heuristic: first 2-5 words often contain title
        lines = jd_text.strip().split('\n')
        for line in lines[:5]:
            line = line.strip()
            # Skip empty or very long lines (likely headers/descriptions)
            if 3 <= len(line.split()) <= 8:
                # Common title patterns
                if any(word in line.lower() for word in ["engineer", "developer", "manager", "analyst", "tutor", "specialist"]):
                    return line
        
        return lines[0].strip() if lines else "Unknown Role"
    
    def _extract_from_section(self, jd_text: str, section_type: str, jd_dict: Optional[Dict]) -> Set[str]:
        """
        Extract keywords from a specific section type.
        
        Args:
            jd_text: Full JD text
            section_type: "required", "preferred", or "responsibilities"
            jd_dict: Optional structured data
        
        Returns:
            Set of keywords from that section
        """
        keywords = set()
        
        # Use structured data if available
        if jd_dict and section_type == "required":
            keywords.update(jd_dict.get("required_skills", []))
        if jd_dict and section_type == "preferred":
            keywords.update(jd_dict.get("preferred_skills", []))
        
        # Also extract from raw text for robustness
        section_headers = self.SECTION_HEADERS.get(section_type, [])
        
        # Find section boundaries
        lines = jd_text.split('\n')
        in_section = False
        section_text = []
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Check if entering this section
            if any(header in line_lower for header in section_headers):
                in_section = True
                continue
            
            # Check if entering another section (exit current)
            if in_section:
                # Check for other section headers
                other_sections = [h for sec_type, headers in self.SECTION_HEADERS.items() 
                                 if sec_type != section_type for h in headers]
                if any(header in line_lower for header in other_sections):
                    break
                
                section_text.append(line)
        
        # Extract keywords from section text
        if section_text:
            section_content = '\n'.join(section_text)
            extracted = self._extract_keywords_from_text(section_content)
            keywords.update(extracted)
        
        return keywords
    
    def _extract_keywords_from_text(self, text: str) -> Set[str]:
        """
        Extract meaningful keywords from text using NLP heuristics.
        
        Extracts:
        - Multi-word technical terms (Python, Machine Learning, etc.)
        - Bullet point items
        - Repeated important terms
        """
        keywords = set()
        
        # Extract from bullet points
        bullet_pattern = r'[•\-\*]\s*(.+?)(?:\n|$)'
        bullets = re.findall(bullet_pattern, text)
        for bullet in bullets:
            # Clean and extract
            bullet = bullet.strip().rstrip('.,;:')
            if 2 <= len(bullet.split()) <= 6:  # Reasonable keyword length
                keywords.add(bullet)
        
        # Extract capitalized multi-word terms (likely technical terms or proper nouns)
        capitalized_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b'
        cap_terms = re.findall(capitalized_pattern, text)
        keywords.update(cap_terms)
        
        # Extract single capitalized words (technologies, tools)
        single_cap_pattern = r'\b([A-Z][a-z]{2,})\b'
        single_terms = re.findall(single_cap_pattern, text)
        keywords.update(single_terms)
        
        # Extract common skill patterns (X.js, X++, etc.)
        tech_pattern = r'\b(\w+(?:\.js|\.py|\.NET|\+\+|#))\b'
        tech_terms = re.findall(tech_pattern, text, re.IGNORECASE)
        keywords.update(tech_terms)
        
        # Extract frequent meaningful nouns (appearing 2+ times)
        words = re.findall(r'\b[a-z]{4,}\b', text.lower())
        word_freq = Counter(words)
        frequent = {word for word, count in word_freq.items() 
                   if count >= 2 and word not in self.STOPWORDS}
        keywords.update(frequent)
        
        # Filter out stopwords and clean
        cleaned = set()
        for kw in keywords:
            kw_clean = kw.strip().strip('.,;:()[]')
            if kw_clean and not all(word in self.STOPWORDS for word in kw_clean.lower().split()):
                cleaned.add(kw_clean)
        
        return cleaned
    
    def normalize_keyword(self, kw: str) -> str:
        """
        Normalize keyword for comparison.
        
        - Lowercase
        - Remove punctuation (except . in versions)
        - Strip whitespace
        - Preserve multi-word phrases
        """
        # Preserve dots in versions (Python 3.9, Node.js)
        normalized = kw.lower().strip()
        
        # Remove trailing punctuation (but not internal)
        normalized = normalized.strip('.,;:!?()[]{}')
        
        # Normalize whitespace
        normalized = ' '.join(normalized.split())
        
        return normalized
    
    def score_keyword_importance(
        self, 
        keyword: str, 
        jd_text: str,
        is_required: bool = False,
        is_preferred: bool = False,
        is_in_title: bool = False
    ) -> int:
        """
        Score keyword importance from 0-100.
        
        Factors:
        - Category: required (base 70) > preferred (base 50) > other (base 30)
        - In title: +20
        - Frequency in JD: +1 per occurrence (max +10)
        - Length: Multi-word technical terms +5
        
        Returns:
            Importance score 0-100
        """
        score = 0
        
        # Base score by category
        if is_required:
            score = 70
        elif is_preferred:
            score = 50
        else:
            score = 30
        
        # Title bonus
        if is_in_title:
            score += 20
        
        # Frequency bonus (max +10)
        kw_lower = keyword.lower()
        frequency = jd_text.lower().count(kw_lower)
        score += min(frequency, 10)
        
        # Multi-word technical term bonus
        if len(keyword.split()) >= 2:
            score += 5
        
        return min(score, 100)
    
    def select_top_keywords(self, target_keywords: TargetKeywords, n: int = 20) -> List[str]:
        """
        Select top N keywords by importance score.
        
        Ensures:
        - All required keywords included
        - Remaining slots filled by highest-scoring preferred/other
        
        Args:
            target_keywords: TargetKeywords object
            n: Maximum number of keywords to return
        
        Returns:
            List of top N keywords
        """
        # Always include all required
        top_keywords = list(target_keywords.required)
        
        # Fill remaining with highest-scoring preferred
        remaining_slots = n - len(top_keywords)
        if remaining_slots > 0:
            # Sort all others by score
            others = [kw for kw in target_keywords.raw_all if kw not in top_keywords]
            others_sorted = sorted(others, 
                                  key=lambda k: target_keywords.importance_scores.get(k, 0),
                                  reverse=True)
            
            top_keywords.extend(others_sorted[:remaining_slots])
        
        return top_keywords[:n]


# Convenience functions
def extract_target_keywords(jd_text: str, jd_dict: Optional[Dict] = None) -> TargetKeywords:
    """Extract target keywords from JD."""
    engine = KeywordEngine()
    return engine.extract_target_keywords(jd_text, jd_dict)

def normalize_keyword(kw: str) -> str:
    """Normalize keyword for comparison."""
    engine = KeywordEngine()
    return engine.normalize_keyword(kw)

def select_top_keywords(target_keywords: TargetKeywords, n: int = 20) -> List[str]:
    """Select top N most important keywords."""
    engine = KeywordEngine()
    return engine.select_top_keywords(target_keywords, n)
