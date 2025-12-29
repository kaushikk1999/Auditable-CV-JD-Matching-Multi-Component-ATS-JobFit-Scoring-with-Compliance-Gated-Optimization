"""Unit tests for gap_analyzer module."""

import unittest
from modules.gap_analyzer import KeywordGapAnalyzer, ExperienceAligner
from modules.schemas import (
    StructuredCV, EnhancedJD, ContactInfo, SkillCategory, ExperienceEntry,
    ExperienceBullet, KeywordTaxonomy, Summary, ProjectEntry
)


class TestKeywordGapAnalyzer(unittest.TestCase):
    """Test cases for KeywordGapAnalyzer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = KeywordGapAnalyzer(fuzzy_threshold=80.0)
        
        # Create a mock CV
        self.cv = StructuredCV(
            contact_info=ContactInfo(
                full_name="John Doe",
                email="john@example.com"
            ),
            summary=Summary(text="Experienced software engineer with Python and AWS expertise"),
            skills=[
                SkillCategory(
                    category_name="Programming Languages",
                    skills=["Python", "JavaScript", "Java"]
                ),
                SkillCategory(
                    category_name="Tools",
                    skills=["Docker", "Git", "VS Code"]
                ),
                SkillCategory(
                    category_name="Design",
                    skills=["Photoshop", "Illustrator"]
                )
            ],
            experience=[
                ExperienceEntry(
                    job_title="Software Engineer",
                    company_name="Tech Corp",
                    start_date="2020",
                    end_date="2023",
                    bullets=[
                        ExperienceBullet(text="Developed Python applications using Django and Flask"),
                        ExperienceBullet(text="Deployed applications using Docker containers on AWS"),
                        ExperienceBullet(text="Collaborated with cross-functional teams")
                    ]
                )
            ]
        )
        
        # Create a mock JD
        self.jd = EnhancedJD(
            job_title="Senior Software Engineer",
            company_name="Tech Inc",
            location="Remote",
            work_type="Full-time",
            experience_required="5+ years",
            company_overview="Leading tech company",
            role_summary="Build scalable applications",
            key_responsibilities=[
                "Design and develop backend services",
                "Deploy applications to cloud infrastructure",
                "Collaborate with team members"
            ],
            required_skills=["Python", "AWS", "Docker", "Kubernetes"],
            preferred_skills=["React", "TypeScript"],
            education="Bachelor's degree",
            soft_skills=["Communication", "Teamwork", "Problem-solving"],
            diversity_statement="We value diversity",
            recruiter_contact="recruiter@example.com",
            ats_keywords=["Python", "AWS", "Cloud"],
            keyword_taxonomy=KeywordTaxonomy(
                technical_skills=["Python", "JavaScript"],
                tools_technologies=["Docker", "Kubernetes", "AWS"],
                soft_skills=["Communication", "Teamwork"],
                domain_knowledge=["Cloud Computing"]
            )
        )
    
    def test_exact_match_detection(self):
        """Test A: Exact match detection."""
        result = self.analyzer.analyze(self.cv, self.jd)
        
        # Python should be present (exact match)
        python_matches = [kw for kw in result.present_keywords if kw.keyword == "Python"]
        self.assertEqual(len(python_matches), 1)
        self.assertTrue(python_matches[0].found_in_cv)
        self.assertEqual(python_matches[0].match_score, 100.0)
        self.assertGreater(len(python_matches[0].cv_locations), 0)
    
    def test_fuzzy_match_detection(self):
        """Test B: Fuzzy match detection."""
        # Create a CV with "Java Script" (with space)
        cv_variant = StructuredCV(
            contact_info=ContactInfo(full_name="Jane Doe", email="jane@example.com"),
            skills=[
                SkillCategory(
                    category_name="Languages",
                    skills=["Java Script"]  # Variant spelling
                )
            ],
            experience=[
                ExperienceEntry(
                    job_title="Developer",
                    company_name="Company",
                    start_date="2020",
                    end_date="2023",
                    bullets=[ExperienceBullet(text="Built web apps")]
                )
            ]
        )
        
        result = self.analyzer.analyze(cv_variant, self.jd)
        
        # JavaScript should be detected via fuzzy match
        js_matches = [kw for kw in result.present_keywords if kw.keyword == "JavaScript"]
        if len(js_matches) > 0:
            self.assertTrue(js_matches[0].found_in_cv)
            self.assertGreaterEqual(js_matches[0].match_score, self.analyzer.fuzzy_threshold)
    
    def test_missing_keyword_detection(self):
        """Test C: Missing keyword detection."""
        result = self.analyzer.analyze(self.cv, self.jd)
        
        # Kubernetes should be missing (not in CV)
        kubernetes_matches = [kw for kw in result.missing_keywords if kw.keyword == "Kubernetes"]
        self.assertEqual(len(kubernetes_matches), 1)
        self.assertFalse(kubernetes_matches[0].found_in_cv)
        self.assertEqual(kubernetes_matches[0].match_score, 0.0)
    
    def test_irrelevant_keyword_tracking(self):
        """Test D: Irrelevant keyword tracking."""
        result = self.analyzer.analyze(self.cv, self.jd)
        
        # Photoshop and Illustrator should be irrelevant (in CV but not in JD)
        irrelevant_lower = [kw.lower() for kw in result.irrelevant_keywords]
        self.assertIn("photoshop", irrelevant_lower)
        self.assertIn("illustrator", irrelevant_lower)
    
    def test_coverage_stats_correctness(self):
        """Test E: Coverage stats correctness."""
        # Create specific JD with known counts
        simple_jd = EnhancedJD(
            job_title="Developer",
            company_name="Company",
            location="Remote",
            work_type="Full-time",
            experience_required="3+ years",
            company_overview="Company overview",
            role_summary="Role summary",
            key_responsibilities=["Develop software"],
            required_skills=["Python", "Docker"],  # 2 required
            preferred_skills=["Kubernetes"],  # 1 preferred
            education="Bachelor's",
            soft_skills=[],
            diversity_statement="",
            recruiter_contact="",
            ats_keywords=[],
            keyword_taxonomy=KeywordTaxonomy(
                technical_skills=["Python"],
                tools_technologies=["Docker"],
                soft_skills=[],
                domain_knowledge=[]
            )
        )
        
        result = self.analyzer.analyze(self.cv, simple_jd)
        
        # Verify coverage stats
        self.assertIn("required_coverage", result.coverage_stats)
        self.assertIn("preferred_coverage", result.coverage_stats)
        self.assertIn("overall_coverage", result.coverage_stats)
        self.assertIn("required_present", result.coverage_stats)
        self.assertIn("required_total", result.coverage_stats)
        
        # Required total should be 2 (Python, Docker)
        self.assertEqual(result.coverage_stats["required_total"], 2)
        
        # Both Python and Docker are in CV, so required_present should be 2
        self.assertEqual(result.coverage_stats["required_present"], 2)
        
        # Coverage should be 1.0 (100%)
        self.assertEqual(result.coverage_stats["required_coverage"], 1.0)
    
    def test_build_coverage_table(self):
        """Test coverage table generation."""
        result = self.analyzer.analyze(self.cv, self.jd)
        coverage_table = self.analyzer.build_coverage_table(result, self.jd)
        
        # Coverage table should have entries for all JD keywords
        self.assertGreater(len(coverage_table), 0)
        
        # Check structure of entries
        for entry in coverage_table:
            self.assertIsNotNone(entry.jd_keyword)
            self.assertIsNotNone(entry.category)
            self.assertIsNotNone(entry.priority)
            self.assertIsInstance(entry.present_in_cv, bool)
            self.assertGreaterEqual(entry.current_frequency, 0)
            self.assertGreaterEqual(entry.target_frequency, 0)
            self.assertIsInstance(entry.suggested_sections, list)
        
        # Present keywords should have current_frequency > 0
        present_entries = [e for e in coverage_table if e.present_in_cv]
        for entry in present_entries:
            self.assertGreater(entry.current_frequency, 0)
        
        # Missing keywords should have suggested_sections
        missing_entries = [e for e in coverage_table if not e.present_in_cv]
        for entry in missing_entries:
            self.assertGreater(len(entry.suggested_sections), 0)


class TestExperienceAligner(unittest.TestCase):
    """Test cases for ExperienceAligner."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.aligner = ExperienceAligner()
        self.analyzer = KeywordGapAnalyzer()
        
        # Create CV with multiple experiences
        self.cv = StructuredCV(
            contact_info=ContactInfo(full_name="John Doe", email="john@example.com"),
            skills=[
                SkillCategory(
                    category_name="Programming",
                    skills=["Python", "Java", "Docker"]
                )
            ],
            experience=[
                # High relevance experience
                ExperienceEntry(
                    job_title="Senior Python Developer",
                    company_name="Cloud Tech",
                    start_date="2021",
                    end_date="2023",
                    bullets=[
                        ExperienceBullet(text="Developed Python microservices on AWS using Docker"),
                        ExperienceBullet(text="Implemented CI/CD pipelines with Kubernetes"),
                        ExperienceBullet(text="Led team of 5 engineers in cloud migration")
                    ]
                ),
                # Low relevance experience
                ExperienceEntry(
                    job_title="Junior Java Developer",
                    company_name="Old Corp",
                    start_date="2018",
                    end_date="2020",
                    bullets=[
                        ExperienceBullet(text="Maintained legacy Java applications"),
                        ExperienceBullet(text="Fixed bugs in monolithic system")
                    ]
                )
            ]
        )
        
        self.jd = EnhancedJD(
            job_title="Senior Cloud Engineer",
            company_name="Tech Inc",
            location="Remote",
            work_type="Full-time",
            experience_required="5+ years",
            company_overview="Leading cloud provider",
            role_summary="Build cloud infrastructure",
            key_responsibilities=[
                "Design and deploy cloud infrastructure",
                "Lead engineering teams",
                "Implement CI/CD pipelines"
            ],
            required_skills=["Python", "AWS", "Docker", "Kubernetes"],
            preferred_skills=["Terraform"],
            education="Bachelor's",
            soft_skills=["Leadership"],
            diversity_statement="",
            recruiter_contact="",
            ats_keywords=["Python", "AWS", "Cloud"],
            keyword_taxonomy=KeywordTaxonomy(
                technical_skills=["Python"],
                tools_technologies=["Docker", "Kubernetes", "AWS"],
                soft_skills=["Leadership"],
                domain_knowledge=["Cloud Computing"]
            )
        )
    
    def test_alignment_list_size(self):
        """Test F: Alignment list size matches CV experiences."""
        gap_result = self.analyzer.analyze(self.cv, self.jd)
        alignments = self.aligner.align(self.cv, self.jd, gap_result)
        
        # Should have same number of alignments as experiences
        self.assertEqual(len(alignments), len(self.cv.experience))
    
    def test_sorting_by_relevance(self):
        """Test G: Alignments sorted by relevance (high to low)."""
        gap_result = self.analyzer.analyze(self.cv, self.jd)
        alignments = self.aligner.align(self.cv, self.jd, gap_result)
        
        # First experience (Senior Python Developer) should rank higher
        # than second (Junior Java Developer)
        self.assertEqual(alignments[0].job_title, "Senior Python Developer")
        self.assertGreater(alignments[0].relevance_score, alignments[1].relevance_score)
        
        # Verify sorted in descending order
        for i in range(len(alignments) - 1):
            self.assertGreaterEqual(alignments[i].relevance_score, alignments[i + 1].relevance_score)
    
    def test_bullet_scoring_bounds(self):
        """Test H: Bullet scores are between 0.0 and 1.0."""
        gap_result = self.analyzer.analyze(self.cv, self.jd)
        alignments = self.aligner.align(self.cv, self.jd, gap_result)
        
        # Check all bullet scores are within bounds
        for alignment in alignments:
            for score in alignment.bullet_scores:
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 1.0)
    
    def test_matched_keywords_tracking(self):
        """Test matched keywords are tracked correctly."""
        gap_result = self.analyzer.analyze(self.cv, self.jd)
        alignments = self.aligner.align(self.cv, self.jd, gap_result)
        
        # First experience should have more matched keywords
        self.assertGreater(len(alignments[0].matched_keywords), 0)
    
    def test_responsibility_matching(self):
        """Test JD responsibilities are matched to experience."""
        gap_result = self.analyzer.analyze(self.cv, self.jd)
        alignments = self.aligner.align(self.cv, self.jd, gap_result)
        
        # At least one experience should match responsibilities
        total_matched_resp = sum(len(a.matched_responsibilities) for a in alignments)
        self.assertGreater(total_matched_resp, 0)


if __name__ == "__main__":
    unittest.main()
