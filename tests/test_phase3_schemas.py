"""Quick validation script for Phase 3 schemas."""

from modules.schemas import (
    KeywordMatch,
    GapAnalysisResult,
    ExperienceAlignment,
    KeywordCoverageTable,
    AnalysisReport,
    PIIEntity,
    RedactionMap,
    AnonymizedCV,
    RunConfig,
    RunMetrics
)

def test_keyword_match():
    """Test KeywordMatch instantiation."""
    km = KeywordMatch(keyword="Python", found_in_cv=True)
    assert km.keyword == "Python"
    assert km.found_in_cv == True
    assert km.cv_locations == []
    assert km.jd_priority == "optional"
    assert km.match_score == 0.0
    print("✓ KeywordMatch works correctly")

def test_gap_analysis_result():
    """Test GapAnalysisResult instantiation."""
    gar = GapAnalysisResult()
    assert gar.present_keywords == []
    assert gar.missing_keywords == []
    assert gar.irrelevant_keywords == []
    assert gar.coverage_stats == {}
    print("✓ GapAnalysisResult works correctly")

def test_experience_alignment():
    """Test ExperienceAlignment instantiation."""
    ea = ExperienceAlignment(
        experience_index=0,
        job_title="Software Engineer",
        company_name="Tech Corp"
    )
    assert ea.experience_index == 0
    assert ea.job_title == "Software Engineer"
    assert ea.company_name == "Tech Corp"
    assert ea.relevance_score == 0.0
    assert ea.matched_keywords == []
    assert ea.matched_responsibilities == []
    assert ea.bullet_scores == []
    print("✓ ExperienceAlignment works correctly")

def test_keyword_coverage_table():
    """Test KeywordCoverageTable instantiation."""
    kct = KeywordCoverageTable(
        jd_keyword="SQL",
        category="tool",
        priority="required",
        present_in_cv=False
    )
    assert kct.jd_keyword == "SQL"
    assert kct.category == "tool"
    assert kct.priority == "required"
    assert kct.present_in_cv == False
    assert kct.current_frequency == 0
    assert kct.target_frequency == 1
    assert kct.suggested_sections == []
    print("✓ KeywordCoverageTable works correctly")

def test_analysis_report():
    """Test AnalysisReport instantiation."""
    ar = AnalysisReport(
        run_id="r1",
        timestamp="2025-11-24T21:00:00",
        cv_filename="cv.pdf",
        jd_filename="jd.txt",
        gap_analysis=GapAnalysisResult(),
        experience_alignments=[],
        keyword_coverage_table=[]
    )
    assert ar.run_id == "r1"
    assert ar.cv_filename == "cv.pdf"
    assert ar.jd_filename == "jd.txt"
    assert isinstance(ar.gap_analysis, GapAnalysisResult)
    assert ar.experience_alignments == []
    assert ar.keyword_coverage_table == []
    assert ar.recommendations == []
    print("✓ AnalysisReport works correctly")

def test_pii_entity():
    """Test PIIEntity instantiation."""
    pii = PIIEntity(
        entity_type="EMAIL",
        original_value="test@example.com",
        anonymized_value="[EMAIL_1]"
    )
    assert pii.entity_type == "EMAIL"
    assert pii.original_value == "test@example.com"
    assert pii.anonymized_value == "[EMAIL_1]"
    assert pii.locations == []
    print("✓ PIIEntity works correctly")

def test_redaction_map():
    """Test RedactionMap instantiation."""
    rm = RedactionMap(
        redaction_id="red1",
        timestamp="2025-11-24T21:00:00",
        entities=[]
    )
    assert rm.redaction_id == "red1"
    assert rm.timestamp == "2025-11-24T21:00:00"
    assert rm.entities == []
    print("✓ RedactionMap works correctly")

def test_anonymized_cv():
    """Test AnonymizedCV instantiation."""
    acv = AnonymizedCV(
        original_hash="abc123hash",
        redaction_id="red1",
        anonymized_text="Anonymized CV text...",
        structured_data={"contact": "redacted"}
    )
    assert acv.original_hash == "abc123hash"
    assert acv.redaction_id == "red1"
    assert acv.anonymized_text == "Anonymized CV text..."
    assert acv.structured_data == {"contact": "redacted"}
    print("✓ AnonymizedCV works correctly")

def test_run_config():
    """Test RunConfig instantiation."""
    rc = RunConfig(
        run_id="r1",
        timestamp="2025-11-24T21:00:00",
        cv_file="cv.pdf",
        jd_file="jd.txt"
    )
    assert rc.run_id == "r1"
    assert rc.timestamp == "2025-11-24T21:00:00"
    assert rc.cv_file == "cv.pdf"
    assert rc.jd_file == "jd.txt"
    assert rc.parameters == {}
    print("✓ RunConfig works correctly")

def test_run_metrics():
    """Test RunMetrics instantiation."""
    rm = RunMetrics(
        run_id="r1",
        keyword_coverage=0.75,
        experience_alignment_avg=0.85,
        processing_time_seconds=2.5,
        keywords_present=15,
        keywords_missing=5
    )
    assert rm.run_id == "r1"
    assert rm.keyword_coverage == 0.75
    assert rm.experience_alignment_avg == 0.85
    assert rm.processing_time_seconds == 2.5
    assert rm.keywords_present == 15
    assert rm.keywords_missing == 5
    print("✓ RunMetrics works correctly")

if __name__ == "__main__":
    print("\nRunning Phase 3 Schema Validation Tests...\n")
    
    test_keyword_match()
    test_gap_analysis_result()
    test_experience_alignment()
    test_keyword_coverage_table()
    test_analysis_report()
    test_pii_entity()
    test_redaction_map()
    test_anonymized_cv()
    test_run_config()
    test_run_metrics()
    
    print("\n" + "="*50)
    print("✅ All 10 Phase 3 schemas validated successfully!")
    print("="*50)
