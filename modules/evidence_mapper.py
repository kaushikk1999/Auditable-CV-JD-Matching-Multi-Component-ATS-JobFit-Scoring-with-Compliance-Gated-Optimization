"""
Evidence Mapper - Map JD keywords to CV proof with domain guardrails.

This module implements Step 0B of the evidence-grounded 90+ system.
Finds evidence in CV for each keyword, blocks false matches.
"""
from typing import List, Dict, Set, Optional, Tuple
from pydantic import BaseModel, Field
import re
from rapidfuzz import fuzz
from dataclasses import dataclass

class EvidenceEntry(BaseModel):
    """Evidence for a single keyword in the CV."""
    
    keyword: str = Field(..., description="The keyword being checked")
    has_evidence: bool = Field(..., description="Whether evidence exists")
    snippets: List[str] = Field(default_factory=list, description="Matching text snippets from CV")
    locations: List[str] = Field(default_factory=list, description="CV sections where found")
    confidence: float = Field(default=0.0, description="Evidence quality 0.0-1.0")
    evidence_type: str = Field(default="none", description="exact | synonym | contextual | none")
    blocked_by_false_friend: bool = Field(default=False, description="Blocked by domain guardrails")


# Domain-specific false friend mappings
DOMAIN_FALSE_FRIENDS = {
    "science": {
        "block": ["data science", "computer science", "data scientist"],
        "allow_if_context": ["tutoring", "teaching", "education", "students", "grades"]
    },
    "math": {
        "block": ["mathematical optimization", "mathematics (computer science)", "algorithm design"],
        "allow_if_context": ["tutoring", "teaching", "grades", "students", "arithmetic"]
    },
    "mathematics": {
        "block": ["mathematical optimization", "computational mathematics"],
        "allow_if_context": ["tutoring", "teaching", "grades", "students"]
    },
    "teaching": {
        "block": ["machine learning", "machine teaching", "model training"],
        "allow_if_context": []  # No context can save "machine learning" for "teaching"
    },
    "tutor": {
        "block": ["tutorial", "tutoring system (software)"],
        "allow_if_context": ["students", "online", "lessons"]
    },
    "tutoring": {
        "block": ["tutorial"],
        "allow_if_context": ["students", "education"]
    }
}


class EvidenceMapper:
    """Map JD keywords to CV evidence with domain guardrails."""
    
    def __init__(self, similarity_threshold: float = 0.88):
        """
        Args:
            similarity_threshold: Minimum fuzzy match score for synonyms (0-1)
        """
        self.similarity_threshold = similarity_threshold
    
    def build_evidence_map(
        self, 
        cv_text: str, 
        keywords: List[str],
        cv_structured: Optional[Dict] = None
    ) -> Dict[str, EvidenceEntry]:
        """
        Build evidence map for all keywords.
        
        Args:
            cv_text: Raw CV text
            keywords: List of keywords to check
            cv_structured: Optional structured CV dict for section-specific checks
        
        Returns:
            Dict mapping each keyword to its EvidenceEntry
        """
        evidence_map = {}
        
        for keyword in keywords:
            evidence = self._find_evidence_for_keyword(cv_text, keyword, cv_structured)
            evidence_map[keyword] = evidence
        
        return evidence_map
    
    def _find_evidence_for_keyword(
        self, 
        cv_text: str, 
        keyword: str,
        cv_structured: Optional[Dict]
    ) -> EvidenceEntry:
        """
        Find evidence for a single keyword.
        
        Checks in order:
        1. Domain guardrails (false friends)
        2. Exact match (case-insensitive)
        3. Synonym match (fuzzy ≥88%)
        4. Contextual match (related terms in same sentence)
        """
        keyword_lower = keyword.lower()
        cv_lower = cv_text.lower()
        
        # Step 1: Check domain guardrails
        is_false_friend, reason = self._check_false_friend(keyword, cv_text)
        if is_false_friend:
            return EvidenceEntry(
                keyword=keyword,
                has_evidence=False,
                confidence=0.0,
                evidence_type="none",
                blocked_by_false_friend=True,
                snippets=[f"Blocked: {reason}"]
            )
        
        # Step 2: Exact match
        if keyword_lower in cv_lower:
            snippets, locations = self._extract_snippets(cv_text, keyword, cv_structured)
            return EvidenceEntry(
                keyword=keyword,
                has_evidence=True,
                snippets=snippets,
                locations=locations,
                confidence=1.0,
                evidence_type="exact"
            )
        
        # Step 3: Synonym / fuzzy match (for multi-word phrases)
        if len(keyword.split()) >= 2:
            fuzzy_match, match_text, score = self._fuzzy_match(cv_text, keyword)
            if fuzzy_match:
                snippets, locations = self._extract_snippets(cv_text, match_text, cv_structured)
                return EvidenceEntry(
                    keyword=keyword,
                    has_evidence=True,
                    snippets=snippets,
                    locations=locations,
                    confidence=score / 100.0,
                    evidence_type="synonym"
                )
        
        # Step 4: Contextual match (keyword components appear together)
        contextual_match, context_snippets = self._contextual_match(cv_text, keyword)
        if contextual_match:
            _, locations = self._extract_snippets(cv_text, keyword, cv_structured, use_context=True)
            return EvidenceEntry(
                keyword=keyword,
                has_evidence=True,
                snippets=context_snippets,
                locations=locations,
                confidence=0.6,
                evidence_type="contextual"
            )
        
        # No evidence found
        return EvidenceEntry(
            keyword=keyword,
            has_evidence=False,
            confidence=0.0,
            evidence_type="none"
        )
    
    def _check_false_friend(self, keyword: str, cv_text: str) -> Tuple[bool, str]:
        """
        Check if keyword matches a false friend pattern.
        
        Returns:
            (is_false_friend: bool, reason: str)
        """
        keyword_lower = keyword.lower()
        cv_lower = cv_text.lower()
        
        # Check if this keyword has false friend rules
        if keyword_lower not in DOMAIN_FALSE_FRIENDS:
            return False, ""
        
        rules = DOMAIN_FALSE_FRIENDS[keyword_lower]
        blocked_terms = rules["block"]
        context_terms = rules["allow_if_context"]
        
        # Check if any blocked term appears in CV
        for blocked in blocked_terms:
            if blocked.lower() in cv_lower:
                # Check if context can save it
                if context_terms:
                    has_context = any(ctx.lower() in cv_lower for ctx in context_terms)
                    if has_context:
                        return False, ""  # Context saves it
                
                # Blocked with no saving context
                return True, f"Found '{blocked}' which is not evidence for '{keyword}'"
        
        return False, ""
    
    def _extract_snippets(
        self, 
        cv_text: str, 
        search_term: str,
        cv_structured: Optional[Dict],
        use_context: bool = False,
        max_snippets: int = 3
    ) -> Tuple[List[str], List[str]]:
        """
        Extract snippets containing the search term.
        
        Returns:
            (snippets: List[str], locations: List[str])
        """
        snippets = []
        locations = []
        
        # Split into sentences
        sentences = re.split(r'[.!?•]\s+', cv_text)
        
        search_lower = search_term.lower()
        
        for sentence in sentences:
            if search_lower in sentence.lower():
                # Extract ~100 char context
                snippet = sentence.strip()[:150]
                if snippet and snippet not in snippets:
                    snippets.append(snippet)
                    
                    # Determine location
                    location = self._determine_location(snippet, cv_structured)
                    if location and location not in locations:
                        locations.append(location)
                    
                    if len(snippets) >= max_snippets:
                        break
        
        return snippets, locations
    
    def _determine_location(self, snippet: str, cv_structured: Optional[Dict]) -> str:
        """Determine which CV section a snippet came from."""
        if not cv_structured:
            return "unknown"
        
        snippet_lower = snippet.lower()
        
        # Check summary
        summary = cv_structured.get("summary", "")
        if isinstance(summary, dict):
            summary = str(summary)
        if summary and snippet_lower in str(summary).lower():
            return "summary"
        
        # Check skills
        skills = cv_structured.get("skills", {})
        if isinstance(skills, dict):
            for category, skill_list in skills.items():
                skill_text = " ".join(str(s) for s in skill_list if skill_list).lower()
                if snippet_lower in skill_text:
                    return "skills"
        elif isinstance(skills, list):
            skill_text = " ".join(str(s) for s in skills).lower()
            if snippet_lower in skill_text:
                return "skills"
        
        # Check experience
        experiences = cv_structured.get("experience", [])
        for exp in experiences:
            exp_text = str(exp).lower()
            if snippet_lower in exp_text:
                return "experience"
        
        # Check projects
        projects = cv_structured.get("projects", [])
        for proj in projects:
            proj_text = str(proj).lower()
            if snippet_lower in proj_text:
                return "projects"
        
        return "other"
    
    def _fuzzy_match(self, cv_text: str, keyword: str) -> Tuple[bool, str, float]:
        """
        Find fuzzy matches for multi-word keywords.
        
        Uses token_set_ratio to handle word order variations.
        
        Returns:
            (match_found: bool, matched_text: str, similarity_score: float)
        """
        # Extract candidate phrases from CV (same length as keyword)
        keyword_words = keyword.split()
        kw_len = len(keyword_words)
        
        sentences = re.split(r'[.!?•]\s+', cv_text)
        
        best_score = 0
        best_match = ""
        
        for sentence in sentences:
            words = sentence.split()
            # Generate n-grams of same length as keyword
            for i in range(len(words) - kw_len + 1):
                phrase = " ".join(words[i:i+kw_len])
                
                # Use token_set_ratio (handles word order)
                score = fuzz.token_set_ratio(keyword.lower(), phrase.lower())
                
                if score > best_score:
                    best_score = score
                    best_match = phrase
        
        # Check if score meets threshold
        threshold_score = self.similarity_threshold * 100
        if best_score >= threshold_score:
            return True, best_match, best_score
        
        return False, "", 0.0
    
    def _contextual_match(self, cv_text: str, keyword: str) -> Tuple[bool, List[str]]:
        """
        Check if keyword components appear together in CV.
        
        For multi-word keywords, checks if words appear in same sentence.
        
        Returns:
            (match_found: bool, context_snippets: List[str])
        """
        # Only applies to multi-word keywords
        if len(keyword.split()) < 2:
            return False, []
        
        components = [w.lower() for w in keyword.split() if len(w) > 2]  # Skip short words
        
        if not components:
            return False, []
        
        sentences = re.split(r'[.!?•]\s+', cv_text)
        context_snippets = []
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            # Check if all components appear in this sentence
            if all(comp in sentence_lower for comp in components):
                context_snippets.append(sentence.strip()[:150])
                if len(context_snippets) >= 2:
                    break
        
        return len(context_snippets) > 0, context_snippets
    
    def get_allowed_keywords(self, evidence_map: Dict[str, EvidenceEntry], min_confidence: float = 0.6) -> List[str]:
        """
        Get keywords that have evidence above confidence threshold.
        
        Args:
            evidence_map: Evidence map from build_evidence_map()
            min_confidence: Minimum confidence threshold
        
        Returns:
            List of allowed keywords
        """
        return [
            kw for kw, ev in evidence_map.items()
            if ev.has_evidence and ev.confidence >= min_confidence
        ]
    
    def get_needs_confirmation(
        self, 
        evidence_map: Dict[str, EvidenceEntry],
        target_keywords: 'TargetKeywords'  # Forward reference
    ) -> List[str]:
        """
        Get high-importance keywords that need user confirmation.
        
        Returns keywords that:
        - Have no evidence
        - Are required or high-importance
        - Were not blocked by false friends
        
        Args:
            evidence_map: Evidence map
            target_keywords: TargetKeywords object with importance scores
        
        Returns:
            List of keywords needing confirmation
        """
        needs_confirmation = []
        
        for kw, ev in evidence_map.items():
            # Skip if has evidence
            if ev.has_evidence:
                continue
            
            # Skip if blocked by false friend
            if ev.blocked_by_false_friend:
                continue
            
            # Include if required
            if kw in target_keywords.required:
                needs_confirmation.append(kw)
            # Or if high importance score
            elif target_keywords.importance_scores.get(kw, 0) >= 70:
                needs_confirmation.append(kw)
        
        return needs_confirmation


# Convenience functions
def build_evidence_map(
    cv_text: str, 
    keywords: List[str],
    cv_structured: Optional[Dict] = None,
    similarity_threshold: float = 0.88
) -> Dict[str, EvidenceEntry]:
    """Build evidence map for keywords."""
    mapper = EvidenceMapper(similarity_threshold=similarity_threshold)
    return mapper.build_evidence_map(cv_text, keywords, cv_structured)

def get_allowed_keywords(evidence_map: Dict[str, EvidenceEntry], min_confidence: float = 0.6) -> List[str]:
    """Get keywords with evidence."""
    mapper = EvidenceMapper()
    return mapper.get_allowed_keywords(evidence_map, min_confidence)

def get_needs_confirmation(evidence_map: Dict[str, EvidenceEntry], target_keywords) -> List[str]:
    """Get keywords needing user confirmation."""
    mapper = EvidenceMapper()
    return mapper.get_needs_confirmation(evidence_map, target_keywords)
