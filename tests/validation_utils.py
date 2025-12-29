import os
import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Phase7Validation")

def setup_logging():
    """Ensure logging is configured."""
    return logger

def check_file_exists(path: Union[str, Path], min_size_bytes: int = 0) -> bool:
    """Check if a file exists and has a minimum size."""
    p = Path(path)
    if not p.exists():
        logger.error(f"File not found: {path}")
        return False
    
    if not p.is_file():
        logger.error(f"Path is not a file: {path}")
        return False
        
    size = p.stat().st_size
    if size < min_size_bytes:
        logger.error(f"File {path} is too small: {size} bytes (min {min_size_bytes})")
        return False
        
    logger.info(f"File check passed: {path} ({size} bytes)")
    return True

def normalize_string(s: str) -> str:
    """Normalize string for robust comparison (trim, collapse whitespace)."""
    if not s:
        return ""
    return " ".join(s.split())

def normalize_bullet(s: str) -> str:
    """Normalize bullet points to remove common prefixes."""
    if not s:
        return ""
    s = s.strip()
    # Remove common bullet markers
    s = re.sub(r'^[\u2022\-\*]\s*', '', s)
    return normalize_string(s)

def save_report(data: Dict[str, Any], path: Union[str, Path]) -> None:
    """Save a structured report to JSON."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logger.info(f"Report saved to {path}")

def log_test_result(test_id: str, test_name: str, status: str, details: str):
    """Log a standardized test result."""
    level = logging.INFO if status == "PASS" else logging.WARNING if status == "WARN" else logging.ERROR
    logger.log(level, f"[{status}] {test_id}: {test_name} - {details}")

class TestResult:
    def __init__(self, test_id: str, name: str):
        self.test_id = test_id
        self.name = name
        self.status = "PENDING"
        self.details = []
        self.artifacts = []

    def pass_test(self, message: str = ""):
        self.status = "PASS"
        if message:
            self.details.append(message)
        log_test_result(self.test_id, self.name, "PASS", message)

    def fail_test(self, message: str):
        self.status = "FAIL"
        self.details.append(message)
        log_test_result(self.test_id, self.name, "FAIL", message)

    def warn_test(self, message: str):
        self.status = "WARN"
        self.details.append(message)
        log_test_result(self.test_id, self.name, "WARN", message)
    
    def add_detail(self, detail: str):
        self.details.append(detail)

    def to_dict(self):
        return {
            "id": self.test_id,
            "name": self.name,
            "status": self.status,
            "details": self.details,
            "artifacts": self.artifacts
        }
