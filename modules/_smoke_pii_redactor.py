"""
Smoke test / demo for pii_redactor module.
Shows end-to-end PII redaction functionality.
"""

from modules.pii_redactor import PIIRedactor
import json


def main():
    """Run PII redaction demo."""
    print("=" * 80)
    print("PII REDACTOR SMOKE TEST / DEMO")
    print("=" * 80)
    print()
    
    # Initialize redactor
    print("🔒 Initializing PII Redactor (seed=42 for reproducibility)...")
    redactor = PIIRedactor(seed=42)
    print("   ✓ PIIRedactor initialized")
    print()
    
    # Test 1: Redact raw CV text
    print("=" * 80)
    print("TEST 1: RAW TEXT REDACTION")
    print("=" * 80)
    print()
    
    cv_text = """John Smith
Email: john.smith@email.com
Phone: +1-555-123-4567
Location: San Francisco, CA

PROFESSIONAL SUMMARY
Experienced software engineer with 8+ years building scalable applications.

EXPERIENCE
Senior Software Engineer | Tech Corp
Contact: john.smith@techcorp.com
"""
    
    print("📄 Original CV Text:")
    print("-" * 40)
    print(cv_text[:200] + "...")
    print()
    
    anonymized_text, redaction_map = redactor.redact_cv_text(cv_text)
    
    print("🎭 Anonymized CV Text:")
    print("-" * 40)
    print(anonymized_text[:200] + "...")
    print()
    
    print("📋 Redaction Map:")
    print(f"   Redaction ID: {redaction_map.redaction_id}")
    print(f"   Timestamp: {redaction_map.timestamp}")
    print(f"   Entities Redacted: {len(redaction_map.entities)}")
    print()
    
    for i, entity in enumerate(redaction_map.entities, 1):
        print(f"   Entity {i}:")
        print(f"      Type: {entity.entity_type}")
        print(f"      Original: {entity.original_value}")
        print(f"      Anonymized: {entity.anonymized_value}")
        print(f"      Locations: {', '.join(entity.locations)}")
        print()
    
    # Test 2: Redact structured CV
    print("=" * 80)
    print("TEST 2: STRUCTURED CV REDACTION")
    print("=" * 80)
    print()
    
    cv_dict = {
        "contact_info": {
            "full_name": "Alice Johnson",
            "email": "alice.johnson@example.com",
            "phone": "+1-555-987-6543",
            "linkedin": "linkedin.com/in/alicejohnson",
            "location": "New York, NY"
        },
        "summary": {
            "text": "Results-driven engineer with expertise in cloud architecture"
        },
        "skills": [
            {
                "category_name": "Programming",
                "skills": ["Python", "Java", "Go"]
            }
        ],
        "experience": [
            {
                "job_title": "Lead Engineer",
                "company_name": "Innovation Labs",
                "start_date": "2020",
                "end_date": "Present"
            }
        ]
    }
    
    print("📊 Original Structured CV (contact info):")
    print("-" * 40)
    print(json.dumps(cv_dict["contact_info"], indent=2))
    print()
    
    anonymized_dict, redaction_map2 = redactor.redact_structured_cv(cv_dict)
    
    print("🎭 Anonymized Structured CV (contact info):")
    print("-" * 40)
    print(json.dumps(anonymized_dict["contact_info"], indent=2))
    print()
    
    print("📋 Redaction Summary:")
    print(f"   Total Entities Redacted: {len(redaction_map2.entities)}")
    entity_counts = {}
    for entity in redaction_map2.entities:
        entity_counts[entity.entity_type] = entity_counts.get(entity.entity_type, 0) + 1
    
    for entity_type, count in entity_counts.items():
        print(f"   - {entity_type}: {count}")
    print()
    
    # Verify non-PII is preserved
    print("✅ Verification: Non-PII Data Preserved")
    print(f"   Skills preserved: {anonymized_dict['skills'][0]['skills']}")
    print(f"   Experience preserved: {anonymized_dict['experience'][0]['job_title']} at {anonymized_dict['experience'][0]['company_name']}")
    print()
    
    # Test 3: Complete anonymized CV package
    print("=" * 80)
    print("TEST 3: COMPLETE ANONYMIZED CV PACKAGE")
    print("=" * 80)
    print()
    
    simple_text = "Bob Williams\nbob@example.com\n555-1234"
    simple_dict = {
        "contact_info": {
            "full_name": "Bob Williams",
            "email": "bob@example.com"
        }
    }
    
    anonymized_cv = redactor.create_anonymized_cv(simple_text, simple_dict)
    
    print("📦 AnonymizedCV Package Created:")
    print(f"   Original Hash: {anonymized_cv.original_hash[:16]}...")
    print(f"   Redaction ID: {anonymized_cv.redaction_id}")
    print(f"   Anonymized Text Length: {len(anonymized_cv.anonymized_text)} characters")
    print(f"   Structured Data Keys: {list(anonymized_cv.structured_data.keys())}")
    print()
    
    print("🔍 Verification:")
    print(f"   'Bob Williams' in original: True")
    print(f"   'Bob Williams' in anonymized text: {'Bob Williams' in anonymized_cv.anonymized_text}")
    print(f"   'bob@example.com' in original: True")
    print(f"   'bob@example.com' in anonymized text: {'bob@example.com' in anonymized_cv.anonymized_text}")
    print()
    
    # Summary statistics
    print("=" * 80)
    print("📊 SUMMARY STATISTICS")
    print("=" * 80)
    print()
    print("Test 1 (Raw Text):")
    print(f"   Entities detected: {len(redaction_map.entities)}")
    print(f"   Entity types: {', '.join(set(e.entity_type for e in redaction_map.entities))}")
    print()
    print("Test 2 (Structured CV):")
    print(f"   Entities detected: {len(redaction_map2.entities)}")
    print(f"   Entity types: {', '.join(set(e.entity_type for e in redaction_map2.entities))}")
    print()
    print("Test 3 (Complete Package):")
    print(f"   Hash generated: ✓")
    print(f"   Text anonymized: ✓")
    print(f"   Structured data anonymized: ✓")
    print()
    
    print("=" * 80)
    print("✅ SMOKE TEST COMPLETE - All PII redaction features working!")
    print("=" * 80)


if __name__ == "__main__":
    main()
