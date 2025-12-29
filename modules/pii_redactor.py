import re
import hashlib
from typing import Dict, List, Tuple
from faker import Faker
from modules.schemas import PIIEntity, RedactionMap, AnonymizedCV
from datetime import datetime
import uuid
import json

class PIIRedactor:
    """Detects and redacts personally identifiable information."""
    
    def __init__(self, seed: int = 42):
        """
        Args:
            seed: Random seed for reproducible fake data generation
        """
        self.fake = Faker()
        Faker.seed(seed)
        self.seed = seed
    
    def redact_cv_text(self, cv_text: str) -> Tuple[str, RedactionMap]:
        """
        Redact PII from raw CV text.
        
        Returns:
            (anonymized_text, redaction_map)
        """
        entities = []
        anonymized = cv_text
        
        # Detect and redact emails
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, cv_text)
        for email in emails:
            fake_email = self.fake.email()
            entities.append(PIIEntity(
                entity_type="EMAIL",
                original_value=email,
                anonymized_value=fake_email,
                locations=["raw_text"]
            ))
            anonymized = anonymized.replace(email, fake_email)
        
        # Detect and redact phone numbers
        phone_pattern = r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, cv_text)
        for phone in phones:
            phone_str = ''.join(phone) if isinstance(phone, tuple) else phone
            fake_phone = self.fake.phone_number()
            entities.append(PIIEntity(
                entity_type="PHONE",
                original_value=phone_str,
                anonymized_value=fake_phone,
                locations=["raw_text"]
            ))
            anonymized = anonymized.replace(phone_str, fake_phone)
        
        # Detect and redact common name patterns (first line often contains name)
        lines = cv_text.split('\n')
        if lines:
            first_line = lines[0].strip()
            # If first line looks like a name (2-3 capitalized words, <50 chars)
            if len(first_line) < 50 and re.match(r'^[A-Z][a-z]+ [A-Z][a-z]+', first_line):
                fake_name = self.fake.name()
                entities.append(PIIEntity(
                    entity_type="NAME",
                    original_value=first_line,
                    anonymized_value=fake_name,
                    locations=["raw_text_line_1"]
                ))
                anonymized = anonymized.replace(first_line, fake_name, 1)
        
        # Create redaction map
        redaction_id = str(uuid.uuid4())
        redaction_map = RedactionMap(
            redaction_id=redaction_id,
            timestamp=datetime.now().isoformat(),
            entities=entities
        )
        
        return anonymized, redaction_map
    
    def redact_structured_cv(self, cv_dict: Dict) -> Tuple[Dict, RedactionMap]:
        """
        Redact PII from structured CV dictionary.
        
        Returns:
            (anonymized_cv_dict, redaction_map)
        """
        entities = []
        anonymized = json.loads(json.dumps(cv_dict))  # Deep copy
        
        # Redact contact info
        if "contact_info" in anonymized:
            contact = anonymized["contact_info"]
            
            # Name
            if contact.get("full_name"):
                original_name = contact["full_name"]
                fake_name = self.fake.name()
                entities.append(PIIEntity(
                    entity_type="NAME",
                    original_value=original_name,
                    anonymized_value=fake_name,
                    locations=["contact_info.full_name"]
                ))
                contact["full_name"] = fake_name
            
            # Email
            if contact.get("email"):
                original_email = contact["email"]
                fake_email = self.fake.email()
                entities.append(PIIEntity(
                    entity_type="EMAIL",
                    original_value=original_email,
                    anonymized_value=fake_email,
                    locations=["contact_info.email"]
                ))
                contact["email"] = fake_email
            
            # Phone
            if contact.get("phone"):
                original_phone = contact["phone"]
                fake_phone = self.fake.phone_number()
                entities.append(PIIEntity(
                    entity_type="PHONE",
                    original_value=original_phone,
                    anonymized_value=fake_phone,
                    locations=["contact_info.phone"]
                ))
                contact["phone"] = fake_phone
            
            # Location (city/state only, keep general)
            if contact.get("location"):
                original_loc = contact["location"]
                fake_loc = f"{self.fake.city()}, {self.fake.state_abbr()}"
                entities.append(PIIEntity(
                    entity_type="LOCATION",
                    original_value=original_loc,
                    anonymized_value=fake_loc,
                    locations=["contact_info.location"]
                ))
                contact["location"] = fake_loc
        
        # Optionally redact company names (keep for now, but track)
        # This preserves experience context while allowing full anonymization if needed
        
        redaction_id = str(uuid.uuid4())
        redaction_map = RedactionMap(
            redaction_id=redaction_id,
            timestamp=datetime.now().isoformat(),
            entities=entities
        )
        
        return anonymized, redaction_map
    
    def create_anonymized_cv(self, cv_text: str, structured_cv_dict: Dict) -> AnonymizedCV:
        """
        Create fully anonymized CV package.
        
        Returns:
            AnonymizedCV with both text and structured data anonymized
        """
        # Hash original for tracking
        original_hash = hashlib.sha256(cv_text.encode()).hexdigest()
        
        # Redact structured data
        anon_structured, redaction_map = self.redact_structured_cv(structured_cv_dict)
        
        # Redact raw text using same mapping
        anon_text = cv_text
        for entity in redaction_map.entities:
            anon_text = anon_text.replace(entity.original_value, entity.anonymized_value)
        
        return AnonymizedCV(
            original_hash=original_hash,
            redaction_id=redaction_map.redaction_id,
            anonymized_text=anon_text,
            structured_data=anon_structured
        )
