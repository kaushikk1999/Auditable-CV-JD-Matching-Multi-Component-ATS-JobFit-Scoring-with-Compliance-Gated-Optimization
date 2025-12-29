from typing import List, Dict, Set, Tuple
from modules.schemas import (
    StructuredCV, EnhancedJD, GapAnalysisResult, KeywordMatch,
    ExperienceAlignment, KeywordCoverageTable, AnalysisReport
)
from rapidfuzz import fuzz
from datetime import datetime
import re
import uuid

class KeywordGapAnalyzer:
    """Analyzes keyword gaps between CV and JD."""
    
    def __init__(self, fuzzy_threshold: float = 80.0):
        """
        Args:
            fuzzy_threshold: Minimum similarity score (0-100) for fuzzy matches
        """
        self.fuzzy_threshold = fuzzy_threshold
    
    def analyze(self, cv: StructuredCV, jd: EnhancedJD) -> GapAnalysisResult:
        """
        Perform comprehensive gap analysis.
        
        Returns:
            GapAnalysisResult with Present/Missing/Irrelevant keywords
        """
        # Extract all keywords from JD
        jd_keywords = self._extract_jd_keywords(jd)
        
        # Extract all keywords from CV
        cv_keywords = self._extract_cv_keywords(cv)
        
        # Classify keywords
        present = []
        missing = []
        
        for jd_kw, priority in jd_keywords.items():
            match_result = self._find_keyword_in_cv(jd_kw, cv_keywords, cv)
            
            if match_result["found"]:
                present.append(KeywordMatch(
                    keyword=jd_kw,
                    found_in_cv=True,
                    cv_locations=match_result["locations"],
                    jd_priority=priority,
                    match_score=match_result["score"]
                ))
            else:
                missing.append(KeywordMatch(
                    keyword=jd_kw,
                    found_in_cv=False,
                    jd_priority=priority,
                    match_score=0.0
                ))
        
        # Find irrelevant CV keywords (not in JD)
        jd_keywords_lower = {k.lower() for k in jd_keywords.keys()}
        cv_keywords_lower = {k.lower() for k in cv_keywords.keys()}
        irrelevant = list(cv_keywords_lower - jd_keywords_lower)
        
        # Calculate coverage stats
        coverage_stats = self._calculate_coverage(present, missing, jd_keywords)
        
        return GapAnalysisResult(
            present_keywords=present,
            missing_keywords=missing,
            irrelevant_keywords=irrelevant,
            coverage_stats=coverage_stats
        )
    
    def _extract_jd_keywords(self, jd: EnhancedJD) -> Dict[str, str]:
        """
        Extract all keywords from JD with priority labels.
        
        Returns:
            Dict mapping keyword -> priority ("required", "preferred", "optional")
        """
        keywords = {}
        
        # Required skills
        for skill in jd.required_skills:
            keywords[skill] = "required"
        
        # Technical skills from taxonomy
        for skill in jd.keyword_taxonomy.technical_skills:
            if skill not in keywords:
                keywords[skill] = "required"
        
        # Tools/technologies
        for tool in jd.keyword_taxonomy.tools_technologies:
            if tool not in keywords:
                keywords[tool] = "required"
        
        # Preferred skills
        for skill in jd.preferred_skills:
            keywords[skill] = "preferred"
        
        # Soft skills (optional but valuable)
        for skill in jd.soft_skills:
            keywords[skill] = "optional"
        
        for skill in jd.keyword_taxonomy.soft_skills:
            if skill not in keywords:
                keywords[skill] = "optional"
        
        # ATS keywords
        for kw in jd.ats_keywords:
            if kw not in keywords:
                keywords[kw] = "required"
        
        return keywords
    
    def _extract_cv_keywords(self, cv: StructuredCV) -> Dict[str, List[str]]:
        """
        Extract all keywords from CV with location tracking.
        
        Returns:
            Dict mapping keyword -> list of locations
        """
        keywords = {}
        
        # Skills
        for skill_cat in cv.skills:
            for skill in skill_cat.skills:
                skill_lower = skill.lower()
                if skill_lower not in keywords:
                    keywords[skill_lower] = []
                keywords[skill_lower].append(f"skills_{skill_cat.category_name}")
        
        # Experience bullets
        for exp_idx, exp in enumerate(cv.experience):
            exp_text = f"{exp.job_title} {exp.company_name}"
            words = self._extract_significant_words(exp_text)
            for word in words:
                if word not in keywords:
                    keywords[word] = []
                keywords[word].append(f"experience_{exp_idx}_title")
            
            for bullet_idx, bullet in enumerate(exp.bullets):
                words = self._extract_significant_words(bullet.text)
                for word in words:
                    if word not in keywords:
                        keywords[word] = []
                    keywords[word].append(f"experience_{exp_idx}_bullet_{bullet_idx}")
        
        # Projects
        for proj_idx, proj in enumerate(cv.projects):
            for tech in proj.technologies:
                tech_lower = tech.lower()
                if tech_lower not in keywords:
                    keywords[tech_lower] = []
                keywords[tech_lower].append(f"project_{proj_idx}_tech")
        
        # Summary
        if cv.summary:
            words = self._extract_significant_words(cv.summary.text)
            for word in words:
                if word not in keywords:
                    keywords[word] = []
                keywords[word].append("summary")
        
        return keywords
    
    def _extract_significant_words(self, text: str) -> Set[str]:
        """Extract meaningful words (skip stopwords, min length 3)."""
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        # Basic stopword filter
        stopwords = {'the', 'and', 'for', 'with', 'this', 'that', 'from', 'have', 'are', 'was', 'were'}
        return {w for w in words if w not in stopwords}
    
    def _find_keyword_in_cv(self, jd_keyword: str, cv_keywords: Dict, cv: StructuredCV) -> Dict:
        """
        Find keyword in CV using exact and fuzzy matching.
        
        Returns:
            {"found": bool, "locations": List[str], "score": float}
        """
        jd_kw_lower = jd_keyword.lower()
        
        # Exact match
        if jd_kw_lower in cv_keywords:
            return {
                "found": True,
                "locations": cv_keywords[jd_kw_lower],
                "score": 100.0
            }
        
        # Fuzzy match
        best_score = 0.0
        best_match_locations = []
        
        for cv_kw, locations in cv_keywords.items():
            score = fuzz.ratio(jd_kw_lower, cv_kw)
            if score > best_score and score >= self.fuzzy_threshold:
                best_score = score
                best_match_locations = locations
        
        if best_score >= self.fuzzy_threshold:
            return {
                "found": True,
                "locations": best_match_locations,
                "score": best_score
            }
        
        return {"found": False, "locations": [], "score": 0.0}
    
    def _calculate_coverage(self, present: List[KeywordMatch], 
                           missing: List[KeywordMatch],
                           all_jd_keywords: Dict[str, str]) -> Dict[str, float]:
        """Calculate keyword coverage statistics."""
        required_total = sum(1 for p in all_jd_keywords.values() if p == "required")
        required_present = sum(1 for kw in present if kw.jd_priority == "required")
        
        preferred_total = sum(1 for p in all_jd_keywords.values() if p == "preferred")
        preferred_present = sum(1 for kw in present if kw.jd_priority == "preferred")
        
        total_keywords = len(all_jd_keywords)
        total_present = len(present)
        
        return {
            "required_coverage": required_present / required_total if required_total > 0 else 0.0,
            "preferred_coverage": preferred_present / preferred_total if preferred_total > 0 else 0.0,
            "overall_coverage": total_present / total_keywords if total_keywords > 0 else 0.0,
            "required_present": required_present,
            "required_total": required_total,
            "preferred_present": preferred_present,
            "preferred_total": preferred_total
        }
    
    def build_coverage_table(self, gap_analysis: GapAnalysisResult, jd: EnhancedJD) -> List[KeywordCoverageTable]:
        """
        Build keyword coverage table for rewrite engine guidance.
        
        Returns:
            List of KeywordCoverageTable entries
        """
        table = []
        
        # Process present keywords
        for kw_match in gap_analysis.present_keywords:
            category = self._classify_keyword_category(kw_match.keyword, jd)
            table.append(KeywordCoverageTable(
                jd_keyword=kw_match.keyword,
                category=category,
                priority=kw_match.jd_priority,
                present_in_cv=True,
                current_frequency=len(kw_match.cv_locations),
                target_frequency=1,  # Already present, maintain
                suggested_sections=[]
            ))
        
        # Process missing keywords
        for kw_match in gap_analysis.missing_keywords:
            category = self._classify_keyword_category(kw_match.keyword, jd)
            suggested_sections = self._suggest_sections_for_keyword(kw_match.keyword, category)
            
            table.append(KeywordCoverageTable(
                jd_keyword=kw_match.keyword,
                category=category,
                priority=kw_match.jd_priority,
                present_in_cv=False,
                current_frequency=0,
                target_frequency=1,
                suggested_sections=suggested_sections
            ))
        
        return table
    
    def _classify_keyword_category(self, keyword: str, jd: EnhancedJD) -> str:
        """Classify keyword into category."""
        if keyword in jd.keyword_taxonomy.technical_skills:
            return "technical_skill"
        elif keyword in jd.keyword_taxonomy.tools_technologies:
            return "tool"
        elif keyword in jd.keyword_taxonomy.soft_skills or keyword in jd.soft_skills:
            return "soft_skill"
        elif keyword in jd.keyword_taxonomy.domain_knowledge:
            return "domain"
        else:
            return "general"
    
    def _suggest_sections_for_keyword(self, keyword: str, category: str) -> List[str]:
        """Suggest CV sections where keyword should be added."""
        if category == "technical_skill" or category == "tool":
            return ["skills", "experience_bullets"]
        elif category == "soft_skill":
            return ["summary", "experience_bullets"]
        elif category == "domain":
            return ["summary", "experience_bullets"]
        else:
            return ["experience_bullets"]


class ExperienceAligner:
    """Maps CV experiences to JD requirements."""
    
    def align(self, cv: StructuredCV, jd: EnhancedJD, gap_analysis: GapAnalysisResult) -> List[ExperienceAlignment]:
        """
        Calculate relevance score for each CV experience.
        
        Returns:
            List of ExperienceAlignment sorted by relevance (high to low)
        """
        alignments = []
        
        for exp_idx, exp in enumerate(cv.experience):
            # Calculate relevance based on keyword matches in this experience
            matched_keywords = self._find_matched_keywords_in_experience(
                exp_idx, gap_analysis.present_keywords
            )
            
            # Calculate relevance based on responsibility alignment
            matched_responsibilities = self._match_responsibilities(
                exp, jd.key_responsibilities
            )
            
            # Calculate per-bullet scores
            bullet_scores = self._score_bullets(exp, jd)
            
            # Overall relevance score
            relevance = self._calculate_relevance_score(
                matched_keywords, matched_responsibilities, bullet_scores
            )
            
            alignments.append(ExperienceAlignment(
                experience_index=exp_idx,
                job_title=exp.job_title,
                company_name=exp.company_name,
                relevance_score=relevance,
                matched_keywords=matched_keywords,
                matched_responsibilities=matched_responsibilities,
                bullet_scores=bullet_scores
            ))
        
        # Sort by relevance (descending)
        alignments.sort(key=lambda x: x.relevance_score, reverse=True)
        return alignments
    
    def _find_matched_keywords_in_experience(self, exp_idx: int, 
                                            present_keywords: List[KeywordMatch]) -> List[str]:
        """Find which JD keywords are present in this experience."""
        matched = []
        for kw_match in present_keywords:
            for location in kw_match.cv_locations:
                if location.startswith(f"experience_{exp_idx}"):
                    matched.append(kw_match.keyword)
                    break
        return matched
    
    def _match_responsibilities(self, exp, jd_responsibilities: List[str]) -> List[str]:
        """Match experience bullets to JD responsibilities using fuzzy matching."""
        matched = []
        
        for resp in jd_responsibilities:
            resp_lower = resp.lower()
            for bullet in exp.bullets:
                bullet_lower = bullet.text.lower()
                score = fuzz.partial_ratio(resp_lower, bullet_lower)
                if score >= 60:  # Lower threshold for responsibilities
                    matched.append(resp)
                    break
        
        return matched
    
    def _score_bullets(self, exp, jd: EnhancedJD) -> List[float]:
        """Score each bullet by keyword density and relevance."""
        scores = []
        
        # Get all JD keywords for reference
        all_jd_keywords = set()
        all_jd_keywords.update([s.lower() for s in jd.required_skills])
        all_jd_keywords.update([s.lower() for s in jd.keyword_taxonomy.technical_skills])
        all_jd_keywords.update([s.lower() for s in jd.keyword_taxonomy.tools_technologies])
        
        for bullet in exp.bullets:
            bullet_lower = bullet.text.lower()
            # Count keyword matches
            matches = sum(1 for kw in all_jd_keywords if kw in bullet_lower)
            # Normalize by bullet length (favor density)
            word_count = len(bullet.text.split())
            score = matches / max(word_count / 10, 1)  # Normalize to ~10 words
            scores.append(min(score, 1.0))  # Cap at 1.0
        
        return scores
    
    def _calculate_relevance_score(self, matched_keywords: List[str],
                                  matched_responsibilities: List[str],
                                  bullet_scores: List[float]) -> float:
        """Calculate overall relevance score for experience."""
        keyword_score = len(matched_keywords) * 0.4
        resp_score = len(matched_responsibilities) * 0.3
        bullet_avg = sum(bullet_scores) / len(bullet_scores) if bullet_scores else 0
        bullet_score = bullet_avg * 0.3
        
        return min(keyword_score + resp_score + bullet_score, 1.0)
