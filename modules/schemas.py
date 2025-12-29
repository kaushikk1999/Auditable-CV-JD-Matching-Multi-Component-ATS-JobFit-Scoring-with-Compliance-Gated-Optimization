from typing import List, Optional, Dict, Set
from pydantic import BaseModel, Field, EmailStr, field_validator
from datetime import date, datetime

# ============== CV Data Models ==============

class ContactInfo(BaseModel):
    """User contact information."""
    full_name: str = Field(..., min_length=2)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None
    location: Optional[str] = None

    @field_validator('email', mode='before')
    @classmethod
    def empty_string_to_none(cls, v):
        if v == "":
            return None
        return v

class Summary(BaseModel):
    """Professional summary/objective."""
    text: str = Field(..., min_length=10)
    
class ExperienceBullet(BaseModel):
    """Single bullet point in an experience entry."""
    text: str = Field(..., min_length=5)
    
class ExperienceEntry(BaseModel):
    """Single work experience entry."""
    job_title: str
    company_name: str
    location: Optional[str] = None
    start_date: str  # e.g., "Jan 2020" or "2020-01"
    end_date: Optional[str] = "Present"  # e.g., "Present" or "Dec 2022"
    bullets: List[ExperienceBullet] = Field(default_factory=list)

class ProjectBullet(BaseModel):
    """Single bullet point in a project entry."""
    text: str = Field(..., min_length=5)

class ProjectEntry(BaseModel):
    """Single project entry."""
    project_name: str
    description: Optional[str] = None
    technologies: List[str] = Field(default_factory=list)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    bullets: List[ProjectBullet] = Field(default_factory=list)

class SkillCategory(BaseModel):
    """Categorized skill group."""
    category_name: str  # e.g., "Programming Languages", "Frameworks", "Tools"
    skills: List[str] = Field(..., min_items=1)

class Education(BaseModel):
    """Education entry."""
    degree: str
    institution: str
    location: Optional[str] = None
    graduation_date: Optional[str] = None
    gpa: Optional[str] = None
    relevant_coursework: List[str] = Field(default_factory=list)

class Certification(BaseModel):
    """Certification entry."""
    name: str
    issuer: Optional[str] = None
    date_obtained: Optional[str] = None
    credential_id: Optional[str] = None

class StructuredCV(BaseModel):
    """Complete structured CV representation."""
    contact_info: ContactInfo
    summary: Optional[Summary] = None
    skills: List[SkillCategory] = Field(default_factory=list)
    experience: List[ExperienceEntry] = Field(default_factory=list)
    projects: List[ProjectEntry] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    certifications: List[Certification] = Field(default_factory=list)
    
    @field_validator('experience')
    def validate_experience_not_empty(cls, v):
        if not v:
            raise ValueError("CV must contain at least one experience entry")
        return v

# ============== Enhanced JD Data Models ==============

class KeywordTaxonomy(BaseModel):
    """Categorized keywords from JD."""
    technical_skills: List[str] = Field(default_factory=list)
    tools_technologies: List[str] = Field(default_factory=list)
    soft_skills: List[str] = Field(default_factory=list)
    domain_knowledge: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)

class RequirementLevel(BaseModel):
    """Requirement with priority classification."""
    text: str
    is_required: bool  # True = "must have", False = "nice to have"
    keywords: List[str] = Field(default_factory=list)

class EnhancedJD(BaseModel):
    """Enhanced job description with keyword taxonomy."""
    # Original fields from Phase 1
    job_title: str
    company_name: str
    location: str
    work_type: str
    experience_required: str
    company_overview: str
    role_summary: str
    key_responsibilities: List[str]
    required_skills: List[str]
    preferred_skills: List[str]
    education: str
    soft_skills: List[str]
    diversity_statement: str
    recruiter_contact: str
    ats_keywords: List[str]
    
    # Phase 2 enhancements
    keyword_taxonomy: KeywordTaxonomy = Field(default_factory=KeywordTaxonomy)
    must_have_requirements: List[RequirementLevel] = Field(default_factory=list)
    nice_to_have_requirements: List[RequirementLevel] = Field(default_factory=list)

# ============== Gap Analysis Models ==============

class KeywordMatch(BaseModel):
    """Single keyword match result."""
    keyword: str
    found_in_cv: bool
    cv_locations: List[str] = Field(default_factory=list)  # e.g., ["experience_0_bullet_1", "skills"]
    jd_priority: str = "optional"  # "required", "preferred", "optional"
    match_score: float = 0.0  # 0.0-1.0, fuzzy match confidence

class GapAnalysisResult(BaseModel):
    """Complete keyword gap analysis."""
    present_keywords: List[KeywordMatch] = Field(default_factory=list)
    missing_keywords: List[KeywordMatch] = Field(default_factory=list)
    irrelevant_keywords: List[str] = Field(default_factory=list)  # CV skills not in JD
    
    coverage_stats: Dict[str, float] = Field(default_factory=dict)
    # e.g., {"required_coverage": 0.85, "preferred_coverage": 0.6, "overall_coverage": 0.75}

class ExperienceAlignment(BaseModel):
    """Maps CV experience to JD requirements."""
    experience_index: int
    job_title: str
    company_name: str
    relevance_score: float = 0.0  # 0.0-1.0
    matched_keywords: List[str] = Field(default_factory=list)
    matched_responsibilities: List[str] = Field(default_factory=list)
    bullet_scores: List[float] = Field(default_factory=list)  # Relevance per bullet

class KeywordCoverageTable(BaseModel):
    """ATS keyword coverage report for rewrite engine guidance."""
    jd_keyword: str
    category: str  # "technical_skill", "tool", "soft_skill", "domain"
    priority: str  # "required", "preferred", "optional"
    present_in_cv: bool
    current_frequency: int = 0  # How many times it appears in original CV
    target_frequency: int = 1   # How many times it should appear in optimized CV
    suggested_sections: List[str] = Field(default_factory=list)  # Where to add it

class AnalysisReport(BaseModel):
    """Complete analysis output for a single CV-JD pair."""
    run_id: str
    timestamp: str
    cv_filename: str
    jd_filename: str
    
    gap_analysis: GapAnalysisResult
    experience_alignments: List[ExperienceAlignment]
    keyword_coverage_table: List[KeywordCoverageTable]
    
    recommendations: List[str] = Field(default_factory=list)

# ============== PII Redaction Models ==============

class PIIEntity(BaseModel):
    """Detected PII entity."""
    entity_type: str  # "NAME", "EMAIL", "PHONE", "ADDRESS", "COMPANY"
    original_value: str
    anonymized_value: str
    locations: List[str] = Field(default_factory=list)  # Where it appears

class RedactionMap(BaseModel):
    """Reversible anonymization mapping."""
    redaction_id: str
    timestamp: str
    entities: List[PIIEntity]
    
class AnonymizedCV(BaseModel):
    """CV with PII redacted."""
    original_hash: str  # SHA256 of original for tracking
    redaction_id: str
    anonymized_text: str
    structured_data: Dict  # Anonymized structured CV

# ============== Experiment Tracking Models ==============

class RunConfig(BaseModel):
    """Configuration snapshot for a single run."""
    run_id: str
    timestamp: str
    cv_file: str
    jd_file: str
    parameters: Dict = Field(default_factory=dict)
    # e.g., {"fuzzy_match_threshold": 0.8, "min_keyword_length": 3}

class RunMetrics(BaseModel):
    """Metrics captured during analysis."""
    run_id: str
    keyword_coverage: float
    experience_alignment_avg: float
    processing_time_seconds: float
    keywords_present: int
    keywords_missing: int

# ============== Compliance Audit Models ==============

class BuzzwordAuditResult(BaseModel):
    """Buzzword audit check result."""
    passed: bool
    violations: List[str] = Field(default_factory=list)
    violation_count: int
    status: str  # "NO_BUZZWORDS_PRESENT" or "BUZZWORD_BREACH"

class StopwordAuditResult(BaseModel):
    """Stopword audit check result."""
    passed: bool
    violations: List[str] = Field(default_factory=list)
    violation_count: int
    status: str  # "NO_STOPWORDS_PRESENT" or "STOPWORD_BREACH"

class UniquenessAuditResult(BaseModel):
    """Word uniqueness check result."""
    passed: bool
    duplicates: Dict[str, int] = Field(default_factory=dict)
    violation_count: int
    total_duplicate_instances: int = 0
    status: str  # "ALL_WORDS_UNIQUE" or "DUPLICATE_WORDS_BREACH"

class QuantificationAuditResult(BaseModel):
    """Quantification integrity check result."""
    passed: bool
    compliant_bullets: List[int] = Field(default_factory=list)
    non_compliant_bullets: List[int] = Field(default_factory=list)
    compliance_rate: float
    total_bullets: int
    status: str  # "ALL_POINTS_QUANTIFIED" or "NON_QUANTIFIED_POINTS_FOUND"

class BrevityAuditResult(BaseModel):
    """Brevity analysis result."""
    passed: bool
    word_count: int
    word_count_target: str
    word_count_status: str
    bullet_count: int
    bullet_count_target: str
    bullet_count_status: str

class ComplianceAuditReport(BaseModel):
    """Complete compliance audit report."""
    overall_passed: bool
    timestamp: str
    checks: Dict = Field(default_factory=dict)
    critical_violations: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)

# ============== Scoring Result Models ==============

class ScoringReport(BaseModel):
    """Complete scoring report for CV-JD pair."""
    timestamp: str
    ats_score: float = Field(ge=0, le=100)
    jobfit_score: float = Field(ge=0, le=100)
    ats_components: Dict[str, float]
    jobfit_components: Dict[str, float]
    ats_features: Dict = Field(default_factory=dict)
    jobfit_features: Dict = Field(default_factory=dict)
    interpretation: Dict = Field(default_factory=dict)
