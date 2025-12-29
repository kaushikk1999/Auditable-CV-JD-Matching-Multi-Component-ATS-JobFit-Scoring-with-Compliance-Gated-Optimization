"""
Placement Planner - Strategic keyword distribution for maximum ATS impact.

This module implements Step 0C of the evidence-grounded 90+ system.
Plans where each keyword should appear for optimal scoring.
"""
from typing import List, Dict, Set, Optional
from pydantic import BaseModel, Field
from modules.keyword_engine import TargetKeywords
from modules.evidence_mapper import EvidenceEntry

class PlacementPlan(BaseModel):
    """Strategic plan for keyword placement across CV sections."""
    
    headline_keywords: List[str] = Field(
        default_factory=list,
        description="Keywords for professional headline (2-4 max)"
    )
    summary_keywords: List[str] = Field(
        default_factory=list,
        description="Keywords for summary section (6-10 max)"
    )
    skills_keywords: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Keywords by skill category"
    )
    bullets_keywords: Dict[int, List[str]] = Field(
        default_factory=dict,
        description="Keywords per experience bullet (bullet_idx -> keywords)"
    )
    repetition_budget: Dict[str, int] = Field(
        default_factory=dict,
        description="Allowed repetitions per keyword (2-3x for must-haves)"
    )
    total_placements: int = Field(default=0, description="Total keyword placements planned")


class PlacementPlanner:
    """Plan strategic keyword placement for maximum ATS score."""
    
    # Keyword repetition limits
    REQUIRED_KEYWORD_REPS = (2, 3)   # Min 2, max 3 appearances
    PREFERRED_KEYWORD_REPS = (1, 2)  # Min 1, max 2 appearances
    
    # Section capacity limits
    HEADLINE_MAX = 4
    SUMMARY_MAX = 10
    BULLET_MAX = 2  # Keywords per bullet
    
    def __init__(self):
        pass
    
    def plan_keyword_placements(
        self,
        target_keywords: TargetKeywords,
        evidence_map: Dict[str, EvidenceEntry],
        cv_structured: Dict,
        allowed_keywords: List[str]
    ) -> PlacementPlan:
        """
        Create strategic placement plan for allowed keywords.
        
        Strategy:
        1. Headline: Role title + top 2-4 required keywords
        2. Summary: 6-10 high-importance keywords (mix required + preferred)
        3. Skills: All allowed skill-type keywords (categorized)
        4. Experience bullets: Distribute remaining keywords
        
        Args:
            target_keywords: Extracted JD keywords with importance scores
            evidence_map: Evidence for each keyword
            cv_structured: Structured CV dict
            allowed_keywords: Keywords that have evidence
        
        Returns:
            PlacementPlan with distribution across sections
        """
        plan = PlacementPlan()
        
        # Filter to only allowed keywords
        allowed_set = set(allowed_keywords)
        
        # Separate by type
        required_allowed = [kw for kw in target_keywords.required if kw in allowed_set]
        preferred_allowed = [kw for kw in target_keywords.preferred if kw in allowed_set]
        
        # Step 1: Plan headline (role title + top required)
        plan.headline_keywords = self._plan_headline(
            target_keywords.role_title,
            required_allowed,
            target_keywords.importance_scores
        )
        
        # Step 2: Plan summary (high-importance keywords)
        plan.summary_keywords = self._plan_summary(
            required_allowed,
            preferred_allowed,
            target_keywords.importance_scores,
            already_used=set(plan.headline_keywords)
        )
        
        # Step 3: Plan skills (skill-type keywords categorized)
        plan.skills_keywords = self._plan_skills(
            allowed_keywords,
            cv_structured.get("skills", {}),
            already_used=set(plan.headline_keywords) | set(plan.summary_keywords)
        )
        
        # Step 4: Plan experience bullets (remaining keywords)
        used_in_skills = set()
        for category_kws in plan.skills_keywords.values():
            used_in_skills.update(category_kws)
        
        plan.bullets_keywords = self._plan_bullets(
            required_allowed,
            preferred_allowed,
            cv_structured.get("experience", []),
            evidence_map,
            already_used=set(plan.headline_keywords) | set(plan.summary_keywords) | used_in_skills
        )
        
        # Step 5: Calculate repetition budget
        plan.repetition_budget = self._calculate_repetition_budget(
            required_allowed,
            preferred_allowed,
            plan
        )
        
        # Count total placements
        plan.total_placements = self._count_placements(plan)
        
        return plan
    
    def _plan_headline(
        self,
        role_title: str,
        required_keywords: List[str],
        importance_scores: Dict[str, int]
    ) -> List[str]:
        """
        Plan headline keywords.
        
        Format: "{Role Title} | {Keyword1}, {Keyword2}, {Keyword3}"
        
        Select top 2-4 required keywords for headline.
        """
        # Sort required by importance
        sorted_required = sorted(
            required_keywords,
            key=lambda k: importance_scores.get(k, 0),
            reverse=True
        )
        
        # Take top 2-4 (prefer shorter phrases for headline)
        headline_kws = []
        for kw in sorted_required:
            if len(headline_kws) >= self.HEADLINE_MAX:
                break
            # Prefer shorter keywords for headline (3 words or less)
            if len(kw.split()) <= 3:
                headline_kws.append(kw)
        
        # If we have less than 2, add longer ones
        if len(headline_kws) < 2:
            for kw in sorted_required:
                if kw not in headline_kws:
                    headline_kws.append(kw)
                    if len(headline_kws) >= 2:
                        break
        
        return headline_kws[:self.HEADLINE_MAX]
    
    def _plan_summary(
        self,
        required_keywords: List[str],
        preferred_keywords: List[str],
        importance_scores: Dict[str, int],
        already_used: Set[str]
    ) -> List[str]:
        """
        Plan summary keywords (6-10 high-importance).
        
        Prioritize:
        1. Required keywords not in headline
        2. High-scoring preferred keywords
        3. Mix to avoid repetition with headline
        """
        summary_kws = []
        
        # Add required keywords not in headline
        for kw in required_keywords:
            if kw not in already_used and len(summary_kws) < self.SUMMARY_MAX:
                summary_kws.append(kw)
        
        # Add high-scoring preferred
        preferred_sorted = sorted(
            [kw for kw in preferred_keywords if kw not in already_used],
            key=lambda k: importance_scores.get(k, 0),
            reverse=True
        )
        
        for kw in preferred_sorted:
            if len(summary_kws) >= self.SUMMARY_MAX:
                break
            summary_kws.append(kw)
        
        # Ensure minimum 6 keywords
        if len(summary_kws) < 6:
            # Add any remaining
            all_remaining = [kw for kw in (required_keywords + preferred_keywords)
                           if kw not in already_used and kw not in summary_kws]
            summary_kws.extend(all_remaining[:6 - len(summary_kws)])
        
        return summary_kws
    
    def _plan_skills(
        self,
        allowed_keywords: List[str],
        existing_skills: Dict[str, List],
        already_used: Set[str]
    ) -> Dict[str, List[str]]:
        """
        Plan skills section keywords.
        
        Categorizes keywords into:
        - Technical Skills
        - Soft Skills
        - Tools & Platforms
        - Domain Knowledge
        """
        skills_plan = {
            "Technical Skills": [],
            "Soft Skills": [],
            "Tools & Platforms": [],
            "Domain Knowledge": []
        }
        
        # Skill type indicators
        technical_indicators = ["programming", "language", "framework", "coding", "algorithm"]
        soft_indicators = ["communication", "leadership", "teaching", "mentoring", "collaboration"]
        tool_indicators = ["platform", "software", "system", "tool", "lms"]
        
        for kw in allowed_keywords:
            if kw in already_used:
                continue
            
            kw_lower = kw.lower()
            
            # Categorize
            if any(ind in kw_lower for ind in technical_indicators):
                skills_plan["Technical Skills"].append(kw)
            elif any(ind in kw_lower for ind in soft_indicators):
                skills_plan["Soft Skills"].append(kw)
            elif any(ind in kw_lower for ind in tool_indicators):
                skills_plan["Tools & Platforms"].append(kw)
            else:
                # Check if it's a pure skill term (single/double word, capitalized or technical)
                if len(kw.split()) <= 2 and (kw[0].isupper() or kw.lower() in ["python", "java", "math"]):
                    # Likely a skill
                    skills_plan["Technical Skills"].append(kw)
                else:
                    skills_plan["Domain Knowledge"].append(kw)
        
        # Remove empty categories
        skills_plan = {cat: kws for cat, kws in skills_plan.items() if kws}
        
        return skills_plan
    
    def _plan_bullets(
        self,
        required_keywords: List[str],
        preferred_keywords: List[str],
        experiences: List[Dict],
        evidence_map: Dict[str, EvidenceEntry],
        already_used: Set[str]
    ) -> Dict[int, List[str]]:
        """
        Plan keyword distribution across experience bullets.
        
        Strategy:
        - Max 2 keywords per bullet
        - Place keywords in bullets where evidence was found
        - Distribute evenly across experiences
        """
        bullets_plan = {}
        
        # Count total bullets
        total_bullets = 0
        bullet_to_exp = {}  # bullet_global_idx -> (exp_idx, bullet_local_idx)
        
        for exp_idx, exp in enumerate(experiences):
            exp_bullets = exp.get("bullets", [])
            for bullet_idx, _ in enumerate(exp_bullets):
                bullet_to_exp[total_bullets] = (exp_idx, bullet_idx)
                total_bullets += 1
        
        if total_bullets == 0:
            return bullets_plan
        
        # Get keywords not yet placed
        remaining = [kw for kw in (required_keywords + preferred_keywords)
                    if kw not in already_used]
        
        # Sort by importance (required first)
        remaining_sorted = sorted(
            remaining,
            key=lambda k: (
                1 if k in required_keywords else 0,  # Required first
                len(evidence_map.get(k, EvidenceEntry(keyword=k, has_evidence=False)).snippets)  # More evidence first
            ),
            reverse=True
        )
        
        # Distribute keywords
        current_bullet = 0
        for kw in remaining_sorted:
            # Find best bullet (where evidence exists, or next available)
            best_bullet = self._find_best_bullet_for_keyword(
                kw, evidence_map, bullet_to_exp, experiences, bullets_plan
            )
            
            if best_bullet is not None:
                if best_bullet not in bullets_plan:
                    bullets_plan[best_bullet] = []
                
                # Only add if under limit
                if len(bullets_plan[best_bullet]) < self.BULLET_MAX:
                    bullets_plan[best_bullet].append(kw)
            else:
                # Round-robin to next available bullet
                while current_bullet in bullets_plan and len(bullets_plan[current_bullet]) >= self.BULLET_MAX:
                    current_bullet += 1
                    if current_bullet >= total_bullets:
                        break
                
                if current_bullet < total_bullets:
                    if current_bullet not in bullets_plan:
                        bullets_plan[current_bullet] = []
                    bullets_plan[current_bullet].append(kw)
                    current_bullet += 1
        
        return bullets_plan
    
    def _find_best_bullet_for_keyword(
        self,
        keyword: str,
        evidence_map: Dict[str, EvidenceEntry],
        bullet_to_exp: Dict[int, tuple],
        experiences: List[Dict],
        current_plan: Dict[int, List[str]]
    ) -> Optional[int]:
        """Find the best bullet to place a keyword based on evidence location."""
        evidence = evidence_map.get(keyword)
        if not evidence or not evidence.snippets:
            return None
        
        # Check if any snippet matches an existing bullet
        for bullet_idx, (exp_idx, local_idx) in bullet_to_exp.items():
            if bullet_idx in current_plan and len(current_plan[bullet_idx]) >= self.BULLET_MAX:
                continue  # Bullet full
            
            exp = experiences[exp_idx]
            bullets = exp.get("bullets", [])
            if local_idx < len(bullets):
                bullet_text = str(bullets[local_idx])
                
                # Check if any evidence snippet is from this bullet
                for snippet in evidence.snippets:
                    if snippet[:50] in bullet_text or bullet_text[:50] in snippet:
                        return bullet_idx
        
        return None
    
    def _calculate_repetition_budget(
        self,
        required_keywords: List[str],
        preferred_keywords: List[str],
        plan: PlacementPlan
    ) -> Dict[str, int]:
        """
        Calculate how many times each keyword should appear.
        
        Required: 2-3x
        Preferred: 1-2x
        """
        budget = {}
        
        # Count current placements
        placements = {}
        
        for kw in plan.headline_keywords:
            placements[kw] = placements.get(kw, 0) + 1
        for kw in plan.summary_keywords:
            placements[kw] = placements.get(kw, 0) + 1
        for kws in plan.skills_keywords.values():
            for kw in kws:
                placements[kw] = placements.get(kw, 0) + 1
        for kws in plan.bullets_keywords.values():
            for kw in kws:
                placements[kw] = placements.get(kw, 0) + 1
        
        # Set budget
        for kw in required_keywords:
            current = placements.get(kw, 0)
            budget[kw] = max(self.REQUIRED_KEYWORD_REPS[0], min(current, self.REQUIRED_KEYWORD_REPS[1]))
        
        for kw in preferred_keywords:
            current = placements.get(kw, 0)
            budget[kw] = max(self.PREFERRED_KEYWORD_REPS[0], min(current, self.PREFERRED_KEYWORD_REPS[1]))
        
        return budget
    
    def _count_placements(self, plan: PlacementPlan) -> int:
        """Count total keyword placements in plan."""
        count = 0
        count += len(plan.headline_keywords)
        count += len(plan.summary_keywords)
        for kws in plan.skills_keywords.values():
            count += len(kws)
        for kws in plan.bullets_keywords.values():
            count += len(kws)
        return count


# Convenience function
def plan_keyword_placements(
    target_keywords: TargetKeywords,
    evidence_map: Dict[str, EvidenceEntry],
    cv_structured: Dict,
    allowed_keywords: List[str]
) -> PlacementPlan:
    """Create strategic placement plan."""
    planner = PlacementPlanner()
    return planner.plan_keyword_placements(
        target_keywords, evidence_map, cv_structured, allowed_keywords
    )
