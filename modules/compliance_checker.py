import re
from typing import List, Dict, Set, Tuple
from collections import Counter
from config.word_lists import (
    APPROVED_ACTION_VERBS, BANNED_TERMS, STOPWORDS, 
    CONTRACTIONS_MAP, METRIC_PATTERNS
)
from config.settings import (
    ENFORCE_UNIQUE_WORDS, ENFORCE_STOPWORD_BAN, ENFORCE_BUZZWORD_BAN,
    ALLOW_NUMERIC_REPETITION, TARGET_WORD_COUNT_MIN, TARGET_WORD_COUNT_MAX,
    TARGET_BULLET_COUNT_MIN, TARGET_BULLET_COUNT_MAX
)
from rapidfuzz import fuzz

class ComplianceChecker:
    """
    Comprehensive ATS compliance checker implementing all 7 audit rules.
    """
    
    def __init__(self):
        # Preprocess word lists for efficient lookup
        self.approved_verbs_lower = {v.lower() for v in APPROVED_ACTION_VERBS}
        self.banned_terms_lower = {term.lower() for term in BANNED_TERMS}
        self.stopwords_lower = {sw.lower() for sw in STOPWORDS}
        self.metric_regex = re.compile('|'.join(METRIC_PATTERNS))
    
    # ========== 1. BUZZWORD AUDIT ==========
    
    def check_buzzwords(self, text: str) -> Dict:
        """
        Check 1: Buzzword Audit
        Detects banned jargon and buzzwords.
        
        Returns:
            {
                "passed": bool,
                "violations": List[str],
                "violation_count": int,
                "status": "NO_BUZZWORDS_PRESENT" | "BUZZWORD_BREACH"
            }
        """
        violations = []
        text_lower = text.lower()
        
        # Check exact matches
        for term in BANNED_TERMS:
            term_lower = term.lower()
            if term_lower in text_lower:
                # Find actual occurrences with context
                pattern = re.compile(r'\b' + re.escape(term_lower) + r'\b', re.IGNORECASE)
                matches = pattern.findall(text)
                if matches:
                    violations.append(term)
        
        # Check fuzzy matches for common variants
        words_in_text = set(re.findall(r'\b[a-zA-Z]{4,}\b', text_lower))
        for word in words_in_text:
            for banned in self.banned_terms_lower:
                if len(word) > 5 and fuzz.ratio(word, banned) > 70:
                    if word not in [v.lower() for v in violations]:
                        violations.append(word)
        
        passed = len(violations) == 0
        
        return {
            "passed": passed,
            "violations": violations,
            "violation_count": len(violations),
            "status": "NO_BUZZWORDS_PRESENT" if passed else "BUZZWORD_BREACH"
        }
    
    # ========== 2. STOPWORD AUDIT ==========
    
    def check_stopwords(self, text: str) -> Dict:
        """
        Check 2: Stopword Audit
        Validates zero stopwords in output.
        Expands contractions first if CONTRACTION_EXPANSION is enabled.
        
        Returns:
            {
                "passed": bool,
                "violations": List[str],
                "violation_count": int,
                "status": "NO_STOPWORDS_PRESENT" | "STOPWORD_BREACH"
            }
        """
        # Expand contractions
        expanded_text = text
        for contraction, expansion in CONTRACTIONS_MAP.items():
            expanded_text = re.sub(
                r'\b' + re.escape(contraction) + r'\b', 
                expansion, 
                expanded_text, 
                flags=re.IGNORECASE
            )
        
        # Extract words
        words = re.findall(r'\b[a-zA-Z]+\b', expanded_text.lower())
        
        # Filter numbers, emails, URLs (excluded from stopword check)
        violations = []
        for word in words:
            if word in self.stopwords_lower:
                violations.append(word)
        
        # Remove duplicates while preserving order
        violations = list(dict.fromkeys(violations))
        
        passed = len(violations) == 0
        
        return {
            "passed": passed,
            "violations": violations,
            "violation_count": len(violations),
            "status": "NO_STOPWORDS_PRESENT" if passed else "STOPWORD_BREACH"
        }
    
    # ========== 3. WORD UNIQUENESS AUDIT ==========
    
    def check_word_uniqueness(self, text: str) -> Dict:
        """
        Check 3: Word Uniqueness Report
        Verifies each word appears only once across entire CV.
        Numbers are excluded if ALLOW_NUMERIC_REPETITION is True.
        
        Returns:
            {
                "passed": bool,
                "duplicates": Dict[str, int],  # word -> count
                "violation_count": int,
                "status": "ALL_WORDS_UNIQUE" | "DUPLICATE_WORDS_BREACH"
            }
        """
        # Extract all words
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        
        # Count occurrences
        word_counts = Counter(words)
        
        # Find duplicates (words appearing more than once)
        duplicates = {word: count for word, count in word_counts.items() if count > 1}
        
        passed = len(duplicates) == 0
        
        return {
            "passed": passed,
            "duplicates": duplicates,
            "violation_count": len(duplicates),
            "total_duplicate_instances": sum(duplicates.values()) - len(duplicates) if duplicates else 0,
            "status": "ALL_WORDS_UNIQUE" if passed else "DUPLICATE_WORDS_BREACH"
        }
    
    # ========== 4. DUPLICATE TERM CHECK ==========
    
    def check_duplicate_terms(self, text: str) -> Dict:
        """
        Check 4: Duplicate Term Check
        Similar to uniqueness but focuses on skill terms and phrases.
        
        Returns:
            {
                "passed": bool,
                "duplicate_phrases": List[str],
                "violation_count": int,
                "status": "NO_DUPLICATES" | "DUPLICATE_DETECTED"
            }
        """
        # Extract 2-3 word phrases (common skill patterns)
        phrases = []
        words = re.findall(r'\b[a-zA-Z]+\b', text)
        
        # Bigrams
        for i in range(len(words) - 1):
            phrase = f"{words[i]} {words[i+1]}".lower()
            phrases.append(phrase)
        
        # Trigrams
        for i in range(len(words) - 2):
            phrase = f"{words[i]} {words[i+1]} {words[i+2]}".lower()
            phrases.append(phrase)
        
        # Count duplicates
        phrase_counts = Counter(phrases)
        duplicate_phrases = [phrase for phrase, count in phrase_counts.items() if count > 1]
        
        # Filter out common patterns (e.g., dates)
        duplicate_phrases = [p for p in duplicate_phrases if not re.match(r'\w+ \d{4}', p)]
        
        passed = len(duplicate_phrases) == 0
        
        return {
            "passed": passed,
            "duplicate_phrases": duplicate_phrases[:10],  # Top 10
            "violation_count": len(duplicate_phrases),
            "status": "NO_DUPLICATES" if passed else "DUPLICATE_DETECTED"
        }
    
    # ========== 5. QUANTIFICATION INTEGRITY AUDIT ==========
    
    def check_quantification(self, bullets: List[str]) -> Dict:
        """
        Check 5: Quantification Integrity Audit
        Verifies bullets follow [Action Verb] + [Accomplishment] + [Metric] structure.
        
        Args:
            bullets: List of bullet point text strings
        
        Returns:
            {
                "passed": bool,
                "compliant_bullets": List[int],
                "non_compliant_bullets": List[int],
                "compliance_rate": float,
                "status": "ALL_POINTS_QUANTIFIED" | "NON_QUANTIFIED_POINTS_FOUND"
            }
        """
        compliant = []
        non_compliant = []
        
        for idx, bullet in enumerate(bullets):
            has_verb = self._starts_with_action_verb(bullet)
            has_metric = self._contains_metric(bullet)
            
            if has_verb and has_metric:
                compliant.append(idx)
            else:
                non_compliant.append(idx)
        
        total = len(bullets)
        compliance_rate = len(compliant) / total if total > 0 else 0.0
        passed = len(non_compliant) == 0
        
        return {
            "passed": passed,
            "compliant_bullets": compliant,
            "non_compliant_bullets": non_compliant,
            "compliance_rate": compliance_rate,
            "total_bullets": total,
            "status": "ALL_POINTS_QUANTIFIED" if passed else "NON_QUANTIFIED_POINTS_FOUND"
        }
    
    def _starts_with_action_verb(self, bullet: str) -> bool:
        """Check if bullet starts with approved action verb."""
        words = bullet.strip().split()
        if not words:
            return False
        first_word = words[0].lower().rstrip('.,;:')
        return first_word in self.approved_verbs_lower
    
    def _contains_metric(self, bullet: str) -> bool:
        """Check if bullet contains quantifiable metric."""
        return bool(self.metric_regex.search(bullet))
    
    # ========== 6. BREVITY & WORD COUNT ANALYSIS ==========
    
    def check_brevity(self, text: str, bullet_count: int) -> Dict:
        """
        Check 6: Brevity & Word Count Analysis
        Validates word count (400-450) and bullet density (12-15).
        
        Returns:
            {
                "passed": bool,
                "word_count": int,
                "bullet_count": int,
                "word_count_status": "WITHIN_RANGE" | "WORDCOUNT_ADJUSTMENT_REQUIRED",
                "bullet_count_status": "BULLET_COUNT_OK" | "BULLET_COUNT_OUT_OF_RANGE"
            }
        """
        # Count words (exclude numbers, special chars)
        words = re.findall(r'\b[a-zA-Z]+\b', text)
        word_count = len(words)
        
        word_in_range = TARGET_WORD_COUNT_MIN <= word_count <= TARGET_WORD_COUNT_MAX
        bullet_in_range = TARGET_BULLET_COUNT_MIN <= bullet_count <= TARGET_BULLET_COUNT_MAX
        
        return {
            "passed": word_in_range and bullet_in_range,
            "word_count": word_count,
            "word_count_target": f"{TARGET_WORD_COUNT_MIN}-{TARGET_WORD_COUNT_MAX}",
            "word_count_status": "WITHIN_RANGE" if word_in_range else "WORDCOUNT_ADJUSTMENT_REQUIRED",
            "bullet_count": bullet_count,
            "bullet_count_target": f"{TARGET_BULLET_COUNT_MIN}-{TARGET_BULLET_COUNT_MAX}",
            "bullet_count_status": "BULLET_COUNT_OK" if bullet_in_range else "BULLET_COUNT_OUT_OF_RANGE"
        }
    
    # ========== 7. BULLET POINT DENSITY CHECK ==========
    
    def check_bullet_density(self, bullets_by_section: Dict[str, int]) -> Dict:
        """
        Check 7: Bullet Point Density Check
        Analyzes distribution of bullets across sections.
        
        Args:
            bullets_by_section: {"experience": 10, "projects": 3, ...}
        
        Returns:
            {
                "passed": bool,
                "total_bullets": int,
                "distribution": Dict[str, int],
                "recommendations": List[str]
            }
        """
        total_bullets = sum(bullets_by_section.values())
        passed = TARGET_BULLET_COUNT_MIN <= total_bullets <= TARGET_BULLET_COUNT_MAX
        
        recommendations = []
        
        # Check experience dominance (should be 70-80% of bullets)
        if "experience" in bullets_by_section:
            exp_ratio = bullets_by_section["experience"] / total_bullets if total_bullets > 0 else 0
            if exp_ratio < 0.7 or exp_ratio > 0.8:
                recommendations.append("Experience section should contain 70-80% of total bullets")
        
        # Check for too many project bullets
        if "projects" in bullets_by_section:
            proj_ratio = bullets_by_section["projects"] / total_bullets if total_bullets > 0 else 0
            if proj_ratio > 0.3:
                recommendations.append("Projects section should not exceed 30% of total bullets")
        
        return {
            "passed": passed,
            "total_bullets": total_bullets,
            "distribution": bullets_by_section,
            "recommendations": recommendations,
            "status": "BULLET_COUNT_OK" if passed else "BULLET_COUNT_OUT_OF_RANGE"
        }


class ComplianceAuditor:
    """
    Orchestrates all compliance checks and generates comprehensive reports.
    """
    
    def __init__(self):
        self.checker = ComplianceChecker()
    
    def audit_cv_text(self, cv_text: str, bullets: List[str] = None) -> Dict:
        """
        Run full compliance audit on CV text.
        
        Args:
            cv_text: Full CV text
            bullets: List of all bullet points from experience + projects
        
        Returns:
            Comprehensive audit report with all 7 checks
        """
        if bullets is None:
            bullets = self._extract_bullets_from_text(cv_text)
        
        bullet_count = len(bullets)
        
        # Run all checks
        buzzword_result = self.checker.check_buzzwords(cv_text)
        stopword_result = self.checker.check_stopwords(cv_text)
        uniqueness_result = self.checker.check_word_uniqueness(cv_text)
        duplicate_result = self.checker.check_duplicate_terms(cv_text)
        quantification_result = self.checker.check_quantification(bullets)
        brevity_result = self.checker.check_brevity(cv_text, bullet_count)
        
        # Bullet density (default to flat distribution if sections not provided)
        # In a real scenario, we'd pass section-specific counts. Here we assume generic.
        bullets_by_section = {"general": bullet_count}
        density_result = self.checker.check_bullet_density(bullets_by_section)
        
        # Determine overall pass/fail
        critical_checks = [
            buzzword_result["passed"] if ENFORCE_BUZZWORD_BAN else True,
            stopword_result["passed"] if ENFORCE_STOPWORD_BAN else True,
            uniqueness_result["passed"] if ENFORCE_UNIQUE_WORDS else True,
        ]
        
        overall_passed = all(critical_checks)
        
        return {
            "overall_passed": overall_passed,
            "timestamp": __import__('datetime').datetime.now().isoformat(),
            "checks": {
                "buzzword_audit": buzzword_result,
                "stopword_audit": stopword_result,
                "word_uniqueness": uniqueness_result,
                "duplicate_terms": duplicate_result,
                "quantification_integrity": quantification_result,
                "brevity_analysis": brevity_result,
                "bullet_density": density_result
            },
            "critical_violations": [
                check for check in ["buzzword_audit", "stopword_audit", "word_uniqueness"]
                if not overall_passed
            ],
            "warnings": [
                check for check, result in [
                    ("duplicate_terms", duplicate_result),
                    ("quantification_integrity", quantification_result),
                    ("brevity_analysis", brevity_result),
                    ("bullet_density", density_result)
                ] if not result["passed"]
            ]
        }
    
    def _extract_bullets_from_text(self, text: str) -> List[str]:
        """Extract bullet points using common patterns."""
        # Look for lines starting with bullets or dashes
        lines = text.split('\n')
        bullets = []
        
        for line in lines:
            line = line.strip()
            # Check if line starts with bullet markers or action verbs
            if re.match(r'^[•\-\*]\s+', line) or any(line.lower().startswith(verb.lower()) for verb in list(APPROVED_ACTION_VERBS)[:50]):
                cleaned = re.sub(r'^[•\-\*]\s+', '', line)
                if len(cleaned) > 20:  # Minimum bullet length
                    bullets.append(cleaned)
        
        return bullets
