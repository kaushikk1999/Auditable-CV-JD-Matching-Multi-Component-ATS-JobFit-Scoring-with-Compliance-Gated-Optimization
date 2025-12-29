import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.pii_redactor import PIIRedactor

def test_email_redaction():
    """Test email redaction."""
    redactor = PIIRedactor(seed=42)
    
    text = "Contact me at john.doe@example.com for opportunities"
    anonymized, redaction_map = redactor.redact_cv_text(text)
    
    # Original email should be gone
    assert "john.doe@example.com" not in anonymized
    
    # Should have redaction record
    assert len(redaction_map.entities) >= 1
    assert any(e.entity_type == "EMAIL" for e in redaction_map.entities)
    
    print("✅ Email redaction test passed")

def test_phone_redaction():
    """Test phone number redaction."""
    redactor = PIIRedactor(seed=42)
    
    text = "Call me at 555-123-4567"
    anonymized, redaction_map = redactor.redact_cv_text(text)
    
    assert "555-123-4567" not in anonymized
    assert any(e.entity_type == "PHONE" for e in redaction_map.entities)
    
    print("✅ Phone redaction test passed")

if __name__ == "__main__":
    test_email_redaction()
    test_phone_redaction()
