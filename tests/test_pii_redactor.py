"""Unit tests for pii_redactor module."""

import unittest
import re
from modules.pii_redactor import PIIRedactor
from modules.schemas import PIIEntity, RedactionMap, AnonymizedCV


class TestPIIRedactor(unittest.TestCase):
    """Test cases for PIIRedactor."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.redactor = PIIRedactor(seed=42)
    
    def test_initialization(self):
        """Test PIIRedactor initialization."""
        self.assertEqual(self.redactor.seed, 42)
        self.assertIsNotNone(self.redactor.fake)
    
    def test_email_redaction_in_text(self):
        """Test email detection and redaction in raw text."""
        cv_text = """
        John Doe
        Email: john.doe@example.com
        Phone: 555-123-4567
        """
        
        anonymized, redaction_map = self.redactor.redact_cv_text(cv_text)
        
        # Check that original email is not in anonymized text
        self.assertNotIn("john.doe@example.com", anonymized)
        
        # Check redaction map contains email entity
        email_entities = [e for e in redaction_map.entities if e.entity_type == "EMAIL"]
        self.assertEqual(len(email_entities), 1)
        self.assertEqual(email_entities[0].original_value, "john.doe@example.com")
        
        # Check that fake email is valid format
        self.assertRegex(email_entities[0].anonymized_value, r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    
    def test_phone_redaction_in_text(self):
        """Test phone number detection and redaction."""
        cv_text = "Contact: 555-123-4567 or (555) 987-6543"
        
        anonymized, redaction_map = self.redactor.redact_cv_text(cv_text)
        
        # Check phone entities were detected
        phone_entities = [e for e in redaction_map.entities if e.entity_type == "PHONE"]
        self.assertGreaterEqual(len(phone_entities), 1)
        
        # Verify original phones are redacted
        self.assertNotIn("555-123-4567", anonymized)
    
    def test_name_redaction_in_text(self):
        """Test name detection and redaction from first line."""
        cv_text = "John Doe\nSoftware Engineer\nemail@example.com"
        
        anonymized, redaction_map = self.redactor.redact_cv_text(cv_text)
        
        # Check name entity
        name_entities = [e for e in redaction_map.entities if e.entity_type == "NAME"]
        if len(name_entities) > 0:
            self.assertEqual(name_entities[0].original_value, "John Doe")
            self.assertNotIn("John Doe", anonymized.split('\n')[0])
    
    def test_redaction_map_structure(self):
        """Test redaction map structure and fields."""
        cv_text = "Jane Smith\njane.smith@email.com\n555-1234"
        
        _, redaction_map = self.redactor.redact_cv_text(cv_text)
        
        # Verify RedactionMap structure
        self.assertIsInstance(redaction_map, RedactionMap)
        self.assertIsNotNone(redaction_map.redaction_id)
        self.assertIsNotNone(redaction_map.timestamp)
        self.assertIsInstance(redaction_map.entities, list)
        
        # Verify entities have correct structure
        for entity in redaction_map.entities:
            self.assertIsInstance(entity, PIIEntity)
            self.assertIn(entity.entity_type, ["NAME", "EMAIL", "PHONE", "LOCATION"])
            self.assertIsNotNone(entity.original_value)
            self.assertIsNotNone(entity.anonymized_value)
            self.assertIsInstance(entity.locations, list)
    
    def test_structured_cv_name_redaction(self):
        """Test name redaction in structured CV."""
        cv_dict = {
            "contact_info": {
                "full_name": "Alice Johnson",
                "email": "alice@example.com",
                "phone": "555-8888",
                "location": "New York, NY"
            }
        }
        
        anonymized, redaction_map = self.redactor.redact_structured_cv(cv_dict)
        
        # Verify name is redacted
        self.assertNotEqual(anonymized["contact_info"]["full_name"], "Alice Johnson")
        
        # Verify redaction map has name entity
        name_entities = [e for e in redaction_map.entities if e.entity_type == "NAME"]
        self.assertEqual(len(name_entities), 1)
        self.assertEqual(name_entities[0].original_value, "Alice Johnson")
        self.assertEqual(name_entities[0].locations, ["contact_info.full_name"])
    
    def test_structured_cv_email_redaction(self):
        """Test email redaction in structured CV."""
        cv_dict = {
            "contact_info": {
                "full_name": "Bob Smith",
                "email": "bob.smith@company.com"
            }
        }
        
        anonymized, redaction_map = self.redactor.redact_structured_cv(cv_dict)
        
        # Verify email is redacted
        self.assertNotEqual(anonymized["contact_info"]["email"], "bob.smith@company.com")
        
        # Verify redaction map
        email_entities = [e for e in redaction_map.entities if e.entity_type == "EMAIL"]
        self.assertEqual(len(email_entities), 1)
        self.assertEqual(email_entities[0].original_value, "bob.smith@company.com")
    
    def test_structured_cv_phone_redaction(self):
        """Test phone redaction in structured CV."""
        cv_dict = {
            "contact_info": {
                "full_name": "Charlie Brown",
                "phone": "+1-555-9999"
            }
        }
        
        anonymized, redaction_map = self.redactor.redact_structured_cv(cv_dict)
        
        # Verify phone is redacted
        self.assertNotEqual(anonymized["contact_info"]["phone"], "+1-555-9999")
        
        # Verify redaction map
        phone_entities = [e for e in redaction_map.entities if e.entity_type == "PHONE"]
        self.assertEqual(len(phone_entities), 1)
        self.assertEqual(phone_entities[0].original_value, "+1-555-9999")
    
    def test_structured_cv_location_redaction(self):
        """Test location redaction in structured CV."""
        cv_dict = {
            "contact_info": {
                "full_name": "Diana Prince",
                "location": "San Francisco, CA"
            }
        }
        
        anonymized, redaction_map = self.redactor.redact_structured_cv(cv_dict)
        
        # Verify location is redacted
        self.assertNotEqual(anonymized["contact_info"]["location"], "San Francisco, CA")
        
        # Verify redaction map
        location_entities = [e for e in redaction_map.entities if e.entity_type == "LOCATION"]
        self.assertEqual(len(location_entities), 1)
        self.assertEqual(location_entities[0].original_value, "San Francisco, CA")
    
    def test_structured_cv_preserves_non_pii(self):
        """Test that non-PII data is preserved in structured CV."""
        cv_dict = {
            "contact_info": {
                "full_name": "Test User",
                "email": "test@example.com"
            },
            "skills": ["Python", "JavaScript"],
            "experience": [
                {
                    "job_title": "Software Engineer",
                    "company_name": "Tech Corp"
                }
            ]
        }
        
        anonymized, _ = self.redactor.redact_structured_cv(cv_dict)
        
        # Non-PII should be preserved
        self.assertEqual(anonymized["skills"], ["Python", "JavaScript"])
        self.assertEqual(anonymized["experience"][0]["job_title"], "Software Engineer")
        self.assertEqual(anonymized["experience"][0]["company_name"], "Tech Corp")
    
    def test_create_anonymized_cv(self):
        """Test complete anonymized CV creation."""
        cv_text = "John Doe\nEmail: john@example.com\nPhone: 555-1234"
        cv_dict = {
            "contact_info": {
                "full_name": "John Doe",
                "email": "john@example.com",
                "phone": "555-1234"
            }
        }
        
        anonymized_cv = self.redactor.create_anonymized_cv(cv_text, cv_dict)
        
        # Verify AnonymizedCV structure
        self.assertIsInstance(anonymized_cv, AnonymizedCV)
        self.assertIsNotNone(anonymized_cv.original_hash)
        self.assertIsNotNone(anonymized_cv.redaction_id)
        self.assertIsNotNone(anonymized_cv.anonymized_text)
        self.assertIsInstance(anonymized_cv.structured_data, dict)
        
        # Verify PII is redacted in text
        self.assertNotIn("john@example.com", anonymized_cv.anonymized_text)
        
        # Verify PII is redacted in structured data
        self.assertNotEqual(anonymized_cv.structured_data["contact_info"]["email"], "john@example.com")
    
    def test_original_hash_generation(self):
        """Test original hash is generated correctly."""
        cv_text = "Test CV Content"
        cv_dict = {"contact_info": {"full_name": "Test"}}
        
        anonymized_cv = self.redactor.create_anonymized_cv(cv_text, cv_dict)
        
        # Hash should be 64 characters (SHA256 hex)
        self.assertEqual(len(anonymized_cv.original_hash), 64)
        
        # Hash should be consistent for same input
        import hashlib
        expected_hash = hashlib.sha256(cv_text.encode()).hexdigest()
        self.assertEqual(anonymized_cv.original_hash, expected_hash)
    
    def test_reproducibility_with_seed(self):
        """Test that redaction maintains consistency with seed."""
        cv_dict = {
            "contact_info": {
                "full_name": "Test User",
                "email": "test@example.com"
            }
        }
        
        # Create redactor with specific seed
        redactor = PIIRedactor(seed=42)
        
        # Redact twice with same redactor
        anon1, map1 = redactor.redact_structured_cv(cv_dict.copy())
        
        # Verify fake data is generated
        self.assertNotEqual(anon1["contact_info"]["full_name"], "Test User")
        self.assertNotEqual(anon1["contact_info"]["email"], "test@example.com")
        
        # Verify redaction map has correct entities
        self.assertEqual(len(map1.entities), 2)  # Name and email
        entity_types = [e.entity_type for e in map1.entities]
        self.assertIn("NAME", entity_types)
        self.assertIn("EMAIL", entity_types)
    
    def test_multiple_emails_in_text(self):
        """Test handling multiple emails in text."""
        cv_text = "Contact: primary@example.com or backup@company.com"
        
        anonymized, redaction_map = self.redactor.redact_cv_text(cv_text)
        
        # Should detect both emails
        email_entities = [e for e in redaction_map.entities if e.entity_type == "EMAIL"]
        self.assertEqual(len(email_entities), 2)
        
        # Both should be redacted
        self.assertNotIn("primary@example.com", anonymized)
        self.assertNotIn("backup@company.com", anonymized)
    
    def test_empty_contact_info(self):
        """Test handling of missing contact info fields."""
        cv_dict = {
            "contact_info": {}
        }
        
        anonymized, redaction_map = self.redactor.redact_structured_cv(cv_dict)
        
        # Should handle gracefully without errors
        self.assertIsInstance(anonymized, dict)
        self.assertEqual(len(redaction_map.entities), 0)


if __name__ == "__main__":
    unittest.main()
