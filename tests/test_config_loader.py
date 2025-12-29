import pytest
import yaml
from pathlib import Path
from modules.config_loader import load_scoring_config
from config.scoring_schemas import ScoringConfig
from config.settings import BASE_DIR

def test_load_scoring_config_default():
    """Test loading the default configuration."""
    config = load_scoring_config()
    assert isinstance(config, ScoringConfig)
    assert config.version == "1.0"
    assert config.random_seed == 42

def test_load_scoring_config_explicit(tmp_path):
    """Test loading configuration from an explicit path."""
    config_data = {
        "version": "1.0",
        "random_seed": 123,
        "ats_weights": {
            "lexical_coverage": 0.2,
            "fuzzy_coverage": 0.2,
            "tfidf_relevance": 0.2,
            "tfidf_cosine_similarity": 0.2,
            "section_distribution": 0.2
        },
        "jobfit_weights": {
            "summary_similarity": 0.2,
            "experience_alignment": 0.2,
            "skills_alignment": 0.2,
            "education_match": 0.2,
            "domain_relevance": 0.2
        },
        "score_bands": {
            "poor": [0, 50],
            "medium": [50, 75],
            "strong": [75, 90],
            "excellent": [90, 100]
        },
        "models": {
            "embedding_model": "test-model",
            "embedding_device": "cpu",
            "fuzzy_threshold": 85.0,

        },
        "tokenization": {
            "lowercase": True,
            "min_token_length": 2,
            "remove_stopwords": False,
            "remove_punctuation": True
        },
        "normalization": {
            "tfidfcos_min": 0.0,
            "tfidfcos_max": 10.0
        }
    }
    
    config_file = tmp_path / "test_config.yaml"
    with open(config_file, "w") as f:
        yaml.dump(config_data, f)
        
    config = load_scoring_config(config_file)
    assert isinstance(config, ScoringConfig)
    assert config.random_seed == 123
    assert config.models.embedding_model == "test-model"

def test_load_scoring_config_invalid_sum(tmp_path):
    """Test that invalid weight sums raise a ValueError."""
    config_data = {
        "version": "1.0",
        "random_seed": 42,
        "ats_weights": {
            "lexical_coverage": 0.5, # Sum > 1.0
            "fuzzy_coverage": 0.5,
            "tfidf_relevance": 0.2,
            "tfidf_cosine_similarity": 0.2,
            "section_distribution": 0.1
        },
        "jobfit_weights": {
            "summary_similarity": 0.2,
            "experience_alignment": 0.2,
            "skills_alignment": 0.2,
            "education_match": 0.2,
            "domain_relevance": 0.2
        },
        "score_bands": {
            "poor": [0, 50],
            "medium": [50, 75],
            "strong": [75, 90],
            "excellent": [90, 100]
        },
        "models": {
            "embedding_model": "test-model",
            "embedding_device": "cpu",
            "fuzzy_threshold": 90.0,

        },
        "tokenization": {
            "lowercase": True,
            "min_token_length": 2,
            "remove_stopwords": False,
            "remove_punctuation": True
        },
        "normalization": {
            "tfidfcos_min": 0.0,
            "tfidfcos_max": 10.0
        }
    }
    
    config_file = tmp_path / "invalid_config.yaml"
    with open(config_file, "w") as f:
        yaml.dump(config_data, f)
        
    with pytest.raises(ValueError, match="ATS weights must sum to 1.0"):
        load_scoring_config(config_file)

def test_load_scoring_config_missing_file():
    """Test that missing file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        load_scoring_config(Path("nonexistent.yaml"))
