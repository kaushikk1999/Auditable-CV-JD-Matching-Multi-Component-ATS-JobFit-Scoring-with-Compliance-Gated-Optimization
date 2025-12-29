"""
Smoke test / demo for gap_analyzer module.
Shows end-to-end keyword gap analysis and experience alignment.
"""

from modules.gap_analyzer import KeywordGapAnalyzer, ExperienceAligner
from modules.schemas import (
    StructuredCV, EnhancedJD, ContactInfo, SkillCategory, 
    ExperienceEntry, ExperienceBullet, KeywordTaxonomy, Summary
)


def create_sample_cv():
    """Create a sample CV for testing."""
    return StructuredCV(
        contact_info=ContactInfo(
            full_name="Alex Johnson",
            email="alex.johnson@email.com",
            phone="+1-555-123-4567",
            linkedin="linkedin.com/in/alexjohnson",
            location="San Francisco, CA"
        ),
        summary=Summary(
            text="Experienced software engineer with 6+ years building scalable cloud applications using Python, AWS, and Docker"
        ),
        skills=[
            SkillCategory(
                category_name="Programming Languages",
                skills=["Python", "JavaScript", "TypeScript", "Java"]
            ),
            SkillCategory(
                category_name="Cloud & DevOps",
                skills=["AWS", "Docker", "Jenkins", "Terraform"]
            ),
            SkillCategory(
                category_name="Frameworks",
                skills=["Django", "Flask", "React", "Node.js"]
            )
        ],
        experience=[
            ExperienceEntry(
                job_title="Senior Software Engineer",
                company_name="CloudTech Solutions",
                location="San Francisco, CA",
                start_date="Jan 2021",
                end_date="Present",
                bullets=[
                    ExperienceBullet(text="Architected and deployed microservices on AWS using Docker and Kubernetes"),
                    ExperienceBullet(text="Developed Python-based REST APIs serving 10M+ requests/day"),
                    ExperienceBullet(text="Implemented CI/CD pipelines reducing deployment time by 60%"),
                    ExperienceBullet(text="Led team of 4 engineers in migrating monolith to microservices architecture")
                ]
            ),
            ExperienceEntry(
                job_title="Software Engineer",
                company_name="StartupXYZ",
                location="Remote",
                start_date="Jun 2018",
                end_date="Dec 2020",
                bullets=[
                    ExperienceBullet(text="Built full-stack web applications using Python Django and React"),
                    ExperienceBullet(text="Optimized database queries improving performance by 40%"),
                    ExperienceBullet(text="Collaborated with product team to define technical requirements")
                ]
            )
        ]
    )


def create_sample_jd():
    """Create a sample JD for testing."""
    return EnhancedJD(
        job_title="Principal Software Engineer - Cloud Infrastructure",
        company_name="Tech Innovators Inc.",
        location="Remote",
        work_type="Full-time",
        experience_required="7+ years",
        company_overview="Leading provider of cloud infrastructure solutions",
        role_summary="Lead the design and implementation of next-generation cloud infrastructure",
        key_responsibilities=[
            "Design and architect scalable cloud infrastructure",
            "Lead engineering teams in building microservices",
            "Implement robust CI/CD pipelines",
            "Optimize system performance and reliability"
        ],
        required_skills=["Python", "AWS", "Kubernetes", "Docker", "Terraform"],
        preferred_skills=["Go", "GraphQL", "Service Mesh"],
        education="Bachelor's degree in Computer Science or equivalent",
        soft_skills=["Leadership", "Communication", "Problem-solving", "Collaboration"],
        diversity_statement="We are committed to building a diverse and inclusive team",
        recruiter_contact="jobs@techinnovators.com",
        ats_keywords=["Python", "AWS", "Kubernetes", "Cloud", "Microservices", "CI/CD"],
        keyword_taxonomy=KeywordTaxonomy(
            technical_skills=["Python", "Go"],
            tools_technologies=["AWS", "Kubernetes", "Docker", "Terraform", "GraphQL"],
            soft_skills=["Leadership", "Communication", "Problem-solving"],
            domain_knowledge=["Cloud Infrastructure", "Microservices", "DevOps"]
        )
    )


def main():
    """Run gap analysis demo."""
    print("=" * 80)
    print("GAP ANALYZER SMOKE TEST / DEMO")
    print("=" * 80)
    print()
    
    # Create sample data
    cv = create_sample_cv()
    jd = create_sample_jd()
    
    print(f"📄 CV: {cv.contact_info.full_name}")
    print(f"💼 JD: {jd.job_title} at {jd.company_name}")
    print()
    
    # Initialize analyzers
    gap_analyzer = KeywordGapAnalyzer(fuzzy_threshold=80.0)
    experience_aligner = ExperienceAligner()
    
    # Perform gap analysis
    print("🔍 Running Keyword Gap Analysis...")
    gap_result = gap_analyzer.analyze(cv, jd)
    
    print(f"\n✅ Present Keywords: {len(gap_result.present_keywords)}")
    for kw in gap_result.present_keywords[:5]:  # Show first 5
        locations_str = ", ".join(kw.cv_locations[:2])  # Show first 2 locations
        print(f"   • {kw.keyword} ({kw.jd_priority}) - Score: {kw.match_score:.1f} - Locations: {locations_str}")
    
    print(f"\n❌ Missing Keywords: {len(gap_result.missing_keywords)}")
    for kw in gap_result.missing_keywords[:5]:  # Show first 5
        print(f"   • {kw.keyword} ({kw.jd_priority})")
    
    print(f"\n⚠️  Irrelevant Keywords: {len(gap_result.irrelevant_keywords)}")
    for kw in gap_result.irrelevant_keywords[:5]:  # Show first 5
        print(f"   • {kw}")
    
    # Coverage statistics
    print("\n📊 Coverage Statistics:")
    stats = gap_result.coverage_stats
    print(f"   • Required Coverage: {stats['required_coverage']:.1%} ({stats['required_present']}/{stats['required_total']})")
    print(f"   • Preferred Coverage: {stats['preferred_coverage']:.1%} ({stats['preferred_present']}/{stats['preferred_total']})")
    print(f"   • Overall Coverage: {stats['overall_coverage']:.1%}")
    
    # Build coverage table
    print("\n📋 Building Keyword Coverage Table...")
    coverage_table = gap_analyzer.build_coverage_table(gap_result, jd)
    print(f"   Generated {len(coverage_table)} coverage entries")
    
    # Show sample missing keywords with suggestions
    missing_entries = [e for e in coverage_table if not e.present_in_cv]
    if missing_entries:
        print("\n   Sample Missing Keywords with Suggestions:")
        for entry in missing_entries[:3]:
            sections = ", ".join(entry.suggested_sections)
            print(f"   • {entry.jd_keyword} ({entry.category}) → Add to: {sections}")
    
    # Perform experience alignment
    print("\n🎯 Running Experience Alignment...")
    alignments = experience_aligner.align(cv, jd, gap_result)
    
    print(f"\n📈 Experience Relevance Rankings:")
    for i, alignment in enumerate(alignments, 1):
        print(f"\n   {i}. {alignment.job_title} at {alignment.company_name}")
        print(f"      Relevance Score: {alignment.relevance_score:.2f}")
        print(f"      Matched Keywords: {len(alignment.matched_keywords)} - {', '.join(alignment.matched_keywords[:5])}")
        print(f"      Matched Responsibilities: {len(alignment.matched_responsibilities)}")
        if alignment.bullet_scores:
            avg_bullet_score = sum(alignment.bullet_scores) / len(alignment.bullet_scores)
            print(f"      Avg Bullet Score: {avg_bullet_score:.2f}")
    
    print("\n" + "=" * 80)
    print("✅ SMOKE TEST COMPLETE - All components working correctly!")
    print("=" * 80)


if __name__ == "__main__":
    main()
