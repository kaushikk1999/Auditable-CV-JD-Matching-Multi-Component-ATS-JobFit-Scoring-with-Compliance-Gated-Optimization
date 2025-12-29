"""
Diagnostic script to analyze CV/JD data quality and scoring.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from modules.storage import Storage
from modules.scoring_pipeline import ScoringPipeline
from modules.gap_analyzer import KeywordGapAnalyzer
import json

print("=" * 80)
print("CV/JD DIAGNOSTIC REPORT")
print("=" * 80)

# Load data
try:
    cv_structured = Storage.load_structured_cv()
    jd_enhanced = Storage.load_enhanced_jd()
    cv_raw = Storage.load_raw_cv()
    jd_raw = Storage.load_raw_jd()
    print("✅ Successfully loaded all data files")
except Exception as e:
    print(f"❌ Error loading data: {e}")
    sys.exit(1)

# Convert to dicts for analysis
if hasattr(cv_structured, 'model_dump'):
    cv_dict = cv_structured.model_dump()
else:
    cv_dict = cv_structured

if hasattr(jd_enhanced, 'model_dump'):
    jd_dict = jd_enhanced.model_dump()
else:
    jd_dict = jd_enhanced

print("\n" + "=" * 80)
print("1. CV CONTENT ANALYSIS")
print("=" * 80)

# Experience analysis
exp_count = len(cv_dict.get("experience", []))
total_bullets = sum(len(exp.get("bullets", [])) for exp in cv_dict.get("experience", []))
print(f"Experience Entries: {exp_count}")
print(f"Total Bullets: {total_bullets}")

if total_bullets > 0:
    print("\nSample bullets:")
    for i, exp in enumerate(cv_dict.get("experience", [])[:2]):
        print(f"\n  {exp.get('job_title', 'N/A')} at {exp.get('company_name', 'N/A')}")
        for j, bullet in enumerate(exp.get("bullets", [])[:3]):
            text = bullet.get("text", "") if isinstance(bullet, dict) else str(bullet)
            print(f"    • {text[:100]}...")

# Skills analysis
skills_count = sum(len(cat.get("skills", [])) for cat in cv_dict.get("skills", []))
print(f"\nSkills Count: {skills_count}")

# Projects
project_count = len(cv_dict.get("projects", []))
print(f"Projects: {project_count}")

# Certs
cert_count = len(cv_dict.get("certifications", []))
print(f"Certifications: {cert_count}")

# Raw text length
print(f"\nCV Raw Text Length: {len(cv_raw)} characters")

print("\n" + "=" * 80)
print("2. JD CONTENT ANALYSIS")
print("=" * 80)

req_skills = jd_dict.get("required_skills", [])
pref_skills = jd_dict.get("preferred_skills", [])
ats_keywords = jd_dict.get("ats_keywords", [])

print(f"Required Skills: {len(req_skills)}")
print(f"  Examples: {', '.join(req_skills[:5])}")
print(f"\nPreferred Skills: {len(pref_skills)}")
print(f"  Examples: {', '.join(pref_skills[:5])}")
print(f"\nATS Keywords: {len(ats_keywords)}")
print(f"  Examples: {', '.join(ats_keywords[:10])}")

responsibilities = jd_dict.get("key_responsibilities", [])
print(f"\nKey Responsibilities: {len(responsibilities)}")

print(f"\nJD Raw Text Length: {len(jd_raw)} characters")

print("\n" + "=" * 80)
print("3. SCORING ANALYSIS")
print("=" * 80)

scorer = ScoringPipeline()
score_result = scorer.score_cv_jd_pair(cv_structured, jd_enhanced, cv_raw, jd_raw)

print(f"ATS Score: {score_result['ats_score']:.2f}")
print(f"JobFit Score: {score_result['jobfit_score']:.2f}")

print("\nDetailed Breakdown:")
print(json.dumps(score_result, indent=2))

print("\n" + "=" * 80)
print("4. GAP ANALYSIS")
print("=" * 80)

gap_analyzer = KeywordGapAnalyzer()
gap_result = gap_analyzer.analyze(cv_structured, jd_enhanced)

print(f"Missing Keywords: {len(gap_result.missing_keywords)}")
print("\nTop 10 Missing Keywords:")
for i, kw in enumerate(gap_result.missing_keywords[:10], 1):
    print(f"  {i}. {kw.keyword} (Priority: {kw.jd_priority}, Category: {kw.category})")

print(f"\nCoverage Rate: {gap_result.coverage_stats.get('coverage_rate', 0):.1f}%")
print(f"Keywords in CV: {gap_result.coverage_stats.get('cv_keyword_count', 0)}")
print(f"Keywords in JD: {gap_result.coverage_stats.get('jd_keyword_count', 0)}")

print("\n" + "=" * 80)
print("5. RECOMMENDATIONS")
print("=" * 80)

issues = []
if total_bullets < 10:
    issues.append(f"❌ Too few experience bullets ({total_bullets}). Aim for 15-20+")
if skills_count < 15:
    issues.append(f"❌ Too few skills ({skills_count}). Aim for 20-30+")
if len(cv_raw) < 1000:
    issues.append(f"❌ CV text too short ({len(cv_raw)} chars). Aim for 2000+")
if len(gap_result.missing_keywords) > len(ats_keywords) * 0.5:
    issues.append(f"⚠️ Missing {len(gap_result.missing_keywords)} critical keywords")
if score_result['ats_score'] < 50:
    issues.append(f"❌ ATS score critically low ({score_result['ats_score']:.1f})")

if issues:
    print("\nIssues Found:")
    for issue in issues:
        print(f"  {issue}")
else:
    print("✅ No major issues detected")

print("\nSuggested Actions:")
if total_bullets < 15:
    print("  1. Add more detailed bullets to experience section")
if skills_count < 20:
    print("  2. Expand skills section with JD keywords")
if len(gap_result.missing_keywords) > 10:
    print("  3. Incorporate missing keywords into bullets")
print("  4. Enable Projects and Certificates rewriting")
print("  5. Increase max iterations to 5")

print("\n" + "=" * 80)
