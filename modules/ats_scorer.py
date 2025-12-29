import math
from typing import Dict
from modules.scoring_utils import build_ablation_rows
from modules.feature_extractor import FeatureExtractor


class ATSScorer:
    """Computes ATS score and sub-components."""

    def __init__(self, feature_extractor: FeatureExtractor):
        self.extractor = feature_extractor
        self.config = feature_extractor.config

    def score(self, cv_dict: Dict, jd_dict: Dict, cv_text: str, jd_text: str) -> Dict:
        """
        Compute full ATS score with all components.
        Returns:
          {
            "ats_score": float,  # [0, 100]
            "components": { ... each in [0,100] },
            "features": {...}
          }
        """
        cv_keywords = self.extractor.extract_cv_keywords(cv_dict)
        jd_keywords = self.extractor.extract_jd_keywords(jd_dict)

        jd_all = jd_keywords["all"]
        cv_all = cv_keywords["all"]

        # Component 1: Lexical Coverage
        c_lex = self._lexical_coverage(jd_all, cv_all)

        # Component 2: Fuzzy Coverage
        c_fuzzy = self._fuzzy_coverage(jd_all, cv_all)

        # Component 3: TF-IDF Relevance
        r_tfidf = self._tfidf_relevance(jd_text, cv_text, jd_all, cv_all)

        # Component 4: TF-IDF Cosine Similarity
        s_tfidfcos = self._tfidf_cosine_similarity(jd_text, cv_text)

        # Component 5: Section Distribution Quality (PDF intent: matched JD keywords per section)
        q_section = self._section_distribution(jd_all, cv_keywords)

        weights = self.config.ats_weights
        ats_score = (
            weights.lexical_coverage * c_lex +
            weights.fuzzy_coverage * c_fuzzy +
            weights.tfidf_relevance * r_tfidf +
            weights.tfidf_cosine_similarity * s_tfidfcos +
            weights.section_distribution * q_section
        )

        ats_score_100 = ats_score * 100

        matched_dist = self._matched_keyword_distribution(jd_all, cv_keywords)

        # Prepare data for ablation helper
        components_0_1 = {
            "lexical_coverage": c_lex,
            "fuzzy_coverage": c_fuzzy,
            "tfidf_relevance": r_tfidf,
            "tfidf_cosine_similarity": s_tfidfcos,
            "section_distribution": q_section,
        }

        weights_dict = {
            "lexical_coverage": float(weights.lexical_coverage),
            "fuzzy_coverage": float(weights.fuzzy_coverage),
            "tfidf_relevance": float(weights.tfidf_relevance),
            "tfidf_cosine_similarity": float(weights.tfidf_cosine_similarity),
            "section_distribution": float(weights.section_distribution),
        }

        # Determine ats_score_0_1 (it is ats_score before multiplying by 100)
        ats_score_0_1 = ats_score

        ablation_rows = build_ablation_rows(ats_score_0_1, components_0_1, weights_dict)

        return {
            "ats_score": ats_score_100,
            "components": {
                "lexical_coverage": c_lex * 100,
                "fuzzy_coverage": c_fuzzy * 100,
                "tfidf_relevance": r_tfidf * 100,
                "tfidf_cosine_similarity": s_tfidfcos * 100,
                "section_distribution": q_section * 100
            },
            "features": {
                "jd_keywords_count": len(jd_all),
                "cv_keywords_count": len(cv_all),
                "exact_matches": len(jd_all & cv_all),
                "keyword_distribution_raw_cv": {k: len(v) for k, v in cv_keywords.items() if isinstance(v, set)},
                "matched_jd_keyword_distribution": matched_dist,
            },
            "ablation": ablation_rows
        }

    def _lexical_coverage(self, jd_keywords: set, cv_keywords: set) -> float:
        """Exact keyword recall."""
        if not jd_keywords:
            return 0.0
        matches = jd_keywords & cv_keywords
        return len(matches) / len(jd_keywords)

    def _fuzzy_coverage(self, jd_keywords: set, cv_keywords: set) -> float:
        """Fuzzy coverage for unmatched JD keywords."""
        exact_matches = jd_keywords & cv_keywords
        unmatched_jd = jd_keywords - exact_matches

        if not unmatched_jd:
            return 1.0

        fuzzy_matches = self.extractor.fuzzy_match_keywords(unmatched_jd, cv_keywords)
        return len(fuzzy_matches) / len(unmatched_jd)

    def _tfidf_relevance(self, jd_text: str, cv_text: str, jd_keywords: set, cv_keywords: set) -> float:
        """TF-IDF weighted coverage over JD keywords."""
        tfidf_weights = self.extractor.compute_tfidf_weights(jd_text, cv_text)

        total_weight = 0.0
        matched_weight = 0.0

        for kw in jd_keywords:
            w = float(tfidf_weights.get(kw, 0.0))
            total_weight += w
            if kw in cv_keywords:
                matched_weight += w

        if total_weight <= 0:
            return 0.0

        return matched_weight / total_weight

    def _tfidf_cosine_similarity(self, jd_text: str, cv_text: str) -> float:
        """TF-IDF cosine similarity normalized to [0,1]."""
        raw_score = self.extractor.compute_tfidf_cosine_similarity(jd_text, cv_text)

        t_min = float(self.config.normalization.tfidfcos_min)
        t_max = float(self.config.normalization.tfidfcos_max)

        den = (t_max - t_min)
        if den <= 0:
            return 0.0

        normalized = (raw_score - t_min) / den
        return max(0.0, min(1.0, normalized))

    def _matched_keyword_distribution(self, jd_keywords: set, cv_keywords: Dict[str, set]) -> Dict[str, int]:
        """Counts matched JD keywords per section."""
        sections = ["summary", "skills", "experience"]
        return {s: len((cv_keywords.get(s, set()) & jd_keywords)) for s in sections}

    def _section_distribution(self, jd_keywords: set, cv_keywords: Dict[str, set]) -> float:
        """
        Entropy of matched JD keyword distribution across sections (summary/skills/experience),
        normalized by log2(3).
        """
        sections = ["summary", "skills", "experience"]
        counts = [len((cv_keywords.get(s, set()) & jd_keywords)) for s in sections]

        total = sum(counts)
        if total == 0:
            return 0.0

        probs = [c / total for c in counts if c > 0]
        if not probs:
            return 0.0

        entropy = -sum(p * math.log2(p) for p in probs)
        max_entropy = math.log2(len(sections))
        return entropy / max_entropy
