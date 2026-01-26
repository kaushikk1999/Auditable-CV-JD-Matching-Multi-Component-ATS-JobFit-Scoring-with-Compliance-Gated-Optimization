"""
Test the complete evidence-grounded optimization pipeline.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from modules.rewrite_orchestrator import optimize_cv_for_jd
from modules.storage import Storage

# Load structured CV and JD
cv_structured = Storage.load_structured_cv()
jd_enhanced = Storage.load_enhanced_jd()
cv_text = Storage.load_raw_cv()
jd_text = Storage.load_raw_jd()

print("="*100)
print("TESTING EVIDENCE-GROUNDED OPTIMIZATION PIPELINE")
print("="*100)

#Run optimization
result = optimize_cv_for_jd(
    cv_structured=cv_structured.model_dump(),
    cv_text=cv_text,
    jd_dict=jd_enhanced.model_dump(),
    jd_text=jd_text,
    user_confirmations=None
)

print(f"\n🎯 SCORES:")
print(f"   ATS: {result.ats_score:.1f}")
print(f"   JobFit: {result.jobfit_score:.1f}")

if result.score_capped:
    print(f"\n⚠️ SCORE CAPPED:")
    print(f"   Reason: {result.cap_reason}")

print(f"\n✅ ALLOWED KEYWORDS ({len(result.allowed_keywords)}):")
for kw in result.allowed_keywords[:10]:
    print(f"   - {kw}")

print(f"\n⚠️ NEEDS CONFIRMATION ({len(result.needs_user_confirmation)}):")
for kw in result.needs_user_confirmation[:5]:
    print(f"   - {kw}")

print(f"\n🎯 PLACEMENT PLAN:")
plan = result.placement_plan
print(f"   Headline: {len(plan.get('headline_keywords', []))} keywords")
print(f"   Summary: {len(plan.get('summary_keywords', []))} keywords")
print(f"   Skills: {sum(len(v) for v in plan.get('skills_keywords', {}).values())} keywords")
print(f"   Bullets: {len(plan.get('bullets_keywords', {}))} bullets targeted")

print("\n" + "="*100)
print("PIPELINE TEST COMPLETE")
print("="*100)
