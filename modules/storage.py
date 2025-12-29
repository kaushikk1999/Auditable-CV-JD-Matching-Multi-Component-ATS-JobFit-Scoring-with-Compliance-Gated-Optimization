import json
from datetime import datetime
from pathlib import Path
from typing import Dict
from config.settings import DATA_RAW_DIR, DATA_PROCESSED_DIR
from modules.schemas import StructuredCV, EnhancedJD, AnalysisReport

class Storage:
    """Handles persistence of CV, JD, and parsed data."""
    
    @staticmethod
    def save_raw_cv(cv_text: str, filename: str = "cv_raw.txt") -> Path:
        """Save raw CV text."""
        filepath = DATA_RAW_DIR / filename
        filepath.write_text(cv_text, encoding='utf-8')
        return filepath
    
    @staticmethod
    def save_raw_jd(jd_text: str, filename: str = "jd_raw.txt") -> Path:
        """Save raw JD text."""
        filepath = DATA_RAW_DIR / filename
        filepath.write_text(jd_text, encoding='utf-8')
        return filepath

    @staticmethod
    def load_raw_cv(filename: str = "cv_raw.txt") -> str:
        """Load raw CV text."""
        filepath = DATA_RAW_DIR / filename
        if not filepath.exists():
            return ""
        return filepath.read_text(encoding='utf-8')

    @staticmethod
    def load_raw_jd(filename: str = "jd_raw.txt") -> str:
        """Load raw JD text."""
        filepath = DATA_RAW_DIR / filename
        if not filepath.exists():
            return ""
        return filepath.read_text(encoding='utf-8')
    
    @staticmethod
    def save_parsed_jd(jd_structure: dict, filename: str = "jd_parsed.json") -> Path:
        """Save parsed JD structure as JSON."""
        filepath = DATA_PROCESSED_DIR / filename
        
        # Add metadata
        output = {
            "extracted_at": datetime.now().isoformat(),
            "data": jd_structure
        }
        
        filepath.write_text(json.dumps(output, indent=2), encoding='utf-8')
        return filepath
    
    @staticmethod
    def load_parsed_jd(filename: str = "jd_parsed.json") -> dict:
        """Load parsed JD structure."""
        filepath = DATA_PROCESSED_DIR / filename
        if not filepath.exists():
            return {}
        return json.loads(filepath.read_text(encoding='utf-8'))
    
    @staticmethod
    def save_structured_cv(structured_cv, filename: str = "cv_structured.json") -> Path:
        """Save structured CV with validation."""
        filepath = DATA_PROCESSED_DIR / filename
        
        # Handle both Pydantic models and dicts
        if hasattr(structured_cv, 'model_dump'):
            cv_data = structured_cv.model_dump()  # Pydantic v2 method
        else:
            cv_data = structured_cv  # Already a dict
        
        output = {
            "structured_at": datetime.now().isoformat(),
            "schema_version": "2.0",
            "data": cv_data
        }
        
        filepath.write_text(json.dumps(output, indent=2), encoding='utf-8')
        return filepath
    
    @staticmethod
    def load_structured_cv(filename: str = "cv_structured.json") -> StructuredCV:
        """Load and validate structured CV."""
        filepath = DATA_PROCESSED_DIR / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Structured CV not found: {filepath}")
        
        data = json.loads(filepath.read_text(encoding='utf-8'))
        return StructuredCV(**data["data"])
    
    @staticmethod
    def save_enhanced_jd(enhanced_jd: EnhancedJD, filename: str = "jd_enhanced.json") -> Path:
        """Save enhanced JD with validation."""
        filepath = DATA_PROCESSED_DIR / filename
        
        output = {
            "enhanced_at": datetime.now().isoformat(),
            "schema_version": "2.0",
            "data": enhanced_jd.model_dump()
        }
        
        filepath.write_text(json.dumps(output, indent=2), encoding='utf-8')
        return filepath
    
    @staticmethod
    def load_enhanced_jd(filename: str = "jd_enhanced.json") -> EnhancedJD:
        """Load and validate enhanced JD."""
        filepath = DATA_PROCESSED_DIR / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Enhanced JD not found: {filepath}")
        
        data = json.loads(filepath.read_text(encoding='utf-8'))
        return EnhancedJD(**data["data"])

    @staticmethod
    def save_analysis_report(report: AnalysisReport, filename: str = "analysis_report.json") -> Path:
        """Save analysis report."""
        from modules.schemas import AnalysisReport
        filepath = DATA_PROCESSED_DIR / filename
        filepath.write_text(report.model_dump_json(indent=2), encoding='utf-8')
        return filepath

    @staticmethod
    def load_analysis_report(filename: str = "analysis_report.json") -> AnalysisReport:
        """Load analysis report."""
        from modules.schemas import AnalysisReport
        filepath = DATA_PROCESSED_DIR / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Analysis report not found: {filepath}")
        
        data = json.loads(filepath.read_text(encoding='utf-8'))
        return AnalysisReport(**data)

    @staticmethod
    def save_redaction_map(redaction_map, filename: str = "redaction_map.json") -> Path:
        """Save PII redaction map."""
        from modules.schemas import RedactionMap
        filepath = DATA_PROCESSED_DIR / filename
        filepath.write_text(redaction_map.model_dump_json(indent=2), encoding='utf-8')
        return filepath

    @staticmethod
    def save_compliance_report(report: dict, filename: str = "compliance_report.json") -> Path:
        """Save compliance audit report."""
        filepath = DATA_PROCESSED_DIR / filename
        filepath.write_text(json.dumps(report, indent=2), encoding='utf-8')
        return filepath

    @staticmethod
    def load_compliance_report(filename: str = "compliance_report.json") -> dict:
        """Load compliance audit report."""
        filepath = DATA_PROCESSED_DIR / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Compliance report not found: {filepath}")
        return json.loads(filepath.read_text(encoding='utf-8'))

    @staticmethod
    def save_scoring_report(report: Dict, filename: str = "scoring_report.json") -> Path:
        """Save scoring report."""
        filepath = DATA_PROCESSED_DIR / filename
        filepath.write_text(json.dumps(report, indent=2), encoding='utf-8')
        return filepath

    @staticmethod
    def load_scoring_report(filename: str = "scoring_report.json") -> Dict:
        """Load scoring report."""
        filepath = DATA_PROCESSED_DIR / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Scoring report not found: {filepath}")
        return json.loads(filepath.read_text(encoding='utf-8'))

    @staticmethod
    def save_optimized_cv(optimized_cv, filename: str = "cv_optimized.json") -> Path:
        """Save optimized/rewritten CV."""
        filepath = DATA_PROCESSED_DIR / filename
        
        # Handle both Pydantic models and dicts
        if hasattr(optimized_cv, 'model_dump'):
            cv_data = optimized_cv.model_dump()
        else:
            cv_data = optimized_cv
        
        output = {
            "optimized_at": datetime.now().isoformat(),
            "schema_version": "2.0",
            "data": cv_data
        }
        
        filepath.write_text(json.dumps(output, indent=2), encoding='utf-8')
        return filepath

    @staticmethod
    def load_optimized_cv(filename: str = "cv_optimized.json") -> Dict:
        """Load optimized CV."""
        filepath = DATA_PROCESSED_DIR / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Optimized CV not found: {filepath}")
        
        data = json.loads(filepath.read_text(encoding='utf-8'))
        return data["data"]

