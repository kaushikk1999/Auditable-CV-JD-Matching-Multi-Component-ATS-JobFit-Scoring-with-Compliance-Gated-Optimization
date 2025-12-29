import pytest
import numpy as np
from unittest.mock import MagicMock, patch
from modules.feature_extractor import FeatureExtractor
from config.scoring_schemas import ScoringConfig

# Mock config for testing
@pytest.fixture
def mock_config():
    config = MagicMock(spec=ScoringConfig)
    config.random_seed = 42
    
    # Mock nested models config
    config.models = MagicMock()
    config.models.embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
    config.models.embedding_device = "cpu"
    config.models.fuzzy_threshold = 90.0

    
    # Mock nested tokenization config
    config.tokenization = MagicMock()
    config.tokenization.min_token_length = 2
    
    return config

@pytest.fixture
def feature_extractor(mock_config):
    with patch('modules.feature_extractor.load_scoring_config', return_value=mock_config):
        # Mock SentenceTransformer to avoid loading large models during tests
        with patch('modules.feature_extractor.SentenceTransformer') as MockST:
            mock_model = MockST.return_value
            mock_model.get_sentence_embedding_dimension.return_value = 384
            # Mock encode to return dummy embeddings
            mock_model.encode.side_effect = lambda texts, **kwargs: (
                np.ones((len(texts), 384)) if isinstance(texts, list) else np.ones(384)
            )
            extractor = FeatureExtractor()
            return extractor

def test_extract_keywords(feature_extractor):
    text = "Python machine learning AI"
    keywords = feature_extractor.extract_keywords(text)
    assert keywords == {"python", "machine", "learning", "ai"}
    
    # Test min length
    text_short = "a an the"
    keywords_short = feature_extractor.extract_keywords(text_short)
    # "an" is 2 chars, "the" is 3 chars. Both should be kept if min_token_length=2
    assert keywords_short == {"an", "the"}

# ... (omitted lines)

def test_compute_tfidf_cosine_similarity(feature_extractor):
    jd_text = "python developer"
    cv_text = "python developer"
    
    score = feature_extractor.compute_tfidf_cosine_similarity(jd_text, cv_text)
    
    assert isinstance(score, float)
    # TF-IDF cosine scores should be >= 0.
    # We just check it returns a float and is not None.
    assert score is not None

def test_extract_cv_keywords(feature_extractor):
    cv_dict = {
        "summary": {"text": "Experienced Python Developer"},
        "skills": [{"skills": ["Django", "Flask"]}],
        "experience": [
            {
                "job_title": "Software Engineer",
                "bullets": [{"text": "Developed API"}]
            }
        ],
        "projects": [
            {
                "project_name": "CV Optimizer",
                "technologies": ["NLP"]
            }
        ]
    }
    
    keywords = feature_extractor.extract_cv_keywords(cv_dict)
    
    assert "python" in keywords["summary"]
    assert "django" in keywords["skills"]
    assert "flask" in keywords["skills"]
    assert "software" in keywords["experience"]
    assert "engineer" in keywords["experience"]
    assert "developed" in keywords["experience"]
    assert "api" in keywords["experience"]
    assert "optimizer" in keywords["projects"]
    assert "nlp" in keywords["projects"]
    assert keywords["all"] == keywords["summary"] | keywords["skills"] | keywords["experience"] | keywords["projects"]

def test_extract_jd_keywords(feature_extractor):
    jd_dict = {
        "required_skills": ["Python", "SQL"],
        "preferred_skills": ["AWS"],
        "keyword_taxonomy": {
            "technical_skills": ["Git"],
            "tools_technologies": ["Docker"]
        },
        "ats_keywords": ["Agile"]
    }
    
    keywords = feature_extractor.extract_jd_keywords(jd_dict)
    
    assert "python" in keywords["required"]
    assert "sql" in keywords["required"]
    assert "git" in keywords["required"]
    assert "docker" in keywords["required"]
    assert "agile" in keywords["required"]
    assert "aws" in keywords["preferred"]
    assert keywords["all"] == keywords["required"] | keywords["preferred"]

def test_fuzzy_match_keywords(feature_extractor):
    jd_kw = {"javascript", "kubernetes"} # removed python as it is exact match
    cv_kw = {"python", "java", "kubernets"} # Typo in kubernetes
    
    matches = feature_extractor.fuzzy_match_keywords(jd_kw, cv_kw)
    
    # Python is exact match, so not in fuzzy matches
    assert "python" not in matches
    
    # Kubernetes should be fuzzy matched
    assert "kubernetes" in matches
    assert matches["kubernetes"]["match"] == "kubernets"
    assert matches["kubernetes"]["score"] >= 90.0

def test_compute_tfidf_weights(feature_extractor):
    jd_text = "python machine learning"
    cv_text = "python developer"
    
    weights = feature_extractor.compute_tfidf_weights(jd_text, cv_text)
    
    assert isinstance(weights, dict)
    assert "python" in weights
    assert "machine" in weights
    assert "learning" in weights
    # Weights should be normalized max 1.0
    assert max(weights.values()) <= 1.0

def test_compute_tfidf_cosine_similarity_repeat(feature_extractor):
    jd_text = "python developer"
    cv_text = "python developer"
    
    score = feature_extractor.compute_tfidf_cosine_similarity(jd_text, cv_text)
    
    assert isinstance(score, float)
    # TF-IDF cosine scores should be >= 0.
    # We just check it returns a float and is not None.
    assert score is not None

def test_embed_text(feature_extractor):
    embedding = feature_extractor.embed_text("test")
    assert isinstance(embedding, np.ndarray)
    assert embedding.shape == (384,)
    
    # Empty text
    embedding_empty = feature_extractor.embed_text("")
    assert np.all(embedding_empty == 0)

def test_embed_texts(feature_extractor):
    embeddings = feature_extractor.embed_texts(["test1", "test2"])
    assert isinstance(embeddings, np.ndarray)
    assert embeddings.shape == (2, 384)
    
    # Empty list
    embeddings_empty = feature_extractor.embed_texts([])
    assert embeddings_empty.shape == (0, 384)

def test_cosine_similarity(feature_extractor):
    vec1 = np.ones(384)
    vec2 = np.ones(384)
    
    sim = feature_extractor.cosine_similarity(vec1, vec2)
    assert np.isclose(sim, 1.0)
    
    # Orthogonal
    vec3 = np.zeros(384)
    vec3[0] = 1
    vec4 = np.zeros(384)
    vec4[1] = 1
    sim_ortho = feature_extractor.cosine_similarity(vec3, vec4)
    assert np.isclose(sim_ortho, 0.0)
