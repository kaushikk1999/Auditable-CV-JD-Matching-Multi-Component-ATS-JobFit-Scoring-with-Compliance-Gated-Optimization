from typing import Dict
from modules.feature_extractor import FeatureExtractor
from modules.ats_scorer import ATSScorer
from modules.jobfit_scorer import JobFitScorer
from datetime import datetime


class ScoringPipeline:
    """Unified pipeline for ATS + Job-Compatibility scoring."""

    def __init__(self, config_path=None):
        self.feature_extractor = FeatureExtractor(config_path)
        self.ats_scorer = ATSScorer(self.feature_extractor)
        self.jobfit_scorer = JobFitScorer(self.feature_extractor)

    def score_cv_jd_pair(
        self,
        cv_structured: Dict,
        jd_enhanced: Dict,
        cv_raw_text: str,
        jd_raw_text: str
    ) -> Dict:
        """
        Score a single CV-JD pair.
        """
        ats_result = self.ats_scorer.score(
            cv_structured, jd_enhanced, cv_raw_text, jd_raw_text
        )

        jobfit_result = self.jobfit_scorer.score(cv_structured, jd_enhanced)

        report = {
            "timestamp": datetime.now().isoformat(),
            "ats_score": ats_result["ats_score"],
            "jobfit_score": jobfit_result["jobfit_score"],
            "ats_components": ats_result["components"],
            "jobfit_components": jobfit_result["components"],
            "ats_features": ats_result["features"],
            "ats_features": ats_result["features"],
            "jobfit_features": jobfit_result["features"],
            "ats_ablation": ats_result.get("ablation", []),
            "jobfit_ablation": jobfit_result.get("ablation", []),
            "interpretation": self._interpret_scores(
                ats_result["ats_score"],
                jobfit_result["jobfit_score"]
            )
        }
        return report

    def _interpret_scores(self, ats_score: float, jobfit_score: float) -> Dict:
        """Interpret scores into actionable feedback."""
        bands = self.feature_extractor.config.score_bands

        def get_band(score: float) -> str:
            for band_name, (low, high) in bands.items():
                if low <= score < high:
                    return band_name
            return "excellent"

        ats_band = get_band(ats_score).title()
        jobfit_band = get_band(jobfit_score).title()

        feedback = []

        if ats_band == "Poor":
            feedback.append("ATS Score is low. Focus on adding missing JD keywords to skills and experience sections.")
        elif ats_band == "Medium":
            feedback.append("ATS Score is moderate. Add more JD-aligned keywords and distribute them across sections.")
        elif ats_band == "Strong":
            feedback.append("ATS Score is strong. Minor keyword optimizations recommended.")
        else:
            feedback.append("ATS Score is excellent. CV is highly optimized for ATS parsing.")

        if jobfit_band == "Poor":
            feedback.append("Job-Compatibility is low. Rewrite experience bullets to align with JD responsibilities.")
        elif jobfit_band == "Medium":
            feedback.append("Job-Compatibility is moderate. Strengthen alignment between your experience and the role.")
        elif jobfit_band == "Strong":
            feedback.append("Job-Compatibility is strong. CV demonstrates good fit for this role.")
        else:
            feedback.append("Job-Compatibility is excellent. CV is highly aligned with role requirements.")

        return {
            "ats_band": ats_band,
            "jobfit_band": jobfit_band,
            "feedback": feedback
        }
