# ... (everything above unchanged)

class TestJobFitScorer:
    def setup_method(self):
        self.extractor = FeatureExtractor()
        self.scorer = JobFitScorer(self.extractor)

    def test_components_bounds(self, sample_cv, sample_jd):
        report = self.scorer.score(sample_cv, sample_jd)
        comps = report["components"]

        assert 0 <= comps["summary_similarity"] <= 100
        assert 0 <= comps["experience_alignment"] <= 100
        assert 0 <= comps["skills_alignment"] <= 100
        assert comps["education_match"] in [0.0, 50.0, 100.0]
        assert 0 <= comps["domain_relevance"] <= 100
        assert 0 <= report["jobfit_score"] <= 100

    def test_domain_relevance_uses_experience_bullets(self):
        """
        Regression test: Domain relevance must be computed from EXPERIENCE BULLETS (spec),
        not job titles (old implementation).

        We check ordering: bullet-aligned CV should score higher than unrelated-bullet CV,
        even if job titles are the same/unhelpful.
        """
        jd = {
            "keyword_taxonomy": {
                "domain_knowledge": ["cloud computing", "kubernetes", "microservices"]
            }
        }

        cv_good = {
            "experience": [
                {
                    "job_title": "Marketing Manager",  # intentionally unrelated
                    "bullets": [
                        {"text": "Deployed microservices on Kubernetes for cloud computing workloads; improved rollout frequency 2x."}
                    ]
                }
            ]
        }

        cv_bad = {
            "experience": [
                {
                    "job_title": "Marketing Manager",  # same title
                    "bullets": [
                        {"text": "Planned social media campaigns and improved brand awareness across channels."}
                    ]
                }
            ]
        }

        good = self.scorer._domain_relevance(cv_good, jd)
        bad = self.scorer._domain_relevance(cv_bad, jd)

        assert good > bad

# ... (everything below unchanged)
