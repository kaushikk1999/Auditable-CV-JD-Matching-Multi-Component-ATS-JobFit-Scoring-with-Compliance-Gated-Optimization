"""
Quick test of keyword engine and evidence mapper modules.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from modules.keyword_engine import extract_target_keywords, select_top_keywords
from modules.evidence_mapper import build_evidence_map, get_allowed_keywords, get_needs_confirmation

# Sample JD
jd_text = """
Online Tutor
We are seeking a qualified tutor to teach mathematics, English, and science to students in grades 1-10.

REQUIREMENTS:
- Skills: Math (required), Tutoring, Teaching experience, Lesson planning
- Education: Bachelor's degree (required)
- Languages: English (required)

RESPONSIBILITIES:
- Teach mathematics, English, and science
- Create engaging lesson plans
- Provide personalized tutoring
"""

# Sample CV (Coding Educator)
cv_text = """
KAUSHIK KARMAKAR

SUMMARY
Coding Educator focused on technology development for children. Instructed 500+ students in Python programming,
achieving 4.9/5 satisfaction rating. Designed interactive learning experiences using gamification.

TECHNICAL SKILLS
Teaching & Pedagogy: Online Teaching, Mentoring, Curriculum Development, Student Engagement
Programming: Python, Coding Logic, Software Development
EdTech Tools: Video Conferencing, Gamified Learning Platforms, LMS

PROFESSIONAL EXPERIENCE
Machine Learning Coach internship | Sep 2024 – Present
• Conducted 100+ interactive online sessions, teaching Python concepts to diverse student groups globally
• Adapted instructional methods using gamification, ensuring 100% concept clarity via visual aids
• Provided constructive feedback and mentorship, helping learners succeed in real-world projects
"""

print("="*80)
print("TESTING KEYWORD ENGINE & EVIDENCE MAPPER")
print("="*80)

# Step 1: Extract keywords
print("\n📋 Step 1: Extract Target Keywords from JD")
print("-"*80)
target_keywords = extract_target_keywords(jd_text)

print(f"Role Title: {target_keywords.role_title}")
print(f"\nRequired ({len(target_keywords.required)}):")
for kw in target_keywords.required[:5]:
    score = target_keywords.importance_scores.get(kw, 0)
    print(f"  - {kw} (importance: {score})")

print(f"\nPreferred ({len(target_keywords.preferred)}):")
for kw in target_keywords.preferred[:5]:
    score = target_keywords.importance_scores.get(kw, 0)
    print(f"  - {kw} (importance: {score})")

# Step 2: Select top keywords
print("\n🎯 Step 2: Select Top 15 Keywords")
print("-"*80)
top_15 = select_top_keywords(target_keywords, n=15)
for kw in top_15:
    score = target_keywords.importance_scores.get(kw, 0)
    print(f"  - {kw} ({score})")

# Step 3: Build evidence map
print("\n🔍 Step 3: Build Evidence Map")
print("-"*80)
evidence_map = build_evidence_map(cv_text, top_15)

has_evidence_count = sum(1 for ev in evidence_map.values() if ev.has_evidence)
print(f"Keywords with evidence: {has_evidence_count}/{len(top_15)}")

print("\n✅ Keywords WITH Evidence:")
for kw, ev in evidence_map.items():
    if ev.has_evidence:
        print(f"  - {kw} ({ev.evidence_type}, confidence={ev.confidence:.2f})")
        print(f"    Locations: {', '.join(ev.locations)}")
        if ev.snippets:
            print(f"    Snippet: {ev.snippets[0][:80]}...")

print("\n❌ Keywords WITHOUT Evidence:")
for kw, ev in evidence_map.items():
    if not ev.has_evidence:
        blocked_msg = " [BLOCKED BY FALSE FRIEND]" if ev.blocked_by_false_friend else ""
        print(f"  - {kw}{blocked_msg}")

# Step 4: Get allowed and needs confirmation
print("\n📊 Step 4: Classification")
print("-"*80)
allowed = get_allowed_keywords(evidence_map)
needs_confirmation = get_needs_confirmation(evidence_map, target_keywords)

print(f"\n✅ Allowed Keywords ({len(allowed)}):")
print(f"   {', '.join(allowed)}")

print(f"\n⚠️ Needs User Confirmation ({len(needs_confirmation)}):")
print(f"   {', '.join(needs_confirmation)}")

# Step 5: Test domain guardrails
print("\n🛡️ Step 5: Domain Guardrails Test")
print("-"*80)
print("Testing if 'Data Science' is blocked as evidence for 'Science':")

test_cv = "Expert in Data Science and Machine Learning"
test_kws = ["Science"]
test_evidence = build_evidence_map(test_cv, test_kws)

if test_evidence["Science"].blocked_by_false_friend:
    print("  ✅ PASS: Correctly blocked 'Data Science' as false friend for 'Science'")
else:
    print("  ❌ FAIL: Did not block false friend")

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80)
