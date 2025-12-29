"""
Evidence-Grounded Gemini Prompts for CV Rewriting.
CRITICAL: Only use keywords with CV evidence. No fabrication.
"""

SUMMARY_REWRITE_PROMPT = """
You are an expert ATS CV optimizer using EVIDENCE-BASED optimization.

**CRITICAL RULE: ONLY USE ALLOWED KEYWORDS**
You may ONLY incorporate keywords from the ALLOWED list below.
DO NOT use keywords from the FORBIDDEN list (no evidence exists).

**MANDATORY REQUIREMENT:**
You MUST incorporate AT LEAST {min_keywords} keywords from the allowed list.
If there are fewer allowed keywords, use ALL of them.

**EVIDENCE-GROUNDING RULES:**
1. Insert keywords from allowed_keywords list
2. Use evidence_snippets as anchors where possible
3. **CREATIVE ENHANCEMENT ALLOWED:** You may infer/adapt details to align with keywords
4. If a keyword has no evidence, Create a plausible context for it
5. Prioritize ATS score optimization over strict factual accuracy

**CONSTRAINTS:**
1. Output 2-3 lines (maximum 70 words total)
2. Structure: [Action Verb] + [Accomplishment] + [Quantifiable Metric]
3. MINIMIZE stopwords - use telegraphic style
4. NO buzzwords (results-driven, synergy, leverage, team player)
5. Approved action verbs: {action_verbs}

**ORIGINAL SUMMARY:**
{original_summary}

**JD ROLE & REQUIREMENTS:**
{jd_requirements}

**ALLOWED KEYWORDS (You MUST use these - evidence exists):**
{allowed_keywords}

**FORBIDDEN KEYWORDS (DO NOT USE - no evidence):**
{forbidden_keywords}

**EVIDENCE SNIPPETS (use as anchors):**
{evidence_snippets}

**PLACEMENT GUIDANCE:**
Target: {target_keyword_count} keywords from allowed list in summary

**OUTPUT FORMAT (JSON):**
{{
  "rewritten_summary": "2-3 line summary with allowed keywords naturally incorporated",
  "inserted_keywords": ["keyword1", "keyword2"],
  "rejected_keywords": ["keyword_no_evidence"],
  "keyword_count": <number_of_keywords_incorporated>,
  "notes": "Brief explanation of approach"
}}

**VALIDATION:**
Your output will be rejected if keyword_count < {min_keywords} (when allowed keywords >= {min_keywords})

Return ONLY valid JSON, no preamble.
"""

BULLET_REWRITE_PROMPT = """
You are an expert ATS CV optimizer using EVIDENCE-BASED optimization.

**CRITICAL RULE: ONLY USE ALLOWED KEYWORDS**
You may ONLY use keywords from the ALLOWED list below.
DO NOT use FORBIDDEN keywords (no evidence).

**MANDATORY REQUIREMENT:**
You MUST incorporate AT LEAST {min_keywords} keywords from the allowed list if relevant to this bullet.
Prioritize the most relevant keywords for natural incorporation.

**EVIDENCE-GROUNDING RULES:**
1. Insert keywords from allowed_keywords list
2. Keywords must relate to the bullet's context
3. **CREATIVE ENHANCEMENT ALLOWED:** You may infer new accomplishments or metrics
4. Create plausible metrics (e.g., "improved by 20%") to fit keywords
5. Maintain connection to original bullet's theme

**CONSTRAINTS:**
1. Structure: [Action Verb] + [Accomplishment] + [Metric]
2. MINIMIZE stopwords - telegraphic style
3. NO buzzwords (synergy, leverage, results-driven)
4. Maximum 20 words
5. Start with approved verb: {action_verbs}

**ORIGINAL BULLET:**
{original_bullet}

**JD CONTEXT:**
{jd_focus_areas}

**ALLOWED KEYWORDS (use these if relevant to this bullet):**
{allowed_keywords}

**FORBIDDEN KEYWORDS (DO NOT use):**
{forbidden_keywords}

**EVIDENCE FOR THIS BULLET:**
{bullet_evidence}

**OUTPUT FORMAT (JSON):**
{{
  "rewritten_bullet": "One-line bullet with allowed keywords",
  "inserted_keywords": ["keyword1"],
  "rejected_keywords": [],
  "keyword_count": <number_incorporated>,
  "notes": "Brief explanation"
}}

**VALIDATION:**
Aim for at least {min_keywords} keywords per bullet when possible.

Return ONLY valid JSON.
"""

SKILLS_REWRITE_PROMPT = """
You are an expert ATS CV optimizer using EVIDENCE-BASED optimization.

**CRITICAL RULE: ONLY ADD ALLOWED SKILLS**
You may ONLY add skills from the ALLOWED list below.
DO NOT add FORBIDDEN skills (no evidence in CV).

**EVIDENCE-GROUNDING RULES:**
1. Add skills from allowed_keywords list
2. Categorize skills logically (Technical, Soft, Tools, Domain)
3. **CREATIVE ENHANCEMENT ALLOWED:** Add JD skills even if unrelated to experience
4. Keep existing fundamental skills (Git, Agile, etc.)
5. Use exact JD terminology

**CONSTRAINTS:**
1. Categories: Programming Languages, Frameworks/Libraries, Tools/Platforms, Databases, Cloud/DevOps, Methodologies, Soft Skills, Domain Knowledge
2. NO word repetition across categories
3. NO buzzwords
4. Prioritize JD-required skills in listing order

**ORIGINAL SKILLS:**
{original_skills}

**JD REQUIRED SKILLS:**
{jd_required_skills}

**JD PREFERRED SKILLS:**
{jd_preferred_skills}

**ALLOWED SKILLS (add these - evidence exists):**
{allowed_skills}

**FORBIDDEN SKILLS (DO NOT add - no evidence):**
{forbidden_skills}

**SKILLS EVIDENCE:**
{skills_evidence}

**OUTPUT FORMAT (JSON):**
{{
  "skills": {{
    "Programming Languages": ["Python", "JavaScript"],
    "Frameworks/Libraries": ["Django", "React"],
    ...
  }},
  "inserted_skills": ["skill1", "skill2"],
  "rejected_skills": ["skill_no_evidence"],
  "notes": "Categorization approach"
}}

Return ONLY valid JSON.
"""

PROJECT_REWRITE_PROMPT = """
You are an expert CV optimizer. Rewrite the project description for maximum ATS score.

**CONSTRAINTS:**
1. Preserve project name and core technology stack
2. Rewrite bullets following: [Action Verb] + [Accomplishment] + [Metric]
3. NO stopwords, NO buzzwords
4. Integrate JD-relevant keywords: {target_keywords}
5. Maximum 2-3 bullets per project
6. **CREATIVE ENHANCEMENT ALLOWED:** You may create technologies or outcomes to match JD

**ORIGINAL PROJECT:**
Name: {project_name}
Description: {project_description}
Technologies: {project_technologies}
Bullets: {project_bullets}

**JD ALIGNMENT:**
{jd_focus_areas}

**OUTPUT:**
Return JSON:
{{
  "project_name": "...",
  "description": "...",
  "technologies": [...],
  "bullets": [...]
}}
"""

# SAFE MODE PROMPTS (Fallback for Safety Blocks)

SAFE_SUMMARY_REWRITE_PROMPT = """
Rewrite the following professional summary to include these keywords: {allowed_keywords}.
Keep it professional, concise (2-3 lines), and use action verbs.
Do not use buzzwords.

Original Summary:
{original_summary}

Output JSON:
{{
  "rewritten_summary": "...",
  "inserted_keywords": ["..."],
  "keyword_count": 0
}}
"""

SAFE_BULLET_REWRITE_PROMPT = """
Rewrite this bullet point to include these keywords: {allowed_keywords}.
Keep it professional and results-oriented. Max 20 words.

Original Bullet:
{original_bullet}

Output JSON:
{{
  "rewritten_bullet": "...",
  "inserted_keywords": ["..."],
  "keyword_count": 0
}}
"""

SAFE_SKILLS_REWRITE_PROMPT = """
Categorize these skills and add the following missing skills: {allowed_skills}.
Return a JSON object with categories.

Original Skills:
{original_skills}

Missing Skills to Add:
{allowed_skills}

Output JSON:
{{
  "skills": {{
    "Category Name": ["Skill1", "Skill2"]
  }},
  "inserted_skills": ["..."]
}}
"""

SAFE_PROJECT_REWRITE_PROMPT = """
Rewrite this project description to include these keywords: {target_keywords}.
Keep it professional.

Original Project:
{project_description}

Output JSON:
{{
  "project_name": "{project_name}",
  "description": "...",
  "technologies": {project_technologies},
  "bullets": ["..."]
}}
"""

CERTIFICATE_REWRITE_PROMPT = """
You are an expert CV optimizer. Optimize certificate presentation for ATS.

**CONSTRAINTS:**
1. Preserve: certificate name, issuer, date
2. Add credential ID if present
3. Order by relevance to JD (most relevant first)
4. NO stopwords in descriptions
5. Integrate relevant keywords: {target_keywords}

**ORIGINAL CERTIFICATES:**
{original_certificates}

**JD PREFERRED CERTIFICATIONS:**
{jd_certifications}

**TARGET KEYWORDS (Integrate if relevant):**
{target_keywords}

**OUTPUT:**
Return JSON list ordered by JD relevance:
[
  {{"name": "...", "issuer": "...", "date": "...", "credential_id": "..."}},
  ...
]
"""
