# core/suggestions_models.py
from dataclasses import dataclass, field
from typing import List, Literal, Dict, Any

Impact = Literal["HIGH", "MEDIUM", "LOW"]


@dataclass
class BulletSuggestion:
    section: Literal["experience", "projects", "certificates"]
    role_index: int              # which experience/project index
    bullet_index: int | None     # None = new bullet
    impact: Impact
    reason: str                  # "Not quantified", "Missing must-have term", etc.
    before: str | None           # existing bullet or None
    after_example: str           # suggested replacement bullet (policy-clean)


@dataclass
class SummarySuggestion:
    impact: Impact
    reason: str
    before: str | None
    after_example: str


@dataclass
class SkillSuggestion:
    impact: Impact
    reason: str                  # e.g. "Missing JD must-have"
    to_add: List[str]
    to_remove: List[str]


@dataclass
class CleanupSuggestion:
    impact: Impact
    reason: str                  # "Buzzword breach", "Stopword breach"
    before: str
    after_example: str           # buzzword/stopword-free version


@dataclass
class RewriteSuggestionBundle:
    target_min_score: float      # e.g. 80.0
    current_ats: float
    current_jobcompat: float
    predicted_gain: Dict[str, float] = field(default_factory=dict)
    bullets: List[BulletSuggestion] = field(default_factory=list)
    summary: List[SummarySuggestion] = field(default_factory=list)
    skills: List[SkillSuggestion] = field(default_factory=list)
    cleanup: List[CleanupSuggestion] = field(default_factory=list)
    meta: Dict[str, Any] = field(default_factory=dict)
