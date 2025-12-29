"""
Benchmark Dataset Schema and Management for Journal Publication.
Supports 50+ CV-JD pairs across 5 domains with ground truth annotations.
"""
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import json
from pathlib import Path

class CVJDPair(BaseModel):
    """Single CV-JD pair with metadata and annotations."""
    
    pair_id: str = Field(..., description="Unique identifier (e.g., 'swe_001')")
    domain: str = Field(..., description="Domain: software_engineering, data_science, marketing, healthcare, education")
    
    # Raw texts
    cv_text: str = Field(..., description="Raw CV text")
    jd_text: str = Field(..., description="Raw JD text")
    
    # Metadata
    match_quality: str = Field(..., description="poor, fair, good, excellent")
    expected_ats_range: List[float] = Field(..., description="[min, max] expected ATS score")
    expected_jobfit_range: List[float] = Field(..., description="[min, max] expected JobFit score")
    
    # Ground truth annotations (optional, for validation)
    human_ats_score: Optional[float] = Field(None, description="Expert-rated ATS score")
    human_jobfit_score: Optional[float] = Field(None, description="Expert-rated JobFit score")
    human_notes: Optional[str] = Field(None, description="Expert comments")
    
    # Test results (populated after running)
    actual_ats_score: Optional[float] = None
    actual_jobfit_score: Optional[float] = None
    test_timestamp: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "pair_id": "swe_001",
                "domain": "software_engineering",
                "cv_text": "Software Engineer with Python...",
                "jd_text": "Seeking Senior Python Developer...",
                "match_quality": "excellent",
                "expected_ats_range": [75, 90],
                "expected_jobfit_range": [70, 85]
            }
        }

class BenchmarkDataset(BaseModel):
    """Complete benchmark dataset for scoring validation."""
    
    dataset_version: str = "1.0"
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    description: str = "ATS CV Optimizer Benchmark Dataset for Journal Publication"
    
    pairs: List[CVJDPair] = Field(default_factory=list)
    
    @property
    def domain_counts(self) -> Dict[str, int]:
        """Count pairs by domain."""
        counts = {}
        for pair in self.pairs:
            counts[pair.domain] = counts.get(pair.domain, 0) + 1
        return counts
    
    @property
    def match_quality_counts(self) -> Dict[str, int]:
        """Count pairs by match quality."""
        counts = {}
        for pair in self.pairs:
            counts[pair.match_quality] = counts.get(pair.match_quality, 0) + 1
        return counts
    
    def save(self, filepath: str):
        """Save dataset to JSON file."""
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(self.model_dump(), f, indent=2)
    
    @classmethod
    def load(cls, filepath: str) -> 'BenchmarkDataset':
        """Load dataset from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls(**data)
    
    def add_pair(self, pair: CVJDPair):
        """Add a CV-JD pair to the dataset."""
        self.pairs.append(pair)
    
    def get_by_domain(self, domain: str) -> List[CVJDPair]:
        """Get all pairs for a specific domain."""
        return [p for p in self.pairs if p.domain == domain]
    
    def get_by_quality(self, quality: str) -> List[CVJDPair]:
        """Get all pairs with specific match quality."""
        return [p for p in self.pairs if p.match_quality == quality]

# ==========================================
# Dataset Creation Utilities
# ==========================================

def create_initial_dataset() -> BenchmarkDataset:
    """Create initial dataset with example pairs from different domains."""
    
    dataset = BenchmarkDataset()
    
    # Software Engineering - Excellent Match
    dataset.add_pair(CVJDPair(
        pair_id="swe_001",
        domain="software_engineering",
        match_quality="excellent",
        expected_ats_range=[75, 90],
        expected_jobfit_range=[70, 85],
        cv_text="""
ALEX JOHNSON
Senior Software Engineer
Email: alex@email.com | LinkedIn: linkedin.com/in/alexj

SUMMARY
Senior Software Engineer with 5+ years building scalable web applications using Python, Django, and AWS.
Expertise in microservices, REST APIs, and cloud infrastructure. Led teams delivering high-quality code.

SKILLS
Languages: Python, JavaScript, SQL, TypeScript
Frameworks: Django, Flask, React, FastAPI
Cloud: AWS (EC2, S3, Lambda), Docker, Kubernetes
Databases: PostgreSQL, MySQL, MongoDB, Redis

EXPERIENCE
Senior Software Engineer | Tech Solutions Inc | 2021-Present
• Designed RESTful APIs using Django and Python serving 1M+ daily requests
• Built microservices on AWS with Docker and Kubernetes, improving scalability 300%
• Led migration from monolithic to microservices, reducing deployment time 60%
• Mentored 4 junior developers in Python best practices

Software Engineer | Digital Innovations | 2019-2020
• Developed full-stack applications using Django, React, PostgreSQL
• Optimized database queries with Redis caching, reducing response time 40%
• Collaborated in agile sprints delivering features on time
• Achieved 90% code coverage with comprehensive unit tests

EDUCATION
Bachelor of Science in Computer Science | University of Technology | 2018
        """,
        jd_text="""
Senior Software Engineer - Tech Corp

We seek an experienced Senior Software Engineer with strong Python, Django, and cloud expertise.

REQUIREMENTS:
Education: Bachelor's in Computer Science or related field (required)

Required Skills:
- Python Programming (5+ years)
- Django Framework
- RESTful API Design  
- AWS Cloud Platform
- Docker and Kubernetes
- PostgreSQL or MySQL
- Git Version Control
- Agile Development

Preferred Skills:
- React or frontend frameworks
- CI/CD pipelines
- Microservices architecture
- MongoDB

RESPONSIBILITIES:
- Design and develop scalable backend services using Python and Django
- Build and maintain RESTful APIs
- Deploy and manage applications on AWS
- Optimize database performance
- Collaborate in agile teams
- Mentor junior engineers
- Write clean, testable code

Experience: 5+ years
Location: Remote
Type: Full-time
        """
    ))
    
    # Add more pairs for other domains will be added programmatically or manually
    
    return dataset

if __name__ == "__main__":
    # Create and save initial dataset
    dataset = create_initial_dataset()
    
    output_path = "research_package/benchmark_dataset_v1.json"
    dataset.save(output_path)
    
    print(f"✅ Created benchmark dataset with {len(dataset.pairs)} pairs")
    print(f"📊 Domain distribution: {dataset.domain_counts}")
    print(f"📊 Quality distribution: {dataset.match_quality_counts}")
    print(f"💾 Saved to: {output_path}")
