from pydantic import BaseModel, Field, field_validator
from typing import Dict, List, Tuple

class ATSWeights(BaseModel):
    lexical_coverage: float = Field(ge=0, le=1)
    fuzzy_coverage: float = Field(ge=0, le=1)
    tfidf_relevance: float = Field(ge=0, le=1)
    tfidf_cosine_similarity: float = Field(ge=0, le=1)
    section_distribution: float = Field(ge=0, le=1)
    
    @field_validator('*')
    def check_sum(cls, v, info):
        # Validation of sum happens at config level
        return v

class JobFitWeights(BaseModel):
    summary_similarity: float = Field(ge=0, le=1)
    experience_alignment: float = Field(ge=0, le=1)
    skills_alignment: float = Field(ge=0, le=1)
    education_match: float = Field(ge=0, le=1)
    domain_relevance: float = Field(ge=0, le=1)

class ModelConfig(BaseModel):
    embedding_model: str
    embedding_device: str
    fuzzy_threshold: float


class TokenizationConfig(BaseModel):
    lowercase: bool
    min_token_length: int
    remove_stopwords: bool
    remove_punctuation: bool

class NormalizationConfig(BaseModel):
    tfidfcos_min: float
    tfidfcos_max: float

class ScoringConfig(BaseModel):
    version: str
    random_seed: int
    ats_weights: ATSWeights
    jobfit_weights: JobFitWeights
    score_bands: Dict[str, List[int]]
    models: ModelConfig
    tokenization: TokenizationConfig
    normalization: NormalizationConfig
    
    @field_validator('ats_weights')
    def validate_ats_sum(cls, v):
        total = sum([
            v.lexical_coverage, v.fuzzy_coverage, v.tfidf_relevance,
            v.tfidf_cosine_similarity, v.section_distribution
        ])
        if abs(total - 1.0) > 0.001:
            raise ValueError(f"ATS weights must sum to 1.0, got {total}")
        return v
    
    @field_validator('jobfit_weights')
    def validate_jobfit_sum(cls, v):
        total = sum([
            v.summary_similarity, v.experience_alignment, v.skills_alignment,
            v.education_match, v.domain_relevance
        ])
        if abs(total - 1.0) > 0.001:
            raise ValueError(f"JobFit weights must sum to 1.0, got {total}")
        return v
