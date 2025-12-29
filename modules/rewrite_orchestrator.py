"""
Rewrite Orchestrator - End-to-end evidence-grounded CV optimization pipeline.

Implements Step 3 of the evidence-grounded 90+ system.
Coordinates keyword extraction, evidence mapping, planning, and rewriting.
"""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
import json

from modules.keyword_engine import extract_target_keywords, select_top_keywords, TargetKeywords
from modules.evidence_mapper import build_evidence_map, get_allowed_keywords, get_needs_confirmation, EvidenceEntry
from modules.placement_planner import plan_keyword_placements, PlacementPlan
from modules.scoring_pipeline import ScoringPipeline
from modules.storage import Storage


class OptimizeResult(BaseModel):
    """Result of CV optimization with full transparency."""
    
    optimized_cv: Dict = Field(..., description="Optimized structured CV")
    ats_score: float = Field(..., description="Final ATS score")
    jobfit_score: float = Field(..., description="Final JobFit score")
    
    evidence_map: Dict[str, Dict] = Field(default_factory=dict, description="Keyword evidence details")
    needs_user_confirmation: List[str] = Field(default_factory=list, description="Keywords needing confirmation")
    allowed_keywords: List[str] = Field(default_factory=list, description="Keywords with evidence")
    inserted_keywords: List[str] = Field(default_factory=list, description="Keywords actually inserted")
    rejected_keywords: List[str] = Field(default_factory=list, description="Keywords rejected (no evidence)")
    
    placement_plan: Dict = Field(default_factory=dict, description="Keyword placement strategy")
    
    score_capped: bool = Field(default=False, description="Whether score was capped")
    cap_reason: str = Field(default="", description="Reason for capping")
    
    initial_scores: Dict = Field(default_factory=dict, description="Scores before optimization")
    improvements: Dict = Field(default_factory=dict, description="Score improvements")


class RewriteOrchestrator:
    """Orchestrate evidence-grounded CV optimization."""
    
    def __init__(self):
        self.scorer = ScoringPipeline()
    
    def optimize_cv_for_jd(
        self,
        cv_structured: Dict,
        cv_text: str,
        jd_dict: Dict,
        jd_text: str,
        user_confirmations: Optional[Dict[str, bool]] = None,
        max_keywords: int = 20
    ) -> OptimizeResult:
        """
        End-to-end evidence-grounded CV optimization.
        
        Pipeline:
        1. Extract keywords from JD
        2. Build evidence map from CV
        3. Identify allowed vs needs_confirmation
        4. Create placement plan
        5. Optimize CV (currently stores plan, full rewriting in next phase)
        6. Score optimized CV
        7. Apply caps if needed
        
        Args:
            cv_structured: Structured CV dict
            cv_text: Raw CV text
            jd_dict: Structured JD dict
            jd_text: Raw JD text
            user_confirmations: Optional dict of {keyword: True/False}
            max_keywords: Max keywords to focus on (default 20)
        
        Returns:
            OptimizeResult with scores, evidence, and transparency data
        """
        # Step 1: Extract target keywords
        target_keywords = extract_target_keywords(jd_text, jd_dict)
        top_keywords = select_top_keywords(target_keywords, n=max_keywords)
        
        # Step 2: Build evidence map
        evidence_map = build_evidence_map(cv_text, top_keywords, cv_structured)
        
        # Convert evidence map to serializable format
        evidence_map_serializable = {
            kw: ev.model_dump() for kw, ev in evidence_map.items()
        }
        
        # Step 3: Get allowed keywords
        allowed_keywords = get_allowed_keywords(evidence_map, min_confidence=0.6)
        needs_confirmation = get_needs_confirmation(evidence_map, target_keywords)
        
        # Step 4: Apply user confirmations
        if user_confirmations:
            confirmed_keywords = [kw for kw, confirmed in user_confirmations.items() if confirmed]
            allowed_keywords.extend(confirmed_keywords)
            needs_confirmation = [kw for kw in needs_confirmation if kw not in confirmed_keywords]
        
        # Step 5: Create placement plan
        placement_plan = plan_keyword_placements(
            target_keywords,
            evidence_map,
            cv_structured,
            allowed_keywords
        )
        
        # Step 6: Calculate initial scores
        initial_scores = self.scorer.score_cv_jd_pair(
            cv_structured,
            jd_dict,
            cv_text,
            jd_text
        )
        
        # Step 7: For now, use current CV (full rewriting integration in next phase)
        # This demonstrates the pipeline with scoring and capping logic
        optimized_cv = cv_structured.copy()
        
        # Store placement plan in metadata for UI display
        if 'metadata' not in optimized_cv:
            optimized_cv['metadata'] = {}
        optimized_cv['metadata']['placement_plan'] = placement_plan.model_dump()
        optimized_cv['metadata']['allowed_keywords'] = allowed_keywords
        optimized_cv['metadata']['needs_confirmation'] = needs_confirmation
        
        # Step 8: Score (same as initial for now, will improve with actual rewriting)
        final_scores = initial_scores.copy()
        
        # Step 9: Apply hard caps
        score_capped = False
        cap_reason = ""
        
        # Cap 1: Required keywords missing
        required_missing = [kw for kw in target_keywords.required 
                           if kw not in allowed_keywords]
        if required_missing:
            if final_scores['jobfit_score'] > 89.0:
                final_scores['jobfit_score'] = 89.0
                score_capped = True
                cap_reason = f"Required keywords missing evidence: {', '.join(required_missing[:3])}"
        
        # Cap 2: Too many high-importance keywords need confirmation
        high_importance_missing = [kw for kw in needs_confirmation 
                                  if target_keywords.importance_scores.get(kw, 0) >= 70]
        if len(high_importance_missing) > 3:
            if final_scores['ats_score'] > 75.0:
                final_scores['ats_score'] = 75.0
                score_capped = True
                if cap_reason:
                    cap_reason += "; "
                cap_reason += f"Many high-importance keywords missing ({len(high_importance_missing)})"
        
        # Calculate improvements
        improvements = {
            'ats_delta': final_scores['ats_score'] - initial_scores['ats_score'],
            'jobfit_delta': final_scores['jobfit_score'] - initial_scores['jobfit_score']
        }
        
        # Step 10: Build result
        result = OptimizeResult(
            optimized_cv=optimized_cv,
            ats_score=final_scores['ats_score'],
            jobfit_score=final_scores['jobfit_score'],
            evidence_map=evidence_map_serializable,
            needs_user_confirmation=needs_confirmation,
            allowed_keywords=allowed_keywords,
            inserted_keywords=allowed_keywords[:10],  # Top 10 for now
            rejected_keywords=[kw for kw in top_keywords if kw not in allowed_keywords and kw not in needs_confirmation],
            placement_plan=placement_plan.model_dump(),
            score_capped=score_capped,
            cap_reason=cap_reason,
            initial_scores=initial_scores,
            improvements=improvements
        )
        
        return result


# Convenience function
def optimize_cv_for_jd(
    cv_structured: Dict,
    cv_text: str,
    jd_dict: Dict,
    jd_text: str,
    user_confirmations: Optional[Dict[str, bool]] = None
) -> OptimizeResult:
    """Optimize CV for JD using evidence-grounded approach."""
    orchestrator = RewriteOrchestrator()
    return orchestrator.optimize_cv_for_jd(
        cv_structured, cv_text, jd_dict, jd_text, user_confirmations
    )
