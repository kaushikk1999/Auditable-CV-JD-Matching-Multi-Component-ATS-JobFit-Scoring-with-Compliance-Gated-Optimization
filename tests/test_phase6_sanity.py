# tests/test_phase6_sanity.py
import sys
import os

# Add project root to path so we can import 'core'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.phase6_engine import (
    generate_suggestions,
    RewriteSuggestionBundle,
    _call_gemini_for_suggestions,
)


def test_phase6_generate_suggestions_dummy(monkeypatch):
    """
    Tiny sanity-check: ensure generate_suggestions():
    - does not raise
    - returns RewriteSuggestionBundle
    - populates at least one suggestion from fake Gemini JSON
    """

    # ---- 1) Fake Gemini JSON that respects SUGGESTIONS_RESPONSE_SCHEMA
    fake_model_json = {
        "summary": [
            {
                "impact": "HIGH",
                "reason": "Summary is generic and does not highlight data science / ML.",
                "after_example": (
                    "Data science educator and ML intern, mentoring 50+ learners "
                    "in Python, statistics, and machine learning projects."
                ),
            }
        ],
        "bullets": [
            {
                "slot_index": 0,
                "after_example": (
                    "Designed and delivered weekly ML labs, improving student "
                    "project completion rate by 30%."
                ),
            }
        ],
        "skills": [
            {
                "impact": "MEDIUM",
                "reason": "JD requires explicit mention of SQL and cloud tools.",
                "to_add": ["SQL", "Google BigQuery"],
                "to_remove": [],
            }
        ],
        "cleanup": [
            {
                "impact": "LOW",
                "reason": "Remove buzzword 'innovative' from summary.",
                "after_example": (
                    "Replace 'innovative' with a concrete result or metric."
                ),
            }
        ],
    }

    # ---- 2) Monkeypatch the Gemini call to return our fake JSON
    def fake_call(*args, **kwargs):
        return fake_model_json

    monkeypatch.setattr(
        "core.phase6_engine._call_gemini_for_suggestions",
        fake_call,
        raising=True,
    )

    # ---- 3) Build minimal dummy inputs from earlier phases
    dummy_cv_shell = {
        "summary": "Innovative data enthusiast.",
        "skills": ["Python", "Pandas"],
        "experience": [
            {
                "title": "ML Coach",
                "company": "Clevered",
                "dates": "2024",
                "bullets": ["I am a hard-working professional."],
            }
        ],
        "projects": [],
        "certificates": [],
    }

    dummy_mapping = {
        "present": ["python", "machine learning"],
        "missing_critical": [{"keyword": "SQL"}],
        "missing_bonus": [],
        "irrelevant": [],
    }

    dummy_phase4_report = {
        "buzzwords": ["innovative"],
        "stopwords": ["and", "in", "for"],
        "duplicate_words": [],
        "duplicate_lines": [],
    }

    dummy_phase5_bundle = {
        "ats": {
            "score": 55.0,
            "components": {
                "coverage": {"value": 60.0},
                "quantified": {"value": 40.0},
                "uniqueness": {"value": 70.0},
                "buzzword": {"value": 80.0},
                "stopword": {"value": 75.0},
            },
        },
        "job_compatibility": {"score": 50.0},
        "scorecard": {},
    }

    dummy_jd_structured = {
        "title": "Data Scientist – Education",
        "must_have_skills": ["Python", "SQL", "Statistics"],
        "nice_to_have_skills": ["Cloud", "BigQuery"],
    }

    # ---- 4) Call Phase-6
    bundle = generate_suggestions(
        cv_shell=dummy_cv_shell,
        mapping=dummy_mapping,
        phase4_report=dummy_phase4_report,
        phase5_bundle=dummy_phase5_bundle,
        jd_structured=dummy_jd_structured,
    )

    # ---- 5) Assertions: no crash, correct type, some content
    assert isinstance(bundle, RewriteSuggestionBundle)
    assert bundle.current_ats == 55.0
    assert bundle.current_jobcompat == 50.0

    # From fake JSON we expect at least 1 summary + 1 bullet + 1 skill + 1 cleanup
    assert len(bundle.summary) == 1
    assert len(bundle.bullets) == 1
    assert len(bundle.skills) == 1
    assert len(bundle.cleanup) == 1

    # Check content
    s0 = bundle.summary[0]
    assert s0.impact == "HIGH"
    assert "Summary is generic" in s0.reason

if __name__ == "__main__":
    # Rudimentary running if pytest not available
    import pytest
    sys.exit(pytest.main([__file__]))
