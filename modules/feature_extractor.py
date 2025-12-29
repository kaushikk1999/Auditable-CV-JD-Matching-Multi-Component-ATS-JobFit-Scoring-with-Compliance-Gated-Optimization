import re
import numpy as np
from typing import List, Dict, Set

from sklearn.feature_extraction.text import TfidfVectorizer

from sentence_transformers import SentenceTransformer
from rapidfuzz import fuzz

from modules.config_loader import load_scoring_config


class FeatureExtractor:
    """Extracts scoring features from CV and JD (ATS + JobFit)."""

    def __init__(self, config_path=None):
        self.config = load_scoring_config(config_path)

        # Reproducibility
        np.random.seed(int(self.config.random_seed))

        # Embeddings
        self.embedding_model = SentenceTransformer(
            self.config.models.embedding_model,
            device=self.config.models.embedding_device,
        )
        # Some SentenceTransformer versions expose .eval(); guard it.
        try:
            self.embedding_model.eval()
        except Exception:
            pass

        # Determine embedding dimension dynamically (fallback to 384 for MiniLM)
        try:
            self.embedding_dim = int(self.embedding_model.get_sentence_embedding_dimension())
        except Exception:
            self.embedding_dim = 384

        # TF-IDF (must match tokenization rule: alnum tokens, min_len)
        min_len = int(self.config.tokenization.min_token_length)
        lowercase = bool(self.config.tokenization.lowercase)

        self.tfidf = TfidfVectorizer(
            lowercase=lowercase,
            token_pattern=rf"(?u)\b[a-zA-Z0-9]{{{min_len},}}\b",
            max_features=1000,
        )

    # ========== TOKENIZATION (SINGLE SOURCE OF TRUTH) ==========

    def _tokenize_alnum(self, text: str) -> List[str]:
        """
        Tokenization rule (consistent across keywords/TF-IDF/TF-IDF-cosine):
        - lowercase (if enabled)
        - alphanumeric tokens only
        - min token length from config
        Returns tokens with duplicates (needed for term frequency).
        """
        if not text:
            return []

        s = str(text)
        min_len = int(self.config.tokenization.min_token_length)
        if bool(self.config.tokenization.lowercase):
            s = s.lower()

        return re.findall(rf"\b[a-z0-9]{{{min_len},}}\b", s)

    def extract_keywords(self, text: str) -> Set[str]:
        """Extract normalized keyword SET from text."""
        return set(self._tokenize_alnum(text))

    # ========== KEYWORD EXTRACTION ==========

    def extract_cv_keywords(self, cv_dict: Dict) -> Dict[str, Set[str]]:
        """Extract keywords by CV section."""
        keywords: Dict[str, Set[str]] = {
            "summary": set(),
            "skills": set(),
            "experience": set(),
            "projects": set(),
            "education": set(),
            "all": set(),
        }

        # Summary
        summary = cv_dict.get("summary") or {}
        if isinstance(summary, dict):
            keywords["summary"] = self.extract_keywords(summary.get("text", ""))

        # Skills
        for skill_cat in cv_dict.get("skills", []) or []:
            if not isinstance(skill_cat, dict):
                continue
            for skill in skill_cat.get("skills", []) or []:
                keywords["skills"].update(self.extract_keywords(skill))

        # Experience (job title + bullets)
        for exp in cv_dict.get("experience", []) or []:
            if not isinstance(exp, dict):
                continue
            keywords["experience"].update(self.extract_keywords(exp.get("job_title", "")))
            keywords["experience"].update(self.extract_keywords(exp.get("company_name", "")))

            for bullet in exp.get("bullets", []) or []:
                if isinstance(bullet, dict):
                    keywords["experience"].update(self.extract_keywords(bullet.get("text", "")))
                else:
                    keywords["experience"].update(self.extract_keywords(str(bullet)))

        # Projects (name + technologies + bullets)
        for proj in cv_dict.get("projects", []) or []:
            if not isinstance(proj, dict):
                continue
            keywords["projects"].update(self.extract_keywords(proj.get("project_name", "")))

            for tech in proj.get("technologies", []) or []:
                keywords["projects"].update(self.extract_keywords(tech))

            for bullet in proj.get("bullets", []) or []:
                if isinstance(bullet, dict):
                    keywords["projects"].update(self.extract_keywords(bullet.get("text", "")))
                else:
                    keywords["projects"].update(self.extract_keywords(str(bullet)))

        # Education (optional but useful for keyword presence + domain terms)
        for edu in cv_dict.get("education", []) or []:
            if not isinstance(edu, dict):
                continue
            keywords["education"].update(self.extract_keywords(edu.get("degree", "")))
            keywords["education"].update(self.extract_keywords(edu.get("institution", "")))
            keywords["education"].update(self.extract_keywords(edu.get("field_of_study", "")))

        # All keywords (include everything)
        for section in ("summary", "skills", "experience", "projects", "education"):
            keywords["all"].update(keywords[section])

        return keywords

    def extract_jd_keywords(self, jd_dict: Dict) -> Dict[str, Set[str]]:
        """Extract keywords from JD with priority labels."""
        keywords: Dict[str, Set[str]] = {"required": set(), "preferred": set(), "all": set()}

        # Required skills
        for skill in jd_dict.get("required_skills", []) or []:
            keywords["required"].update(self.extract_keywords(skill))

        # Taxonomy: technical skills
        taxonomy = jd_dict.get("keyword_taxonomy") or {}
        for skill in taxonomy.get("technical_skills", []) or []:
            keywords["required"].update(self.extract_keywords(skill))

        # Tools/technologies
        for tool in taxonomy.get("tools_technologies", []) or []:
            keywords["required"].update(self.extract_keywords(tool))

        # ATS keywords
        for kw in jd_dict.get("ats_keywords", []) or []:
            keywords["required"].update(self.extract_keywords(kw))

        # Preferred skills
        for skill in jd_dict.get("preferred_skills", []) or []:
            keywords["preferred"].update(self.extract_keywords(skill))

        keywords["all"] = keywords["required"] | keywords["preferred"]
        return keywords

    # ========== FUZZY MATCHING ==========

    def fuzzy_match_keywords(self, unmatched_jd_keywords: Set[str], cv_keywords: Set[str]) -> Dict[str, Dict]:
        """
        Find fuzzy matches for UNMATCHED JD keywords.
        Returns: { jd_kw: {"match": best_cv_kw, "score": similarity} }
        """
        fuzzy_matches: Dict[str, Dict] = {}
        threshold = float(self.config.models.fuzzy_threshold)

        # Small micro-optimization: list once
        cv_list = list(cv_keywords)

        for jd_kw in unmatched_jd_keywords:
            best_match = None
            best_score = 0.0

            for cv_kw in cv_list:
                score = float(fuzz.ratio(jd_kw, cv_kw))
                if score > best_score:
                    best_score = score
                    best_match = cv_kw

            if best_match is not None and best_score >= threshold:
                fuzzy_matches[jd_kw] = {"match": best_match, "score": best_score}

        return fuzzy_matches

    # ========== TF-IDF FEATURES ==========

    def compute_tfidf_weights(self, jd_text: str, cv_text: str) -> Dict[str, float]:
        """Compute normalized TF-IDF importance weights for JD tokens in [0,1]."""
        corpus = [jd_text or "", cv_text or ""]
        tfidf_matrix = self.tfidf.fit_transform(corpus)

        feature_names = self.tfidf.get_feature_names_out()
        jd_scores = tfidf_matrix[0].toarray().flatten()

        max_score = float(np.max(jd_scores)) if jd_scores.size else 0.0
        if max_score <= 0:
            return {}

        weights: Dict[str, float] = {}
        for idx, score in enumerate(jd_scores):
            if score > 0:
                weights[str(feature_names[idx])] = float(score) / max_score

        return weights

    # ========== TF-IDF COSINE FEATURES ==========

    def compute_tfidf_cosine_similarity(self, jd_text: str, cv_text: str) -> float:
        """
        Compute TF-IDF cosine similarity between JD and CV.
        
        Compute TF-IDF cosine similarity between JD and CV.
        
        Note: Stable two-document similarity baseline using TF-IDF cosine similarity.
        TF-IDF cosine similarity is more appropriate for comparing just 2 documents.
        
        Returns: Raw similarity score in [0, ~10] range (not normalized here).
        """
        jd_tokens = self._tokenize_alnum(jd_text or "")
        cv_tokens = self._tokenize_alnum(cv_text or "")

        if not jd_tokens or not cv_tokens:
            return 0.0

        # Reconstruct texts from tokens for TF-IDF
        jd_text_clean = " ".join(jd_tokens)
        cv_text_clean = " ".join(cv_tokens)
        
        if not jd_text_clean or not cv_text_clean:
            return 0.0

        try:
            # Use TF-IDF vectorizer (already initialized)
            tfidf_matrix = self.tfidf.fit_transform([jd_text_clean, cv_text_clean])
            
            # Compute cosine similarity between JD and CV
            jd_vector = tfidf_matrix[0].toarray().flatten()
            cv_vector = tfidf_matrix[1].toarray().flatten()
            
            # Cosine similarity
            dot_product = float(np.dot(jd_vector, cv_vector))
            norm_jd = float(np.linalg.norm(jd_vector))
            norm_cv = float(np.linalg.norm(cv_vector))
            
            if norm_jd == 0 or norm_cv == 0:
                return 0.0
            
            cosine_sim = dot_product / (norm_jd * norm_cv)
            
            # Scale to roughly [0, 10] range for compatibility with normalization
            # Cosine sim is in [0, 1], multiply by 10
            return max(0.0, cosine_sim * 10.0)
            
        except Exception:
            return 0.0

    # ========== EMBEDDING FEATURES ==========

    def embed_text(self, text: str) -> np.ndarray:
        """Generate sentence embedding for a single text."""
        if not text or not str(text).strip():
            return np.zeros(self.embedding_dim, dtype=np.float32)

        vec = self.embedding_model.encode(
            str(text),
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        return np.asarray(vec, dtype=np.float32)

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for multiple texts."""
        if not texts:
            return np.zeros((0, self.embedding_dim), dtype=np.float32)

        vecs = self.embedding_model.encode(
            [str(t) for t in texts],
            convert_to_numpy=True,
            show_progress_bar=False,
            batch_size=32,
        )
        return np.asarray(vecs, dtype=np.float32)

    def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Compute cosine similarity in [-1,1]."""
        if vec1 is None or vec2 is None:
            return 0.0
        v1 = np.asarray(vec1, dtype=np.float32)
        v2 = np.asarray(vec2, dtype=np.float32)
        if v1.size == 0 or v2.size == 0:
            return 0.0

        norm1 = float(np.linalg.norm(v1))
        norm2 = float(np.linalg.norm(v2))
        if norm1 == 0.0 or norm2 == 0.0:
            return 0.0

        return float(np.dot(v1, v2) / (norm1 * norm2))
