import numpy as np
from typing import Dict, List
from modules.scoring_utils import build_ablation_rows
from modules.feature_extractor import FeatureExtractor


class JobFitScorer:
    """Computes Job-Compatibility score and sub-components."""

    def __init__(self, feature_extractor: FeatureExtractor):
        self.extractor = feature_extractor
        self.config = feature_extractor.config

    def score(self, cv_dict: Dict, jd_dict: Dict) -> Dict:
        """
        Compute full Job-Compatibility score.

        Returns:
            {
                "jobfit_score": float,  # [0, 100]
                "components": {
                    "summary_similarity": float,
                    "experience_alignment": float,
                    "skills_alignment": float,
                    "education_match": float,
                    "domain_relevance": float
                },
                "features": {...}
            }
        """
        # Component 1: Summary Similarity
        s_summary = self._summary_similarity(cv_dict, jd_dict)

        # Component 2: Experience-Responsibility Alignment
        a_exp = self._experience_alignment(cv_dict, jd_dict)

        # Component 3: Skills Alignment
        a_skills = self._skills_alignment(cv_dict, jd_dict)

        # Component 4: Education Match
        m_edu = self._education_match(cv_dict, jd_dict)

        # Component 5: Domain Relevance
        d_domain = self._domain_relevance(cv_dict, jd_dict)

        # Weighted combination
        weights = self.config.jobfit_weights
        jobfit_score = (
            weights.summary_similarity * s_summary +
            weights.experience_alignment * a_exp +
            weights.skills_alignment * a_skills +
            weights.education_match * m_edu +
            weights.domain_relevance * d_domain
        )

        # Convert to [0, 100]
        jobfit_score_100 = jobfit_score * 100

        # Prepare data for ablation helper
        components_0_1 = {
            "summary_similarity": s_summary,
            "experience_alignment": a_exp,
            "skills_alignment": a_skills,
            "education_match": m_edu,
            "domain_relevance": d_domain,
        }

        weights_dict = {
            "summary_similarity": float(weights.summary_similarity),
            "experience_alignment": float(weights.experience_alignment),
            "skills_alignment": float(weights.skills_alignment),
            "education_match": float(weights.education_match),
            "domain_relevance": float(weights.domain_relevance),
        }

        # Recalculate full score 0-1 from dicts to be sure
        jobfit_score_0_1 = sum(weights_dict[k] * components_0_1[k] for k in components_0_1)
        
        # Ablation table rows
        ablation_rows = build_ablation_rows(jobfit_score_0_1, components_0_1, weights_dict)

        return {
            "jobfit_score": jobfit_score_100,
            "components": {
                "summary_similarity": s_summary * 100,
                "experience_alignment": a_exp * 100,
                "skills_alignment": a_skills * 100,
                "education_match": m_edu * 100,
                "domain_relevance": d_domain * 100
            },
            "features": {},
            "ablation": ablation_rows
        }

    def _summary_similarity(self, cv_dict: Dict, jd_dict: Dict) -> float:
        """Component 1: CV summary ↔ JD role summary cosine similarity."""
        cv_summary_text = cv_dict.get("summary", {}).get("text", "")
        jd_summary_text = jd_dict.get("role_summary", "")

        if not cv_summary_text or not jd_summary_text:
            return 0.0

        cv_embed = self.extractor.embed_text(cv_summary_text)
        jd_embed = self.extractor.embed_text(jd_summary_text)

        similarity = self.extractor.cosine_similarity(cv_embed, jd_embed)

        # Shift from [-1, 1] to [0, 1]
        normalized = (similarity + 1) / 2
        return float(normalized)

    def _experience_alignment(self, cv_dict: Dict, jd_dict: Dict) -> float:
        """Component 2: Average max similarity between CV bullets and JD responsibilities."""
        # Extract CV experience bullets
        cv_bullets: List[str] = []
        for exp in cv_dict.get("experience", []) or []:
            for bullet in exp.get("bullets", []) or []:
                if isinstance(bullet, dict):
                    t = bullet.get("text", "")
                else:
                    t = str(bullet)
                t = (t or "").strip()
                if t:
                    cv_bullets.append(t)

        # Extract JD responsibilities
        jd_responsibilities = jd_dict.get("key_responsibilities", []) or []

        if not cv_bullets or not jd_responsibilities:
            return 0.0

        # Embed all texts
        cv_embeds = self.extractor.embed_texts(cv_bullets)
        jd_embeds = self.extractor.embed_texts(jd_responsibilities)

        # For each JD responsibility, find max similarity with CV bullets
        alignment_scores: List[float] = []

        for jd_embed in jd_embeds:
            max_sim = -1.0
            for cv_embed in cv_embeds:
                sim = self.extractor.cosine_similarity(cv_embed, jd_embed)
                if sim > max_sim:
                    max_sim = sim

            # Shift to [0, 1]
            max_sim_normalized = (max_sim + 1) / 2
            alignment_scores.append(float(max_sim_normalized))

        # Average alignment
        avg_alignment = float(np.mean(alignment_scores)) if alignment_scores else 0.0
        return avg_alignment

    def _skills_alignment(self, cv_dict: Dict, jd_dict: Dict) -> float:
        """Component 3: Weighted required/preferred skills match."""
        # Extract skills
        cv_skills = set()
        for skill_cat in cv_dict.get("skills", []) or []:
            for s in (skill_cat.get("skills", []) or []):
                if s is None:
                    continue
                cv_skills.add(str(s).lower())

        jd_required = set(str(s).lower() for s in (jd_dict.get("required_skills", []) or []) if s is not None)
        jd_preferred = set(str(s).lower() for s in (jd_dict.get("preferred_skills", []) or []) if s is not None)

        # Required match rate
        if jd_required:
            required_match_rate = len(jd_required & cv_skills) / len(jd_required)
        else:
            required_match_rate = 1.0

        # Preferred match rate
        if jd_preferred:
            preferred_match_rate = len(jd_preferred & cv_skills) / len(jd_preferred)
        else:
            preferred_match_rate = 1.0

        # Weighted combination (70% required, 30% preferred)
        alignment = 0.7 * required_match_rate + 0.3 * preferred_match_rate
        return float(alignment)

    def _education_match(self, cv_dict: Dict, jd_dict: Dict) -> float:
        """
        Component 4: Education level match.
        Supports both:
          - Single field: jd_dict['education']
          - Dual fields: jd_dict['education_required_text'] + jd_dict['education_preferred_text']
        """
        degree_levels = {
            "high school": 1,
            "associate": 2,
            "bachelor": 3,
            "master": 4,
            "phd": 5,
            "doctorate": 5
        }

        # Extract CV education
        cv_degrees = cv_dict.get("education", []) or []
        cv_max_level = 0

        for edu in cv_degrees:
            degree = (edu.get("degree", "") if isinstance(edu, dict) else str(edu)).lower()
            for key, level in degree_levels.items():
                if key in degree:
                    cv_max_level = max(cv_max_level, level)

        # Extract JD education requirement - support multiple field names
        jd_required_text = ""
        jd_preferred_text = ""
        
        # Try dual-field first (UI spec)
        if "education_required_text" in jd_dict:
            jd_required_text = str(jd_dict.get("education_required_text", "") or "").lower()
            jd_preferred_text = str(jd_dict.get("education_preferred_text", "") or "").lower()
        # Fall back to single field (old spec)
        elif "education" in jd_dict:
            jd_required_text = str(jd_dict.get("education", "") or "").lower()
        
        # Find required level
        jd_required_level = 0
        for key, level in degree_levels.items():
            if key in jd_required_text:
                jd_required_level = max(jd_required_level, level)
        
        # Find preferred level
        jd_preferred_level = 0
        for key, level in degree_levels.items():
            if key in jd_preferred_text:
                jd_preferred_level = max(jd_preferred_level, level)

        # Match logic
        # If no education requirement specified
        if jd_required_level == 0 and jd_preferred_level == 0:
            return 1.0  # No requirement = full match
        
        # If meets/exceeds required level
        if jd_required_level > 0 and cv_max_level >= jd_required_level:
            return 1.0
        
        # If meets preferred level (when no required, or one below required)
        if jd_preferred_level > 0 and cv_max_level >= jd_preferred_level:
            return 0.75
        
        # If one level below required
        if jd_required_level > 0 and cv_max_level == jd_required_level - 1:
            return 0.5
        
        # Significantly below
        return 0.0

    def _domain_relevance(self, cv_dict: Dict, jd_dict: Dict) -> float:
        """
        Component 5: Domain/industry relevance via embedding similarity.

        SPEC (paper-compliant):
            D_domain = cosine(mean(B), embed(JD_domain_keywords))
            where B = embeddings of CV *experience bullet* texts.

        Output:
            Shift cosine from [-1, 1] -> [0, 1]
            Return 0.5 (neutral) when insufficient data.
        """
        # 1) Collect CV experience BULLET texts (not job titles)
        cv_bullet_texts: List[str] = []
        for exp in cv_dict.get("experience", []) or []:
            for bullet in exp.get("bullets", []) or []:
                if isinstance(bullet, dict):
                    t = bullet.get("text", "")
                else:
                    t = str(bullet)
                t = (t or "").strip()
                if t:
                    cv_bullet_texts.append(t)

        # 2) Collect JD domain keywords (support a couple common keys)
        jd_domain_kws = (
            jd_dict.get("jd_domain_keywords")
            or jd_dict.get("domain_keywords")
            or (jd_dict.get("keyword_taxonomy", {}) or {}).get("domain_knowledge", [])
            or []
        )

        # Normalize JD domain kw list -> list[str]
        if isinstance(jd_domain_kws, str):
            jd_domain_kws = [jd_domain_kws]
        jd_domain_kws = [str(x).strip() for x in jd_domain_kws if x is not None and str(x).strip()]

        if not cv_bullet_texts or not jd_domain_kws:
            return 0.5  # Neutral if no data

        # 3) Embed bullets, take mean embedding
        cv_embeds = self.extractor.embed_texts(cv_bullet_texts)

        # embed_texts could return list[np.ndarray] OR np.ndarray
        if isinstance(cv_embeds, np.ndarray):
            if cv_embeds.ndim == 1:
                mean_cv_embed = cv_embeds
            else:
                mean_cv_embed = cv_embeds.mean(axis=0)
        else:
            arr = np.asarray(cv_embeds)
            # arr should be (n, d)
            if arr.ndim == 1:
                mean_cv_embed = arr
            else:
                mean_cv_embed = arr.mean(axis=0)

        # 4) Embed JD domain keywords (as one combined text)
        jd_domain_text = " ".join(jd_domain_kws).strip()
        jd_domain_embed = self.extractor.embed_text(jd_domain_text)

        # 5) Cosine similarity, shifted to [0, 1]
        sim = self.extractor.cosine_similarity(mean_cv_embed, jd_domain_embed)
        normalized = (sim + 1) / 2

        # Clamp safety
        if not np.isfinite(normalized):
            return 0.5
        return float(max(0.0, min(1.0, normalized)))
