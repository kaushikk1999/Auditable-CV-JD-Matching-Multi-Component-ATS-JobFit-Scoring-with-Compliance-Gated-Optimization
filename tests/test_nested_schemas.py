"""Test nested schema relationships for Phase 3."""

from modules.schemas import (
    KeywordMatch,
    GapAnalysisResult,
    ExperienceAlignment,
    KeywordCoverageTable,
    AnalysisReport,
    PIIEntity,
    RedactionMap,
)

def test_complex_nested_structures():
    """Test complex nested schema structures."""
    
    # Create a comprehensive AnalysisReport with nested data
    keyword1 = KeywordMatch(
        keyword="Python",
        found_in_cv=True,
        cv_locations=["experience_0_bullet_1", "skills"],
        jd_priority="required",
        match_score=1.0
    )
    
    keyword2 = KeywordMatch(
        keyword="Machine Learning",
        found_in_cv=False,
        jd_priority="preferred",
        match_score=0.0
    )
    
    gap_analysis = GapAnalysisResult(
        present_keywords=[keyword1],
        missing_keywords=[keyword2],
        irrelevant_keywords=["Fortran", "COBOL"],
        coverage_stats={
            "required_coverage": 0.85,
            "preferred_coverage": 0.6,
            "overall_coverage": 0.75
        }
    )
    
    exp_align = ExperienceAlignment(
        experience_index=0,
        job_title="Senior Software Engineer",
        company_name="TechCorp Inc.",
        relevance_score=0.92,
        matched_keywords=["Python", "AWS", "Docker"],
        matched_responsibilities=["Led team of 5 engineers", "Built scalable APIs"],
        bullet_scores=[0.95, 0.88, 0.93]
    )
    
    coverage_table = [
        KeywordCoverageTable(
            jd_keyword="Python",
            category="technical_skill",
            priority="required",
            present_in_cv=True,
            current_frequency=5,
            target_frequency=5,
            suggested_sections=[]
        ),
        KeywordCoverageTable(
            jd_keyword="Kubernetes",
            category="tool",
            priority="preferred",
            present_in_cv=False,
            current_frequency=0,
            target_frequency=2,
            suggested_sections=["experience", "skills"]
        )
    ]
    
    analysis_report = AnalysisReport(
        run_id="run_123",
        timestamp="2025-11-24T21:00:00",
        cv_filename="john_doe_cv.pdf",
        jd_filename="senior_engineer_jd.txt",
        gap_analysis=gap_analysis,
        experience_alignments=[exp_align],
        keyword_coverage_table=coverage_table,
        recommendations=[
            "Add Kubernetes experience to skills section",
            "Emphasize Machine Learning projects",
            "Remove outdated technologies (Fortran, COBOL)"
        ]
    )
    
    # Verify nested structures
    assert len(analysis_report.gap_analysis.present_keywords) == 1
    assert analysis_report.gap_analysis.present_keywords[0].keyword == "Python"
    assert analysis_report.gap_analysis.coverage_stats["overall_coverage"] == 0.75
    assert len(analysis_report.experience_alignments) == 1
    assert analysis_report.experience_alignments[0].relevance_score == 0.92
    assert len(analysis_report.keyword_coverage_table) == 2
    assert len(analysis_report.recommendations) == 3
    
    print("✓ Complex nested AnalysisReport structure works correctly")
    
    # Test PII redaction with nested entities
    pii_entities = [
        PIIEntity(
            entity_type="NAME",
            original_value="John Doe",
            anonymized_value="[NAME_1]",
            locations=["contact_info", "experience_0"]
        ),
        PIIEntity(
            entity_type="EMAIL",
            original_value="john.doe@email.com",
            anonymized_value="[EMAIL_1]",
            locations=["contact_info"]
        ),
        PIIEntity(
            entity_type="PHONE",
            original_value="+1-555-123-4567",
            anonymized_value="[PHONE_1]",
            locations=["contact_info"]
        )
    ]
    
    redaction_map = RedactionMap(
        redaction_id="redact_456",
        timestamp="2025-11-24T21:00:00",
        entities=pii_entities
    )
    
    assert len(redaction_map.entities) == 3
    assert redaction_map.entities[0].entity_type == "NAME"
    assert redaction_map.entities[1].original_value == "john.doe@email.com"
    assert redaction_map.entities[2].anonymized_value == "[PHONE_1]"
    
    print("✓ RedactionMap with nested PIIEntity list works correctly")
    
    print("\n" + "="*60)
    print("✅ All nested schema relationship tests passed!")
    print("="*60)

if __name__ == "__main__":
    print("\nTesting Nested Schema Relationships...\n")
    test_complex_nested_structures()
