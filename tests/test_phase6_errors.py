
import sys
import os
import pytest

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.phase6_engine import generate_suggestions, RewriteSuggestionBundle

def test_phase6_handles_bad_json(monkeypatch):
    """
    Ensure that if Gemini returns invalid JSON, we don't crash,
    but return a bundle with specific error metadata.
    """
    
    # 1. Mock Gemini to return garbage
    def fake_call(*args, **kwargs):
        return {"_error": "JSON_PARSE", "_raw": "Start of text... { invalid json ..."}

    monkeypatch.setattr(
        "core.phase6_engine._call_gemini_for_suggestions",
        fake_call,
        raising=True,
    )

    # 2. Minimal inputs
    dummy_cv = {"experience": [{"bullets": ["B1"]}]} # minimal valid structure
    dummy_mapping = {"missing_critical": []}
    dummy_p4 = {}
    dummy_p5 = {"ats": {"score": 50}, "job_compatibility": {"score": 50}}
    dummy_jd = {}

    # 3. Call engine
    bundle = generate_suggestions(
        cv_shell=dummy_cv,
        mapping=dummy_mapping,
        phase4_report=dummy_p4,
        phase5_bundle=dummy_p5,
        jd_structured=dummy_jd,
        target_min_score=80.0,
    )

    # 4. Assertions
    assert isinstance(bundle, RewriteSuggestionBundle)
    
    # Should be marked as error
    assert bundle.meta.get("error") == "JSON_PARSE"
    assert "invalid json" in bundle.meta.get("raw_response", "")

    # Lists should be empty
    assert bundle.bullets == []
    assert bundle.summary == []
